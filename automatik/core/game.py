import datetime

from curl_cffi import requests
from bs4 import BeautifulSoup


class Game:
    def __init__(self, name, link, service_id, date=None):
        self.NAME = name
        self.LINK = link
        self.SERVICE_ID = service_id  # Service ID of the service which generated the instance
        self.DATE = str(datetime.datetime.now()) if date is None else date

    def __eq__(self, other):
        """When comparing two Game objects only the link and service ID attributes will matter."""
        return self.LINK == other.LINK and self.SERVICE_ID == other.SERVICE_ID

    @property
    def promo_img_url(self):
        response = requests.get(self.LINK, impersonate="chrome")
        bs4 = BeautifulSoup(response.content, "html.parser")
        img_tag = bs4.find("meta", property="og:image")
        return img_tag["content"] if img_tag else None


class GameAdapter:
    @staticmethod
    def to_dict(game: Game):
        """Converts a 'Game' instance into a dictionary."""
        return {"name": game.NAME,
                "link": game.LINK,
                "service_id": game.SERVICE_ID,
                "date": game.DATE}

    @staticmethod
    def to_object(game_dict):
        """Converts a compatible dictionary into a 'Game' instance."""
        if game_dict.get("date") is None:
            game_dict["date"] = str(datetime.datetime.now())
        return Game(name=game_dict["name"], link=game_dict["link"],
                    service_id=game_dict["service_id"], date=game_dict["date"])
