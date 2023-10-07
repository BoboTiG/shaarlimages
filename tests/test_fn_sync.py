"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

import responses

from host import functions, helpers
from host.constants import DATA, IMAGES

from .constants import FEED_URL, FEED_XML, IMAGE_JPG, TEST_IMAGES


@responses.activate
def test_fetch_image(capsys) -> None:
    url = f"https://example.org/{IMAGE_JPG.name}"
    body = IMAGE_JPG.read_bytes()

    responses.add(method="GET", url=url, body=body)
    assert functions.fetch_image(url) == body

    out = capsys.readouterr().out
    assert f">>> ✅ {url}" in out


@responses.activate
def test_fetch_image_not_an_image(capsys) -> None:
    url = f"https://example.org/{IMAGE_JPG.name}"
    body = b"not an image!"

    responses.add(method="GET", url=url, body=body)
    assert functions.fetch_image(url) is None

    out = capsys.readouterr().out
    assert f">>> 📛 {url}" in out


@responses.activate
def test_fetch_image_request_error(capsys) -> None:
    url = f"https://example.org/{IMAGE_JPG.name}"

    responses.add(method="GET", url=url, status=404)
    assert functions.fetch_image(url) is None

    out = capsys.readouterr().out
    assert f">>> ❌ {url}" in out


@responses.activate
def test_fetch_rss() -> None:
    url = "https://example.org/?do=rss"
    body = "<rss><channel><title>Test</title></channel></rss>"

    responses.add(method="GET", url=url, body=body)
    feed = functions.fetch_rss_feed(url)

    assert isinstance(feed, dict)
    assert feed.feed.title == "Test"
    assert not feed.entries


@responses.activate
def test_sync_feed(tmp_path: Path, setup_data):
    # Remove several copied files in conftest.py to cover more code
    for file in (tmp_path / DATA.name / IMAGES.name).glob("*.jpg"):
        file.unlink()

    # XML feed
    responses.add(method="GET", url=FEED_URL, body=FEED_XML)

    # Not an image link
    responses.add(method="GET", url=f"{FEED_URL}/code.txt", body="Le code, c'est le code ?")

    # Image not found
    responses.add(method="GET", url=f"{FEED_URL}/{TEST_IMAGES[0][0].name}", status=404)

    # Image link with invalid image data
    responses.add(method="GET", url=f"{FEED_URL}/{TEST_IMAGES[1][0].name}", body=b"no image")

    # Valid images
    for file, *_ in TEST_IMAGES[2:]:
        responses.add(method="GET", url=f"{FEED_URL}/{file.name}", body=file.read_bytes())

    res = helpers.sync_feed(FEED_URL)
    assert res == {"count": len(TEST_IMAGES) - 2}

    # Force the sync
    helpers.sync_feed(FEED_URL, force=True)

    # Sync them all too
    helpers.sync_them_all()


@responses.activate
def test_sync_feed_error():
    responses.add(method="GET", url=FEED_URL, body=ConnectionError("Boom"))

    assert helpers.sync_feed(FEED_URL) == {"count": -1}
