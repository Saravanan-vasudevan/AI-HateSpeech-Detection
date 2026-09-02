import os

from passlib.context import CryptContext
from pymongo import MongoClient


# Read database and admin settings from environment variables.
connection_string = os.environ.get("DB_STRING")
db_name = os.environ.get("DB_NAME", "Hate_App")
admin_username = os.environ.get("ADMIN_USERNAME")
admin_password = os.environ.get("ADMIN_PASSWORD")

if not connection_string:
    raise RuntimeError("DB_STRING environment variable is required")
if not admin_username or not admin_password:
    raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD are required")

# Connect to the database.
client = MongoClient(connection_string)
db = client[db_name]
users_collection = db["users"]

# Hash the password before saving the admin user.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_pwd = pwd_context.hash(admin_password)

user_doc = {
    "username": admin_username,
    "hashed_password": hashed_pwd,
    "role": "admin",
}

users_collection.insert_one(user_doc)
print("Admin user registered directly to MongoDB successfully!")
