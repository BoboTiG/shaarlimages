"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from unittest.mock import patch

import pytest

from host.__main__ import main


def test_fix():
    with patch("functions.fix_images_medatadata") as mocker:
        assert main(["fix"]) == 0
        mocker.assert_called_once_with(force=False)


def test_fix_forced():
    with patch("functions.fix_images_medatadata") as mocker:
        assert main(["fix", "--force"]) == 0
        mocker.assert_called_once_with(force=True)


def test_purge():
    with patch("functions.purge") as mocker:
        assert main(["purge", "file.jpg"]) == 0
        mocker.assert_called_once_with({"file.jpg"})


def test_purge_no_file():
    with pytest.raises(SystemExit, match="2"):
        main(["purge"])


def test_sync():
    with patch("helpers.sync_them_all") as mocker:
        assert main(["sync"]) == 0
        mocker.assert_called_once_with(force=False)


def test_sync_forced():
    with patch("helpers.sync_them_all") as mocker:
        assert main(["sync", "--force"]) == 0
        mocker.assert_called_once_with(force=True)


def test_sync_specific():
    url = "https://example.org/links/"
    with patch("helpers.sync_feed") as mocker:
        assert main(["sync", "--url", url]) == 0
        mocker.assert_called_once_with(url, force=False)


def test_sync_specific_forced():
    url = "https://example.org/links/"
    with patch("helpers.sync_feed") as mocker:
        assert main(["sync", "--url", url, "--force"]) == 0
        mocker.assert_called_once_with(url, force=True)
