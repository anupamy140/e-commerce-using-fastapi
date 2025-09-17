from fastapi import FastAPI
from app.routes import product_routes, cart_routes, order_routes

app = FastAPI()  # 👈 create FastAPI app instance first

# Include routers
app.include_router(product_routes.router)
app.include_router(cart_routes.router)
app.include_router(order_routes.router)
