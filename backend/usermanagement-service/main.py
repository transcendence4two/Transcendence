from fastapi import FastAPI
from .core.config import settings

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}