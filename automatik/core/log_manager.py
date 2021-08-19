import logging
import os
from logging.handlers import TimedRotatingFileHandler


class CustomLogger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET):
        try:
            os.mkdir("./automatik/logs")
        except FileExistsError:
            pass
        super(CustomLogger, self).__init__(name, level)

    @staticmethod
    def create_custom_logger(logger_name, logging_level):
        # Creation of the custom logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging_level)
        formatter = logging.Formatter("%(asctime)s[%(levelname)s]: %(message)s.", "[%H:%M]")

        # Creation of the logger handlers
        stream_h = logging.StreamHandler()
        file_h = TimedRotatingFileHandler("./automatik/logs/latest.log", when="midnight", backupCount=365)

        stream_h.setFormatter(formatter)
        file_h.setFormatter(formatter)

        logger.addHandler(stream_h)
        logger.addHandler(file_h)
        return logger


logging.setLoggerClass(CustomLogger)
# todo Improve this file's structure

