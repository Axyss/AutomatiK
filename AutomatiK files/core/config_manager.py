import json
import os

from core.log_manager import logger


class ConfigManager:

    def __init__(self, config_name):
        self.config_name = config_name
        self.data_config = None  # Loaded config

        # Template of the config
        self.data_template = {"mentioned_role": "<@&1234>",
                              "lang": "en_EN"}

    def create_config_keys(self, modules):
        """Creates fields in the configuration file for new modules."""
        for i in modules:
            if i.MODULE_ID not in list(self.data_config.keys()):
                self.edit_config(f"{i.MODULE_ID}_status", True)

    def check_config_changes(self):
        """Adds new fields to the configuration If the template has more."""
        template_keys = list(self.data_template.keys())
        current_keys = list(self.data_config.keys())

        for i in template_keys:  # Checks the differences between configs
            if i in current_keys:
                continue
            else:
                self.edit_config(i, self.data_template[i])  # Adds the element using the value from the template
                logger.debug(f"New field detected in the configuration template. "
                             f"Adding '{i}': '{self.data_template[i]}'")

    def load_config(self):
        """Loads the config from the file."""
        if self.config_name in os.listdir("."):  # If config file already exists

            with open(self.config_name, "r") as file:
                self.data_config = json.load(file)  # Loads config
                file.close()

        else:  # Creates the config file and writes the template into It
            with open(self.config_name, "w") as file:
                json.dump(self.data_template, file, indent=2)  # Injects the template
                file.close()
                self.data_config = self.data_template  # Loads the template into the current config
        logger.info("Configuration loaded")

    def edit_config(self, key, value):
        """Provides a handy way to modify both configs (permanent and loaded)."""
        self.data_config[key] = value  # Alters loaded config
        file = open(self.config_name, "w")
        json.dump(self.data_config, file, indent=2)  # Rewrites the permanent config using the loaded
        file.close()
        logger.debug(f"Configuration key '{key}' was successfully assigned the value '{value}'")