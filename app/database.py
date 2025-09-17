from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Access the database (make sure the name matches the one in your URI: 'mydb')
db = client["mydb"]

# Define collections
product_collection = db["products"]
cart_collection = db["carts"]
order_collection = db["orders"]
