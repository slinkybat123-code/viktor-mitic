"""Builds the Viktor Mitic website into the _site/ folder.

Run:  python build.py     (then python check.py)

The page text lives in sitegen/pages/, shared tables in sitegen/content.py,
image lists in data/site.json, styles and script in assets/.
GitHub Actions runs this on every push to main and publishes _site/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sitegen import build_all  # noqa: E402

if __name__ == "__main__":
    build_all()
