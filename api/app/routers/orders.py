import uuid as uuid_mod
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import require_api_key
from app.models.lookups import OrderItemType, OrderStatus
from app.models.order import Order, OrderItem, OrderStatusHistory

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(require_api_key)])


class OrderItemCreate(BaseModel):
    description: str
    item_type: str = "product"
    quantity: Decimal = Decimal("1.00")
    unit_price: Decimal
    discount_amount: Decimal = Decimal("0.00")


class OrderCreate(BaseModel):
    contact_uuid: str
    order_date: str
    due_date: str | None = None
    scheduled_at: str | None = None
    items: list[OrderItemCreate] = []
    notes_text: str | None = None


class StatusChange(BaseModel):
    status: str
    changed_by: str | None = None
    notes: str | None = None


async def _get_order(db: AsyncSession, uuid: str) -> Order | None:
    stmt = (
        select(Order).where(Order.uuid == uuid)
        .options(
            selectinload(Order.order_status),
            selectinload(Order.items).selectinload(OrderItem.item_type),
            selectinload(Order.status_history).selectinload(OrderStatusHistory.from_status),
            selectinload(Order.status_history).selectinload(OrderStatusHistory.to_status),
            selectinload(Order.invoices),
            selectinload(Order.contact),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()


@router.get("")
async def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    status: str | None = None,
    contact_uuid: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order).where(Order.is_active == True)  # noqa: E712
    if status:
        stmt = stmt.join(OrderStatus, Order.order_status_id == OrderStatus.id).where(OrderStatus.code == status)
    if contact_uuid:
        from app.models.contact import Contact
        stmt = stmt.join(Contact).where(Contact.uuid == contact_uuid)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Order.order_date.desc()).offset((page - 1) * per_page).limit(per_page)
    stmt = stmt.options(selectinload(Order.order_status), selectinload(Order.contact))
    result = await db.execute(stmt)
    orders = result.scalars().all()

    return {
        "data": [
            {"uuid": o.uuid, "order_number": o.order_number, "status": o.order_status.code,
             "total": str(o.total), "order_date": str(o.order_date),
             "contact": f"{o.contact.first_name} {o.contact.last_name}"}
            for o in orders
        ],
        "pagination": {"page": page, "per_page": per_page, "total": total,
                        "total_pages": (total + per_page - 1) // per_page if per_page else 0},
    }


@router.get("/{uuid}")
async def get_order(uuid: str, db: AsyncSession = Depends(get_db)):
    order = await _get_order(db, uuid)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {uuid} not found")
    return {
        "uuid": order.uuid,
        "order_number": order.order_number,
        "contact": {"uuid": order.contact.uuid, "name": f"{order.contact.first_name} {order.contact.last_name}"},
        "status": order.order_status.code,
        "order_date": str(order.order_date),
        "due_date": str(order.due_date) if order.due_date else None,
        "subtotal": str(order.subtotal),
        "discount_amount": str(order.discount_amount),
        "tax_amount": str(order.tax_amount),
        "total": str(order.total),
        "items": [
            {"description": i.description, "type": i.item_type.code, "quantity": str(i.quantity),
             "unit_price": str(i.unit_price), "line_total": str(i.line_total)}
            for i in order.items
        ],
        "status_history": [
            {"from": h.from_status.code if h.from_status else None, "to": h.to_status.code,
             "changed_by": h.changed_by, "at": h.created_at.isoformat() if h.created_at else None}
            for h in sorted(order.status_history, key=lambda x: x.created_at)
        ],
        "notes_text": order.notes_text,
    }


@router.post("", status_code=201)
async def create_order(body: OrderCreate, db: AsyncSession = Depends(get_db)):
    from app.models.contact import Contact
    contact = (await db.execute(select(Contact).where(Contact.uuid == body.contact_uuid))).scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=400, detail=f"Contact {body.contact_uuid} not found")

    # Default to 'quoted' status
    status = (await db.execute(select(OrderStatus).where(OrderStatus.code == "quoted"))).scalar_one()

    # Calculate totals from items
    subtotal = Decimal("0.00")
    order_items = []
    for idx, item in enumerate(body.items):
        line_total = (item.quantity * item.unit_price) - item.discount_amount
        subtotal += line_total
        item_type = (await db.execute(select(OrderItemType).where(OrderItemType.code == item.item_type))).scalar_one_or_none()
        if not item_type:
            raise HTTPException(status_code=400, detail=f"Unknown item type: {item.item_type}")
        order_items.append(OrderItem(
            item_type_id=item_type.id, description=item.description,
            quantity=item.quantity, unit_price=item.unit_price,
            discount_amount=item.discount_amount, line_total=line_total, sort_order=idx,
        ))

    order = Order(
        uuid=str(uuid_mod.uuid4()), contact_id=contact.id, order_status_id=status.id,
        order_date=body.order_date, due_date=body.due_date,
        subtotal=subtotal, total=subtotal, notes_text=body.notes_text, created_by="api",
    )
    order.items = order_items
    order.status_history = [OrderStatusHistory(to_status_id=status.id, changed_by="api")]
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return {"uuid": order.uuid, "order_number": order.order_number, "total": str(order.total)}


@router.post("/{uuid}/status")
async def change_order_status(uuid: str, body: StatusChange, db: AsyncSession = Depends(get_db)):
    order = await _get_order(db, uuid)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {uuid} not found")

    new_status = (await db.execute(select(OrderStatus).where(OrderStatus.code == body.status))).scalar_one_or_none()
    if not new_status:
        raise HTTPException(status_code=400, detail=f"Unknown status: {body.status}")

    history = OrderStatusHistory(
        order_id=order.id, from_status_id=order.order_status_id,
        to_status_id=new_status.id, changed_by=body.changed_by, notes_text=body.notes,
    )
    db.add(history)
    order.order_status_id = new_status.id
    await db.commit()
    return {"uuid": order.uuid, "status": body.status}


@router.delete("/{uuid}", status_code=204)
async def delete_order(uuid: str, db: AsyncSession = Depends(get_db)):
    order = await _get_order(db, uuid)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {uuid} not found")
    order.is_active = False
    order.deleted_at = datetime.now(timezone.utc)
    await db.commit()
