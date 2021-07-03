import json
import time

import requests
from requests.exceptions import HTTPError, Timeout

from core.log_manager import logger


class Update:
    MAX_LENGTH = 25  # Maximum amount of numbers that a version can support

    def __init__(self, local_version):
        self.LOCAL_VERSION = Update.convert(local_version)

    @staticmethod
    def get_remote_version_data():
        """Gets the last version's tag name from the remote AutomatiK repository."""
        try:
            req = requests.get("https://api.github.com/repos/Axyss/AutomatiK/releases")
            remote_version_data = json.loads(req.content)[0]
            return remote_version_data["tag_name"], remote_version_data["html_url"]
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error("Version request to GitHub failed")
        except AttributeError:
            logger.error("Version parsing from GitHub failed")
        return False

    @staticmethod
    def convert(raw_version):
        """Converts the syntax of a version string into an integer."""
        if not raw_version:
            return False

        parsed_version = "".join([x for x in raw_version if x.isdigit()])
        parsed_version += "0" * (Update.MAX_LENGTH - len(parsed_version))
        return int(parsed_version)

    def check_every_x_days(self, x):
        """Looks for a new version every x days."""
        while True:
            remote_version, remote_version_url = Update.get_remote_version_data()
            #  If the number of 25 digits of the remote version is higher, then it's a newer one
            if Update.convert(remote_version) > self.LOCAL_VERSION:
                logger.info(f"New update ({remote_version}) available at {remote_version_url}")
            time.sleep(24 * 3600 * x)
