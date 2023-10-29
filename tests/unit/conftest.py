"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from email.utils import formatdate
from pathlib import Path
from shutil import copyfile
from unittest.mock import patch

import pytest

from host import functions
from host.constants import (
    CACHE,
    DATA,
    FEEDS,
    IMAGES,
    SHAARLIS,
    THUMBNAILS,
    WAYBACK_MACHINE,
)

from .constants import FEED_URL, TEST_IMAGES


@pytest.fixture(autouse=True)
def setup_data_folders(tmp_path: Path) -> None:
    data = tmp_path / DATA.name

    with (
        patch("constants.CACHE", data / CACHE.name),
        patch("constants.DATA", data),
        patch("constants.FEEDS", data / FEEDS.name),
        patch("constants.IMAGES", data / IMAGES.name),
        patch("constants.SHAARLIS", data / SHAARLIS.name),
        patch("constants.THUMBNAILS", data / THUMBNAILS.name),
        patch("constants.WAYBACK_MACHINE", data / WAYBACK_MACHINE.name),
    ):
        yield


@pytest.fixture()
def setup_data(tmp_path: Path):
    # Create the shaarlis.json file
    functions.persist(
        tmp_path / DATA.name / SHAARLIS.name,
        {"feeds": [FEED_URL], "updated": functions.now()},
    )

    # Create the JSON feed
    feed_key = functions.small_hash(functions.feed_key(FEED_URL))
    functions.persist(
        tmp_path / DATA.name / FEEDS.name / f"{feed_key}.json",
        {
            str(idx): {
                "checksum": functions.checksum(file),
                "date": formatdate(usegmt=True),
                "desc": "Simple description with the 'robe' keyword.",
                "docolav": color,
                "guid": f"{FEED_URL}/shaare/{idx}",
                "height": size.height,
                "link": file.name,
                "tags": ["sample", "test", "image"],
                "title": "Awesome image!",
                "width": size.width,
                "url": f"{FEED_URL}/original/{idx}",
            }
            for idx, (file, _, size, color, *__) in enumerate(TEST_IMAGES, 1)
        },
    )

    # Copy images
    images = tmp_path / DATA.name / IMAGES.name
    thumbs = tmp_path / DATA.name / THUMBNAILS.name
    images.mkdir(parents=True)
    thumbs.mkdir()
    for file, *_ in TEST_IMAGES:
        copyfile(file, images / file.name)
        copyfile(file, thumbs / file.name)
