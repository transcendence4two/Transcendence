from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controller import tournament as tournament_controller
from src.core.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
)
from src.core.settings import settings
from src.di_config import engine
from src.domain.exceptions import DomainError
from src.domain.models import Base


@asynccontextmanager
async def lifespan(_fastapi_application: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    root_path="/api",
    docs_url="/tournaments/docs",
    redoc_url="/tournaments/redoc",
    openapi_url="/tournaments/openapi.json",
)

app.add_exception_handler(DomainError, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(
    tournament_controller.router,
    prefix="/tournaments",
    tags=["tournaments"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
