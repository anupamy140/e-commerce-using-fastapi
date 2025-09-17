from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import product_routes, cart_routes, order_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ['http://localhost:5173']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(product_routes.router)
app.include_router(cart_routes.router)
app.include_router(order_routes.router)

# 👇 Root route with full API route summary
@app.get("/")
async def root():
    return {
        "message": "👋 Welcome to the E-Commerce API!",
        "available_routes": {
            "Products": [
                {"method": "GET", "path": "/products/", "desc": "Get all products"},
                {"method": "POST", "path": "/products/", "desc": "Create new product"},
                {"method": "PUT", "path": "/products/{product_id}", "desc": "Update product"},
                {"method": "DELETE", "path": "/products/{product_id}", "desc": "Delete product"},
                {"method": "GET", "path": "/products/sort/{order}", "desc": "Get products sorted"},
                {"method": "GET", "path": "/products/filter", "desc": "Filter products"},
            ],
            "Cart": [
                {"method": "GET", "path": "/cart/{user_id}", "desc": "Get user's cart"},
                {"method": "POST", "path": "/cart/{user_id}/add", "desc": "Add item to cart"},
                {"method": "POST", "path": "/cart/{user_id}/remove", "desc": "Remove item from cart"},
                {"method": "GET", "path": "/cart/", "desc": "Get all carts"},
                {"method": "GET", "path": "/cart/sort/{order}", "desc": "Sort cart items"},
            ],
            "Orders": [
                {"method": "POST", "path": "/orders/", "desc": "Create new order"},
                {"method": "GET", "path": "/orders/{user_id}", "desc": "Get orders by user"},
                {"method": "PATCH", "path": "/orders/{order_id}/status", "desc": "Update order status"},
            ]
        },
        "docs": "/docs",
        "note": "Visit /docs for Swagger UI and testing endpoints interactively."
    }
