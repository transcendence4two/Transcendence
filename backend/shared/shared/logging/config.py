import logging
import logging.config

import structlog
import os
from .processors import (
    add_service,
    add_request_context,
    rename_level_key,
    rename_event_key,
)

config = {
    "version": 1,
    "handlers": {"default": {"class": "logging.StreamHandler"}},
    "loggers": {
        "uvicorn.access": {"handlers": [], "propagate": False},
        "uvicorn.error": {"handlers": [], "propagate": False},
    },
}


def configure_logging(service_name: str = None):
    logging.config.dictConfig(config)

    service = service_name or os.getenv("SERVICE_NAME", "unknown")
    env = os.getenv("ENV", "development")

    def add_env(_, __, event_dict):
        event_dict["service.environment"] = env
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", key="@timestamp"),
            add_env,
            add_service(service),
            add_request_context,
            rename_level_key,
            rename_event_key,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
