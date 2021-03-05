import os
import json

from core.log_manager import logger


class LangManager:

    def __init__(self, lang_dir):
        self.langs = {}
        self.lang_dir = lang_dir if lang_dir[-1] == "/" else lang_dir + "/"

    def load_lang_packages(self):
        """Loads all the language packages into a dictionary."""
        for filename in os.listdir(self.lang_dir):
            lang_id = os.path.splitext(filename)[0]
            with open(f"{self.lang_dir + filename}", encoding="utf-8") as package:
                self.langs[lang_id] = json.load(package)
        logger.info(str(len(self.langs.keys())) + f" language packages loaded")

    def get_lang_packages_metadata(self):
        """Retrieves metadata from the language packages"""
        lang_codes = [id for id in self.langs]
        lang_names = [self.langs[id]["language"] for id in self.langs]
        lang_authors = [self.langs[id]["author"] for id in self.langs]

        return lang_codes, lang_names, lang_authors

    def get_message(self, lang_code, message_id):
        return self.langs[lang_code]["messages"][message_id]
