"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import math
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import get_ident
from time import mktime

import config
import constants
import custom_types
import functions
import requests.exceptions
import urllib3.exceptions
import version
from bottle import redirect, request, template

#
# Sync
#


def sync_feed(url: str, force: bool = False) -> int:
    """Sync a shaarli."""
    feed_key = functions.feed_key(url)
    cache_key = functions.small_hash(feed_key)
    cache_file = constants.FEEDS / f"{cache_key}.json"
    cache: dict[str, str] = functions.read(cache_file)
    latest_image = float(max(cache.keys(), key=float)) if cache else 0.0

    # First sync, starts from the begining
    if force or not cache:
        url += "&nb=all" if url.endswith("?do=rss") else "?nb=all"

    print(f"START {get_ident()} {feed_key=} {cache_key=}", flush=True)

    try:
        feed = functions.fetch_rss_feed(url)
    except Exception:
        print(f"END {get_ident()} {feed_key=} {cache_key=} (-1)", flush=True)
        return -1

    total_new_images = 0
    count = 0

    for item in feed.entries:
        if not hasattr(item, "published_parsed"):
            # Shaarli is configured with HIDE_TIMESTAMPS=true
            # https://github.com/sebsauvage/Shaarli/blob/029f75f/index.php#L23
            item.published_parsed = functions.today().utctimetuple()

        published = mktime(item.published_parsed)
        if not force and published < latest_image:
            break

        try:
            is_new, metadata = functions.handle_item(item, cache.get(str(published), {}))
        except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError, functions.Evanesco):
            continue
        except Exception as exc:
            print(f"🐛 {get_ident()} {type(exc).__name__} on {item=}", flush=True)
            print(f"{exc}", flush=True)
            continue

        if not metadata:
            continue

        cache[str(published)] = metadata
        if is_new:
            total_new_images += 1

        count += 1
        if count % 10 == 0 and cache:  # pragma: nocover
            functions.persist(cache_file, cache)
            count = 0

    if count and cache:
        functions.persist(cache_file, cache)

    if total_new_images:
        functions.invalidate_caches()

    amount = f"+{total_new_images}" if total_new_images else "0"
    print(f"END {get_ident()} {feed_key=} {cache_key=} ({amount})", flush=True)
    return total_new_images


def sync_feeds(force: bool = False) -> custom_types.Shaarlis:
    """Retrieve the JSON file containing all shaarlis."""
    data = {"feeds": [], "updated": functions.now()}
    file = constants.SHAARLIS

    if not force and file.is_file():
        stored_data = functions.read(file)
        if data["updated"] - stored_data["updated"] < constants.FEEDS_TTL:
            return stored_data["feeds"]

    # Remove duplicates
    uniq_feeds = []
    known_feeds = set()
    for shaarli in functions.fetch_json(constants.FEEDS_URL):
        url = shaarli["url"]
        key = functions.feed_key(url)
        if url and key not in known_feeds:
            known_feeds.add(key)
            uniq_feeds.append(url)

    data["feeds"] = sorted(uniq_feeds)

    functions.persist(file, data)
    return data["feeds"]


def sync_them_all(force: bool = False) -> None:
    """Sync all shaarlis."""
    sync_feeds(force=force)

    all_url = functions.read(constants.SHAARLIS)["feeds"]
    with ThreadPoolExecutor() as pool:
        pool.map(partial(sync_feed, force=force), all_url)


#
# Web
#


def pagination(images: custom_types.Metadatas, total: int, page: int) -> str:
    """Pagined page renderer."""
    path = request.path.removesuffix(f"/{page}")

    if page < 1:
        redirect(f"{path}/1")

    last = math.ceil(total / config.SITE.images_per_page)

    if page > last:
        redirect(f"{path}/{last}")

    tags = functions.get_tags()
    return render("page", **locals())


def render(tpl: str, **kwargs) -> str:
    """Render a template with provided keyword arguments."""
    return template(
        tpl,
        **kwargs,
        headers=[],
        version=version.__version__,
        site=config.SITE,
        template_lookup=[constants.VIEWS],
    )


def render_home_page(page: int) -> str:
    """Render the home page."""
    total, images = functions.get_last(page, config.SITE.images_per_page)
    return pagination(images, total, page)


def render_search(images: custom_types.Images, page: int) -> str:
    """Render search results."""
    total = len(images)
    images = functions.get_a_slice(images, page, config.SITE.images_per_page)
    return pagination(images, total, page)


def render_zoom_page(image: custom_types.Image) -> str:
    """Render an image page."""
    if not (result := functions.get_metadata(image)):
        redirect("/")

    prev_img, metadata, next_img = result
    css_class = functions.any_css_class_question()
    return render("zoom", **locals())
