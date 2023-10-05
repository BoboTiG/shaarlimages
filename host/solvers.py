"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from urllib.parse import urlparse

import constants
import functions

IMGUR_SUFFIX = tuple(f"_d{ext}" for ext in constants.IMAGE_EXT)


def imgur(url: str) -> str:
    """
    Resolve the original image URL from Imgut.

        >>> imgur("https://i.imgur.com/qypAs0A_d.jpg")
        'https://i.imgur.com/qypAs0A.jpg'
        >>> imgur("https://i.imgur.com/qypAs0A_d.jpeg")
        'https://i.imgur.com/qypAs0A.jpeg'
        >>> imgur("https://i.imgur.com/qypAs0A_d.png")
        'https://i.imgur.com/qypAs0A.png'
        >>> imgur("https://i.imgur.com/qypAs0A_dd.png")
        'https://i.imgur.com/qypAs0A_dd.png'

    """
    if url.endswith(IMGUR_SUFFIX):
        for ext in constants.IMAGE_EXT:
            url = url.replace(f"_d{ext}", ext)
    return url


def wikimedia(url: str) -> str:
    """
    Resolve the original image URL from Wikimedia.

        >>> wikimedia("http://upload.wikimedia.org/wikipedia/en/a/a8/New_British_Coinage_2008.jpg")
        'http://upload.wikimedia.org/wikipedia/en/a/a8/New_British_Coinage_2008.jpg'

    """
    parts = urlparse(url)
    path = parts.path if ":" in parts.path else parts.fragment if ":" in parts.fragment else ""
    if ":" not in path:
        return url

    file = path.split(":", 1)[1]
    files = functions.fetch_json(f"https://api.wikimedia.org/core/v1/commons/file/File:{file}")
    return files.get("original", {}).get("url", url)


SOLVERS = {
    "i.imgur.com": imgur,
}


def guess_url(url: str) -> str:
    """Resolve a specific URL."""
    hostname = urlparse(url).hostname

    if solver := SOLVERS.get(hostname):
        return solver(url)

    if hostname.endswith((".wikimedia.org", ".wikipedia.org")):
        return wikimedia(url)

    return url
