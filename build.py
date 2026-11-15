"""Builds every page of the Viktor Mitic site.

Run:  python build.py
Reads data/site.json (image lists) and writes the .html files next to this script.
Edit the text in this file, run it again, then commit and push.
"""
import json, os, re, sys
from html import escape as esc
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import site_meta  # noqa: E402  canonical addresses, sharing tags, sitemap (see site_meta.py)
U = "https://artorwar.com/wp-content/uploads/"          # images are still served from here
V = "https://artorwar.com/wp-content/themes/customizr/"  # 3D turntable files
EMAIL = "info@artorwar.com"
DATA = json.load(open(os.path.join(HERE, "data", "site.json"), encoding="utf-8"))
for group in DATA.values():
    for it in group:
        if it["w"] == 4:
            it["w"], it["h"] = 640, 800
BLANK = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="


def stamp(name):
    """Short fingerprint of an asset file, so browsers fetch the new copy after every change."""
    import hashlib
    with open(os.path.join(HERE, "assets", name), "rb") as f:
        return hashlib.sha1(f.read().replace(b"\r\n", b"\n")).hexdigest()[:8]


CSS_V, JS_V = stamp("site.css"), stamp("site.js")

SERIES = [
    ("rain-dance.html", "Rain Dance"),
    ("art-or-war.html", "Art or War"),
    ("dealers.html", "Dealers"),
    ("sculptures.html", "Sculptures & installations"),
    ("sculptures-3d.html", "Sculptures in 3D"),
]
NAV = [("available-work.html", "Available"), ("press.html", "Press"), ("books.html", "Books"), ("cv.html", "CV")]


def by_file(group, name):
    for it in DATA[group]:
        if name in it["f"]:
            return it
    raise KeyError(name)


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
    <div class="dd"><button class="dd-btn" type="button" aria-expanded="false">Works</button><div class="dd-menu">{works}</div></div>
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
        <p style="max-width:300px;color:var(--muted)">Viktor Mitic. Painting, sculpture and installation. Toronto and Sarasota.</p>
      </div>
      <div><h3>Works</h3><ul>{works}<li><a href="available-work.html">Available work</a></li></ul></div>
      <div><h3>Read</h3><ul>
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
    pre = f'<link rel="preload" as="image" href="{preload}">\n' if preload else ""
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og}">
{site_meta.head_extra(slug, title, desc)}
<link rel="icon" href="{U}2017/11/cropped-Viktor_doc-155-32x32.jpg">
{pre}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css?v={CSS_V}">
<script>document.documentElement.classList.add('js')</script>
</head>
<body id="top">
{nav(slug)}
{body}
{footer()}
</body>
</html>
"""
    with open(os.path.join(HERE, slug), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return slug


def phero(crumbs, label, h1, intro, img=None, alt=""):
    c = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' if h else f"<li>{esc(t)}</li>" for h, t in crumbs)
    pic = f'<img src="{img}" alt="{esc(alt)}">' if img else ""
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


def lb_attrs(it, group, title="", cap="", alt="", enq=""):
    a = f'data-lb="{group}" data-src="{U}{it["l"]}" data-alt="{esc(alt)}"'
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
    return (f'<figure class="tile"><button type="button" {lb_attrs(it, group, title, cap, alt)} aria-label="Enlarge {esc(label)}">'
            f'<img loading="lazy" src="{U}{it["t"]}" width="{it["w"]}" height="{it["h"]}" alt="{esc(alt)}"></button>{fc}</figure>')


def strip(group, picks, alt):
    out = []
    for i, (name, wide) in enumerate(picks, 1):
        it = by_file(group, name)
        out.append(f'<button type="button"{" class=wide" if wide else ""} {lb_attrs(it, "strip-" + group, alt=alt)} aria-label="Enlarge image {i} of {len(picks)}">'
                   f'<img loading="lazy" src="{U}{it["t"]}" alt="{esc(alt)}, view {i}"></button>')
    return f'<div class="strip">{"".join(out)}</div>'


def pager(slug):
    order = [h for h, _ in SERIES] + ["available-work.html"]
    names = dict(SERIES + [("available-work.html", "Available work")])
    i = order.index(slug)
    prev = f'<a class="more back" href="{order[i-1]}">{esc(names[order[i-1]])}</a>' if i > 0 else '<a class="more back" href="index.html#works">All works</a>'
    nxt = f'<a class="more" href="{order[i+1]}">{esc(names[order[i+1]])}</a>' if i + 1 < len(order) else ""
    return f'<div class="wrap"><div class="pager">{prev}{nxt}</div></div>'


def cta(h2, text, topic=""):
    href = "contact.html" + (f"?topic={quote(topic)}" if topic else "")
    return f"""<section class="cta-band tight">
  <div class="wrap">
    <span class="label">Enquire</span>
    <h2>{h2}</h2>
    <p>{text}</p>
    <div class="actions"><a class="btn fill" href="{href}">Contact the studio</a><a class="btn ghost" href="available-work.html">View available work</a></div>
  </div>
