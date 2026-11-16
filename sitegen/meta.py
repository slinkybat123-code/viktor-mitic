"""Search-engine and sharing plumbing: canonical addresses, sharing tags, structured data,
sitemap.xml and robots.txt. layout.page() calls head_extra() for every page; build_all()
calls finish() once at the end."""
import json
import os
from html import escape as esc

from .config import EMAIL, OUT, SITE_URL

SITE_NAME = "Viktor Mitic"
NOINDEX = {"404.html"}

# Page name and parent used for breadcrumbs in search results.
PAGES = {
    "index.html": ("Home", None),
    "rain-dance.html": ("Rain Dance", "index.html"),
    "art-or-war.html": ("Art or War", "index.html"),
    "dealers.html": ("Dealers", "index.html"),
    "sculptures.html": ("Sculptures & installations", "index.html"),
    "sculptures-3d.html": ("Sculptures in 3D", "sculptures.html"),
    "available-work.html": ("Available work", "index.html"),
    "news.html": ("News", "index.html"),
    "press.html": ("Press & video", "index.html"),
    "books.html": ("Books & films", "index.html"),
    "cv.html": ("Curriculum vitae", "index.html"),
    "acquisitions.html": ("Collector acquisitions", "index.html"),
    "contact.html": ("Contact", "index.html"),
}

PERSON = {
    "@type": "Person",
    "@id": SITE_URL + "#viktor-mitic",
    "name": "Viktor Mitic",
    "jobTitle": "Painter and sculptor",
    "url": SITE_URL,
    "email": EMAIL,
    "sameAs": ["https://en.wikipedia.org/wiki/Viktor_Mitic"],
    "alumniOf": [
        {"@type": "CollegeOrUniversity", "name": "University of Toronto"},
        {"@type": "CollegeOrUniversity", "name": "Sheridan College"},
    ],
}


def url_of(slug):
    return SITE_URL + ("" if slug == "index.html" else slug)


def _crumbs(slug):
    trail = []
    while slug:
        name, parent = PAGES[slug]
        trail.append((name, url_of(slug)))
        slug = parent
    trail.reverse()
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(trail, 1)],
    }


def structured_data(slug, title, desc):
    if slug == "index.html":
        graph = [
            {"@type": "WebSite", "@id": SITE_URL + "#site", "url": SITE_URL, "name": SITE_NAME, "description": desc,
             "about": {"@id": PERSON["@id"]}},
            PERSON,
        ]
    else:
        graph = [
            {"@type": "ContactPage" if slug == "contact.html" else "WebPage", "url": url_of(slug), "name": title, "description": desc,
             "isPartOf": {"@id": SITE_URL + "#site"}, "about": {"@id": PERSON["@id"]}},
            _crumbs(slug),
        ]
    return {"@context": "https://schema.org", "@graph": graph}


def head_extra(slug, title, desc):
    """Extra <head> tags for one page: canonical address, sharing tags, structured data."""
    if slug in NOINDEX:
        return '<meta name="robots" content="noindex">'
    data = json.dumps(structured_data(slug, title, desc), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return "\n".join([
        f'<link rel="canonical" href="{esc(url_of(slug))}">',
        f'<meta property="og:url" content="{esc(url_of(slug))}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{esc(SITE_NAME)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<script type="application/ld+json">{data}</script>',
    ])


def finish(built):
    """Write sitemap.xml and robots.txt for the pages that were built."""
    pages = [s for s in built if s not in NOINDEX]
    urls = "\n".join(f"  <url><loc>{esc(url_of(s))}</loc></url>" for s in pages)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    return len(pages)
