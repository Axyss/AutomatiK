import json
from typing import Optional

import requests
from igdb.wrapper import IGDBWrapper

from automatik import logger


class IGDBClient:

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.wrapper = None
        self._get_token_and_init()

    def _get_token_and_init(self):
        try:
            response = requests.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                }
            )
            response.raise_for_status()
            token = response.json()["access_token"]
            self.wrapper = IGDBWrapper(self.client_id, token)
        except Exception as e:
            logger.error(f"Failed to initialize IGDB client: {e}")
            self.wrapper = None

    def get_game_data(self, game_name: str) -> Optional[dict]:
        if not self.wrapper:
            return None

        try:
            query = f'search "{game_name}"; fields name, summary, rating, aggregated_rating, total_rating, genres.name, first_release_date; limit 1;'
            response = self.wrapper.api_request('games', query)
            games = json.loads(response)
            return games[0] if games else None
        except Exception as e:
            logger.warning(f"Failed to fetch IGDB data for '{game_name}': {e}")
            return None

    @staticmethod
    def rating_to_stars(rating: float) -> str:
        filled_stars = round(rating / 20)
        return "★" * filled_stars + "☆" * (5 - filled_stars)

