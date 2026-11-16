"""Small building blocks shared by the pages: headers, image tiles, lists, calls to action."""
from html import escape as esc
from urllib.parse import quote

from .config import DATA, SERIES, U, U2
from .content import DEALER_NAMES, FILMS


def by_file(group, name):
    for it in DATA[group]:
        if name in it["f"]:
            return it
    raise KeyError(name)


def phero(crumbs, label, h1, intro, img=None, alt=""):
    c = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' if h else f"<li>{esc(t)}</li>" for h, t in crumbs)
    pic = f'<img src="{img}" alt="{esc(alt)}" fetchpriority="high">' if img else ""
    cls = "phero" if img else "phero plain"
    return f"""<header class="{cls}">
  {pic}
  <div class="wrap">
    <ol class="crumbs" aria-label="Breadcrumb">{c}</ol>
    <span class="label">{esc(label)}</span>
    <h1>{h1}</h1>
    <p class="intro">{intro}</p>
  </div>
</header>"""


def local_name(name):
    """File name as stored in img/: the copyright sign in a few photo names is written as a plain c."""
    return name.replace("©", "c")


def src(path):
    """Address of an image: entries from data/site.json are relative to U, extras are already complete."""
    return path if path.startswith(("http", "img/")) else U + path


def extra(name, w, h):
    """An image from the artist's second site, shaped like the entries in data/site.json."""
    url = U2 + quote(local_name(name))
    return {"f": url, "t": url, "l": url, "w": w, "h": h}


def shots(items, group, cls=""):
    """A row of small photographs at their natural size. items: (file, width, height, title)."""
    out = ""
    for name, w, h, title in items:
        it = extra(name, w, h)
        out += (f'<button type="button" {lb_attrs(it, group, title=title, alt=title)} aria-label="Enlarge {esc(title)}">'
                f'<img loading="lazy" src="{it["t"]}" width="{w}" height="{h}" alt="{esc(title)}"></button>')
    return f'<div class="shots{" " + cls if cls else ""}">{out}</div>'


def lb_attrs(it, group, title="", cap="", alt="", enq=""):
    a = f'data-lb="{group}" data-src="{src(it["l"])}" data-alt="{esc(alt)}"'
    if title:
        a += f' data-title="{esc(title)}"'
    if cap:
        a += f' data-cap="{esc(cap)}"'
    if enq:
        a += f' data-enq="{esc(enq)}"'
    return a


def tile(it, group, alt, title="", cap="", n=0):
    label = title or f"image {n}"
    fc = ""
    if title or cap:
        fc = "<figcaption>" + (f"<strong>{esc(title)}</strong>" if title else "") + esc(cap) + "</figcaption>"
    cls = "tile small" if it["w"] < 300 else "tile"  # small originals are shown at their own size, not stretched
    return (f'<figure class="{cls}"><button type="button" {lb_attrs(it, group, title, cap, alt)} aria-label="Enlarge {esc(label)}">'
            f'<img loading="lazy" src="{src(it["t"])}" width="{it["w"]}" height="{it["h"]}" alt="{esc(alt)}"></button>{fc}</figure>')


def strip(group, picks, alt):
    out = []
    for i, (name, wide) in enumerate(picks, 1):
        it = by_file(group, name)
        out.append(f'<button type="button"{" class=wide" if wide else ""} {lb_attrs(it, "strip-" + group, alt=alt)} aria-label="Enlarge image {i} of {len(picks)}">'
                   f'<img loading="lazy" src="{src(it["t"])}" alt="{esc(alt)}, view {i}"></button>')
    return f'<div class="strip">{"".join(out)}</div>'


def pager(slug):
    order = [h for h, _ in SERIES] + ["available-work.html"]
    names = dict(SERIES + [("available-work.html", "Available work")])
    i = order.index(slug)
    prev = f'<a class="more back" href="{order[i-1]}">{esc(names[order[i-1]])}</a>' if i > 0 else '<a class="more back" href="index.html#works">All works</a>'
    nxt = f'<a class="more" href="{order[i+1]}">{esc(names[order[i+1]])}</a>' if i + 1 < len(order) else ""
    return f'<div class="wrap"><div class="pager">{prev}{nxt}</div></div>'


def cta(h2, text, topic="", alt=("available-work.html", "View available work")):
    href = "contact.html" + (f"?topic={quote(topic)}" if topic else "")
    alt_href, alt_text = alt
    return f"""<section class="cta-band tight">
  <div class="wrap">
    <span class="label">Enquire</span>
    <h2>{h2}</h2>
    <p>{text}</p>
    <div class="actions"><a class="btn fill" href="{href}">Contact the studio</a><a class="btn ghost" href="{alt_href}">{alt_text}</a></div>
  </div>
</section>"""


def rows(items):
    return '<ul class="rows">' + "".join(
        f'<li><span class="yr">{esc(y)}</span><p>{t}{f"<span>{esc(s)}</span>" if s else ""}</p></li>' for y, t, s in items) + "</ul>"


def lookup(table, f):
    return next((v for k, v in table.items() if k in f), ("", ""))


def dealer_name(f):
    return next((v for k, v in DEALER_NAMES.items() if k in f), "")


def films_html():
    return '<ul>' + "".join(f'<li><span class="t">{esc(t)}</span><span class="d">{esc(d)}</span><span class="y">{y}</span></li>' for t, d, y in FILMS) + "</ul>"


def avail_cat(i):
    if 6 <= i <= 14:
        return "dealers"
    if i in (1, 2, 38, 39, 40) or 16 <= i <= 35:
        return "painting"
    return "sculpture"
