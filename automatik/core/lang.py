import os
import json

from automatik import logger


class LangLoader:
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
        lang_codes = [id_ for id_ in self.lang_data]
        lang_names = [self.lang_data[id_]["language"] for id_ in self.lang_data]
        lang_authors = [self.lang_data[id_]["author"] for id_ in self.lang_data]
        return lang_codes, lang_names, lang_authors

    def get_message(self, lang_code, message_id):
        try:
            return self.lang_data[lang_code]["messages"][message_id]
        except KeyError:  # Fallback if the message in the selected language package does not exist
            logger.debug(f"Message '{message_id}' could not be found on '{lang_code}.json'. " +
                         "Falling back to 'en_EN'..")
            return self.lang_data["en_EN"]["messages"][message_id]
