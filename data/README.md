# Data

All datasets of the DataLab project.

| Folder | File | Molecules | Contains | Used in |
|---|---|---|---|---|
| `001_raw_data/` | `HOPV_homolumo.data` | 350 | SMILES, HOMO, LUMO and other experimental and computed data, in the original HOPV text format | Iteration 2 |
| `001_raw_data/` | `HOPV_stability.csv` | 350 | SMILES, stability (`low`, `medium`, `high`) | Iteration 2 |
| `001_raw_data/` | `lab_measurements.db` | 232 | SQLite database, table `measurements`: SMILES, HOMO, LUMO, stability | Iteration 4 |
| `002_processed_data/` | `starter_dataset.xlsx` | 80 | SMILES, 217 molecular descriptors, HOMO, LUMO, stability | Iteration 1 |
| `003_test_data/` | `classification_sample_submission.csv`, `regression_sample_submission.csv` | 200 | id, SMILES and placeholder values: the test molecules you predict | Iteration 3 onward |

HOMO and LUMO are in electronvolts (eV). Missing values are part of the data.

**Test molecules:** the 200 molecules you predict are in `003_test_data/`, in two sample submissions:
`classification_sample_submission.csv` (`id`, `smiles`, `stability`) and `regression_sample_submission.csv`
(`id`, `smiles`, `homo`, `lumo`), with placeholder values. Replace the placeholders with your predictions,
save the file in the same folder under another name and score it with `tools/score.py`
([how](https://ai.buas.nl/open-courses/introduction-to-ml/datalab/iteration-3/00_overview.html#scoring-your-predictions)). Git ignores everything in that folder except the two sample submissions,
including the scorer's log `score_log.csv`.

**About the molecules and targets:** the molecules come from two published research datasets: the
Harvard Organic Photovoltaic Dataset ([Lopez et al., 2016](https://doi.org/10.1038/sdata.2016.86)),
molecules that were made and tested in real solar cells, and the Harvard Clean Energy Project
([Hachmann et al., 2011](https://doi.org/10.1021/jz200866s)), candidate molecules designed for organic
solar cells in a large computational screening. The HOPV files hold the HOPV molecules; finding out
where the other molecules come from is part of the project (Iteration 5 gives the answer). The
target values (HOMO, LUMO and stability) of all datasets are **synthetically generated** based on
real molecular properties. They follow realistic chemical relationships, but they do not match
published values for these molecules. In `HOPV_homolumo.data`, the optical gap, PCE, Voc and Jsc of each
experiment are the published values adjusted to the synthetic HOMO and LUMO, so that the columns stay
consistent; the descriptions of the experiments, the fill factor and the computed (DFT) values in the
conformer blocks are as published.

Files you create while working through the notebooks (for example `HOPV_homolumo_processed.csv`
and `xy_df_hopv.csv`) go in `002_processed_data/`. Git ignores them there, so they are not saved
in the history of your copy of the course: the notebooks that create them can always make them again.
