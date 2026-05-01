"""
Configuration du logging :
  - Format JSON structuré
  - Sortie stdout (capturée par Docker)
  - Sortie TCP vers Logstash (best-effort, ne casse pas si Logstash est down)
"""
import logging
import logging.handlers
import socket

from pythonjsonlogger import jsonlogger


class SafeLogstashHandler(logging.handlers.SocketHandler):
    """SocketHandler qui ne plante pas si Logstash est inaccessible."""

    def emit(self, record):
        try:
            super().emit(record)
        except (OSError, socket.error):
            # On ne propage pas l'erreur pour ne pas faire tomber l'app
            self.handleError(record)


def setup_logging(service_name: str, logstash_host: str, logstash_port: int) -> logging.Logger:
    """Configure les loggers root + uvicorn en JSON."""
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "@timestamp", "levelname": "level"},
    )

    # Stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Logstash (TCP, best-effort)
    handlers = [stream_handler]
    try:
        logstash_handler = SafeLogstashHandler(logstash_host, logstash_port)
        logstash_handler.setFormatter(formatter)
        handlers.append(logstash_handler)
    except (OSError, socket.gaierror):
        # Logstash pas encore disponible, on continue avec stdout uniquement
        pass

    root = logging.getLogger()
    root.handlers.clear()
    for h in handlers:
        root.addHandler(h)
    root.setLevel(logging.INFO)

    # Uniformiser uvicorn
    for log_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(log_name)
        lg.handlers = handlers
        lg.propagate = False

    logger = logging.getLogger(service_name)
    logger.info("logging_initialized", extra={"service": service_name})
    return logger
