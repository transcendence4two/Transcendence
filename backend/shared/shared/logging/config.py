import logging
import logging.config
from copy import deepcopy
import os

import structlog

from .processors import (
    add_service,
    add_request_context,
    rename_level_key,
    rename_event_key,
)

from ..sender.send_logs import send_logs


config = {
    "version": 1,
    "formatters": {
        "uvicorn_default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "uvicorn_access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {"class": "logging.StreamHandler"},
        "uvicorn_default": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_default",
        },
        "uvicorn_access": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_access",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
    "loggers": {
        "uvicorn.access": {"handlers": [], "propagate": False},
        "uvicorn.error": {"handlers": [], "propagate": False},
    },
}


def configure_logging(service_name: str = None):
    runtime_config = deepcopy(config)

    service = service_name or os.getenv("SERVICE_NAME", "unknown")
    env = os.getenv("ENV", "development")

    if env.lower() == "development":
        runtime_config["loggers"]["uvicorn.error"] = {
            "handlers": ["uvicorn_default"],
            "level": "INFO",
            "propagate": False,
        }
        runtime_config["loggers"]["uvicorn.access"] = {
            "handlers": ["uvicorn_access"],
            "level": "INFO",
            "propagate": False,
        }

    logging.config.dictConfig(runtime_config)

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
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    send_logs()
