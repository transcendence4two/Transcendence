import time
import uuid

import structlog
from fastapi import Request


def request_context_middleware():
    async def middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        trace_id = request.headers.get("x-trace-id") or request_id

        route = request.scope.get("route")
        route_path = route.path if route else request.url.path

        structlog.contextvars.bind_contextvars(
            **{"http.request.id": request_id},
            **{"trace.id": trace_id},
            **{"http.request.method": request.method},
            **{"url.path": request.url.path},
            **{"url.route": route_path},
            **{"client.address": request.client.host if request.client else None},
            **{"user_agent.original": request.headers.get("user-agent")},
        )

        request.state.request_id = request_id
        request.state.start_at = time.perf_counter_ns()

        logger = structlog.get_logger()
        await logger.ainfo("request_received", message="Request received")

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id

        return response

    return middleware
