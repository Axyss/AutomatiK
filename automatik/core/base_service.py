from abc import ABC, abstractmethod
from typing import List

from requests import Request

from automatik.core.game import Game


class BaseService(ABC):
    @property
    @abstractmethod
    def SERVICE_NAME(self):
        pass

    @property
    @abstractmethod
    def SERVICE_ID(self):
        pass

    @property
    @abstractmethod
    def EMBED_COLOR(self):
        pass

    @abstractmethod
    def make_request(self) -> Request:
        """Makes the HTTP request to the service's backend."""
        pass

    @abstractmethod
    def get_free_games(self) -> List[Game]:
        pass