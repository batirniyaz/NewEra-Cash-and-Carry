from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


async def get_products(db: AsyncSession):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products if products else []


async def get_product(db: AsyncSession, product_id: int):
    db_product = await db.execute(select(Product).filter_by(id=product_id))
    db_product = db_product.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    return db_product


async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate):

    db_product = await get_product(db, product_id)
    db_products = await get_products(db)
    if product.name in [d.name for d in db_products]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this name already exists")

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)

    await db.commit()

    return db_product


async def delete_product(db: AsyncSession, product_id: int):
    db_product = await get_product(db, product_id)
    await db.delete(db_product)
    await db.commit()
    return {"detail": "Product deleted successfully"}
