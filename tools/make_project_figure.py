"""Draw the project figure: a molecule (SMILES) -> ML model(s) -> HOMO, LUMO and stability.

Writes _includes/project-figure.qmd, an inline SVG that the Course Guide and the Iteration 1
overview include with {{< include >}}. Inline (not an <img>), so that the text uses the site's
font and the colors follow light and dark mode (the .project-figure block in styles.css). The
molecule is drawn by RDKit and sits on a white card, so it reads in dark mode too.

    uv run python tools/make_project_figure.py
"""

import re
from pathlib import Path

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

OUT = Path(__file__).resolve().parent.parent / "_includes" / "project-figure.qmd"
SMILES = "Cn1c2ccccc2c2ccc(-c3ccc(-c4ccc(-c5cccs5)c5nonc54)s3)cc21"
# Darker heteroatom colors than the RDKit default (as in make_smiles_figures.py).
PALETTE = {7: (0.10, 0.30, 0.75), 8: (0.82, 0.12, 0.12), 16: (0.72, 0.55, 0.0)}

# Layout (viewBox units). Three columns: molecule card, model, predictions.
W, H = 820, 300
MOL = dict(x=0, y=40, w=340, h=250)            # molecule card
DRAW = dict(w=320, h=175)                      # RDKit drawing inside the card
MODEL = dict(x=410, y=125, w=140, h=80)        # model box
PRED = dict(x=615, y=40, w=205, h=74, gap=14)  # prediction cards
PREDICTIONS = [("HOMO", "energy level (eV)"), ("LUMO", "energy level (eV)"), ("Stability", "low, medium or high")]


def molecule_svg():
    mol = Chem.MolFromSmiles(SMILES)
    d = rdMolDraw2D.MolDraw2DSVG(DRAW["w"], DRAW["h"])
    o = d.drawOptions()
    o.clearBackground = False
    o.bondLineWidth = 2
    o.scaleBondWidth = False
    o.updateAtomPalette(PALETTE)
    o.padding = 0.06
    d.DrawMolecule(mol)
    d.FinishDrawing()
    svg = d.GetDrawingText()
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!-- END OF HEADER -->\s*", "", svg)
    x = MOL["x"] + (MOL["w"] - DRAW["w"]) / 2
    y = MOL["y"] + 22
    # Nest the drawing: replace RDKit's outer <svg ...> with one positioned in the figure.
    svg = re.sub(r"<svg[^>]*>", f'<svg x="{x:g}" y="{y:g}" width="{DRAW["w"]}" height="{DRAW["h"]}" '
                 f'viewBox="0 0 {DRAW["w"]} {DRAW["h"]}" class="pf-mol" aria-hidden="true">', svg, count=1)
    return svg.strip()


def arrow(x1, x2, y):
    return f'<path class="pf-arrow" d="M{x1} {y} H{x2}" marker-end="url(#pf-head)"/>'


def figure():
    cx_mol = MOL["x"] + MOL["w"] / 2
    cx_pred = PRED["x"] + PRED["w"] / 2
    mid = MODEL["y"] + MODEL["h"] / 2
    parts = [
        f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="pf-title pf-desc">',
        '<title id="pf-title">From a molecule to predictions</title>',
        '<desc id="pf-desc">A molecule, written as a SMILES string, goes into the machine learning model(s), '
        'which predict three properties: the HOMO energy level and the LUMO energy level, in eV, and the '
        'stability (low, medium or high).</desc>',
        '<defs><marker id="pf-head" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto"><path class="pf-arrowhead" d="M1 1.5 L8.5 5 L1 8.5"/></marker></defs>',
        # Column headings
        f'<text class="pf-head" x="{cx_mol:g}" y="20">Molecule</text>',
        f'<text class="pf-head" x="{MODEL["x"] + MODEL["w"] / 2:g}" y="20">Model</text>',
        f'<text class="pf-head" x="{cx_pred:g}" y="20">Predictions</text>',
        # Molecule card with the drawing and its SMILES string
        f'<rect class="pf-card" x="{MOL["x"]}" y="{MOL["y"]}" width="{MOL["w"]}" height="{MOL["h"]}" rx="12"/>',
        molecule_svg(),
        f'<text class="pf-smiles" x="{cx_mol:g}" y="{MOL["y"] + MOL["h"] - 32}">{SMILES}</text>',
        # Arrows and the model
        arrow(MOL["x"] + MOL["w"] + 10, MODEL["x"] - 10, mid),
        f'<rect class="pf-model" x="{MODEL["x"]}" y="{MODEL["y"]}" width="{MODEL["w"]}" height="{MODEL["h"]}" rx="12"/>',
        f'<text class="pf-model-text" x="{MODEL["x"] + MODEL["w"] / 2:g}" y="{mid:g}">ML Model(s)</text>',
        arrow(MODEL["x"] + MODEL["w"] + 10, PRED["x"] - 10, mid),
    ]
    for i, (name, sub) in enumerate(PREDICTIONS):
        y = PRED["y"] + i * (PRED["h"] + PRED["gap"])
        parts += [
            f'<rect class="pf-pred" x="{PRED["x"]}" y="{y}" width="{PRED["w"]}" height="{PRED["h"]}" rx="10"/>',
            f'<text class="pf-pred-name" x="{cx_pred:g}" y="{y + 32}">{name}</text>',
            f'<text class="pf-pred-sub" x="{cx_pred:g}" y="{y + 54}">{sub}</text>',
        ]
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        "<!-- Written by tools/make_project_figure.py; do not edit by hand. -->\n\n"
        "```{=html}\n"
        '<figure class="project-figure">\n'
        + figure() + "\n"
        "<figcaption>A molecule, written as a SMILES string, goes into your machine learning model(s), "
        "which predict its HOMO and LUMO energy levels and its stability.</figcaption>\n"
        "</figure>\n"
        "```\n",
        encoding="utf-8",
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
