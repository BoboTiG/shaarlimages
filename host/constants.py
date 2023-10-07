"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

from custom_types import Size

# Folders
ROOT = Path(__file__).parent.parent
HOST = ROOT / "host"
ASSETS = HOST / "assets"
DATA = ROOT / "data"
FEEDS = DATA / "feeds"
IMAGES = DATA / "images"
THUMBNAILS = DATA / "thumbnails"
VIEWS = HOST / "views"

# Files
SHAARLIS = DATA / "shaarlis.json"

# Sync
HTTP_REQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
}
FEEDS_TTL = 60 * 60 * 6  # 6 hours
FEEDS_URL = "https://www.ecirtam.net/shaarli-api/feeds?disabled=0"
IMAGE_EXT = (".jpeg", ".jpg", ".png")
IMAGES_MAGIC_SIG = (b"\xff\xd8\xff", b"\x89PNG")
NSFW = "nsfw"
NSFW_TAGS = {"hentai", "hentaï", "nude", NSFW, "sex", "sexe", "sexy"}
THUMBNAIL_MAX_SIZE = Size(width=400, height=400)

# Local web server
HTTP_PORT = 8080
