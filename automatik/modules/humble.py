import json

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Main:
    def __init__(self):
        """Defines the module parameters."""
        self.SERVICE_NAME = "Humble Bundle"
        self.MODULE_ID = "humble"
        self.AUTHOR = "Default"
        self.ENDPOINT = "https://www.humblebundle.com/store/api/search?sort=discount&filter=onsale&request=1"
        self.URL = "https://www.humblebundle.com/store/"

    def make_request(self):
        """Makes the HTTP request to the Humble Bundle's backend."""
        try:
            raw_data = requests.get(self.ENDPOINT)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by module \'{self.MODULE_ID}\' failed")
            raise InvalidGameDataException
        else:
            return raw_data

    def process_request(self, raw_data):
        """Returns a list of free games from the raw data."""
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["results"]
            for i in processed_data:
                if i["current_price"]["amount"] == 0:  # If game's price is 0
                    game = Game(i["human_name"], self.URL + i["human_url"], self.MODULE_ID)
                    parsed_games.append(game)
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self.process_request(self.make_request())
        return free_games
