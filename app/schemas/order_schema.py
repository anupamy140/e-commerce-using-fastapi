from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItemSchema(BaseModel):
    product_id: str
    quantity: int


class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItemSchema]
    total: float


# ✅ Order response
class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemSchema]
    total: float
    status: str
    created_at: datetime


# ✅ Order status update schema
class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="New status of the order")

    class Config:
        schema_extra = {
            "example": {
                "status": "shipped"
            }
        }
