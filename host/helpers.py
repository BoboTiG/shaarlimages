"""This is part of Shaarlimages.

Source: https://github.com/BoboTiG/shaarlimages.
"""

import math
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import get_ident
from typing import Any

import config
import constants
import custom_types
import functions
import requests.exceptions
import urllib3.exceptions
import version
from bottle import redirect, request, response, template

#
# Sync
#


def sync_feed(url: str, *, force: bool = False) -> int:
    """Sync a shaarli."""
    feed_key = functions.feed_key(url)
    cache_key = functions.small_hash(feed_key)
    cache_file = constants.FEEDS / f"{cache_key}.json"
    cache = functions.read(cache_file)

    url = functions.fix_url(url)

    # First sync, starts from the begining
    if force or not cache:
        url += "&nb=all" if url.endswith(("?do=rss", "?do=atom")) else "?nb=all"

    functions.debug(f"START {get_ident()} {feed_key=} {cache_key=}")

    try:
        feed = functions.fetch_rss_feed(url)
    except Exception:
        functions.debug(f"END {get_ident()} {feed_key=} {cache_key=} (-1)")
        return -1

    new_images = 0

    for item in feed.entries:
        if not hasattr(item, "published_parsed"):
            # Sadly, Shaarli is configured with HIDE_TIMESTAMPS=true
            # https://github.com/sebsauvage/Shaarli/blob/029f75f/index.php#L23
            now = functions.today()
            item.published_parsed = now.utctimetuple()

        try:
            new_images += int(functions.handle_item(item, cache, feed_key=cache_key))
        except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError, functions.EvanescoError):
            pass
        except Exception as exc:
            print(f"🐛 {get_ident()} {type(exc).__name__} on {item=}", flush=True)
            print(f"{exc}", flush=True)

    if new_images:
        functions.persist(cache_file, cache)
        functions.invalidate_caches()

    amount = f"+{new_images}" if new_images else "0"
    if new_images:
        print(f"END {get_ident()} {feed_key=} {cache_key=} ({amount})", flush=True)
    return new_images


def sync_feeds(*, force: bool = False) -> custom_types.Shaarlis:
    """Retrieve the JSON file containing all shaarlis."""
    data = {"feeds": None, "updated": functions.now()}
    file = constants.SHAARLIS

    if not force and file.is_file():
        stored_data = functions.read(file)
        if data["updated"] - stored_data["updated"] < constants.FEEDS_TTL:
            return stored_data["feeds"]

    fetched_feeds = functions.fetch_json(constants.FEEDS_URL, verify=True)
    if data["feeds"] != fetched_feeds:
        data["feeds"] = fetched_feeds
        functions.persist(file, data)

    return fetched_feeds


def sync_them_all(*, force: bool = False) -> None:
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

    last = math.ceil(total / config.SITE.images_per_page) or 1

    if page > last:
        redirect(f"{path}/{last}")

    tags = functions.get_tags()
    rss_link = f"/rss{path.replace('/page', '')}"
    return render("page", **locals())


def render(tpl: str, **kwargs: Any) -> str:  # noqa: ANN401
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


def render_rss(images: custom_types.Metadatas, count: int = config.SITE.images_per_page) -> str:
    """Render the RSS feed."""
    images = functions.get_a_slice(images, 1, count)
    response.content_type = "application/rss+xml"
    return functions.craft_feed(images, request.path)


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
