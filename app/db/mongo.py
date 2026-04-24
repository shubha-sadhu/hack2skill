from pymongo import MongoClient
import os
client = MongoClient(os.getenv("MONGO_URL"))
db = client["chainguard"]
users = db["users"]