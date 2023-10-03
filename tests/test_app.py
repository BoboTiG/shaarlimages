"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from host import app


def test_page_home() -> None:
    content = app.page_home()
    assert "Petit voyeur ;)" in content


def test_static_asset() -> None:
    response = app.static_asset("css/app.css")
    assert response.status_code == 200
    assert response.content_type == "text/css; charset=UTF-8"


def test_static_favicon() -> None:
    response = app.static_favicon()
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_static_robots() -> None:
    response = app.static_robots()
    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=UTF-8"
