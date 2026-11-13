"""Draw the figures of self-study/theme-2/03_leakage_and_distribution_shift.qmd.

Photos: images/leakage/photos/*.jpg (Wikimedia Commons; licenses and authors in
images/leakage/photos/credits.json). Writes the figures to images/leakage/.

    uv run python tools/make_leakage_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch, Polygon
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.spatial import ConvexHull
from sklearn.datasets import fetch_openml
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "images" / "leakage" / "photos"
OUT = ROOT / "images" / "leakage"
CREDITS = json.loads((PHOTOS / "credits.json").read_text())

BLUE, ORANGE, TEAL = "#00558c", "#f47a20", "#2a9d8f"
INK, MUTED, GRID = "#1f2328", "#5b6470", "#e6e8eb"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 12, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 150,
})


def names(group):
    return [n for n, c in CREDITS.items() if c["group"] == group]


def square(name, size):
    im = Image.open(PHOTOS / f"{name}.jpg").convert("RGB")
    return ImageOps.fit(im, (size, size), Image.LANCZOS)


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT, size, index=1 if bold else 0)
    except OSError:
        return ImageFont.load_default()


def collage(rows, path, tile=220, gap=6, label_w=230):
    """rows: list of (label, [photo names]). Photos are cropped to squares."""
    ncol = max(len(r[1]) for r in rows)
    w = label_w + ncol * (tile + gap)
    h = len(rows) * (tile + gap)
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    for i, (label, row) in enumerate(rows):
        y = i * (tile + gap)
        d.text((16, y + tile / 2), label, font=font(30, bold=True), fill=INK, anchor="lm")
        for j, n in enumerate(row):
            im.paste(square(n, tile), (label_w + j * (tile + gap), y))
    im.save(path, quality=85, optimize=True)


def pca_figure(path):
    """PCA of the raw pixels (32x32 RGB) of all photos, with the photos as markers."""
    all_names = list(CREDITS)
    X = np.array([np.asarray(square(n, 32), float).ravel() / 255 for n in all_names])
    Z = PCA(n_components=2).fit_transform(X)
    dev = [i for i, n in enumerate(all_names) if CREDITS[n]["group"] != "usage"]

    fig, ax = plt.subplots(figsize=(11, 6.2))
    hull = ConvexHull(Z[dev])
    pts = Z[dev][hull.vertices]
    centre = pts.mean(axis=0)
    pts = centre + (pts - centre) * 1.1  # some room around the photos
    ax.add_patch(Polygon(pts, closed=True, fc="#e8eef4", ec=BLUE, lw=1.5, ls="--", zorder=0))
    ax.text(centre[0] + 3, pts[:, 1].max() + 1.2, "Development data: animals in snow",
            color=BLUE, ha="center", fontsize=13, weight="bold")
    for i, n in enumerate(all_names):
        usage = CREDITS[n]["group"] == "usage"
        thumb = np.asarray(square(n, 90))
        ab = AnnotationBbox(OffsetImage(thumb, zoom=0.55), Z[i], frameon=True, pad=0.15,
                            bboxprops=dict(ec=ORANGE if usage else BLUE, lw=2.2))
        ax.add_artist(ab)
    usage_pts = Z[[i for i in range(len(all_names)) if i not in dev]]
    ax.text(usage_pts[:, 0].mean(), usage_pts[:, 1].min() - 4.2, "Usage data:\nanimals elsewhere",
            color=ORANGE, ha="center", va="top", fontsize=13, weight="bold")
    pad = 6
    ax.set_xlim(Z[:, 0].min() - pad, Z[:, 0].max() + pad)
    ax.set_ylim(Z[:, 1].min() - pad - 3, Z[:, 1].max() + pad)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def penguin_figures(path_islands, path_scores):
    df = fetch_openml(name="penguins", version=1, as_frame=True).frame
    feats = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]
    df = df.dropna(subset=feats)

    # Species per island (stacked horizontal bars, direct labels)
    tab = df.groupby(["island", "species"], observed=True).size().unstack(fill_value=0)
    tab = tab.loc[["Torgersen", "Dream", "Biscoe"], ["Adelie", "Chinstrap", "Gentoo"]]
    colors = {"Adelie": BLUE, "Chinstrap": ORANGE, "Gentoo": TEAL}
    fig, ax = plt.subplots(figsize=(9, 3.4))
    left = np.zeros(len(tab))
    for sp in tab.columns:
        vals = tab[sp].to_numpy()
        ax.barh(tab.index, vals, left=left, color=colors[sp], height=0.6, edgecolor="white", lw=2, label=sp)
        for k, v in enumerate(vals):
            if v:
                ax.text(left[k] + v / 2, k, f"{sp} {v}", ha="center", va="center", color="white",
                        fontsize=11, weight="bold")
        left += vals
    ax.set_xlabel("Number of penguins")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=12, labelcolor=INK)
    ax.legend(ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path_islands, facecolor="white")
    plt.close(fig)

    # Train on Biscoe; test on Biscoe (held out) and on Dream
    b, d = df[df.island == "Biscoe"], df[df.island == "Dream"]
    Xtr, Xte, ytr, yte = train_test_split(b[feats], b.species, test_size=0.25, random_state=42,
                                          stratify=b.species)
    model = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr)
    scores = {"Test set from Biscoe": model.score(Xte, yte), "Penguins from Dream": model.score(d[feats], d.species)}
    fig, ax = plt.subplots(figsize=(9, 2.6))
    labels = list(scores)[::-1]
    vals = [scores[k] * 100 for k in labels]
    ax.barh(labels, vals, color=[ORANGE, BLUE], height=0.55)
    for k, v in enumerate(vals):
        ax.text(v + 1.5, k, f"{v:.0f}%", va="center", color=INK, fontsize=13, weight="bold")
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Accuracy of a model trained on penguins from Biscoe")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=12, labelcolor=INK)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path_scores, facecolor="white")
    plt.close(fig)
    return {k: round(v, 3) for k, v in scores.items()}


def split_figure(path):
    """Four patients with four images each: a random split and a split by patient."""
    rng = np.random.default_rng(3)
    patients, per = 4, 4
    test_random = set(rng.choice(patients * per, size=4, replace=False).tolist())
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, title, is_test in [
        (axes[0], "Random split: images", lambda p, k: p * per + k in test_random),
        (axes[1], "Split by patient", lambda p, k: p == patients - 1),
    ]:
        for p in range(patients):
            y = patients - 1 - p
            ax.text(-0.25, y + 0.4, f"Patient {chr(65 + p)}", ha="right", va="center", color=INK, fontsize=12)
            for k in range(per):
                test = is_test(p, k)
                ax.add_patch(FancyBboxPatch((k * 1.1, y), 0.9, 0.8, boxstyle="round,pad=0,rounding_size=0.12",
                                            fc=ORANGE if test else BLUE, ec="none"))
                ax.text(k * 1.1 + 0.45, y + 0.4, "test" if test else "train", ha="center", va="center",
                        color="white", fontsize=10, weight="bold")
        ax.set_xlim(-2.2, per * 1.1)
        ax.set_ylim(-0.2, patients)
        ax.set_title(title, color=INK, fontsize=14, weight="bold", loc="left", x=0.0)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def hospital_figure(path):
    """Published results of Zech et al. (2018), PLOS Medicine, CC BY 4.0."""
    labels = ["X-rays from the two training\nhospital systems (internal test)",
              "X-rays from a third hospital\nsystem (external test)"][::-1]
    vals = [0.931, 0.815][::-1]
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.barh(labels, vals, color=[ORANGE, BLUE], height=0.55)
    for k, v in enumerate(vals):
        ax.text(v + 0.01, k, f"{v:.3f}", va="center", color=INK, fontsize=13, weight="bold")
    ax.set_xlim(0.5, 1.03)
    ax.set_xlabel("AUC of the pneumonia model (0.5 = guessing, 1 = perfect)")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11, labelcolor=INK)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def side_by_side(left, right, path, gap=40):
    a, b = Image.open(OUT / left).convert("RGB"), Image.open(OUT / right).convert("RGB")
    h = min(a.height, b.height)
    a, b = a.resize((a.width * h // a.height, h)), b.resize((b.width * h // b.height, h))
    im = Image.new("RGB", (a.width + gap + b.width, h), "white")
    im.paste(a, (0, 0))
    im.paste(b, (a.width + gap, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(a.width + 8, h // 2 - 14), (a.width + 32, h // 2), (a.width + 8, h // 2 + 14)], fill=MUTED)
    im.save(path, quality=85, optimize=True)


def main():
    cats, notcats, usage = names("cat"), names("notcat"), names("usage")
    collage([("Cat (1)", cats), ("Not a cat (0)", notcats)], OUT / "training_set.jpg")
    collage([("", usage)], OUT / "usage_photos.jpg", label_w=0)
    pca_figure(OUT / "pca_photos.png")
    print(penguin_figures(OUT / "penguins_islands.png", OUT / "penguins_scores.png"))
    split_figure(OUT / "split_by_patient.png")
    hospital_figure(OUT / "hospital_auc.png")
    # Figures 1 and 3 of Noyan (2022), arXiv:2206.04374, CC BY 4.0 (PlantVillage images CC BY-SA 3.0)
    side_by_side("plantvillage_examples.jpg", "plantvillage_8px_examples.jpg", OUT / "plantvillage_8px.jpg")


if __name__ == "__main__":
    main()
