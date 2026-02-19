import structlog
import os
from .processors import add_service, add_request_context


def configure_logging(service_name: str = None):
    service = service_name or os.getenv("SERVICE_NAME", "unknown")
    env = os.getenv("ENV", "development")

    def add_env(_, __, event_dict):
        event_dict["env"] = env
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_env,
            add_service(service),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            add_request_context,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
