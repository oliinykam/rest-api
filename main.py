from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.api import router as book_router
from app.database import client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()

app = FastAPI(title="Library API", lifespan=lifespan)

app.include_router(book_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)