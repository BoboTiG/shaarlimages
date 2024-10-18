"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from mimetypes import guess_type
from pathlib import Path

import pytest
import responses
from _pytest.capture import CaptureFixture

from host import custom_types, functions, helpers
from host.constants import DATA, FEEDS, FEEDS_URL, HASH_LEN, IMAGE_EXT, IMAGES

from .constants import (
    FEED_URL,
    FEED_XML,
    FEED_XML_NO_TIMESTAMPS,
    IMAGE_JPG,
    TEST_IMAGES,
)


@responses.activate
def test_fetch_image(capsys: CaptureFixture) -> None:
    url = f"https://example.org/{IMAGE_JPG.name}"
    body = IMAGE_JPG.read_bytes()

    responses.add(method="GET", url=url, body=body)
    assert functions.fetch_image(url) == body

    out = capsys.readouterr().out
    assert f">>> ✅ {url}" in out


@responses.activate
def test_fetch_image_not_an_image(capsys: CaptureFixture) -> None:
    url = f"https://example.org/{IMAGE_JPG.name}"
    body = b"not an image!"

    responses.add(method="GET", url=url, body=body)
    assert functions.fetch_image(url) is None

    out = capsys.readouterr().out
    assert f">>> 📛 {url}" in out


@responses.activate
def test_fetch_image_request_error(capsys: CaptureFixture) -> None:
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
    assert feed.feed.title == "Test"  # type:ignore[attr-defined]
    assert not feed.entries  # type:ignore[attr-defined]


@responses.activate
@pytest.mark.parametrize("with_timestamps", [True, False])
def test_sync_feed(with_timestamps: bool, tmp_path: Path) -> None:
    feed_data = FEED_XML if with_timestamps else FEED_XML_NO_TIMESTAMPS

    # Remove several copied files in conftest.py to cover more code
    for file in (tmp_path / DATA.name / IMAGES.name).glob("*.jpg"):
        file.unlink()

    # Shaarlis list
    responses.add(method="GET", url=FEEDS_URL, json=[])

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
        print(file.name, guess_type(file)[0])
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

    assert helpers.sync_feed(FEED_URL) == 3
    assert helpers.sync_feed(FEED_URL) == 0

    # Force the sync
    assert helpers.sync_feed(FEED_URL, force=True) == 0

    # Sync them all too
    helpers.sync_them_all()

    # Check downloaded images
    for file in (tmp_path / DATA.name / IMAGES.name).glob("*"):
        assert len(file.stem) == HASH_LEN
        assert file.suffix in IMAGE_EXT

    # Check item metadata
    file = tmp_path / DATA.name / FEEDS.name / f"{functions.small_hash(functions.feed_key(FEED_URL))}.json"
    data = sorted(functions.load_metadata(file), key=lambda meta: meta.url)[-1]
    image = TEST_IMAGES[-1]
    assert data.checksum == image[5]
    assert isinstance(data.date, float)
    assert data.date > 0.0
    assert data.description.startswith("Some description with the 'robe' keyword.")
    assert data.docolav == image[4]
    assert data.file == f'{functions.small_hash(f"{FEED_URL}/{image[0].name}")}{image[0].suffix}'
    assert data.height == image[2].height
    assert data.tags == ["image", "nsfw", "sample", "test"]
    assert data.title == f"Image - {image[0].name}"
    assert data.url == f"{FEED_URL}/{image[0].name}"
    assert data.width == image[2].width


@responses.activate
def test_sync_feed_error() -> None:
    responses.add(method="GET", url=FEED_URL, body=ConnectionError("Boom"))

    assert helpers.sync_feed(FEED_URL) == -1


@responses.activate
def test_try_wayback_machine_get() -> None:
    url_img = "https://web.archive.org/web/20060101064348/http://www.example.com/f.png"
    url_final = "https://web.archive.org/web/20060101064348if_/http://www.example.com/f.png"
    data = {
        "archived_snapshots": {
            "closest": {"available": True, "url": url_img, "timestamp": "20060101064348", "status": "200"}
        }
    }
    responses.add(method="GET", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"https://archive.org/wayback/available?url={FEED_URL}", json=data)
    responses.add(method="GET", url=url_final, body=b"ok")

    response = functions.fetch(FEED_URL)
    assert response.url == url_final
    assert response.content == b"ok"


