"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from random import choice, randint

import feedparser
from _pytest.fixtures import FixtureFunction

from host import config, custom_types, functions
from host.constants import DATA, FEEDS, HASH_LEN


def check_item(item: custom_types.Metadata) -> None:
    assert isinstance(item, custom_types.Metadata)
    assert isinstance(item.description, str)
    assert isinstance(item.docolav, str)
    assert isinstance(item.guid, str)
    assert isinstance(item.height, int)
    assert isinstance(item.file, str)
    assert isinstance(item.tags, list)
    assert isinstance(item.title, str)
    assert isinstance(item.width, int)

    assert len(item.docolav) == HASH_LEN
    assert item.height > 0
    assert item.width > 0


def test_craft_feed(setup_data: FixtureFunction) -> None:
    images = functions.retrieve_all_uniq_metadata()
    parsed = feedparser.parse(functions.craft_feed(images, "/rss"))

    feed = parsed.feed
    assert feed.author == config.SITE.title
    assert feed.description == config.SITE.description
    assert feed.link == f"{config.SITE.url}/rss"
    assert sorted(tag.term for tag in feed.tags) == ["Shaarli", "gallery", "image"]
    assert feed.title == config.SITE.title

    items = parsed.entries
    assert len(items) == 4

    item = items[0]
    assert config.SITE.url in item.description
    assert "Simple description with the 'robe' keyword." in item.description
    assert item.link.startswith(f"{config.SITE.url}/zoom/")
    assert sorted(tag.term for tag in item.tags) == ["clothes", "image", "sample", "test"]
    assert item.title == "Awesome image!"


def test_get_last(setup_data: FixtureFunction) -> None:
    data = functions.retrieve_all_uniq_metadata()
    total = len(data)

    assert functions.get_last(0, 1) == (total, [])
    assert functions.get_last(1, 1) == (total, [data[0]])
    assert functions.get_last(1, 10) == (total, data[:10])
    assert functions.get_last(2, 1) == (total, [data[1]])
    assert functions.get_last(2, 10) == (total, data[10:20])


def test_get_metadata(setup_data: FixtureFunction) -> None:
    data = functions.retrieve_all_uniq_metadata()
    idx = randint(1, len(data) - 2)
    image = data[idx]

    res = functions.get_metadata(image.file)
    assert res
    prev_img, metadata, next_img = res
    assert metadata == image
    assert prev_img == data[idx - 1].file
    assert next_img == data[idx + 1].file


def test_get_metadata_first(setup_data: FixtureFunction) -> None:
    data = functions.retrieve_all_uniq_metadata()
    image = data[0]

    res = functions.get_metadata(image.file)
    assert res
    prev_img, metadata, next_img = res
    assert metadata == image
    assert prev_img == ""
    assert next_img == data[1].file


def test_get_metadata_last(setup_data: FixtureFunction) -> None:
    data = functions.retrieve_all_uniq_metadata()
    image = data[-1]

    res = functions.get_metadata(image.file)
    assert res
    prev_img, metadata, next_img = res
    assert metadata == image
    assert prev_img == data[-2].file
    assert next_img == ""


def test_get_tags(setup_data: FixtureFunction) -> None:
    assert functions.get_tags() == ["clothes", "image", "nsfw", "sample", "test"]


def test_get_random_image(setup_data: FixtureFunction) -> None:
    metadata = functions.get_random_image()
    assert isinstance(metadata, custom_types.Metadata)


def test_load_metadata(tmp_path: Path, setup_data: FixtureFunction) -> None:
    feed = choice(list((tmp_path / DATA.name / FEEDS.name).glob("*.json")))
    data = functions.load_metadata(feed)

    assert data
    assert isinstance(data, list)

    item = choice(data)
    check_item(item)


def test_lookup(setup_data: FixtureFunction) -> None:
    result_lowercase = functions.lookup("robe")

    assert result_lowercase
    assert isinstance(result_lowercase, list)
    for item in result_lowercase:
        check_item(item)

    result_uppercase = functions.lookup("ROBE")
    assert result_lowercase == result_uppercase


def test_lookup_tag(setup_data: FixtureFunction) -> None:
    result_lowercase = functions.lookup_tag("sample")

    assert result_lowercase
    assert isinstance(result_lowercase, list)
    for item in result_lowercase:
        check_item(item)

    result_uppercase = functions.lookup_tag("SAMPLE")
    assert result_lowercase == result_uppercase


def test_retrieve_all_uniq_metadata(setup_data: FixtureFunction) -> None:
    data = functions.retrieve_all_uniq_metadata()
    assert data

    item = choice(data)
    check_item(item)
