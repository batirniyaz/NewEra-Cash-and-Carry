from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.product import get_product
from app.models.order import Order, OrderDetail
from app.schemas.order import OrderCreate, OrderUpdate


async def create_order(db: AsyncSession, order: OrderCreate, user_id: int):
    db_order = Order(**order.model_dump(), created_by=user_id)
    db.add(db_order)
    await db.flush()

    for item in order.items:
        db_product = await get_product(db, item)
        db_order_detail = OrderDetail(order_id=db_order.id,
                                      status='pending',
                                      product_detail={
                                            "product_id": db_product.id,
                                            "product_name": db_product.name,
                                            "product_price": db_product.price,
                                            "description": db_product.description,
                                      })
        db.add(db_order_detail)

    await db.commit()
    await db.refresh(db_order)

    return db_order


async def get_orders(db: AsyncSession, user_id: Optional[int] = None):
    stmt = select(Order).filter_by(created_by=user_id) if user_id else select(Order)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return orders if orders else []


async def get_order(db: AsyncSession, order_id: int):
    stmt = await db.execute(select(Order).filter_by(id=order_id))
    db_order = stmt.scalar_one_or_none()

    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    return db_order


async def update_order(db: AsyncSession, order_id: int, order: OrderUpdate):

    db_order = await get_order(db, order_id)

    for key, value in order.model_dump(exclude_unset=True).items():
        setattr(db_order, key, value)

    await db.commit()

    return db_order


async def delete_order(db: AsyncSession, order_id: int):
    db_order = await get_order(db, order_id)
    await db.delete(db_order)
    await db.commit()
    return db_order
