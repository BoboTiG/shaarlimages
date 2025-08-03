"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

from host.constants import (
    CACHE,
    DATA,
    FEEDS,
    IMAGES,
    SHAARLIS,
    THUMBNAILS,
    WAYBACK_MACHINE,
)


@pytest.fixture(autouse=True)
def setup_data_folders(tmp_path: Path) -> Generator:
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
