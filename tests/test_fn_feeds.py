"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from random import choice, randint

from host import constants, custom_types, functions


def random_feed() -> Path:
    feed = choice(list(constants.CACHE_FEEDS.glob("*.json")))
    print(f"Chosen {feed = }")
    return feed


def check_item(item: custom_types.Metadata) -> None:
    assert isinstance(item, custom_types.Metadata)
    assert isinstance(item.desc, str)
    assert isinstance(item.docolav, str)
    assert isinstance(item.guid, str)
    assert isinstance(item.height, int)
    assert isinstance(item.link, str)
    assert isinstance(item.tags, list)
    assert isinstance(item.title, str)
    assert isinstance(item.width, int)

    assert len(item.docolav) == 6
    assert item.height > 0
    assert item.width > 0


def test_get_last() -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    total = len(data)

    assert functions.get_last(0, 1) == (total, [])
    assert functions.get_last(1, 1) == (total, [data[0]])
    assert functions.get_last(1, 10) == (total, data[:10])
    assert functions.get_last(2, 1) == (total, [data[1]])
    assert functions.get_last(2, 10) == (total, data[10:20])


def test_get_metadata() -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    idx = randint(0, len(data) - 1)
    metadata = data[idx]

    assert functions.get_metadata(metadata.link) == metadata


def test_get_prev_next() -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    idx = randint(1, len(data) - 2)
    metadata = data[idx]
    prev_img, next_img = functions.get_prev_next(metadata.link)

    assert prev_img == data[idx - 1].link
    assert next_img == data[idx + 1].link


def test_load_metadata() -> None:
    feed = random_feed()
    data = functions.load_metadata(feed)

    assert data
    assert isinstance(data, list)

    key, item = choice(data)
    assert isinstance(key, float)
    check_item(item)


def test_lookup() -> None:
    result_lowercase = functions.lookup("robe")

    assert result_lowercase
    assert isinstance(result_lowercase, list)
    for item in result_lowercase:
        check_item(item)

    result_uppercase = functions.lookup("ROBE")
    assert result_lowercase == result_uppercase


def test_lookup_tag() -> None:
    result_lowercase = functions.lookup_tag("robe")

    assert result_lowercase
    assert isinstance(result_lowercase, list)
    for item in result_lowercase:
        check_item(item)

    result_uppercase = functions.lookup_tag("ROBE")
    assert result_lowercase == result_uppercase


def test_retrieve_all_uniq_metadata() -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    assert data

    item = choice(data)
    check_item(item)
