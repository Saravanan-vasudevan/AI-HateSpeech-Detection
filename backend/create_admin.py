from passlib.context import CryptContext
from pymongo import MongoClient

# 1. Connect to MongoDB
client = MongoClient("mongodb+srv://username:<db_password>@cluster.example.mongodb.net/")
db = client["Hate_App"]
users_collection = db["users"] # Matches standard FastAPI auth tutorials

# 2. Hash the password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_pwd = pwd_context.hash("Admin1234!")

# 3. Insert the user
user_doc = {
    "username": "Admin1234",
    "hashed_password": hashed_pwd,
    "role": "admin"
}

users_collection.insert_one(user_doc)
print("Admin user registered directly to MongoDB successfully!")