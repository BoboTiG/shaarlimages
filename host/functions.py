"""This is part of Shaarlimages.

Source: https://github.com/BoboTiG/shaarlimages.
"""

import hashlib
import json
import os
import re
from base64 import b64encode
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from random import choice
from shutil import copyfile
from time import mktime, struct_time
from typing import Any
from urllib.parse import urlparse, urlunparse
from zlib import compress, decompress

import config
import constants
import custom_types
import cv2
import feedparser
import numpy as np
import requests
import solvers
import urllib3
from feedgenerator import Atom1Feed
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADAPTER = HTTPAdapter(max_retries=Retry(total=0, backoff_factor=0))
SESSION = requests.Session()
SESSION.mount("http://", ADAPTER)
SESSION.mount("https://", ADAPTER)


class EvanescoError(Exception):
    """Exception raised when an image no more exist on the internet."""

    def __str__(self) -> str:  # noqa: D105
        return "Cannot found the resource on internet anymore."


def any_css_class_question() -> str:
    """Return an eventual custom CSS class to add to the zoom'ed image."""
    right_now = today()

    if (right_now.day, right_now.month) == (28, 6):
        # Easter egg: gay pride on june 28
        return "gay-pride"

    return ""


def checksum(file: Path, algo: str = "md5") -> str:
    """Compute the check sum of the given `file`."""
    return hashlib.new(algo, file.read_bytes()).hexdigest().lower()


def craft_feed(images: custom_types.Metadatas, rss_link: str) -> str:
    """RSS feed creator."""
    title = config.SITE.title
    if "/search/" in rss_link:
        title += f" 🔎 {rss_link.split('/')[-1]}"
    elif "/tag/" in rss_link:
        title += f" 🏷️ {rss_link.split('/')[-1]}"

    feed = Atom1Feed(
        title,
        f"{config.SITE.url}{rss_link}",
        config.SITE.description,
        author_name=config.SITE.title,
        categories=["Shaarli", "gallery", "image"],
        image=f"{config.SITE.url}/favicon.png",
    )

    for image in images:
        feed.add_item(
            image.title,
            f"{config.SITE.url}/zoom/{image.file}",
            f'<img src="{config.SITE.url}/image/{image.file}"/><br /><br />{image.description}',
            categories=image.tags,
            pubdate=datetime.fromtimestamp(image.date, tz=timezone.utc),
            unique_id=f"{config.SITE.url}/zoom/{image.file}",
        )

    return feed.writeString("utf-8")


