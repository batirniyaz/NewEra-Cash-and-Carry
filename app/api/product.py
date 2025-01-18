
from fastapi import APIRouter, HTTPException, status

from app.auth.utils import user_get
from app.database import get_session

from app.crud.product import create_product, get_products, get_product, update_product, delete_product
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate


router = APIRouter()


@router.post("/", response_model=ProductResponse)
async def create_product_endpoint(
        product: ProductCreate,
        current_user: user_get,
        db: get_session,
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permission to create product")
    return await create_product(db, product)


@router.get("/", response_model=list[ProductResponse])
async def get_products_endpoint(
        current_user: user_get,
        db: get_session,
):
    return await get_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
        product_id: int,
        current_user: user_get,
        db: get_session,
):
    return await get_product(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
        product_id: int,
        product: ProductUpdate,
        current_user: user_get,
        db: get_session,
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permission to update product")
    return await update_product(db, product_id, product)


@router.delete("/{product_id}")
async def delete_product_endpoint(
        product_id: int,
        current_user: user_get,
        db: get_session
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have permission to delete product")
    return await delete_product(db, product_id)
