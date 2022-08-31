import ast
import os

import dotenv


class Config:
    def __init__(self, dotenv_path):
        self._DOTENV_PATH = dotenv_path
        if self._is_cfg_stored_in_env():
            self._config = self._get_cfg_from_env()
        else:
            self._config = self._get_cfg_from_file()

    def __getattr__(self, attr):
        attr = attr.upper()
        try:
            return ast.literal_eval(self._config[attr])
        except ValueError:
            # todo this exception should at least be shown in the debug mode
            pass
        return self._config[attr]

    @staticmethod
    def _is_cfg_stored_in_env():
        return "CONFIG_VERSION" in os.environ.keys()

    @staticmethod
    def _get_cfg_from_env():
        return os.environ

    def _get_cfg_from_file(self):
        return dotenv.dotenv_values(self._DOTENV_PATH)
