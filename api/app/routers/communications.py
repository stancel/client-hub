import json
import uuid as uuid_mod

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import SourceContext, require_api_key
from app.models.communication import Communication
from app.models.contact import Contact
from app.models.lookups import ChannelType
from app.models.order import Order
from app.models.source import Source
from app.services.request_meta import _is_public_ip, extract_request_meta
from app.services.spam_filter_service import (
    IntakePayload,
    spam_check_or_raise,
)

router = APIRouter(prefix="/communications", tags=["communications"], dependencies=[Depends(require_api_key)])


class CommCreate(BaseModel):
    contact_uuid: str
    channel: str
    direction: str
    occurred_at: str
    subject: str | None = None
    body: str | None = None
    order_uuid: str | None = None
    external_message_id: str | None = None
    created_by: str | None = None
    # Optional integration metadata — consumer sites pass ip_address and
    # user_agent here (extracted from CF-Connecting-IP server-side); the spam
    # filter prefers these over the request peer for source-key endpoints.
    external_refs_json: dict | None = None


@router.get("")
async def list_communications(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    contact_uuid: str | None = None,
    channel: str | None = None,
    direction: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Communication)
    if contact_uuid:
        stmt = stmt.join(Contact).where(Contact.uuid == contact_uuid)
    if channel:
        stmt = stmt.join(ChannelType, Communication.channel_type_id == ChannelType.id).where(ChannelType.code == channel)
    if direction:
        stmt = stmt.where(Communication.direction == direction)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (stmt.order_by(Communication.occurred_at.desc()).offset((page - 1) * per_page).limit(per_page)
            .options(selectinload(Communication.channel_type), selectinload(Communication.contact)))
    result = await db.execute(stmt)
    comms = result.scalars().all()

    return {
        "data": [
            {"uuid": c.uuid, "contact": f"{c.contact.first_name} {c.contact.last_name}",
             "channel": c.channel_type.code, "direction": c.direction,
             "subject": c.subject, "occurred_at": c.occurred_at.isoformat() if c.occurred_at else None}
            for c in comms
        ],
        "pagination": {"page": page, "per_page": per_page, "total": total,
                        "total_pages": (total + per_page - 1) // per_page if per_page else 0},
    }


@router.get("/{uuid}")
async def get_communication(uuid: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Communication).where(Communication.uuid == uuid)
        .options(selectinload(Communication.channel_type), selectinload(Communication.contact))
    )
    comm = (await db.execute(stmt)).scalar_one_or_none()
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {uuid} not found")
    return {
        "uuid": comm.uuid,
        "contact": {"uuid": comm.contact.uuid, "name": f"{comm.contact.first_name} {comm.contact.last_name}"},
        "channel": comm.channel_type.code,
        "direction": comm.direction,
        "subject": comm.subject,
        "body": comm.body,
        "occurred_at": comm.occurred_at.isoformat() if comm.occurred_at else None,
        "external_message_id": comm.external_message_id,
    }


@router.post("", status_code=201)
async def create_communication(
    body: CommCreate,
    request: Request,
    ctx: SourceContext = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    # Run the spam guard BEFORE any DB write. CommCreate references the
    # parent contact by uuid (no email/phone on the comm itself), so we
    # look the parent up first and pull its primary email + stored
    # ip_address out of external_refs_json. This means:
    #   - submitted_email is recorded on spam_events (not NULL),
    #     which lets email-substring patterns and email rate-limits
    #     fire on follow-up communications from a known spam address.
    #   - canonical visitor IP propagates from the contact-create call
    #     even when the comm payload itself doesn't carry it (consumer
    #     sites that haven't yet adopted the v0.4.0 SDK contract still
    #     get correct IP forensics).
    contact = (await db.execute(
        select(Contact)
        .options(selectinload(Contact.emails))
        .where(Contact.uuid == body.contact_uuid)
    )).scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=400, detail=f"Contact {body.contact_uuid} not found")

    parent_email: str | None = None
    primary_email = next(
        (e for e in contact.emails if e.is_primary), None
    ) or next(iter(contact.emails), None)
    if primary_email is not None:
        parent_email = primary_email.email_address

    parent_ip_fallback: str | None = None
    if contact.external_refs_json:
        try:
            refs = (
                contact.external_refs_json
                if isinstance(contact.external_refs_json, dict)
                else json.loads(contact.external_refs_json)
            )
            stored_ip = refs.get("ip_address") if isinstance(refs, dict) else None
            if isinstance(stored_ip, str) and _is_public_ip(stored_ip):
                parent_ip_fallback = stored_ip.strip()
        except (TypeError, ValueError):
            parent_ip_fallback = None

    canonical_ip, peer_ip, ua = extract_request_meta(
        request, payload_external_refs=body.external_refs_json
    )
    intake = IntakePayload(
        email=parent_email,
        phone=None,
        body=body.body,
        remote_ip=canonical_ip or parent_ip_fallback,
        peer_ip=peer_ip,
        user_agent=ua,
    )
    await spam_check_or_raise(
        db, intake,
        source_id=ctx.source_id,
        endpoint="/api/v1/communications",
        integration_kind="web_form",
        payload=body.model_dump(mode="json"),
        # The parent contact-create has already written the email's
        # rate-log row; counting this comm as a 2nd email-hit would
        # block the standard logConversion(contact+comm) consumer flow.
        skip_email_rate_limit=True,
    )

    channel = (await db.execute(select(ChannelType).where(ChannelType.code == body.channel))).scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {body.channel}")

    order_id = None
    if body.order_uuid:
        order = (await db.execute(select(Order).where(Order.uuid == body.order_uuid))).scalar_one_or_none()
        if order:
            order_id = order.id

    # Resolve source_id from auth context
    source_id = ctx.source_id
    if source_id is None:
        bootstrap = (await db.execute(select(Source).where(Source.code == "bootstrap"))).scalar_one()
        source_id = bootstrap.id

    from datetime import datetime
    comm = Communication(
        uuid=str(uuid_mod.uuid4()), source_id=source_id,
        contact_id=contact.id, channel_type_id=channel.id,
        order_id=order_id, direction=body.direction,
        subject=body.subject, body=body.body,
        occurred_at=datetime.fromisoformat(body.occurred_at),
        external_message_id=body.external_message_id, created_by=body.created_by,
    )
    db.add(comm)
    await db.commit()
    await db.refresh(comm)
    return {"uuid": comm.uuid, "channel": body.channel, "direction": body.direction}
