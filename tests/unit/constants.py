"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import re
from pathlib import Path

from host.custom_types import Size

HERE = Path(__file__).parent
DATA = HERE / "data"
IMAGE_JPG = DATA / "0_kVjw_SjIx2y8.jpg"
IMAGE_JPG_IS_PNG = DATA / "ZKwOVg_vYAvIM0_d.jpg"
IMAGE_PNG = DATA / "8kZBBg_1471877768-20160824.png"
IMAGE_SQUARE = DATA / "-1hlcA_icugvpr.jpg"
IMAGE_WEBP = DATA / "aGE2Q5Z_460swp.webp"

TEST_IMAGES = [
    (IMAGE_JPG, 22548, Size(width=400, height=267), "585E50", "29c25875e30fe9547349057887b19682"),
    (IMAGE_JPG_IS_PNG, 503, Size(width=161, height=81), "323232", "d835884373f4d6c8f24742ceabe74946"),
    (IMAGE_PNG, 61283, Size(width=317, height=400), "B19C95", "2a4ab87892014129a4f1e73ba9dfe22d"),
    (IMAGE_SQUARE, 21519, Size(width=400, height=400), "656B72", "8bdecafe89fd9e02981720ba8172dad4"),
    (IMAGE_WEBP, 123482, Size(width=358, height=400), "6A7777", "95603fa0936de10e5068b1d200680273"),
]
FEED_URL = "https://shaarli.example.org"
FEED_XML = (
    f"""
<?xml version="1.0" encoding="UTF-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Liens en vrac de Alice</title>
    <subtitle>Shaared links</subtitle>
    <updated>2023-08-10T22:41:40+02:00</updated>
    <author>
        <name>Liens en vrac de Alice</name>
        <uri>{FEED_URL}</uri>
    </author>
    <id>{FEED_URL}</id>
    <generator>Shaarli</generator>
"""
    + f"""
    <entry>
        <title>Not an image</title>
        <link href="{FEED_URL}/code.txt" />
        <id>{FEED_URL}/shaare/1</id>
        <published>2023-08-10T22:41:41+02:00</published>
    </entry>
"""
    + f"""
    <entry>
        <title>Not an image link with actual image data</title>
        <link href="https://qph.cf2.quoracdn.net/main-qimg-ok" />
        <id>{FEED_URL}/shaare/2</id>
        <published>2023-08-11T22:41:41+02:00</published>
        <content type="html" xml:lang="en"></content>
    </entry>
"""
    + f"""
    <entry>
        <title>Not an image link and not image data</title>
        <link href="https://qph.cf2.quoracdn.net/main-qimg-bad" />
        <id>{FEED_URL}/shaare/3</id>
        <published>2023-08-11T22:41:41+02:00</published>
        <content type="html" xml:lang="en"></content>
    </entry>
"""
    + f"""
    <entry>
        <title>Not an image link and website is down</title>
        <link href="https://qph.cf2.quoracdn.net/main-qimg-down" />
        <id>{FEED_URL}/shaare/4</id>
        <published>2023-08-11T22:41:41+02:00</published>
        <content type="html" xml:lang="en"></content>
    </entry>
"""
    + "\n".join(
        f"""
    <entry>
        <title>Image - {file.name}</title>
        <link href="{FEED_URL}/{file.name}" />
        <id>{FEED_URL}/shaare/{file.name}</id>
        <published>2023-08-20T22:41:4{idx}+02:00</published>
        <content type="html" xml:lang="en"><![CDATA[
            Some description with the 'robe' keyword.
            {"Lets also trigger the Not Safe For Work filter here: NSFW!" if file == TEST_IMAGES[-1][0] else ""}
        ]]></content>
        <category scheme="{FEED_URL}/?searchtags=" term="sample" label="sample" />
        <category scheme="{FEED_URL}/?searchtags=" term="test" label="test" />
        <category scheme="{FEED_URL}/?searchtags=" term="image" label="image" />
    </entry>
"""
        for idx, (file, *_) in enumerate(TEST_IMAGES)
    )
    + "</feed>"
)
FEED_XML_NO_TIMESTAMPS = re.sub(r"<published>.+</published>", "", FEED_XML)