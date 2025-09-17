from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    discountPercentage: Optional[float] = 0.0
    rating: Optional[float] = 0.0
    stock: int
    brand: str
    category: str
    thumbnail: Optional[str]
    images: Optional[List[str]] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[float]
    discountPercentage: Optional[float]
    rating: Optional[float]
    stock: Optional[int]
    brand: Optional[str]
    category: Optional[str]
    thumbnail: Optional[str]
    images: Optional[List[str]]

class ProductResponse(ProductBase):
    id: str

    class Config:
        orm_mode = True
