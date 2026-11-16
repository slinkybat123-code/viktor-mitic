"""Site-wide settings: folders, web addresses, navigation, security policy and asset fingerprints."""
import base64
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the repository folder
OUT = os.path.join(ROOT, "_site")  # the finished site; GitHub Actions publishes this folder
SITE_URL = "https://slinkybat123-code.github.io/viktor-mitic/"  # change here when the site moves to its own domain

# Pictures live in img/ inside this repository. The folder names record where each one came from:
U = "img/u/"    # artorwar.com/wp-content/uploads/ (same year/month folders)
U2 = "img/v/"   # artorwar.viktormitic.com/wp-content/uploads/2022/09/
V = "img/3d/"   # the five 3D turntables, one folder each: sc1 ... sc5, frames named {tilt}_{turn}.webp

OENO = "https://oenogallery.com/artists/viktor-mitic/"
EMAIL = "info@artorwar.com"
BLANK = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="

DATA = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))  # gallery image lists
for _group in DATA.values():
    for _it in _group:
        if _it["w"] == 4:  # a few entries were recorded without real dimensions
            _it["w"], _it["h"] = 640, 800

SERIES = [
    ("rain-dance.html", "Rain Dance"),
    ("art-or-war.html", "Art or War"),
    ("dealers.html", "Dealers"),
    ("sculptures.html", "Sculptures & installations"),
    ("sculptures-3d.html", "Sculptures in 3D"),
]
NAV = [("available-work.html", "Available"), ("news.html", "News"), ("press.html", "Press"), ("books.html", "Books"), ("cv.html", "CV")]


def stamp(name):
    """Short fingerprint of an asset file, so browsers fetch the new copy after every change."""
    with open(os.path.join(ROOT, "assets", name), "rb") as f:
        return hashlib.sha1(f.read().replace(b"\r\n", b"\n")).hexdigest()[:8]


CSS_V, JS_V = stamp("site.css"), stamp("site.js")

# The one inline script: marks the page as script-enabled before it paints, so reveal effects
# do not flash. The security policy allows exactly this script by its hash and nothing else inline.
HEAD_JS = "document.documentElement.classList.add('js')"
HEAD_JS_HASH = "sha256-" + base64.b64encode(hashlib.sha256(HEAD_JS.encode()).digest()).decode()

# Content Security Policy. GitHub Pages cannot send security headers, so the policy is set with a
# <meta> tag on every page. It allows only this site's own files plus the two video players and
# YouTube's preview images. Anything injected from elsewhere is refused by the browser.
CSP = "; ".join([
    "default-src 'self'",
    f"script-src 'self' '{HEAD_JS_HASH}'",
    "style-src 'self'",
    "img-src 'self' data: https://i.ytimg.com",
    "font-src 'self'",
    "frame-src https://www.youtube-nocookie.com https://player.vimeo.com",
    "connect-src 'none'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
    "upgrade-insecure-requests",
])
