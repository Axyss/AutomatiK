import os
import json

from core.log_manager import logger


class LangManager:

    def __init__(self, lang_dir):
        self.lang = None
        self.lang_name = None
        self.lang_author = None
        self.lang_dir = lang_dir if lang_dir[-1] == "/" else lang_dir + "/"

    def load_lang(self, chosen_lang):
        """Loads the language file based on the 'lang' option from config.json"""

        file = open(f"{self.lang_dir}{chosen_lang}.json", encoding="utf-8")
        self.lang = json.load(file)["messages"]
        file.close()
        logger.info(f"Language '{chosen_lang}' loaded")

    def get_lang_ids(self):
        """Obtains a list containing all the available languages for AutomatiK"""

        language_list = os.listdir(self.lang_dir)  # Obtains the name of the files in lang to generate a list
        parsed_language_list = []

        for i in language_list:  # Adds to the new list the file names without their extensions
            parsed_language_list.append(i[0:i.rindex(".")])

        return parsed_language_list

    def get_lang_metadata(self):
        """Retrieves metadata from the language packages"""

        lang_name = []
        lang_author = []

        for i in os.listdir(self.lang_dir):
            file = open(self.lang_dir + i, encoding="utf-8")
            metadata = json.load(file)

            lang_name.append(metadata["language"])
            lang_author.append(metadata["author"])

        return lang_name, lang_author
