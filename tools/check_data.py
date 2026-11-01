"""Checks the course data: files, columns, sizes, and that no competition answers are published.

usage: python tools/check_data.py   (from the repository root; exits with 1 on a failure)
"""
import sqlite3
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
    "003_kaggle_competition_data/classification_sample_submission.csv",
    "003_kaggle_competition_data/regression_sample_submission.csv",
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

# Kaggle sample submissions: schema, the same 200 molecules, placeholders only (no answers).
cls = pd.read_csv(DATA / "003_kaggle_competition_data/classification_sample_submission.csv")
reg = pd.read_csv(DATA / "003_kaggle_competition_data/regression_sample_submission.csv")
check(list(cls.columns) == ["smiles", "stability"] and len(cls) == 200, "classification sample: smiles, stability; 200 rows")
check(list(reg.columns) == ["smiles", "homo", "lumo"] and len(reg) == 200, "regression sample: smiles, homo, lumo; 200 rows")
check(list(cls["smiles"]) == list(reg["smiles"]) and cls["smiles"].is_unique, "both samples list the same 200 unique molecules")
check(cls["stability"].nunique() == 1 and reg["homo"].nunique() == 1 and reg["lumo"].nunique() == 1,
      "sample submissions hold one placeholder value per column (no answers)")
kaggle = set(cls["smiles"])
check(not kaggle & set(lab["smiles"]) and not kaggle & set(stab["smiles"]) and not kaggle & set(starter["smiles"]),
      "no Kaggle molecule appears in a labelled dataset")

# No solution or ground-truth files anywhere in the repository.
leaks = [str(p) for p in Path(".").rglob("*") if p.is_file() and ".venv" not in p.parts and ".git" not in p.parts
         and any(k in p.name.lower() for k in ("solution.csv", "ground_truth", "test_submission"))]
check(not leaks, f"no solution/ground-truth files in the repository {leaks if leaks else ''}")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
