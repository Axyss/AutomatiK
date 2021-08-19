import json

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.errors import InvalidDataException
from automatik.core.game import Game


class Main:
    def __init__(self):
        """Defines the module parameters."""
        self.SERVICE_NAME = "Epic Games"
        self.MODULE_ID = "epic"
        self.AUTHOR = "Default"
        self.URL = "https://www.epicgames.com/store/us-US/product/"
        self.ENDPOINT = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    def make_request(self):
        """Makes the HTTP request to the Epic Games' backend."""
        try:
            raw_data = requests.get(self.ENDPOINT)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by module \'{self.MODULE_ID}\' failed")
            raise InvalidDataException
        else:
            return raw_data

    def process_request(self, raw_data):
        """Returns a list of free games from the raw data."""
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["data"]["Catalog"]["searchStore"]["elements"]
            for i in processed_data:
                if i["promotions"] and i["promotions"]["promotionalOffers"]:
                    game = Game(i["title"], self.URL + i["productSlug"], self.MODULE_ID)
                    parsed_games.append(game)
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self.process_request(self.make_request())
        return free_games
