"""This is part of Shaarlimages.

Source: https://github.com/BoboTiG/shaarlimages.
"""

import re
from collections.abc import Callable
from time import struct_time
from urllib.parse import parse_qs, urlparse, urlunparse

import constants
import functions

IMGUR_SUFFIX = tuple(f"_d{ext}" for ext in constants.IMAGE_EXT)


def cheeseburger(url: str, date: struct_time, *, feed_key: str = "") -> str:  # noqa: ARG001
    """Resolve the original image URL from Cheeseburger.

    >>> cheeseburger("https://i.chzbgr.com/maxW500/7579559168/hFBFD2016/", None, feed_key="012345")
    'https://i.chzbgr.com/maxW500/7579559168/hFBFD2016/'

    """
    return url


def developpez(url: str, date: struct_time, *, feed_key: str = "") -> str:  # noqa: ARG001
    """Resolve the original image URL from Developpez.net.

    >>> developpez("https://www.developpez.net/forums/attachments/p627433d1/a/a/a", None)
    'https://www.developpez.net/forums/attachments/p627433d1/a/a/a'
    >>> developpez("https://www.developpez.com/images/logos/forum.png", None)
    'https://www.developpez.com/images/logos/forum.png'
    >>> developpez("https://www.developpez.net/forums/d1526370/", None, feed_key="012345")
    ''

    """
    return url if functions.is_image_link(url) or "/forums/attachments/" in url else ""


def imgur(url: str, date: struct_time, *, feed_key: str = "") -> str:  # noqa: ARG001
    """Resolve the original image URL from Imgut.

    >>> imgur("https://i.imgur.com/qypAs0A_d.gif", None, feed_key="012345")
    ''
    >>> imgur("https://i.imgur.com/qypAs0A_d.gifv", None)
    ''
    >>> imgur("https://i.imgur.com/qypAs0A_d.mp4", None)
    ''

    """
    # Remove all URL parameters
    parts = urlparse(url)
    parts = parts._replace(fragment="", query="")
    url = urlunparse(parts)

    if url.endswith(IMGUR_SUFFIX):
        for ext in constants.IMAGE_EXT:
            url = url.replace(f"_d{ext}", ext)

    if not functions.is_image_link(url):
        return ""

    # Ensure the image still exists
    response = functions.fetch(url, method="head", verify=True, feed_key=feed_key)
    return "" if response.url.endswith("/removed.png") else url


