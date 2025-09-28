# This is not a removable service. If you wish to disable it use the '!mk disable' command.

from automatik.core.base_service import BaseService


class Service(BaseService):
    SERVICE_NAME = "Mention"
    EMBED_COLOR = 0x7289DA
    SERVICE_IMAGE = "null.png"

    def make_request(self):
        pass

    def get_free_games(self):
        return []

# todo Altering the state of the mentions should have nothing to do with services
