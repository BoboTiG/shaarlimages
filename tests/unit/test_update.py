"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

import responses

from host import constants, functions, helpers
from host.constants import DATA, FEEDS_URL, SHAARLIS


@responses.activate
def test_sync_feeds(tmp_path: Path) -> None:
    file = tmp_path / DATA.name / SHAARLIS.name
    assert not file.is_file()

    body = [
        {
            "id": 1,
            "url": "https://example.shaarli.net/links/?do=rss",
            "link": "https://example.shaarli.net/links/",
            "title": "Liens en vrac de X",
        },
        {
            "id": 2,
            "url": "https://example.shaarli.net/links?do=rss",
            "link": "https://example.shaarli.net/links/duplicate",
            "title": "Liens en vrac de XX",
        },
        {
            "id": 3,
            "url": "",
            "link": "https://example.shaarli.net/links/",
            "title": "Liens en vrac de XXX",
        },
    ]
    resp = responses.add(method="GET", url=FEEDS_URL, json=body)

    feeds = helpers.sync_feeds()
    assert body[0]["url"] in feeds
    assert body[1]["url"] not in feeds
    assert body[2]["url"] not in feeds
    assert len(feeds) == len(constants.MORE_SHAARLIS) + 1
    assert resp.call_count == 1
    assert file.is_file()

    stored_shaarlis = functions.read(file)
    assert stored_shaarlis["feeds"] == feeds
    assert stored_shaarlis["updated"] > 0.0

    # Ensure the cache logic is working
    helpers.sync_feeds()
    assert resp.call_count == 1
