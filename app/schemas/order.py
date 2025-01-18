import datetime
from pydantic import BaseModel, Field
from typing import Optional


class OrderDetailBase(BaseModel):
    order_id: int = Field(..., description="The ID of the order")
    created_by: int = Field(..., description="The ID of the user who created the order")
    product_detail: dict = Field(..., description="The product detail of the order", examples=[
        {"product_id": 1, "quantity": 1}])
    status: str = Field(..., description="The status of the order", examples=["pending", "completed"])


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailUpdate(OrderDetailBase):
    order_id: Optional[int] = Field(None, description="The ID of the order")
    product_detail: Optional[dict] = Field(None, description="The product detail of the order", examples=[
        {"product_id": 1, "name": 'bla'}])
    status: Optional[str] = Field(None, description="The status of the order", examples=["pending", "completed"])


class OrderDetailResponse(OrderDetailBase):
    id: int = Field(..., description="The ID of the order detail")
    created_at: datetime.datetime = Field(..., description="The time the order detail was created")
    updated_at: datetime.datetime = Field(..., description="The time the order detail was updated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "order_id": 1,
                "product_detail": {"product_id": 1, "name": 'bla'},
                "status": "pending",
                "created_at": "2021-08-01T12:00:00",
                "updated_at": "2021-08-01T12:00:00"
            }
        }


class OrderBase(BaseModel):
    items: list = Field(..., description="The items of the order", examples=[1,2,3,4])


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    items: Optional[list] = Field(None, description="The items of the order", examples=[1,2,3,4])


class OrderResponse(OrderBase):
    id: int = Field(..., description="The ID of the order")
    order_details: Optional[OrderDetailResponse] = Field(..., description="The details of the order")
    created_at: datetime.datetime = Field(..., description="The time the order was created")
    updated_at: datetime.datetime = Field(..., description="The time the order was updated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "items": [1,2,3,4],
                "created_at": "2021-08-01T12:00:00",
                "updated_at": "2021-08-01T12:00:00"
            }
        }


