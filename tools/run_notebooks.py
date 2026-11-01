"""Runs notebooks from a fresh kernel and fails if a cell raises an error.

The exercise cells are left as they are (`# YOUR CODE HERE`): the self-study notebooks are
written so that the provided code runs without the learner's answers.

usage:
  python tools/run_notebooks.py self-study/0*.ipynb            # check only, files unchanged
  python tools/run_notebooks.py --write self-study/005_*.ipynb  # also store the outputs in the file
"""
import argparse
import json
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4.rwbase import split_lines

parser = argparse.ArgumentParser()
parser.add_argument("notebooks", nargs="+")
parser.add_argument("--write", action="store_true", help="store the outputs in the notebook files")
args = parser.parse_args()

repo = str(Path.cwd().resolve())
home = str(Path.home())
failed = False
for path in args.notebooks:
    p = Path(path)
    nb = nbformat.read(p, as_version=4)
    start = time.time()
    client = NotebookClient(nb, timeout=1200, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": str(p.parent)}})
    client.execute()
    errors = [(i, o.get("ename"), o.get("evalue", "")[:120])
              for i, c in enumerate(nb.cells) if c.cell_type == "code"
              for o in c.get("outputs", []) if o.get("output_type") == "error"]
    text = json.dumps([c.get("outputs", []) for c in nb.cells if c.cell_type == "code"])
    local_paths = repo in text or home in text
    print(f"{p}: {time.time() - start:.0f} s, {len(errors)} error(s)" + (", LOCAL PATHS IN OUTPUT" if local_paths else ""))
    for e in errors:
        print("   cell", *e)
    failed |= bool(errors)
    if args.write:
        if errors or local_paths:
            print("   not written")
            failed = True
            continue
        for c in nb.cells:
            c.metadata.pop("execution", None)
        # sources and outputs as lists of lines, like the rest of the repository
        p.write_text(json.dumps(split_lines(nb), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

sys.exit(1 if failed else 0)
