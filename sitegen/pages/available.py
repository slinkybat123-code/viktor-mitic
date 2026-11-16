"""Available work, with the category filter."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


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
<main id="main" tabindex="-1">
<section class="tight pt0">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Filter by type">{chips}</div>
    <p class="count" id="count" aria-live="polite">Showing {total} of {total} works</p>
    <h2 class="sr">Works</h2>
    <div class="gal">{cards}</div>
    <p class="note">Prices, dimensions and availability are confirmed by the studio on request. Select any image to enlarge it. Works are also offered through <a class="inline" href="{OENO}" target="_blank" rel="noopener">Oeno Gallery</a>, which lists its current pieces and prices.</p>
  </div>
</section>
{cta("Found something?", "Send the reference number and we will reply with price, size and shipping details.", "Available work",
     ("index.html#works", "Browse the series"))}
</main>"""
    return page("available-work.html", "Available work · Viktor Mitic", "Paintings, sculptures and Dealers portraits by Viktor Mitic currently available from the studio.", body,
                og=U + by_file("avail", "PSX_20230408")["l"])
