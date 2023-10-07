"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from types import SimpleNamespace

SITE = SimpleNamespace(
    description="Shaarlimages, la galerie des shaarlis !",
    display_last_n_images=56,
    host="www.shaarlimages.net",
    title="Shaarlimages",
)
SITE.url = f"https://{SITE.host}"
