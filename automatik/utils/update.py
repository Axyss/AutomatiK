import json
import traceback

import requests
from requests.exceptions import HTTPError, Timeout

from automatik import __version__, logger


def _get_remote_version_data():
    """Gets the last version's tag name from the remote repository."""
    try:
        req = requests.get("https://api.github.com/repos/Axyss/AutomatiK/releases")
        remote_version_data = json.loads(req.content)[0]
    except (HTTPError, Timeout, requests.exceptions.ConnectionError):
        logger.warning("Could not check for updates: GitHub API request failed (network error)")
    except AttributeError:
        logger.warning("Could not check for updates: failed to parse GitHub API response")
    else:
        return remote_version_data["tag_name"], remote_version_data["html_url"]


def check_updates():
    """Looks for newer versions."""
    remote_version, remote_version_url = _get_remote_version_data()
    try:
        _parse_version = lambda v: tuple(map(int, v.lstrip("v").split(".")))
        if _parse_version(remote_version) > _parse_version(__version__):
            logger.warning(
                f"A new version is available: {remote_version} (current: {__version__}), see {remote_version_url}"
            )
    except Exception:
        traceback.print_exc()
