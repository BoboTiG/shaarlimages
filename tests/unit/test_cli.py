"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from unittest.mock import patch

import pytest

from host.__main__ import main


def test_fix():
    with patch("cli.fix_images_medatadata") as mocker:
        assert main(["fix"]) == 0
        mocker.assert_called_once_with(force=False)


@pytest.mark.parametrize("arg_force", ["--force", "-f"])
def test_fix_forced(arg_force: str):
    with patch("cli.fix_images_medatadata") as mocker:
        assert main(["fix", arg_force]) == 0
        mocker.assert_called_once_with(force=True)


def test_purge():
    with patch("cli.purge") as mocker:
        assert main(["purge", "file.jpg"]) == 0
        mocker.assert_called_once_with({"file.jpg"})


def test_purge_no_file():
    with pytest.raises(SystemExit, match="2"):
        main(["purge"])


def test_sync():
    with patch("helpers.sync_them_all") as mocker:
        assert main(["sync"]) == 0
        mocker.assert_called_once_with(force=False)


@pytest.mark.parametrize("arg_force", ["--force", "-f"])
def test_sync_forced(arg_force: str):
    with patch("helpers.sync_them_all") as mocker:
        assert main(["sync", arg_force]) == 0
        mocker.assert_called_once_with(force=True)


@pytest.mark.parametrize("arg_url", ["--url", "-u"])
def test_sync_specific(arg_url: str):
    url = "https://example.org/links/"
    with patch("helpers.sync_feed") as mocker:
        assert main(["sync", arg_url, url]) == 0
        mocker.assert_called_once_with(url, force=False)


@pytest.mark.parametrize("arg_force", ["--force", "-f"])
@pytest.mark.parametrize("arg_url", ["--url", "-u"])
def test_sync_specific_forced(arg_url: str, arg_force: str):
    url = "https://example.org/links/"
    with patch("helpers.sync_feed") as mocker:
        assert main(["sync", arg_url, url, arg_force]) == 0
        mocker.assert_called_once_with(url, force=True)
