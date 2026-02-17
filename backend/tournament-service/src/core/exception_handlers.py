import logging
from typing import Tuple

from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DatabaseError,
    DomainError,
    TournamentNotFoundError,
)

logger = logging.getLogger(__name__)

DOMAIN_ERROR_MAP: dict[type[DomainError], Tuple[int, str]] = {
    TournamentNotFoundError: (404, "TOURNAMENT_NOT_FOUND"),
    DatabaseError: (500, "DATABASE_ERROR"),
}

SERVER_ERROR_THRESHOLD = 500


async def app_exception_handler(
    request: Request,
    exception: DomainError,
) -> JSONResponse:
    del request
    status_code, error_type = _get_error_details(exception)
    _log_exception(error_type, exception, status_code)

    return _create_error_response(
        status_code=status_code,
        error_type=error_type,
        detail=str(exception),
    )


async def general_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    logger.error(
        "Unexpected error occurred: %s",
        str(exception),
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )
    return _create_error_response(
        status_code=500,
        error_type="INTERNAL_ERROR",
        detail="Internal server error occurred",
    )


def _get_error_details(exception: DomainError) -> Tuple[int, str]:
    return DOMAIN_ERROR_MAP.get(type(exception), (500, "INTERNAL_ERROR"))


def _log_exception(
    error_type: str,
    exception: DomainError,
    status_code: int,
) -> None:
    log_level = (
        logging.ERROR if status_code >= SERVER_ERROR_THRESHOLD else logging.WARNING
    )
    logger.log(
        log_level,
        "%s: %s",
        error_type,
        str(exception),
        extra={"error_type": error_type, "exception": exception.__class__.__name__},
    )


def _create_error_response(
    status_code: int,
    error_type: str,
    detail: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error_type": error_type, "detail": detail},
    )
