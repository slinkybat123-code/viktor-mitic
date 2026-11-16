"""News: dated updates from 2023 on, newest first. Add new items at the top of NEWS."""
from html import escape as esc

from ..config import U
from ..layout import page
from ..parts import by_file, cta, phero

# (year, when, headline, text, link, link label). Text may contain <em>; links open in a new tab
# unless they point at a page of this site.
NEWS = [
    ("2026", "April", "A feature on the post-Pop sculptures",
     "Canadian Art Junkie publishes a feature on the recent sculptures, among them the 2025 <em>XoX</em> Kiddo figures in painted resin and <em>Halcyon Gold</em>, a 7 ft piece in gold-finished stainless steel.",
     "https://canadianartjunkie.com/2026/04/04/viktor-mitics-post-pop-sculptures/", "Read the feature"),
    ("2025", "Spring", "New Members at the Canadian Sculpture Centre",
     "Mitic joins the Sculptors Society of Canada and shows <em>Hydra</em>, a towering sculpture in 24k gold-plated stainless steel, in the society's New Members exhibition at the Canadian Sculpture Centre in Toronto.",
     "https://www.sculptorssocietyofcanada.org/viktor-mitic/", "Member profile"),
    ("2025", "New work", "Corten, gold and colour",
     "New pieces this year include <em>Sirius No 2</em> in Corten steel, <em>Astra Yellow</em> and <em>Halcyon Gold</em> in stainless steel, and new <em>XoX</em> Kiddo figures.",
     "contact.html?topic=Available%20work", "Ask about new work"),
    ("2024", "May", "Space Lounger lands in Sarasota",
     "The 20 ft <em>Space Lounger</em> is installed at the Suncoast Science Center in Sarasota, Florida.",
     "https://www.srqmagazine.com/srq-daily/2024-05-16/24277_The-Space-Lounger-Lands-at-Suncoast-Science-Center", "SRQ Daily"),
    ("2024", "New work", "Bronze and black marble",
     "Outdoor works cast in bronze, <em>Cygnus A</em> and <em>Titan</em>, and carved totems in Spanish black marble, <em>Halcyon</em> and the <em>Elemental</em> series.",
     "contact.html?topic=Available%20work", "Ask about these works"),
    ("2024", "January 26", "Art or War and So Much More",
     "An artist talk at the Arts Advocates Gallery at the Crossings at Siesta Key, Sarasota, on the bullet paintings and the work that followed.",
     "https://www.artsadvocates.org/component/eventbooking/gallery/248-art-talk-viktor-mitic-art-or-war-and-so-much-more", "Arts Advocates"),
    ("2023", "May", "Getting people talking",
     "SRQ Magazine profiles the studio and sculpture garden on Siesta Key, and the plan for a 20 ft stainless steel <em>XOX</em> painted bright yellow.",
     "https://www.srqmagazine.com/articles/1834/Getting-People-Talking", "SRQ Magazine"),
    ("2023", "February 3", "Sculptures find new homes",
     "Collectors in Sonoma, Port Moody and New Jersey acquire sculptures, and the work reaches Doha and Colombo.",
     "acquisitions.html", "The announcement"),
]


def build_news():
    items = ""
    for year, when, head, text, link, label in NEWS:
        outside = link.startswith("http")
        attrs = ' target="_blank" rel="noopener"' if outside else ""
        items += (f'<li class="rv"><span class="yr">{year}<span class="when">{esc(when)}</span></span>'
                  f'<div><h2>{esc(head)}</h2><p>{text}</p><a class="more" href="{esc(link)}"{attrs}>{esc(label)}</a></div></li>')
    hero = by_file("media", "heartland-oeno")
    body = phero([("index.html", "Home"), (None, "News")], "From the studio", "News",
                 "New work, exhibitions and coverage since 2023, newest first.") + f"""
<main id="main" tabindex="-1">
<section class="tight pt0">
  <div class="wrap">
    <ul class="news">{items}</ul>
    <p class="note">For older exhibitions, collections and films, see the <a class="inline" href="cv.html">curriculum vitae</a>.</p>
  </div>
</section>
{cta("Write to the studio", "For press, exhibitions or available work, the studio replies by email.", "Press")}
</main>"""
    return page("news.html", "News · Viktor Mitic", "News from Viktor Mitic's studio: new sculpture, exhibitions and coverage from 2023 to 2026.", body,
                og=U + hero["l"])