def nasa_apod(
    url: str,
    date: struct_time,
    *,
    pattern: re.Pattern = re.compile(rb'<a href="(image/[^"]+)"'),
    feed_key: str = "",
) -> str:
    """Resolve the original image URL from Astronomy Picture of the Day (APOD - NASA).

    >>> nasa_apod("http://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg", None)
    'http://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg'
    >>> nasa_apod("https://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg", None)
    'https://apod.nasa.gov/apod/image/1204/EndeavourFlightDeck_cooper_1050.jpg'
    >>> nasa_apod("http://antwrp.gsfc.nasa.gov/apod/image/0702/mcnaught3_kemppainen.jpg", None)
    'http://antwrp.gsfc.nasa.gov/apod/image/0702/mcnaught3_kemppainen.jpg'
    >>> nasa_apod("http://apod.nasa.gov/apod/archivepix.html", None, feed_key="012345")
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

    response = functions.fetch(urlunparse(parts), verify=True, feed_key=feed_key)
    if (image := pattern.search(response.content)) is None:
        return ""

    parts = parts._replace(path=f"/apod/{image[1].decode()}")
    return urlunparse(parts)


def nasa_jpl(url: str, date: struct_time, *, feed_key: str = "") -> str:  # noqa: ARG001
    """Resolve the original image URL from NASA's Jet Propulsion Laboratory (JPL).

    >>> nasa_jpl("https://photojournal.jpl.nasa.gov/jpeg/PIA25440.jpg", None)
    'https://photojournal.jpl.nasa.gov/jpeg/PIA25440.jpg'
    >>> nasa_jpl("https://photojournal.jpl.nasa.gov/jpeg/PIA25440.JPG", None)
    'https://photojournal.jpl.nasa.gov/jpeg/PIA25440.JPG'
    >>> nasa_jpl("https://photojournal.jpl.nasa.gov/catalog/PIA25440", None, feed_key="012345")
    'https://photojournal.jpl.nasa.gov/jpeg/PIA25440.jpg'

    """
    if functions.is_image_link(url):
        return url

    catalog = urlparse(url).path.split("/")[-1]
    return f"https://photojournal.jpl.nasa.gov/jpeg/{catalog}.jpg"


def quora(
    url: str,
    date: struct_time,  # noqa: ARG001
    *,
    pattern: re.Pattern = re.compile(rb"<meta property='og:image' content='([^']+)'"),
    feed_key: str = "",
) -> str:
    """Resolve the original image URL from Quora.

    >>> quora("https://qph.cf2.quoracdn.net/main-qimg-146ab3a9693b5c97c7fb1e48c3898c46", None, feed_key="012345")
    'https://qph.cf2.quoracdn.net/main-qimg-146ab3a9693b5c97c7fb1e48c3898c46'

    """
    parts = urlparse(url)
    if parts.path.startswith("/main-qimg-"):
        return url

    response = functions.fetch(url, verify=True, feed_key=feed_key)
    return "" if (image := pattern.search(response.content)) is None else image[1].decode()


def twitter_img(url: str, date: struct_time, *, feed_key: str = "") -> str:  # noqa: ARG001
    """Resolve the original image URL from Twitter.

    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.JPG", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.JPG'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg:small", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg:medium", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg:large", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg:something", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY?format=jpg", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'
    >>> twitter_img("https://pbs.twimg.com/media/CrlG7oSWYAA9APY?format=jpg&name=4096x4096", None)
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg'

    """
    parts = urlparse(url)
    if ":" in parts.path:
        parts = parts._replace(path=parts.path.split(":", 1)[0])

    if not functions.is_image_link(parts.path) and "format" in parts.query:
        query = parse_qs(parts.query)
        ext = query["format"][0].lower()
        parts = parts._replace(path=f"{parts.path}.{ext}", query="")

    url = urlunparse(parts)
    return url if functions.is_image_link(url) else ""


def webb_telescope(
    url: str,
    date: struct_time,  # noqa: ARG001
    *,
    pattern: re.Pattern = re.compile(rb'<meta property="og:image" content="([^"]+)"'),
    feed_key: str = "",
) -> str:
    """Resolve the original image URL from Webb Space Telescope."""
    response = functions.fetch(url, verify=True, feed_key=feed_key)
    if not (url := "" if (image := pattern.search(response.content)) is None else image[1].decode()):
        return ""

    if not url.startswith("http"):
        url = f"https:{url}"
    return url


def wikimedia(url: str, date: struct_time, *, feed_key: str = "") -> str:  # noqa: ARG001
    """Resolve the original image URL from Wikimedia.

    >>> wikimedia("http://upload.wikimedia.org/wikipedia/en/a/a8/New_British_Coinage_2008.jpg", None)
    'http://upload.wikimedia.org/wikipedia/en/a/a8/New_British_Coinage_2008.jpg'
    >>> wikimedia("https://en.wikipedia.org/wiki/File:Douglas-Peucker_animated.gif", None, feed_key="012345")
    ''

    """
    parts = urlparse(url)
    path = parts.path if ":" in parts.path else parts.fragment if ":" in parts.fragment else ""
    if ":" not in path:
        return url

    file = path.split(":", 1)[1]
    if not functions.is_image_link(file):
        return ""

    files = functions.fetch_json(
        f"https://api.wikimedia.org/core/v1/commons/file/File:{file}",
        verify=True,
        feed_key=feed_key,
    )
    return files.get("original", {}).get("url") or ""


def zbrush_central(
    url: str,
    date: struct_time,  # noqa: ARG001
    *,
    pattern: re.Pattern = re.compile(rb'<meta property="og:image" content="([^"]+)"'),
    feed_key: str = "",
) -> str:
    """Resolve the original image URL from ZBrushCentral."""
    response = functions.fetch(url, verify=True, feed_key=feed_key)
    return "" if (image := pattern.search(response.content)) is None else image[1].decode()


SOLVERS: dict[str, Callable] = {
    "antwrp.gsfc.nasa.gov": nasa_apod,
    "apod.nasa.gov": nasa_apod,
    "i.chzbgr.com": cheeseburger,
    "i.imgur.com": imgur,
    "pbs.twimg.com": twitter_img,
    "photojournal.jpl.nasa.gov": nasa_jpl,
    "webbtelescope.org": webb_telescope,
    "www.developpez.net": developpez,
    "www.zbrushcentral.com": zbrush_central,
}


def guess_url(url: str, date: struct_time, *, feed_key: str = "") -> str:
    """Resolve a specific URL.

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
        return solver(url, date, feed_key=feed_key)

    if hostname.endswith((".wikimedia.org", ".wikipedia.org")):
        return wikimedia(url, date, feed_key=feed_key)

    if hostname.endswith((".quora.com", ".quoracdn.net")):
        return quora(url, date, feed_key=feed_key)

    return url if functions.is_image_link(url) else ""


def alter_url(url: str) -> str:
    """Sometimes it might be better to alter the image URL.

    >>> alter_url("https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg")
    'https://pbs.twimg.com/media/CrlG7oSWYAA9APY.jpg:orig'

    """
    match urlparse(url).hostname:
        case "pbs.twimg.com":
            # We want the maximum quality
            return f"{url}:orig"
    return url
