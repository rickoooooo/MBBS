import logging
from utils.config import config

# Global var which can be imported and used to write formatted log messages
logger = logging.getLogger(__name__)

log_level = config["main"]["log_level"]

match log_level:
    case "NOTSET":
        log_level = logging.NOTSET
    case "DEBUG":
        log_level = logging.DEBUG
    case "INFO":
        log_level = logging.INFO
    case "WARNING":
        log_level = logging.WARNING
    case "ERROR":
        log_level = logging.ERROR
    case "CRITICAL":
        log_level = logging.CRITICAL
    case _:
        log_level = logging.DEBUG

logging.basicConfig(level=log_level)
