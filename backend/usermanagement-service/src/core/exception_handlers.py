import logging
from typing import Tuple

from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DatabaseError,
    DomainError,
    InvalidCredentialsError,
    InvalidOtpError,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError,
    UserAlreadyExistsError,
)

logger = logging.getLogger(__name__)


DOMAIN_ERROR_MAP: dict[type[DomainError], Tuple[int, str]] = {
    UserAlreadyExistsError: (409, "USER_ALREADY_EXISTS"),
    InvalidCredentialsError: (401, "INVALID_CREDENTIALS"),
    InvalidOtpError: (401, "INVALID_OTP"),
    DatabaseError: (500, "DATABASE_ERROR"),
    TokenMissingError: (401, "TOKEN_MISSING"),
    TokenInvalidError: (401, "TOKEN_INVALID"),
    TokenExpiredError: (401, "TOKEN_EXPIRED"),
}

STATUS_CODE_ERROR_THRESHOLD = 500


async def app_exception_handler(
    request: Request,
    exc: DomainError,
) -> JSONResponse:
    status_code, error_type = _get_error_details(exc)
    _log_exception(error_type, exc, status_code)

    return _create_error_response(
        status_code=status_code,
        error_type=error_type,
        detail=str(exc),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unexpected error occurred: %s",
        str(exc),
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )

    return _create_error_response(
        status_code=500,
        error_type="INTERNAL_ERROR",
        detail="Internal server error occurred",
    )


def _get_error_details(exc: DomainError) -> Tuple[int, str]:
    return DOMAIN_ERROR_MAP.get(
        type(exc),
        (500, "INTERNAL_ERROR"),  # Fallback
    )


def _log_exception(error_type: str, exc: DomainError, status_code: int) -> None:
    log_level = (
        logging.ERROR if status_code >= STATUS_CODE_ERROR_THRESHOLD else logging.WARNING
    )

    logger.log(
        log_level,
        "%s: %s",
        error_type,
        str(exc),
        extra={"error_type": error_type, "exception": exc.__class__.__name__},
    )


def _create_error_response(
    status_code: int,
    error_type: str,
    detail: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error_type": error_type,
            "detail": detail,
        },
    )
