"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import pytest
import responses

from host import solvers


def test_guess_url() -> None:
    url = "https://example.org/favicon.png"
    assert solvers.guess_url(url) == url


@responses.activate
@pytest.mark.parametrize(
    "url",
    [
        "https://commons.wikimedia.org/wiki/File:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        "https://commons.wikimedia.org/wiki/Gustave_Dor%C3%A9#/media/File:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        "https://secure.wikimedia.org/wikipedia/fr/wiki/Fichier:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        "https://fr.wikipedia.org/wiki/Fichier:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
    ],
)
def test_guess_url_wikimedia_wikipedia(url: str) -> None:
    url_files = "https://api.wikimedia.org/core/v1/commons/file/File:Chess_Single_Image_Stereogram_by_3Dimka.jpg"
    body = {
        "title": "Chess Single Image Stereogram by 3Dimka.jpg",
        "file_description_url": "//commons.wikimedia.org/wiki/File:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        "latest": {"timestamp": "2010-05-23T04:21:07Z", "user": {"id": 64713, "name": "3Dimka~commonswiki"}},
        "preferred": {
            "mediatype": "BITMAP",
            "size": 202859,
            "width": 800,
            "height": 600,
            "duration": None,
            "url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        },
        "original": {
            "mediatype": "BITMAP",
            "size": 202859,
            "width": 800,
            "height": 600,
            "duration": None,
            "url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        },
        "thumbnail": {
            "mediatype": "BITMAP",
            "size": 202859,
            "width": 800,
            "height": 600,
            "duration": None,
            "url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Chess_Single_Image_Stereogram_by_3Dimka.jpg",
        },
    }

    responses.add(method="GET", url=url_files, json=body)
    assert solvers.guess_url(url) == body["original"]["url"]


@responses.activate
def test_guess_url_wikimedia_wikipedia_not_found() -> None:
    url = "https://en.wikipedia.org/wiki/File:CE_marks.jpg"
    url_files = "https://api.wikimedia.org/core/v1/commons/file/File:CE_marks.jpg"
    body = {
        "errorKey": "rest-nonexistent-title",
        "messageTranslations": {"en": "The specified title (File:CE_marks.jpg) does not exist"},
        "httpCode": 404,
        "httpReason": "Not Found",
    }

    responses.add(method="GET", url=url_files, json=body)
    assert solvers.guess_url(url) == url
