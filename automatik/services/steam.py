import json

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.base_service import BaseService
from automatik.core.errors import GameRetrievalException, InvalidGameDataException
from automatik.core.game import Game


class Service(BaseService):
    SERVICE_NAME = "Steam"
    EMBED_COLOR = 0x1B2838
    SERVICE_IMAGE = "steam_logo.png"

    _url = "https://store.steampowered.com/app/"
    _endpoint = "https://store.steampowered.com/search/results/?query&start=0&count=25&sort_by=Price_ASC&specials=1&infinite=1"

    def is_dlc(self, app_id):
        response = self.make_request(self._url + app_id)
        soup = BeautifulSoup(response.content, "html.parser")
        dlc_area = bool(soup.find("div", {"class": "game_area_dlc_bubble"}))
        purchase_area = bool(soup.find("div", {"class": "game_area_purchase_game_wrapper"}))

        return dlc_area and purchase_area

    def make_request(self, endpoint=None):
        url = endpoint if endpoint else self._endpoint
        try:
            return requests.get(url)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError) as e:
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise GameRetrievalException(e)

    def _process_request(self, raw_data):
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["results_html"]
            soup = BeautifulSoup(processed_data, "html.parser")
            for tag in soup.find_all("a", {"class": "search_result_row ds_collapse_flag"}):
                product_id = tag.get("data-ds-appid") or tag.get("data-ds-bundleid")
                price_div = tag.find("div", {"class": "search_price_discount_combined"})
                if price_div is None or price_div.get("data-price-final") != "0" or self.is_dlc(product_id):
                    continue
                game = Game(tag.find("span", {"class": "title"}).text, self._url + product_id, self.SERVICE_ID)
                parsed_games.append(game)
            return parsed_games
        except (AttributeError, TypeError, KeyError, json.decoder.JSONDecodeError) as e:
            raise InvalidGameDataException(e)

    def get_free_games(self):
        return self._process_request(self.make_request())