def create_thumbnail(file: Path) -> Path | None:
    """Generate the image thumbnail.

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


def debug(*msg: str) -> None:
    """Print a message, but only when run outside the CI."""
    if not constants.IS_CI:
        print(*msg, flush=True)


def docolav(file: Path) -> str:
    """Determine the DOminant COlor AVerage of the given image.

    Return the RGB hex code.

    Source: https://stackoverflow.com/a/43112217/1117028
    """
    im = cv2.imread(str(file))
    avg_color_per_row = np.average(im, axis=0)  # type: ignore[arg-type]
    avg_color = np.average(avg_color_per_row, axis=0)
    return "".join(f"{int(n):02X}" for n in avg_color[::-1])


def feed_key(url: str) -> str:
    """Craft the feed URL key for the local storage.

    Note: The URL is already sanitized here: https://github.com/BoboTiG/shaarlis/blob/main/sync.py#L31.

    >>> feed_key("http://www.example.org/?do=rss")
    'www.example.org'
    >>> feed_key("https://www.example.org/?do=rss")
    'www.example.org'
    >>> feed_key("https://shaarli.example.org/?do=rss")
    'shaarli.example.org'
    >>> feed_key("https://www.example.org/shaarli?do=rss")
    'www.example.org/shaarli'
    >>> feed_key("https://www.example.org/rss.php?mode=linksédo=rss")
    'www.example.org'
    >>> feed_key("https://www.example.org/links/rss.php?mode=linksédo=rss")
    'www.example.org/links'
    >>> feed_key("https://example.org/carnet.atom")
    'example.org/carnet.atom'

    """
    parts = urlparse(url)
    # BlogoText / oText support
    path = parts.path.removesuffix("/rss.php")
    return f"{parts.hostname}{path.removesuffix('/')}"


def fetch(
    url: str,
    *,
    method: str = "get",
    verify: bool = False,
    from_the_past: bool = True,
    feed_key: str = "",
) -> requests.Response:
    """Make a HTTP call."""
    with SESSION.request(method=method, url=url, headers=constants.HTTP_HEADERS, timeout=120.0, verify=verify) as req:
        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError:
            if not from_the_past:
                raise
        else:
            return req

    return try_wayback_machine(url, method, feed_key=feed_key)


def fetch_json(url: str, *, verify: bool = False, feed_key: str = "") -> dict[str, Any]:
    """Fetch a JSON file."""
    debug(">>> 📑", url, f"{feed_key=}")
    return fetch(url, verify=verify, feed_key=feed_key).json()


def fetch_image(url: str, *, verify: bool = False, feed_key: str = "") -> bytes | None:
    """Fetch an image."""
    try:
        req = fetch(solvers.alter_url(url), verify=verify, feed_key=feed_key)
        image = req.content
        if is_image_data(image):
            print(">>> ✅", url, f"{feed_key=}", flush=True)
            return image
        print(">>> 📛", url, f"{feed_key=}", flush=True)
    except Exception:
        print(">>> ❌", url, f"{feed_key=}", flush=True)
    return None


def find_image(key: str) -> custom_types.Metadata:
    """Find the image associated to the given `key`, which is a `small_hash()` value."""
    return next((meta for meta in retrieve_all_uniq_metadata() if meta.file[: constants.HASH_LEN] == key), "")


def fix_url(url: str) -> str:
    """Fix common URL issues.

    >>> fix_url("https://example.org/")
    'https://example.org/'
    >>> fix_url("https://example.org?do=rss")
    'https://example.org?do=rss'
    >>> fix_url("https://example.org/?do=rss")
    'https://example.org/?do=rss'
    >>> fix_url("https://example.org//shaarli/feed/rss?do=rss")
    'https://example.org/shaarli/feed/rss?do=rss'

    """
    parts = urlparse(url)
    parts = parts._replace(path=parts.path.replace("//", "/"))
    return urlunparse(parts)


def extract_content_type(req: requests.Response) -> str:
    """Extract the content type from the given request response."""
    return req.headers.get("content-type", "").replace(" ", "").split(";", 1)[0].lower()


def fetch_image_type(url: str, feed_key: str = "") -> str:
    """Fetch an image type using HTTP headers from the HEAD response."""
    req = fetch(url, method="head", feed_key=feed_key)
    content_type = extract_content_type(req)
    if (
        "image/" in content_type
        and content_type not in constants.IMAGES_CONTENT_TYPE
        and content_type not in constants.IMAGES_CONTENT_TYPE_IGNORED
    ):
        print(f"🎨 Unhandled {content_type=} for {url=} {feed_key=}", flush=True)
    return constants.IMAGES_CONTENT_TYPE.get(content_type, "")


def fetch_rss_feed(url: str, feed_key: str = "") -> feedparser.FeedParserDict:  # noqa: ARG001
    """Fetch a XML RSS feed."""
    debug(">>> 📜", url)
    """Make a HTTP call."""
    return feedparser.parse(fetch(url, from_the_past=False).text)


def get_a_slice(data: list, page: int, count: int) -> list:
    """Get a slice of a list.

    >>> get_a_slice(list(range(10)), 1, 1)
    [0]
    >>> get_a_slice(list(range(10)), 1, 5)
    [0, 1, 2, 3, 4]
    >>> get_a_slice(list(range(10)), 2, 5)
    [5, 6, 7, 8, 9]
    >>> get_a_slice(list(range(10)), 3, 5)
    []
    >>> get_a_slice(list(range(10)), 1, -1)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> get_a_slice(list(range(10)), 2, -1)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return data if count == -1 else data[(page - 1) * count : page * count]


