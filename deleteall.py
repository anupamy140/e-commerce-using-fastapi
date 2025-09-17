from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["mydb"]
product_collection = db["products"]

# Delete all documents in the products collection
result = product_collection.delete_many({})

print(f"🗑️ Deleted {result.deleted_count} products from the database.")
