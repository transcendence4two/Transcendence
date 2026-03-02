import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from shared import configure_logging, logging_middleware, request_context_middleware

from src.controller import auth as auth_controller
from src.controller import user as user_controller
from src.core.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
)
from src.core.settings import settings
from src.di_config import engine
from src.domain.exceptions import DomainError
from src.domain.models import Base

configure_logging(service_name="usermanagement-service")

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception:
            if attempt == max_attempts:
                raise
            await asyncio.sleep(1)

    logger.info("Usermanagement service started")

    yield

    logger.info("Usermanagement service terminated")

    await engine.dispose()
    logging.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    root_path="/api",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Exceptions handler
app.add_exception_handler(DomainError, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.middleware("http")(logging_middleware())
app.middleware("http")(request_context_middleware())

# Routes
app.include_router(user_controller.router, prefix="/users", tags=["users"])
app.include_router(auth_controller.router, prefix="/auth", tags=["auth"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
