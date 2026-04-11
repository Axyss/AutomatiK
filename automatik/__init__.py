__version__ = "v2.0"
__all__ = ["logger", "__version__", "LOGO_URL", "AVATAR_URL", "SRC_DIR"]

import os

from automatik.utils.log_setup import create_custom_logger as _create_custom_logger
from automatik.utils.log_setup import create_logs_folder as _create_logs_folder
from .core.config import Config as _Config

LOGO_URL = "https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png"
AVATAR_URL = "https://avatars3.githubusercontent.com/u/55812692"
SRC_DIR = os.path.dirname(__file__)

_logging_level = "DEBUG" if _Config(".env").debug_messages else "INFO"
_create_logs_folder()
logger = _create_custom_logger("automatik_logger", _logging_level)
