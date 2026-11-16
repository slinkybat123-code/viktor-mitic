"""Generator for the Viktor Mitic website.

    config.py   folders, web address, navigation, asset fingerprints
    content.py  shared data tables (captions, videos, articles, films, 3D viewer settings)
    parts.py    building blocks (page headers, image tiles, lists, calls to action)
    layout.py   the frame around every page (<head>, navigation, footer, image viewer)
    meta.py     search and sharing tags, sitemap.xml, robots.txt
    redirects.py  forwarding pages for the old WordPress addresses
    pages/      one module per area of the site
"""
import os
import shutil

from . import meta, redirects
from .config import OUT, ROOT

COPY = ["assets", "img"]  # folders copied into the finished site unchanged


def build_all():
    """Build the whole site into _site/ from scratch."""
    from .pages import ALL

    if os.path.basename(OUT) != "_site":  # never wipe anything but the output folder
        raise SystemExit("unexpected output folder: " + OUT)
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    for folder in COPY:
        if os.path.isdir(os.path.join(ROOT, folder)):
            shutil.copytree(os.path.join(ROOT, folder), os.path.join(OUT, folder))
    built = [build() for build in ALL]
    listed = meta.finish(built)
    moved = redirects.write_redirects()
    print("built", len(built), "pages into _site/:", ", ".join(built))
    print(moved, "forwarding pages for old artorwar.com addresses")
    print("sitemap.xml lists", listed, "pages; robots.txt written")
    return built
