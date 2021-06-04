import time
import requests
from requests.exceptions import HTTPError, Timeout
from bs4 import BeautifulSoup

from core.log_manager import logger


class Update:
    MAX_LENGTH = 25  # Maximum amount of numbers that a version can support

    def __init__(self, link, local_version):
        self.LOCAL_VERSION = Update.convert(local_version)
        self.remote_version = None
        self.url = link if link[-1] == "/" else link + "/"  # IMPORTANT: the url must contain a slash at the end

    def get_remote_version(self):
        """Gets the last version of the remote AutomatiK repository."""
        try:
            req = requests.get(self.url)
        except (HTTPError, Timeout, requests.exceptions.ConnectionError):
            logger.error("Version request to GitHub failed")
            return False

        soup = BeautifulSoup(req.content, "html.parser")
        try:
            remote_version = soup.find("span",  # Type of container
                                       {"class": "css-truncate-target"},  # Additional attrs
                                       recursive=True).text  # Parameters of the search
        except AttributeError:
            logger.error("Version parsing from GitHub failed")
            return False

        return remote_version

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
            self.remote_version = self.get_remote_version()
            #  If the number of 25 digits of the remote version is higher, then it's a newer one
            if Update.convert(self.remote_version) > self.LOCAL_VERSION:
                logger.info(f"New update ({self.remote_version}) available at {self.url + self.remote_version}")
            time.sleep(24 * 3600 * x)
