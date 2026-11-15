# Viktor Mitic website

Live at https://slinkybat123-code.github.io/viktor-mitic/

## How it is put together

| File | What it is |
|---|---|
| `build.py` | Generates every `.html` page. All page text lives here. |
| `data/site.json` | The image lists for each gallery. |
| `assets/site.css`, `assets/site.js` | The one stylesheet and the one script every page shares. |
| `site_meta.py` | Web address of the site, sharing tags, `sitemap.xml`, `robots.txt`. |
| `check.py` | Checks links, images and 3D frames. |

Artwork images and the 3D turntable frames are loaded from `artorwar.com/wp-content/`.

## Changing something

1. Edit the text in `build.py` (or the styles in `assets/`).
2. Run `python build.py`.
3. Run `python check.py`.
4. Commit and push to `main`. The site updates in about a minute.

The same check runs on GitHub after every push and every Monday. If an image
disappears from the old site, GitHub emails the repository owner.

## Moving to a custom domain

Change `SITE_URL` in `site_meta.py`, run `python build.py`, and push.
