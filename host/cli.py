"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import constants
import functions

MD5_EMPTY = "d835884373f4d6c8f24742ceabe74946"


def download(url_original: str, url_download: str) -> None:
    cache_key = functions.small_hash(url_original)
    ext = functions.fetch_image_type(url_download)
    output_file = constants.IMAGES / f"{cache_key}{ext}"

    if output_file.is_file():
        return

    image = functions.fetch_image(url_download)
    output_file.write_bytes(image)

    functions.create_thumbnail(output_file)
    print(f"+ {cache_key}{ext}", flush=True)


def fix_images_medatadata() -> None:
    at_least_one_change = False

    for feed in constants.FEEDS.glob("*.json"):
        changed = False
        data = functions.read(feed)

        for stem, metadata in data.copy().items():
            if not metadata:
                del data[stem]
                changed = True
                at_least_one_change = True
                continue

            # Purge removed Imgur images
            if data[stem]["checksum"] == MD5_EMPTY:
                print("- Imgur", metadata["file"], flush=True)
                del data[stem]
                changed = True
                at_least_one_change = True
                continue

            # Add missing NSFW tag
            if constants.NSFW not in metadata["tags"] and functions.is_nsfw(metadata):
                print("+ NSFW", metadata["file"], flush=True)
                metadata["tags"].append(constants.NSFW)
                metadata["tags"] = sorted(metadata["tags"])
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

        for stem, metadata in cache.copy().items():
            if metadata["file"] in files:
                cache.pop(stem)
                changed = True
                at_least_one_change = True

        if changed:
            functions.persist(feed, cache)

    for file in files:
        (constants.IMAGES / file).unlink(missing_ok=True)
        (constants.THUMBNAILS / file).unlink(missing_ok=True)

    if at_least_one_change:
        functions.invalidate_caches()
