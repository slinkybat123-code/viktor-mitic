"""Series pages: Rain Dance, Art or War, Dealers."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


def build_rain():
    works = DATA["rain"] + [extra("viktor-16jun08-008a-web-crop-u5356.jpg", 259, 164), extra("viktor-16jun08-014a-web-crop-u5300.jpg", 259, 150)]
    g = "".join(tile(it, "rain", "Rain Dance, painting by Viktor Mitic", n=i) for i, it in enumerate(works, 1))
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Rain Dance")], "Series · Painting", "Rain Dance",
                 "Paintings made outdoors, in the rain, at sites across North America.",
                 U + "2017/10/Diptych-10-Aug-08-sm-web.jpg", "Rain Dance diptych by Viktor Mitic") + f"""
<main id="main" tabindex="-1">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv"><span class="label">The process</span><h2>Weather as a <em>collaborator</em></h2></div>
    <div class="rv prose">
      <p>In Rain Dance, Mitic mixes natural elements with traditional painting mediums. Each canvas was made outside while it rained, so the weather on the day shaped the result as much as the brush did.</p>
      <p>He came to the method by accident and calls it acid rain painting: non-representational paintings on canvas that the environment helps to make. He has said he enjoys rebuilding structures that nature has erased.</p>
      <p>It is a kind of aleatory art, art that lets chance in. The canvases lie flat on the ground outdoors, and the rain is a constant painting partner whose effects cannot be planned.</p>
      <p><em>Galaxy</em> (2008) was shown at Muramatsu Gallery in Tokyo and later sold at a charity auction in Toronto to a private collector. It is on the cover of the <em>Rain Dance</em> book.</p>
      <a class="more" href="books.html#rain-dance">The book and film</a>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>The <em>paintings</em></h2><span class="label">{len(works)} works · select to enlarge</span></div>
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
    works = DATA["war"] + [extra("viktor_08.jpg", 924, 928), extra("viktor_mstr-148.jpg", 956, 1174),
                           extra("viktor-matic-_0030_doc1-1200x796-1.jpg", 511, 339), extra("viktor_doc-1841-582x540-crop-u5527.jpg", 480, 339),
                           extra("viktor-mitic-homebg-537x540-crop-u5393.jpg", 480, 339)]
    for i, it in enumerate(works, 1):
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
                 "Portraits and icons, painted and then outlined with live ammunition.", U + hero["l"], "Blasted Guernica by Viktor Mitic") + f"""
<main id="main" tabindex="-1">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv">
      <span class="label">The idea</span>
      <h2>Can a gun <em>make</em> something?</h2>
      <blockquote class="quote mt-36">“Guns were made to destroy, but can they be used to create something beautiful?”<cite>Viktor Mitic</cite></blockquote>
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
    <div class="sec-head sm"><h2>The <em>paintings</em></h2><span class="label">{len(works)} works · select to enlarge</span></div>
    <div class="gal">{g}</div>
  </div>
</section>
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Notable <em>works</em></h2></div>
    {rows(notable)}
    <div class="sec-head sm rv mt-section"><h2>Where it was <em>shown</em></h2><a class="more" href="cv.html">Full CV</a></div>
    {rows([(y, esc(t), s) for y, t, s in shows])}
    <div class="actions"><a class="more" href="books.html#art-or-war">The book and films</a><a class="more" href="press.html">Press and video</a></div>
  </div>
</section>
{cta("Ask about Art or War", "For availability, commissions or exhibition loans, write to the studio.", "Available work")}
{pager("art-or-war.html")}
</main>"""
    return page("art-or-war.html", "Art or War · Viktor Mitic", "Art or War: Viktor Mitic's bullet-hole paintings, including Hole Jesus, Blasted Beaverbrook and Blasted Guernica.", body, og=U + hero["l"])


def build_dealers():
    g = ""
    works = DATA["dealers"] + [extra("untitled-1500x623-1.jpg", 500, 623)]
    for i, it in enumerate(works, 1):
        t = dealer_name(it["f"])
        g += tile(it, "dealers", (t + ". " if t else "") + "Portrait from Dealers by Viktor Mitic, Japanese ink on gold leaf", title=t, n=i)
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Dealers")], "Series · Japanese ink on gold leaf", "Dealers",
                 "Thirty-six portraits of Toronto's art dealers.") + f"""
<main id="main" tabindex="-1">
<section class="tight">
  <div class="wrap split top flush">
    <div class="rv"><span class="label">The idea</span><h2>The artist promotes <em>the dealer</em></h2></div>
    <div class="rv prose">
      <p>Dealers is a series of portraits in Japanese ink on gold leaf. It opened at Odon Wagner Contemporary in Toronto on December 11, 2009, Mitic's first solo show with the gallery, together with a book of the same name.</p>
      <p>The series turns the usual arrangement around. A dealer normally promotes the artist. Here the artist promotes the dealer.</p>
      <p>The book presents it as a portrait survey of the city's most distinctive dealers, each one caught in character: passionate, shrewd, eccentric or genial.</p>
      <p>Nine of the portraits are currently listed as available.</p>
      <a class="more" href="available-work.html#dealers">Available portraits</a>
      <a class="more" href="books.html#dealers">The book</a>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm"><h2>The <em>portraits</em></h2><span class="label">{len(works)} shown · select to enlarge</span></div>
    <div class="gal c5">{g}</div>
  </div>
</section>
{cta("Ask about Dealers", "For availability or prices of individual portraits, write to the studio.", "Available work")}
{pager("dealers.html")}
</main>"""
    return page("dealers.html", "Dealers · Viktor Mitic", "Dealers: 36 portraits of Toronto's art dealers by Viktor Mitic in Japanese ink on gold leaf.", body,
                og=U + "2017/10/Viktor-14Sep09_0047-prnt.jpg")
