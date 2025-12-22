import json
import time
from functools import wraps
from typing import Optional

import requests
from igdb.wrapper import IGDBWrapper

from automatik import logger


def ensure_token(func):
    """Decorator to ensure token is valid before API calls."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.wrapper or time.time() >= self.token_expiry:
            self._refresh_token()
        return func(self, *args, **kwargs) if self.wrapper else None
    return wrapper


class IGDBClient:

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.wrapper = None
        self.token_expiry = 0
        self._refresh_token()

    def _refresh_token(self):
        """Fetch a new OAuth token from Twitch."""
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
            data = response.json()
            token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            # Refresh 60s before expiry for safety
            self.token_expiry = time.time() + expires_in - 60
            self.wrapper = IGDBWrapper(self.client_id, token)
            logger.debug("IGDB token refreshed successfully")
        except Exception as e:
            logger.error(f"Failed to refresh IGDB token: {e}")
            self.wrapper = None
            self.token_expiry = 0

    @ensure_token
    def get_game_data(self, game_name: str) -> Optional[dict]:
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

