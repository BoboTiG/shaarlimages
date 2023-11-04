"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

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
        (data / IMAGES.name).mkdir(exist_ok=True, parents=True)
        (data / THUMBNAILS.name).mkdir(exist_ok=True)
        yield


@pytest.fixture()
def setup_data(tmp_path: Path):
    # Create the shaarlis.json file
    functions.persist(
        tmp_path / DATA.name / SHAARLIS.name,
        {"feeds": [FEED_URL], "updated": functions.now()},
    )

    # Will copy images there
    images = tmp_path / DATA.name / IMAGES.name
    thumbs = tmp_path / DATA.name / THUMBNAILS.name

    # Create the JSON feed
    feed_key = functions.small_hash(functions.feed_key(FEED_URL))
    data = {}
    for idx, (file, file_size, size, thumb_size, color, checksum) in enumerate(TEST_IMAGES, 1):
        url = f"{FEED_URL}/{file.name}"
        cache_key = functions.small_hash(url)
        stored_file = f"{cache_key}{file.suffix}"
        data[cache_key] = {
            "checksum": functions.checksum(file),
            "date": functions.now(),
            "description": f"Simple description with the '{'nsfw' if idx == 1 else 'robe'}' keyword.",
            "docolav": color,
            "file": stored_file,
            "guid": f"{FEED_URL}/shaare/{idx}",
            "height": size.height,
            "tags": ["sample", "test", "image"] + ["nsfw" if idx % 2 == 1 else "clothes"],
            "title": "Awesome image!",
            "width": size.width,
            "url": url,
        }
        copyfile(file, images / stored_file)
        copyfile(file, thumbs / stored_file)
    functions.persist(tmp_path / DATA.name / FEEDS.name / f"{feed_key}.json", data)
