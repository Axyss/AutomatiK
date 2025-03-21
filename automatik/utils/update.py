import json

import requests
from requests.exceptions import HTTPError, Timeout
from distutils.version import LooseVersion

from automatik import __version__, logger


def _get_remote_version_data():
    """Gets the last version's tag name from the remote repository."""
    try:
        req = requests.get("https://api.github.com/repos/Axyss/AutomatiK/releases")
        remote_version_data = json.loads(req.content)[0]
    except (HTTPError, Timeout, requests.exceptions.ConnectionError):
        logger.error("Version request to GitHub failed")
    except AttributeError:
        logger.error("Version parsing from GitHub failed")
    else:
        return remote_version_data["tag_name"], remote_version_data["html_url"]


def check_updates():
    """Looks for newer versions."""
    remote_version, remote_version_url = _get_remote_version_data()
    if LooseVersion(remote_version) > LooseVersion(__version__):
        logger.info(f"New version ({remote_version}) available at {remote_version_url}")
