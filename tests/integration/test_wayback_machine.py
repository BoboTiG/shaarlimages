"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

import pytest

from host import functions


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://lh4.googleusercontent.com/-Rw5ELCgTOwc/VLVE6HNxicI/AAAAAAAAGTM/YDtaR8Qc-Ys/w960-h614-no/Patrio%2Bact%2Bfrance.jpg",  # noqa[W503]
            "https://web.archive.org/web/20160826130632if_/https://lh4.googleusercontent.com/-Rw5ELCgTOwc/VLVE6HNxicI/AAAAAAAAGTM/YDtaR8Qc-Ys/w960-h614-no/Patrio%2Bact%2Bfrance.jpg",  # noqa[W503]
        ),
    ],
)
@pytest.mark.parametrize("method", ["head", "get"])
def test_wayback_machine(method: str, url: str, expected: str) -> None:
    assert functions.try_wayback_machine(url, method=method).url == expected
