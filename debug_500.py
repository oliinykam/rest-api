
import asyncio
from main import app
from fastapi.testclient import TestClient
from app.core.database import Base, engine
import traceback

async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(setup())

client = TestClient(app, raise_server_exceptions=False)
resp = client.post("/api/auth/register", json={"username": "test_500_user", "password": "testpassword123"})
print("Register:", resp.status_code, resp.text)

resp = client.post("/api/auth/login", json={"username": "test_500_user", "password": "testpassword123"})
print("Login:", resp.status_code, resp.text)
