"""
Shaarlimages CLI • https://github.com/BoboTiG/shaarlimages
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""
import sys
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="python -m host",
        description="Shaarlimages CLI • https://github.com/BoboTiG/shaarlimages",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(dest="action")

    # fix
    parser_fix = subparsers.add_parser("fix", help="several fix actions on images")
    parser_fix.add_argument("--force", action="store_true", help="force full recheck")

    # purge
    parser_purge = subparsers.add_parser("purge", help="remove an image")
    parser_purge.add_argument("FILE", metavar="FILE", help="the image file to remove")

    # sync
    parser_sync = subparsers.add_parser("sync", help="synchronize all shaarlis, or only a specific one")
    parser_sync.add_argument("--url", help="specific shaarli URL")
    parser_sync.add_argument("--force", action="store_true", help="force full resync")

    return parser


def main(cli_args: list[str]) -> int:
    import functions
    import helpers

    args = create_parser().parse_args(cli_args)
    print(args)

    match args.action:
        case "fix":
            functions.fix_images_medatadata(force=args.force)
        case "purge":
            functions.purge({args.FILE})
        case "sync":
            if url := args.url:
                helpers.sync_feed(url, force=args.force)
            else:
                helpers.sync_them_all(force=args.force)

    return 0


if __name__ == "__main__":  # pragma: nocover
    sys.exit(main(sys.argv[1:]))
