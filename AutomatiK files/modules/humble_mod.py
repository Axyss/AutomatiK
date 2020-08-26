import time

import requests

from core.log_manager import logger
from core.generic_mod import GenericModule


class Humble(GenericModule):

    def __init__(self):

        self.SERVICE_NAME = "Humble Bundle"
        self.MODULE_ID = "humble"
        self.AUTHOR = "Default"
        self.ENDPOINT = "https://www.humblebundle.com/store/api/search?sort=discount&filter=onsale&request=1"
        self.URL = "https://www.humblebundle.com/store/"

    def make_request(self):
        """Makes the request and removes the unnecessary JSON data"""

        try:
            raw_data = requests.get(self.ENDPOINT).json()
            raw_data = raw_data["results"]
            return raw_data
        except:
            logger.error(f"Request to {self.SERVICE_NAME} failed!")

    def process_request(self, raw_data):  # Filters games that are not free
        """Returns the useful information from the request in a tuple"""

        processed_data = []
        for i in raw_data:
            if i["current_price"]["amount"] == 0:  # If game's price is 0
                # Parses relevant data such as name and link and adds It to gameData
                game = (i["human_name"], str(self.URL + i["human_url"]))
                processed_data.append(game)

        return processed_data

    def get_free_games(self):

        processed_data = self.process_request(self.make_request())
        free_games = self.check_database(table="HUMBLE_TABLE", processed_data=processed_data)
        return free_games
