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
def test_cg_society() -> None:
    url = "https://oscarfb.cgsociety.org/9ndp/aspidochelone"
    body = """
<meta content='https://cg3.cgsociety.org/uploads/images/medium/oscarfb-aspidochelone-1-a6c5cb99-9ndp.jpg' name='twitter:image'>
<meta content='The myth of the living island' name='twitter:description'>
<meta content='OscarFB — Aspidochelone' property='og:title'>
<meta content='https://cg3.cgsociety.org/uploads/images/medium/oscarfb-aspidochelone-1-a6c5cb99-9ndp.jpg' property='og:image'>
<meta content='1366' property='og:image:width'>
	"""  # noqa[W503]

    responses.add(method="GET", url=url, body=body)

    expected = "https://cg3.cgsociety.org/uploads/images/large/oscarfb-aspidochelone-1-a6c5cb99-9ndp.jpg"
    assert solvers.guess_url(url, None) == expected


@responses.activate
@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://i.imgur.com/qypAs0A_d.jpg", "https://i.imgur.com/qypAs0A.jpg"),
        ("https://i.imgur.com/qypAs0A_d.jpg?1", "https://i.imgur.com/qypAs0A.jpg"),
        ("https://i.imgur.com/qypAs0A_d.jpg#1", "https://i.imgur.com/qypAs0A.jpg"),
        ("https://i.imgur.com/qypAs0A_d.jpeg", "https://i.imgur.com/qypAs0A.jpeg"),
        ("https://i.imgur.com/qypAs0A_d.png", "https://i.imgur.com/qypAs0A.png"),
        ("https://i.imgur.com/qypAs0A_dd.jpg", "https://i.imgur.com/qypAs0A_dd.jpg"),
        ("https://i.imgur.com/qypAs0A_dd.jpg?1", "https://i.imgur.com/qypAs0A_dd.jpg"),
        ("https://i.imgur.com/qypAs0A_dd.jpg#1", "https://i.imgur.com/qypAs0A_dd.jpg"),
        ("https://i.imgur.com/qypAs0A_dd.jpeg", "https://i.imgur.com/qypAs0A_dd.jpeg"),
        ("https://i.imgur.com/qypAs0A_dd.png", "https://i.imgur.com/qypAs0A_dd.png"),
    ],
)
def test_imgur(url: str, expected: str) -> None:
    responses.add(method="HEAD", url=expected, content_type="image/jpg")
    assert solvers.guess_url(url, None) == expected


