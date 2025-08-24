import json

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Main:
    def __init__(self):
        """Defines the service parameters."""
        self.SERVICE_NAME = "Ubisoft Connect"
        self.SERVICE_ID = "ubisoft"
        self.ENDPOINT = "https://public-ubiservices.ubi.com/v1/spaces/news?spaceId=6d0af36b-8226-44b6-a03b" \
                        "-4660073a6349"
        self.HEADERS = {"ubi-appid": "314d4fef-e568-454a-ae06-43e3bece12a6",
                        "ubi-localecode": "en-US",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    def make_request(self):
        """Makes the HTTP request to the Ubisoft's backend."""
        try:
            raw_data = requests.get(self.ENDPOINT, headers=self.HEADERS)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException
        else:
            return raw_data

    def process_request(self, raw_data):
        """Returns a list of free games from the raw data."""
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["news"]
            for i in processed_data:
                if i["type"] == "freegame" and i["expirationDate"]:
                    game = Game(i["title"], i["links"][0]["param"], self.SERVICE_ID)
                    parsed_games.append(game)
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self.process_request(self.make_request())
        return free_games
