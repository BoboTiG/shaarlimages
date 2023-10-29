"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

from types import SimpleNamespace

SITE = SimpleNamespace(
    description="Shaarlimages, la galerie des shaarlis !",
    host="www.shaarlimages.net",
    images_per_page=50,
    title="Shaarlimages",
)
SITE.url = f"https://{SITE.host}"
