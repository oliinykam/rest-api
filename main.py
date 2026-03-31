from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.api import router as book_router
from app.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Library API", lifespan=lifespan)

app.include_router(book_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
