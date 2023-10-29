"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from email.utils import formatdate
from pathlib import Path

import constants
import functions

MD5_EMPTY = "d835884373f4d6c8f24742ceabe74946"


def fix_images_medatadata(force: bool = False):
    at_least_one_change = False
    images = {image.name for image in constants.IMAGES.glob("*.*")}

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
            key = file.stem[:6]  # The small hash
            name_original = file.stem[7:]
            name_sanitized = functions.safe_filename(name_original)
            name_has_changed = False

            if name_original != name_sanitized:
                name_has_changed = True
                new_file = file.with_stem(f"{key}_{name_sanitized}")
            elif file.suffix not in list(constants.IMAGES_CONTENT_TYPE.values()):
                if file.suffix.startswith((".jpg", ".jpeg")):
                    name_has_changed = True
                    new_file = file.with_suffix(".jpg")
                elif file.suffix.startswith(".png"):
                    name_has_changed = True
                    new_file = file.with_suffix(".png")
                else:
                    del data[k]
                    changed = True
                    at_least_one_change = True

            if name_has_changed:
                print(f"{file.name!r} -> {new_file.name!r}")
                file = new_file if new_file.is_file() else file.rename(new_file)
                data[k] |= {"link": file.name}
                changed = True
                at_least_one_change = True

                # Recreate the thumbnail
                (constants.THUMBNAILS / v["link"]).unlink(missing_ok=True)
                functions.create_thumbnail(file)

            images.discard(v["link"])

            # Fix the size
            if force or "width" not in v:
                if not (size := functions.get_size(file)):
                    del data[k]
                    changed = True
                    at_least_one_change = True
                    continue

                data[k] |= {"width": size.width, "height": size.height}
                changed = True
                at_least_one_change = True

            # Fix the dominant color average
            if force or "docolav" not in v:
                if not (color := functions.docolav(file)):
                    del data[k]
                    changed = True
                    at_least_one_change = True
                    continue

                data[k] |= {"docolav": color}
                changed = True
                at_least_one_change = True

            # Fix tags
            sanitized_tags = sorted(functions.safe_tag(tag) for tag in v["tags"])
            if v["tags"] != sanitized_tags:
                data[k] |= {"tags": sanitized_tags}
                changed = True
                at_least_one_change = True

            # Purge removed Imgur images
            if functions.checksum(file) == MD5_EMPTY:
                del data[k]
                changed = True
                at_least_one_change = True
                continue

            # Add checksum
            if not v.get("checksum", ""):
                data[k] |= {"checksum": functions.checksum(file)}
                changed = True
                at_least_one_change = True

            # Add URL
            if "url" not in v:
                data[k] |= {"url": ""}
                changed = True
                at_least_one_change = True

            # Add date
            if "date" not in v:
                data[k] |= {"date": formatdate(timeval=float(k), usegmt=True)}
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
