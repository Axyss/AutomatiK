import os
from logging.handlers import TimedRotatingFileHandler

import logging


def create_logs_folder():
    try:
        os.mkdir("./automatik/logs")
    except FileExistsError:
        pass

def create_custom_logger(logger_name, logging_level):
    """Creates the default AutomatiK logger."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    formatter = logging.Formatter("%(asctime)s[%(levelname)s]: %(message)s.", "[%H:%M]")
    # Logger handlers
    stream_h = logging.StreamHandler()
    file_h = TimedRotatingFileHandler("./automatik/logs/latest.log", when="midnight", backupCount=365)
    stream_h.setFormatter(formatter)
    file_h.setFormatter(formatter)
    logger.addHandler(stream_h)
    logger.addHandler(file_h)
    return logger
