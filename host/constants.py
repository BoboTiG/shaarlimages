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
# Unsupported image types
# image/apng: animation would make the gallery weird, issues with thumbnails & dominant color
# image/gif: animation would make the gallery weird, issues with thumbnails & dominant color
# image/svg+xml: issues with color average
# image/tiff: files are too big
IMAGES_CONTENT_TYPE_IGNORED = {"image/apng", "image/gif", "image/svg+xml", "image/tiff"}
NSFW = "nsfw"
THUMBNAIL_MAX_SIZE = Size(width=400, height=400)

# Local web server
HTTP_PORT = 8080

# Additional shaarlis
MORE_SHAARLIS = [
    {"url": "http://140.238.202.186:8080/feed/atom"},
    {"url": "http://abrochier.org/sha//feed/rss"},
    {"url": "http://l.pot.cat/?do=atom"},
    {"url": "http://ludo.amok.free.fr/shaarli/?do=rss"},
    {"url": "http://lwuibr.free.fr/shaarli/?do=rss"},
    {"url": "http://osveji.com/?do=atom"},
    {"url": "http://perrot.thierry.free.fr/rss.xml"},
    {"url": "http://profouzors.fr/feed/atom"},
    {"url": "http://signets.daoust.media/?do=rss"},
    {"url": "http://shaarli.sam7.blog/?do=atom"},
    {"url": "http://shaarli.speakerine.fr/?do=atom"},
    {"url": "http://shaarli.veneau.net/feed/atom"},
    {"url": "http://www.ngourillon.com/links/?do=rss"},
    {"url": "http://wwwcdorg.hd.free.fr/shaarli/feed/atom"},
    {"url": "https://amy.cat/feed/atom"},
    {"url": "https://arthur.lutz.im/shaarli/feed/atom"},
    {"url": "https://bm.raphaelbastide.com/feed/atom"},
    {"url": "https://bookmarks.simeonradivoev.com/feed/atom"},
    {"url": "https://brouillon.zici.fr/liens/feed/atom"},
    {"url": "https://deleurme.net/liens/?do=rss"},
    {"url": "https://dmeloni.fr/shaarli/?do=rss"},
    {"url": "https://dreamhome.zone:8060/feed/atom"},
    {"url": "https://evroundup.net/feed/atom"},
    {"url": "https://foxicorn.red/shaarli/feed/atom"},
    {"url": "https://gregoire.surrel.org/links/?do=atom"},
    {"url": "https://herr-pfeiffer.de/shaarli/feed/atom"},
    {"url": "https://ireading.info/feed/atom"},
    {"url": "https://l.wentao.org//feed/atom"},
    {"url": "https://lebaohiep.com/feed/atom"},
    {"url": "https://liens.ordinator.fr/?do=atom"},
    {"url": "https://link.boiteataquets.org/feed/atom"},
    {"url": "https://links.angristan.xyz/feed/atom"},
    {"url": "https://links.izissise.net/feed/atom"},
    {"url": "https://links.kirsch.mx/feed/atom"},
    {"url": "https://links.leicher.me/feed/atom"},
    {"url": "https://links.martyoeh.me/feed/atom"},
    {"url": "https://links.nixdevil.com/feed/atom"},
    {"url": "https://links.portailpro.net/?do=rss"},
    {"url": "https://links.solarchemist.se/feed/atom"},
    {"url": "https://links.thetaggarthouse.com/feed/atom"},
    {"url": "https://lz.lewumpy.de/?do=atom"},
    {"url": "https://martouf.ch/liens/?do=rss"},
    {"url": "https://news.restez-curieux.ovh/feed/atom"},
    {"url": "https://news.torii-security.fr/feed/atom"},
    {"url": "https://nymous.io/?do=rss"},
    {"url": "https://radix.mywire.org/feed/atom"},
    {"url": "https://ressources.fransgenre.fr/feed/atom"},
    {"url": "https://romainmarula.fr/Shaarli/feed/atom"},
    {"url": "https://s.yul.li/feed/atom"},
    {"url": "https://shaarli.4nton.dk/feed/atom"},
    {"url": "https://shaarli.anael.cloud/feed/atom"},
    {"url": "https://shaarli.antredugreg.be/?do=rss"},
    {"url": "https://shaarli.capsule-corp.fr/feed/atom"},
    {"url": "https://shaarli.cardina1.red/feed/atom"},
    {"url": "https://shaarli.chenze60.cc:4433/feed/atom"},
    {"url": "https://shaarli.demapage.fr/feed/atom"},
    {"url": "https://shaarli.dreads-unlock.fr/feed/atom"},
    {"url": "https://shaarli.gardes.fr/feed/atom"},
    {"url": "https://shaarli.grimbox.be/feed/atom"},
    {"url": "https://shaarli.grummi.net/feed/atom"},
    {"url": "https://shaarli.hoab.fr/feed/atom"},
    {"url": "https://shaarli.hotinno.com/feed/atom"},
    {"url": "https://shaarli.iooner.io/feed/atom"},
    {"url": "https://shaarli.kazhnuz.space/feed/atom"},
    {"url": "https://shaarli.kcaran.com/feed/atom"},
    {"url": "https://shaarli.lain.li/feed/atom"},
    {"url": "https://shaarli.libretgeek.fr/feed/atom"},
    {"url": "https://shaarli.lyc-lecastel.fr/feed/atom"},
    {"url": "https://shaarli.nailyk.fr/feed/atom"},
    {"url": "https://shaarli.rosenberg-watt.com/feed/atom"},
    {"url": "https://shaarli.underworld.fr/fouine/?do=atom"},
    {"url": "https://tech.deuchnord.fr/feed/atom"},
    {"url": "https://tobru.guru/feed/atom"},
    {"url": "https://top7box.com/shaarli/feed/atom"},
    {"url": "https://www.ainw.org/links/perso/feed/atom"},
    {"url": "https://www.cyber-news.fr/feed/atom"},
    {"url": "https://www.funksys.net/feed/atom"},
    {"url": "https://www.joelmariteau.fr/shaarli/?do=atom"},
    {"url": "https://www.musee-gourmandise.be/shaarli/index.php?do=rss"},
    {"url": "https://www.orpheomundi.fr/shaarli/?do=rss"},
    {"url": "https://www.wanderings.net/links//feed/atom"},
]
