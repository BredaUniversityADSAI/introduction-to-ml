"""Redirect pages for the old addresses of pages that moved (run by Quarto after rendering).

On 13 Nov 2026 the Self-study pages moved into one folder per theme, numbered in course order,
the overview pages became 00_overview.qmd, the Iteration 2 files were renumbered and
"How to use this course" (start-here.qmd) became the Course Guide (course-guide.qmd). Old links
(bookmarks, other sites, Colab tabs) keep working: for every old address below, this script
writes a small page into the rendered site that forwards to the new address, keeping #anchors.
Notebooks get no `aliases:` front matter for this, so that the files learners open stay clean.

Runs as `post-render` in _quarto.yml; by hand: python tools/old_page_urls.py _book
"""
import os
import posixpath
import sys
from pathlib import Path

S = "self-study"
OLD_TO_NEW = {
    f"{S}/index.html": f"{S}/00_overview.html",
    f"{S}/00_what_is_machine_learning.html": f"{S}/theme-1/01_what_is_machine_learning.html",
    f"{S}/001_getting_started.html": f"{S}/theme-1/02_getting_started.html",
    f"{S}/002_classification.html": f"{S}/theme-1/03_classification.html",
    f"{S}/003_regression.html": f"{S}/theme-1/04_regression.html",
    f"{S}/004_unsupervised_learning.html": f"{S}/theme-1/05_unsupervised_learning.html",
    f"{S}/015_end_to_end_ml.html": f"{S}/theme-1/06_end_to_end_ml.html",
    f"{S}/005_data_prep.html": f"{S}/theme-2/01_data_prep.html",
    f"{S}/006_data_understanding.html": f"{S}/theme-2/02_data_understanding.html",
    f"{S}/12_leakage_and_distribution_shift.html": f"{S}/theme-2/03_leakage_and_distribution_shift.html",
    f"{S}/007_modeling_and_evaluation.html": f"{S}/theme-3/01_modeling_and_evaluation.html",
    f"{S}/012_linear_regression.html": f"{S}/theme-3/02_linear_regression.html",
    f"{S}/013_logistic_regression.html": f"{S}/theme-3/03_logistic_regression.html",
    f"{S}/014_clustering.html": f"{S}/theme-3/04_clustering.html",
    f"{S}/008_advanced_scikitlearn.html": f"{S}/theme-4/01_pipelines_and_columntransformer.html",
    f"{S}/009_decision_trees.html": f"{S}/theme-5/01_decision_trees.html",
    f"{S}/010_random_forests.html": f"{S}/theme-5/02_random_forests.html",
    f"{S}/011_gradient_boosting.html": f"{S}/theme-5/03_gradient_boosting.html",
    f"{S}/09_communicating_technical_work.html": f"{S}/theme-6/01_communicating_technical_work.html",
    f"{S}/10_understanding_ml_research.html": f"{S}/theme-6/02_understanding_ml_research.html",
    f"{S}/11_from_research_to_practice.html": f"{S}/theme-6/03_from_research_to_practice.html",
    "start-here.html": "course-guide.html",  # "How to use this course", renamed 13 Nov 2026
    "datalab/index.html": "datalab/00_overview.html",
    "datalab/iteration-2/00_understanding_smiles.html": "datalab/iteration-2/01_understanding_smiles.html",
    "datalab/iteration-2/01_understanding_stability_data.html": "datalab/iteration-2/02_understanding_stability_data.html",
    "datalab/iteration-2/02_understanding_homolumo_data.html": "datalab/iteration-2/03_understanding_homolumo_data.html",
    "datalab/iteration-2/03_data_preparation.html": "datalab/iteration-2/04_data_preparation.html",
    "datalab/iteration-2/04_baseline.html": "datalab/iteration-2/05_baseline.html",
}
for n in range(1, 7):
    OLD_TO_NEW[f"{S}/theme-{n}.html"] = f"{S}/theme-{n}/00_overview.html"
    # The folder address (self-study/theme-1/) opens its overview.
    OLD_TO_NEW[f"{S}/theme-{n}/index.html"] = f"{S}/theme-{n}/00_overview.html"
    OLD_TO_NEW[f"datalab/iteration-{n}/index.html"] = f"datalab/iteration-{n}/00_overview.html"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>This page has moved</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{t}">
<meta http-equiv="refresh" content="0; url={t}">
<script>location.replace("{t}" + location.search + location.hash);</script>
</head>
<body>
<p>This page has moved to <a href="{t}">{t}</a>.</p>
</body>
</html>
"""

out = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_book"))
root = Path(__file__).resolve().parent.parent
for old, new in OLD_TO_NEW.items():
    stem = old[: -len(".html")]
    if (root / f"{stem}.qmd").exists() or (root / f"{stem}.ipynb").exists():
        sys.exit(f"old_page_urls.py: {old} is a page again; remove it from OLD_TO_NEW")
    if not (out / new).exists():
        continue  # partial render (quarto preview of one page): the new page is not there yet
    target = posixpath.relpath(new, posixpath.dirname(old))
    dest = out / old
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(PAGE.format(t=target), encoding="utf-8")
