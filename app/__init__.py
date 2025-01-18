from fastapi import APIRouter
from app.auth import router as auth_router
from app.api.product import router as product_router
from app.api.order import router as order_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(product_router, prefix="/products", tags=["products"])
router.include_router(order_router, prefix="/orders", tags=["orders"])