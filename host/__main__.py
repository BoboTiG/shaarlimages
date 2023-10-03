"""
Shaarlimages CLI • https://github.com/BoboTiG/shaarlimages

Usage:
    sync [ACTION]
    sync ACTION --force
    sync ACTION --index IDX
    sync ACTION --index IDX --force

Options:
    -h --help     Show this screen.
    --index=<idx> Feed index to sync.
    --force       Force resync.
"""

if __name__ == "__main__":
    from docopt import docopt

    from . import functions, helpers

    args = docopt(__doc__)
    force = args["--force"]

    match args["ACTION"]:
        case "fix":
            functions.fix_images_medatadata(force=force)
        case "sync":
            if idx := args["--index"]:
                helpers.sync_feed(int(idx), force=force)
            else:
                helpers.sync_them_all(force=force)

    functions.generate_images_file(force=force)
