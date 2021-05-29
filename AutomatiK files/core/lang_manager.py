import os
import json

from core.log_manager import logger


class LangManager:
    def __init__(self, lang_dir):
        self.lang_data = {}  # Language packages are stored in memory in this var
        self.lang_dir = lang_dir if lang_dir[-1] == "/" else lang_dir + "/"

    def load_lang_packages(self):
        """Loads all the language packages into memory."""
        for filename in os.listdir(self.lang_dir):
            lang_id = os.path.splitext(filename)[0]
            with open(f"{self.lang_dir + filename}", encoding="utf-8") as package:
                self.lang_data[lang_id] = json.load(package)
        logger.info(str(len(self.lang_data.keys())) + f" language packages loaded")

    def get_lang_packages_metadata(self):
        """Retrieves metadata from the language packages."""
        lang_codes = [id for id in self.lang_data]
        lang_names = [self.lang_data[id]["language"] for id in self.lang_data]
        lang_authors = [self.lang_data[id]["author"] for id in self.lang_data]
        return lang_codes, lang_names, lang_authors

    def get_message(self, lang_code, message_id):
        return self.lang_data[lang_code]["messages"][message_id]
