from automatik.core.config import ConfigManager as _ConfigManager
from automatik.core.log_manager import CustomLogger as _CustomLogger

__version__ = "v2.0"
LOGO_URL = "https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png"
AVATAR_URL = "https://avatars3.githubusercontent.com/u/55812692"
__all__ = ["logger", "__version__", "LOGO_URL", "AVATAR_URL"]

_debug = _ConfigManager("./automatik/config.yml", ignore_logger=True).get_general_value("debug")
_logging_level = "DEBUG" if _debug else "INFO"
logger = _CustomLogger.create_custom_logger("automatik_logger", _logging_level)
