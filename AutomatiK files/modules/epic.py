import json
import requests

from core.module_manager import Game
from core.log_manager import logger


class Epic:

    def __init__(self):
        self.SERVICE_NAME = "Epic Games"
        self.MODULE_ID = "epic"
        self.AUTHOR = "Default"
        self.URL = "https://www.epicgames.com/store/us-US/product/"
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
            logger.error(f"Request to {self.SERVICE_NAME} by module \'{self.MODULE_ID}\' failed")
            return False

    def process_request(self, raw_data):  # Filters games that are free
        """Returns the useful information from the request"""

        processed_data = []

        if not raw_data:
            return False
        try:
            for i in raw_data:
                # (i["price"]["totalPrice"]["discountPrice"] == i["price"]["totalPrice"]["originalPrice"]) != 0
                if i["promotions"]["promotionalOffers"]:
                    game = Game(i["title"], str(self.URL + i["productSlug"]))
                    processed_data.append(game)
        except (TypeError, KeyError):
            logger.debug(f"{self.SERVICE_NAME} by module \'{self.MODULE_ID}\' couldn't be processed")
            return False

        return processed_data

    def get_free_games(self):

        free_games = self.process_request(self.make_request())
        return free_games
