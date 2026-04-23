import pytest
from fastapi.testclient import TestClient
from main import app as fastapi_app
from app.database import get_db, Base
from app.models.models import Book
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import app.database
import uuid
import uuid6
import os

DATABASE_URL_TEST = "sqlite+aiosqlite:///./test.db"
engine_test = create_async_engine(DATABASE_URL_TEST, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine_test, expire_on_commit=False)

app.database.engine = engine_test
app.database.AsyncSessionLocal = TestingSessionLocal

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def reset_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        seed_book = Book(
            id=uuid6.uuid7(),
            title="Alice`s Adventures in Wonderland",
            author="Lewis Carroll",
            description="A novel about Alice",
            status="available",
            release_year=1865,
        )
        session.add(seed_book)
        await session.commit()
    yield

@pytest.fixture
def client():
    yield TestClient(fastapi_app)

@pytest.fixture(scope="session", autouse=True)
async def cleanup_engine():
    yield
    await engine_test.dispose()
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except OSError:
            pass
