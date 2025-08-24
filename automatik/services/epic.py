import json

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Main:
    def __init__(self):
        """Defines the service parameters."""
        self.SERVICE_NAME = "Epic Games"
        self.SERVICE_ID = "epic"
        self.URL = "https://www.epicgames.com/store/us-US/p/"
        self.ENDPOINT = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    def make_request(self):
        """Makes the HTTP request to the Epic Games' backend."""
        try:
            raw_data = requests.get(self.ENDPOINT)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException
        else:
            return raw_data

    def process_request(self, raw_data):
        """Returns a list of free games from the raw data."""
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["data"]["Catalog"]["searchStore"]["elements"]
            for element in processed_data:
                promotions = element["promotions"]  # None if there aren't any, so there's no need to use 'get'
                current_price = element["price"]["totalPrice"]["originalPrice"] - \
                                element["price"]["totalPrice"]["discount"]

                # The order of the next if statement is crucial since 'promotions' may be None
                if current_price == 0 and promotions and promotions["promotionalOffers"]:
                    url_slug = element["productSlug"] if element["productSlug"] else element["offerMappings"][0]["pageSlug"]
                    game = Game(element["title"], self.URL + url_slug, self.SERVICE_ID)
                    parsed_games.append(game)
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self.process_request(self.make_request())
        return free_games
