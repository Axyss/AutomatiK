import json
import os
from pathlib import Path

import discord

from automatik import logger


class LanguageManager:
    def __init__(self, language_directory):
        self.languages_data = {}
        self._language_directory = Path(language_directory) / language_directory

    def load_language_files(self):
        for filename in os.listdir(self._language_directory):
            lang_id = os.path.splitext(filename)[0]
            with open(f"{self._language_directory / filename}", encoding="utf-8") as package:
                self.languages_data[lang_id] = Language(json.load(package))
        logger.info(
            f"{len(self.languages_data)} language package(s) loaded: {list(self.languages_data.keys())}"
        )

    def get_language_emoji(self, lang_code):
        return self.languages_data[lang_code].emoji

    def get_message(self, lang_code, message_id):
        try:
            return self.languages_data[lang_code].get_message(message_id)
        except KeyError:  # Fallback if the message in the selected language package does not exist
            logger.debug(f"Message ID '{message_id}' not found in '{lang_code}.json', falling back to 'en'")
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
