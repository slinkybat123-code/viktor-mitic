"""Contact page and the page-not-found page."""
from html import escape as esc  # noqa: F401
from urllib.parse import quote  # noqa: F401

from ..config import *  # noqa: F401,F403  site settings
from ..content import *  # noqa: F401,F403  shared data tables
from ..layout import page  # noqa: F401
from ..parts import *  # noqa: F401,F403  building blocks


def build_contact():
    body = phero([("index.html", "Home"), (None, "Contact")], "Enquire", "Contact",
                 "Ask about available work, commissions, exhibitions or press. The studio replies by email.") + f"""
<main id="main" tabindex="-1">
<section class="tight pt0">
  <div class="wrap contact">
    <div>
      <h2>Write to <em>the studio</em></h2>
      <p>Email is the quickest way to reach us. Use the form to have your message written out for you, or copy the address below.</p>
      <div class="direct">
        <span class="label">Email</span><br>
        <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a>
        <div class="actions">
          <button class="btn ghost small" type="button" data-copy-email="copyStatus">Copy address</button>
          <a class="btn ghost small" href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to={EMAIL}" target="_blank" rel="noopener">Open Gmail</a>
        </div>
        <p class="status" id="copyStatus" role="status"></p>
      </div>
      <dl class="facts">
        <div><dt>Studios</dt><dd>Toronto, Ontario · Sarasota, Florida</dd></div>
        <div><dt>Gallery</dt><dd><a class="inline" href="{OENO}" target="_blank" rel="noopener">Oeno Gallery</a>, Prince Edward County, Ontario</dd></div>
        <div><dt>Quote a reference</dt><dd>Each piece on the <a class="inline" href="available-work.html">available work</a> page has a number such as AW-12.</dd></div>
      </dl>
    </div>
    <form class="enq" id="enquiry" novalidate>
      <div class="two">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required aria-describedby="err-name"><span class="err" id="err-name" role="alert"></span></div>
        <div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="err-email"><span class="err" id="err-email" role="alert"></span></div>
      </div>
      <div class="two">
        <div class="field"><label for="f-topic">Subject</label>
          <select id="f-topic" name="topic"><option>Available work</option><option>Commission</option><option>Exhibition or loan</option><option>Press</option><option>Other</option></select></div>
        <div class="field"><label for="f-ref">Work reference (optional)</label><input id="f-ref" name="ref" placeholder="AW-12" maxlength="80"></div>
      </div>
      <div class="field"><label for="f-message">Message</label><textarea id="f-message" name="message" required aria-describedby="err-message"></textarea><span class="err" id="err-message" role="alert"></span></div>
      <div><button class="btn fill" type="submit">Prepare my message</button></div>
      <p class="status" id="formStatus" role="status"></p>
      <div class="send" id="send" hidden>
        <p>This page does not send email itself. Pick the mail service you use and your message opens there, ready to send.</p>
        <div class="actions">
          <a class="btn fill small" id="viaGmail" href="#" target="_blank" rel="noopener">Gmail</a>
          <a class="btn ghost small" id="viaOutlook" href="#" target="_blank" rel="noopener">Outlook</a>
          <a class="btn ghost small" id="viaYahoo" href="#" target="_blank" rel="noopener">Yahoo Mail</a>
          <a class="btn ghost small" id="viaApp" href="#">Mail app</a>
          <button class="btn ghost small" id="copyMsg" type="button">Copy message</button>
        </div>
      </div>
    </form>
  </div>
</section>
</main>"""
    return page("contact.html", "Contact · Viktor Mitic", "Contact Viktor Mitic's studio about available work, commissions, exhibitions and press.", body)


def build_404():
    body = phero([("index.html", "Home"), (None, "Page not found")], "404", "Nothing hangs here",
                 "That page does not exist. Try one of these instead.") + """
<main id="main" tabindex="-1">
<section class="tight pt0"><div class="wrap"><h2 class="sr">Pages to try</h2><div class="actions mt0">
<a class="btn fill" href="index.html">Home</a><a class="btn ghost" href="available-work.html">Available work</a><a class="btn ghost" href="contact.html">Contact</a>
</div></div></section>
</main>"""
    return page("404.html", "Page not found · Viktor Mitic", "Page not found.", body)
