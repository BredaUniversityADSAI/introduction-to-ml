# Introduction to Machine Learning

A public, first-year machine learning course from the [Applied Data Science & AI](https://ai.buas.nl/) programme at Breda University of Applied Sciences (BUas).

You learn machine learning by solving a real problem. The client is the OMEGA Lab at KAUST, which is searching for molecules for next-generation organic solar cells. You build models that predict molecular properties from structure, so the lab can screen thousands of candidates computationally and only test the most promising ones.

The course has three core components:

- **Self-study**: learn the concepts independently of the project. Jupyter notebooks and reading guides cover the fundamentals: classification, regression, clustering, the end-to-end ML workflow, scikit-learn pipelines, decision trees and ensembles.
- **DataLab**: apply what you learned to the real client challenge. You work with real molecular data (the HOPV dataset) and improve your solution through successive CRISP-DM iterations, with less guidance in each one.
- **Assessment**: demonstrate how well your solution performs. You predict properties of unseen molecules and submit them to a Kaggle competition, then use your score to evaluate and improve your model.

The on-campus course also assesses deliverables such as reports and presentations. This public version is adapted for independent learning without supervision or formal grading, so the Kaggle competition is the main way to evaluate your solution.

📖 **Course website:** <https://bredauniversityadsai.github.io/introduction-to-ml/>

## Local setup

The course is designed to be done on your own machine. The notebooks pass data and processed files between each other, so a local setup is the way to work through the course. The "Open in Colab" buttons on the website are only meant for a quick look at a notebook.

You need [Git](https://git-scm.com/downloads) and [uv](https://docs.astral.sh/uv/). uv installs the correct Python version and all packages for you, so you do not need to install Python separately.

### 1. Install uv

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal afterwards and check that it works with `uv --version`. Other installation options are listed in the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Get the course

```bash
git clone https://github.com/BredaUniversityADSAI/introduction-to-ml.git
cd introduction-to-ml
```

### 3. Install Python and the packages

```bash
uv python install   # installs Python 3.13 (the version in .python-version)
uv sync             # creates .venv/ and installs the packages from uv.lock
```

The environment contains everything the course uses, including `rdkit`, `optuna`, `xgboost`, `lightgbm` and `catboost`.

> **Note:** `rdkit` is pinned to exactly `2025.9.3`. Different RDKit versions can calculate some molecular descriptors slightly differently, and the course data was prepared with this version. Do not upgrade it.

On macOS, `xgboost` and `lightgbm` also need the OpenMP runtime, which uv cannot install. If importing them fails with a message about `libomp`, install it with [Homebrew](https://brew.sh/):

```bash
brew install libomp
```

### 4. Open the notebooks

Start Jupyter Lab from the project folder:

```bash
uv run jupyter lab
```

Or open the folder in VS Code (with the Python and Jupyter extensions), open a notebook, and select the `.venv` environment as the kernel.

### Adding packages

If you want to use a package that is not in the environment, run this from the project folder:

```bash
uv add <package-name>
```

Then restart the notebook kernel. Don't use `pip install` inside the notebooks: it skips `pyproject.toml` and `uv.lock`, so the package is lost the next time you run `uv sync`. Note that `uv add` changes `pyproject.toml` and `uv.lock`, so pulling later updates of this repository may then give a merge conflict in these files.

If something breaks, delete the `.venv` folder and run `uv sync` again.

## Repository structure

```
self-study/   Self-study notebooks (001_–011_) and reading guides (01_–11_)
datalab/      DataLab project notebooks, one folder per iteration
data/         Datasets: raw HOPV data, the starter dataset, Kaggle files
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

Every push to `main` is published to GitHub Pages automatically.

## Feedback

Found a mistake or something unclear? [Open an issue](https://github.com/BredaUniversityADSAI/introduction-to-ml/issues), or use "Report an issue" on any page of the website.
