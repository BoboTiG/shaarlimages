"""
Shaarlimages CLI • https://github.com/BoboTiG/shaarlimages

Usage:
    prog -h
    prog fix [--force]
    prog purge FILE
    prog sync [--force] [--index=IDX]

Arguments:
    FILE  The image to delete.

Options:
    -h --help     Show this screen.
    --index=IDX   Feed index to synchronize.
    --force       Force the action.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import functions
    import helpers
    from docopt import docopt

    args = docopt(__doc__)
    force = args["--force"]

    if args["fix"]:
        functions.fix_images_medatadata(force=force)
    elif args["purge"]:
        functions.purge({args["FILE"]})
    elif args["sync"]:
        if idx := args["--index"]:
            helpers.sync_feed(int(idx), force=force)
        else:
            helpers.sync_them_all(force=force)
