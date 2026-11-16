"""Press, television and newspaper clippings."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


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
    clips = [("viktormitic_torontostar_cover_april10_132.jpg", 225, 433, "Toronto Star, front page, April 10, 2013"),
             ("globe-300x267-1.jpg", 300, 267, "The Globe and Mail, Globe Review"),
             ("nationalpost-326x540-1.jpg", 260, 431, "National Post"),
             ("dailymail2.jpg", 196, 433, "Daily Mail"),
             ("telegraph-661x12002-1.jpg", 239, 433, "Telegraph-Journal"),
             ("dynamic_resize-248x3002-1.jpg", 225, 272, "Toronto Sun, front page"),
             ("huffington-post2.jpg", 294, 473, "The Huffington Post")]
    body = phero([("index.html", "Home"), (None, "Press & video")], "Media coverage", "In the press",
                 "Television, newspapers and magazines on the bullet paintings, the bus and the sculptures.", U + inc["l"], "Incident, the bullet-riddled school bus") + f"""
<main id="main" tabindex="-1">
<section class="tight">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>On <em>television</em></h2><span class="label">{len(VIDEOS)} videos</span></div>
    <div class="videos">{vids}</div>
    <p class="note">Videos play from YouTube when you press play. When Incident went to Washington, the story also ran on CBS, ABC and MSNBC, and in Canada on CTV.</p>
  </div>
</section>
<section class="tight pt0">
  <div class="wrap">
    <div class="sec-head sm rv"><h2>In the <em>papers</em></h2><span class="label">{len(clips)} clippings · select to enlarge</span></div>
    {shots(clips, "clips", "tall")}
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
      <p>For interviews, images and information, write to <a class="mail in-text" href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <p>Release images of recent collector acquisitions are available for media use.</p>
      <a class="more" href="acquisitions.html">Collector acquisitions and images</a>
      <a class="more" href="contact.html?topic=Press">Contact page</a>
    </div>
  </div>
</section>
</main>"""
    return page("press.html", "Press & video · Viktor Mitic", "Press coverage and television interviews with Viktor Mitic: BBC, CBC, Fox News, The Globe and Mail, The Washington Post and more.", body, og=U + inc["l"])
