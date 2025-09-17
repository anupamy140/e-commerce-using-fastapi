from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from app.database import cart_collection, product_collection
from fastapi import Query
from pymongo import ASCENDING, DESCENDING
from app.schemas.cart_schema import CartCreate, CartUpdate, CartResponse

router = APIRouter(prefix="/cart", tags=["Cart"])

def serialize_cart(cart):
    cart["id"] = str(cart["_id"])
    # Convert all ObjectId product_ids in items to strings for frontend
    for item in cart.get("items", []):
        item["product_id"] = str(item["product_id"])
    del cart["_id"]
    return cart

@router.get("/{user_id}", response_model=CartResponse)
def get_cart(user_id: str):
    cart = cart_collection.find_one({"user_id": user_id})
    if not cart:
        # If no cart exists for user, create empty one
        cart = {"user_id": user_id, "items": []}
        cart_collection.insert_one(cart)
        cart = cart_collection.find_one({"user_id": user_id})
    return serialize_cart(cart)

@router.post("/{user_id}/add")
def add_to_cart(user_id: str, item: CartCreate):
    # 1. Check if items list is empty
    if not item.items or len(item.items) == 0:
        raise HTTPException(status_code=400, detail="Cart items list is empty.")

    # 2. Extract the first item (you can extend this later for multiple items)
    cart_item = item.items[0]

    # 3. Validate product ID format and check product existence
    try:
        product = product_collection.find_one({"_id": ObjectId(cart_item.product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID format.")

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 4. Get or create cart
    cart = cart_collection.find_one({"user_id": user_id})
    if not cart:
        cart = {"user_id": user_id, "items": []}
        cart_collection.insert_one(cart)
        cart = cart_collection.find_one({"user_id": user_id})

    # 5. Update quantity if product already exists, else add new
    updated_items = []
    product_found = False
    for existing_item in cart["items"]:
        existing_pid_str = str(existing_item["product_id"])  # Convert ObjectId to string for comparison
        if existing_pid_str == cart_item.product_id:
            new_qty = existing_item["quantity"] + cart_item.quantity
            updated_items.append({"product_id": ObjectId(cart_item.product_id), "quantity": new_qty})
            product_found = True
        else:
            updated_items.append(existing_item)

    if not product_found:
        updated_items.append({"product_id": ObjectId(cart_item.product_id), "quantity": cart_item.quantity})

    # 6. Save updated cart
    cart_collection.update_one({"user_id": user_id}, {"$set": {"items": updated_items}})

    updated_cart = cart_collection.find_one({"user_id": user_id})
    return serialize_cart(updated_cart)

@router.post("/{user_id}/remove")
def remove_from_cart(user_id: str, product_id: str):
    cart = cart_collection.find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    try:
        # Just check if product_id is valid ObjectId string
        ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    # Filter out the product to remove by comparing as strings
    updated_items = [
        item for item in cart["items"]
        if str(item["product_id"]) != product_id
    ]

    cart_collection.update_one({"user_id": user_id}, {"$set": {"items": updated_items}})

    updated_cart = cart_collection.find_one({"user_id": user_id})
    return serialize_cart(updated_cart)


@router.get("/")
def get_all_carts():
    carts = list(cart_collection.find())
    for cart in carts:
        cart["id"] = str(cart["_id"])
        # convert product_ids to strings in items
        for item in cart.get("items", []):
            item["product_id"] = str(item["product_id"])
        del cart["_id"]
    return carts


@router.get("/sort/{order}")
def sort_all_cart_items(
    order: str,
    sort_by: str = Query("title")
):
    # Validate order param
    if order.lower() not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'.")

    sort_order = ASCENDING if order.lower() == "asc" else DESCENDING

    # Fetch all carts
    carts = list(cart_collection.find({}))

    if not carts:
        return {"items": []}

    # Aggregate quantities per product_id (as string)
    product_quantity_map = {}

    for cart in carts:
        for item in cart.get("items", []):
            pid = str(item["product_id"])  # convert ObjectId to string
            qty = item["quantity"]
            product_quantity_map[pid] = product_quantity_map.get(pid, 0) + qty

    # Convert keys to ObjectId
    try:
        product_ids = [ObjectId(pid) for pid in product_quantity_map.keys()]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID in carts.")

    # Fetch and sort products by field
    products = list(
        product_collection.find({"_id": {"$in": product_ids}}).sort(sort_by, sort_order)
    )

    # Attach quantity info and serialize
    for product in products:
        pid_str = str(product["_id"])
        product["quantity"] = product_quantity_map.get(pid_str, 0)
        product["id"] = pid_str
        del product["_id"]

    return {
        "sort_by": sort_by,
        "order": order,
        "total_items": len(products),
        "items": products
    }
