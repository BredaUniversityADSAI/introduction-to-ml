"""Redirect pages for the old addresses of pages that moved (run by Quarto after rendering).

Pages moved twice:
- 13 Nov 2026 (NOV13): the Self-study pages moved into one folder per theme, numbered in course
  order, the overview pages became 00_overview.qmd, the Iteration 2 files were renumbered and
  "How to use this course" (start-here.qmd) became the Course Guide (course-guide.qmd).
- 15 Nov 2026 (NOV15): self-study/ and datalab/ became modules/, one folder per module with the
  module overview (00_overview.qmd), the Self-study (1_self_study/) and the DataLab iteration
  (2_datalab/), so that the menu, the Next links and the folders follow the course order. The
  top-level Self-study and DataLab overview pages were removed: their content went into the Course
  Guide and the overviews of Iterations 1 and 3.
Old links (bookmarks, other sites, Colab tabs) keep working: for every old address below, this script
writes a small page into the rendered site that forwards to the new address, keeping #anchors.
Notebooks get no `aliases:` front matter for this, so that the files learners open stay clean.
When a page moves again, add a table and chain it like NOV13 -> NOV15 below: a target that is
not a page any more is skipped silently.

Runs as `post-render` in _quarto.yml; by hand: python tools/old_page_urls.py _book
"""
import os
import posixpath
import sys
from pathlib import Path

S = "self-study"
D = "datalab"
M = {
    1: "modules/1_foundations",
    2: "modules/2_data_preparation",
    3: "modules/3_modeling_and_evaluation",
    4: "modules/4_advanced_scikit_learn",
    5: "modules/5_tree_based_algorithms",
    6: "modules/6_applied_ml_research",
}

