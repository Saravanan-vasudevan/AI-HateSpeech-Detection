import os

import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('credentials.env')


connection_string = os.environ.get("DB_STRING")
db_password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME", "Hate_App")
admin_username = os.environ.get("ADMIN_USERNAME")
admin_password = os.environ.get("ADMIN_PASSWORD")

if not connection_string:
    raise RuntimeError("DB_STRING environment variable is required")
if '<db_password>' in connection_string:
    if not db_password:
        raise RuntimeError("DB_PASSWORD is required by the connection string")
    connection_string = connection_string.replace('<db_password>', db_password)
if not admin_username or not admin_password:
    raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD are required")

client = MongoClient(connection_string)
db = client[db_name]
users_collection = db["user"]

hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

user_doc = {
    "username": admin_username,
    "password": hashed_password,
    "first_name": "Initial",
    "last_name": "Admin",
    "admin": True,
}

users_collection.update_one(
    {"username": admin_username},
    {"$set": user_doc},
    upsert=True,
)
print("Admin user registered directly to MongoDB successfully!")
