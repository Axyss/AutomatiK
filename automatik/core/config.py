import logging
import os
from distutils.util import strtobool

import yaml

logger = logging.getLogger("automatik_logger")


class ConfigManager:

    def __init__(self, filename, ignore_logger=False):
        self.CONFIG_TEMPLATE = ("# We know writing important credentials inside a plain text file\n"
                                "# might feel a bit scary. That's why now you can use environment variables!\n"
                                "# To use them, follow the next syntax: env(my_new_env_variable).\n\n"
                                "GENERAL:\n"
                                "# Bot owners have access to exclusive commands to help them manage the bot. "
                                "Introduce as many as you want.\n"
                                "# Try replicating the syntax down below with your own Discord tag.\n"
                                "  bot_owners:\n"
                                "#    - 'Axyss#5593'\n"
                                "  debug: false\n"
                                "MONGODB:\n"
                                "  host: '127.0.0.1'\n"
                                "  port: 27017\n"
                                "  user: ''\n"
                                "  password: ''\n"
                                "  auth_source: ''\n"
                                "  auth_mechanism: 'DEFAULT'\n"
                                "SECRET:\n"
                                "  discord_bot_token: ''")
        self.FILENAME = filename
        self.IGNORE_LOGGER = ignore_logger
        self.config = None
        self._create_config()
        self.load_config()

    def _create_config(self):
        """Creates the configuration file and dumps in it the configuration template if the file does not exist."""
        if not os.path.exists(self.FILENAME):
            with open(self.FILENAME, "w") as f:
                f.write(self.CONFIG_TEMPLATE)
                logger.debug("Configuration file created") if not self.IGNORE_LOGGER else None
                return True
        logger.debug("Configuration file already exists, omitting...") if not self.IGNORE_LOGGER else None
        # todo Find a better workaround for when the logger object is called before its creation
        return False

    def load_config(self):
        """Loads into memory the information of the configuration file."""
        with open(self.FILENAME, "r") as f:
            config = yaml.safe_load(f.read())
            self.config = config
        logger.debug("Config LOADED") if not self.IGNORE_LOGGER else None

    @staticmethod
    def _get_env_var(value):
        """
           Returns the value from the YAML configuration file, directly, or from an environment variable if
           the syntax is: env(my_env_var).
        """
        if isinstance(value, list):
            return value

        value = str(value)  # Necessary to try to parse numeric values without crashing
        if value.startswith("env(") and value.endswith(")"):
            env_var = value[value.find("(") + 1: value.rfind(")")]
            return os.getenv(env_var)
        return value
        # todo env vars do not work properly on linux

    def get_general_value(self, field):
        """Returns the value of a given key from the GENERAL field."""
        value = ConfigManager._get_env_var(self.config["GENERAL"][field])
        if field == "debug":
            return strtobool(value)
        else:
            return value

    def get_mongo_value(self, field):
        """Returns the value of a given key from the MONGODB field."""
        value = ConfigManager._get_env_var(self.config["MONGODB"][field])
        if field == "port":
            return int(value)
        else:
            return value

    def get_secret_value(self, field):
        """Returns the value of a given key from the SECRET field."""
        return ConfigManager._get_env_var(self.config["SECRET"][field])
