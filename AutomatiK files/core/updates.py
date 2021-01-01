import time
import requests
from bs4 import BeautifulSoup

from core.log_manager import logger


class Updates:
    MAX_LENGTH = 25  # Maximum amount of numbers that a version can support
    TIME_INTERVAL = 48  # In hours

    def __init__(self, link, local_version):
        self.raw_local_version = str(local_version)
        self.url = link if link[-1] == "/" else link + "/"  # IMPORTANT: the url must contain a slash at the end

    def get_remote_version(self):
        """Gets the last version of the remote AutomatiK repository."""
        try:
            req = requests.get(self.url)  # Gets the HTML code from the web page
        except:
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

    def convert(self, raw_remote_version):
        """Converts the complex syntax of a version to an integer."""
        if not raw_remote_version:
            return False

        local_version = "".join([x for x in self.raw_local_version if x.isdigit()])
        local_version += "0" * (Updates.MAX_LENGTH - len(local_version))

        remote_version = "".join([x for x in raw_remote_version if x.isdigit()])
        remote_version += "0" * (Updates.MAX_LENGTH - len(remote_version))

        #  If the number of 25 digits of the remote version is higher, then It is a newer one
        if int(remote_version) > int(local_version):
            logger.info(f"New update ({raw_remote_version}) available at {self.url + raw_remote_version}")
            return {"remote": int(remote_version), "local": int(local_version)}

    def start_checking(self):
        """Starts looking for new version every X hours."""
        while True:
            self.convert(self.get_remote_version())
            time.sleep(Updates.TIME_INTERVAL * 3600)
