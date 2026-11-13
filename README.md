# Introduction to Machine Learning

A public, first-year machine learning course from the [Applied Data Science & AI](https://ai.buas.nl/) programme at Breda University of Applied Sciences (BUas).

You learn machine learning by solving a real problem. The client is the OMEGA Lab at KAUST, which is searching for molecules for next-generation organic solar cells. You build models that predict molecular properties from structure, so the lab can screen thousands of candidates computationally and only test the most promising ones.

The course has two parts:

- **Self-study**: learn the concepts, independently of the project. Jupyter notebooks and reading pages in six themes: Theme 1 takes you through a small project from start to finish, and the other themes go deeper into data preparation, modeling and evaluation, scikit-learn pipelines, tree-based models and applied ML research.
- **DataLab**: apply what you learned to the real client challenge. You work with real molecular data (the HOPV dataset) and improve your solution through six CRISP-DM iterations, with less guidance in each one. You predict properties of 200 unseen test molecules and score them with the scorer in this repository.

The on-campus course also assesses deliverables such as reports and presentations. This public version is adapted for independent learning without supervision or formal grading, so the test set is the main way to evaluate your solution.

📖 **Course website:** <https://ai.buas.nl/open-courses/introduction-to-ml/>

> **Early release (v0.7).** The course is complete enough to learn from but still being finished: pages may change. You can [score your predictions](https://ai.buas.nl/open-courses/introduction-to-ml/datalab/iteration-3/00_overview.html#scoring-your-predictions) on the test set at any time. See [What's new](https://ai.buas.nl/open-courses/introduction-to-ml/whats-new.html).
>
> **BUas students:** follow your course in the BUas learning environment. The data, deadlines and Kaggle competitions there differ from this public version.

## Getting started

New to the course? Start with the [Course Guide](https://ai.buas.nl/open-courses/introduction-to-ml/course-guide.html): how the course works, the recommended order and setup, and where to get help.

The course is designed to be done on your own computer, in your own copy of this repository. The full step-by-step guide, with troubleshooting, is [Set Up Your Computer](https://ai.buas.nl/open-courses/introduction-to-ml/setup.html). In short:

1. Click "Use this template" > "Create a new repository" and make a private copy of the course in your GitHub account.
2. Clone your copy, for example in [VS Code](https://code.visualstudio.com/) with "Git: Clone" > "Clone from GitHub".
3. In the course folder, install Python and the packages with [uv](https://docs.astral.sh/uv/getting-started/installation/):

   ```bash
   uv sync   # installs Python 3.13 and every package the course uses into .venv/
   ```

4. In VS Code, install the extensions it recommends (Python, Jupyter and, optionally, Quarto), open a notebook and select the `.venv` kernel.

Save your work by committing and pushing to your copy. Your copy keeps the course version you started with: finish the course with it.

`rdkit` is pinned to version 2025.9.3 on purpose: the course data was prepared with it. On macOS, `xgboost` and `lightgbm` may need `brew install libomp`.

Questions? Ask in the [Discussions](https://github.com/BredaUniversityADSAI/introduction-to-ml/discussions).

## The course route

The course has six steps. Each step is a Self-study theme, followed by the DataLab iteration with the same number.

| Step | Self-study | DataLab |
|---|---|---|
| 1 | [Theme 1: Foundations of Machine Learning](self-study/theme-1/00_overview.qmd) | [Iteration 1: first ML cycle](datalab/iteration-1/00_overview.qmd) |
| 2 | [Theme 2: Data Preparation & Understanding](self-study/theme-2/00_overview.qmd) | [Iteration 2: your own dataset](datalab/iteration-2/00_overview.qmd) |
| 3 | [Theme 3: Modeling & Evaluation](self-study/theme-3/00_overview.qmd) | [Iteration 3: better evaluation, first submission](datalab/iteration-3/00_overview.qmd) |
| 4 | [Theme 4: Advanced Scikit-Learn](self-study/theme-4/00_overview.qmd) | [Iteration 4: streamlined code, new data](datalab/iteration-4/00_overview.qmd) |
| 5 | [Theme 5: Tree-Based Algorithms](self-study/theme-5/00_overview.qmd) | [Iteration 5: better models](datalab/iteration-5/00_overview.qmd) |
| 6 | [Theme 6: Applied ML Research](self-study/theme-6/00_overview.qmd) | [Iteration 6: your final solution](datalab/iteration-6/00_overview.qmd) |

Every theme and iteration has its own folder. In each folder, the files are numbered in the order you work through them, starting with the overview `00_overview.qmd`.

- The `.ipynb` files are Jupyter notebooks: open them in VS Code and run them.
- The `.qmd` files are pages of the course website. Read them on the website, where the figures, videos and interactive parts work: each file starts with its web address.

## Repository structure

```
self-study/   Self-study, one folder per theme (theme-1/ to theme-6/)
datalab/      DataLab project, one folder per iteration (iteration-1/ to iteration-6/)
data/         Datasets: raw HOPV data, the lab database, the starter dataset, the test molecules (see data/README.md)
tools/        The scorer for your test-set predictions (score.py) and the course's own checks
models/       Models you save while working through the notebooks (not tracked by Git)
images/       Figures used in the notebooks and on the website
```

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
