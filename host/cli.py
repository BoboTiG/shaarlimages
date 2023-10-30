"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from contextlib import suppress
from pathlib import Path

import constants
import functions

MD5_EMPTY = "d835884373f4d6c8f24742ceabe74946"


def fix_images_medatadata(force: bool = False):
    at_least_one_change = False

    for feed in constants.FEEDS.glob("*.json"):
        changed = False
        data = functions.read(feed)

        if not data:
            print(f" ! Remove empty feed {feed}")
            feed.unlink()
            continue

        for k, v in data.copy().items():
            if not v:
                del data[k]
                changed = True
                at_least_one_change = True
                continue

            # Fix the filename
            file: Path = constants.IMAGES / v["link"]
            stem = file.stem
            if len(stem) > 6:
                name = file.name
                new_file = file.with_stem(stem[:6])
                print(f"{file.name!r} -> {new_file.name!r}")
                file = new_file if new_file.is_file() else file.rename(new_file)
                data[k] |= {"link": file.name}
                changed = True
                at_least_one_change = True

                # Rename the thumbnail
                thumb = constants.THUMBNAILS / name
                with suppress(FileNotFoundError):
                    thumb.rename(thumb.with_stem(new_file.stem))

            # Purge removed Imgur images
            if data[k]["checksum"] == MD5_EMPTY:
                del data[k]
                changed = True
                at_least_one_change = True
                continue

            # Rename "link" to "file"
            data[k]["file"] = data[k].pop("link")
            changed = True
            at_least_one_change = True

        if not data:
            print(f" ! Remove empty feed {feed}")
            feed.unlink()
            at_least_one_change = True
        elif changed:
            functions.persist(feed, data)

    if at_least_one_change:
        functions.invalidate_caches()


def purge(files: set[str]) -> None:
    """Remove an image from databases."""
    at_least_one_change = False

    for file in files:
        print(" !! Removing file", file)

    for feed in constants.FEEDS.glob("*.json"):
        changed = False
        cache = functions.read(feed)

        for date, metadata in cache.copy().items():
            if metadata["link"] in files:
                cache.pop(date)
                changed = True
                at_least_one_change = True

        if changed:
            functions.persist(feed, cache)

    for file in files:
        (constants.IMAGES / file).unlink(missing_ok=True)
        (constants.THUMBNAILS / file).unlink(missing_ok=True)

    if at_least_one_change:
        functions.invalidate_caches()
