import ast
import os

import dotenv


class Config:
    def __init__(self, dotenv_path):
        dotenv.load_dotenv(dotenv_path)
        self._config = os.environ

    def __getattr__(self, attr):
        attr = attr.upper()
        try:
            return ast.literal_eval(self._config[attr])
        except (ValueError, SyntaxError):
            # todo this exception should at least be shown in the debug mode
            pass
        return self._config[attr]
