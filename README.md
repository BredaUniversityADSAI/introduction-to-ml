# Introduction to Machine Learning

A public, first-year machine learning course from the [Applied Data Science & AI](https://ai.buas.nl/) programme at Breda University of Applied Sciences (BUas).

You learn machine learning by solving a real problem. The client is the OMEGA Lab at KAUST, which is searching for molecules for next-generation organic solar cells. You build models that predict molecular properties from structure, so the lab can screen thousands of candidates computationally and only test the most promising ones.

The course has three core components:

- **Self-study**: learn the concepts independently of the project. Jupyter notebooks and reading guides cover the fundamentals: classification, regression, clustering, the end-to-end ML workflow, scikit-learn pipelines, decision trees and ensembles.
- **DataLab**: apply what you learned to the real client challenge. You work with real molecular data (the HOPV dataset) and improve your solution through successive CRISP-DM iterations, with less guidance in each one.
- **Assessment**: demonstrate how well your solution performs. You predict properties of 200 unseen test molecules and score them with the scorer in this repository, then use your score to evaluate and improve your model.

The on-campus course also assesses deliverables such as reports and presentations. This public version is adapted for independent learning without supervision or formal grading, so the test set is the main way to evaluate your solution.

📖 **Course website:** <https://ai.buas.nl/open-courses/introduction-to-ml/>

> **Early release (v0.4).** The course is complete enough to learn from but still being finished: pages may change. You can [score your predictions](https://ai.buas.nl/open-courses/introduction-to-ml/datalab/iteration-3/index.html#scoring-your-predictions) on the test set at any time. See [What's new](https://ai.buas.nl/open-courses/introduction-to-ml/whats-new.html).
>
> **BUas students:** follow your course in the BUas learning environment. The data, deadlines and Kaggle competitions there differ from this public version.

## Getting started

New to the course? Start with [How to use this course](https://ai.buas.nl/open-courses/introduction-to-ml/start-here.html): paths for different learners, an 8-week plan and where to get help.

The course is designed to be done on your own computer. The full step-by-step guide, with troubleshooting, is [Set up your computer](https://ai.buas.nl/open-courses/introduction-to-ml/setup.html). In short, with [Git](https://git-scm.com/downloads) and [uv](https://docs.astral.sh/uv/getting-started/installation/) installed:

```bash
git clone https://github.com/BredaUniversityADSAI/introduction-to-ml.git
cd introduction-to-ml
uv sync              # installs Python 3.13 and every package the course uses into .venv/
uv run jupyter lab   # or open the folder in VS Code and select the .venv kernel
```

`rdkit` is pinned to version 2025.9.3 on purpose: the course data was prepared with it. On macOS, `xgboost` and `lightgbm` may need `brew install libomp`.

Questions? Ask in the [Discussions](https://github.com/BredaUniversityADSAI/introduction-to-ml/discussions).

## Repository structure

```
self-study/   Self-study notebooks (001_–011_) and reading guides (01_–11_)
datalab/      DataLab project notebooks, one folder per iteration
data/         Datasets: raw HOPV data, the lab database, the starter dataset, the test molecules (see data/README.md)
models/       Models you save while working through the notebooks (not tracked by Git)
images/       Figures used in the notebooks and on the website
```

The order of the activities is set on the website, not by the file names. Follow the course from the website sidebar.

## Building the website

Only needed if you want to work on the website itself. Install [Quarto](https://quarto.org/docs/get-started/), then run from the project folder:

```bash
quarto preview   # local preview with live reload
quarto render    # full build into _book/
```

The site at <https://ai.buas.nl/open-courses/introduction-to-ml/> is built from version tags: a tag `vX.Y.Z` builds
the site and attaches it to a GitHub Release, and the ADS&AI department site serves the release it
points to. Pushes to `main` only refresh the redirects from the old github.io address and run the
checks (`.github/workflows/check.yml`).

## License

You may use and adapt this course in your own teaching. The course content is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and the code under the MIT License; see
[LICENSE.md](LICENSE.md) for the details, how to give credit and what is not covered.
To cite the course, use [CITATION.cff](CITATION.cff) ("Cite this repository" on GitHub).

## Feedback

Found a mistake or something unclear? [Open an issue](https://github.com/BredaUniversityADSAI/introduction-to-ml/issues), or use "Report an issue" on any page of the website. Questions about the course material go to the [Discussions](https://github.com/BredaUniversityADSAI/introduction-to-ml/discussions).
