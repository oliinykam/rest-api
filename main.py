from fastapi import FastAPI
from app.api.api import router as book_router

app = FastAPI(title="Library API")

app.include_router(book_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)