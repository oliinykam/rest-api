import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mongodb://mongo_admin:password@localhost:27017"
)

DATABASE_NAME = os.getenv("DATABASE_NAME", "library")

client = MongoClient(DATABASE_URL)

def get_db():
    return client[DATABASE_NAME]
