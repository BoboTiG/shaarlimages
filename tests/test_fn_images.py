"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from host import functions
from host.custom_types import Size

from .constants import IMAGE_JPG, IMAGE_JPG_IS_PNG, IMAGE_PNG, IMAGE_SQUARE


def test_any_css_class_question() -> None:
    assert functions.any_css_class_question() == ""


@freeze_time("1969-06-28")
def test_any_css_class_question_gray_pride() -> None:
    assert functions.any_css_class_question() == "gay-pride"


@pytest.mark.parametrize(
    "file, expected_file_size, expected_size",
    [
        (IMAGE_JPG, 22548, Size(width=400, height=267)),
        (IMAGE_JPG_IS_PNG, 503, Size(width=161, height=81)),
        (IMAGE_PNG, 61283, Size(width=317, height=400)),
        (IMAGE_SQUARE, 21519, Size(width=400, height=400)),
    ],
)
def test_create_thumbnail(file: Path, expected_file_size: int, expected_size: int, tmp_path: Path) -> None:
    dest_file = tmp_path / file.name
    assert not dest_file.is_file()

    with patch("constants.THUMBNAILS", tmp_path):
        assert functions.create_thumbnail(file) == dest_file
        assert dest_file.is_file()
        assert functions.get_size(dest_file) == expected_size
        assert dest_file.stat().st_size == expected_file_size


def test_create_thumbnail_already_exist(tmp_path: Path) -> None:
    dest_file = tmp_path / IMAGE_JPG.name
    assert not dest_file.is_file()
    dest_file.write_bytes(b"")

    with patch("constants.THUMBNAILS", tmp_path):
        assert functions.create_thumbnail(IMAGE_JPG) == dest_file
        assert dest_file.is_file()
        assert dest_file.stat().st_size == 0


@pytest.mark.parametrize(
    "file, color",
    [
        (IMAGE_JPG, "585E50"),
        (IMAGE_JPG_IS_PNG, "323232"),
        (IMAGE_PNG, "B19C95"),
    ],
)
def test_docolav(file: Path, color: str) -> None:
    assert functions.docolav(file) == color


@pytest.mark.parametrize(
    "file, size",
    [
        (IMAGE_JPG, Size(width=2880, height=1920)),
        (IMAGE_JPG_IS_PNG, Size(width=161, height=81)),
        (IMAGE_PNG, Size(width=684, height=864)),
    ],
)
def test_get_size(file: Path, size: Size) -> None:
    assert functions.get_size(file) == size
