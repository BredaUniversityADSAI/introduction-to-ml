"""Checks the course data: files, columns, sizes, the test set and its scorer (tools/score.py),
and that no solution files are published.

usage: python tools/check_data.py   (from the repository root; exits with 1 on a failure)
"""
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd

DATA = Path("data")
failures = []


def check(ok, message):
    print(("ok    " if ok else "FAIL  ") + message)
    if not ok:
        failures.append(message)


# Every published data file is there (and nothing else is tracked in data/, see .gitignore).
expected = [
    "001_raw_data/HOPV_homolumo.data",
    "001_raw_data/HOPV_stability.csv",
    "001_raw_data/lab_measurements.db",
    "002_processed_data/starter_dataset.xlsx",
]
for f in expected:
    check((DATA / f).is_file(), f"data/{f} exists")

# Starter dataset: smiles, 217 descriptors, three targets, 80 molecules.
starter = pd.read_excel(DATA / "002_processed_data/starter_dataset.xlsx")
check(starter.shape == (80, 221), f"starter_dataset.xlsx is 80 x 221 (is {starter.shape})")
check(starter.columns[0] == "smiles" and list(starter.columns[-3:]) == ["homo", "lumo", "stability"],
      "starter_dataset.xlsx: smiles first, homo/lumo/stability last")

# HOPV stability file.
stab = pd.read_csv(DATA / "001_raw_data/HOPV_stability.csv")
check(list(stab.columns) == ["smiles", "stability"] and len(stab) == 350, "HOPV_stability.csv: smiles, stability; 350 rows")
check(set(stab["stability"].dropna()) == {"low", "medium", "high"}, "HOPV_stability.csv: classes low/medium/high")

# HOPV HOMO/LUMO file: 350 molecule records.
n_records = sum(1 for line in open(DATA / "001_raw_data/HOPV_homolumo.data") if line.startswith("InChI="))
check(n_records == 350, f"HOPV_homolumo.data has 350 molecules (has {n_records})")

# Lab database.
con = sqlite3.connect(DATA / "001_raw_data/lab_measurements.db")
lab = pd.read_sql("SELECT * FROM measurements", con)
con.close()
check(list(lab.columns) == ["id", "smiles", "homo", "lumo", "stability"] and len(lab) == 232,
      "lab_measurements.db: table measurements (id, smiles, homo, lumo, stability), 232 rows")

# Test set: the two sample submissions (id, smiles, placeholders) and the scorer's labels.
TEST = DATA / "003_test_data"
tracked = subprocess.run(["git", "ls-files", "data", "tools"], capture_output=True, text=True).stdout.split()
check(not [f for f in tracked if f.startswith("data/003_") and Path(f).name not in
           ("classification_sample_submission.csv", "regression_sample_submission.csv")],
      "data/003_test_data/ tracks only the two sample submissions (not your submissions or score_log.csv)")
cls = pd.read_csv(TEST / "classification_sample_submission.csv")
reg = pd.read_csv(TEST / "regression_sample_submission.csv")
check(list(cls.columns) == ["id", "smiles", "stability"] and len(cls) == 200 and set(cls["stability"]) == {"medium"},
      "classification_sample_submission.csv: id, smiles, stability = medium; 200 rows")
check(list(reg.columns) == ["id", "smiles", "homo", "lumo"] and len(reg) == 200
      and set(reg["homo"]) == {-5} and set(reg["lumo"]) == {-3},
      "regression_sample_submission.csv: id, smiles, homo = -5, lumo = -3; 200 rows")
check(cls["id"].is_unique and cls["smiles"].is_unique and cls[["id", "smiles"]].equals(reg[["id", "smiles"]]),
      "sample submissions: unique ids and SMILES, the same molecules in the same order")

sys.path.insert(0, str(Path("tools").resolve()))
import score  # noqa: E402

labels = score.load_labels()
check(sorted(labels.index) == sorted(cls["id"]), "score_labels.json.gz has exactly the ids of the sample submissions")
check(labels["split"].value_counts().to_dict() == {"public": 100, "private": 100}
      and all(labels.groupby("split")["stability"].value_counts().unstack().loc[s].tolist() == [25, 25, 50]
              for s in ("public", "private")),
      "score_labels.json.gz: 100 public / 100 private, each 25 high / 25 low / 50 medium")
check(not labels[["stability", "homo", "lumo"]].isna().any().any(), "score_labels.json.gz: no missing targets")

# The scorer reproduces the Kaggle scores of the sample submissions (2026 Q4 sandbox, 3 Nov 2026).
expected = {"stability": (0.2222, 0.2222), "energy levels": (0.3881, 0.3852)}
for f in (cls, reg):
    task, pred, _ = score.prepare(f)
    s = score.compute_scores(task, pred, labels)
    check((round(s["public"], 4), round(s["private"], 4)) == expected[task],
          f"score.py: {task} sample submission scores {expected[task]} (public, private)")

# The scorer rejects broken submissions with a message.
bad = {
    "wrong class name": cls.assign(stability="Medium"),
    "class numbers": cls.assign(stability=1),
    "missing class": cls.assign(stability=None),
    "missing rows": cls.iloc[:150],
    "duplicate rows": pd.concat([cls, cls.iloc[:1]]),
    "unknown id": cls.assign(id=cls["id"].str.replace("M", "X")),
    "no key column": cls.drop(columns=["id", "smiles"]),
    "unknown SMILES": cls.drop(columns="id").assign(smiles="CCO"),
    "wrong column case": reg.rename(columns={"homo": "HOMO", "lumo": "LUMO"}),
    "no target column": reg.drop(columns=["homo", "lumo"]),
    "both tasks": reg.assign(stability="medium"),
    "NaN value": reg.assign(homo=float("nan")),
    "text value": reg.assign(lumo="n/a"),
    "infinite value": reg.assign(lumo=float("inf")),
}
for name, df in bad.items():
    try:
        score.prepare(df)
        check(False, f"score.py rejects a submission with {name}")
    except score.SubmissionError:
        check(True, f"score.py rejects a submission with {name}")

# Messages that help: name only the wrongly written columns, and say when the id column is missing.
try:
    score.prepare(reg.rename(columns={"homo": "HOMO"}))
    check(False, "score.py names only the wrongly written column")
except score.SubmissionError as e:
    check("'HOMO'" in str(e) and "'lumo'" not in str(e), f"score.py names only the wrongly written column ({e})")
_, _, notes = score.prepare(reg.drop(columns="id"))
check(any("no id column" in n for n in notes), "score.py says that a submission without an id column was matched on the SMILES")

# No solution or ground-truth files anywhere in the repository; the scorer's labels are the only label file.
leaks = [str(p) for p in Path(".").rglob("*") if p.is_file() and ".venv" not in p.parts and ".git" not in p.parts
         and any(k in p.name.lower() for k in ("solution.csv", "ground_truth", "test_submission", "labels"))
         and p.as_posix() != "tools/score_labels.json.gz"]
check(not leaks, f"no solution/ground-truth files in the repository {leaks if leaks else ''}")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
