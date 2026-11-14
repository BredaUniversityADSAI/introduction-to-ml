"""Scores your predictions for the 200 test molecules.

usage (from the repository root):
    python tools/score.py SUBMISSION.csv              public score (100 of the 200 molecules)
    python tools/score.py SUBMISSION.csv --private    also the private score (the other 100)

From a notebook in datalab/iteration-N/:
    %run ../../tools/score.py SUBMISSION.csv

Start from one of the sample submissions in data/003_test_data/ and replace the placeholder values:
- classification_sample_submission.csv: id, smiles, stability (low, medium or high);
- regression_sample_submission.csv: id, smiles, homo, lumo (in eV).
The script recognises the task from the columns. Rows are matched on `id`; without an `id`
column they are matched on the SMILES.

Scores: stability with the macro-averaged F1 score (higher is better), HOMO and LUMO with the
mean absolute error over all homo and lumo predictions together (lower is better).

Every score is added to data/003_test_data/score_log.csv (Git ignores it). The log also records
when you first looked at the private score, and every later look starts with a warning: a test
score you have already seen, and then tuned against, no longer tells you how your model does on
unseen molecules.
"""
import argparse
import datetime
import gzip
import json
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parents[1]
TEST_DATA = ROOT / "data" / "003_test_data"
LABELS = Path(__file__).resolve().parent / "score_labels.json.gz"
LOG = TEST_DATA / "score_log.csv"
CLASSES = ["low", "medium", "high"]
TASKS = {
    "stability": {"columns": ["stability"], "sample": "classification_sample_submission.csv",
                  "metric": "macro-F1", "better": "higher is better"},
    "energy levels": {"columns": ["homo", "lumo"], "sample": "regression_sample_submission.csv",
                      "metric": "MAE over homo and lumo, in eV", "better": "lower is better"},
}


class SubmissionError(Exception):
    """A problem with the submission file, with a message that says how to fix it."""


def load_labels():
    with gzip.open(LABELS) as f:
        return pd.DataFrame(json.load(f)).drop(columns="about", errors="ignore").set_index("id")


def load_test_molecules():
    return pd.read_csv(TEST_DATA / TASKS["stability"]["sample"], usecols=["id", "smiles"])


def _examples(values, n=3):
    values = list(values)
    shown = ", ".join(str(v) for v in values[:n])
    return shown + (f" (and {len(values) - n} more)" if len(values) > n else "")


def detect_task(df):
    """Recognises the task from the column names, or raises a SubmissionError with a hint."""
    cols = set(df.columns)
    has = {task: set(spec["columns"]) <= cols for task, spec in TASKS.items()}
    if all(has.values()):
        raise SubmissionError("The file has both a stability column and homo/lumo columns. "
                              "Score one task per file: start from the sample submission of that task.")
    for task, ok in has.items():
        if ok:
            return task
    lower = {c.strip().lower(): c for c in df.columns}
    for task, spec in TASKS.items():
        if all(c in lower for c in spec["columns"]):
            pairs = [(lower[c], c) for c in spec["columns"] if lower[c] != c]
            wrong = ", ".join(repr(w) for w, _ in pairs)
            right = ", ".join(repr(r) for _, r in pairs)
            raise SubmissionError(f"Column names are case-sensitive: rename {wrong} to {right}.")
    raise SubmissionError(f"No target columns found (the file has {_examples(df.columns, 6)}). A stability "
                          "submission needs a column 'stability'; an energy-levels submission needs "
                          "'homo' and 'lumo'. Start from a sample submission in data/003_test_data/.")


def match_rows(df, molecules):
    """Returns the test ids of the submission's rows, matched on id or else on the SMILES."""
    notes = []
    if "id" in df.columns:
        ids = df["id"].astype(str).str.strip()
        known = set(molecules["id"])
        unknown = [i for i in ids if i not in known]
        if unknown:
            raise SubmissionError(f"{len(unknown)} id(s) are not test molecules: {_examples(unknown)}. "
                                  "Keep the id column of the sample submission unchanged.")
    elif "smiles" in df.columns:
        lookup = dict(zip(molecules["smiles"], molecules["id"]))
        ids = df["smiles"].astype(str).str.strip().map(lookup)
        if ids.isna().any():
            from rdkit import Chem, RDLogger
            RDLogger.DisableLog("rdApp.*")

            def canonical(s):
                mol = Chem.MolFromSmiles(s)
                return Chem.MolToSmiles(mol) if mol is not None else None

            canon = {canonical(s): i for s, i in lookup.items()}
            ids = ids.fillna(df["smiles"].astype(str).map(lambda s: canon.get(canonical(s))))
            notes.append("the file has no id column, so the rows were matched on the canonical SMILES. "
                         "Keep the id column of the sample submission in your files.")
        else:
            notes.append("the file has no id column, so the rows were matched on the SMILES. "
                         "Keep the id column of the sample submission in your files.")
        if ids.isna().any():
            missing = df.loc[ids.isna(), "smiles"]
            raise SubmissionError(f"{len(missing)} SMILES are not test molecules: {_examples(missing, 2)}. "
                                  "Start from the sample submission and keep its id column.")
    else:
        raise SubmissionError("The file has no id column (and no smiles column) to match the rows on. "
                              "Keep the id column of the sample submission.")
    dup = ids[ids.duplicated()].unique()
    if len(dup):
        raise SubmissionError(f"{len(dup)} molecule(s) appear more than once: {_examples(dup)}. "
                              "Give one prediction per molecule.")
    missing = sorted(set(molecules["id"]) - set(ids))
    if missing:
        raise SubmissionError(f"{len(missing)} of the {len(molecules)} test molecules have no prediction: "
                              f"{_examples(missing)}. Predict every molecule of the sample submission.")
    return ids.values, notes


