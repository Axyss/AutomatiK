import os
import yaml
from core.log_manager import logger


class ConfigManager:
    def __init__(self, filename):
        self.CONFIG_TEMPLATE = ("# We know that putting important credentials inside a plain text file\n"
                                "# might feel a bit scary. That's why now you can use environment variables!\n"
                                "# To use them, follow the next syntax: env(my_new_env_variable).\n"
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
        self.config = None
        self._create_config()
        self.load_config()

    def _create_config(self):
        """Creates the configuration file and dumps in it the configuration template if the file does not exist."""
        if self.FILENAME not in os.listdir("."):
            with open(self.FILENAME, "w") as f:
                f.write(self.CONFIG_TEMPLATE)
                return True
        logger.debug("Configuration file already exists, omitting...")
        return False

    def load_config(self):
        """Loads into memory the information of the configuration file."""
        with open(self.FILENAME, "r") as f:
            config = yaml.safe_load(f.read())
            self.config = config

    @staticmethod
    def _get_env_var(value):
        """
           Obtains the value from the YAML configuration file, directly, or from an environment variable if
           the syntax is: env(my_env_var).
        """
        value = str(value)  # Necessary to try to parse numeric values without crashing
        if value.startswith("env(") and value.endswith(")"):
            env_var = value[value.find("(") + 1: value.rfind(")")]
            return os.getenv(env_var)
        return value

    def get_mongo_value(self, field):
        """Returns the value of a given key from the MONGODB field."""
        return ConfigManager._get_env_var(self.config["MONGODB"][field])

    def get_secret_value(self, field):
        """Returns the value of a given key from the SECRET field."""
        return ConfigManager._get_env_var(self.config["SECRET"][field])