</section>"""


def rows(items):
    return '<ul class="rows">' + "".join(
        f'<li><span class="yr">{esc(y)}</span><p>{t}{f"<span>{esc(s)}</span>" if s else ""}</p></li>' for y, t, s in items) + "</ul>"


# ------------------------------------------------------------------ landing page
def build_index():
    rain_picks = [(f"Oct-2008_{n}.", False) for n in (11, 13, 15, 17, 19, 21)] + [("22jun08-007", True)] + \
                 [(f"M00{n}-doc", False) for n in ("02", "06", "10", "20", "35", "45")]
    war_picks = [("Viktor_doc-204", True), ("Viktor_doc-157", False), ("Viktor_doc-122", True), ("IMG_3325", False),
                 ("Viktor_doc-10", False), ("MiticViktor", False), ("Triptych-V1", True), ("Beiber-mstr", False)]
    cards = [
        ("c1", "rain-dance.html", "2017/10/Viktor-Mitic-Oct-2008_14.jpg", "Rain Dance, painting by Viktor Mitic", "Painting", "Rain Dance",
         "Canvases painted outdoors in showers and storms at sites across North America, with the rain doing part of the work.", "View the series"),
        ("c2", "art-or-war.html", "2017/11/Viktor_doc-157-1024x1015.jpg", "Bullet-hole portrait from Art or War by Viktor Mitic", "Bullet-hole paintings", "Art or War",
         "Icons and portraits outlined with live rounds.", "View the series"),
        ("c3", "dealers.html", "2017/10/Viktor-14Sep09_0047-prnt.jpg", "Portrait from the Dealers series by Viktor Mitic", "Ink on gold leaf", "Dealers",
         "Thirty-six portraits of Toronto's art dealers.", "View the series"),
        ("c4", "sculptures.html", "2022/09/IMG_20220411_104605-1024x768.jpg", "Outdoor sculpture by Viktor Mitic", "Sculpture", "Sculptures &amp; Installations",
         "Steel, gold, cut aluminum, and a school bus.", "View the work"),
        ("c5", "sculptures-3d.html", "2017/12/Ax11-1024x683.jpg", "Painted aluminum wall sculpture by Viktor Mitic", "Interactive", "Sculptures in 3D",
         "Five pieces you can click and drag to turn.", "Open the viewer"),
    ]
    cards_html = "".join(
        f'<a class="card {c} rv" href="{h}"><img loading="lazy" alt="{esc(a)}" src="{U}{img}">'
        f'<div class="cap"><span class="label">{l}</span><h3>{t}</h3><p>{p}</p><span class="go">{go} →</span></div></a>'
        for c, h, img, a, l, t, p, go in cards)
    places = [("Heartland-Port-Moody", "Heartland", "Port Moody, British Columbia"), ("fragment-doha", "Fragment", "Doha, Qatar"),
              ("CELESTIAL", "Celestial", "Sonoma, California"), ("red-gold-gold-totem", "Gold Totem", "Englewood, New Jersey")]
    places_html = ""
    for name, t, where in places:
        it = by_file("media", name)
        places_html += (f'<a class="place rv" href="acquisitions.html"><img loading="lazy" alt="{t}, sculpture by Viktor Mitic, {where}" src="{U}{it["t"]}">'
                        f'<div class="cap"><h3>{t}</h3><span class="where">{where}</span></div></a>')
    chips = "".join(f'<a class="chip" href="sculptures-3d.html#sc{i}">SC {i}</a>' for i in range(1, 6))
    timeline = [
        ("1995", "Paints a portrait of Prime Minister Jean Chrétien, unveiled at the prime minister's office in Ottawa."),
        ("2008", "<em>Hole Jesus</em> is shown at Trias Gallery in Toronto. <em>Galaxy</em> is shown at Muramatsu Gallery in Tokyo."),
        ("2009", "The Beaverbrook Art Gallery commissions <em>Blasted Beaverbrook</em>. <em>Dealers</em>, 36 portraits of Toronto's art dealers, opens at Odon Wagner Contemporary."),
        ("2010", "<em>Art or War</em> opens at Gallery Moos in Toronto, with a book and a short film. The work travels to the Armory Show in New York and Art Chicago."),
        ("2011", "Fourfront Editions publishes <em>Rain Dance</em> as a book and film."),
        ("2013", "<em>Incident</em> tours to Washington, D.C. during the U.S. gun debates."),
        ("2014", "The documentary <em>Gun Porn</em>, on how the bullet paintings are made, screens at Hot Docs."),
        ("2015", "Artisan Works in Rochester, New York, exhibits the 58 works it acquired. <em>Blasted Guernica</em> goes on permanent view in Markham, Ontario."),
        ("2018", "<em>Lyric Star</em> and <em>The Music Garage</em> are installed at the Marriott Hotel in Markham. The Biggs Museum of American Art adds a work to its collection."),
        ("2021", "<em>Heartland</em> becomes public art in Port Moody, British Columbia."),
        ("2023", "Sculptures enter private collections in Sonoma and New Jersey. A second studio is working in Sarasota, Florida."),
    ]
    tl = "".join(f'<li class="rv"><span class="yr">{y}</span><p>{t}</p></li>' for y, t in timeline)
    press = [
        ("https://www.theglobeandmail.com/arts/viktor-mitic-from-the-barrel-of-a-gun/article4213687/", "The Globe and Mail", "From the barrel of a gun"),
        ("https://www.cbc.ca/news/entertainment/bullet-holes-stud-viktor-mitic-s-pop-art-1.1403936", "CBC News", "Bullet holes and pop art"),
        ("https://www.washingtonpost.com/local/bullet-riddled-school-bus-debuts-in-dc-as-a-rolling-art-exhibit/2013/04/07/cb06bb2c-9fa9-11e2-9c03-6952ff305f35_story.html", "The Washington Post", "Incident arrives in Washington, D.C. · 2013"),
        ("https://www.huffpost.com/entry/art-against-guns-viktor-mitic-fights-back-with-bullet-riddled-bus-artwork_n_3036727", "HuffPost", "The bullet-riddled bus · 2013"),
        ("https://www.thestar.com/news/gta/bullet-riddled-painting-of-justin-bieber-missing-after-tiff-debut/article_a278af2e-7416-57b7-a84a-3ac78af6173c.html", "Toronto Star", "The Bieber painting goes missing after TIFF · 2017"),
    ]
    press_html = "".join(f'<li><a href="{h}" target="_blank" rel="noopener"><span class="o">{o}</span><span class="s">{s}</span><span class="r">Read ↗</span></a></li>' for h, o, s in press)
    hero = U + "2017/10/Diptych-10-Aug-08-sm-web.jpg"
    body = f"""<header class="hero">
  <div class="hero-img" id="heroImg" style="background-image:url('{hero}')"></div>
  <canvas id="rain" aria-hidden="true"></canvas>
  <div class="hero-body">
    <span class="label">Painting · Sculpture · Installation</span>
    <h1>Viktor Mitic<span>Rain Dance &nbsp;·&nbsp; Art or War</span></h1>
    <p>A painter and sculptor who lets storms finish his canvases, draws portraits with live ammunition, and builds in steel, gold and painted aluminum.</p>
    <div class="actions">
      <a class="btn fill" href="#works">Explore the work</a>
      <a class="btn ghost" href="available-work.html">Available work</a>
    </div>
  </div>
  <div class="scroll" aria-hidden="true">Scroll</div>
</header>

<div class="cities">
  <span class="label">Exhibited in</span>
  <ul><li>Toronto</li><li>Tokyo</li><li>New York</li><li>Chicago</li><li>Washington, D.C.</li><li>Montreal</li></ul>
</div>

<main id="main">
<section id="artist">
  <div class="wrap">
    <div class="artist">
      <div class="rv">
        <span class="label">The Artist</span>
        <h2>Creation, close to <em>destruction.</em></h2>
      </div>
      <div class="rv">
        <p class="lead">Viktor Mitic is a Serbian-born Canadian painter and sculptor with studios in Toronto and Sarasota, Florida.</p>
        <p>He grew up in the former Yugoslavia, where national service taught him to handle firearms, and later moved to Canada. He holds a Bachelor of Fine Art from the University of Toronto and a Fine Arts Diploma from Sheridan College.</p>
        <p>His practice runs in several directions at once. The Rain Dance paintings are made outdoors and left to the weather. The Art or War paintings are outlined in bullet holes, a way of turning a tool built for harm into one that makes an image. His sculptures range from cut aluminum finished in car paint to stainless steel plated in 24k gold.</p>
        <p>Mitic says the gun works are meant to start a conversation about gun violence, and he leaves the conclusions to the viewer.</p>
        <a class="more" href="cv.html">Curriculum vitae</a>
        <a class="more" href="acquisitions.html">Collector acquisitions</a>
      </div>
    </div>
    <div class="studio rv">
      <img loading="lazy" alt="A sculpture prototype in Viktor Mitic's studio" src="{U}2023/02/xox-prototype-studio-1024x497.jpg">
      <span class="label">In the studio</span>
    </div>
  </div>
</section>

<section id="works" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head rv"><h2>Bodies <em>of work</em></h2><span class="label">Five series</span></div>
    <div class="grid">{cards_html}</div>
  </div>
</section>

<section class="feature" id="rain-dance">
  <div class="wrap split">
    <div class="rv">
      <span class="label">Series · Painting</span>
      <h2>Rain <em>Dance</em></h2>
      <a class="more" href="rain-dance.html">See the full series</a>
    </div>
    <div class="rv">
      <p>Every painting in the series was made outside, in the rain. Natural elements mix with traditional painting mediums, so the weather on the day decides part of the picture.</p>
      <p>Mitic found the method by accident and calls it acid rain painting. <em>Galaxy</em> (2008), first shown at Muramatsu Gallery in Tokyo, is on the cover of the <em>Rain Dance</em> book.</p>
    </div>
  </div>
  <span class="label hint rv">Drag or scroll · select to enlarge</span>
  {strip("rain", rain_picks, "Rain Dance, painting by Viktor Mitic")}
</section>

<section id="art-or-war">
  <div class="wrap split">
    <div class="rv">
      <span class="label">Series · Bullet-hole paintings</span>
      <h2>Art <em>or War</em></h2>
      <p>Mitic paints the image, then outlines it with gunfire. His subjects include Gandhi, John F. Kennedy and John Lennon, people whose lives were ended by guns, alongside Jesus, Marilyn Monroe and Chairman Mao.</p>
      <p><em>Hole Jesus</em> (2008) was made with .22-calibre rounds. <em>Blasted Beaverbrook</em> (2009) was commissioned by the Beaverbrook Art Gallery in New Brunswick. <em>Blasted Guernica</em>, his answer to Picasso, is on permanent view at the Remington Contemporary Art Museum in Markham, Ontario.</p>
      <a class="more" href="art-or-war.html">See the full series</a>
    </div>
    <blockquote class="quote rv">“Guns were made to destroy, but can they be used to create something beautiful?”<cite>Viktor Mitic</cite></blockquote>
  </div>
  <span class="label hint rv">Drag or scroll · select to enlarge</span>
  {strip("war", war_picks, "Bullet-hole painting from Art or War by Viktor Mitic")}