def get_from_cache(cache_key: str) -> str | None:
    """Retreive a compressed response from a potential cache file."""
    file = constants.CACHE / f"{cache_key}.cache"
    with suppress(FileNotFoundError):
        return decompress(file.read_bytes()).decode()
    return None


def get_last(page: int, count: int) -> tuple[int, custom_types.Metadatas]:
    """Get last N images."""
    all_images = retrieve_all_uniq_metadata()
    return len(all_images), get_a_slice(all_images, page, count)


def get_metadata(image: str) -> tuple[str, custom_types.Metadata, str] | None:
    """Retrieve an given image metadata, including previous & next images."""
    all_cache = retrieve_all_uniq_metadata()
    for idx, metadata in enumerate(all_cache):
        if metadata.file == image:
            prev_img = all_cache[idx - 1].file if idx > 0 else ""
            next_img = all_cache[idx + 1].file if idx < len(all_cache) - 1 else ""
            return prev_img, metadata, next_img

    return None


def get_random_image() -> custom_types.Metadata:
    """Get a random image."""
    return choice(retrieve_all_uniq_metadata())  # noqa: S311


def get_size(file: Path) -> custom_types.Size:
    """Retrieve the file width & height."""
    im = cv2.imread(str(file))
    return custom_types.Size(width=im.shape[1], height=im.shape[0])


def get_tags() -> list[str]:
    """Get all available tags."""
    return sorted({tag for metadata in retrieve_all_uniq_metadata() for tag in metadata.tags})


def handle_item(item: feedparser.FeedParserDict, cache: dict, feed_key: str = "") -> bool:
    """Take a feed `item`, and populate the `cache` on success."""
    if not (link := solvers.guess_url(item.link, item.published_parsed, feed_key=feed_key)):
        return False

    cache_key = small_hash(link)
    metadata = cache.get(cache_key, {})
    in_cache = bool(metadata)

    if not (ext := metadata["file"][constants.HASH_LEN :] if in_cache else fetch_image_type(link, feed_key=feed_key)):
        # Cannot guess the image type (either because the URL does not end with a file extension,
        # or because we failed to fetch the image type from the Content-Type header response).
        return False

    output_file = constants.IMAGES / f"{cache_key}{ext}"
    if not output_file.is_file():
        if not (image := fetch_image(link, feed_key=feed_key)):
            return False

        output_file.write_bytes(image)

    create_thumbnail(output_file)

    if in_cache:
        return False

    # Prevent timeshift issues (https://stackoverflow.com/a/14467744/1117028)
    date = struct_time(list(item.published_parsed)[:8] + [-1])

    size = get_size(output_file)
    item.tags = [safe_tag(tag.term) for tag in getattr(item, "tags", [])]
    metadata |= {
        "checksum": checksum(output_file),
        "date": mktime(date),
        "description": item.description,
        "docolav": docolav(output_file),
        "file": output_file.name,
        "guid": item.guid,
        "height": size.height,
        "tags": item.tags,
        "title": item.title,
        "url": link,
        "width": size.width,
    }

    # NSFW
    if constants.NSFW not in metadata["tags"] and is_nsfw(item):
        metadata["tags"].append(constants.NSFW)

    metadata["tags"] = sorted(metadata["tags"])

    cache[cache_key] = metadata
    return True


def invalidate_caches() -> None:
    """Remove all cache files."""
    for file in constants.CACHE.glob("*.cache"):
        file.unlink(missing_ok=True)


def is_image_data(raw: bytes) -> bool:
    r"""Check whenever the provided `raw` data seems like a supported image format.

    >>> is_image_data(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")  # JPG with exif data
    True
    >>> is_image_data(b"\xff\xd8\xff\xe14\xbbExif\x00")  # JPG
    True
    >>> is_image_data(b"\x89PNG\r\n\x1a")  # PNG
    True
    >>> is_image_data(b"RIFFRh\x00\x00WE")  # WEBP
    True
    >>> is_image_data(b"\00")
    False

    """
    return raw.startswith(tuple(constants.IMAGES_MAGIC_SIG.values()))


