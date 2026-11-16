"""Books and films, curriculum vitae, collector acquisitions."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


def build_books():
    own = [
        ("dealers", "01 · 2009", "Dealers", "The 36 portraits of Toronto's art dealers. Introduction by Gary Michael Dault. Tightrope Books.", "https://www.amazon.ca/Dealers-Viktor-Mitic/dp/1926639146", "dealers.html", ("dealersbook2.jpg", 130, 177)),
        ("art-or-war", "02 · 2010", "Art or War", "Bullet hole paintings by Viktor Mitic. Introduction by Jim Nason. Tightrope Books.", "https://www.amazon.ca/Art-War-Paintings-Viktor-Mitic/dp/1926639154", "art-or-war.html", ("artofwarbook2.jpg", 170, 177)),
        ("rain-dance", "03 · 2011", "Rain Dance", "Reproductions of the rain paintings, with Galaxy on the cover, published with a DVD. Fourfront Editions.", "https://www.amazon.com/Rain-Dance-DVD-Viktor-Mitic/dp/1926802667", "rain-dance.html", ("raindancebook2.jpg", 181, 177)),
    ]
    own_html = "".join(
        f'<div class="book" id="{i}"><img loading="lazy" src="{U2}{cover}" width="{cw}" height="{ch}" alt="Cover of the book {t}">'
        f'<span class="n">{n}</span><h3>{t}</h3><p>{p}</p>'
        f'<a class="more" href="{buy}" target="_blank" rel="noopener">Find the book</a><a class="more" href="{series}">See the series</a></div>' for i, n, t, p, buy, series, (cover, cw, ch) in own)
    poster = by_file("war", "Viktor-hirez")
    essays = [("2021", "<em>Shifting Paradigms: Essays on Art and Culture</em>", "Guernica Editions. Includes an extensive essay on Mitic's work."),
              ("2018", "<em>Cagdas Sanat Ve Yeniden Uretim</em>", "Hayalaperest Yayinevi. Includes an extensive essay on Mitic's work."),
              ("2017", "<em>Desire Lines</em>", "Guernica Editions. Includes an extensive essay on Mitic's work.")]
    body = phero([("index.html", "Home"), (None, "Books & films")], "Publications", "Books &amp; films",
                 "Three books of the work, three books that write about it, and four short films.") + f"""
<main id="main" tabindex="-1">
<section class="tight pt0">
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
    <div class="film rv">
      <article class="video"><div class="frame"><button type="button" data-vimeo="178039534" aria-label="Play: Point Blank: Art or War, a film by Nora Stankovic">
        <img loading="lazy" src="{U}{poster["l"]}" alt=""></button></div></article>
      <div>
        <span class="label">Watch · 6 minutes</span>
        <h3>Point Blank: Art or War</h3>
        <p>A short film by Nora Stankovic, shown at the Cannes Film Festival in 2016. It plays from Vimeo when you press play.</p>
        <a class="more" href="https://vimeo.com/178039534" target="_blank" rel="noopener">Open on Vimeo</a>
      </div>
    </div>
    <div class="films rv mt0">{films_html()}</div>
  </div>
</section>
</main>"""
    return page("books.html", "Books & films · Viktor Mitic", "Books and films by and about Viktor Mitic: Dealers, Art or War, Rain Dance, Gun Porn and Point Blank.", body)


def build_cv():
    public = [("2024", "<em>Space Lounger</em>", "Suncoast Science Center, Sarasota, Florida"), ("2021", "<em>Heartland</em>", "Port Moody, British Columbia, Canada"), ("2019", "<em>Purple Heart</em>", "Moot Manor of Sri Lanka, Colombo, Sri Lanka"),
              ("2018", "<em>Lyric Star</em>", "Marriott Hotel, Markham, Ontario, Canada"), ("2018", "<em>The Music Garage</em>", "Marriott Hotel, Markham, Ontario, Canada"),
              ("2018", "<em>Hypervelocity Asteroid</em>", "Rochester Car Museum, Rochester, New York"), ("2018", "<em>Death Flower</em>", "Elizabeth Collection, Rochester, New York"),
              ("2015", "<em>Blasted Guernica</em>", "Remington Contemporary Art Museum, Markham, Ontario, Canada")]
    collections = [("2018", "Biggs Museum of American Art", "Dover, Delaware. Work in the permanent collection."),
                   ("2015", "Elizabeth Collection", "Rochester, New York. Collection of paintings and sculptures."),
                   ("2015", "Remington Contemporary Art Museum", "Markham, Ontario. Work in the permanent collection."),
                   ("2009", "Beaverbrook Art Gallery", "Fredericton, New Brunswick. Work in the permanent collection.")]
    shows = [("2025", "Canadian Sculpture Centre", "New Members, Sculptors Society of Canada, Toronto, Ontario"),
             ("2024", "Arts Advocates Gallery", "Artist talk, Art or War and So Much More, Sarasota, Florida"),
             ("2022", "Oeno Gallery", "small spaces BIG IDEAS, Bloomfield, Ontario (Prince Edward County)"), ("2021", "Art Toronto", "Toronto, Ontario"),
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
    memberships = [("2025", "Sculptors Society of Canada", "Member. Exhibited with the society at the Canadian Sculpture Centre, Toronto.")]
    edu = [("1996", "Bachelor of Fine Art", "Fine art and art history. University of Toronto, Toronto, Ontario."),
           ("1995", "Fine Arts Diploma", "Fine art and art history. Sheridan College, Oakville, Ontario.")]
    e = lambda items: rows([(y, t if "<em>" in t else esc(t), s) for y, t, s in items])
    block = lambda h, content: f'<div class="cv-block rv"><h2>{h}</h2>{content}</div>'
    body = phero([("index.html", "Home"), (None, "Curriculum vitae")], "Viktor Mitic", "Curriculum vitae",
                 "Public art, collections, exhibitions, films, books, memberships and education.") + f"""
<main id="main" tabindex="-1">
<section class="tight pt0">
  <div class="wrap">
    <div class="actions cv-actions"><button class="btn ghost small" type="button" data-print>Print or save as PDF</button><a class="btn ghost small" href="contact.html">Contact the studio</a></div>
    {block("Public <em>art</em>", e(public))}
    {block("Collections", e(collections))}
    {block("Shows", e(shows))}
    {block("Films", '<div class="films mt0">' + films_html() + "</div>")}
    {block("Books", e(books))}
    {block("Memberships", e(memberships))}
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
<main id="main" tabindex="-1">
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
