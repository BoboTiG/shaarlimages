"""
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
"""

SITE = {
    "description": "Shaarlimages, la galerie des shaarlis !",
    "display_last_n_images": 56,
    # Hostname running the galery -- to prevent re-downloading our images.
    "host": "www.shaarlimages.net",
    "title": "Shaarlimages",
    "url": "https://www.shaarlimages.net",
}

SYNC = {
    "ttl": 60 * 60 * 24,  # 24 hours
    "url": "https://www.ecirtam.net/shaarli-api/feeds?disabled=0",
}
