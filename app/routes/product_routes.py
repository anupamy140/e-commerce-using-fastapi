from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from bson.errors import InvalidId
from app.database import product_collection
from app.schemas.product_schema import ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

def serialize_product(product):
    product["id"] = str(product["_id"])
    del product["_id"]
    return product

@router.get("/")
def get_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(default=None, enum=["price", "rating"]),
    sort_order: Optional[str] = Query(default="asc", enum=["asc", "desc"]),
    skip: int = 0,
    limit: int = 10
):
    query = {}

    # 🔍 Search in title or description
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]

    # 🧠 Category and Brand filters
    if category:
        query["category"] = category
    if brand:
        query["brand"] = brand

    # 💰 Price range
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price

    # ⬆️ Sorting
    sort = []
    if sort_by:
        sort.append((sort_by, ASCENDING if sort_order == "asc" else DESCENDING))

    cursor = product_collection.find(query)
    if sort:
        cursor = cursor.sort(sort)

    products = [serialize_product(p) for p in cursor.skip(skip).limit(limit)]

    return {
        "total": product_collection.count_documents(query),
        "count": len(products),
        "data": products
    }

@router.get("/{product_id}")
def get_product_by_id(product_id: str):
    try:
        product = product_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return serialize_product(product)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID")

@router.post("/", status_code=201)
def create_product(product: ProductCreate):
    result = product_collection.insert_one(product.dict())
    new_product = product_collection.find_one({"_id": result.inserted_id})
    return serialize_product(new_product)

@router.put("/{product_id}")
def update_product(product_id: str, product: ProductUpdate):
    result = product_collection.update_one(
        {"_id": ObjectId(product_id)}, {"$set": {k: v for k, v in product.dict().items() if v is not None}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = product_collection.find_one({"_id": ObjectId(product_id)})
    return serialize_product(updated)

@router.delete("/{product_id}")
def delete_product(product_id: str):
    result = product_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

@router.get("/sort/{order}")
def get_all_products_sorted(
    order: str,
    sort_by: str = Query("title")
):
    if order.lower() not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'.")

    sort_order = ASCENDING if order.lower() == "asc" else DESCENDING

    products = list(product_collection.find({}).sort(sort_by, sort_order))

    for product in products:
        product["id"] = str(product["_id"])
        del product["_id"]

    return {
        "sort_by": sort_by,
        "order": order,
        "total_products": len(products),
        "products": products
    }

@router.get("/filter")
def filter_products(
    category: str = Query(None, description="Filter by category"),
    min_price: float = Query(None, description="Minimum price"),
    max_price: float = Query(None, description="Maximum price"),
):
    query = {}
    if category:
        query["category"] = category
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        query["price"] = price_filter

    products = list(product_collection.find(query))

    for product in products:
        product["id"] = str(product["_id"])
        del product["_id"]

    return {
        "filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price
        },
        "total": len(products),
        "products": products,
    }
