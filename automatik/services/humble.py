import json

from curl_cffi import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError

from automatik import logger
from automatik.core.base_service import BaseService
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Service(BaseService):
    SERVICE_NAME = "Humble Bundle"
    EMBED_COLOR = 0xCC2929

    _endpoint = "https://www.humblebundle.com/store/api/search?sort=discount&filter=onsale&request=1"
    _url = "https://www.humblebundle.com/store/"

    def make_request(self):
        try:
            return requests.get(self._endpoint, impersonate="chrome")
        except (HTTPError, Timeout, ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException

    def _process_request(self, raw_data):
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.text)["results"]
            for i in processed_data:
                if i["current_price"]["amount"] == 0:
                    game = Game(i["human_name"], self._url + i["human_url"], self.SERVICE_ID)
                    parsed_games.append(game)
            return parsed_games
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException

    def get_free_games(self):
        return self._process_request(self.make_request())
