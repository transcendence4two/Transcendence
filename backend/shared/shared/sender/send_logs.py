import logging
import structlog
import socket
import json


class LogstashTCPHandler(logging.Handler):
    def __init__(self, host="localhost", port=5000):
        super().__init__()
        self.host = host
        self.port = port

    def emit(self, record):
        try:
            log_dict = {
                "message": record.getMessage(),
                "level": record.levelname,
                "logger": record.name,
            }

            log_entry = json.dumps(log_dict)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.sendall((log_entry + "\n").encode("utf-8"))
            sock.close()

        except Exception:
            pass


def send_logs():
    handler = LogstashTCPHandler("localhost", 5000)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    logger = structlog.get_logger()
    context = structlog.contextvars.get_contextvars()
    logger.info("Sending logs to logstash", context=context)
