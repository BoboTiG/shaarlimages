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
import solvers
import version
from bottle import redirect, template

#
# Sync
#


def sync_feed(url: str, force: bool = False) -> dict[str, int]:
    """Sync a shaarli."""
    host = urlparse(url).hostname
    cache_key = functions.small_hash(host)
    cache_file = constants.CACHE_FEEDS / f"{cache_key}.json"
    cache: custom_types.Cache = functions.read(cache_file)
    latest_image = float(max(cache.keys(), key=float)) if cache else 0.0

    # First sync, starts from the begining
    if force or not cache:
        url += "&nb=all" if url.endswith("?do=rss") else "?nb=all"

    print(f"START {url=} feed={cache_key!r}")

    feed = functions.fetch_rss_feed(url)
    total_new_images = 0
    count = 0

    for item in feed.entries:
        published = mktime(item.published_parsed)
        if not force and published < latest_image:
            break

        if not (link := solvers.guess_url(item.link, item.published_parsed)):
            continue

        path = Path(link)
        file = f"{functions.small_hash(link)}_{functions.safe_filename(path.stem)}{path.suffix.lower()}"
        output_file = constants.IMAGES / file

        if not output_file.is_file():
            if not (image := functions.fetch_image(link)):
                continue

            output_file.write_bytes(image)
            total_new_images += 1

        if not (size := functions.get_size(output_file)) or not functions.create_thumbnail(output_file):
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
        cache[str(published)] = metadata

        count += 1
        if count % 10 == 0:
            functions.persist(cache_file, cache)
            count = 0

    if count:
        functions.persist(cache_file, cache)

    print(f"END {url=} feed={cache_key!r} (+ {total_new_images})")
    return {"count": total_new_images}


def sync_feeds(force: bool = False) -> custom_types.Shaarlis:
    """Retrieve the JSON file containing all shaarlis."""
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
    """Sync all shaarlis."""
    sync_feeds(force=force)

    for url in functions.read(constants.SHAARLIS)["feeds"]:
        sync_feed(url, force=force)


#
# Web
#


def render(tpl: str, **kwargs) -> str:
    """Render a template with provided keyword arguments."""
    return template(
        tpl, **kwargs, headers=[], version=version.__version__, site=config.SITE, template_lookup=[constants.VIEWS]
    )


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


def render_search(images: custom_types.Images) -> str:
    """Render search results."""
    total = len(images)
    page = last = 0
    return render("page", **locals())


def render_zoom_page(image: custom_types.Image) -> str:
    """Render an image page."""
    if not (metadata := functions.get_metadata(image)):
        redirect("/")

    prev_img, next_img = functions.get_prev_next(image)
    css_class = functions.any_css_class_question()
    return render("zoom", **locals())
