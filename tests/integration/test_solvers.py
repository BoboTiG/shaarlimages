"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

import pytest

from host import functions, solvers


@pytest.mark.parametrize(
    "solver, url, checksum",
    [
        (
            "cheeseburger",
            "https://i.chzbgr.com/maxW500/7579559168/hFBFD2016/",
            "b303c658fe124f27a60c161ea021e1fc",
        ),
        (
            "developpez",
            "https://www.developpez.net/forums/attachments/p627433d1/a/a/a",
            "9e33f526d924caee437e9705e887a31d",
        ),
        (
            "imgur",
            "https://i.imgur.com/qypAs0A_d.jpg",
            "bca5dcf37292b684035984ff69f5ecb8",
        ),
        (
            "nasa_apod",
            "https://apod.nasa.gov/apod/ap110904.html",
            "fff00e95a3b1ce41c8860287c82a0410",
        ),
        (
            "nasa_apod",
            "https://antwrp.gsfc.nasa.gov/apod/ap110904.html",
            "fff00e95a3b1ce41c8860287c82a0410",
        ),
        (
            "nasa_jpl",
            "https://photojournal.jpl.nasa.gov/catalog/PIA25440",
            "2b607715100fcfb9cbff305a3b84d1e9",
        ),
        (
            "nasa_jpl",
            "https://photojournal.jpl.nasa.gov/jpeg/PIA25440.jpg",
            "2b607715100fcfb9cbff305a3b84d1e9",
        ),
        (
            "quora",
            "https://qph.cf2.quoracdn.net/main-qimg-146ab3a9693b5c97c7fb1e48c3898c46",
            "07a0e7a1965a0c74af2fe221e4922a0e",
        ),
        (
            "quora",
            "https://www.quora.com/What-is-the-history-of-Japanese-jacket-wrestlers-judoka-beating-up-founding-family-members-of-Brazilian-Jiu-Jitsu-the-Gracie-family/answer/Andr%C3%A9-Abrah%C3%A3o-3",  # noqa: W503
            "b3b0c5903a666b88965871fd034110d1",
        ),
        (
            "twitter_img",
            "https://pbs.twimg.com/media/DbeGV44WkAAjNAx.jpg:large",
            "6ea62f00e181fb28beb54a998dd6817f",
        ),
        (
            "twitter_img",
            "https://pbs.twimg.com/media/DbeGV44WkAAjNAx?format=jpg",
            "6ea62f00e181fb28beb54a998dd6817f",
        ),
        (
            "webb_telescope",
            "https://webbtelescope.org/contents/media/images/2023/134/01HAWFJMYS933DDC7NJJE2VFRH",
            "89607347744366c0861286da5307eb24",
        ),
        (
            "wikimedia",
            "https://commons.wikimedia.org/wiki/File:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
            "67c199c4fd2d641e9d608c957193fe07",
        ),
        (
            "wikimedia",
            "https://commons.wikimedia.org/wiki/Gustave_Dor%C3%A9#/media/File:Chess_Single_Image_Stereogram_by_3Dimka.jpg",  # noqa: W503
            "67c199c4fd2d641e9d608c957193fe07",
        ),
        (
            "wikimedia",
            "https://secure.wikimedia.org/wikipedia/fr/wiki/Fichier:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
            "67c199c4fd2d641e9d608c957193fe07",
        ),
        (
            "wikimedia",
            "https://fr.wikipedia.org/wiki/Fichier:Chess_Single_Image_Stereogram_by_3Dimka.jpg",
            "67c199c4fd2d641e9d608c957193fe07",
        ),
        (
            "zbrush_central",
            "https://www.zbrushcentral.com/t/tdk-batman/453080",
            "94ebff2c54729fac4a753d8b02e982df",
        ),
    ],
)
def test_solver(solver: str, url: str, checksum: str, tmp_path: Path) -> None:
    url_img = getattr(solvers, solver)(url, None)
    assert url_img
    img = functions.fetch_image(url_img, verify=True)

    assert img
    file = tmp_path / "file.ext"
    file.write_bytes(img)
    assert functions.checksum(file) == checksum
