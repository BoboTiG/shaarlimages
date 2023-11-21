"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

import responses

from host import functions, helpers
from host.constants import DATA, FEEDS_URL, SHAARLIS


@responses.activate
def test_sync_feeds(tmp_path: Path) -> None:
    file = tmp_path / DATA.name / SHAARLIS.name
    assert not file.is_file()

    body = ["https://example.shaarli.net/links?do=rss"]
    resp = responses.add(method="GET", url=FEEDS_URL, json=body)

    feeds = helpers.sync_feeds()
    assert body[0] in feeds
    assert len(feeds) == 1
    assert resp.call_count == 1
    assert file.is_file()

    stored_shaarlis = functions.read(file)
    assert stored_shaarlis["feeds"] == feeds
    assert stored_shaarlis["updated"] > 0.0

    # Ensure the cache logic is working
    helpers.sync_feeds()
    assert resp.call_count == 1
