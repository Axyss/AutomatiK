import requests
from requests.exceptions import HTTPError, Timeout

from core.module_manager import Game
from core.log_manager import logger


class Main:

    def __init__(self):
        """Defines the module parameters."""
        self.SERVICE_NAME = "Humble Bundle"
        self.MODULE_ID = "humble"
        self.AUTHOR = "Default"
        self.ENDPOINT = "https://www.humblebundle.com/store/api/search?sort=discount&filter=onsale&request=1"
        self.URL = "https://www.humblebundle.com/store/"

    def make_request(self):
        """Makes the request and removes the unnecessary JSON data."""
        try:
            raw_data = requests.get(self.ENDPOINT).json()
            raw_data = raw_data["results"]
            return raw_data
        except (HTTPError, Timeout, requests.exceptions.ConnectionError, TypeError):
            logger.error(f"Request to {self.SERVICE_NAME} by module \'{self.MODULE_ID}\' failed")
            return False

    def process_request(self, raw_data):
        """Returns a list of free games from the raw data."""
        processed_data = []

        if not raw_data:
            return False
        try:
            for i in raw_data:
                if i["current_price"]["amount"] == 0:  # If game's price is 0
                    # Parses relevant data such as name and link and adds It to gameData
                    game = Game(i["human_name"], str(self.URL + i["human_url"]))
                    processed_data.append(game)
        except (TypeError, KeyError):
            logger.exception(f"Data from module \'{self.MODULE_ID}\' couldn't be processed")

        return processed_data

    def get_free_games(self):
        free_games = self.process_request(self.make_request())
        return free_games
