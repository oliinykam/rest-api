import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mongodb://mongo_admin:password@localhost:27017"
)

client = AsyncIOMotorClient(DATABASE_URL)

async def get_db():
    yield client.library
