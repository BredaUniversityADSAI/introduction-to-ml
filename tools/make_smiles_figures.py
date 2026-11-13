"""Draw the molecule figures of datalab/iteration-2/01_understanding_smiles.qmd.

Writes SVGs with a transparent background to images/iteration-2/smiles/. All figures
use the same canvas size and bond length, so molecules have the same scale on the page.
styles.css (.mol-row) shows them on a light card, in light and in dark mode.

    uv run python tools/make_smiles_figures.py
"""

from pathlib import Path

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

OUT = Path(__file__).resolve().parent.parent / "images" / "iteration-2" / "smiles"
ORANGE = (0.957, 0.478, 0.125, 0.55)  # BUas orange, semi-transparent
# Darker heteroatom colors than the RDKit default, so that S and F read well on white.
PALETTE = {7: (0.10, 0.30, 0.75), 8: (0.82, 0.12, 0.12), 9: (0.05, 0.55, 0.45), 16: (0.72, 0.55, 0.0), 14: (0.45, 0.35, 0.25)}


def draw(name, smiles, *, add_hs=False, atoms=(), bonds=(), size=(360, 220), bond_length=50):
    mol = Chem.MolFromSmiles(smiles)
    if add_hs:
        mol = Chem.AddHs(mol)
    d = rdMolDraw2D.MolDraw2DSVG(*size)
    o = d.drawOptions()
    o.clearBackground = False
    o.bondLineWidth = 3
    o.scaleBondWidth = False
    o.updateAtomPalette(PALETTE)
    o.highlightBondWidthMultiplier = 14
    o.fixedBondLength = bond_length
    o.padding = 0.12
    o.minFontSize = 22
    o.maxFontSize = 26
    o.highlightRadius = 0.4
    o.setHighlightColour(ORANGE)
    bond_ids = [mol.GetBondBetweenAtoms(a, b).GetIdx() for a, b in bonds]
    rdMolDraw2D.PrepareAndDrawMolecule(
        d, mol, highlightAtoms=list(atoms), highlightBonds=bond_ids
    )
    d.FinishDrawing()
    (OUT / f"{name}.svg").write_text(d.GetDrawingText())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Atoms and implicit hydrogens
    draw("ethanol", "CCO")
    draw("ethanol_h", "CCO", add_hs=True)
    # Bonds
    draw("acetaldehyde", "CC=O", bonds=[(1, 2)])
    draw("acetonitrile", "CC#N", bonds=[(1, 2)])
    # Branches: the atoms inside the parentheses
    draw("butanol", "CC(O)CC", atoms=[2])
    draw("acetic_acid", "CC(=O)O", atoms=[2])
    # Rings: the bond that the ring-closure digits create
    draw("cyclohexane", "C1CCCCC1", bonds=[(0, 5)])
    draw("naphthalene", "c1ccc2ccccc2c1", bonds=[(0, 9), (3, 8)])
    # Aromatic rings
    draw("benzene", "c1ccccc1")
    draw("thiophene", "c1ccsc1")
    draw("benzothiadiazole", "c1ccc2nsnc2c1")
    # Double-bond geometry
    draw("difluoroethene_trans", "F/C=C/F")
    draw("difluoroethene_cis", "F/C=C\\F")
    # A molecule from the starter dataset
    draw(
        "project_molecule",
        "Cn1c2ccccc2c2ccc(-c3ccc(-c4ccc(-c5cccs5)c5nonc54)s3)cc21",
        size=(760, 300),
        bond_length=30,
    )


if __name__ == "__main__":
    main()
