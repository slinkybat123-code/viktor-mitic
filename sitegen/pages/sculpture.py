"""Sculptures and installations, and the 3D turntable page."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


def build_sculptures():
    g = ""
    works = DATA["sculpt"] + [extra("dsc_2058.jpg", 921, 518), extra("hotel-elevator-lobby-view_white-wall.jpg", 916, 512),
                              extra("img_20160522_132531-crop-u7615.jpg", 480, 339), extra("img_20160721_220325-crop-u7681.jpg", 480, 339),
                              extra("img_20160523_213644-crop-u7653.jpg", 480, 339)]
    bus = [("viktor_mitic_bus©john_drajewicz_0122.jpg", 268, 171, "Incident, the school bus"),
           ("viktor_mitic_bus©john_drajewicz_0007.jpg", 323, 242, "Incident, side view"),
           ("viktor_mitic_bus©john_drajewicz_0082208x156.jpg", 207, 156, "Incident, bullet holes in the bodywork"),
           ("viktor_mitic_bus©john_drajewicz_0067.jpg", 233, 311, "Incident, the shattered windscreen"),
           ("viktor_mitic_bus©john_drajewicz_0053.jpg", 210, 158, "Incident, detail of the side panel"),
           ("gun_porn_2-1024x575-1.jpg", 278, 156, "Incident in Washington, D.C., a still from the film Gun Porn")]
    story = [
        ("2012", "<em>The idea</em>", "With Toronto's Nuit Blanche approaching, Mitic wanted to take the bullet works somewhere new. He bought a yellow school bus and fired about 6,000 rounds into it. He named it Incident and thought of it as forensic evidence: a study of how closely violence and beauty now sit together."),
        ("2012", "<em>Nuit Blanche</em>", "The bus was moved to Todmorden Mills for the festival. Parents who saw it beforehand called the police, and the organisers asked that it stay covered until the night itself. It was on view for seven hours before he was asked to remove it."),
        ("2013", "<em>To Washington</em>", "After the Newtown school shooting, talks with peers led to a U.S. tour. Charles Krause, a Washington gallery owner and journalist, invited the bus to his gallery event The Newtown Project: Art Targets Guns."),
        ("2013", "<em>Around the city</em>", "Loaded onto a flatbed truck, Incident was parked and shown near the White House, in Georgetown, in Chinatown, in Adams Morgan and at George Mason University."),
        ("2013", "<em>Coverage</em>", "Fox News, CBS, ABC, MSNBC, The Washington Post and the Huffington Post ran feature stories, many with interviews. In Canada it was covered by the CBC, CTV, Global and the Toronto Star."),
        ("Since", "<em>Acquired</em>", "An American collector in New York State acquired the bus, and it remains there."),
    ]
    for i, it in enumerate(works, 1):
        t, c = lookup(SCULPT_CAPS, it["f"])
        g += tile(it, "sculpt", (t + ", " if t else "") + "sculpture by Viktor Mitic", title=t, cap=c, n=i)
    public = [
        ("2024", "<em>Space Lounger</em>", "Suncoast Science Center, Sarasota, Florida"),
        ("2021", "<em>Heartland</em>", "Port Moody, British Columbia"), ("2019", "<em>Purple Heart</em>", "Moot Manor of Sri Lanka, Colombo"),
        ("2018", "<em>Lyric Star</em>", "Marriott Hotel, Markham, Ontario"), ("2018", "<em>The Music Garage</em>", "Marriott Hotel, Markham, Ontario"),
        ("2018", "<em>Hypervelocity Asteroid</em>", "Rochester Car Museum, Rochester, New York"), ("2018", "<em>Death Flower</em>", "Elizabeth Collection, Rochester, New York"),
        ("2015", "<em>Blasted Guernica</em>", "Remington Contemporary Art Museum, Markham, Ontario"),
    ]
    hero = by_file("sculpt", "IMG_20220411_104605")
    inc = by_file("war", "cropped-incident-c.jpg")
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Sculptures & installations")], "Sculpture · Installation", "Shape in Space",
                 "Totems in steel, bronze and 24k gold, cut aluminum in car paint, and a school bus.", U + hero["l"], "Outdoor sculpture by Viktor Mitic on a beach") + f"""
<main id="main" tabindex="-1">
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
    <div class="sec-head sm"><h2>The <em>sculptures</em></h2><span class="label">{len(works)} images · select to enlarge</span></div>
    <div class="gal">{g}</div>
  </div>
</section>
<section class="banner" id="incident" aria-labelledby="incident-h">
  <img loading="lazy" alt="Incident, a bullet-riddled school bus by Viktor Mitic" src="{U}{inc["l"]}">
  <div class="wrap rv">
    <span class="label">Installation · 2013</span>
    <h2 id="incident-h">Incident</h2>
    <p>A school bus shot through with bullet holes. It premiered at Nuit Blanche in Toronto, then toured to Washington, D.C. in April 2013 during the U.S. gun debates. It is in the permanent collection of Artisan Works in Rochester, New York.</p>
    <div class="row"><a class="more" href="#incident-story">The full story</a><a class="more" href="press.html">Press and video</a></div>
  </div>
</section>
<section class="tight" id="incident-story">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Violence <em>as beauty</em></h2><span class="label">The story of Incident</span></div>
    <div class="story">
      <div class="rv">
        {shots(bus, "incident")}
        <p class="credit">Bus photographs © John Drajewicz. Select any photograph to enlarge it.</p>
      </div>
      <div class="rv">{rows(story)}</div>
    </div>
  </div>
</section>
<section class="feature tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>Public <em>art</em></h2><a class="more" href="cv.html">Full CV</a></div>
    {rows(public)}
  </div>
</section>
{cta("Commission or acquire a sculpture", "Works range from tabletop pieces to outdoor sculptures 16 feet tall. Write to the studio about available pieces and commissions.", "Commission")}
{pager("sculptures.html")}
</main>"""
    return page("sculptures.html", "Sculptures & installations · Viktor Mitic", "Sculptures and installations by Viktor Mitic: steel and 24k gold totems, cut aluminum, public art and Incident.", body, og=U + hero["l"])


def build_3d():
    tabs = "".join(
        f'<button class="chip" type="button" data-id="{i}" data-name="{esc(n)}" data-folder="{i}" data-w="{w}" data-h="{h}" '
        f'data-u="{u}" data-v="{v}" data-su="{su}" data-sv="{sv}" aria-pressed="false">{l}</button>' for i, l, n, f, w, h, u, v, su, sv in VIEWERS)
    body = phero([("index.html", "Home"), ("index.html#works", "Works"), (None, "Sculptures in 3D")], "Interactive", "Click &amp; Drag",
                 "Five sculptures you can turn. Drag across the image to rotate it, up and down to tilt it.") + f"""
<main id="main" tabindex="-1">
<section class="tight pt0">
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