</section>

<section class="banner" id="incident" aria-labelledby="incident-h">
  <img loading="lazy" alt="Incident, a bullet-riddled school bus by Viktor Mitic" src="{U}2017/10/cropped-incident-c-1-1024x495.jpg">
  <div class="wrap rv">
    <span class="label">Installation · 2013</span>
    <h2 id="incident-h">Incident</h2>
    <p>A school bus riddled with bullet holes. It premiered at Nuit Blanche in Toronto and toured to Washington, D.C. in April 2013, at the height of the U.S. gun debates. It is now in the permanent collection of Artisan Works in Rochester, New York.</p>
    <div class="row">
      <a class="more" href="sculptures.html#incident">About the work</a>
      <a class="more" href="press.html">Press and video</a>
    </div>
  </div>
</section>

<section id="sculpture">
  <div class="wrap">
    <div class="split">
      <div class="rv">
        <span class="label">Sculpture &amp; installation</span>
        <h2>Shape <em>in space</em></h2>
        <a class="more" href="sculptures.html">All sculptures</a>
      </div>
      <div class="rv">
        <p>The early sculptures are cut from aluminum and sprayed in car paint, with a post-Pop energy. Recent pieces grow from paint splatters found on the studio floor and become totems in stainless steel, bronze and 24k gold, some of them 16 feet tall.</p>
        <p>They now stand in public and private collections from Port Moody, British Columbia, to Doha and Colombo.</p>
      </div>
    </div>
    <div class="places">{places_html}</div>
    <div class="chips rv"><span class="label">Turn them in 3D</span>{chips}</div>
  </div>
</section>

<section class="feature" id="timeline">
  <div class="wrap">
    <div class="sec-head rv"><h2>Selected <em>history</em></h2><a class="more" href="cv.html">Full CV</a></div>
    <ul class="timeline">{tl}</ul>
  </div>
</section>

<section id="books">
  <div class="wrap">
    <div class="sec-head rv"><h2>Books <em>&amp; films</em></h2><a class="more" href="books.html">All publications</a></div>
    <div class="books rv">
      <a class="book" href="books.html#dealers"><span class="n">01 · 2009</span><h3>Dealers</h3><p>The 36 dealer portraits, with an introduction by Gary Michael Dault. Tightrope Books.</p><span class="more" aria-hidden="true">About the book</span></a>
      <a class="book" href="books.html#art-or-war"><span class="n">02 · 2010</span><h3>Art or War</h3><p>The bullet-hole paintings, with an introduction by Jim Nason. Tightrope Books.</p><span class="more" aria-hidden="true">About the book</span></a>
      <a class="book" href="books.html#rain-dance"><span class="n">03 · 2011</span><h3>Rain Dance</h3><p>Reproductions of the rain paintings, published with a DVD. Fourfront Editions.</p><span class="more" aria-hidden="true">About the book</span></a>
    </div>
  </div>
</section>

<section class="feature" id="press">
  <div class="wrap">
    <div class="sec-head rv"><h2>In the <em>press</em></h2><span class="label">Selected coverage</span></div>
    <ul class="press rv">{press_html}</ul>
    <div class="press-foot rv"><a class="more" href="press.html">All press and video</a></div>
  </div>
</section>

<section class="collect" id="collect">
  <div class="wrap">
    <span class="label rv">Collect</span>
    <h2 class="rv">Bring the storm home</h2>
    <p class="rv">Original paintings and sculptures are available to collectors and dealers.</p>
    <div class="actions rv" style="margin-top:26px">
      <a class="btn fill" href="available-work.html">View available work</a>
      <a class="btn ghost" href="contact.html">Enquire</a>
    </div>
    <div class="tiles rv">
      <a href="acquisitions.html"><span class="label">News</span><h3>Collector acquisitions</h3><span class="sub">Sonoma, Port Moody, New Jersey</span></a>
      <a href="cv.html"><span class="label">About</span><h3>Curriculum vitae</h3><span class="sub">Public art, collections, shows</span></a>
      <a href="press.html"><span class="label">Media</span><h3>Press &amp; video</h3><span class="sub">Articles and television</span></a>
    </div>
  </div>
</section>
</main>"""
    return page("index.html", "Viktor Mitic · Art or War",
                "Viktor Mitic, painter and sculptor: Rain Dance paintings made in the rain, Art or War bullet-hole paintings, Dealers, sculpture and installations.",
                body, preload=hero)


# ------------------------------------------------------------------ series pages
def build_rain():
    g = "".join(tile(it, "rain", "Rain Dance, painting by Viktor Mitic", n=i) for i, it in enumerate(DATA["rain"], 1))
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Rain Dance")], "Series · Painting", "Rain Dance",
                 "Paintings made outdoors, in the rain, at sites across North America.",
                 U + "2017/10/Diptych-10-Aug-08-sm-web.jpg", "Rain Dance diptych by Viktor Mitic") + f"""
<main id="main">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv"><span class="label">The process</span><h2>Weather as a <em>collaborator</em></h2></div>
    <div class="rv prose">
      <p>In Rain Dance, Mitic mixes natural elements with traditional painting mediums. Each canvas was made outside while it rained, so the weather on the day shaped the result as much as the brush did.</p>
      <p>He came to the method by accident and calls it acid rain painting: non-representational paintings on canvas that the environment helps to make. He has said he enjoys rebuilding structures that nature has erased.</p>
      <p><em>Galaxy</em> (2008) was shown at Muramatsu Gallery in Tokyo and later sold at a charity auction in Toronto to a private collector. It is on the cover of the <em>Rain Dance</em> book.</p>
      <a class="more" href="books.html#rain-dance">The book and film</a>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>The <em>paintings</em></h2><span class="label">{len(DATA["rain"])} works · select to enlarge</span></div>
    <div class="gal">{g}</div>
  </div>
</section>
{cta("Ask about Rain Dance", "For availability, prices or exhibition loans, write to the studio.", "Available work")}
{pager("rain-dance.html")}
</main>"""
    return page("rain-dance.html", "Rain Dance · Viktor Mitic", "Rain Dance: paintings by Viktor Mitic made outdoors in the rain across North America.", body)


def build_war():
    titles = {"Viktor-hirez": "Blasted Guernica", "cropped-incident-c": "Incident"}
    g = ""
    for i, it in enumerate(DATA["war"], 1):
        t = next((v for k, v in titles.items() if k in it["f"]), "")
        g += tile(it, "war", (t + ", " if t else "") + "work by Viktor Mitic from Art or War", title=t, n=i)
    notable = [
        ("2008", "<em>Hole Jesus</em>", "Made with .22-calibre rounds. Shown at Trias Gallery, Toronto. Private collection."),
        ("2008", "<em>Screw Harper</em>", "A portrait of Prime Minister Stephen Harper made of screws. Private collection."),
        ("2009", "<em>Blasted Beaverbrook</em>", "Commissioned by the Beaverbrook Art Gallery, Fredericton, New Brunswick. Permanent collection."),
        ("2013", "<em>Incident</em>", "A shot-out school bus. Nuit Blanche, Toronto, and Washington, D.C. Permanent collection, Artisan Works, Rochester, New York."),
        ("2015", "<em>Blasted Guernica</em>", "A shot-up version of Picasso's Guernica. Remington Contemporary Art Museum, Markham, Ontario."),
    ]
    shows = [
        ("2010", "Gallery Moos, Toronto", "Art or War"), ("2010", "The Armory Show, New York", "Courtesy of ADAC"),
        ("2010", "Art Chicago, Chicago", "Courtesy of ADAC"), ("2011", "Gallery Moos, Toronto", ""),
        ("2013", "George Mason University, Fairfax, Virginia", ""), ("2015", "Artisan Works, Rochester, New York", "58 works"),
    ]
    hero = by_file("war", "Viktor-hirez")
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Art or War")], "Series · Bullet-hole paintings", "Art or War",
                 "Portraits and icons, painted and then outlined with live ammunition.", U + hero["f"], "Blasted Guernica by Viktor Mitic") + f"""