@responses.activate
def test_imgur_removed() -> None:
    url0 = "https://i.imgur.com/qypAs0A_d.jpg"
    url1 = "https://i.imgur.com/qypAs0A.jpg"
    url2 = "https://i.imgur.com/removed.png"

    responses.add(method="HEAD", url=url1, status=302, headers={"Location": url2})
    responses.add(method="HEAD", url=url2, content_type="image/png")
    assert solvers.guess_url(url0, None) == ""


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
def test_quora() -> None:
    url = "https://www.quora.com/What-is-the-history-of-Japanese-jacket-wrestlers-judoka-beating-up-founding-family-members-of-Brazilian-Jiu-Jitsu-the-Gracie-family/answer/Andr%C3%A9-Abrah%C3%A3o-3"  # noqa[W503]
    body = """
<title>(15) André Abrahão&#039;s answer to What is the history of Japanese jacket wrestlers (judoka) beating up founding family members of Brazilian Jiu-Jitsu (the Gracie family)? - Quora</title>
<link rel='icon' href='https://qsf.cf2.quoracdn.net/-4-images.favicon-new.ico-26-07ecf7cd341b6919.ico' />
<meta name="robots" content="noindex, follow" />
<meta property='fb:app_id' content='136609459636' />
<meta property='og:title' content='What is the history of Japanese jacket wrestlers (judoka) beating up founding family members of Brazilian Jiu-Jitsu (the Gracie family)?' />
<meta property='og:type' content='article' />
<meta property='og:site_name' content='Quora' />
<meta property='og:image' content='https://qph.cf2.quoracdn.net/main-qimg-c419a1e03b967d4c9f61286a32f34613' />
<meta property='og:url' content='https://www.quora.com/What-is-the-history-of-Japanese-jacket-wrestlers-judoka-beating-up-founding-family-members-of-Brazilian-Jiu-Jitsu-the-Gracie-family/answer/André-Abrahão-3' />
<meta property='og:description' content='André Abrahão&#039;s answer: To understand this, one must know the history of Brazilian Jiu Jitsu (BJJ).

BJJ is a direct “son” of the original Judo.

And Judo is a “son” of the original Japanese JuJutsu, an old martial art used by the samurais in real wars, that was banned with the end of the Feudal ...' />
<meta name='twitter:card' content='summary_large_image' />
<meta name='twitter:site' content='@Quora' />
<meta name='twitter:url' content='https://www.quora.com/What-is-the-history-of-Japanese-jacket-wrestlers-judoka-beating-up-founding-family-members-of-Brazilian-Jiu-Jitsu-the-Gracie-family/answer/André-Abrahão-3' />
<meta name='twitter:title' content='What is the history of Japanese jacket wrestlers (judoka) beating up founding family members of Brazilian Jiu-Jitsu (the Gracie family)?' />
<meta name='twitter:description' content='André Abrahão&#039;s answer: To understand this, one must know the history of Brazilian Jiu Jitsu (BJJ).

BJJ is a direct “son” of the original Judo.

And Judo is a “son” of the original Japanese JuJutsu, an old martial art used by the samurais in real wars, that was banned with the end of the Feudal ...' />
<meta name='twitter:image' content='https://qph.cf2.quoracdn.net/main-qimg-c419a1e03b967d4c9f61286a32f34613' />
<link rel='canonical' href='https://www.quora.com/What-is-the-history-of-Japanese-jacket-wrestlers-judoka-beating-up-founding-family-members-of-Brazilian-Jiu-Jitsu-the-Gracie-family' />
"""  # noqa[W503]

    responses.add(method="GET", url=url, body=body)
    assert solvers.guess_url(url, None) == "https://qph.cf2.quoracdn.net/main-qimg-c419a1e03b967d4c9f61286a32f34613"


@responses.activate
def test_webb_telescope() -> None:
    url = "https://webbtelescope.org/contents/media/images/2022/041/01GA77HHT9R4WR4XT89704VT4M?page=2&filterUUID=91dfa083-c258-4f9f-bef1-8f40c26f4c97"  # noqa[W503]
    body = """
    <meta property="og:url" content="https://webbtelescope.org/contents/media/images/2022/041/01GA77HHT9R4WR4XT89704VT4M">
    <meta property="og:image" content="//stsci-opo.org/STScI-01GD3HTYP68G8VQFJPNZ0RVBT9.png">
    <meta property="og:image:type" content="image/png">
    """  # noqa[W503]

    responses.add(method="GET", url=url, body=body)
    assert solvers.guess_url(url, None) == "https://stsci-opo.org/STScI-01GD3HTYP68G8VQFJPNZ0RVBT9.png"


@responses.activate
def test_webb_telescope_nothing_found() -> None:
    url = "https://webbtelescope.org/contents/media/images/2022/041/01GA77HHT9R4WR4XT89704VT4M?page=2&filterUUID=91dfa083-c258-4f9f-bef1-8f40c26f4c97"  # noqa[W503]
    body = """
    <meta property="og:url" content="https://webbtelescope.org/contents/media/images/2022/041/01GA77HHT9R4WR4XT89704VT4M">
    <meta property="og:image:type" content="image/png">
	"""  # noqa[W503]

    responses.add(method="GET", url=url, body=body)
    assert solvers.guess_url(url, None) == ""


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


@responses.activate
def test_zbrushcentral() -> None:
    url = "https://www.zbrushcentral.com/t/tdk-batman/453080"
    body = """
<meta property="og:image" content="http://www.zbrushcentral.com/uploads/default/optimized/4X/1/a/b/1abfaaf8e1c27403c147abe77407231d79a9172c_2_1024x683.jpeg" />
<meta property="og:url" content="http://www.zbrushcentral.com/t/tdk-batman/453080" />
<meta name="twitter:url" content="http://www.zbrushcentral.com/t/tdk-batman/453080" />
	"""  # noqa[W503]

    responses.add(method="GET", url=url, body=body)

    expected = "http://www.zbrushcentral.com/uploads/default/optimized/4X/1/a/b/1abfaaf8e1c27403c147abe77407231d79a9172c_2_1024x683.jpeg"  # noqa[W503]
    assert solvers.guess_url(url, None) == expected
