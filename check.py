"""Checks the built site.

Run:  python check.py            full check (needs internet)
      python check.py --offline  only the checks that need no network

Fails (exit code 1) when:
  * any link points at a page of the old artorwar.com site (only its image files are allowed)
  * an internal link or #anchor leads nowhere
  * an image, thumbnail or 3D frame no longer loads
Links to other websites (press articles, book shops) are reported but never fail the check,
because many news sites refuse automated visitors.
"""
import glob
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote, urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_SITE = "artorwar.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
# hashes that the page's script handles itself instead of matching an element id
SCRIPT_HASHES = {"available-work.html": {"painting", "sculpture", "dealers"}, "sculptures-3d.html": {"sc1", "sc2", "sc3", "sc4", "sc5"}}


def status(url):
    """HTTP status of a URL, trying a light request first."""
    last = "ERR"
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


def collect():
    pages = sorted(glob.glob(os.path.join(HERE, "*.html")))
    ids, refs = {}, []
    for path in pages:
        name = os.path.basename(path)
        html = open(path, encoding="utf-8").read()
        ids[name] = set(re.findall(r'\bid="([^"]+)"', html))
        for attr, url in re.findall(r'\b(href|src|data-src|content)="([^"]+)"', html):
            if attr == "content" and not url.startswith("http"):
                continue
            refs.append((name, attr, url.replace("&amp;", "&")))
        refs += [(name, "css", u) for u in re.findall(r"url\('([^']+)'\)", html)]
    return pages, ids, refs


def main():
    offline = "--offline" in sys.argv
    pages, ids, refs = collect()
    old_links, broken, assets, external = [], [], set(), set()
    for name, attr, url in refs:
        if url.startswith(("data:", "mailto:", "tel:")):
            continue
        if url.startswith("#"):
            if len(url) > 1 and url[1:] not in ids[name]:
                broken.append((name, url))
            continue
        if url.startswith("http"):
            host = urlsplit(url).netloc
            if host.endswith(OLD_SITE):
                is_file = "/wp-content/" in url
                if is_file and (attr != "href" or re.search(r"\.(jpe?g|png|webp)$", url)):
                    assets.add(url)
                elif not (attr == "href" and url.rstrip("/") == "https://" + OLD_SITE):  # preconnect hint
                    old_links.append((name, url))
            elif host.endswith(("googleapis.com", "gstatic.com", "github.io")):
                continue
            elif attr in ("src", "data-src"):
                assets.add(url)
            elif attr == "href":
                external.add(url)
            continue
        path, _, frag = url.partition("#")
        path = path.split("?")[0]
        if path and not os.path.exists(os.path.join(HERE, path)):
            broken.append((name, url))
            continue
        target = path or name
        if frag and target.endswith(".html") and frag not in ids.get(target, set()) and frag not in SCRIPT_HASHES.get(target, set()):
            broken.append((name, url))

    print(f"pages: {len(pages)}   references: {len(refs)}")
    print(f"links to old-site pages: {len(old_links)}")
    for item in old_links[:20]:
        print("   ", item)
    print(f"broken internal links: {len(broken)}")
    for item in broken[:20]:
        print("   ", item)
    failed = bool(old_links or broken)

    if not offline:
        viewer = open(os.path.join(HERE, "sculptures-3d.html"), encoding="utf-8").read()
        base = re.search(r'data-base="([^"]+)"', viewer)
        frames = []
        if base:
            for m in re.finditer(r'data-folder="([^"]+)" data-w="\d+" data-h="\d+" data-u="(\d+)" data-v="(\d+)" data-su="(\d+)" data-sv="(\d+)"', viewer):
                folder, turns, tilts, start_turn, start_tilt = m.group(1), *map(int, m.groups()[1:])
                frames += [f"{base.group(1)}{quote(folder)}/{start_tilt}_{t}.png" for t in range(turns)]
                frames += [f"{base.group(1)}{quote(folder)}/{t}_{start_turn}.png" for t in range(tilts)]
        with ThreadPoolExecutor(10) as pool:
            asset_results = list(zip(sorted(assets), pool.map(status, sorted(assets))))
            frame_results = list(zip(frames, pool.map(status, frames)))
            external_results = list(zip(sorted(external), pool.map(status, sorted(external))))
        bad_assets = [r for r in asset_results if r[1] not in (200, 206)]
        bad_frames = [r for r in frame_results if r[1] not in (200, 206)]
        bad_external = [r for r in external_results if r[1] not in (200, 206)]
        print(f"images and thumbnails: {len(asset_results)} checked, {len(bad_assets)} failing")
        for url, code in bad_assets[:30]:
            print("   ", code, url)
        print(f"3D frames: {len(frame_results)} checked, {len(bad_frames)} failing")
        for url, code in bad_frames[:30]:
            print("   ", code, url)
        print(f"links to other websites: {len(external_results)} checked, {len(bad_external)} did not answer (not a failure)")
        for url, code in bad_external:
            print("   ", code, url[:120])
        failed = failed or bool(bad_assets or bad_frames)

    print("RESULT:", "FAILED" if failed else "OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
