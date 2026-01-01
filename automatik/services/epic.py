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
    SERVICE_IMAGE = "epic_games_logo.png"

    _base_url = "https://store.epicgames.com/store/us-US/"
    _endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    def make_request(self):
        try:
            return requests.get(self._endpoint)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException

    def _process_request(self, raw_data):
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["data"]["Catalog"]["searchStore"]["elements"]
            for element in processed_data:
                promotions = element["promotions"]  # None if there aren't any, so there's no need to use 'get'
                current_price = element["price"]["totalPrice"]["originalPrice"] - element["price"]["totalPrice"]["discount"]

                if current_price != 0 or not promotions or not promotions["promotionalOffers"]:
                    continue

                url_slug = element["productSlug"] if element["productSlug"] else element["offerMappings"][0]["pageSlug"]
                if element["offerType"] == "BUNDLE":
                    product_url = self._base_url + "bundles/" + url_slug
                else:
                    product_url = self._base_url + "p/" + url_slug

                game = Game(element["title"], product_url, self.SERVICE_ID)
                parsed_games.append(game)
            return parsed_games
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException

    def get_free_games(self):
        return self._process_request(self.make_request())
