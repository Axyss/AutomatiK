import logging
import os
from logging.handlers import TimedRotatingFileHandler


class LogManager(logging.Logger):

    def __init__(self, name, level=logging.NOTSET):
        try:
            os.mkdir("./logs")
        except FileExistsError:
            pass

        super(LogManager, self).__init__(name, level)

    def critical(self, msg, *args, **kwargs):
        super().critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        super().error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        super().info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        super().debug(msg, *args, **kwargs)


logging.setLoggerClass(LogManager)

# Creation of the custom logger
logger = logging.getLogger("regular_logger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s[%(levelname)s]: %(message)s", "[%H:%M]")

stream_h = logging.StreamHandler()
file_h = TimedRotatingFileHandler("./logs/latest.log", when="midnight", backupCount=365)

stream_h.setFormatter(formatter)
file_h.setFormatter(formatter)

logger.addHandler(stream_h)
logger.addHandler(file_h)
