# License

You are welcome to use this course in your own teaching: copy it, adapt it, translate it,
mix it into your own course materials, in class, online or commercially. All we ask is that you
give credit.

## What is licensed how

| What | License |
|---|---|
| Course content: the website pages, the text, exercises and figures in the notebooks, and the data in `data/` (see below) | [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), full text in [`LICENSE-CC-BY-4.0.txt`](LICENSE-CC-BY-4.0.txt) |
| Code: code cells in the notebooks, scripts, the Quarto filter and site configuration | [MIT License](LICENSE-MIT.txt) |

Copyright © 2025–2026 Breda University of Applied Sciences.

## How to give credit

For example:

> Based on *Introduction to Machine Learning* by M. Alican Noyan, Applied Data Science & AI,
> Breda University of Applied Sciences, <https://github.com/BredaUniversityADSAI/introduction-to-ml>,
> licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

If you changed the material, say so (for example "adapted from"). You don't need to ask us for
permission, but we'd love to hear how you use it: [open an issue](https://github.com/BredaUniversityADSAI/introduction-to-ml/issues).

The illustrations `images/ml-opv-hero.png`, `images/ml-opv-pipeline.png` and `images/crispdm.png` were
created with ChatGPT (OpenAI) for this course and are licensed under CC BY 4.0 like the rest of the content.

## Data

- `data/001_raw_data/HOPV_homolumo.data` is the Harvard Organic Photovoltaic Dataset (HOPV15),
  Lopez et al., *Scientific Data* 3, 160086 (2016), <https://doi.org/10.1038/sdata.2016.86>,
  CC BY 4.0. **Changed:** the experimental HOMO, LUMO and electrochemical-gap values are replaced
  by synthetic values.
- The molecules in `lab_measurements.db` and in `data/003_test_data/` come from the Harvard Clean
  Energy Project, Hachmann et al., *J. Phys. Chem. Lett.* 2, 2241 (2011),
  <https://doi.org/10.1021/jz200866s>, via the subset published by Duvenaud et al. (2015) at
  <https://github.com/HIPS/neural-fingerprint> (MIT License).
- All target values (HOMO, LUMO, stability) in `data/` and `tools/score_labels.json.gz` are synthetic and were generated for this
  course. Together with `starter_dataset.xlsx` and `lab_measurements.db` they are licensed under
  CC BY 4.0.

## Not covered by these licenses

- The name and logo of Breda University of Applied Sciences.
- Third-party images, credited in their captions under their own licenses (for example
  Wikimedia Commons images under CC BY-SA or in the public domain).
- Videos, books, papers and websites that the course links to or embeds, such as the course
  textbook (Aurélien Géron, *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow*,
  O'Reilly) and the YouTube videos.
- The student quotes on the homepage.
- The font files in `fonts/` (Source Sans Pro, SIL Open Font License, see `fonts/OFL.txt`).