<main id="main">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv">
      <span class="label">The idea</span>
      <h2>Can a gun <em>make</em> something?</h2>
      <blockquote class="quote" style="margin-top:36px">“Guns were made to destroy, but can they be used to create something beautiful?”<cite>Viktor Mitic</cite></blockquote>
    </div>
    <div class="rv prose">
      <p>Mitic starts from a history of sacred places and symbols being attacked. He points to the giant Buddhas of Bamiyan, destroyed in 2001, and to twelfth-century frescoes in Kosovo defaced by gunfire.</p>
      <p>His answer is to turn the weapon around. He believes the impulses to create and to destroy sit close together, an idea he traces to the Upanishads, and he uses one to do the work of the other.</p>
      <p>He paints the image first, then outlines it with bullets. A friend, a writer, coined the name for the result: bullet hole paintings. The subjects include Gandhi, John F. Kennedy and John Lennon, whose lives were ended by guns, as well as Jesus, Marilyn Monroe, John Wayne and Chairman Mao. The Lennon portrait was made with the same model of gun that killed him.</p>
      <p>Mitic has said he does not think guns should exist. He does not call himself an activist, and leaves it to the viewer to decide what to do about them.</p>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>The <em>paintings</em></h2><span class="label">{len(DATA["war"])} works · select to enlarge</span></div>
    <div class="gal">{g}</div>
  </div>
</section>
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Notable <em>works</em></h2></div>
    {rows(notable)}
    <div class="sec-head sm rv" style="margin-top:clamp(56px,8vw,100px)"><h2>Where it was <em>shown</em></h2><a class="more" href="cv.html">Full CV</a></div>
    {rows([(y, esc(t), s) for y, t, s in shows])}
    <div class="actions"><a class="more" href="books.html#art-or-war">The book and films</a><a class="more" href="press.html">Press and video</a></div>
  </div>
</section>
{cta("Ask about Art or War", "For availability, commissions or exhibition loans, write to the studio.", "Available work")}
{pager("art-or-war.html")}
</main>"""
    return page("art-or-war.html", "Art or War · Viktor Mitic", "Art or War: Viktor Mitic's bullet-hole paintings, including Hole Jesus, Blasted Beaverbrook and Blasted Guernica.", body, og=U + hero["l"])


DEALER_NAMES = {"0096-prnt": "Jamie Angell, Angell Gallery", "0082-prnt": "Christopher Cutts, Christopher Cutts Gallery",
                "0064-prnt": "Olga Korper, Olga Korper Gallery", "0173-prnt-1": "Odon Wagner, Odon Wagner Gallery"}


def dealer_name(f):
    return next((v for k, v in DEALER_NAMES.items() if k in f), "")


def build_dealers():
    g = ""
    for i, it in enumerate(DATA["dealers"], 1):
        t = dealer_name(it["f"])
        g += tile(it, "dealers", (t + ". " if t else "") + "Portrait from Dealers by Viktor Mitic, Japanese ink on gold leaf", title=t, n=i)
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Dealers")], "Series · Japanese ink on gold leaf", "Dealers",
                 "Thirty-six portraits of Toronto's art dealers.") + f"""
<main id="main">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv"><span class="label">The idea</span><h2>The artist promotes <em>the dealer</em></h2></div>
    <div class="rv prose">
      <p>Dealers is a series of portraits in Japanese ink on gold leaf. It opened at Odon Wagner Contemporary in Toronto on December 11, 2009, Mitic's first solo show with the gallery, together with a book of the same name.</p>
      <p>The series turns the usual arrangement around. A dealer normally promotes the artist. Here the artist promotes the dealer.</p>
      <p>Nine of the portraits are currently listed as available.</p>
      <a class="more" href="available-work.html#dealers">Available portraits</a>
      <a class="more" href="books.html#dealers">The book</a>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>The <em>portraits</em></h2><span class="label">{len(DATA["dealers"])} shown · select to enlarge</span></div>
    <div class="gal c5">{g}</div>
  </div>
</section>
{cta("Ask about Dealers", "For availability or prices of individual portraits, write to the studio.", "Available work")}
{pager("dealers.html")}
</main>"""
    return page("dealers.html", "Dealers · Viktor Mitic", "Dealers: 36 portraits of Toronto's art dealers by Viktor Mitic in Japanese ink on gold leaf.", body,
                og=U + "2017/10/Viktor-14Sep09_0047-prnt.jpg")


SCULPT_CAPS = {
    "Screenshot_20210811": ("", "Studio shot of a 17 ft sculpture in stainless steel and 24k gold."),
    "9206d1df": ("Red-Gold", "Abstract forms with 24k gold accents, for indoors or outdoors."),
    "red-6": ("Red-Gold", ""), "red-gold-gold-plated": ("Red-Gold", "Gold-plated stainless steel."),
    "puff-samurai": ("Puff Samurai", ""),
}
MEDIA_CAPS = {
    "CELESTIAL": ("Celestial", "Sonoma, California. Collection of Gary Spain."), "1_viktor_mitic": ("Lyric Star", "Marriott Hotel, Markham, Ontario."),
    "Gold-top-lorne-gertner": ("Gold Top", "Lorne Gertner."), "red-gold-lorne-gertner": ("Red Gold", "Lorne Gertner."),
    "gold-top-and-red-gold": ("Gold Top and Red Gold", "Fortune Global Forum view."), "Heartland-Port-Moody": ("Heartland", "Port Moody, British Columbia."),
    "heartland-oeno": ("Heartland", "Oeno Gallery view."), "fragment-doha": ("Fragment", "Doha, Qatar."),
    "purple-heart-oeno": ("Purple Heart", "Oeno Gallery view, 2019."), "purple-heart-veranda": ("Purple Heart", "Veranda, Colombo, Sri Lanka."),
    "gold-totem-shoe": ("Gold Totem", "Shoe-Inn collection, New Jersey."), "red-gold-gold-totem": ("Red Gold and Gold Totem", ""),
    "xox-prototype-studio": ("XOX prototype", "In the studio."), "xox-prototype": ("XOX prototype", ""),
    "Washington-DC-2013": ("Incident", "Washington, D.C., 2013."), "viktor-mitic": ("Viktor Mitic", ""),
}


def lookup(table, f):
    return next((v for k, v in table.items() if k in f), ("", ""))


def build_sculptures():
    g = ""
    for i, it in enumerate(DATA["sculpt"], 1):
        t, c = lookup(SCULPT_CAPS, it["f"])
        g += tile(it, "sculpt", (t + ", " if t else "") + "sculpture by Viktor Mitic", title=t, cap=c, n=i)
    public = [
        ("2021", "<em>Heartland</em>", "Port Moody, British Columbia"), ("2019", "<em>Purple Heart</em>", "Moot Manor of Sri Lanka, Colombo"),
        ("2018", "<em>Lyric Star</em>", "Marriott Hotel, Markham, Ontario"), ("2018", "<em>The Music Garage</em>", "Marriott Hotel, Markham, Ontario"),
        ("2018", "<em>Hypervelocity Asteroid</em>", "Rochester Car Museum, Rochester, New York"), ("2018", "<em>Death Flower</em>", "Elizabeth Collection, Rochester, New York"),
        ("2015", "<em>Blasted Guernica</em>", "Remington Contemporary Art Museum, Markham, Ontario"),
    ]
    hero = by_file("sculpt", "IMG_20220411_104605")
    inc = by_file("war", "cropped-incident-c.jpg")
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Sculptures & installations")], "Sculpture · Installation", "Shape in Space",
                 "Totems in steel, bronze and 24k gold, cut aluminum in car paint, and a school bus.", U + hero["l"], "Outdoor sculpture by Viktor Mitic on a beach") + f"""
