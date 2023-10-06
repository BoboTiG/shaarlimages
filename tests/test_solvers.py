"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from time import strptime

import pytest
import responses

from host import solvers

DATE = strptime("2011-09-04 00:00:00", "%Y-%m-%d %H:%M:%S")


@responses.activate
@pytest.mark.parametrize("scheme", ["http", "https"])
@pytest.mark.parametrize(
    "rest",
    [
        "apod.nasa.gov/apod",
        "apod.nasa.gov/apod/",
        "apod.nasa.gov/apod/astropix.html",
        "apod.nasa.gov/apod/ap110904.html",
        "antwrp.gsfc.nasa.gov/apod/ap110904.html",
    ],
)
def test_nasa_apod(scheme: str, rest: str) -> None:
    url = f"{scheme}://{rest}"
    url_page = "https://apod.nasa.gov/apod/ap110904.html"
    body = """
<center>
<h1> Astronomy Picture of the Day </h1>
<p>

<a href="archivepix.html">Discover the cosmos!</a>
Each day a different image or photograph of our fascinating universe is
featured, along with a brief explanation written by a professional astronomer.
<p>

2011 September 4
<br>
<a href="image/0901/newrings_cassini_big.jpg">
<IMG SRC="image/0901/newrings_cassini.jpg"
alt="See Explanation.  Clicking on the picture will download
 the highest resolution version available."></a>
</center>
"""

    responses.add(method="GET", url=url_page, body=body)
    assert solvers.guess_url(url, DATE) == "https://apod.nasa.gov/apod/image/0901/newrings_cassini_big.jpg"


@responses.activate
def test_nasa_apod_invalid_response() -> None:
    url = "https://apod.nasa.gov/apod/ap110904.html"
    body = """
<center>
<h1> Astronomy Picture of the Day </h1>
<p>

<a href="archivepix.html">Discover the cosmos!</a>
Each day a different image or photograph of our fascinating universe is
featured, along with a brief explanation written by a professional astronomer.
<p>
"""

    responses.add(method="GET", url=url, body=body)
    assert solvers.guess_url(url, DATE) == ""


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
def test_wikimedia(url: str) -> None:
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
    assert solvers.guess_url(url, None) == body["original"]["url"]


@responses.activate
def test_wikimedia_not_found() -> None:
    url = "https://en.wikipedia.org/wiki/File:CE_marks.jpg"
    url_files = "https://api.wikimedia.org/core/v1/commons/file/File:CE_marks.jpg"
    body = {
        "errorKey": "rest-nonexistent-title",
        "messageTranslations": {"en": "The specified title (File:CE_marks.jpg) does not exist"},
        "httpCode": 404,
        "httpReason": "Not Found",
    }

    responses.add(method="GET", url=url_files, json=body)
    assert solvers.guess_url(url, None) == ""
