import json

import requests

from core.generic_mod import GenericModule
from core.log_manager import logger


class Epic(GenericModule):

    def __init__(self):

        self.SERVICE_NAME = "Epic Games"
        self.MODULE_ID = "epic"
        self.AUTHOR = "Default"
        self.URL = "https://www.epicgames.com/store/es-ES/product/"
        self.ENDPOINT = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-ES&country" \
                        "=ES&allowCountries=ES"

    def make_request(self):
        """Makes the request and removes the unnecessary JSON data"""

        try:
            raw_data = requests.get(self.ENDPOINT)
            raw_data = json.loads(raw_data.content)  # Bytes to json object
            raw_data = raw_data["data"]["Catalog"]["searchStore"]["elements"]  # Cleans the data
            return raw_data

        except:
            logger.error(f"Request to {self.SERVICE_NAME} failed!")

    def process_request(self, raw_data):  # Filters games that are free
        """Returns the useful information form the request"""

        processed_data = []

        for i in raw_data:
            # i["promotions"]["upcomingPromotionalOffers"]
            try:
                if (i["price"]["totalPrice"]["discountPrice"] == i["price"]["totalPrice"]["originalPrice"]) != 0:
                    continue
            except TypeError:
                continue

            # Parses relevant data such as name and link and adds It to parsed_data
            game = (i["title"], str(self.URL + i["productSlug"]))
            processed_data.append(game)
        return processed_data

    def get_free_games(self):

        processed_data = self.process_request(self.make_request())
        free_games = self.check_database(table="EPIC_TABLE", processed_data=processed_data)
        return free_games
