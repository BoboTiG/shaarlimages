"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from pathlib import Path
from random import choice, randint

from host import custom_types, functions
from host.constants import DATA, FEEDS


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


def test_get_last(setup_data) -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    total = len(data)

    assert functions.get_last(0, 1) == (total, [])
    assert functions.get_last(1, 1) == (total, [data[0]])
    assert functions.get_last(1, 10) == (total, data[:10])
    assert functions.get_last(2, 1) == (total, [data[1]])
    assert functions.get_last(2, 10) == (total, data[10:20])


def test_get_metadata(setup_data) -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    idx = randint(1, len(data) - 2)
    image = data[idx]

    prev_img, metadata, next_img = functions.get_metadata(image.link)
    assert metadata == image
    assert prev_img == data[idx - 1].link
    assert next_img == data[idx + 1].link


def test_get_metadata_first(setup_data) -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    image = data[0]

    prev_img, metadata, next_img = functions.get_metadata(image.link)
    assert metadata == image
    assert prev_img == ""
    assert next_img == data[1].link


def test_get_metadata_last(setup_data) -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    image = data[-1]

    prev_img, metadata, next_img = functions.get_metadata(image.link)
    assert metadata == image
    assert prev_img == data[-2].link
    assert next_img == ""


def test_load_metadata(tmp_path: Path, setup_data) -> None:
    feed = choice(list((tmp_path / DATA.name / FEEDS.name).glob("*.json")))
    data = functions.load_metadata(feed)

    assert data
    assert isinstance(data, list)

    key, item = choice(data)
    assert isinstance(key, float)
    check_item(item)


def test_lookup(setup_data) -> None:
    result_lowercase = functions.lookup("robe")

    assert result_lowercase
    assert isinstance(result_lowercase, list)
    for item in result_lowercase:
        check_item(item)

    result_uppercase = functions.lookup("ROBE")
    assert result_lowercase == result_uppercase


def test_lookup_tag(setup_data) -> None:
    result_lowercase = functions.lookup_tag("sample")

    assert result_lowercase
    assert isinstance(result_lowercase, list)
    for item in result_lowercase:
        check_item(item)

    result_uppercase = functions.lookup_tag("SAMPLE")
    assert result_lowercase == result_uppercase


def test_retrieve_all_uniq_metadata(setup_data) -> None:
    data = list(functions.retrieve_all_uniq_metadata())
    assert data

    item = choice(data)
    check_item(item)
