__version__ = "v1.4"
__all__ = ["logger", "__version__", "LOGO_URL", "AVATAR_URL"]

from .core.config import ConfigManager as _ConfigManager
from .core.logging import create_custom_logger as _create_custom_logger
from .core.logging import create_logs_folder as _create_logs_folder

LOGO_URL = "https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png"
AVATAR_URL = "https://avatars3.githubusercontent.com/u/55812692"

_debug = _ConfigManager("./automatik/config.yml", __version__, ignore_logger=True).get_general_value("debug")
_logging_level = "DEBUG" if _debug else "INFO"
_create_logs_folder()
logger = _create_custom_logger("automatik_logger", _logging_level)
