"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import constants
import functions
import helpers
import version
from bottle import HTTPResponse, default_app, route, static_file

__version__ = version.__version__
__author__ = "Mickaël Schoentgen"
__copyright__ = """
Copyright (c) 2013-2023, Mickaël 'Tiger-222' Schoentgen

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee or royalty is hereby
granted, provided that the above copyright notice appear in all copies
and that both that copyright notice and this permission notice appear
in supporting documentation or portions thereof, including
modifications, that you make.
"""


@route("/")
def page_home() -> str:
    """Display the primary page."""
    return helpers.render_home_page(1)


@route("/page/<page:int>")
def page_home_pagination(page: int) -> str:
    """Display a pagined page."""
    return helpers.render_home_pagination_page(page)


@route("/zoom/<image>")
def page_zoom(image: str) -> str:
    """Display an image."""
    return helpers.render_zoom_page(image)


@route("/search/<value>")
def search(value: str) -> str:
    """Search for images."""
    return helpers.render_search(functions.lookup(value))


@route("/search/tag/<tag>")
def search_by_tag(tag: str) -> str:
    """Search for images by tag."""
    return helpers.render_search(functions.lookup_tag(tag))


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
