"""Landing page."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


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
        ("2024", "The 20 ft <em>Space Lounger</em> is installed at the Suncoast Science Center in Sarasota. New outdoor work in bronze and Spanish black marble."),
        ("2025", "Joins the Sculptors Society of Canada and shows <em>Hydra</em>, in 24k gold-plated stainless steel, at the Canadian Sculpture Centre in Toronto."),
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
  <div class="hero-img" id="heroImg"></div>
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

<main id="main" tabindex="-1">
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

<section id="works" class="pt0">
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
    <div class="actions rv mt-26">
      <a class="btn fill" href="available-work.html">View available work</a>
      <a class="btn ghost" href="contact.html">Enquire</a>
    </div>
    <div class="tiles rv">
      <a href="news.html"><span class="label">News</span><h3>From the studio</h3><span class="sub">New work and shows, 2023 to 2026</span></a>
      <a href="cv.html"><span class="label">About</span><h3>Curriculum vitae</h3><span class="sub">Public art, collections, shows</span></a>
      <a href="press.html"><span class="label">Media</span><h3>Press &amp; video</h3><span class="sub">Articles and television</span></a>
    </div>
  </div>
</section>
</main>"""
    return page("index.html", "Viktor Mitic · Art or War",
                "Viktor Mitic, painter and sculptor: Rain Dance paintings made in the rain, Art or War bullet-hole paintings, Dealers, sculpture and installations.",
                body, preload=hero)
