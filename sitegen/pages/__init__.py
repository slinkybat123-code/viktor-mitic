"""One module per area of the site. ALL lists every page builder in build order."""
from .about import build_acquisitions, build_books, build_cv
from .available import build_available
from .contact import build_404, build_contact
from .home import build_index
from .news import build_news
from .press import build_press
from .sculpture import build_3d, build_sculptures
from .series import build_dealers, build_rain, build_war

ALL = [build_index, build_rain, build_war, build_dealers, build_sculptures, build_3d, build_available,
       build_news, build_press, build_books, build_cv, build_acquisitions, build_contact, build_404]
