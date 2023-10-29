"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from email.utils import formatdate

import config
import custom_types
import functions

FEED = f"""\
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <description>{config.SITE.description}</description>
        <category>gallery</category>
        <category>images</category>
        <category>Shaarli</category>
        <generator>{config.SITE.title}</generator>
        <image>
            <link>{config.SITE.url}</link>
            <title>{config.SITE.title}</title>
            <url>{config.SITE.url}/favicon.png</url>
        </image>
        <link>{config.SITE.url}</link>
        <pubDate>{{date}}</pubDate>
        <title>{config.SITE.title}</title>
{{items}}
    </channel>
</rss>
"""
ITEM = """\
        <item>
            <description><![CDATA[{description}]]></description>
{categories}
            <guid>{guid}</guid>
            <link>{link}</link>
            <pubDate>{date}</pubDate>
            <title>{title}</title>
        </item>\
"""


def craft_feed(images: custom_types.Metadatas) -> str:
    """RSS feed creator."""
    return FEED.format(
        date=formatdate(timeval=functions.now(), usegmt=True),
        items="\n".join(craft_item(image) for image in images),
    )


def craft_item(image: custom_types.Metadata) -> str:
    return ITEM.format(
        categories="\n".join(f"{' ' * 12}<category>{tag}</category>" for tag in image.tags),
        date=image.date,
        description=image.desc,
        guid=f"{config.SITE.url}/zoom/{image.link}",
        link=f"{config.SITE.url}/image/{image.link}",
        title=image.title,
    )
