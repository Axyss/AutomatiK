import json
import os

import discord

from automatik import logger


class LanguageManager:
    def __init__(self, language_directory):
        self.languages_data = {}
        self._language_directory = language_directory if language_directory[-1] == "/" else language_directory + "/"

    def load_language_files(self):
        """Loads all the language packages into memory."""
        for filename in os.listdir(self._language_directory):
            lang_id = os.path.splitext(filename)[0]
            with open(f"{self._language_directory + filename}", encoding="utf-8") as package:
                self.languages_data[lang_id] = Language(json.load(package))
        logger.info(str(len(self.languages_data.keys())) + f" language packages loaded")

    def get_languages(self):
        return self.languages_data.values()

    def get_languages_metadata(self):
        """Retrieves metadata from the language packages."""
        lang_codes = [id_ for id_ in self.languages_data]
        lang_names = [self.languages_data[id_].language for id_ in self.languages_data]
        return lang_codes, lang_names

    def get_message(self, lang_code, message_id):
        try:
            return self.languages_data[lang_code].get_message(message_id)
        except KeyError:  # Fallback if the message in the selected language package does not exist
            logger.debug(f"Message '{message_id}' could not be found on '{lang_code}.json'. " +
                         "Falling back to english..")
            return self.languages_data["en"].get_message(message_id)

class Language:
    def __init__(self, lang_data):
        self.language = lang_data["language"]
        self.emoji = lang_data["emoji"]
        self._messages = lang_data["messages"]

    def get_message(self, message_id):
        return self._messages[message_id]

    def to_select_option(self):
        return discord.SelectOption(label=self.language, emoji=self.emoji)