<main id="main">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv"><span class="label">The work</span><h2>Drawing <em>in space</em></h2>
      <p class="note">This section summarises an essay on the sculptures by John K. Grande, writer and art critic.</p></div>
    <div class="rv prose">
      <p>The cut-aluminum sculptures have a post-Pop flair and a debt to Frank Stella. Shaped metal is finished in car paint, and the forms sit at different depths, so the gaps between them matter as much as the shapes.</p>
      <p>Lines curve almost in parallel, one behind another, held by oversized fixings that look like rivets. The effect is theatrical: a machine that works only in the imagination. The shapes cut for one large piece leave negative offcuts, and those are reused in another, so the two works speak to each other about presence and absence.</p>
      <p>Smaller, more recent sculptures begin with paint drips from the studio floor. They rise from painted blocks and carry something of Arp's surrealist forms. The critic also compares the organic shapes to Frederick Kiesler's experiments with biomorphic design.</p>
      <p>The language is neither abstract nor figurative. It is about perception: how colour and shape build meaning, and how an object in space changes the way we read the space around it.</p>
      <a class="more" href="sculptures-3d.html">Turn the sculptures in 3D</a>
      <a class="more" href="acquisitions.html">Collector acquisitions</a>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>The <em>sculptures</em></h2><span class="label">{len(DATA["sculpt"])} images · select to enlarge</span></div>
    <div class="gal">{g}</div>
  </div>
</section>
<section class="banner" id="incident" aria-labelledby="incident-h">
  <img loading="lazy" alt="Incident, a bullet-riddled school bus by Viktor Mitic" src="{U}{inc["l"]}">
  <div class="wrap rv">
    <span class="label">Installation · 2013</span>
    <h2 id="incident-h">Incident</h2>
    <p>A school bus shot through with bullet holes. It premiered at Nuit Blanche in Toronto, then toured to Washington, D.C. in April 2013 during the U.S. gun debates. It is in the permanent collection of Artisan Works in Rochester, New York.</p>
    <div class="row"><a class="more" href="press.html">Press and video</a></div>
  </div>
</section>
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Public <em>art</em></h2><a class="more" href="cv.html">Full CV</a></div>
    {rows(public)}
  </div>
</section>
{cta("Commission or acquire a sculpture", "Works range from tabletop pieces to outdoor sculptures 16 feet tall. Write to the studio about available pieces and commissions.", "Commission")}
{pager("sculptures.html")}
</main>"""
    return page("sculptures.html", "Sculptures & installations · Viktor Mitic", "Sculptures and installations by Viktor Mitic: steel and 24k gold totems, cut aluminum, public art and Incident.", body, og=U + hero["l"])


VIEWERS = [  # id, tab label, name, folder, width, height, turn frames, tilt frames, start turn, start tilt
    ("sc1", "SC 1", "Sculpture 1", "final render_XR.29", 886, 582, 20, 10, 10, 1),
    ("sc2", "SC 2", "Sculpture 2", "Sculpt 2_XR.71", 800, 708, 18, 9, 9, 0),
    ("sc3", "SC 3", "Gold Top", "Gold top-colored_XR.39", 801, 605, 10, 10, 5, 0),
    ("sc4", "SC 4", "Sculpture 4", "Sculpt-3_XR.103", 800, 708, 10, 10, 5, 0),
    ("sc5", "SC 5", "Sculpture 5", "Model_XR.117", 801, 601, 10, 10, 5, 1),
]


def build_3d():
    tabs = "".join(
        f'<button class="chip" type="button" data-id="{i}" data-name="{esc(n)}" data-folder="{esc(f)}" data-w="{w}" data-h="{h}" '
        f'data-u="{u}" data-v="{v}" data-su="{su}" data-sv="{sv}" aria-pressed="false">{l}</button>' for i, l, n, f, w, h, u, v, su, sv in VIEWERS)
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Sculptures in 3D")], "Interactive", "Click &amp; Drag",
                 "Five sculptures you can turn. Drag across the image to rotate it, up and down to tilt it.") + f"""
<main id="main">
<section class="tight" style="padding-top:0">
  <div class="wrap">
    <div class="tabs" role="group" aria-label="Choose a sculpture">{tabs}</div>
    <div class="viewer" id="turn" data-base="{V}" tabindex="0" role="img" aria-label="3D view">
      <img alt="" src="{BLANK}"><span class="turn-load" role="status">Loading…</span>
    </div>
    <p class="viewer-note"><span id="viewerName"></span> · Drag to rotate, or use the arrow keys · Each new angle loads as you reach it.</p>
  </div>
</section>
{cta("Ask about a sculpture", "Tell us which piece caught your eye and we will send details.", "Available work")}
{pager("sculptures-3d.html")}
</main>"""
    return page("sculptures-3d.html", "Sculptures in 3D · Viktor Mitic", "Turn five Viktor Mitic sculptures in 3D: click and drag to rotate.", body, og=U + "2017/12/Ax11-1024x683.jpg")


# ------------------------------------------------------------------ available work
AVAIL_INFO = {
    6: ("Jamie Angell, Angell Gallery", ""), 13: ("Christopher Cutts, Christopher Cutts Gallery", ""),
    15: ("Installation", "A car riddled with bullet holes."),
    26: ("John Ringling", "Square acrylic portrait of the founder of the Ringling Museum in Sarasota, Florida, with bullet-hole details."),
    36: ("XOX Kiddo Hipster", ""), 37: ("Caelum", ""),
    41: ("Space Lounger", "Experimental sculpture, 20 ft tall, photographed before its move to the Suncoast Science Center."),
    42: ("Orion", "Mirror-polished stainless steel dipped in 24k gold, on a white marble base."),
    43: ("Red-Gold", "Abstract sculpture with 24k gold accents, suited to indoor or outdoor settings."),
    44: ("Heartland", "Tall, narrow stack of forms in stainless steel finished in black wax."),
    45: ("Fragment Spectrum", "Slim, angular sculpture in stainless steel with painted surfaces and 24k gold accents."),
}
CATS = {"painting": ("Painting", "Paintings"), "sculpture": ("Sculpture", "Sculpture"), "dealers": ("Dealers portrait", "Dealers portraits")}


def avail_cat(i):
    if 6 <= i <= 14:
        return "dealers"
    if i in (1, 2, 38, 39, 40) or 16 <= i <= 35:
        return "painting"
    return "sculpture"


def build_available():
    counts = {k: 0 for k in CATS}
    cards = ""
    for i, it in enumerate(DATA["avail"], 1):
        cat = avail_cat(i)
        counts[cat] += 1
        ref = f"AW-{i:02d}"
        title, desc = AVAIL_INFO.get(i, ("", ""))
        if cat == "dealers" and not title:
            title = dealer_name(it["f"])
        shown = title or CATS[cat][0]
        medium = "Japanese ink on gold leaf" if cat == "dealers" else ""
        enq = "contact.html?work=" + quote(f"{ref} {title}".strip())
        alt = f"{shown} by Viktor Mitic, reference {ref}"
        p = f"<p>{esc(desc or medium)}</p>" if (desc or medium) else ""
        cards += (f'<figure class="tile work" data-cat="{cat}" id="{ref}"><button type="button" {lb_attrs(it, "avail", shown, ref + " · " + CATS[cat][0], alt, enq)} aria-label="Enlarge {esc(shown)}, {ref}">'
                  f'<img loading="lazy" src="{U}{it["t"]}" width="{it["w"]}" height="{it["h"]}" alt="{esc(alt)}"></button>'
                  f'<figcaption><span class="ref">{ref} · {CATS[cat][0]}</span><h3>{esc(shown)}</h3>{p}<a class="more" href="{esc(enq)}">Enquire</a></figcaption></figure>')
    total = len(DATA["avail"])
    chips = f'<button class="chip" type="button" data-filter="all" aria-pressed="true">All<span class="n">{total}</span></button>' + "".join(
        f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{v[1]}<span class="n">{counts[k]}</span></button>' for k, v in CATS.items())
    body = phero([("index.html", "Home"), (None, "Available work")], "Collect", "Available work",
                 "Paintings, sculptures and portraits currently offered by the studio. Each piece has a reference number to quote when you enquire.") + f"""
