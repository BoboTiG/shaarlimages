"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

import responses

from host import functions, helpers
from host.constants import DATA, FEEDS_URL, SHAARLIS


@responses.activate
def test_sync_feeds(tmp_path: Path, setup_data_folders) -> None:
    file = tmp_path / DATA.name / SHAARLIS.name
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
    resp = responses.add(method="GET", url=FEEDS_URL, json=body)

    helpers.sync_feeds()
    assert resp.call_count == 1
    assert file.is_file()

    stored_shaarlis = functions.read(file)
    assert stored_shaarlis["feeds"] == [body[0]["url"]]
    assert stored_shaarlis["updated"] > 0.0

    # Ensure the cache logic is working
    helpers.sync_feeds()
    assert resp.call_count == 1
