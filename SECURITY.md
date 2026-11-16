# Security

This is a static website: plain HTML, one stylesheet and one script, served by GitHub Pages.
There is no server code, database, login or admin panel to break into, and the contact form
does not send anything itself (it prepares an email in the visitor's own mail service).

What protects it:

- **Content Security Policy** on every page (`sitegen/config.py`). Browsers refuse any script,
  style, font, picture or frame that does not come from this site, apart from the YouTube and
  Vimeo players and YouTube's preview pictures. The one inline script is allowed by its hash.
- **No outside code.** Fonts, pictures and 3D frames are stored in this repository. No
  analytics, trackers or third-party scripts are loaded.
- **Checked before publishing.** GitHub Actions builds the site and runs `check.py` on every
  push. A page that breaks the policy, a missing file or a link to the old site stops the
  publish.
- **Locked-down workflow.** The workflow can only read the repository; only the publish job
  may write to GitHub Pages. Each action is pinned to an exact commit, and Dependabot proposes
  updates.
- **Protected branch.** `main` cannot be deleted or force-pushed.
- **Photos cleaned.** Camera data (which can include GPS position) was removed from the photos.

## Reporting a problem

Email info@artorwar.com, or use **Report a vulnerability** on the repository's Security tab.
Please do not open a public issue for a security problem.
