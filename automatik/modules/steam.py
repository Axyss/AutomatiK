import json

import requests
from requests.exceptions import HTTPError, Timeout
from bs4 import BeautifulSoup

from automatik import logger
from automatik.core.errors import InvalidGameDataException
from automatik.core.game import Game


class Main:
    def __init__(self):
        """Defines the module parameters."""
        self.SERVICE_NAME = "Steam"
        self.MODULE_ID = "steam"
        self.AUTHOR = "Default"
        self.URL = "https://store.steampowered.com/app/"
        self.ENDPOINT = "https://store.steampowered.com/search/results/?query&start=0&count=25&sort_by=Price_ASC" \
                        "&specials=1&infinite=1"

    def is_dlc(self, app_id):
        response = self.make_request(self.URL + app_id)
        soup = BeautifulSoup(response.content, "html.parser")
        return bool(soup.find("div", {"class": "game_area_dlc_bubble"}))

    def make_request(self, endpoint):
        """Makes the HTTP request to the Steam's backend."""
        try:
            raw_data = requests.get(endpoint)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error(f"Request to {self.SERVICE_NAME} by module \'{self.MODULE_ID}\' failed")
            raise InvalidGameDataException
        else:
            return raw_data

    def process_request(self, raw_data):
        """Returns a list of free games from the raw data."""
        parsed_games = []

        try:
            processed_data = json.loads(raw_data.content)["results_html"]
            soup = BeautifulSoup(processed_data, "html.parser")
            for tag in soup.find_all("a", {"class": "search_result_row ds_collapse_flag"}):
                app_id = tag.get("data-ds-appid")
                bundle_id = tag.get("data-ds-bundleid")  # Walrus operator would shine here :(
                product_id = app_id if app_id is not None else bundle_id

                is_free = str(tag.find("div", {"class": "col search_discount responsive_secondrow"})
                                 .find("span").text) == "-100%"
                if is_free and not self.is_dlc(product_id):
                    game = Game(tag.find("span", {"class": "title"}).text, self.URL + product_id, self.MODULE_ID)
                    parsed_games.append(game)
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            raise InvalidGameDataException
        else:
            return parsed_games

    def get_free_games(self):
        free_games = self.process_request(self.make_request(self.ENDPOINT))
        return free_games
