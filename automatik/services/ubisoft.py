import json

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.base_service import BaseService
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Service(BaseService):
    SERVICE_NAME = "Ubisoft Connect"
    EMBED_COLOR = 0x0084FF
    SERVICE_IMAGE = "ubisoft_logo.png"

    _base_url = "https://store.ubisoft.com"
    _endpoint = "https://store.ubisoft.com/us/free-games?lang=en_US"

    def make_request(self):
        try:
            return requests.get(self._endpoint)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError) as e:
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException(e)

    def _process_request(self, raw_data):
        parsed_games = []

        try:
            soup = BeautifulSoup(raw_data.content, "html.parser")
            for game in soup.find_all("div", {"class": "product-tile"}):
                if game.find("div", {"class": "card-subtitle"}).text.strip() == "Free":
                    game_title = game.find("div", {"class": "prod-title"}).text.strip()
                    game_link = self._base_url + game.find("a")["href"]
                    game = Game(game_title, game_link, self.SERVICE_ID)
                    parsed_games.append(game)
            return parsed_games
        except (TypeError, KeyError, json.decoder.JSONDecodeError) as e:
            raise InvalidGameDataException(e)

    def get_free_games(self):
        return self._process_request(self.make_request())
