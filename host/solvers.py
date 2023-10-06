"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import re
from time import struct_time
from urllib.parse import urlparse, urlunparse

import constants
import functions

IMGUR_SUFFIX = tuple(f"_d{ext}" for ext in constants.IMAGE_EXT)


def imgur(url: str, *_) -> str:
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


def nasa_apod(url: str, date: struct_time, pattern=re.compile(rb'<a href="(image/[^"]+)"').search) -> str:
    """
    Resolve the original image URL from Astronomy Picture of the Day (APOD - NASA).

        >>> nasa_apod("http://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg", None)
        'http://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg'
        >>> nasa_apod("https://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg", None)
        'https://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg'
        >>> nasa_apod("http://antwrp.gsfc.nasa.gov/apod/image/0702/mcnaught3_kemppainen.jpg", None)
        'http://antwrp.gsfc.nasa.gov/apod/image/0702/mcnaught3_kemppainen.jpg'
        >>> nasa_apod("http://apod.nasa.gov/apod/archivepix.html", None)
        'http://apod.nasa.gov/apod/archivepix.html'

    """
    parts = urlparse(url)

    if parts.path in {"/apod", "/apod/", "/apod/astropix.html"}:
        # Lets use the explicit date from the time the image was shared
        parts = parts._replace(
            scheme="https",
            path=f"/apod/ap{str(date.tm_year)[2:]}{date.tm_mon:02d}{date.tm_mday:02d}.html",
        )

    if "/apod/ap" not in parts.path:
        return url

    if parts.scheme != "https":
        parts = parts._replace(scheme="https")

    if parts.hostname != "apod.nasa.gov":
        parts = parts._replace(netloc="apod.nasa.gov")

    response = functions.fetch(urlunparse(parts))
    if (image := pattern(response.content)) is None:
        return ""

    parts = parts._replace(path=f"/apod/{image[1].decode()}")
    return urlunparse(parts)


def wikimedia(url: str, *_) -> str:
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
    return files.get("original", {}).get("url") or ""


SOLVERS = {
    "antwrp.gsfc.nasa.gov": nasa_apod,
    "apod.nasa.gov": nasa_apod,
    "i.imgur.com": imgur,
}


def guess_url(url: str, date: struct_time) -> str:
    """
    Resolve a specific URL.
    Return an empty string if the URL was not resolved to an image.

        >>> guess_url("http://", None)
        ''
        >>> guess_url("https://example.org/", None)
        ''
        >>> guess_url("https://example.org/favicon.png", None)
        'https://example.org/favicon.png'

    """
    if not (hostname := urlparse(url).hostname):
        return ""

    if solver := SOLVERS.get(hostname):
        url = solver(url, date)
    elif hostname.endswith((".wikimedia.org", ".wikipedia.org")):
        url = wikimedia(url)

    return url if functions.is_image_link(url) else ""
