from copy import deepcopy
import logging.config

import structlog

from shared.logging import config as logging_config_module


def setup_function():
    structlog.contextvars.clear_contextvars()


def teardown_function():
    structlog.contextvars.clear_contextvars()


def test_configure_logging_uses_argument_service_name_and_development_handlers(
    monkeypatch,
):
    captured = {}

    def fake_dict_config(cfg):
        captured["dict_config"] = cfg

    def fake_structlog_configure(**kwargs):
        captured["structlog_config"] = kwargs

    def fake_send_logs():
        captured["send_logs_called"] = True

    monkeypatch.setenv("SERVICE_NAME", "service-from-env")
    monkeypatch.setenv("ENV", "DEVELOPMENT")
    monkeypatch.setattr(logging.config, "dictConfig", fake_dict_config)
    monkeypatch.setattr(logging_config_module.structlog, "configure", fake_structlog_configure)
    monkeypatch.setattr(logging_config_module, "send_logs", fake_send_logs)

    original_base_config = deepcopy(logging_config_module.config)
    logging_config_module.configure_logging(service_name="service-from-argument")

    runtime_config = captured["dict_config"]
    processors = captured["structlog_config"]["processors"]

    assert runtime_config["loggers"]["uvicorn.error"]["handlers"] == ["uvicorn_default"]
    assert runtime_config["loggers"]["uvicorn.access"]["handlers"] == ["uvicorn_access"]
    assert runtime_config["loggers"]["uvicorn.error"]["level"] == "INFO"
    assert runtime_config["loggers"]["uvicorn.access"]["level"] == "INFO"

    env_event = processors[3](None, None, {})
    service_event = processors[4](None, None, {})

    assert env_event["service.environment"] == "DEVELOPMENT"
    assert service_event["service.name"] == "service-from-argument"
    assert captured["send_logs_called"] is True

    # Ensure global base config is not mutated by runtime adjustments.
    assert logging_config_module.config == original_base_config


def test_configure_logging_uses_env_service_name_outside_development(monkeypatch):
    captured = {}

    def fake_dict_config(cfg):
        captured["dict_config"] = cfg

    def fake_structlog_configure(**kwargs):
        captured["structlog_config"] = kwargs

    monkeypatch.setenv("SERVICE_NAME", "service-from-env")
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setattr(logging.config, "dictConfig", fake_dict_config)
    monkeypatch.setattr(logging_config_module.structlog, "configure", fake_structlog_configure)
    monkeypatch.setattr(logging_config_module, "send_logs", lambda: None)

    logging_config_module.configure_logging()

    runtime_config = captured["dict_config"]
    processors = captured["structlog_config"]["processors"]

    # In non-development environment, uvicorn handlers should stay as base config.
    assert runtime_config["loggers"]["uvicorn.error"]["handlers"] == []
    assert runtime_config["loggers"]["uvicorn.access"]["handlers"] == []

    service_event = processors[4](None, None, {})
    env_event = processors[3](None, None, {})

    assert service_event["service.name"] == "service-from-env"
    assert env_event["service.environment"] == "production"
