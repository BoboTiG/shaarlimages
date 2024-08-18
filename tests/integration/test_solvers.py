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
            "https://i.imgur.com/y06MsKG.jpg",  # Removed
            "d41d8cd98f00b204e9800998ecf8427e",
        ),
        (
            "imgur",
            "https://i.imgur.com/qypAs0A_d.jpg",
            "bca5dcf37292b684035984ff69f5ecb8",
        ),
        (
            "lutim",
            "https://lut.im/0p6CmKuV/YyBE3qfb",
            "becb6c495c6927446158b822deca3f0e",
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
            "c419a1e03b967d4c9f61286a32f34613",
        ),
        (
            "twitter_img",
            "https://pbs.twimg.com/media/DbeGV44WkAAjNAx.jpg:large",
            "3477f54ac9564123b66503c364a2d18a",
        ),
        (
            "twitter_img",
            "https://pbs.twimg.com/media/DbeGV44WkAAjNAx?format=jpg",
            "3477f54ac9564123b66503c364a2d18a",
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
    img = b""
    if url_img := getattr(solvers, solver)(url, None):
        img = functions.fetch_image(url_img, verify=True)

    file = tmp_path / "file.ext"
    file.write_bytes(img)
    assert functions.checksum(file) == checksum
