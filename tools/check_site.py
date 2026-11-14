"""Checks the rendered site in _book/: every local link and image resolves, and every
"Open in Colab" button points to a notebook that exists in the repository. Absolute links to the
course website (used in notebooks, so that VS Code opens the page instead of its source) must point
to a page that exists in _book/.

usage: python tools/check_site.py [_book]   (after `quarto render`; exits with 1 on a failure)
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_book")
COLAB = "https://colab.research.google.com/github/BredaUniversityADSAI/introduction-to-ml/blob/"
SITE = "https://ai.buas.nl/open-courses/introduction-to-ml/"
ATTR = re.compile(r'(?:href|src)="([^"]+)"')

broken, colab, pages = [], 0, 0
for page in sorted(site.rglob("*.html")):
    pages += 1
    html = page.read_text(encoding="utf-8", errors="replace")
    for url in ATTR.findall(html):
        if url.startswith(COLAB):
            colab += 1
            path = url[len(COLAB):].split("/", 1)[1]  # drop the branch or tag
            if not Path(unquote(path)).is_file():
                broken.append((page, url))
            continue
        if url.startswith(SITE):
            path = unquote(urlsplit(url).path)[len(urlsplit(SITE).path):]
            if not ((site / path).is_file() or (site / path / "index.html").is_file()):
                broken.append((page, url))
            continue
        if url.startswith(("http:", "https:", "mailto:", "#", "data:", "javascript:", "//", "{")):
            continue
        target = unquote(urlsplit(url).path)
        if not target:
            continue
        resolved = (page.parent / target).resolve()
        if not (resolved.is_file() or (resolved / "index.html").is_file()):
            broken.append((page, url))

for page, url in broken:
    print(f"BROKEN  {page.relative_to(site)}: {url}")
print(f"{pages} pages, {colab} Colab links, {len(broken)} broken link(s)")
sys.exit(1 if broken else 0)
