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

from .constants import IMAGE_JPG, TEST_IMAGES


def test_any_css_class_question() -> None:
    assert functions.any_css_class_question() == ""


@freeze_time("1969-06-28")
def test_any_css_class_question_gray_pride() -> None:
    assert functions.any_css_class_question() == "gay-pride"


@pytest.mark.parametrize("file, file_size, size, thumb_size, color, checksum, mimetype", TEST_IMAGES)
def test_checksum(
    file: Path,
    file_size: int,
    size: Size,
    thumb_size: Size,
    color: str,
    checksum: str,
    mimetype: str,
    tmp_path: Path,
) -> None:
    assert functions.checksum(file) == checksum


@pytest.mark.parametrize("file, file_size, size, thumb_size, color, checksum, mimetype", TEST_IMAGES)
def test_create_thumbnail(
    file: Path,
    file_size: int,
    size: Size,
    thumb_size: Size,
    color: str,
    checksum: str,
    mimetype: str,
    tmp_path: Path,
) -> None:
    dest_file = tmp_path / file.name
    assert not dest_file.is_file()

    with patch("constants.THUMBNAILS", tmp_path):
        assert functions.create_thumbnail(file) == dest_file
        assert dest_file.is_file()
        assert functions.get_size(dest_file) == thumb_size
        assert dest_file.stat().st_size == file_size


def test_create_thumbnail_already_exist(tmp_path: Path) -> None:
    dest_file = tmp_path / IMAGE_JPG.name
    assert not dest_file.is_file()
    dest_file.write_bytes(b"")

    with patch("constants.THUMBNAILS", tmp_path):
        assert functions.create_thumbnail(IMAGE_JPG) == dest_file
        assert dest_file.is_file()
        assert dest_file.stat().st_size == 0


@pytest.mark.parametrize("file, file_size, size, thumb_size, color, checksum, mimetype", TEST_IMAGES)
def test_docolav(
    file: Path,
    file_size: int,
    size: Size,
    thumb_size: Size,
    color: str,
    checksum: str,
    mimetype: str,
) -> None:
    assert functions.docolav(file) == color


@pytest.mark.parametrize("file, file_size, size, thumb_size, color, checksum, mimetype", TEST_IMAGES)
def test_get_size(
    file: Path,
    file_size: int,
    size: Size,
    thumb_size: Size,
    color: str,
    checksum: str,
    mimetype: str,
) -> None:
    assert functions.get_size(file) == size
