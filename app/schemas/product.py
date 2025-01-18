import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="The name of the product", examples=["Product 1"])
    price: float = Field(..., description="The price of the product", examples=[100.0])
    description: str = Field(..., min_length=3, max_length=255, description="The description of the product",
                             examples=["Description of product 1"])


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="The name of the product", examples=["Product 1"])
    price: Optional[float] = Field(None, description="The price of the product", examples=[100.0])
    description: Optional[str] = Field(None, min_length=3, max_length=255, description="The description of the product",
                                       examples=["Description of product 1"])


class ProductResponse(ProductBase):
    id: int = Field(..., description="The ID of the product")
    created_at: datetime.datetime = Field(..., description="The time the product was created")
    updated_at: datetime.datetime = Field(..., description="The time the product was updated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Product 1",
                "price": 100.0,
                "description": "Description of product 1",
                "created_at": "2021-08-01T12:00:00",
                "updated_at": "2021-08-01T12:00:00"
            }
        }
