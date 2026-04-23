import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mongodb://mongo_admin:password@localhost:27017"
)

DATABASE_NAME = os.getenv("DATABASE_NAME", "library")

client = AsyncIOMotorClient(DATABASE_URL)

async def get_db():
    yield client[DATABASE_NAME]
