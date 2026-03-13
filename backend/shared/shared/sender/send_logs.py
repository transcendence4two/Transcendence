import os
import logging
import structlog
import socket


class LogstashTCPHandler(logging.Handler):
    def __init__(self, host="localhost", port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = None
        self._connect()

    def _connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except Exception as e:
            self.sock = None
            print("Logstash connection error:", e)

    def emit(self, record):
        try:
            if self.sock is None:
                self._connect()
                if self.sock is None:
                    return

            log_entry = self.format(record)
            self.sock.sendall((log_entry + "\n").encode("utf-8"))

        except Exception:
            self.close()
            self.sock = None

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None
        super().close()


def send_logs():
    host = os.getenv("LOGSTASH_HOST", "logstash")
    handler = LogstashTCPHandler(host, 5000)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    logger = structlog.get_logger()
    context = structlog.contextvars.get_contextvars()
    logger.info("Sending logs to logstash", context=context)
