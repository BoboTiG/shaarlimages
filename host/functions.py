"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import json
import os
import re
from base64 import b64encode
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfile
from typing import Any
from urllib.parse import urlparse

import config
import constants
import custom_types
import cv2
import feedparser
import numpy
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def any_css_class_question() -> str:
    """Should we add a custom CSS class to the zoom'ed image?"""
    right_now = today()

    if (right_now.day, right_now.month) == (28, 6):
        # Easter egg: gay pride on june 28
        return "gay-pride"

    return ""


def create_thumbnail(file: Path) -> Path | None:
    """
    Generate the image thumbnail.

    Inspiration: https://stackoverflow.com/a/44724368/1117028
    """
    thumbnail = constants.THUMBNAILS / file.name

    if thumbnail.is_file():
        return thumbnail

    if (im := cv2.imread(str(file))) is None:
        return None

    height, width = im.shape[:2]
    if (height, width) <= (constants.THUMBNAIL_MAX_SIZE.height, constants.THUMBNAIL_MAX_SIZE.width):
        return copyfile(file, thumbnail)

    if height > constants.THUMBNAIL_MAX_SIZE.height or width > constants.THUMBNAIL_MAX_SIZE.width:
        # Shrinking image
        interpolation = cv2.INTER_AREA
    else:
        # Stretching image
        interpolation = cv2.INTER_CUBIC

    # Aspect ratio of image
    aspect = width / height

    # Compute scaling
    if aspect > 1:
        # Horizontal image
        new_w = constants.THUMBNAIL_MAX_SIZE.width
        new_h = int(round(new_w / aspect))
    elif aspect < 1:
        # Vertical image
        new_h = constants.THUMBNAIL_MAX_SIZE.height
        new_w = int(round(new_h * aspect))
    else:
        # Square image
        new_h, new_w = constants.THUMBNAIL_MAX_SIZE.height, constants.THUMBNAIL_MAX_SIZE.width

    # Scale down
    im = cv2.resize(im, (new_w, new_h), interpolation=interpolation)

    cv2.imwrite(
        str(thumbnail),
        im,
        [
            int(cv2.IMWRITE_JPEG_QUALITY),
            80,
            int(cv2.IMWRITE_JPEG_OPTIMIZE),
            int(True),
            int(cv2.IMWRITE_JPEG_PROGRESSIVE),
            int(True),
            int(cv2.IMWRITE_PNG_COMPRESSION),
            9,
        ],
    )

    return thumbnail


def docolav(file: Path) -> str:
    """
    Determine the DOminant COlor AVerage of the given image.
    Return the RGB hex code.

    https://stackoverflow.com/a/43112217/1117028
    """
    if (im := cv2.imread(str(file))) is None:
        return ""

    avg_color_per_row = numpy.average(im, axis=0)
    avg_color = numpy.average(avg_color_per_row, axis=0)

    return "".join(f"{int(n):02X}" for n in avg_color[::-1])


def fix_images_medatadata(force: bool = False):
    errors = set()
    for feed in constants.CACHE_FEEDS.glob("*.json"):
        changed = False

        if not (data := read(feed)):
            continue

        for k, v in data.items():
            file = constants.IMAGES / v["link"]

            if force or "width" not in v:
                if not (size := get_size(file)):
                    errors.add(v["link"])
                    continue

                data[k] |= {"width": size.width, "height": size.height}
                changed = True

            if force or "docolav" not in v:
                if not (color := docolav(file)):
                    errors.add(v["link"])
                    continue

                data[k] |= {"docolav": color}
                changed = True

        if changed:
            persist(feed, data)

    if errors:
        purge(errors)


def generate_images_file(force: bool = False) -> list[tuple[str, list[str], str]]:
    """Craft the JSON file containing all images."""
    if force or not (uniq_images := read(constants.CACHE_HOME_ALL)):
        all_images = sorted(
            (
                (float(key), feed.stem, value["link"], value["tags"], value["width"], value["height"], value["docolav"])
                for feed in constants.CACHE_FEEDS.glob("*.json")
                for key, value in read(feed).items()
            ),
            reverse=True,
        )

        know_images = set()
        uniq_images = []
        for _, feed, image, tags, width, height, color in all_images[::-1]:
            if image in know_images:
                continue
            uniq_images.append((image, tags, width, height, color, feed))
            know_images.add(image)

        uniq_images = uniq_images[::-1]
        persist(constants.CACHE_HOME_ALL, uniq_images)

    return uniq_images


def get_last(page: int, count: int) -> tuple[int, custom_types.Images]:
    """Get last N images."""
    all_images = generate_images_file()
    return len(all_images), all_images[(page - 1) * count : page * count]


def get_metadata(image: str) -> custom_types.Metadata:
    all_cache = read(constants.CACHE_HOME_ALL)

    if not (feed := next((stored_feed for stored_image, *_, stored_feed in all_cache if stored_image == image), "")):
        assert 0, "TODO #1"

    if not (cache := read(constants.CACHE_FEEDS / f"{feed}.json")):
        assert 0, "TODO #2"

    for metadata in cache.values():
        if metadata["link"] == image:
            return metadata

    assert 0, "TODO #3"


def get_prev_next(image: str) -> tuple[str, str]:
    all_cache = read(constants.CACHE_HOME_ALL)

    for idx, (stored_image, *_) in enumerate(all_cache):
        if stored_image != image:
            continue

        prev_key = all_cache[idx - 1][0] if idx > 0 else ""
        next_key = all_cache[idx + 1][0] if idx < len(all_cache) - 1 else ""
        return prev_key, next_key

    return "", ""


