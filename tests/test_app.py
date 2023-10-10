"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from random import choice

import pytest
from bottle import HTTPResponse

from host import app, functions


def test_page_home(setup_data) -> None:
    content = app.page_home()
    assert "Petit voyeur ;)" in content


def test_page_home_pagination(setup_data) -> None:
    content = app.page_home_pagination(1)
    assert "Petit voyeur ;)" in content


def test_page_home_pagination_lower_than_min(setup_data) -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_home_pagination(0)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/page/1"


def test_page_home_pagination_higher_than_max(setup_data) -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_home_pagination(99999999999)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"].startswith("http://127.0.0.1/page/")


def test_page_random(setup_data) -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_random()

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"].startswith("http://127.0.0.1/zoom/")


def test_page_zoom(setup_data) -> None:
    image = choice(list(functions.retrieve_all_uniq_metadata()))
    content = app.page_zoom(image.link)
    assert image.link in content


def test_page_zoom_image_not_found() -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_zoom("foo(does-not-exist)")

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/"


def test_search(setup_data) -> None:
    response_lowercase = app.search("robe")
    response_uppercase = app.search("ROBE")

    assert "{src:" in response_lowercase
    assert response_lowercase == response_uppercase


def test_search_by_tag(setup_data) -> None:
    response_lowercase = app.search_by_tag("sample")
    response_uppercase = app.search_by_tag("SAMPLE")

    assert "{src:" in response_lowercase
    assert response_lowercase == response_uppercase


def test_static_asset() -> None:
    response = app.static_asset("css/app.css")
    response.body.close()
    assert response.status_code == 200
    assert response.content_type == "text/css; charset=UTF-8"


def test_static_favicon() -> None:
    response = app.static_favicon()
    response.body.close()
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_static_image(setup_data) -> None:
    image = choice(list(functions.retrieve_all_uniq_metadata()))
    response = app.static_image(image.link)
    response.body.close()
    assert response.status_code == 200
    assert response.content_type.startswith("image/")


def test_static_thumbnail(setup_data) -> None:
    image = choice(list(functions.retrieve_all_uniq_metadata()))
    response = app.static_thumbnail(image.link)
    response.body.close()
    assert response.status_code == 200
    assert response.content_type.startswith("image/")


def test_static_robots() -> None:
    response = app.static_robots()
    response.body.close()
    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=UTF-8"
