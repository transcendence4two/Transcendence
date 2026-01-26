import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    logger.log(log_level, f"{exc.error_type}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": exc.error_type,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "internal error application",
            "error_type": "INTERNAL_ERROR",
        },
    )
