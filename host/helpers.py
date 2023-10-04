"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import math
from pathlib import Path
from time import mktime
from urllib.parse import urlparse

import config
import constants
import custom_types
import functions
import version
from bottle import FormsDict, redirect, template

#
# Sync
#


def sync_feed(index: int, force: bool = False) -> dict[str, int]:
    """Sync one feed."""
    url = functions.read(constants.SHAARLIS)["feeds"][index]
    host = urlparse(url).hostname
    cache_key = functions.small_hash(host)
    cache_file = constants.CACHE_FEEDS / f"{cache_key}.json"
    cache: custom_types.Cache = functions.read(cache_file)
    latest_image = float(max(cache.keys(), key=float)) if cache else 0.0

    # First sync, starts from the begining
    if force or not cache:
        url += "&nb=all" if url.endswith("?do=rss") else "?nb=all"

    print(f"START {index=} {host=} feed={cache_key!r}")

    feed = functions.fetch_rss_feed(url)
    new_images = 0

    for item in feed.entries:
        published = mktime(item.published_parsed)
        if not force and published < latest_image:
            break

        # Strip URL parameters
        link = item.link.split("?", 1)[0]
        if not functions.is_image_link(link):
            continue

        parts = urlparse(link)
        file = parts.path
        if parts.fragment and functions.is_image_link(parts.fragment):
            # Ex: https://commons.wikimedia.org/wiki/Gustave_Dor%C3%A9#/media/File:Paradise_Lost_12.jpg
            file += f"_{parts.fragment}"
        path = Path(file)
        file = f"{functions.small_hash(link)}_{functions.safe_filename(path.stem)}{path.suffix.lower()}"
        output_file = constants.IMAGES / file

        if not output_file.is_file():
            if not (image := functions.fetch_image(link)):
                continue

            output_file.write_bytes(image)

        key = str(published)
        if key in cache:
            continue

        if not (size := functions.get_size(output_file)):
            output_file.unlink(missing_ok=True)
            continue

        metadata = {
            "desc": item.description,
            "docolav": functions.docolav(output_file),
            "guid": item.guid,
            "height": size.height,
            "link": file,
            "tags": [tag.term.lower().strip() for tag in getattr(item, "tags", [])],
            "title": item.title,
            "width": size.width,
        }

        # NSFW
        if (
            any(tag in constants.NSFW_TAGS for tag in metadata["tags"])
            or constants.NSFW in item.title.lower()
            or constants.NSFW in item.description.lower()
        ) and constants.NSFW not in metadata["tags"]:
            metadata["tags"].append(constants.NSFW)

        metadata["tags"] = sorted(metadata["tags"])

        cache[key] = metadata
        new_images += 1

        if new_images % 10 == 0:
            functions.persist(cache_file, cache)

    if new_images:
        functions.persist(cache_file, cache)
        functions.invalidate_cache()

    print(f"END {index=} {host} feed={cache_key!r} (+ {new_images})")
    return {"count": new_images}


def sync_feeds(force: bool = False) -> custom_types.Shaarlis:
    """Retrieve the JSON file containing all shaarlis feed's."""
    data = {"feeds": [], "updated": functions.now()}
    file = constants.SHAARLIS

    if not force and file.is_file():
        stored_data = functions.read(file)
        if data["updated"] - stored_data["updated"] < config.SYNC["ttl"]:
            return stored_data["feeds"]

    url = str(config.SYNC["url"])
    data["feeds"] = sorted({shaarli["url"] for shaarli in functions.fetch_json(url)})

    functions.persist(file, data)
    return data["feeds"]


def sync_them_all(force: bool = False) -> None:
    """Sync all feeds."""
    sync_feeds(force=force)

    for idx in range(len(functions.read(constants.SHAARLIS)["feeds"])):
        sync_feed(idx, force=force)


#
# Web
#


def lookup(value: str) -> custom_types.Images:
    """Search for images."""
    value = value.lower()

    if len(value) < 3:
        return []

    res = sorted(
        (float(date), (metadata["link"], metadata["tags"], ""))
        for feed in constants.CACHE_FEEDS.glob("*.json")
        for date, metadata in functions.read(feed).items()
        if (
            value in metadata["title"]
            or value in metadata["desc"]
            or value in metadata["guid"]
            or value in metadata["link"]
            or value in metadata["tags"]
        )
    )

    # Uniquify
    know_images = set()
    uniq_images = []
    for _, images in res:
        if images[0] in know_images:
            continue
        uniq_images.append(images)
        know_images.add(images[0])

    return uniq_images[::-1]


def lookup_tag(tag: str) -> custom_types.Images:
    """Search for images by tag."""
    tag = tag.lower()
    return [metadata for metadata in functions.read(constants.CACHE_HOME_ALL) if tag in metadata[1]]


def render(tpl: str, **kwargs) -> str:
    """Render a template with provided keyword arguments."""
    return template(tpl, **kwargs, version=version.__version__, site=config.SITE, template_lookup=[constants.VIEWS])


def render_home_page(page: int) -> str:
    """Render the home page."""
    total, images = functions.get_last(page, config.SITE["display_last_n_images"])
    last = math.ceil(total / config.SITE["display_last_n_images"])

    if page > last:
        redirect(f"/page/{last}")

    return render("page", **locals())


def render_home_pagination_page(page: int) -> str:
    """Render a pagined page."""
    if page < 1:
        redirect("/page/1")

    return render_home_page(page)


def render_rss_feed(params: FormsDict) -> str:
    """Render the XML RSS feed."""
    return ""


def render_search(images: custom_types.Images) -> str:
    """Render search results."""
    total = len(images)
    page = last = 0
    return render("page", **locals())


def render_update_page() -> str:
    """Render the update page."""
    return render("update", feeds=sync_feeds())


def render_zoom_page(image: str) -> str:
    """Render an image page."""
    metadata = functions.get_metadata(image)
    prev_img, next_img = functions.get_prev_next(image)
    css_class = functions.any_css_class_question()
    return render("zoom", **locals())
