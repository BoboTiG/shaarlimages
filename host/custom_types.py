"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""
from typing import NamedTuple

Cache = dict[float, str]
Image = str
Images = list[Image]
Metadata = dict[str, str]
Shaarli = str
Shaarlis = list[Shaarli]


class Size(NamedTuple):
    width: int
    height: int