NOV13 = {
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
    NOV13[f"{S}/theme-{n}.html"] = f"{S}/theme-{n}/00_overview.html"
    # The folder address (self-study/theme-1/) opens its overview.
    NOV13[f"{S}/theme-{n}/index.html"] = f"{S}/theme-{n}/00_overview.html"
    NOV13[f"datalab/iteration-{n}/index.html"] = f"datalab/iteration-{n}/00_overview.html"

NOV15 = {
    f"{D}/iteration-1/00_overview.html": f"{M[1]}/2_datalab/00_overview.html",
    f"{D}/iteration-1/01_business_understanding.html": f"{M[1]}/2_datalab/01_business_understanding.html",
    f"{D}/iteration-1/02_data_understanding.html": f"{M[1]}/2_datalab/02_data_understanding.html",
    f"{D}/iteration-1/03_classification.html": f"{M[1]}/2_datalab/03_classification.html",
    f"{D}/iteration-1/04_regression.html": f"{M[1]}/2_datalab/04_regression.html",
    f"{D}/iteration-1/05_clustering.html": f"{M[1]}/2_datalab/05_clustering.html",
    f"{D}/iteration-2/00_overview.html": f"{M[2]}/2_datalab/00_overview.html",
    f"{D}/iteration-2/01_understanding_smiles.html": f"{M[2]}/2_datalab/01_understanding_smiles.html",
    f"{D}/iteration-2/02_understanding_stability_data.html": f"{M[2]}/2_datalab/02_understanding_stability_data.html",
    f"{D}/iteration-2/03_understanding_homolumo_data.html": f"{M[2]}/2_datalab/03_understanding_homolumo_data.html",
    f"{D}/iteration-2/04_data_preparation.html": f"{M[2]}/2_datalab/04_data_preparation.html",
    f"{D}/iteration-2/05_baseline.html": f"{M[2]}/2_datalab/05_baseline.html",
    f"{D}/iteration-3/00_overview.html": f"{M[3]}/2_datalab/00_overview.html",
    f"{D}/iteration-3/01_classification.html": f"{M[3]}/2_datalab/01_classification.html",
    f"{D}/iteration-3/02_regression.html": f"{M[3]}/2_datalab/02_regression.html",
    f"{D}/iteration-3/03_clustering.html": f"{M[3]}/2_datalab/03_clustering.html",
    f"{D}/iteration-4/00_overview.html": f"{M[4]}/2_datalab/00_overview.html",
    f"{D}/iteration-5/00_overview.html": f"{M[5]}/2_datalab/00_overview.html",
    f"{D}/iteration-6/00_overview.html": f"{M[6]}/2_datalab/00_overview.html",
    f"{S}/theme-1/00_overview.html": f"{M[1]}/00_overview.html",
    f"{S}/theme-1/01_what_is_machine_learning.html": f"{M[1]}/1_self_study/01_what_is_machine_learning.html",
    f"{S}/theme-1/02_getting_started.html": f"{M[1]}/1_self_study/02_getting_started.html",
    f"{S}/theme-1/03_classification.html": f"{M[1]}/1_self_study/03_classification.html",
    f"{S}/theme-1/04_regression.html": f"{M[1]}/1_self_study/04_regression.html",
    f"{S}/theme-1/05_unsupervised_learning.html": f"{M[1]}/1_self_study/05_unsupervised_learning.html",
    f"{S}/theme-1/06_end_to_end_ml.html": f"{M[1]}/1_self_study/06_end_to_end_ml.html",
    f"{S}/theme-1/07_review.html": f"{M[1]}/1_self_study/07_review.html",
    f"{S}/theme-2/00_overview.html": f"{M[2]}/00_overview.html",
    f"{S}/theme-2/01_data_prep.html": f"{M[2]}/1_self_study/01_data_prep.html",
    f"{S}/theme-2/02_data_understanding.html": f"{M[2]}/1_self_study/02_data_understanding.html",
    f"{S}/theme-2/03_leakage_and_distribution_shift.html": f"{M[2]}/1_self_study/03_leakage_and_distribution_shift.html",
    f"{S}/theme-2/04_review.html": f"{M[2]}/1_self_study/04_review.html",
    f"{S}/theme-3/00_overview.html": f"{M[3]}/00_overview.html",
    f"{S}/theme-3/01_modeling_and_evaluation.html": f"{M[3]}/1_self_study/01_modeling_and_evaluation.html",
    f"{S}/theme-3/02_linear_regression.html": f"{M[3]}/1_self_study/02_linear_regression.html",
    f"{S}/theme-3/03_logistic_regression.html": f"{M[3]}/1_self_study/03_logistic_regression.html",
    f"{S}/theme-3/04_clustering.html": f"{M[3]}/1_self_study/04_clustering.html",
    f"{S}/theme-3/05_review.html": f"{M[3]}/1_self_study/05_review.html",
    f"{S}/theme-4/00_overview.html": f"{M[4]}/00_overview.html",
    f"{S}/theme-4/01_pipelines_and_columntransformer.html": f"{M[4]}/1_self_study/01_pipelines_and_columntransformer.html",
    f"{S}/theme-4/02_review.html": f"{M[4]}/1_self_study/02_review.html",
    f"{S}/theme-5/00_overview.html": f"{M[5]}/00_overview.html",
    f"{S}/theme-5/01_decision_trees.html": f"{M[5]}/1_self_study/01_decision_trees.html",
    f"{S}/theme-5/02_random_forests.html": f"{M[5]}/1_self_study/02_random_forests.html",
    f"{S}/theme-5/03_gradient_boosting.html": f"{M[5]}/1_self_study/03_gradient_boosting.html",
    f"{S}/theme-5/04_review.html": f"{M[5]}/1_self_study/04_review.html",
    f"{S}/theme-6/00_overview.html": f"{M[6]}/00_overview.html",
    f"{S}/theme-6/01_communicating_technical_work.html": f"{M[6]}/1_self_study/01_communicating_technical_work.html",
    f"{S}/theme-6/02_understanding_ml_research.html": f"{M[6]}/1_self_study/02_understanding_ml_research.html",
    f"{S}/theme-6/03_from_research_to_practice.html": f"{M[6]}/1_self_study/03_from_research_to_practice.html",
    f"{S}/theme-6/04_review.html": f"{M[6]}/1_self_study/04_review.html",
    # Removed overview pages.
    f"{S}/00_overview.html": "course-guide.html",
    f"{D}/00_overview.html": f"{M[1]}/2_datalab/00_overview.html",
    # Old addresses of the Iteration 3 notebooks (were `aliases:` in their front matter until 15 Nov 2026).
    f"{D}/iteration-2/04_classification.html": f"{M[3]}/2_datalab/01_classification.html",
    f"{D}/iteration-2/05_regression.html": f"{M[3]}/2_datalab/02_regression.html",
    f"{D}/iteration-2/06_clustering.html": f"{M[3]}/2_datalab/03_clustering.html",
}
for n, m in M.items():
    # Folder addresses (modules/1_foundations/ and its subfolders) open an overview.
    NOV15[f"{m}/index.html"] = f"{m}/00_overview.html"
    NOV15[f"{m}/1_self_study/index.html"] = f"{m}/00_overview.html"
    NOV15[f"{m}/2_datalab/index.html"] = f"{m}/2_datalab/00_overview.html"

OLD_TO_NEW = dict(NOV15)
for old, mid in NOV13.items():
    OLD_TO_NEW[old] = NOV15.get(mid, mid)

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
