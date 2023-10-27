"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""


class DisparoisseError(Exception):
    def __str__(self) -> str:
        return "Cannot found the resource on internet anymore."
