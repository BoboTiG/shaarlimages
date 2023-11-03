"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

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

            # Purge removed Imgur images
            if data[k]["checksum"] == MD5_EMPTY:
                print("- Imgur", v["file"], flush=True)
                del data[k]
                changed = True
                at_least_one_change = True
                continue

            # Fix date
            if not isinstance(v["date"], float):
                print("! date", v["file"], flush=True)
                data[k] |= {"date": float(k)}
                changed = True
                at_least_one_change = True

            # add missing NSFW tag
            if constants.NSFW not in v["tags"] and functions.is_nsfw(v):
                print("+ NSFW", v["file"], flush=True)
                v["tags"].append(constants.NSFW)
                v["tags"] = sorted(v["tags"])
                changed = True
                at_least_one_change = True

        if not data:
            print(f" ! Remove empty feed {feed}", flush=True)
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
            if metadata["file"] in files:
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
