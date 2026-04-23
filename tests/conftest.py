import pytest
import os
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

os.environ["DATABASE_NAME"] = "library_test"

from main import app as fastapi_app
from app.database import get_db

DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST", "mongodb://mongo_admin:password@localhost:27017")
DATABASE_NAME_TEST = os.getenv("DATABASE_NAME", "library_test")


async def override_get_db():
    test_mongo_client = AsyncIOMotorClient(DATABASE_URL_TEST)
    try:
        yield test_mongo_client[DATABASE_NAME_TEST]
    finally:
        test_mongo_client.close()

fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    sync_client = MongoClient(DATABASE_URL_TEST)
    db_test = sync_client[DATABASE_NAME_TEST]
    
    db_test.books.drop()

    seed_book = {
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "description": "A novel about Alice",
        "status": "available",
        "release_year": 1865,
    }
    db_test.books.insert_one(seed_book)
    
    sync_client.close()
    yield


@pytest.fixture
def client():
    with TestClient(fastapi_app) as test_client:
        yield test_client