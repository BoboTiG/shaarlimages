"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from unittest.mock import patch

import pytest

from host.__main__ import main


def test_fix() -> None:
    with patch("cli.fix_images_medatadata") as mocker:
        assert main(["fix"]) == 0
        mocker.assert_called_once_with()


def test_purge() -> None:
    with patch("cli.purge") as mocker:
        assert main(["purge", "file.jpg"]) == 0
        mocker.assert_called_once_with({"file.jpg"})


def test_purge_no_file() -> None:
    with pytest.raises(SystemExit, match="2"):
        main(["purge"])


def test_sync() -> None:
    with patch("helpers.sync_them_all") as mocker:
        assert main(["sync"]) == 0
        mocker.assert_called_once_with(force=False)


@pytest.mark.parametrize("arg_force", ["--force", "-f"])
def test_sync_forced(arg_force: str) -> None:
    with patch("helpers.sync_them_all") as mocker:
        assert main(["sync", arg_force]) == 0
        mocker.assert_called_once_with(force=True)


@pytest.mark.parametrize("arg_url", ["--url", "-u"])
def test_sync_specific(arg_url: str) -> None:
    url = "https://example.org/links/"
    with patch("helpers.sync_feed") as mocker:
        assert main(["sync", arg_url, url]) == 0
        mocker.assert_called_once_with(url, force=False)


@pytest.mark.parametrize("arg_force", ["--force", "-f"])
@pytest.mark.parametrize("arg_url", ["--url", "-u"])
def test_sync_specific_forced(arg_url: str, arg_force: str) -> None:
    url = "https://example.org/links/"
    with patch("helpers.sync_feed") as mocker:
        assert main(["sync", arg_url, url, arg_force]) == 0
        mocker.assert_called_once_with(url, force=True)
