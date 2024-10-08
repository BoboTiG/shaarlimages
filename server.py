"""Local web server for testing purposes."""

if __name__ == "__main__":  # pragma:nocover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent / "host"))

    import bottle
    from paste import httpserver

    from host.app import application
    from host.constants import HTTP_PORT

    bottle.debug()
    httpserver.serve(application, host="0.0.0.0", port=HTTP_PORT)  # noqa: S104