<main id="main">
<section class="tight" style="padding-top:0">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Filter by type">{chips}</div>
    <p class="count" id="count" aria-live="polite">Showing {total} of {total} works</p>
    <h2 class="sr">Works</h2>
    <div class="gal">{cards}</div>
    <p class="note">Prices, dimensions and availability are confirmed by the studio on request. Select any image to enlarge it.</p>
  </div>
</section>
{cta("Found something?", "Send the reference number and we will reply with price, size and shipping details.", "Available work")}
</main>"""
    return page("available-work.html", "Available work · Viktor Mitic", "Paintings, sculptures and Dealers portraits by Viktor Mitic currently available from the studio.", body,
                og=U + by_file("avail", "PSX_20230408")["l"])


# ------------------------------------------------------------------ press
VIDEOS = [("CfB2f5PzN4s", "Fox News", "Washington, D.C. · 2013"), ("-Ulu7HZxoUw", "BBC", "Interview on the gun art"),
          ("GS1DhUaLQE8", "CBC National", "Toronto · 2013"), ("2NpswdtdfZ4", "Global TV National", "Art or War"),
          ("ta87GB1G0qs", "Global Morning Show", "2013"), ("_w5PNtoVKdk", "MTV", "Interview · 2015"),
          ("ghJIg8etS70", "ET Canada", "Feature on Art or War"), ("98KjMoDBhHc", "The Canadian Press", "Interview on Art or War · Toronto, 2010"),
          ("rpdk_YbBYtw", "Rochester, New York", "2015"), ("P6FACwvOk4o", "Bullet Artist", "Short profile")]
WB = "https://web.archive.org/web/"
ARTICLES = [
    ("The Globe and Mail", "From the barrel of a gun", "https://www.theglobeandmail.com/arts/viktor-mitic-from-the-barrel-of-a-gun/article4213687/", ""),
    ("The Washington Post", "A bullet-riddled school bus debuts in D.C. · 2013", "https://www.washingtonpost.com/local/bullet-riddled-school-bus-debuts-in-dc-as-a-rolling-art-exhibit/2013/04/07/cb06bb2c-9fa9-11e2-9c03-6952ff305f35_story.html", ""),
    ("CBC News", "Bullet holes stud Viktor Mitic's pop art", "https://www.cbc.ca/news/entertainment/bullet-holes-stud-viktor-mitic-s-pop-art-1.1403936", ""),
    ("HuffPost", "Art against guns: the bullet-riddled bus · 2013", "https://www.huffpost.com/entry/art-against-guns-viktor-mitic-fights-back-with-bullet-riddled-bus-artwork_n_3036727", ""),
    ("Toronto Star", "Bullet-riddled Bieber painting missing after TIFF debut · 2017", "https://www.thestar.com/news/gta/bullet-riddled-painting-of-justin-bieber-missing-after-tiff-debut/article_a278af2e-7416-57b7-a84a-3ac78af6173c.html", ""),
    ("Toronto Sun", "Bullet-riddled Bieber painting returned to artist · 2017", "https://torontosun.com/2017/09/21/bullet-riddled-bieber-painting-returned-to-artist", ""),
    ("Daily Mail", "Portraits of Lennon, JFK and Gandhi in bullet holes", "https://www.dailymail.com/news/article-1337552/Viktor-Mitic-paints-pictures-gun-victims-John-Lennon-JFK-Gandhi-bullet-holes.html", ""),
    ("SRQ Magazine", "Gone shooting with Viktor Mitic · 2014", "https://www.srqmagazine.com/srq-daily/2014-08-22/447_Gone-Shooting-with-Viktor-Mitic", ""),
    ("Democrat and Chronicle", "Artisan Works, Rochester · 2015", WB + "20230326153100/https://www.democratandchronicle.com/story/lifestyle/art/2015/05/15/artisanworks-viktor-mitic-rochester-louis-perticone-guns/27382641/", "Archived copy"),
    ("Metro News", "A portrait of Hugo Chávez, marked with bullets · 2013", WB + "20180321051455/http://www.metronews.ca/news/toronto/2013/03/25/artist-viktor-mitic-makes-his-mark-with-bullets-on-hugo-chavezs-face.html", "Archived copy"),
    ("Miami Herald", "Coverage from South Florida · 2016", WB + "20190818091942/https://www.miamiherald.com/news/local/community/gay-south-florida/article85840067.html", "Archived copy"),
    ("Downtown Markham", "Blasted Guernica", "https://downtownmarkham.ca/artists/blasted-guernica/", ""),
    ("Tightrope Books", "Art or War, the book", "http://tightropebooks.com/art-or-war-viktor-mitic/", ""),
    ("Abhijit Bhaduri", "Interview with Viktor Mitic · 2011", "https://abhijitbhaduri.com/global-trends-insights/interview-viktor-mitic/", ""),
    ("Dobbernationloves", "TIFF 2017 at Toronto's Campbell House", "https://dobbernationloves.com/life-culture/tiff17-mongrel-media-celebrates-top-films-at-torontos-campbell-house/", ""),
    ("Canadian Art", "Feature on Viktor Mitic", "", ""),
    ("Vancouver Sun", "Toronto dealers react to the Dealers portraits", "", ""),
    ("Torontoist", "Paint by bullets · 2013", "", ""),
]


def build_press():
    vids = "".join(
        f'<article class="video"><div class="frame"><button type="button" data-yt="{i}" aria-label="Play: {esc(t)}, {esc(s)}">'
        f'<img loading="lazy" src="https://i.ytimg.com/vi/{i}/hqdefault.jpg" alt=""></button></div><h3>{esc(t)}</h3><p>{esc(s)}</p></article>' for i, t, s in VIDEOS)
    arts = ""
    for o, s, href, note in ARTICLES:
        if href:
            arts += f'<li><a href="{esc(href)}" target="_blank" rel="noopener"><span class="o">{esc(o)}</span><span class="s">{esc(s)}</span><span class="r">{note or "Read"} ↗</span></a></li>'
        else:
            arts += f'<li><div class="dead"><span class="o">{esc(o)}</span><span class="s">{esc(s)}</span><span class="r">No longer online</span></div></li>'
    inc = by_file("war", "cropped-incident-c.jpg")
    body = phero([("index.html", "Home"), (None, "Press & video")], "Media coverage", "In the press",
                 "Television, newspapers and magazines on the bullet paintings, the bus and the sculptures.", U + inc["f"], "Incident, the bullet-riddled school bus") + f"""
<main id="main">
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>On <em>television</em></h2><span class="label">{len(VIDEOS)} videos</span></div>
    <div class="videos">{vids}</div>
    <p class="note">Videos play from YouTube when you press play.</p>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>In <em>print</em></h2><span class="label">Selected articles</span></div>
    <ul class="press">{arts}</ul>
  </div>
</section>
<section class="tight">
  <div class="wrap split top flush sm">
    <div class="rv"><span class="label">For journalists</span><h2>Press <em>enquiries</em></h2></div>
    <div class="rv prose">
      <p>For interviews, images and information, write to <a class="mail" style="font-size:inherit;margin:0" href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <p>Release images of recent collector acquisitions are available for media use.</p>
      <a class="more" href="acquisitions.html">Collector acquisitions and images</a>
      <a class="more" href="contact.html?topic=Press">Contact page</a>
    </div>
  </div>
