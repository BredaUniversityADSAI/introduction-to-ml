# Data

All datasets of the DataLab project.

| Folder | File | Molecules | Contains | Used in |
|---|---|---|---|---|
| `001_raw_data/` | `HOPV_homolumo.data` | 350 | SMILES, HOMO, LUMO and other experimental and computed data, in the original HOPV text format | Iteration 2 |
| `001_raw_data/` | `HOPV_stability.csv` | 350 | SMILES, stability (`low`, `medium`, `high`) | Iteration 2 |
| `001_raw_data/` | `lab_measurements.db` | 232 | SQLite database, table `measurements`: SMILES, HOMO, LUMO, stability | Iteration 3+ |
| `002_processed_data/` | `starter_dataset.xlsx` | 80 | SMILES, 217 molecular descriptors, HOMO, LUMO, stability | Iteration 1 |
| `003_kaggle_competition_data/` | `classification_sample_submission.csv`, `regression_sample_submission.csv` | 200 | SMILES and placeholder predictions | Iteration 3+ |

HOMO and LUMO are in electronvolts (eV). Missing values are part of the data.

**About the targets:** the molecules are real. The HOPV molecules come from the Harvard Organic
Photovoltaic Dataset ([Lopez et al., 2016](https://doi.org/10.1038/sdata.2016.86)); the other
molecules come from the Harvard Clean Energy Project
([Hachmann et al., 2011](https://doi.org/10.1021/jz200866s)). To keep the competition fair, the
target values (HOMO, LUMO and stability) of all datasets are **synthetically generated** based on
real molecular properties. They follow realistic chemical relationships, but they do not match
published values for these molecules.

Files you create while working through the notebooks (for example `HOPV_homolumo_processed.csv`
and `xy_df_hopv.csv`) go in `002_processed_data/`.
