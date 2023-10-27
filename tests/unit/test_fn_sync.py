"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from mimetypes import guess_type
from pathlib import Path

import pytest
import responses

from host import functions, helpers
from host.constants import DATA, IMAGES
from host.exceptions import DisparoisseError

from .constants import (
    FEED_URL,
    FEED_XML,
    FEED_XML_NO_TIMESTAMPS,
    IMAGE_JPG,
    TEST_IMAGES,
)


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
@pytest.mark.parametrize(
    "content_type, ext",
    [
        # Ignored
        ("application/xml", ""),
        ("image/gif", ""),
        ("image/apng", ""),
        # Supported
        ("image/JPEG", ".jpg"),
        ("image/jpeg", ".jpg"),
        ('image/jpeg;name="BzQGBMDC;MAEnGGO.jpg:large.jpeg"', ".jpg"),
        ("image/jpg", ".jpg"),
        ("image/png", ".png"),
        ('image/png;name="votation.PNG"', ".png"),
        # Unhandled
        ("image/xyz", ""),
    ],
)
def test_fetch_image_type(content_type: str, ext: str) -> None:
    url = "https://example.org/image"
    responses.add(method="HEAD", url=url, content_type=content_type)
    assert functions.fetch_image_type(url) == ext


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
@pytest.mark.parametrize("feed_data", [FEED_XML, FEED_XML_NO_TIMESTAMPS])
def test_sync_feed(feed_data: str, tmp_path: Path, setup_data):
    # Remove several copied files in conftest.py to cover more code
    for file in (tmp_path / DATA.name / IMAGES.name).glob("*.jpg"):
        file.unlink()

    # XML feed
    responses.add(method="GET", url=FEED_URL, body=feed_data)

    # Image not found
    responses.add(
        method="HEAD",
        url=f"{FEED_URL}/{TEST_IMAGES[0][0].name}",
        content_type=guess_type(TEST_IMAGES[0][0].name)[0],
    )
    responses.add(
        method="GET",
        url=f"{FEED_URL}/{TEST_IMAGES[0][0].name}",
        status=404,
    )

    # Image link with invalid image data
    responses.add(
        method="HEAD",
        url=f"{FEED_URL}/{TEST_IMAGES[1][0].name}",
        content_type=guess_type(TEST_IMAGES[1][0].name)[0],
    )
    responses.add(
        method="GET",
        url=f"{FEED_URL}/{TEST_IMAGES[1][0].name}",
        body=b"no image",
    )

    # Not an image link but actual image data
    responses.add(
        method="HEAD",
        url="https://qph.cf2.quoracdn.net/main-qimg-ok",
        content_type="image/jpeg",
    )
    responses.add(
        method="GET",
        url="https://qph.cf2.quoracdn.net/main-qimg-ok",
        body=TEST_IMAGES[1][0].read_bytes(),
    )

    # Not an image link and not image data
    responses.add(
        method="HEAD",
        url="https://qph.cf2.quoracdn.net/main-qimg-bad",
        content_type="application/xml",
    )

    # Not an image link and website is down
    responses.add(
        method="HEAD",
        url="https://qph.cf2.quoracdn.net/main-qimg-down",
        status=500,
    )
    responses.add(
        method="GET",
        url="http://archive.org/wayback/available?url=https://qph.cf2.quoracdn.net/main-qimg-down",
        json={"archived_snapshots": {}},
    )

    # Valid images
    for file, *_ in TEST_IMAGES[2:]:
        responses.add(
            method="HEAD",
            url=f"{FEED_URL}/{file.name}",
            content_type=guess_type(file)[0],
        )
        responses.add(
            method="GET",
            url=f"{FEED_URL}/{file.name}",
            body=file.read_bytes(),
        )

    assert helpers.sync_feed(FEED_URL) == 4
    assert helpers.sync_feed(FEED_URL) == 0

    # Force the sync
    assert helpers.sync_feed(FEED_URL, force=True) == 0

    # Sync them all too
    helpers.sync_them_all()


@responses.activate
def test_sync_feed_error():
    responses.add(method="GET", url=FEED_URL, body=ConnectionError("Boom"))

    assert helpers.sync_feed(FEED_URL) == -1


@responses.activate
def test_try_wayback_machine_get():
    url_img = "http://web.archive.org/web/20060101064348/http://www.example.com:80/f.png"
    data = {
        "archived_snapshots": {
            "closest": {"available": True, "url": url_img, "timestamp": "20060101064348", "status": "200"}
        }
    }
    responses.add(method="GET", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"http://archive.org/wayback/available?url={FEED_URL}", json=data)
    responses.add(method="GET", url=url_img, body=b"ok")

    response = functions.fetch(FEED_URL)
    assert response.url == url_img
    assert response.content == b"ok"


@responses.activate
def test_try_wayback_machine_head():
    url_img = "http://web.archive.org/web/20060101064348/http://www.example.com:80/f.png"
    data = {
        "archived_snapshots": {
            "closest": {"available": True, "url": url_img, "timestamp": "20060101064348", "status": "200"}
        }
    }
    responses.add(method="HEAD", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"http://archive.org/wayback/available?url={FEED_URL}", json=data)
    responses.add(method="HEAD", url=url_img, content_type="image/png")

    assert functions.fetch_image_type(FEED_URL) == ".png"


@responses.activate
def test_try_wayback_machine_not_found():
    data = {"archived_snapshots": {}}
    responses.add(method="GET", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"http://archive.org/wayback/available?url={FEED_URL}", json=data)

    with pytest.raises(DisparoisseError) as exc:
        functions.fetch(FEED_URL)

    assert str(exc.value) == "Cannot found the resource on internet anymore."
