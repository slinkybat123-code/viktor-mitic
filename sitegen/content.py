"""Shared data tables: captions, titles, videos, articles, films, 3D viewer settings."""

DEALER_NAMES = {"0096-prnt": "Jamie Angell, Angell Gallery", "0082-prnt": "Christopher Cutts, Christopher Cutts Gallery",
                "0064-prnt": "Olga Korper, Olga Korper Gallery", "0173-prnt-1": "Odon Wagner, Odon Wagner Gallery"}

SCULPT_CAPS = {
    "Screenshot_20210811": ("", "Studio shot of a 17 ft sculpture in stainless steel and 24k gold."),
    "9206d1df": ("Red-Gold", "Abstract forms with 24k gold accents, for indoors or outdoors."),
    "red-6": ("Red-Gold", ""), "red-gold-gold-plated": ("Red-Gold", "Gold-plated stainless steel."),
    "puff-samurai": ("Puff Samurai", ""),
    "hotel-elevator-lobby": ("", "View for a hotel elevator lobby."),
    "img_2016": ("", "In the studio, 2016."),
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

VIEWERS = [  # id (also the frame folder in img/3d/), tab label, name, original KeyShot folder, width, height, turn frames, tilt frames, start turn, start tilt
    ("sc1", "SC 1", "Sculpture 1", "final render_XR.29", 886, 582, 20, 10, 10, 1),
    ("sc2", "SC 2", "Sculpture 2", "Sculpt 2_XR.71", 800, 708, 18, 9, 9, 0),
    ("sc3", "SC 3", "Gold Top", "Gold top-colored_XR.39", 801, 605, 10, 10, 5, 0),
    ("sc4", "SC 4", "Sculpture 4", "Sculpt-3_XR.103", 800, 708, 10, 10, 5, 0),
    ("sc5", "SC 5", "Sculpture 5", "Model_XR.117", 801, 601, 10, 10, 5, 1),
]

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

FILMS = [("Point Blank: Art or War", "Nora Stankovic · 6 min · Cannes Film Festival", "2016"), ("Gun Porn", "Brahm Rosensweig · 11 min · Hot Docs, Hulu", "2014"),
         ("Rain Dance", "Brahm Rosensweig · 14 min · Fourfront Editions", "2011"), ("Art or War", "Laurie Kwasnik · 12 min · Tightrope Books", "2010")]
