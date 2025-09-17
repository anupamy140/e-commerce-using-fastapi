# E-Commerce API with FastAPI and MongoDB

## Overview

This project is a simple e-commerce backend built using **FastAPI** and **MongoDB**.  
It supports product management, cart operations, sorting, filtering, and pagination.

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <your_repo_url>
   cd <your_repo_folder>
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   # On Linux/macOS
   source venv/bin/activate

   # On Windows
   venv\Scriptsctivate

   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the root folder and add your MongoDB URI:

   ```ini
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/mydb?retryWrites=true&w=majority
   ```

4. **Run the application**

   ```bash
   uvicorn app.main:app --reload
   ```

   Your API will be accessible at: http://localhost:8000

---

## API Endpoints

### Products

- `GET /products` — Retrieve a list of all products.
- `GET /products/{product_id}` — Retrieve details of a specific product by its ID.
- `GET /products/filter?name={name}` — Filter products by name (case-insensitive partial match).
- `GET /products/sort/{order}` — Sort products by price (`order` can be `asc` or `desc`).
- `GET /products/paginate?page={page}&limit={limit}` — Paginate products list.
  - `page` (default: 1) — page number
  - `limit` (default: 10) — items per page

### Cart

- `GET /cart/{user_id}` — Get the cart details for a specific user.
- `POST /cart/{user_id}/add` — Add items to a user's cart.

  Example request body:

  ```json
  {
    "user_id": "string",
    "items": [
      {
        "product_id": "string",
        "quantity": 1
      }
    ]
  }
  ```

- `POST /cart/{user_id}/remove?product_id={product_id}` — Remove a product from the user's cart.
- `GET /cart/all` — Get all cart items for all users (for admin or debugging).
- `GET /cart/sort/{order}` — Sort all cart items by quantity (`order` can be `asc` or `desc`).
- `GET /cart/filter?product_id={product_id}` — Filter cart items by product ID.

---

## Data Models

### Product
- `_id`: MongoDB ObjectId (string)
- `title`: string
- `description`: string
- `price`: float
- `category`: string
- ... other product-specific fields

### Cart
- `_id`: MongoDB ObjectId (string)
- `user_id`: string
- `items`: list of cart items, each containing:
  - `product_id`: string
  - `quantity`: integer

---

## Notes

- Ensure MongoDB is running and accessible using the URI in `.env`.
- Use JSON format in POST request bodies.
- Pagination defaults: `page=1`, `limit=10`.
- Product and user IDs are strings matching MongoDB ObjectIds.
- Sorting and filtering are case-insensitive where applicable.

---
# e-commerce-using-fastapi
