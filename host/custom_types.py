"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""
from types import SimpleNamespace
from typing import NamedTuple

Image = str
Images = list[Image]
Metadata = SimpleNamespace
Metadatas = list[Metadata]
Shaarli = str
Shaarlis = list[Shaarli]
Waybackdata = SimpleNamespace


class Size(NamedTuple):
    width: int
    height: int