def check_values(df, task):
    """Returns the predictions in a clean form, or raises a SubmissionError."""
    if task == "stability":
        raw = df["stability"]
        if raw.isna().any():
            raise SubmissionError(f"{int(raw.isna().sum())} stability prediction(s) are missing (empty or NaN).")
        values = raw.astype(str).str.strip()
        bad = values[~values.isin(CLASSES)]
        if len(bad):
            if bad.str.lower().isin(CLASSES).all():
                raise SubmissionError("Class names are case-sensitive: use low, medium and high in lowercase.")
            if pd.to_numeric(bad, errors="coerce").notna().all():
                raise SubmissionError("The stability column contains numbers: convert the class numbers back "
                                      "to the names low, medium and high (for example with the inverse_transform "
                                      "of the encoder you used).")
            raise SubmissionError(f"Unknown class name(s): {_examples(bad.unique())}. "
                                  "Use low, medium or high.")
        return pd.DataFrame({"stability": values.values})
    out = {}
    for col in TASKS[task]["columns"]:
        values = pd.to_numeric(df[col], errors="coerce")
        text = df[col][values.isna() & df[col].notna()]
        if len(text):
            raise SubmissionError(f"Column {col} contains values that are not numbers: {_examples(text.unique())}.")
        if values.isna().any():
            raise SubmissionError(f"{int(values.isna().sum())} {col} prediction(s) are missing (empty or NaN).")
        if not np.isfinite(values).all():
            raise SubmissionError(f"Column {col} contains infinite values.")
        out[col] = values.values
    return pd.DataFrame(out)


def prepare(df, molecules=None):
    """Validates a submission. Returns (task, predictions indexed by test id, notes)."""
    molecules = load_test_molecules() if molecules is None else molecules
    if len(df) == 0:
        raise SubmissionError("The file has no rows.")
    task = detect_task(df)
    ids, notes = match_rows(df, molecules)
    pred = check_values(df, task).set_index(pd.Index(ids, name="id"))
    if task == "energy levels" and (pred[["homo", "lumo"]] > 0).all(axis=None):
        notes.append("all predictions are positive, but HOMO and LUMO in this course are negative (in eV): "
                     "check the signs")
    return task, pred, notes


def compute_scores(task, pred, labels=None):
    """Returns {split: score} for 'public' and 'private' (and per-target MAE for energy levels)."""
    labels = load_labels() if labels is None else labels
    y = labels.loc[pred.index]
    scores = {}
    for split in ("public", "private"):
        m = (y["split"] == split).values
        if task == "stability":
            scores[split] = f1_score(y["stability"][m], pred["stability"][m], labels=CLASSES,
                                     average="macro", zero_division=0)
        else:
            err = np.abs(pred.loc[m, ["homo", "lumo"]].values - y.loc[m, ["homo", "lumo"]].values)
            scores[split] = err.mean()
            scores[split + " homo"], scores[split + " lumo"] = err.mean(axis=0)
    return scores


def say(text):
    """Prints a long message wrapped and indented, so it reads well in a terminal."""
    print(textwrap.fill(text, width=88, initial_indent="  ", subsequent_indent="  "))


def read_log():
    if not LOG.is_file():
        return pd.DataFrame(columns=["time", "task", "file", "public", "private"])
    return pd.read_csv(LOG)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scores predictions for the 200 test molecules.")
    parser.add_argument("submission", help="your CSV file (start from a sample submission in data/003_test_data/)")
    parser.add_argument("--private", action="store_true", help="also show the private score")
    args = parser.parse_args(argv)

    path = Path(args.submission)
    try:
        if not path.is_file():
            raise SubmissionError(f"File not found: {path}")
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise SubmissionError(f"Could not read {path} as a CSV file: {e}") from None
        df = df.drop(columns=[c for c in df.columns if str(c).startswith("Unnamed:")])
        task, pred, notes = prepare(df)
    except SubmissionError as e:
        print(textwrap.fill(f"Not scored: {e}", width=88, subsequent_indent="  "))
        return 1

    scores = compute_scores(task, pred)
    log = read_log()
    earlier = log[log["task"] == task]
    looks = earlier[earlier["private"].notna()]
    spec = TASKS[task]

    print(f"{task.capitalize()}: {spec['metric']}, {spec['better']}")
    for note in notes:
        say(f"note: {note}")
    detail = f"  (homo {scores['public homo']:.3f}, lumo {scores['public lumo']:.3f})" if task != "stability" else ""
    print(f"  public score  (100 molecules): {scores['public']:.3f}{detail}   [public score #{len(earlier) + 1}]")

    if args.private:
        if len(looks):
            first = looks["time"].iloc[0][:10]
            print()
            say(f"Warning: you first looked at the private {task} score on {first}; this is look "
                f"#{len(looks) + 1}. If you changed your model after seeing it, this score is no longer "
                "an honest estimate for unseen molecules.")
            print()
        detail = f"  (homo {scores['private homo']:.3f}, lumo {scores['private lumo']:.3f})" if task != "stability" else ""
        print(f"  private score (100 molecules): {scores['private']:.3f}{detail}")
        if not len(looks):
            print()
            say(f"This was your first look at the private {task} score, and it is recorded in "
                f"{LOG.relative_to(ROOT)}. It is an honest estimate only for a model you chose without it.")
    else:
        print("  private score (100 molecules): hidden. Add --private once you have chosen your final model.")

    row = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "task": task,
           "file": str(path), "public": round(scores["public"], 4),
           "private": round(scores["private"], 4) if args.private else None}
    TEST_DATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row]).to_csv(LOG, mode="a", header=not LOG.is_file(), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
