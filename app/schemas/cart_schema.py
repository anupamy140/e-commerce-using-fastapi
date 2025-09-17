from pydantic import BaseModel, Field
from typing import List, Optional

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

# ❌ Remove user_id from CartBase
class CartBase(BaseModel):
    items: List[CartItem] = []

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    items: Optional[List[CartItem]]

class CartResponse(CartBase):
    id: str

    class Config:
        orm_mode = True
