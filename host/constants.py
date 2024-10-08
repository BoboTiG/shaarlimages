"""This is part of Shaarlimages.

Source: https://github.com/BoboTiG/shaarlimages.
"""

import os
from pathlib import Path

from custom_types import Size

# CI
IS_CI = "CI" in os.environ

# Folders
ROOT = Path(__file__).parent.parent
HOST = ROOT / "host"
ASSETS = HOST / "assets"
CACHE = ROOT / "cache"
DATA = ROOT / "data"
FEEDS = DATA / "feeds"
IMAGES = DATA / "images"
THUMBNAILS = DATA / "thumbnails"
VIEWS = HOST / "views"
WAYBACK_MACHINE = DATA / "wayback-machine"

# Files
SHAARLIS = DATA / "shaarlis.json"

# Sync
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
FEEDS_TTL = 60 * 60 * 6  # 6 hours
FEEDS_URL = "https://raw.githubusercontent.com/BoboTiG/shaarlis/main/shaarlis.json"
# https://www.iana.org/assignments/media-types/media-types.xhtml#image
IMAGE_EXT = (".jfif", ".jpeg", ".jpg", ".pjp", ".pjpeg", ".png", ".webp")
IMAGES_MAGIC_SIG = {".jpg": b"\xff\xd8\xff", ".png": b"\x89PNG", ".webp": b"RIFF"}
IMAGES_CONTENT_TYPE = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
# Unsupported image types
# image/apng: animation would make the gallery weird, issues with thumbnails & dominant color
# image/gif: animation would make the gallery weird, issues with thumbnails & dominant color
# image/svg+xml: issues with color average
# image/tiff: files are too big
IMAGES_CONTENT_TYPE_IGNORED = {"image/apng", "image/gif", "image/svg+xml", "image/tiff"}
NSFW = "nsfw"
NSFW_TAGS = {NSFW, "porn", "sexy"}
THUMBNAIL_MAX_SIZE = Size(width=400, height=400)
HASH_LEN = 6  # `small_hash()` value is always 6 characters long

# Local web server
HTTP_PORT = 8080