@responses.activate
def test_try_wayback_machine_head() -> None:
    url_img = "https://web.archive.org/web/20060101064348/http://www.example.com/f.png"
    url_final = "https://web.archive.org/web/20060101064348if_/http://www.example.com/f.png"
    data = {
        "archived_snapshots": {
            "closest": {"available": True, "url": url_img, "timestamp": "20060101064348", "status": "200"}
        }
    }
    responses.add(method="HEAD", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"https://archive.org/wayback/available?url={FEED_URL}", json=data)
    responses.add(method="HEAD", url=url_final, content_type="image/png")

    assert functions.fetch_image_type(FEED_URL) == ".png"

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert waybackdata.content_type == "image/png"
    assert not waybackdata.is_lost
    assert waybackdata.snapshot


@responses.activate
def test_try_wayback_machine_head_cache() -> None:
    url_final = "https://web.archive.org/web/20060101064348if_/http://www.example.com/f.png"

    waybackdata = custom_types.Waybackdata(content_type="image/png", snapshot=url_final)
    functions.set_wayback_back_data(FEED_URL, waybackdata)

    response = functions.try_wayback_machine(FEED_URL, "head")
    assert response.headers == {"Content-Type": "image/png"}

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert waybackdata.content_type == "image/png"
    assert not waybackdata.is_lost
    assert waybackdata.snapshot


@responses.activate
def test_try_wayback_machine_cache() -> None:
    url_final = "https://web.archive.org/web/20060101064348if_/http://www.example.com/f.png"
    responses.add(method="HEAD", url=FEED_URL, status=404)
    responses.add(method="HEAD", url=url_final, content_type="image/png")

    waybackdata = custom_types.Waybackdata(snapshot=url_final)
    functions.set_wayback_back_data(FEED_URL, waybackdata)

    assert functions.fetch_image_type(FEED_URL) == ".png"

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert waybackdata.content_type == "image/png"
    assert not waybackdata.is_lost
    assert waybackdata.snapshot


@responses.activate
def test_try_wayback_machine_head_is_lost() -> None:
    url_img = "https://web.archive.org/web/20060101064348/http://www.example.com/f.png"
    url_final = "https://web.archive.org/web/20060101064348if_/http://www.example.com/f.png"
    data: dict[str, dict] = {
        "archived_snapshots": {
            "closest": {"available": True, "url": url_img, "timestamp": "20060101064348", "status": "200"}
        }
    }

    responses.add(method="HEAD", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"https://archive.org/wayback/available?url={FEED_URL}", json=data)
    responses.add(method="HEAD", url=url_final, content_type=None)

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert not waybackdata.content_type
    assert not waybackdata.is_lost
    assert not waybackdata.snapshot

    with pytest.raises(functions.EvanescoError) as exc:
        functions.try_wayback_machine(FEED_URL, "head")

    assert str(exc.value) == "Cannot found the resource on internet anymore."

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert not waybackdata.content_type
    assert waybackdata.is_lost
    assert waybackdata.snapshot


@responses.activate
def test_try_wayback_machine_get_is_lost() -> None:
    data: dict[str, dict] = {"archived_snapshots": {}}
    responses.add(method="GET", url=FEED_URL, status=404)
    responses.add(method="GET", url=f"https://archive.org/wayback/available?url={FEED_URL}", json=data)

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert not waybackdata.content_type
    assert not waybackdata.is_lost
    assert not waybackdata.snapshot

    with pytest.raises(functions.EvanescoError) as exc:
        functions.fetch(FEED_URL)

    assert str(exc.value) == "Cannot found the resource on internet anymore."

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert not waybackdata.content_type
    assert waybackdata.is_lost
    assert not waybackdata.snapshot


@responses.activate
def test_try_wayback_machine_resource_is_lost() -> None:
    waybackdata = custom_types.Waybackdata(is_lost=True)
    functions.set_wayback_back_data(FEED_URL, waybackdata)

    waybackdata = functions.load_wayback_back_data(FEED_URL)
    assert not waybackdata.content_type
    assert waybackdata.is_lost
    assert not waybackdata.snapshot

    with pytest.raises(functions.EvanescoError) as exc:
        functions.try_wayback_machine(FEED_URL, "get")

    assert str(exc.value) == "Cannot found the resource on internet anymore."
