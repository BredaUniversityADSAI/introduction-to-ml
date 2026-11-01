"""Turn a rendered site into redirect pages for the old GitHub Pages address.

    python tools/make_redirects.py _book _redirect

The course lives at https://ai.buas.nl/open-courses/introduction-to-ml/. GitHub Pages
(https://bredauniversityadsai.github.io/introduction-to-ml/) only forwards: for every page in
_book it writes a page with the same path that redirects to the same page on ai.buas.nl
(canonical link + meta refresh + JavaScript, keeping #anchors), plus a 404.html that forwards any
other path.
"""
import sys, html
from pathlib import Path

NEW = "https://ai.buas.nl/open-courses/introduction-to-ml/"
OLD_PREFIX = "/introduction-to-ml/"
src, out = Path(sys.argv[1]), Path(sys.argv[2])

def page(target):
    t = html.escape(target, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Introduction to Machine Learning has moved</title>
<link rel="canonical" href="{t}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={t}">
<script>location.replace({target!r} + location.hash);</script>
</head>
<body>
<p>This course has moved to <a href="{t}">{t}</a>.</p>
</body>
</html>
"""

n = 0
for f in sorted(src.rglob("*.html")):
    rel = f.relative_to(src).as_posix()
    target = NEW + ("" if rel == "index.html" else rel)
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page(target), encoding="utf-8")
    n += 1

# Any other path (old links to files, pages that no longer exist): forward with the same path.
(out / "404.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Introduction to Machine Learning has moved</title>
<meta name="robots" content="noindex">
<script>
  var p = location.pathname;
  if (p.indexOf({OLD_PREFIX!r}) === 0) p = p.slice({len(OLD_PREFIX)});
  location.replace({NEW!r} + p.replace(/^\\//, "") + location.search + location.hash);
</script>
</head>
<body>
<p>This course has moved to <a href="{NEW}">{NEW}</a>.</p>
</body>
</html>
""", encoding="utf-8")
print(f"{n} redirect pages + 404.html -> {out}")
