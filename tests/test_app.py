"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from random import choice

import pytest
from bottle import HTTPResponse

from host import app, custom_types, functions


def random_image() -> custom_types.Metadata:
    image = choice(list(functions.retrieve_all_uniq_metadata()))
    print(f"Chosen {image = }")
    return image


def test_page_home() -> None:
    content = app.page_home()
    assert "Petit voyeur ;)" in content


def test_page_home_pagination() -> None:
    content = app.page_home_pagination(1)
    assert "Petit voyeur ;)" in content


def test_page_home_pagination_lower_than_min() -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_home_pagination(0)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/page/1"


def test_page_home_pagination_higher_than_max() -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_home_pagination(99999999999)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"].startswith("http://127.0.0.1/page/")


def test_page_zoom() -> None:
    image = random_image()
    content = app.page_zoom(image.link)
    assert image.link in content


def test_page_zoom_image_not_found() -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_zoom("foo(does-not-exist)")

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/"


def test_search() -> None:
    response_lowercase = app.search("robe")
    response_uppercase = app.search("ROBE")

    assert "{src:" in response_lowercase
    assert response_lowercase == response_uppercase


def test_search_by_tag() -> None:
    response_lowercase = app.search_by_tag("robe")
    response_uppercase = app.search_by_tag("ROBE")

    assert "{src:" in response_lowercase
    assert response_lowercase == response_uppercase


def test_static_asset() -> None:
    response = app.static_asset("css/app.css")
    assert response.status_code == 200
    assert response.content_type == "text/css; charset=UTF-8"


def test_static_favicon() -> None:
    response = app.static_favicon()
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_static_image() -> None:
    image = random_image()
    response = app.static_image(image.link)
    assert response.status_code == 200
    assert response.content_type.startswith("image/")


def test_static_thumbnail() -> None:
    image = random_image()
    response = app.static_thumbnail(image.link)
    assert response.status_code == 200
    assert response.content_type.startswith("image/")


def test_static_robots() -> None:
    response = app.static_robots()
    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=UTF-8"
