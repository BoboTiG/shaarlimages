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
    )
    subparsers = parser.add_subparsers(dest="action")

    # download
    parser_dl = subparsers.add_parser(
        "download", help="download an image found elsewhere than at its original location"
    )
    parser_dl.add_argument("url_original", metavar="URL_ORIGINAL", help="original URL of the image")
    parser_dl.add_argument("url_download", metavar="URL_DOWNLOAD", help="download URL of the image")

    # fix
    subparsers.add_parser("fix", help="several fix actions on images")

    # purge
    parser_purge = subparsers.add_parser("purge", help="remove an image")
    parser_purge.add_argument("FILE", metavar="FILE", help="the image file to remove")

    # sync
    parser_sync = subparsers.add_parser("sync", help="synchronize all shaarlis, or only a specific one")
    parser_sync.add_argument("--url", "-u", help="specific shaarli URL")
    parser_sync.add_argument("--force", "-f", action="store_true", help="force full resync")

    return parser


def main(cli_args: list[str]) -> int:
    import cli
    import helpers

    args = create_parser().parse_args(cli_args)

    match args.action:
        case "download":
            cli.download(args.url_original, args.url_download)
        case "fix":
            cli.fix_images_medatadata()
        case "purge":
            cli.purge({args.FILE})
        case "sync":
            if url := args.url:
                helpers.sync_feed(url, force=args.force)
            else:
                helpers.sync_them_all(force=args.force)

    return 0


if __name__ == "__main__":  # pragma: nocover
    sys.exit(main(sys.argv[1:]))