</section>
</main>"""
    return page("press.html", "Press & video · Viktor Mitic", "Press coverage and television interviews with Viktor Mitic: BBC, CBC, Fox News, The Globe and Mail, The Washington Post and more.", body, og=U + inc["l"])


# ------------------------------------------------------------------ books, cv, acquisitions
FILMS = [("Point Blank: Art or War", "Nora Stankovic · 11 min · Cannes Film Festival", "2016"), ("Gun Porn", "Brahm Rosensweig · 11 min · Hot Docs, Hulu", "2014"),
         ("Rain Dance", "Brahm Rosensweig · 14 min · Fourfront Editions", "2011"), ("Art or War", "Laurie Kwasnik · 12 min · Tightrope Books", "2010")]


def films_html():
    return '<ul>' + "".join(f'<li><span class="t">{esc(t)}</span><span class="d">{esc(d)}</span><span class="y">{y}</span></li>' for t, d, y in FILMS) + "</ul>"


def build_books():
    own = [
        ("dealers", "01 · 2009", "Dealers", "The 36 portraits of Toronto's art dealers. Introduction by Gary Michael Dault. Tightrope Books.", "https://www.amazon.ca/Dealers-Viktor-Mitic/dp/1926639146", "dealers.html"),
        ("art-or-war", "02 · 2010", "Art or War", "Bullet hole paintings by Viktor Mitic. Introduction by Jim Nason. Tightrope Books.", "https://www.amazon.ca/Art-War-Paintings-Viktor-Mitic/dp/1926639154", "art-or-war.html"),
        ("rain-dance", "03 · 2011", "Rain Dance", "Reproductions of the rain paintings, with Galaxy on the cover, published with a DVD. Fourfront Editions.", "https://www.amazon.com/Rain-Dance-DVD-Viktor-Mitic/dp/1926802667", "rain-dance.html"),
    ]
    own_html = "".join(
        f'<div class="book" id="{i}"><span class="n">{n}</span><h3>{t}</h3><p>{p}</p>'
        f'<a class="more" href="{buy}" target="_blank" rel="noopener">Find the book</a><a class="more" href="{series}">See the series</a></div>' for i, n, t, p, buy, series in own)
    essays = [("2021", "<em>Shifting Paradigms: Essays on Art and Culture</em>", "Guernica Editions. Includes an extensive essay on Mitic's work."),
              ("2018", "<em>Cagdas Sanat Ve Yeniden Uretim</em>", "Hayalaperest Yayinevi. Includes an extensive essay on Mitic's work."),
              ("2017", "<em>Desire Lines</em>", "Guernica Editions. Includes an extensive essay on Mitic's work.")]
    body = phero([("index.html", "Home"), (None, "Books & films")], "Publications", "Books &amp; films",
                 "Three books of the work, three books that write about it, and four short films.") + f"""
<main id="main">
<section class="tight" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>By <em>the artist</em></h2></div>
    <div class="books rv">{own_html}</div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Writing <em>on the work</em></h2></div>
    {rows(essays)}
  </div>
</section>
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>On <em>film</em></h2><a class="more" href="press.html">Television and video</a></div>
    <div class="films rv" style="margin-top:0">{films_html()}</div>
  </div>
</section>
</main>"""
    return page("books.html", "Books & films · Viktor Mitic", "Books and films by and about Viktor Mitic: Dealers, Art or War, Rain Dance, Gun Porn and Point Blank.", body)


def build_cv():
    public = [("2021", "<em>Heartland</em>", "Port Moody, British Columbia, Canada"), ("2019", "<em>Purple Heart</em>", "Moot Manor of Sri Lanka, Colombo, Sri Lanka"),
              ("2018", "<em>Lyric Star</em>", "Marriott Hotel, Markham, Ontario, Canada"), ("2018", "<em>The Music Garage</em>", "Marriott Hotel, Markham, Ontario, Canada"),
              ("2018", "<em>Hypervelocity Asteroid</em>", "Rochester Car Museum, Rochester, New York"), ("2018", "<em>Death Flower</em>", "Elizabeth Collection, Rochester, New York"),
              ("2015", "<em>Blasted Guernica</em>", "Remington Contemporary Art Museum, Markham, Ontario, Canada")]
    collections = [("2018", "Biggs Museum of American Art", "Dover, Delaware. Work in the permanent collection."),
                   ("2015", "Elizabeth Collection", "Rochester, New York. Collection of paintings and sculptures."),
                   ("2015", "Remington Contemporary Art Museum", "Markham, Ontario. Work in the permanent collection."),
                   ("2009", "Beaverbrook Art Gallery", "Fredericton, New Brunswick. Work in the permanent collection.")]
    shows = [("2022", "Oeno Gallery", "small spaces BIG IDEAS, Bloomfield, Ontario (Prince Edward County)"), ("2021", "Art Toronto", "Toronto, Ontario"),
             ("2021", "Oeno Gallery", "Outdoor Sculpture Exhibition, Bloomfield, Ontario"), ("2021", "Oeno Gallery", "Negotiating Diaspora, Bloomfield, Ontario"),
             ("2020", "Oeno Gallery", "Outdoor Sculpture Exhibition, Bloomfield, Ontario"), ("2019", "Oeno Gallery", "Bloomfield, Ontario"),
             ("2019", "Galerie d'arts contemporains", "Montreal, Quebec"), ("2018", "Oeno Gallery", "Oeno's Sculpture Garden at Huff Estates, Bloomfield, Ontario"),
             ("2018", "Galerie d'arts contemporains", "Montreal, Quebec"), ("2018", "Oeno Gallery", "Bloomfield, Ontario"),
             ("2018", "Nuit Blanche", "Out of site, Toronto, Ontario"), ("2017", "Campbell House Museum", "Toronto, Ontario"),
             ("2015", "ARTISANworks", "Rochester, New York"), ("2013", "George Mason University", "Fairfax, Virginia"),
             ("2013", "The Peach Gallery", "Toronto, Ontario"), ("2013", "Todmorden Mills", "Toronto, Ontario"),
             ("2012", "Todmorden Mills", "Nuit Blanche Toronto, Toronto, Ontario"), ("2011", "Gallery Moos", "Toronto, Ontario"),
             ("2010", "Gallery Moos", "Toronto, Ontario"), ("2010", "The Armory Show", "New York, courtesy of ADAC"),
             ("2010", "EXPO Chicago (formerly Art Chicago)", "Chicago, Illinois, courtesy of ADAC"), ("2009", "Art Toronto", "Courtesy of Odon Wagner Contemporary, Toronto, Ontario"),
             ("2009", "Odon Wagner Contemporary", "Toronto, Ontario"), ("2008", "Muramatsu Gallery", "Tokyo, Japan")]
    books = [("2021", "<em>Shifting Paradigms: Essays on Art and Culture</em>", "Guernica Editions. Extensive essay on Mitic's work."),
             ("2018", "<em>Cagdas Sanat Ve Yeniden Uretim</em>", "Hayalaperest Yayinevi. Extensive essay on Mitic's work."),
             ("2017", "<em>Desire Lines</em>", "Guernica Editions. Extensive essay on Mitic's work."),
             ("2011", "<em>Rain Dance</em>", "Fourfront Editions"), ("2010", "<em>Art or War</em>", "Tightrope Books"), ("2009", "<em>Dealers</em>", "Tightrope Books")]
    edu = [("1996", "Bachelor of Fine Art", "Fine art and art history. University of Toronto, Toronto, Ontario."),
           ("1995", "Fine Arts Diploma", "Fine art and art history. Sheridan College, Oakville, Ontario.")]
    e = lambda items: rows([(y, t if "<em>" in t else esc(t), s) for y, t, s in items])
    block = lambda h, content: f'<div class="cv-block rv"><h2>{h}</h2>{content}</div>'
    body = phero([("index.html", "Home"), (None, "Curriculum vitae")], "Viktor Mitic", "Curriculum vitae",
                 "Public art, collections, exhibitions, films, books and education.") + f"""
<main id="main">
<section class="tight" style="padding-top:0">
  <div class="wrap narrow">
    <div class="actions" style="margin:0 0 clamp(40px,6vw,70px)"><button class="btn ghost small" type="button" onclick="window.print()">Print or save as PDF</button><a class="btn ghost small" href="contact.html">Contact the studio</a></div>
    {block("Public <em>art</em>", e(public))}
    {block("Collections", e(collections))}
    {block("Shows", e(shows))}
    {block("Films", '<div class="films" style="margin-top:0">' + films_html() + "</div>")}
    {block("Books", e(books))}
    {block("Education", e(edu))}
  </div>
