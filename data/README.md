# Data

All datasets of the DataLab project.

| Folder | File | Molecules | Contains | Used in |
|---|---|---|---|---|
| `001_raw_data/` | `HOPV_homolumo.data` | 350 | SMILES, HOMO, LUMO and other experimental and computed data, in the original HOPV text format | Iteration 2 |
| `001_raw_data/` | `HOPV_stability.csv` | 350 | SMILES, stability (`low`, `medium`, `high`) | Iteration 2 |
| `001_raw_data/` | `lab_measurements.db` | 232 | SQLite database, table `measurements`: SMILES, HOMO, LUMO, stability | Iteration 4 |
| `002_processed_data/` | `starter_dataset.xlsx` | 80 | SMILES, 217 molecular descriptors, HOMO, LUMO, stability | Iteration 1 |

HOMO and LUMO are in electronvolts (eV). Missing values are part of the data.

**Test molecules:** the 200 molecules you predict are not in the repository. Every quarterly edition
of the Kaggle competitions has its own; download its sample submissions
(`classification_sample_submission.csv`, `regression_sample_submission.csv`) from the competition's
Data tab ([links](https://ai.buas.nl/open-courses/introduction-to-ml/datalab/iteration-3/index.html#the-kaggle-competitions))
into `003_kaggle_competition_data/`. Git ignores that folder.

**About the molecules and targets:** the molecules come from published research datasets. The HOPV
molecules, from the Harvard Organic Photovoltaic Dataset
([Lopez et al., 2016](https://doi.org/10.1038/sdata.2016.86)), were made and tested in real solar
cells. The lab database and test molecules are candidate molecules designed for organic solar cells in
the Harvard Clean Energy Project ([Hachmann et al., 2011](https://doi.org/10.1021/jz200866s)), a large
computational screening. To keep the competition fair, the
target values (HOMO, LUMO and stability) of all datasets are **synthetically generated** based on
real molecular properties. They follow realistic chemical relationships, but they do not match
published values for these molecules.

Files you create while working through the notebooks (for example `HOPV_homolumo_processed.csv`
and `xy_df_hopv.csv`) go in `002_processed_data/`. Git ignores them there, so updating the course
with `git pull` never touches them.
