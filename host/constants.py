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
FEEDS_URL = "https://www.ecirtam.net/shaarli-api/feeds?full=1"
# https://www.iana.org/assignments/media-types/media-types.xhtml#image
IMAGE_EXT = (".jfif", ".jpeg", ".jpg", ".pjp", ".pjpeg", ".png", ".webp")
IMAGES_MAGIC_SIG = {".jpg": b"\xff\xd8\xff", ".png": b"\x89PNG", ".webp": b"RIFF"}
IMAGES_CONTENT_TYPE = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
IMAGES_CONTENT_TYPE_IGNORED = {"image/apng", "image/gif", "image/svg+xml"}
NSFW = "nsfw"
THUMBNAIL_MAX_SIZE = Size(width=400, height=400)

# Local web server
HTTP_PORT = 8080

# Additional shaarlis
MORE_SHAARLIS = [
    {"url": "http://140.238.202.186:8080/feed/atom"},
    {"url": "http://abrochier.org/sha//feed/rss"},
    {"url": "http://lwuibr.free.fr/shaarli/?do=rss"},
    {"url": "http://shaarli.sam7.blog/?do=atom"},
    {"url": "http://shaarli.speakerine.fr/?do=atom"},
    {"url": "http://wwwcdorg.hd.free.fr/shaarli/feed/atom"},
    {"url": "https://arthur.lutz.im/shaarli/feed/atom"},
    {"url": "https://bm.raphaelbastide.com/feed/atom"},
    {"url": "https://brouillon.zici.fr/liens/feed/atom"},
    {"url": "https://dmeloni.fr/shaarli/?do=rss"},
    {"url": "https://foxicorn.red/shaarli/feed/atom"},
    {"url": "https://gregoire.surrel.org/links/?do=atom"},
    {"url": "https://l.wentao.org//feed/atom"},
    {"url": "https://liens.ordinator.fr/?do=atom"},
    {"url": "https://links.nixdevil.com/feed/atom"},
    {"url": "https://news.restez-curieux.ovh/feed/atom"},
    {"url": "https://romainmarula.fr/Shaarli/feed/atom"},
    {"url": "https://shaarli.4nton.dk/feed/atom"},
    {"url": "https://shaarli.antredugreg.be/?do=rss"},
    {"url": "https://shaarli.demapage.fr/feed/atom"},
    {"url": "https://shaarli.dreads-unlock.fr/feed/atom"},
    {"url": "https://shaarli.gardes.fr/feed/atom"},
    {"url": "https://shaarli.grimbox.be/feed/atom"},
    {"url": "https://shaarli.iooner.io/feed/atom"},
    {"url": "https://shaarli.kazhnuz.space/feed/atom"},
    {"url": "https://shaarli.kcaran.com/feed/atom"},
    {"url": "https://shaarli.lyc-lecastel.fr/feed/atom"},
    {"url": "https://shaarli.nailyk.fr/feed/atom"},
    {"url": "https://shaarli.rosenberg-watt.com/feed/atom"},
    {"url": "https://shaarli.underworld.fr/fouine/?do=atom"},
    {"url": "https://top7box.com/shaarli/feed/atom"},
    {"url": "https://www.funksys.net/feed/atom"},
    {"url": "https://www.joelmariteau.fr/shaarli/?do=atom"},
    {"url": "https://www.musee-gourmandise.be/shaarli/index.php?do=rss"},
    {"url": "https://www.orpheomundi.fr/shaarli/?do=rss"},
]
