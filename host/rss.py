"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import config
import custom_types
import functions

FEED = f"""\
<?xml version="1.0" encoding="UTF-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <atom:link href="{config.SITE.url}{{rss_link}}" rel="self" type="application/rss+xml" />
    <generator>{config.SITE.title}</generator>
    <logo>{config.SITE.url}/favicon.png</logo>
    <subtitle>{config.SITE.description}</subtitle>
    <title>{config.SITE.title}</title>
    <updated>{{date}}</updated>
{{items}}
</feed>
"""
ITEM = """\
    <entry>
        <content type="html" xml:lang="en"><![CDATA[{description}]]></content>
{categories}
        <id>{guid}</id>
        <link href="{link}" />
        <published>{date}</published>
        <title>{title}</title>
    </entry>\
"""


def craft_feed(images: custom_types.Metadatas, rss_link: str) -> str:
    """RSS feed creator."""
    return FEED.format(
        date=functions.format_date(functions.now()),
        items="\n".join(craft_item(image) for image in images),
        rss_link=rss_link,
    )


def craft_item(image: custom_types.Metadata) -> str:
    return ITEM.format(
        categories="\n".join(
            f'{" " * 8}<category scheme="{config.SITE.url}/search/tag/{tag}" term="{tag}" label="{tag}"/>'
            for tag in image.tags
        ),
        date=image.date,
        description=image.desc,
        guid=f"{config.SITE.url}/zoom/{image.link}",
        link=f"{config.SITE.url}/image/{image.link}",
        title=image.title,
    )
