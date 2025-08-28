import json

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout

from automatik import logger
from automatik.core.base_service import BaseService
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Service(BaseService):
    SERVICE_NAME = "Steam"
    EMBED_COLOR = "#1B2838"

    _url = "https://store.steampowered.com/app/"
    _endpoint = "https://store.steampowered.com/search/results/?query&start=0&count=25&sort_by=Price_ASC" \
                "&specials=1&infinite=1"

    def is_dlc(self, app_id):
        response = self.make_request(self._url + app_id)
        soup = BeautifulSoup(response.content, "html.parser")
        dlc_area = bool(soup.find("div", {"class": "game_area_dlc_bubble"}))
        purchase_area = bool(soup.find("div", {"class": "game_area_purchase_game_wrapper"}))

        if dlc_area and purchase_area:
            return True
        elif not dlc_area and purchase_area:
            return False
        else:
            return None

    def make_request(self, endpoint=None):
        url = endpoint if endpoint else self._endpoint
        try:
            raw_data = requests.get(url)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by service \'{self.SERVICE_ID}\' failed")
            raise InvalidGameDataException
        else:
            return raw_data

    def _process_request(self, raw_data):
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["results_html"]
            soup = BeautifulSoup(processed_data, "html.parser")
            for tag in soup.find_all("a", {"class": "search_result_row ds_collapse_flag"}):
                product_id = tag.get("data-ds-appid") if tag.get("data-ds-appid") else tag.get("data-ds-bundleid")
                discount_tag = tag.find("div", {"class": "col search_discount responsive_secondrow"})
                # DLCs must be compared carefully since 'not None' is equal to 'True'.
                if discount_tag is None:
                    continue
                elif discount_tag.find("span").text == "-100%" and self.is_dlc(product_id) is False:
                    game = Game(tag.find("span", {"class": "title"}).text, self._url + product_id, self.SERVICE_ID)
                    parsed_games.append(game)
        except (AttributeError, TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self._process_request(self.make_request())
        return free_games
