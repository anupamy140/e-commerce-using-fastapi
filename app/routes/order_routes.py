from fastapi import APIRouter, HTTPException
from app.database import cart_collection, order_collection, product_collection
from bson import ObjectId
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatusUpdate
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

def serialize_order(order):
    order["id"] = str(order["_id"])
    del order["_id"]
    return order

# ✅ Create a new order from the cart
@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate):
    # Get the user's cart
    cart = cart_collection.find_one({"user_id": order_data.user_id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    total = 0

    for item in cart["items"]:
        product = product_collection.find_one({"_id": ObjectId(item["product_id"])})
        if not product:
            continue  # skip invalid products

        item_total = product["price"] * item["quantity"]
        total += item_total

        order_items.append({
            "product_id": str(product["_id"]),
            "quantity": item["quantity"],
            "price": product["price"]
        })

    # Save the order
    order = {
        "user_id": order_data.user_id,
        "items": order_items,
        "total": total,
        "status": "pending"
    }

    result = order_collection.insert_one(order)

    # Clear the cart after checkout
    cart_collection.update_one({"user_id": order_data.user_id}, {"$set": {"items": []}})

    saved_order = order_collection.find_one({"_id": result.inserted_id})
    return serialize_order(saved_order)

# ✅ Get all orders for a user
@router.get("/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: str):
    orders = order_collection.find({"user_id": user_id})
    return [serialize_order(o) for o in orders]

# ✅ Update order status (e.g., shipped, delivered, etc.)
@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    allowed_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    new_status = status_update.status.lower()

    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed values: {allowed_statuses}")

    result = order_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    updated_order = order_collection.find_one({"_id": ObjectId(order_id)})
    return serialize_order(updated_order)