def is_image_link(url: str) -> bool:
    """Check whenever the given `url` points to a supported image format.

    It will also prevent downloading again images from Shaarlimages.

    >>> is_image_link("ok.JPG")
    True
    >>> is_image_link("ok.jpeg")
    True
    >>> is_image_link("ok.jpg")
    True
    >>> is_image_link("ok.jfif")
    True
    >>> is_image_link("ok.pjp")
    True
    >>> is_image_link("ok.pjpeg")
    True
    >>> is_image_link("ok.png")
    True
    >>> is_image_link("ok.webp")
    True

    >>> is_image_link("unwanted.apng")
    False
    >>> is_image_link("unwanted.gif")
    False
    >>> is_image_link("unwanted.gifv")
    False
    >>> is_image_link("unwanted.svg")
    False
    >>> is_image_link("unwanted.tif")
    False

    >>> is_image_link("")
    False
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


def is_nsfw(item: feedparser.FeedParserDict) -> bool:
    """Return True when the given `item` seems Not Safe For Work.

    >>> is_nsfw({"tags": ["nsfw"]})
    True
    >>> is_nsfw({"tags": ["porn"]})
    True
    >>> is_nsfw({"tags": ["sexy"]})
    True

    >>> is_nsfw({"tags": ["fun"]})
    False

    """
    return any(tag in constants.NSFW_TAGS for tag in item.get("tags", []))


def load_metadata(feed: Path) -> custom_types.Metadatas:
    """Load a given `feed` into more a readable object."""
    cls = custom_types.Metadata
    return [cls(**metadata) for metadata in read(feed).values()]


def load_wayback_back_data(url: str) -> custom_types.Waybackdata:
    """Load stored Wayback Machine data."""
    data = read(constants.WAYBACK_MACHINE / f"{small_hash(url)}.json")
    return custom_types.Waybackdata(
        content_type=data.get("content_type", ""),
        is_lost=data.get("is_lost", False),
        snapshot=data.get("snapshot", ""),
    )


def lookup(term: str) -> custom_types.Metadatas:
    """Search for images.

    >>> lookup("ab")
    []

    """
    if len(term) < 3:  # noqa: PLR2004
        return []

    term = term.lower()
    return [
        metadata
        for metadata in retrieve_all_uniq_metadata()
        if (
            term in metadata.title.lower()
            or term in metadata.description.lower()
            or term in metadata.guid.lower()
            or term in metadata.file.lower()
            or term in metadata.tags
            or term in metadata.url.lower()
        )
    ]


def lookup_tag(tag: str) -> custom_types.Metadatas:
    """Search for images by tag."""
    tag = tag.lower()
    return [metadata for metadata in retrieve_all_uniq_metadata() if tag in metadata.tags]


def now() -> float:
    """Return the current UTC timestamp."""
    return today().timestamp()


def persist(file: Path, data: dict[str, Any]) -> None:
    """Save data into a JSON file."""
    file.parent.mkdir(exist_ok=True, parents=True)
    with file.open(mode="w") as fh:
        json.dump(data, fh, sort_keys=True, indent=0)
        fh.flush()
        os.fsync(fh.fileno())


def php_crc32(value: str) -> str:
    """PHP's `hash('crc32' $text, true)` equivalent function in Python.

    >>> php_crc32("20111006_131924")
    'c991f6df'
    >>> php_crc32("liens.mohja.fr")
    '0c05b1a5'

    References
    ----------
        - https://www.php.net/manual/en/function.hash-file.php#104836
        - https://stackoverflow.com/a/50843127/636849

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


