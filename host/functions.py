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
from random import choice
from shutil import copyfile
from typing import Any
from urllib.parse import unquote, urlparse
from zlib import compress, decompress

import config
import constants
import custom_types
import cv2
import feedparser
import numpy
import requests
import urllib3
from unidecode import unidecode

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

    im = cv2.imread(str(file))

    height, width = im.shape[:2]
    if (height, width) <= (constants.THUMBNAIL_MAX_SIZE.height, constants.THUMBNAIL_MAX_SIZE.width):
        return copyfile(file, thumbnail)

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
    im = cv2.resize(im, (new_w, new_h), interpolation=cv2.INTER_AREA)

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
    im = cv2.imread(str(file))
    avg_color_per_row = numpy.average(im, axis=0)
    avg_color = numpy.average(avg_color_per_row, axis=0)
    return "".join(f"{int(n):02X}" for n in avg_color[::-1])


def feed_key(url: str, version: int = 2) -> str:
    """
    Craft the feed URL key for the local storage.

        >>> feed_key("https://www.example.org/links/feed/rss", version=1)
        'www.example.org'

        >>> feed_key("https://www.example.org", version=2)
        'www.example.org'
        >>> feed_key("https://www.example.org/", version=2)
        'www.example.org'
        >>> feed_key("https://shaarli.example.org/?do=rss", version=2)
        'shaarli.example.org'
        >>> feed_key("https://shaarli.example.org/feed/rss?do=rss", version=2)
        'shaarli.example.org'
        >>> feed_key("https://shaarli.example.org//feed/rss?do=rss", version=2)
        'shaarli.example.org'
        >>> feed_key("https://www.example.org/links?do=rss", version=2)
        'www.example.org/links'
        >>> feed_key("https://www.example.org/shaarli/?do=rss", version=2)
        'www.example.org/shaarli'
        >>> feed_key("https://www.example.org//shaarli/feed/rss?do=rss", version=2)
        'www.example.org/shaarli'
        >>> feed_key("https://www.example.org/shaarli/feed/rss", version=2)
        'www.example.org/shaarli'
        >>> feed_key("https://www.example.org/pro/liens/feed/rss?do=rss", version=2)
        'www.example.org/pro/liens'
        >>> feed_key("https://www.example.org/rss.php?do=rss&mode=links", version=2)
        'www.example.org'
        >>> feed_key("https://www.example.org/feed/atom?", version=2)
        'www.example.org'

    """
    parts = urlparse(url)
    match version:
        case 1:
            return parts.hostname
        case 2:
            path = parts.path.replace("//", "/")
            if len(path) > 1:
                path = path.removesuffix("/rss.php").removesuffix("/rss").removesuffix("/atom").removesuffix("/feed")
            return f"{parts.hostname}{path.removesuffix('/')}"


def fetch(url: str, method: str = "get") -> requests.Response:
    """Make a HTTP call."""
    with requests.request(
        method=method,
        url=url,
        headers=constants.HTTP_HEADERS,
        timeout=120.0,
        verify=False,
    ) as req:
        return req


def fetch_json(url: str) -> dict[str, Any]:
    """Fetch a JSON file."""
    print(">>> 📑", url)
    return fetch(url).json()


def fetch_image(url: str) -> bytes | None:
    """Fetch an image."""
    try:
        req = fetch(url)
        req.raise_for_status()
        image = req.content
        if is_image_data(image):
            print(">>> ✅", url)
            return image
        print(">>> 📛", url)
    except Exception:
        print(">>> ❌", url)
    return None


def fetch_image_type(url: str) -> str:
    """Fetch an image type using HTTP headers from the HEAD response."""
    req = fetch(url, method="head")
    content_type = req.headers.get("content-type", "")
    return constants.IMAGES_CONTENT_TYPE.get(content_type, "")


