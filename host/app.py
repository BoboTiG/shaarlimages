"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from functools import wraps

import bottle
import constants
import functions
import helpers
import version
from bottle import HTTPResponse, default_app, redirect, request, route, static_file

__version__ = version.__version__
__author__ = "Mickaël Schoentgen"
__copyright__ = """
Copyright (c) 2013-2014,2023, Mickaël 'Tiger-222' Schoentgen

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee or royalty is hereby
granted, provided that the above copyright notice appear in all copies
and that both that copyright notice and this permission notice appear
in supporting documentation or portions thereof, including
modifications, that you make.
"""


def cache(function):
    """Decorator used to cache HTTP responses."""

    @wraps(function)
    def wrapper(*args, **kwargs) -> str:
        if bottle.DEBUG:  # pragma: nocover
            return function(*args, **kwargs)

        cache_key = functions.small_hash(request.path.lower())
        if (response := functions.get_from_cache(cache_key)) is None:
            response = function(*args, **kwargs)
            functions.store_in_cache(cache_key, response)

        return response

    return wrapper


@route("/")
def page_home() -> str:
    """Display the primary page."""
    redirect("/page/1")


@route("/page/<page:int>")
@cache
def page_home_pagination(page: int) -> str:
    """Display a pagined page."""
    return helpers.render_home_page(page)


@route("/random")
def page_random() -> str:
    """Display a random image."""
    image = functions.get_random_image()
    redirect(f"/zoom/{image.link}")


@route("/zoom/<image>")
def page_zoom(image: str) -> str:
    """Display an image."""
    return helpers.render_zoom_page(image)


@route("/rss")
@cache
def rss() -> str:
    """Main RSS feed."""
    return helpers.render_rss(functions.retrieve_all_uniq_metadata())


@route("/rss/all")
@cache
def rss_all() -> str:
    """Main RSS feed for all entries (do not abuse)."""
    return helpers.render_rss(functions.retrieve_all_uniq_metadata(), count=-1)


@route("/rss/<count:int>")
@cache
def rss_with_custom_items_count(count: int) -> str:
    """Main RSS feed with custom items count."""
    return helpers.render_rss(functions.retrieve_all_uniq_metadata(), count=count)


@route("/rss/search/<term>")
@cache
def rss_search_by_term(term: str) -> str:
    """RSS feed for searches."""
    return helpers.render_rss(functions.lookup(term))


@route("/rss/search/<term>/all")
@cache
def rss_search_by_term_all(term: str) -> str:
    """RSS feed for all searches result."""
    return helpers.render_rss(functions.lookup(term), count=-1)


@route("/rss/search/<term>/<count:int>")
@cache
def rss_search_by_term_with_custom_items_count(term: str, count: int) -> str:
    """RSS feed for searches with custom items count."""
    return helpers.render_rss(functions.lookup(term), count=count)


@route("/rss/search/tag/<tag>")
@cache
def rss_search_by_tag(tag: str) -> str:
    """RSS feed for tag searches."""
    return helpers.render_rss(functions.lookup_tag(tag))


@route("/rss/search/tag/<tag>/all")
@cache
def rss_search_by_tag_all(tag: str) -> str:
    """RSS feed for all tag searches result."""
    return helpers.render_rss(functions.lookup_tag(tag), count=-1)


@route("/rss/search/tag/<tag>/<count:int>")
@cache
def rss_search_by_tag_with_custom_items_count(tag: str, count: int) -> str:
    """RSS feed for tag searches with custom items count."""
    return helpers.render_rss(functions.lookup_tag(tag), count=count)


@route("/search/<term>")
def search(term: str) -> str:
    """Search for images."""
    redirect(f"/search/{term}/1")


@route("/search/<term>/<page:int>")
@cache
def search_pagination(term: str, page: int) -> str:
    """Pagined search for images."""
    return helpers.render_search(functions.lookup(term), page)


@route("/search/tag/<tag>")
def search_by_tag(tag: str) -> str:
    """Search for images by tag."""
    redirect(f"/search/tag/{tag}/1")


@route("/search/tag/<tag>/<page:int>")
@cache
def search_by_tag_pagination(tag: str, page: int) -> str:
    """Pagined search for images by tag."""
    return helpers.render_search(functions.lookup_tag(tag), page)


@route("/assets/<file:path>")
def static_asset(file: str) -> HTTPResponse:
    """Get a resource file used by the website."""
    response = static_file(file, root=constants.ASSETS)
    response.set_header("Cache-Control", "public, max-age=31536000")
    return response


@route("/favicon.png")
def static_favicon() -> HTTPResponse:
    """Get the favicon file."""
    return static_file("img/favicon.png", root=constants.ASSETS)


@route("/image/<image>")
def static_image(image: str) -> str:
    """Get an image."""
    response = static_file(image, root=constants.IMAGES)
    response.set_header("Cache-Control", "public, max-age=31536000")
    return response


@route("/robots.txt")
def static_robots() -> HTTPResponse:
    """Get the robots.txt file (for search engine crawlers)."""
    return static_file("robots.txt", root=constants.ASSETS)


@route("/thumbnail/<image>")
def static_thumbnail(image: str) -> HTTPResponse:
    """Get a thumbnail."""
    response = static_file(image, root=constants.THUMBNAILS)
    response.set_header("Cache-Control", "public, max-age=31536000")
    return response


application = default_app()