</section>
</main>"""
    return page("cv.html", "Curriculum vitae · Viktor Mitic", "Viktor Mitic's CV: public art, museum collections, exhibitions, films, books and education.", body)


def build_acquisitions():
    g = ""
    for i, it in enumerate(DATA["media"], 1):
        t, c = lookup(MEDIA_CAPS, it["f"])
        g += tile(it, "media", (t + ". " if t else "") + (c or "Sculpture by Viktor Mitic"), title=t, cap=c, n=i)
    facts = [("Sonoma", "<em>Celestial</em> and <em>Black</em>", "Acquired by Gary Spain, California interior designer and executive creative director at RH, for his private Sonoma estate. Celestial is 24k gold-plated stainless steel."),
             ("Port Moody", "<em>Heartland</em>", "Acquired by the City of Port Moody, British Columbia, known as the City of the Arts. The 9 ft bronze and black sculpture stands in the centre of the community."),
             ("New Jersey", "<em>Gold Totem</em>", "Acquired for the Shoe-Inn Distribution Center in Englewood. The tall sculpture in 24k gold-plated stainless steel stands on a pedestal in the entry gallery."),
             ("Abroad", "Doha and Colombo", "International collectors now reach as far as Doha, Qatar, and Colombo, Sri Lanka.")]
    hero = by_file("media", "heartland-oeno")
    body = phero([("index.html", "Home"), (None, "Collector acquisitions")], "News · February 3, 2023", "New collectors",
                 "Viktor Mitic's sculptures have entered private, public and commercial collections in California, British Columbia and New Jersey.",
                 U + hero["l"], "Heartland, sculpture by Viktor Mitic, at Oeno Gallery") + f"""
<main id="main">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv"><span class="label">The announcement</span><h2>Sculptures find <em>new homes</em></h2>
      <p class="note">Summary of a press release issued from Sarasota, Florida, and Toronto, Ontario.</p></div>
    <div class="rv prose">
      <p>Collectors have been acquiring Mitic's sculptures for homes, public spaces and commercial projects, sometimes two pieces at a time. He is best known for the earlier bullet paintings, and the sculptures show how far the work has moved since.</p>
      <p>During the pandemic he set up a second studio in Sarasota, Florida, alongside Toronto. The release names Oeno Gallery, in Prince Edward County, Ontario, as the gallery representing his work. The gallery describes the recent sculptures as paint splatters from the studio floor turned into tall, colourful totems.</p>
      <p>The forms are neither abstract nor figurative. Some stand 16 feet tall.</p>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Who acquired <em>what</em></h2></div>
    {rows(facts)}
  </div>
</section>
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>Release <em>images</em></h2><span class="label">For media use · select to enlarge</span></div>
    <div class="gal">{g}</div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap split top flush sm">
    <div class="rv"><span class="label">Background</span><h2>About <em>the artist</em></h2></div>
    <div class="rv prose">
      <p>Mitic's bullet-riddled paintings comment on attitudes to guns, violence and fame. <em>Incident</em>, the shot-out school bus, premiered at Nuit Blanche in Toronto and was shown in Washington, D.C. in April 2013.</p>
      <p>His work has been exhibited at the Armory Show in New York, Gallery Moos in Toronto, Art Chicago, Muramatsu Gallery in Tokyo and the Beaverbrook Art Gallery. Earlier collectors include two former prime ministers of Canada, Stephen Harper and Jean Chrétien.</p>
      <a class="more" href="cv.html">Curriculum vitae</a>
      <a class="more" href="contact.html?topic=Press">Press enquiries</a>
    </div>
  </div>
</section>
</main>"""
    return page("acquisitions.html", "Collector acquisitions · Viktor Mitic", "Viktor Mitic's sculptures acquired by collectors in Sonoma, Port Moody and New Jersey, with release images for media use.", body, og=U + hero["l"])


# ------------------------------------------------------------------ contact + 404
def build_contact():
    body = phero([("index.html", "Home"), (None, "Contact")], "Enquire", "Contact",
                 "Ask about available work, commissions, exhibitions or press. The studio replies by email.") + f"""
<main id="main">
<section class="tight" style="padding-top:0">
  <div class="wrap contact">
    <div>
      <h2>Write to <em>the studio</em></h2>
      <p>Email is the quickest way to reach us. Use the form to have your message written out for you, or copy the address below.</p>
      <div class="direct">
        <span class="label">Email</span><br>
        <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a>
        <div class="actions">
          <button class="btn ghost small" type="button" data-copy-email="copyStatus">Copy address</button>
          <a class="btn ghost small" href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to={EMAIL}" target="_blank" rel="noopener">Open Gmail</a>
        </div>
        <p class="status" id="copyStatus" role="status"></p>
      </div>
      <dl class="facts">
        <div><dt>Studios</dt><dd>Toronto, Ontario · Sarasota, Florida</dd></div>
        <div><dt>Gallery</dt><dd>Oeno Gallery, Prince Edward County, Ontario</dd></div>
        <div><dt>Quote a reference</dt><dd>Each piece on the <a class="more" style="padding:0" href="available-work.html">available work</a> page has a number such as AW-12.</dd></div>
      </dl>
    </div>
    <form class="enq" id="enquiry" novalidate>
      <div class="two">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required aria-describedby="err-name"><span class="err" id="err-name" role="alert"></span></div>
        <div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="err-email"><span class="err" id="err-email" role="alert"></span></div>
      </div>
      <div class="two">
        <div class="field"><label for="f-topic">Subject</label>
          <select id="f-topic" name="topic"><option>Available work</option><option>Commission</option><option>Exhibition or loan</option><option>Press</option><option>Other</option></select></div>
        <div class="field"><label for="f-ref">Work reference (optional)</label><input id="f-ref" name="ref" placeholder="AW-12" maxlength="80"></div>
      </div>
      <div class="field"><label for="f-message">Message</label><textarea id="f-message" name="message" required aria-describedby="err-message"></textarea><span class="err" id="err-message" role="alert"></span></div>
      <div><button class="btn fill" type="submit">Prepare my message</button></div>
      <p class="status" id="formStatus" role="status"></p>
      <div class="send" id="send" hidden>
        <p>This page does not send email itself. Pick the mail service you use and your message opens there, ready to send.</p>
        <div class="actions">
          <a class="btn fill small" id="viaGmail" href="#" target="_blank" rel="noopener">Gmail</a>
          <a class="btn ghost small" id="viaOutlook" href="#" target="_blank" rel="noopener">Outlook</a>
          <a class="btn ghost small" id="viaYahoo" href="#" target="_blank" rel="noopener">Yahoo Mail</a>
          <a class="btn ghost small" id="viaApp" href="#">Mail app</a>
          <button class="btn ghost small" id="copyMsg" type="button">Copy message</button>
        </div>
      </div>
    </form>
  </div>
</section>
</main>"""
    return page("contact.html", "Contact · Viktor Mitic", "Contact Viktor Mitic's studio about available work, commissions, exhibitions and press.", body)


def build_404():
    body = phero([("index.html", "Home"), (None, "Page not found")], "404", "Nothing hangs here",
                 "That page does not exist. Try one of these instead.") + """
<main id="main">
<section class="tight" style="padding-top:0"><div class="wrap"><div class="actions" style="margin-top:0">
<a class="btn fill" href="index.html">Home</a><a class="btn ghost" href="available-work.html">Available work</a><a class="btn ghost" href="contact.html">Contact</a>
</div></div></section>
</main>"""
    return page("404.html", "Page not found · Viktor Mitic", "Page not found.", body)


if __name__ == "__main__":
    built = [f() for f in (build_index, build_rain, build_war, build_dealers, build_sculptures, build_3d, build_available,
                           build_press, build_books, build_cv, build_acquisitions, build_contact, build_404)]
    listed = site_meta.finish(built)
    print("built", len(built), "pages:", ", ".join(built))
    print("sitemap.xml lists", listed, "pages; robots.txt written")
