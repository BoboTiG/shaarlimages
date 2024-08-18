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
            "https://lh4.googleusercontent.com/-Rw5ELCgTOwc/VLVE6HNxicI/AAAAAAAAGTM/YDtaR8Qc-Ys/w960-h614-no/Patrio%2Bact%2Bfrance.jpg",  # noqa: W503
            "https://web.archive.org/web/20160826130632if_/https://lh4.googleusercontent.com/-Rw5ELCgTOwc/VLVE6HNxicI/AAAAAAAAGTM/YDtaR8Qc-Ys/w960-h614-no/Patrio%2Bact%2Bfrance.jpg",  # noqa: W503
        ),
    ],
)
@pytest.mark.parametrize("method", ["head", "get"])
def test_wayback_machine(method: str, url: str, expected: str) -> None:
    response = functions.try_wayback_machine(url, method)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.url == expected

    # The second time, the cache will be used, simple check
    response = functions.try_wayback_machine(url, method)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.url == expected
