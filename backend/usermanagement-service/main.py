import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controller import user as user_controller
from src.core.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
)
from src.core.settings import settings
from src.di_config import engine
from src.domain.exceptions import DomainError
from src.domain.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Creating tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down application...")
    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# Exceptions handler
app.add_exception_handler(DomainError, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Routes
app.include_router(user_controller.router, prefix="/users", tags=["users"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
