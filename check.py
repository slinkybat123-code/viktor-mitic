"""Checks the built site in _site/ before it is published.

Run:  python build.py && python check.py
      python check.py --links   also try every link to another website (never a failure)

Fails (exit code 1) when:
  * a link points at a page of the old artorwar.com site
  * an internal link, #anchor, picture, 3D frame, font or stylesheet file is missing
  * a page breaks its own security policy: an inline style or script, an event-handler
    attribute, a resource from a site the policy does not allow, or a missing policy tag
  * a link that opens a new tab lacks rel="noopener"
"""
import glob
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from urllib.parse import unquote, urlsplit

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")
sys.path.insert(0, ROOT)
from sitegen.config import HEAD_JS, SITE_URL  # noqa: E402

ROOT_PATH = urlsplit(SITE_URL).path  # "/viktor-mitic/" on github.io, "/" on a custom domain

OLD_SITE = "artorwar.com"
REMOTE_OK = {"i.ytimg.com"}  # the only outside host pictures may come from (YouTube previews)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
# hashes that a page's script handles itself instead of matching an element id
SCRIPT_HASHES = {"available-work.html": {"painting", "sculpture", "dealers"}, "sculptures-3d.html": {"sc1", "sc2", "sc3", "sc4", "sc5"}}


def status(url):
    for method, headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, **headers})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status
        except urllib.error.HTTPError as e:
            last = e.code
        except Exception as e:  # timeouts, DNS, TLS
            last = type(e).__name__
    return last


def local(path):
    return os.path.join(OUT, *unquote(path.split("#")[0].split("?")[0]).split("/"))


def main():
    if not os.path.isdir(OUT):
        print("no _site/ folder: run python build.py first")
        return 1
    pages = sorted(glob.glob(os.path.join(OUT, "*.html")))
    problems = {"links to old-site pages": [], "missing files or anchors": [], "security policy": [], "new-tab links without noopener": []}
    external, frames = set(), 0
    ids = {}
    for path in pages:
        ids[os.path.basename(path)] = set(re.findall(r'\bid="([^"]+)"', open(path, encoding="utf-8").read()))
    for path in pages:
        name = os.path.basename(path)
        html = open(path, encoding="utf-8").read()
        add = lambda kind, what: problems[kind].append(f"{name}: {what}")

        # security policy
        if '<meta http-equiv="Content-Security-Policy"' not in html:
            add("security policy", "no Content-Security-Policy tag")
        if re.search(r"\sstyle=\"", html):
            add("security policy", "inline style attribute")
        if re.search(r"<style[\s>]", html):
            add("security policy", "inline <style> block")
        if re.search(r"\son[a-z]+=\"", html):
            add("security policy", "event-handler attribute")
        for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", html, re.S):
            if "src=" in attrs or 'type="application/ld+json"' in attrs:
                continue
            if body != HEAD_JS:
                add("security policy", "inline script that the policy does not allow")
        for a in re.findall(r"<a\s[^>]*target=\"_blank\"[^>]*>", html):
            if "noopener" not in a:
                add("new-tab links without noopener", a[:90])

        # every reference on the page
        for attr, url in re.findall(r'\b(href|src|data-src|data-base|content)="([^"]+)"', html):
            url = unescape(url)
            if attr == "content" and not url.startswith(("http", "img/")):
                continue
            if url.startswith(("data:", "mailto:", "tel:")):
                continue
            if url.startswith(SITE_URL):  # this site's own full address (canonical, sharing picture)
                url = url[len(SITE_URL):] or "index.html"
            elif url.startswith(ROOT_PATH):  # root-based links on the 404 page
                url = url[len(ROOT_PATH):] or "index.html"
            if url.startswith("#"):
                if len(url) > 1 and url[1:] not in ids[name]:
                    add("missing files or anchors", url)
                continue
            if url.startswith("http"):
                host = urlsplit(url).netloc
                if host == OLD_SITE or host.endswith("." + OLD_SITE):
                    add("links to old-site pages", url)
                elif attr in ("src", "data-src") and host not in REMOTE_OK:
                    add("security policy", "picture from " + host)
                elif attr == "href":
                    external.add(url)
                continue
            if attr == "data-base":
                continue
            target, _, frag = url.partition("#")
            target = target.split("?")[0]
            if target and not os.path.exists(local(target)):
                add("missing files or anchors", url)
                continue
            page_name = target or name
            if frag and page_name.endswith(".html") and frag not in ids.get(page_name, set()) and frag not in SCRIPT_HASHES.get(page_name, set()):
                add("missing files or anchors", url)

        # 3D frames: every frame of every turntable must exist
        base = re.search(r'data-base="([^"]+)"', html)
        for folder, turns, tilts in re.findall(r'data-folder="([^"]+)" data-w="\d+" data-h="\d+" data-u="(\d+)" data-v="(\d+)"', html):
            for v in range(int(tilts)):
                for u in range(int(turns)):
                    frames += 1
                    if not os.path.exists(local(f"{base.group(1)}{folder}/{v}_{u}.webp")):
                        add("missing files or anchors", f"3D frame {folder}/{v}_{u}.webp")

    # forwarding pages for old WordPress addresses: each must lead to a page that exists
    moved = 0
    for path in glob.glob(os.path.join(OUT, "**", "index.html"), recursive=True):
        if os.path.dirname(path) == OUT:
            continue
        moved += 1
        html = open(path, encoding="utf-8").read()
        where = os.path.relpath(path, OUT).replace(os.sep, "/")
        m = re.search(r'http-equiv="refresh" content="0; url=([^"]+)"', html)
        if '<meta http-equiv="Content-Security-Policy"' not in html:
            problems["security policy"].append(f"{where}: no Content-Security-Policy tag")
        if not m:
            problems["missing files or anchors"].append(f"{where}: no forwarding address")
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(path), unescape(m.group(1)).split("#")[0]))
        if not os.path.exists(target):
            problems["missing files or anchors"].append(f"{where}: forwards to a missing page")

    # files the stylesheet points at (fonts, the hero picture)
    css_path = os.path.join(OUT, "assets", "site.css")
    for ref in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", open(css_path, encoding="utf-8").read()):
        if not ref.startswith("data:") and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(css_path), ref))):
            problems["missing files or anchors"].append("site.css: " + ref)

    print(f"pages: {len(pages)}   forwarding pages: {moved}   3D frames: {frames}   links to other websites: {len(external)}")
    failed = False
    for kind, items in problems.items():
        print(f"{kind}: {len(items)}")
        for item in items[:25]:
            print("   ", item)
        failed = failed or bool(items)

    if "--links" in sys.argv:
        with ThreadPoolExecutor(4) as pool:
            results = list(zip(sorted(external), pool.map(status, sorted(external))))
        bad = [r for r in results if r[1] not in (200, 206)]
        print(f"links to other websites: {len(results)} tried, {len(bad)} did not answer normally (not a failure; many sites refuse automated visitors)")
        for url, code in bad:
            print("   ", code, url[:120])

    print("RESULT:", "FAILED" if failed else "OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
