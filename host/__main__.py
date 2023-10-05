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
    import functions
    import helpers
    from docopt import docopt

    args = docopt(__doc__)
    force = args["--force"]

    match args["ACTION"]:
        case "fix":
            functions.fix_images_medatadata(force=force)
        case "purge":
            if idx := args["--index"]:
                functions.purge({idx})
        case "sync":
            if idx := args["--index"]:
                helpers.sync_feed(int(idx), force=force)
            else:
                helpers.sync_them_all(force=force)
