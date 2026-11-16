"""Forwarding pages for the addresses of the old WordPress site.

Once artorwar.com points at this site, someone following an old link such as
artorwar.com/hot-art/artwork/rain-dance/ lands on a tiny page that sends them on to the
matching new page. GitHub Pages cannot send real redirects, so each one is an HTML page
with an instant refresh, a canonical link for search engines, and a plain link as backup.
"""
import os
from html import escape as esc

from .config import OUT, SITE_URL

OLD_PAGES = {  # old address (without slashes at the ends) -> new page
    "home": "index.html",
    "hot-art/artwork": "index.html#works",
    "hot-art/artwork/rain-dance": "rain-dance.html",
    "hot-art/artwork/art": "art-or-war.html",
    "hot-art/artwork/dealers": "dealers.html",
    "hot-art/artwork/sculptures": "sculptures.html",
    "hot-art/artwork/final-render": "sculptures-3d.html",
    "hot-art/artwork/final-render/s1": "sculptures-3d.html#sc1",
    "hot-art/artwork/final-render/sc-2": "sculptures-3d.html#sc2",
    "sculpt-2_xr-71": "sculptures-3d.html#sc2",
    "available-work": "available-work.html",
    "2023-media": "acquisitions.html",
    "publications": "books.html",
    "publications/books": "books.html",
    "publications/press-videos": "press.html",
    "channel": "press.html",
    "channel/art-or-war-live": "press.html",
    "channel/vikmik99": "press.html",
    "contact-us": "contact.html",
    "contact-us/email": "contact.html",
}


def write_redirects():
    for old, new in OLD_PAGES.items():
        rel = "../" * (old.count("/") + 1) + new
        folder = os.path.join(OUT, *old.split("/"))
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'">
<meta name="robots" content="noindex">
<title>This page has moved · Viktor Mitic</title>
<link rel="canonical" href="{esc(SITE_URL + new)}">
<meta http-equiv="refresh" content="0; url={esc(rel)}">
</head>
<body>
<p>This page has moved to <a href="{esc(rel)}">{esc(SITE_URL + new)}</a>.</p>
</body>
</html>
""")
    return len(OLD_PAGES)
