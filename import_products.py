import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import urllib3

# ⛔️ Disable warnings (only for development!)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["mydb"]
product_collection = db["products"]

# Fetch products with SSL verification disabled
response = requests.get("https://dummyjson.com/products", verify=False)

if response.status_code == 200:
    products = response.json().get("products", [])
    product_collection.delete_many({})  # Optional: clear old data
    for product in products:
        product.pop("id", None)  # Remove ID so MongoDB can create its own
        product_collection.insert_one(product)
    print(f"✅ Imported {len(products)} products successfully.")
else:
    print("❌ Failed to fetch data from DummyJSON API.")