def fetch_rss_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch a XML RSS feed."""
    print(">>> 📜", url)
    return feedparser.parse(fetch(url).text)


def fix_images_medatadata(force: bool = False):
    at_least_one_change = False
    errors = set()
    images = {image.name for image in constants.IMAGES.glob("*.*")}

    for feed in constants.FEEDS.glob("*.json"):
        changed = False

        for k, v in (data := read(feed)).items():
            # Fix the filename
            file: Path = constants.IMAGES / v["link"]
            key = file.stem[:6]  # The small hash
            name_original = file.stem[7:]
            name_sanitized = safe_filename(name_original)
            name_has_changed = False

            if name_original != name_sanitized:
                name_has_changed = True
                new_file = file.with_stem(f"{key}_{name_sanitized}")
            elif file.suffix not in list(constants.IMAGES_CONTENT_TYPE.values()):
                name_has_changed = True
                if file.suffix.startswith((".jpg", ".jpeg")):
                    suffix = ".jpg"
                elif file.suffix.startswith(".png"):
                    suffix = ".png"
                else:
                    raise ValueError(f"Unknown {suffix=}")
                new_file = file.with_suffix(suffix)

            if name_has_changed:
                print(f"{file.name!r} -> {new_file.name!r}")
                file = new_file if new_file.is_file() else file.rename(new_file)
                data[k] |= {"link": file.name}
                changed = True
                at_least_one_change = True

                # Recreate the thumbnail
                (constants.THUMBNAILS / v["link"]).unlink(missing_ok=True)
                create_thumbnail(file)

            images.discard(v["link"])

            # Fix the size
            if force or "width" not in v:
                if not (size := get_size(file)):
                    errors.add(file.name)
                    continue

                data[k] |= {"width": size.width, "height": size.height}
                changed = True
                at_least_one_change = True

            # Fix the dominant color average
            if force or "docolav" not in v:
                if not (color := docolav(file)):
                    errors.add(file.name)
                    continue

                data[k] |= {"docolav": color}
                changed = True
                at_least_one_change = True

            # Fix tags
            sanitized_tags = sorted(safe_tag(tag) for tag in v["tags"])
            if v["tags"] != sanitized_tags:
                data[k] |= {"tags": sanitized_tags}
                changed = True
                at_least_one_change = True

        if changed:
            persist(feed, data)

    # Remove orphaned files
    errors |= images

    if errors:
        purge(errors)

    if at_least_one_change:
        invalidate_caches()


def get_from_cache(cache_key: str) -> str | None:
    """Retreive a compressed response from a potential cache file."""
    file = constants.CACHE / f"{cache_key}.cache"
    with suppress(FileNotFoundError):
        return decompress(file.read_bytes()).decode()
    return None


def get_last(page: int, count: int) -> tuple[int, custom_types.Metadatas]:
    """Get last N images."""
    all_images = retrieve_all_uniq_metadata()
    return len(all_images), all_images[(page - 1) * count : page * count]


def get_metadata(image: str) -> tuple[str, custom_types.Metadata, str] | None:
    all_cache = retrieve_all_uniq_metadata()
    for idx, metadata in enumerate(all_cache):
        if metadata.link == image:
            prev_img = all_cache[idx - 1].link if idx > 0 else ""
            next_img = all_cache[idx + 1].link if idx < len(all_cache) - 1 else ""
            return prev_img, metadata, next_img

    return None


def get_random_image() -> custom_types.Metadata:
    """Get a random image."""
    return choice(retrieve_all_uniq_metadata())


def get_size(file: Path) -> custom_types.Size:
    """Retrieve the file width & height."""
    im = cv2.imread(str(file))
    return custom_types.Size(width=im.shape[1], height=im.shape[0])


def get_tags() -> list[str]:
    """Get all available tags."""
    return sorted({tag for metadata in retrieve_all_uniq_metadata() for tag in metadata.tags})


def invalidate_caches() -> None:
    """Remove all cache files."""
    for file in constants.CACHE.glob("*.cache"):
        file.unlink()


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
    return raw.startswith(tuple(constants.IMAGES_MAGIC_SIG.values()))


def is_image_link(url: str) -> bool:
    """
    Check whenever the given `url` points to a supported image format.
    It will also prevent downloading again images from Shaarlimages.

        >>> is_image_link("")
        False
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

        >>> is_image_link(f"https://{config.SITE.host}/image/ok.jpg")
        False
        >>> is_image_link(f"{config.SITE.url}/image/ok.png")
        False

    """
    if not url:
        return False
    hostname = urlparse(url).hostname
    return url.lower().endswith(constants.IMAGE_EXT) and hostname != config.SITE.host


def load_metadata(feed: Path) -> list[tuple[float, custom_types.Metadata]]:
    """Load a given `feed` into more a readable object."""
    cls = custom_types.Metadata
    return [(float(date), cls(**metadata)) for date, metadata in read(feed).items()]


def lookup(value: str) -> custom_types.Metadatas:
    """
    Search for images.

        >>> lookup('ab')
        []

    """
    if len(value) < 3:
        return []

    value = value.lower()
    return [
        metadata
        for metadata in retrieve_all_uniq_metadata()
        if (
            value in metadata.title.lower()
            or value in metadata.desc.lower()
            or value in metadata.guid.lower()
            or value in metadata.link.lower()
            or value in metadata.tags
        )
    ]


def lookup_tag(tag: str) -> custom_types.Metadatas:
    """Search for images by tag."""
    tag = tag.lower()
    return [metadata for metadata in retrieve_all_uniq_metadata() if tag in metadata.tags]


def now() -> float:
    return today().timestamp()


def persist(file: Path, data: dict[str, Any]) -> None:
    file.parent.mkdir(exist_ok=True, parents=True)
    with file.open(mode="w") as fh:
        json.dump(data, fh, sort_keys=True, indent=0)
        fh.flush()
        os.fsync(fh.fileno())


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
    at_least_one_change = False

    for file in files:
        print(" !! Removing non-image file", file)

    for feed in constants.FEEDS.glob("*.json"):
        changed = False
        cache = read(feed)

        for date, metadata in cache.copy().items():
            if metadata["link"] in files:
                cache.pop(date)
                changed = True
                at_least_one_change = True

        if changed:
            persist(feed, cache)

    for file in files:
        (constants.IMAGES / file).unlink(missing_ok=True)

    if at_least_one_change:
        invalidate_caches()


def read(file: Path) -> dict[str, Any]:
    return json.loads(file.read_text()) if file.is_file() else {}


def retrieve_all_uniq_metadata() -> custom_types.Metadatas:
    """Retrieve all images with no duplicates, sorted by latest first."""
    cache_key = small_hash("all-in-one")
    if cached := get_from_cache(cache_key):
        cls = custom_types.Metadata
        return [cls(**metadata) for metadata in json.loads(cached)]

    # First, all images
    all_images = []
    for feed in constants.FEEDS.glob("*.json"):
        all_images.extend(load_metadata(feed))

    # Then, keep only the first published version of an image, skipping eventual duplicates (via reshares mostly)
    know_images = set()
    uniq_images = []
    for _, metadata in sorted(all_images, key=lambda i: i[0]):
        if metadata.link in know_images:
            continue
        uniq_images.append(metadata)
        know_images.add(metadata.link)

    res = uniq_images[::-1]
    store_in_cache(cache_key, json.dumps(res, default=lambda s: vars(s)), info=False)
    return res


def safe_filename(value: str, replace=re.compile(r"[^a-z0-9]").sub, cleanup=re.compile(r"--+").sub) -> str:
    r"""
    Sanitize, and control the length, of a given `value`.

        >>> safe_filename("   a/b\\c*d:e<f>g?h\"i|j%k'l#k@     ")
        'a-b-c-d-e-f-g-h-i-j-k-l-k-'
        >>> safe_filename("fetch.php?cache=&media=divers:img_20141120_150542")
        'fetch-php-cache-media-divers-img-20141120-150542'
        >>> safe_filename("普通话/普通話")
        'pu-tong-hua-pu-tong-hua'
        >>> safe_filename("jeux_vidéo")
        'jeux-video'
        >>> safe_filename("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Daikokuji-Sasayama_Komus%C5%8D_Shakuhachi_%E5%A4%A7%E5%9B%BD%E5%AF%BA%EF%BC%88%E7%AF%A0%E5%B1%B1%E5%B8%82%EF%BC%89%E4%B8%B9%E6%B3%A2%E8%8C%B6%E7%A5%AD%E3%82%8A_%E8%99%9A%E7%84%A1%E5%83%A7_DSCF1443.jpg/1200px-Daikokuji-Sasayama_Komus%C5%8D_Shakuhachi_%E5%A4%A7%E5%9B%BD%E5%AF%BA%EF%BC%88%E7%AF%A0%E5%B1%B1%E5%B8%82%EF%BC%89%E4%B8%B9%E6%B3%A2%E8%8C%B6%E7%A5%AD%E3%82%8A_%E8%99%9A%E7%84%A1%E5%83%A7_DSCF1443")
        'https-upload-wikimedia-org-wikipedia-commons-thumb-9-9d-daikoku-chi-da-guo-si-xiao-shan-shi-dan-bo-cha-ji-ri-xu-wu-seng-dscf1443'

    """  # noqa[E501]
    return shortify(cleanup("-", replace("-", unidecode(unquote(value)).strip().lower())))


def safe_tag(tag: str, cleanup=re.compile(r"--+").sub) -> str:
    """
    Sanitize a tag.

        >>> safe_tag("B/W_&_colors?!§")
        'b-w-colors'

    """
    return cleanup(
        "-",
        tag.lower()
        .replace("/", "-")
        .replace("_", "-")
        .replace("&", "-")
        .replace("?", "")
        .replace("!", "")
        .replace("§", ""),
    ).strip()


def shortify(text: str, /, *, limit: int = 128) -> str:
    """Shorten a given `text` to fit in exactly or less `limit` characters."""
    return f"{text[:limit // 2 - 1]}-{text[-limit // 2:]}" if len(text) > limit else text


def small_hash(value: str) -> str:
    """
    Returns the small hash of a string, using RFC 4648 base64url format
    http://sebsauvage.net/wiki/doku.php?id=php:shaarli

    Small hashes:
    - are unique (well, as unique as crc32, at last)
    - are always 6 characters long
    - only use the following characters: a-z A-Z 0-9 - _ @
    - are NOT cryptographically secure (they CAN be forged)

        >>> small_hash("20111006_131924")
        'yZH23w'

    """
    return b64encode(bytes.fromhex(php_crc32(value)), altchars=b"-_").rstrip(b"=").decode()


def store_in_cache(cache_key: str, response: str, info: bool = True) -> None:
    """Store a HTTP response into a compressed cache file."""
    if info:
        response += f"\n<!-- Cached: {today()} -->\n"

    file = constants.CACHE / f"{cache_key}.cache"
    file.parent.mkdir(exist_ok=True)
    file.write_bytes(compress(response.encode(), level=9))


def today() -> datetime:
    return datetime.now(tz=timezone.utc)
