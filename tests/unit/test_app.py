"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from random import choice

import feedparser
import pytest
from _pytest.fixtures import FixtureFunction
from boddle import boddle
from bottle import HTTPResponse

from host import app, functions
from host.constants import HASH_LEN


def test_cache_invalidation(setup_data: FixtureFunction) -> None:
    content = app.page_home_pagination(1)
    assert "Cached:" not in content

    content = app.page_home_pagination(1)
    assert "Cached:" in content

    functions.invalidate_caches()
    content = app.page_home_pagination(1)
    assert "Cached:" not in content


def test_page_home_is_redirection() -> None:
    with boddle(params={}), pytest.raises(HTTPResponse) as exc:
        app.page_home()

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/page/1"


def test_page_home_is_redirection_backward_compatibility(setup_data: FixtureFunction) -> None:
    image = choice(functions.retrieve_all_uniq_metadata())
    file = Path(image.file)

    with boddle(params={"i": file.stem}), pytest.raises(HTTPResponse) as exc:
        app.page_home()

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == f"http://127.0.0.1/zoom/{file.stem}"


def test_page_home_pagination(setup_data: FixtureFunction) -> None:
    content = app.page_home_pagination(1)
    assert "Ouh !" in content

    # Ensure the cache is working
    assert "Cached:" not in content
    content = app.page_home_pagination(1)
    assert "Cached:" in content


def test_page_home_pagination_lower_than_min() -> None:
    with boddle(path="/page/0"), pytest.raises(HTTPResponse) as exc:
        app.page_home_pagination(0)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/page/1"


def test_page_home_pagination_higher_than_max() -> None:
    with boddle(path="/page/99999999999"), pytest.raises(HTTPResponse) as exc:
        app.page_home_pagination(99999999999)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/page/1"


def test_page_random(setup_data: FixtureFunction) -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_random()

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"].startswith("http://127.0.0.1/zoom/")

    key = response.headers["Location"].split("/")[-1]
    assert len(key) == HASH_LEN


def test_page_zoom(setup_data: FixtureFunction) -> None:
    image = choice(functions.retrieve_all_uniq_metadata())
    content = app.page_zoom(image.file)
    assert image.file in content


def test_page_zoom_image_not_found() -> None:
    with pytest.raises(HTTPResponse) as exc:
        app.page_zoom("foo(does-not-exist)")

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/"


def test_rss(setup_data: FixtureFunction) -> None:
    feed1 = app.rss()
    feed2 = app.rss()

    # Check it loads properly, extended tests can be found in a specific test file
    parsed1 = feedparser.parse(feed1)
    parsed2 = feedparser.parse(feed2)
    assert len(parsed1.entries) == 4
    assert len(parsed2.entries) == 4

    # Ensure the cache is working too
    assert "Cached:" not in feed1
    assert "Cached:" in feed2


def test_rss_all(setup_data: FixtureFunction) -> None:
    feed = app.rss_all()

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 4


def test_rss_with_custom_items_count(setup_data: FixtureFunction) -> None:
    feed = app.rss_with_custom_items_count(2)

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 2


def test_rss_search_by_term(setup_data: FixtureFunction) -> None:
    feed = app.rss_search_by_term("robe")

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 3


def test_rss_search_by_term_all(setup_data: FixtureFunction) -> None:
    feed = app.rss_search_by_term_all("robe")

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 3


def test_rss_search_by_term_with_custom_items_count(setup_data: FixtureFunction) -> None:
    feed = app.rss_search_by_term_with_custom_items_count("robe", 3)

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 3


def test_rss_search_by_tag(setup_data: FixtureFunction) -> None:
    feed = app.rss_search_by_tag("nsfw")

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 2


def test_rss_search_by_tag_all(setup_data: FixtureFunction) -> None:
    feed = app.rss_search_by_tag_all("nsfw")

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 2


def test_rss_search_by_tag_with_custom_items_count(setup_data: FixtureFunction) -> None:
    feed = app.rss_search_by_tag_with_custom_items_count("nsfw", 1)

    parsed = feedparser.parse(feed)
    assert len(parsed.entries) == 1


def test_search_first_page_is_redirection() -> None:
    with boddle(path="/search/robe"), pytest.raises(HTTPResponse) as exc:
        app.search("robe")

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/search/robe/1"


def test_search_case_insensitive(setup_data: FixtureFunction) -> None:
    response_lowercase = app.search_pagination("robe", 1)
    response_uppercase = app.search_pagination("ROBE", 1)

    assert "{src:" in response_lowercase
    assert response_uppercase.startswith(response_lowercase)

    # Ensure the cache is working
    assert "Cached:" not in response_lowercase
    assert "Cached:" in response_uppercase


def test_search_pagination_lower_than_min() -> None:
    with boddle(path="/search/robe/0"), pytest.raises(HTTPResponse) as exc:
        app.search_pagination("robe", 0)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/search/robe/1"


def test_search_pagination_higher_than_max() -> None:
    with boddle(path="/search/robe/99999999999"), pytest.raises(HTTPResponse) as exc:
        app.search_pagination("robe", 99999999999)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/search/robe/1"


def test_search_by_tag_first_page_is_redirection() -> None:
    with boddle(path="/tag/sample"), pytest.raises(HTTPResponse) as exc:
        app.search_by_tag("sample")

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/tag/sample/1"


def test_search_by_tag_case_insensitive(setup_data: FixtureFunction) -> None:
    response_lowercase = app.search_by_tag_pagination("sample", 1)
    response_uppercase = app.search_by_tag_pagination("SAMPLE", 1)

    assert "{src:" in response_lowercase
    assert response_uppercase.startswith(response_lowercase)

    # Ensure the cache is working
    assert "Cached:" not in response_lowercase
    assert "Cached:" in response_uppercase


def test_search_by_tag_pagination_lower_than_min() -> None:
    with boddle(path="/tag/sample/0"), pytest.raises(HTTPResponse) as exc:
        app.search_by_tag_pagination("sample", 0)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/tag/sample/1"


def test_search_by_tag_pagination_higher_than_max() -> None:
    with boddle(path="/tag/sample/99999999999"), pytest.raises(HTTPResponse) as exc:
        app.search_by_tag_pagination("sample", 99999999999)

    response = exc.value
    assert response.status_code == 302
    assert response.headers["Location"] == "http://127.0.0.1/tag/sample/1"


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


def test_static_image(setup_data: FixtureFunction) -> None:
    image = choice(functions.retrieve_all_uniq_metadata())
    assert image
    response = app.static_image(image.file)
    response.body.close()
    assert response.status_code == 200
    assert response.content_type.startswith("image/")


def test_static_thumbnail(setup_data: FixtureFunction) -> None:
    image = choice(functions.retrieve_all_uniq_metadata())
    response = app.static_thumbnail(image.file)
    response.body.close()
    assert response.status_code == 200
    assert response.content_type.startswith("image/")


def test_static_robots() -> None:
    response = app.static_robots()
    response.body.close()
    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=UTF-8"
