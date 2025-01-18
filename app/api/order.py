
from fastapi import APIRouter

from app.auth.utils import user_get
from app.database import get_session

from app.crud.order import create_order, get_orders, get_order
from app.schemas.order import OrderCreate

router = APIRouter()


@router.post("/")
async def create_order_endpoint(
        order: OrderCreate,
        current_user: user_get,
        db: get_session,
):
    return await create_order(db, order, current_user.id)


@router.get("/")
async def get_orders_endpoint(
        current_user: user_get,
        db: get_session,
):
    return await get_orders(db, current_user.id if not current_user.is_superuser else None)


@router.get("/{order_id}")
async def get_order_endpoint(
        order_id: int,
        current_user: user_get,
        db: get_session,
):
    return await get_order(db, order_id)


@router.get('/{order_id}/status')
async def get_order_status_endpoint(
        order_id: int,
        current_user: user_get,
        db: get_session,
):
    order = await get_order(db, order_id)
    return {"status": order.order_details[0].status}


