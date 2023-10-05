"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from unittest.mock import patch

import responses

from host import config, constants, functions, helpers


@responses.activate
def test_sync_feeds(tmp_path: Path) -> None:
    file = tmp_path / constants.SHAARLIS.name
    assert not file.is_file()

    body = [
        {
            "id": 1,
            "url": "https://sebsauvage.net/links/?do=rss",
            "link": "https://sebsauvage.net/links/",
            "title": "Liens en vrac de sebsauvage",
        },
        {
            "id": 2,
            "url": "https://sebsauvage.net/links/?do=rss",
            "link": "https://sebsauvage.net/links/duplicate",
            "title": "Liens en vrac de sebsauvage #2",
        },
    ]
    resp = responses.add(method="GET", url=config.SYNC["url"], json=body)

    with patch("constants.SHAARLIS", file):
        helpers.sync_feeds()

    assert resp.call_count == 1

    stored_shaarlis = functions.read(file)
    assert stored_shaarlis["feeds"] == [body[0]["url"]]
    assert stored_shaarlis["updated"] > 0.0


@responses.activate
def test_sync_feeds_cache(tmp_path: Path) -> None:
    file = tmp_path / constants.SHAARLIS.name
    assert not file.is_file()

    functions.persist(
        file,
        {
            "feeds": ["https://sebsauvage.net/links/"],
            "updated": functions.now(),
        },
    )

    resp = responses.add(method="GET", url=config.SYNC["url"], json={})

    with patch("host.constants.SHAARLIS", file):
        helpers.sync_feeds()

    assert resp.call_count == 0
