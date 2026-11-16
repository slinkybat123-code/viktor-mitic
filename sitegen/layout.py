"""The frame around every page: <head>, navigation, footer and image viewer."""
import os
import re
from html import escape as esc
from urllib.parse import urlsplit

from . import meta
from .config import BLANK, CSP, CSS_V, EMAIL, HEAD_JS, JS_V, NAV, OUT, SERIES, SITE_URL, U

PRELOAD_FONTS = ["inter-normal-300-latin.woff2", "cormorant-garamond-normal-300-latin.woff2"]  # the faces seen first


def nav(current):
    cur = lambda href: ' aria-current="page"' if href == current else ""
    works = "".join(f'<a href="{h}"{cur(h)}>{esc(t)}</a>' for h, t in SERIES)
    rest = "".join(f'<a href="{h}"{cur(h)}>{esc(t)}</a>' for h, t in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<div id="ring" aria-hidden="true"></div>
<nav class="top" id="nav" aria-label="Primary">
  <a class="brand" href="index.html" aria-label="Viktor Mitic, Art or War: home">Art or War</a>
  <button class="burger" id="burger" aria-expanded="false" aria-controls="links">Menu</button>
  <div class="links" id="links">
    <a href="index.html#artist">The Artist</a>
    <div class="dd"><button class="dd-btn" type="button" aria-expanded="false">Works</button><span class="label dd-label">Works</span><div class="dd-menu">{works}</div></div>
    {rest}
    <a class="cta" href="contact.html"{cur("contact.html")}>Enquire</a>
  </div>
</nav>"""


def footer():
    works = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in SERIES)
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a class="brand" href="index.html">Art or War</a>
        <p class="foot-note">Viktor Mitic. Painting, sculpture and installation. Toronto and Sarasota.</p>
      </div>
      <div><h3>Works</h3><ul>{works}<li><a href="available-work.html">Available work</a></li></ul></div>
      <div><h3>Read</h3><ul>
        <li><a href="news.html">News</a></li>
        <li><a href="press.html">Press &amp; video</a></li>
        <li><a href="books.html">Books &amp; films</a></li>
        <li><a href="cv.html">Curriculum vitae</a></li>
        <li><a href="acquisitions.html">Collector acquisitions</a></li>
      </ul></div>
      <div><h3>Contact</h3><ul>
        <li><a href="contact.html">Enquire</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      </ul></div>
    </div>
    <div class="legal"><span>© 2026 Viktor Mitic. All rights reserved.</span><a href="#top">Back to top ↑</a></div>
  </div>
</footer>
<dialog id="lb" class="lbox" aria-label="Image viewer">
  <div class="lb">
    <button class="x" type="button" aria-label="Close">×</button>
    <button class="p" type="button" aria-label="Previous image">‹</button>
    <img alt="" src="{BLANK}">
    <div class="meta"><strong></strong><span></span><a class="more" href="contact.html" hidden>Enquire about this work</a></div>
    <button class="n" type="button" aria-label="Next image">›</button>
  </div>
</dialog>
<script src="assets/site.js?v={JS_V}" defer></script>"""


def page(slug, title, desc, body, og=None, preload=None):
    og = og or U + "2017/10/Diptych-10-Aug-08-sm-web.jpg"
    if not og.startswith("http"):  # sharing previews need a full web address
        og = SITE_URL + og
    pre = f'<link rel="preload" as="image" href="{preload}">\n' if preload else ""
    fonts = "".join(f'<link rel="preload" as="font" type="font/woff2" href="assets/fonts/{name}" crossorigin>\n' for name in PRELOAD_FONTS)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(og)}">
{meta.head_extra(slug, title, desc)}
<link rel="icon" href="{U}2017/11/cropped-Viktor_doc-155-32x32.jpg">
{pre}{fonts}<link rel="stylesheet" href="assets/site.css?v={CSS_V}">
<script>{HEAD_JS}</script>
</head>
<body id="top">
{nav(slug)}
{body}
{footer()}
</body>
</html>
"""
    if slug == "404.html":
        html = rooted(html)
    with open(os.path.join(OUT, slug), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return slug


def rooted(html):
    """GitHub Pages shows 404.html at whatever address was missing, however deep, so its links
    and files must start from the site root instead of the current folder."""
    root = urlsplit(SITE_URL).path  # "/viktor-mitic/" now, "/" on a custom domain
    return re.sub(r'\b(href|src|data-src|data-base)="(?!https?:|mailto:|tel:|data:|#|/)', lambda m: f'{m.group(1)}="{root}', html)
