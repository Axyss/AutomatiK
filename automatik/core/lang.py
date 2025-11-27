import json
import os

import discord

from automatik import logger


class LanguageLoader:
    def __init__(self, lang_dir):
        self.lang_pkgs = {}  # Holds the lang packages in memory
        self._lang_dir = lang_dir if lang_dir[-1] == "/" else lang_dir + "/"

    def load_lang_packages(self):
        """Loads all the language packages into memory."""
        for filename in os.listdir(self._lang_dir):
            lang_id = os.path.splitext(filename)[0]
            with open(f"{self._lang_dir + filename}", encoding="utf-8") as package:
                self.lang_pkgs[lang_id] = Language(json.load(package))
        logger.info(str(len(self.lang_pkgs.keys())) + f" language packages loaded")

    def get_lang_packages(self):
        return self.lang_pkgs.values()

    def get_lang_packages_metadata(self):
        """Retrieves metadata from the language packages."""
        lang_codes = [id_ for id_ in self.lang_pkgs]
        lang_names = [self.lang_pkgs[id_].language for id_ in self.lang_pkgs]
        return lang_codes, lang_names

    def get_message(self, lang_code, message_id):
        try:
            return self.lang_pkgs[lang_code].get_message(message_id)
        except KeyError:  # Fallback if the message in the selected language package does not exist
            logger.debug(f"Message '{message_id}' could not be found on '{lang_code}.json'. " +
                         "Falling back to english..")
            return self.lang_pkgs["en"].get_message(message_id)

class Language:
    def __init__(self, lang_data):
        self.language = lang_data["language"]
        self.emoji = lang_data["emoji"]
        self._messages = lang_data["messages"]

    def get_message(self, message_id):
        return self._messages[message_id]

    def to_select_option(self):
        return discord.SelectOption(label=self.language, emoji=self.emoji)
