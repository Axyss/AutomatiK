import logging
import os
from logging.handlers import TimedRotatingFileHandler


# ANSI color codes for console output
_COLORS = {
    "DEBUG":    "\033[36m",   # Cyan
    "INFO":     "\033[32m",   # Green
    "WARNING":  "\033[33m",   # Yellow
    "ERROR":    "\033[31m",   # Red
    "CRITICAL": "\033[1;31m", # Bold Red
    "RESET":    "\033[0m",
}

_FILE_FORMAT    = "[%(asctime)s] [%(levelname)-8s] %(message)s"
_CONSOLE_FORMAT = "[%(asctime)s] %(levelcolor)s[%(levelname)-8s]%(reset)s %(message)s"
_DATE_FORMAT    = "%Y-%m-%d %H:%M:%S"


class _ColorFormatter(logging.Formatter):
    """Formatter that injects ANSI color codes based on the log level."""

    def format(self, record):
        record.levelcolor = _COLORS.get(record.levelname, "")
        record.reset = _COLORS["RESET"]
        return super().format(record)


def create_logs_folder():
    os.makedirs("./automatik/logs", exist_ok=True)


def create_custom_logger(logger_name: str, logging_level: str) -> logging.Logger:
    """Creates the AutomatiK logger with colored console output and rotating file output."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    # Console handler (colored)
    stream_h = logging.StreamHandler()
    stream_h.setFormatter(_ColorFormatter(_CONSOLE_FORMAT, datefmt=_DATE_FORMAT))

    # File handler (plain text, rotated daily, kept for 90 days)
    file_h = TimedRotatingFileHandler(
        "./automatik/logs/latest.log", when="midnight", backupCount=90, encoding="utf-8"
    )
    file_h.setFormatter(logging.Formatter(_FILE_FORMAT, datefmt=_DATE_FORMAT))

    logger.addHandler(stream_h)
    logger.addHandler(file_h)
    return logger

