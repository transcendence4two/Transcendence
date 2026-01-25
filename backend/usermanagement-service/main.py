from fastapi import FastAPI
from src.core.settings import settings
from src.core.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
)
from src.domain.exceptions import AppException
from src.controller import user as user_controller

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Register global exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Routes
app.include_router(user_controller.router, prefix="/users", tags=["users"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