def read(file: Path) -> dict[str, Any]:
    """Get contents of the JSON file."""
    return json.loads(file.read_text() or "{}") if file.is_file() else {}


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
    if not all_images:
        return []

    # Then, keep only the first published version of an image, skipping eventual duplicates (via reshares mostly)
    know_images = set()
    uniq_images = []
    for metadata in sorted(all_images, key=lambda meta: meta.date):
        if metadata.checksum in know_images:
            continue
        know_images.add(metadata.checksum)
        uniq_images.append(metadata)

    res = uniq_images[::-1]
    store_in_cache(cache_key, json.dumps(res, default=lambda s: vars(s)), info=False)
    return res


def safe_tag(tag: str, cleanup: re.Pattern = re.compile(r"--+")) -> str:
    """Sanitize a tag.

    >>> safe_tag("B/W_&_colors?!§")
    'b-w-colors'

    """
    return cleanup.sub(
        "-",
        tag.lower()
        .replace("/", "-")
        .replace("_", "-")
        .replace("&", "-")
        .replace("?", "")
        .replace("!", "")
        .replace("§", ""),
    ).strip()


def set_wayback_back_data(url: str, waybackdata: custom_types.Waybackdata) -> None:
    """Store Wayback Machine data."""
    persist(constants.WAYBACK_MACHINE / f"{small_hash(url)}.json", vars(waybackdata))


def small_hash(value: str) -> str:
    """Return the small hash of a string, using RFC 4648 base64url format.

    http://sebsauvage.net/wiki/doku.php?id=php:shaarli.

    Small hashes:
    - are unique (well, as unique as crc32, at last)
    - are always 6 characters long (`constants.HASH_LEN`)
    - only use the following characters: a-z A-Z 0-9 - _ @
    - are NOT cryptographically secure (they CAN be forged)

        >>> small_hash("20111006_131924")
        'yZH23w'

    """
    return b64encode(bytes.fromhex(php_crc32(value)), altchars=b"-_").rstrip(b"=").decode()


def store_in_cache(cache_key: str, response: str, *, info: bool = True) -> None:
    """Store a HTTP response into a compressed cache file."""
    if info:
        response += f"\n<!-- Cached: {today()} -->\n"

    file = constants.CACHE / f"{cache_key}.cache"
    file.parent.mkdir(exist_ok=True, parents=True)
    file.write_bytes(compress(response.encode(), level=9))


def today() -> datetime:
    """Return the current UTC date."""
    return datetime.now(tz=timezone.utc)


def try_wayback_machine(url: str, method: str, *, force: bool = False, feed_key: str = "") -> requests.Response:
    """Try to fetch a given `url` using the great Wayback Machine."""
    waybackdata = load_wayback_back_data("unknown" if force else url)

    if waybackdata.is_lost:
        raise EvanescoError

    if method == "head" and waybackdata.content_type:
        response = requests.Response()
        response.headers = CaseInsensitiveDict({"Content-Type": waybackdata.content_type})
        response.status_code = 200
        response.url = waybackdata.snapshot
        return response

    if not waybackdata.snapshot:
        url_archive = f"https://archive.org/wayback/available?url={url}"
        with fetch(url_archive, from_the_past=False, feed_key=feed_key) as req:
            if not (snapshot := req.json()["archived_snapshots"].get("closest", {}).get("url")):
                print(">>> 💀", url, flush=True)
                waybackdata.is_lost = True
                set_wayback_back_data(url, waybackdata)
                raise EvanescoError

        # Use direct access to the resource
        parts = urlparse(snapshot)
        path = parts.path
        parts_path = path.split("/")
        parts_path[2] += "if_"

        waybackdata.snapshot = urlunparse(parts._replace(path="/".join(parts_path), scheme="https"))
        set_wayback_back_data(url, waybackdata)

    debug(f">>> ⌛ [{method.upper()}]", url)

    with fetch(waybackdata.snapshot, method=method, from_the_past=False, feed_key=feed_key) as req:
        if method == "head":
            if content_type := extract_content_type(req):
                waybackdata.content_type = content_type
                set_wayback_back_data(url, waybackdata)
            else:
                print(">>> 💀", url, flush=True)
                waybackdata.is_lost = True
                set_wayback_back_data(url, waybackdata)
                raise EvanescoError

        return req
