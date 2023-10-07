"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path

from host.custom_types import Size

HERE = Path(__file__).parent
DATA = HERE / "data"
IMAGE_JPG = DATA / "0_kVjw_SjIx2y8.jpg"
IMAGE_JPG_IS_PNG = DATA / "ZKwOVg_vYAvIM0_d.jpg"
IMAGE_PNG = DATA / "8kZBBg_1471877768-20160824.png"
IMAGE_SQUARE = DATA / "-1hlcA_icugvpr.jpg"

TEST_IMAGES = [
    (IMAGE_JPG, 22548, Size(width=400, height=267), "585E50"),
    (IMAGE_JPG_IS_PNG, 503, Size(width=161, height=81), "323232"),
    (IMAGE_PNG, 61283, Size(width=317, height=400), "B19C95"),
    (IMAGE_SQUARE, 21519, Size(width=400, height=400), "656B72"),
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
    <entry>
        <title>A link</title>
        <link href="{FEED_URL}/code.txt" />
        <id>{FEED_URL}/shaare/0</id>
        <published>2023-08-10T22:41:40+02:00</published>
        <updated>2023-08-10T22:41:40+02:00</updated>
        <content type="html" xml:lang="en"></content>
    </entry>
"""
    + "\n".join(
        f"""
    <entry>
        <title>Image n° {idx}</title>
        <link href="{FEED_URL}/{file.name}" />
        <id>{FEED_URL}/shaare/{idx}</id>
        <published>2023-08-10T22:41:4{idx}+02:00</published>
        <updated>2023-08-10T22:41:4{idx}+02:00</updated>
        <content type="html" xml:lang="en"><![CDATA[
            Some description with the 'robe' keyword.
            {"Lets also trigger the Not Safe For Work filter here: NSFW!" if idx == 3 else ""}
        ]]></content>
        <category scheme="{FEED_URL}/?searchtags=" term="sample" label="sample" />
        <category scheme="{FEED_URL}/?searchtags=" term="test" label="test" />
        <category scheme="{FEED_URL}/?searchtags=" term="image" label="image" />
    </entry>
"""
        for idx, (file, *_) in enumerate(TEST_IMAGES, 1)
    )
    + "</feed>"
)
