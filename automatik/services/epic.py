import json

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.base_service import BaseService
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Service(BaseService):
    SERVICE_NAME = "Epic Games"
    EMBED_COLOR = 0x202020

    _product_url = "https://www.epicgames.com/store/us-US/p/"
    _endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    def make_request(self):
        try:
            raw_data = requests.get(self._endpoint)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException
        else:
            return raw_data

    def _process_request(self, raw_data):
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
                    game = Game(element["title"], self._product_url + url_slug, self.SERVICE_ID)
                    parsed_games.append(game)
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self._process_request(self.make_request())
        return free_games
