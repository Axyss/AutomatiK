import json
import os
from core.log_manager import logger


class ConfigManager:
    def __init__(self, filename):
        self.CONFIG_TEMPLATE = {"MONGODB": {
                                    "HOST": "127.0.0.1",
                                    "PORT": "27017",
                                    "USER": "",
                                    "PASSWORD": "",
                                    "AUTH_SOURCE": "",
                                    "AUTH_MECHANISM": "DEFAULT"
                                    }
                                }
        self.FILENAME = filename
        self.config = None
        self._create_config()
        self.load_config()

    def _create_config(self):
        """Creates the configuration file and dumps in it the configuration template if the file does not exist."""
        try:
            open(self.FILENAME, "x").close()
            with open(self.FILENAME, "w") as f:
                json.dump(self.CONFIG_TEMPLATE, f, indent=2)
        except FileExistsError:
            logger.debug("Configuration file already exists, omitting...")

    def load_config(self):
        """Loads into memory the information of the configuration file."""
        with open(self.FILENAME, "r") as f:
            config = json.load(f)
            self.config = config

    @staticmethod
    def _parse_var(value):
        """
           Obtains the value from the JSON configuration file, directly, or from an environment variable if
           the syntax is: var('env_var').
        """
        if value.startswith("env('") and value.endswith("')"):
            env_var = value[value.find("'") + 1: value.rfind("'")]
            return os.getenv(env_var)
        else:
            return value

    def get_mongo_host(self):
        return ConfigManager._parse_var(self.config["MONGODB"]["HOST"])

    def get_mongo_port(self):
        return ConfigManager._parse_var(self.config["MONGODB"]["PORT"])

    def get_mongo_user(self):
        return ConfigManager._parse_var(self.config["MONGODB"]["USER"])

    def get_mongo_pwd(self):
        return ConfigManager._parse_var(self.config["MONGODB"]["PASSWORD"])

    def get_mongo_auth_source(self):
        return ConfigManager._parse_var(self.config["MONGODB"]["AUTH_SOURCE"])

    def get_mongo_auth_mechanism(self):
        return ConfigManager._parse_var(self.config["MONGODB"]["AUTH_MECHANISM"])
