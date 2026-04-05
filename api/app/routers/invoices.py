import uuid as uuid_mod
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import require_api_key
from app.models.invoice import Invoice, Payment
from app.models.lookups import InvoiceStatus, PaymentMethod
from app.models.order import Order

router = APIRouter(prefix="/invoices", tags=["invoices"], dependencies=[Depends(require_api_key)])


class InvoiceCreate(BaseModel):
    order_uuid: str
    invoice_date: str
    due_date: str | None = None
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0.00")


class PaymentCreate(BaseModel):
    amount: Decimal
    payment_date: str
    payment_method: str = "online"
    reference_number: str | None = None
    external_payment_id: str | None = None


@router.get("")
async def list_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Invoice).where(Invoice.is_active == True)  # noqa: E712
    if status:
        stmt = stmt.join(InvoiceStatus, Invoice.invoice_status_id == InvoiceStatus.id).where(InvoiceStatus.code == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (stmt.order_by(Invoice.invoice_date.desc()).offset((page - 1) * per_page).limit(per_page)
            .options(selectinload(Invoice.invoice_status)))
    result = await db.execute(stmt)
    invoices = result.scalars().all()

    return {
        "data": [
            {"uuid": i.uuid, "invoice_number": i.invoice_number, "status": i.invoice_status.code,
             "total": str(i.total), "balance_due": str(i.balance_due), "invoice_date": str(i.invoice_date)}
            for i in invoices
        ],
        "pagination": {"page": page, "per_page": per_page, "total": total,
                        "total_pages": (total + per_page - 1) // per_page if per_page else 0},
    }


@router.get("/{uuid}")
async def get_invoice(uuid: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Invoice).where(Invoice.uuid == uuid)
        .options(selectinload(Invoice.invoice_status), selectinload(Invoice.payments).selectinload(Payment.payment_method))
    )
    inv = (await db.execute(stmt)).scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Invoice {uuid} not found")
    return {
        "uuid": inv.uuid,
        "invoice_number": inv.invoice_number,
        "status": inv.invoice_status.code,
        "invoice_date": str(inv.invoice_date),
        "due_date": str(inv.due_date) if inv.due_date else None,
        "subtotal": str(inv.subtotal),
        "tax_amount": str(inv.tax_amount),
        "total": str(inv.total),
        "amount_paid": str(inv.amount_paid),
        "balance_due": str(inv.balance_due),
        "payments": [
            {"uuid": p.uuid, "amount": str(p.amount), "method": p.payment_method.code,
             "date": str(p.payment_date), "reference": p.reference_number}
            for p in inv.payments
        ],
    }


@router.post("", status_code=201)
async def create_invoice(body: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).where(Order.uuid == body.order_uuid))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=400, detail=f"Order {body.order_uuid} not found")

    draft_status = (await db.execute(select(InvoiceStatus).where(InvoiceStatus.code == "draft"))).scalar_one()
    total = body.subtotal + body.tax_amount

    inv = Invoice(
        uuid=str(uuid_mod.uuid4()), order_id=order.id, invoice_status_id=draft_status.id,
        invoice_date=body.invoice_date, due_date=body.due_date,
        subtotal=body.subtotal, tax_amount=body.tax_amount, total=total,
        amount_paid=Decimal("0.00"), balance_due=total,
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return {"uuid": inv.uuid, "total": str(inv.total), "balance_due": str(inv.balance_due)}


@router.post("/{uuid}/payments", status_code=201)
async def record_payment(uuid: str, body: PaymentCreate, db: AsyncSession = Depends(get_db)):
    inv = (await db.execute(
        select(Invoice).where(Invoice.uuid == uuid).options(selectinload(Invoice.invoice_status))
    )).scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Invoice {uuid} not found")

    method = (await db.execute(select(PaymentMethod).where(PaymentMethod.code == body.payment_method))).scalar_one_or_none()
    if not method:
        raise HTTPException(status_code=400, detail=f"Unknown payment method: {body.payment_method}")

    payment = Payment(
        uuid=str(uuid_mod.uuid4()), invoice_id=inv.id, payment_method_id=method.id,
        amount=body.amount, payment_date=body.payment_date,
        reference_number=body.reference_number, external_payment_id=body.external_payment_id,
    )
    db.add(payment)

    # Update invoice balances
    inv.amount_paid += body.amount
    inv.balance_due = inv.total - inv.amount_paid

    # Update invoice status
    if inv.balance_due <= 0:
        paid_status = (await db.execute(select(InvoiceStatus).where(InvoiceStatus.code == "paid"))).scalar_one()
        inv.invoice_status_id = paid_status.id
    elif inv.amount_paid > 0:
        partial_status = (await db.execute(select(InvoiceStatus).where(InvoiceStatus.code == "partial"))).scalar_one()
        inv.invoice_status_id = partial_status.id

    await db.commit()
    return {"uuid": payment.uuid, "amount": str(body.amount), "balance_remaining": str(inv.balance_due)}