def get_size(file: Path) -> custom_types.Size | None:
    """Retrieve the file width & height."""
    if (im := cv2.imread(str(file))) is None:
        return None

    return custom_types.Size(width=im.shape[1], height=im.shape[0])


def fetch(url: str) -> requests.Response:
    """Make a HTTP call."""
    with requests.get(url, headers=constants.HTTP_REQ_HEADERS, timeout=120.0, verify=False) as req:
        return req


def fetch_json(url: str) -> dict[str, Any]:
    """Fetch a JSON file."""
    print(">>> 📑", url)
    return fetch(url).json()


def fetch_image(url: str) -> bytes | None:
    """Fetch an image."""
    # Prevent a circular import error
    import solvers

    url = solvers.guess_url(url)
    try:
        req = fetch(url)
        req.raise_for_status()
        image = req.content
        if is_image_data(image):
            print(">>> ✅", url)
            return image
        print(">>> 📛", url)
    except requests.exceptions.RequestException:
        print(">>> ❌", url)
    except Exception:
        print(">>> 🛑", url)
    return None


def fetch_rss_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch a XML RSS feed."""
    print(">>> 📜", url)
    return feedparser.parse(fetch(url).text)


def invalidate_cache() -> None:
    constants.CACHE_HOME_ALL.unlink(missing_ok=True)


def is_image_data(raw: bytes) -> bool:
    r"""
    Check whenever the provided `raw` data seems like a supported image format.

        >>> is_image_data(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")
        True
        >>> is_image_data(b"\xff\xd8\xff\xe14\xbbExif\x00")
        True
        >>> is_image_data(b"\x89PNG\r\n\x1a")
        True
        >>> is_image_data(b"\00")
        False

    """
    return raw.startswith(constants.IMAGES_MAGIC_SIG)


def is_image_link(url: str) -> bool:
    """
    Check whenever the given `url` points to a supported image format.
    It will also prevent downloading again images from Shaarlimages.

        >>> is_image_link("ok.JPG")
        True
        >>> is_image_link("ok.jpg")
        True
        >>> is_image_link("ok.jpeg")
        True
        >>> is_image_link("ok.png")
        True
        >>> is_image_link("bad.html")
        False

        >>> is_image_link(f"https://{config.SITE['host']}/image/ok.jpg")
        False
        >>> is_image_link(f"{config.SITE['url']}/image/ok.png")
        False

    """
    hostname = urlparse(url).hostname
    return url.lower().endswith(constants.IMAGE_EXT) and hostname != config.SITE["host"]


def now() -> float:
    return today().timestamp()


def persist(file: Path, data: dict[str, Any]) -> None:
    with file.open(mode="w") as fh:
        json.dump(data, fh, sort_keys=True, indent=4)
        os.fsync(fh)


def php_crc32(value: str) -> str:
    """
    References:
    - https://www.php.net/manual/en/function.hash-file.php#104836
    - https://stackoverflow.com/a/50843127/636849

        >>> php_crc32("20111006_131924")
        'c991f6df'
        >>> php_crc32("liens.mohja.fr")
        '0c05b1a5'

    """
    crc = 0xFFFFFFFF
    for x in value.encode():
        crc ^= x << 24
        for _ in range(8):
            crc = (crc << 1) ^ 0x04C11DB7 if crc & 0x80000000 else crc << 1
    crc = ~crc
    crc &= 0xFFFFFFFF

    # Convert from big endian to little endian:
    crc = int.from_bytes(crc.to_bytes(4, "big"), byteorder="little")

    return hex(crc)[2:].rjust(8, "0")


def purge(files: set[str]) -> None:
    """Remove an image from databases."""
    for file in files:
        print(" !! Removing non-image file", file)

    for feed in constants.CACHE_FEEDS.glob("*.json"):
        changed = False
        cache = read(feed)

        for key, value in cache.copy().items():
            if value["link"] in files:
                cache.pop(key)
                changed = True

        if changed:
            persist(feed, cache)

    if all_cache := read(constants.CACHE_HOME_ALL):
        indexes = []
        for idx, (name, *_) in enumerate(all_cache):
            if name in files:
                indexes.append(idx)

        if indexes:
            for idx in [idx - count for count, idx in enumerate(indexes)]:
                del all_cache[idx]

            persist(constants.CACHE_HOME_ALL, all_cache)

    for file in files:
        (constants.IMAGES / file).unlink(missing_ok=True)


def read(file: Path) -> dict[str, Any]:
    with suppress(FileNotFoundError):
        return json.loads(file.read_text())
    return {}


def safe_filename(name: str, func=re.compile(constants.SAFE_FILENAME_REGEXP).sub) -> str:
    r"""
    Replace forbidden characters for a given `name`.

        >>> safe_filename("a/b\\c*d:e<f>g?h\"i|j%k'l#@     ")
        'a-b-c-d-e-f-g-h-i-j-k-l-@'
    """
    return func("-", name.strip())


def small_hash(value: str) -> str:
    """
    Returns the small hash of a string, using RFC 4648 base64url format
    http://sebsauvage.net/wiki/doku.php?id=php:shaarli

    Small hashes:
    - are unique (well, as unique as crc32, at last)
    - are always 6 characters long.
    - only use the following characters: a-z A-Z 0-9 - _ @
    - are NOT cryptographically secure (they CAN be forged)

        >>> small_hash("20111006_131924")
        'yZH23w'

    """
    return b64encode(bytes.fromhex(php_crc32(value)), altchars=b"-_").rstrip(b"=").decode()


def today() -> datetime:
    return datetime.now(tz=timezone.utc)
