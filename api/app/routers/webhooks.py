import uuid as uuid_mod
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import SourceContext, require_api_key
from app.models.communication import Communication
from app.models.contact import Contact, ContactEmail, ContactPhone
from app.models.invoice import Invoice, Payment
from app.models.lookups import ChannelType, InvoiceStatus, PaymentMethod
from app.models.source import Source
from app.services.spam_filter_service import (
    IntakePayload,
    spam_check_or_raise,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"], dependencies=[Depends(require_api_key)])


@router.post("/invoiceninja")
async def invoiceninja_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    event = payload.get("event", "unknown")
    data = payload.get("data", {})
    processed = []

    if event == "payment.created":
        # Find invoice by external ID
        ninja_inv_id = data.get("invoice_id")
        if ninja_inv_id:
            inv = (await db.execute(
                select(Invoice).where(Invoice.external_invoice_id == ninja_inv_id)
            )).scalar_one_or_none()
            if inv:
                method = (await db.execute(select(PaymentMethod).where(PaymentMethod.code == "online"))).scalar_one()
                from decimal import Decimal
                amount = Decimal(str(data.get("amount", 0)))
                payment = Payment(
                    uuid=str(uuid_mod.uuid4()), invoice_id=inv.id, payment_method_id=method.id,
                    amount=amount, payment_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    external_payment_id=data.get("payment_id"),
                )
                db.add(payment)
                inv.amount_paid += amount
                inv.balance_due = inv.total - inv.amount_paid
                if inv.balance_due <= 0:
                    paid = (await db.execute(select(InvoiceStatus).where(InvoiceStatus.code == "paid"))).scalar_one()
                    inv.invoice_status_id = paid.id
                await db.commit()
                processed.append(f"payment recorded for invoice {ninja_inv_id}")

    elif event == "client.updated":
        # Update contact info by external ref
        ninja_client_id = data.get("client_id")
        if ninja_client_id:
            contacts = (await db.execute(
                select(Contact).where(Contact.external_refs_json.like(f'%{ninja_client_id}%'))
            )).scalars().all()
            for contact in contacts:
                if data.get("email"):
                    # Update or add email
                    processed.append(f"contact {contact.uuid} matched")
                    pass  # Full implementation would update email records

    return {"status": "ok", "event": event, "processed": processed}


@router.post("/chatwoot")
async def chatwoot_webhook(
    request: Request,
    ctx: SourceContext = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()
    event = payload.get("event", "unknown")
    data = payload.get("data", {})
    processed = []

    if event == "message_created":
        # Try to identify contact by phone or email from sender
        sender = data.get("sender", {})
        phone = sender.get("phone_number")
        email = sender.get("email")
        contact = None

        # Spam guard — Chatwoot widget is public-facing on the consumer
        # site, so messages here can carry the same spam payloads as a
        # plain contact form. Run the filter before any DB write.
        intake = IntakePayload(
            email=email,
            phone=phone,
            body=data.get("content"),
            remote_ip=(request.client.host if request.client else None),
        )
        await spam_check_or_raise(
            db, intake,
            source_id=ctx.source_id,
            endpoint="/api/v1/webhooks/chatwoot",
            integration_kind="webhook",
            payload={"event": event, "sender": sender, "content": data.get("content")},
        )

        if phone:
            cp = (await db.execute(select(ContactPhone).where(ContactPhone.phone_number == phone))).scalar_one_or_none()
            if cp:
                contact = (await db.execute(select(Contact).where(Contact.id == cp.contact_id))).scalar_one_or_none()
        if not contact and email:
            ce = (await db.execute(select(ContactEmail).where(ContactEmail.email_address == email))).scalar_one_or_none()
            if ce:
                contact = (await db.execute(select(Contact).where(Contact.id == ce.contact_id))).scalar_one_or_none()

        if contact:
            # Determine channel
            channel_code = "chat"
            if phone:
                channel_code = "sms"
            channel = (await db.execute(select(ChannelType).where(ChannelType.code == channel_code))).scalar_one_or_none()

            if channel:
                # Resolve source_id from auth context
                source_id = ctx.source_id
                if source_id is None:
                    bootstrap = (await db.execute(select(Source).where(Source.code == "bootstrap"))).scalar_one()
                    source_id = bootstrap.id

                comm = Communication(
                    uuid=str(uuid_mod.uuid4()), source_id=source_id,
                    contact_id=contact.id, channel_type_id=channel.id,
                    direction="inbound", subject=data.get("content", "")[:255] if data.get("content") else None,
                    body=data.get("content"), occurred_at=datetime.now(timezone.utc),
                    external_message_id=str(data.get("id", "")), created_by="chatwoot",
                )
                db.add(comm)
                await db.commit()
                processed.append(f"communication logged for contact {contact.uuid}")
        else:
            processed.append("contact not identified")

    return {"status": "ok", "event": event, "processed": processed}
