import time

import structlog
from fastapi import JSONResponse, Request


def logging_middleware():
    async def middleware(request: Request, call_next):
        error = None
        response = None
        logger = structlog.get_logger()

        try:
            response = await call_next(request)

        except Exception as e:
            logger.exception("request_failed", message="Request failed", error=str(e))
            error = e
            response = JSONResponse(
                status_code=500, content={"detail": "Internal error"}
            )

        if error is None and response.status_code < 400:
            event_outcome = "success"
        else:
            event_outcome = "failure"

        duration_ns = time.perf_counter_ns() - request.state.start_at

        structlog.contextvars.bind_contextvars(
            **{"http.response.status_code": response.status_code},
            **{"event.outcome": event_outcome},
            **{"error.type": type(error).__name__ if error else None},
            **{"event.duration": duration_ns},
        )

        if error:
            logger.info("request_failed", message="Request completed with error")
        else:
            logger.info("request_completed", message="Request completed successfully")

        # CLEAN - removes everything to next request
        structlog.contextvars.clear_contextvars()

        return response

    return middleware
