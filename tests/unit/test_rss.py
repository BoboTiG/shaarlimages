"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import feedparser

from host import config, functions, rss


def test_craft_feed() -> None:
    feed = feedparser.parse(rss.craft_feed([], "/rss")).feed

    assert feed.generator == config.SITE.title
    assert feed.atom_link["href"] == f"{config.SITE.url}/rss"
    assert feed.atom_link["rel"] == "self"
    assert feed.atom_link["type"] == "application/rss+xml"
    assert feed.logo == f"{config.SITE.url}/favicon.png"
    assert feed.subtitle == config.SITE.description
    assert feed.title == config.SITE.title
    assert feed.updated


def test_craft_item(setup_data) -> None:
    images = functions.retrieve_all_uniq_metadata()
    feed = feedparser.parse(rss.craft_feed(images, ""))

    items = feed.entries
    assert len(items) == 5

    item = feed.entries[0]
    assert item.content[0].value == "Simple description with the 'robe' keyword."
    assert item.id == "https://www.shaarlimages.net/zoom/aGE2Q5Z_460swp.webp"
    assert item.link == "https://www.shaarlimages.net/image/aGE2Q5Z_460swp.webp"
    assert item.published
    assert sorted(tag.term for tag in item.tags) == ["image", "nsfw", "sample", "test"]
    assert item.title == "Awesome image!"
