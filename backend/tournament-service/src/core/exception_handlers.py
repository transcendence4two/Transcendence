from typing import Tuple

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DatabaseError,
    DomainError,
    MatchmakingQueueError,
    MatchRecordValidationError,
    TournamentMatchNotFoundError,
    TournamentMatchResultError,
    TournamentNotFoundError,
    TournamentParticipantError,
    TournamentStateError,
)

logger = structlog.get_logger()

DOMAIN_ERROR_MAP: dict[type[DomainError], Tuple[int, str]] = {
    TournamentNotFoundError: (404, "TOURNAMENT_NOT_FOUND"),
    TournamentMatchNotFoundError: (404, "TOURNAMENT_MATCH_NOT_FOUND"),
    DatabaseError: (500, "DATABASE_ERROR"),
    MatchmakingQueueError: (409, "MATCHMAKING_QUEUE_ERROR"),
    MatchRecordValidationError: (422, "MATCH_RECORD_VALIDATION_ERROR"),
    TournamentStateError: (409, "TOURNAMENT_STATE_ERROR"),
    TournamentParticipantError: (409, "TOURNAMENT_PARTICIPANT_ERROR"),
    TournamentMatchResultError: (409, "TOURNAMENT_MATCH_RESULT_ERROR"),
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
    logger.exception(
        "Unexpected error occurred",
        error_type=exception.__class__.__name__,
        url_path=request.url.path,
        http_method=request.method,
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
    bound_logger = logger.bind(
        error_type=error_type,
        exception_class=exception.__class__.__name__,
    )
    if status_code >= SERVER_ERROR_THRESHOLD:
        bound_logger.error(str(exception))
    else:
        bound_logger.warning(str(exception))


def _create_error_response(
    status_code: int,
    error_type: str,
    detail: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error_type": error_type, "detail": detail},
    )
