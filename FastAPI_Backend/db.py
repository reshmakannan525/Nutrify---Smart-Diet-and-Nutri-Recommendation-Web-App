from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URL)

db = client["diet_system"]

users_collection = db["users"]
diet_collection = db["diet_plans"]