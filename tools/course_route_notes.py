"""Writes the "What comes next" note at the end of the last page of each part of the course route.

The course route (filters/course-route.yml) interleaves Self-study and DataLab: Theme n, then
Iteration n. On the website, filters/course-route.lua adds a "Next" callout to the last page of
each part. Learners who work in VS Code read the .ipynb and .qmd files themselves and never see
that callout, so this script writes a note into the files, between two HTML comments:

    <!-- course-route-note: ... -->
    ## What comes next
    ...
    <!-- /course-route-note -->

On the website, the filter removes everything between these comments and adds its callout instead.
Self-study notes do not name the DataLab (Self-study never refers to it): they point to the course
route in the README and on the website. DataLab notes name the next step.

usage:
  python tools/course_route_notes.py           # write or update the notes
  python tools/course_route_notes.py --check   # exit 1 if a note is missing or out of date (CI)
"""
import argparse
import json
import re
import sys
import uuid
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- course-route-note: written by tools/course_route_notes.py from filters/course-route.yml; on the website the Next callout replaces it -->"
END = "<!-- /course-route-note -->"
GUIDE = "https://ai.buas.nl/open-courses/introduction-to-ml/course-guide.html#the-course-route"


def relative(markdown, up):
    """Links in the route file are relative to the project root; make them relative to the page."""
    return re.sub(r"\]\((?![a-z][a-z0-9+.-]*:|#)", "](" + up, markdown)


def note(part, nxt, nsteps, up):
    if part["kind"] == "Self-study":
        body = (f"This is the end of Self-study Theme {part['step']}. If you follow the course route, you have "
                f"finished the first part of step {part['step']} of {nsteps}. The [course route]({up}README.md#the-course-route) "
                f"in the README lists the second part of the step (on the website: the [Course Guide]({GUIDE})).")
    else:
        folder = nxt["href"].rsplit("/", 1)[0]
        body = (f"This is the end of step {part['step']} of {nsteps} of the course route. Continue with step {nxt['step']}: "
                f"[{relative(nxt['title'], up)}]({up}{nxt['href']}), in the folder `{folder}/`. {relative(nxt['text'], up)}")
        if part.get("finish"):
            body = relative(part["finish"], up) + "\n\n" + body
    return f"{START}\n\n## What comes next\n\n{body}\n\n{END}"


def update_notebook(path, text):
    raw = path.read_text(encoding="utf-8")
    nb = json.loads(raw)
    lines = text.split("\n")
    source = [line + "\n" for line in lines[:-1]] + [lines[-1]]
    cells = [c for c in nb["cells"] if c["cell_type"] == "markdown" and "".join(c["source"]).startswith(START)]
    if cells:
        cells[0]["source"] = source
    else:
        nb["cells"].append({"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": source})
    return raw, json.dumps(nb, indent=1, ensure_ascii=False) + "\n"


def update_qmd(path, text):
    raw = path.read_text(encoding="utf-8")
    if START in raw:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: text, raw, flags=re.S)
    else:
        new = raw.rstrip("\n") + "\n\n" + text + "\n"
    return raw, new


parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true", help="only check, change nothing")
args = parser.parse_args()

steps = yaml.safe_load((ROOT / "filters/course-route.yml").read_text(encoding="utf-8"))["steps"]
parts = []
for i, step in enumerate(steps, start=1):
    for p in step["parts"]:
        parts.append(dict(p, step=i, kind=p["title"].split(",")[0]))

stale = []
for part, nxt in zip(parts, parts[1:]):
    path = ROOT / part["ends"]
    up = "../" * part["ends"].count("/")
    text = note(part, nxt, len(steps), up)
    old, new = (update_notebook if path.suffix == ".ipynb" else update_qmd)(path, text)
    if old != new:
        stale.append(part["ends"])
        if not args.check:
            path.write_text(new, encoding="utf-8")

if args.check:
    for s in stale:
        print("note missing or out of date:", s, "(run python tools/course_route_notes.py)")
    sys.exit(1 if stale else 0)
print(f"{len(parts) - 1} notes, {len(stale)} written:", *stale, sep="\n  ")
