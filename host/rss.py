"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from email.utils import formatdate

import config
import custom_types
import functions

FEED = f"""\
<?xml version="1.0" encoding="UTF-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>{config.SITE.title}</title>
    <subtitle>{config.SITE.description}</subtitle>
    <published>{{date}}</published>
    <updated>{{date}}</updated>
    <id>{config.SITE.url}</id>
    <generator>{config.SITE.title}</generator>
    <logo>{config.SITE.url}/favicon.png</logo>
{{items}}
</feed>
"""
ITEM = """\
    <entry>
        <title>{title}</title>
        <link href="{link}" />
        <id>{guid}</id>
        <published>{date}</published>
        <content type="html" xml:lang="en"><![CDATA[{description}]]></content>
{categories}
    </entry>\
"""


def craft_feed(images: custom_types.Metadatas) -> str:
    """RSS feed creator."""
    return FEED.format(
        date=formatdate(timeval=functions.now(), usegmt=True),
        items="\n".join(craft_item(image) for image in images),
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
