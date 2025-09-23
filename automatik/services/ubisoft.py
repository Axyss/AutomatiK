import json

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.base_service import BaseService
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Service(BaseService):
    SERVICE_NAME = "Ubisoft Connect"
    EMBED_COLOR = 0x0084FF

    _endpoint = "https://public-ubiservices.ubi.com/v1/spaces/news?spaceId=6d0af36b-8226-44b6-a03b" \
                "-4660073a6349"
    _headers = {"ubi-appid": "314d4fef-e568-454a-ae06-43e3bece12a6",
                "ubi-localecode": "en-US",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                              "like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    def make_request(self):
        try:
            return requests.get(self._endpoint, headers=self._headers)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException

    def _process_request(self, raw_data):
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["news"]
            for i in processed_data:
                if i["type"] == "freegame" and i["expirationDate"]:
                    game = Game(i["title"], i["links"][0]["param"], self.SERVICE_ID)
                    parsed_games.append(game)
            return parsed_games
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
                raise InvalidGameDataException

    def get_free_games(self):
        return self._process_request(self.make_request())
