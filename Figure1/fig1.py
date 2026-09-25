#!/usr/bin/env python3
"""
Figure 1: a, the general case, the Euler diagram of the three properties with all seven atoms; b, the disk of the 16
binary memory-one strategies and c, the disk of the 65536 binary memory-two strategies, each coloured by its case, a
case being the set of atoms that are non-empty at the game; below, the key to b and c: a row per case, stating which
atoms are empty.

    python3 fig1.py            (reads ../data/arrangement/: m2_faces_k4.npz and m2_faces.csv, the memory-two faces and
                                their atom counts, and m1_faces_k4.npz and m1_faces.csv, the memory-one faces; writes
                                Fig1.pdf and Fig1.png here)

The cases are numbered once for both disks: memory one has twelve, memory two ten, three are shared, nineteen in
all, ordered by the number of empty atoms and then by area.  A case keeps its number and colour on both disks, so
the three shared cases (7, 11, 13) can be seen at a glance.  Under the disks: "Memory-1, 16 strategies" and
"Memory-2, 65536 strategies".  The key lists every case once, by number, cases 1-10 on the left and 11-19 on the
right.  A present atom is a cell in the tint of panel a with its code, an empty atom a white cell with ∅.  Colours
were chosen so that cases that touch on a disk differ by at least 38 CIELAB units and any two of the nineteen by at
least 38 as well.

This is FinalFigures/fig1.py of the working tree with only the data loading changed (the arrays are the same, see
../data/arrangement/README.md); the drawing is untouched.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, os.path.join(ROOT, "data", "arrangement"))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import eulerlib as el                                              # noqa: E402
import arrangement                                                 # noqa: E402  the deposited arrangements
from common import atoms as m1atoms                                # noqa: E402  pieces() (m1atoms.pieces, moved unchanged)

matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "sans-serif"})
K = 4.0
ORDER = el.ORDER


def keys(atoms):
    """the case of each face: seven bits, the atoms of ORDER non-empty or not"""
    present = np.stack([atoms[:, int(c[0]) * 4 + int(c[1]) * 2 + int(c[2])] > 0 for c in ORDER], 1)
    return np.array(["".join("1" if x else "0" for x in row) for row in present])


# ------------------------------------------------------------------ memory two (Figure 1's data)
D2 = arrangement.m2()                          # the faces of ca4_arrangement_k4.npz and the ATOMS of Count6_faces.npz
assert arrangement.K == K
FACES2 = D2["faces"]
ATOMS2 = D2["atoms"]
assert ATOMS2.shape == (len(FACES2), 8) and (ATOMS2[:, 5] == 0).all() and (ATOMS2.sum(1) == 65536).all()


def plane(q):
    q = np.atleast_2d(np.asarray(q, float)); r2 = (q ** 2).sum(1)
    return q * (K / np.sqrt(np.maximum(1.0 - r2, 1e-12)))[:, None]


def interior(f):
    """a game strictly inside the face: generic convex weights, so no point lands on a measure-zero line"""
    p = plane(f); w = 1.0 + 0.1 * np.sin(np.arange(len(p)) + 1.0)
    return (p * w[:, None]).sum(0) / w.sum()


DA2 = np.array([el.polyarea(f) for f in FACES2]); DA2 /= DA2.sum()
CEN2 = np.array([f.mean(0) for f in FACES2])
Q2, W2 = m1atoms.pieces(np.array([interior(f) for f in FACES2]))
PIECE2 = np.array([q + "∩" + w for q, w in zip(Q2, W2)])
KEY2 = keys(ATOMS2)

# ------------------------------------------------------------------ memory one (SI Figure 4's data)
D1 = arrangement.m1()                          # m1atoms.load()
FACES1, DA1, UVC1, ATOMS1 = D1["faces"], D1["diskarea"], D1["uvc"], D1["atoms"]
assert ATOMS1.shape == (len(FACES1), 8) and (ATOMS1[:, 5] == 0).all() and (ATOMS1.sum(1) == 16).all()
DA1 = DA1 / DA1.sum()
CEN1 = np.array([f.mean(0) for f in FACES1])
Q1, W1 = m1atoms.pieces(UVC1)
PIECE1 = np.array([q + "∩" + w for q, w in zip(Q1, W1)])
KEY1 = keys(ATOMS1)

# ------------------------------------------------------------------ the cases, numbered once
area1 = {k: DA1[KEY1 == k].sum() for k in set(KEY1)}
area2 = {k: DA2[KEY2 == k].sum() for k in set(KEY2)}
CASES = sorted(set(KEY1) | set(KEY2), key=lambda k: (k.count("0"), -(area1.get(k, 0) + area2.get(k, 0))))
assert len(CASES) == 19 and len(set(KEY1)) == 12 and len(set(KEY2)) == 10 and len(set(KEY1) & set(KEY2)) == 3
NUM = {k: str(i + 1) for i, k in enumerate(CASES)}
CASES1 = [k for k in CASES if k in area1]
CASES2 = [k for k in CASES if k in area2]
PAL = {                                    # the colour of each case, on both disks and in the key
    "1111111": "#f4cae4", "1011111": "#e69f00", "1101111": "#fc8d62", "1111101": "#fdbf6f", "1111011": "#ffff99",
    "1101101": "#66c2a5", "1011101": "#d0f0c0", "1011110": "#9c9ede", "1101011": "#56b4e9", "1101110": "#bd9e39",
    "1101001": "#a6d854", "1101010": "#c6dbef", "1001101": "#e78ac3", "1101100": "#17becf", "1011100": "#ffd92f",
    "1001010": "#ff9896", "1011000": "#ff7f00", "1001100": "#fdd0a2", "1001000": "#74c476"}
assert set(PAL) == set(CASES)
print("%d cases: %d at memory one, %d at memory two, %d shared" % (len(CASES), len(CASES1), len(CASES2), len(set(CASES1) & set(CASES2))))
for k in CASES:
    print("  %2s %s  empty %-22s  m1 %5.1f%%  m2 %5.1f%%" % (NUM[k], k, ",".join(c for c, x in zip(ORDER, k) if x == "0") or "-",
                                                         100 * area1.get(k, 0), 100 * area2.get(k, 0)))

# ------------------------------------------------------------------ layout (inches)
FW = 7.2
WA, WD = 2.55, (FW - 2.55) / 2                 # panel a; the two disks
ROW1 = 2.40                                    # the top row
RH, CW, SW = 0.19, 0.34, 0.46                  # key: row height, atom cell width, case (swatch) column width
HH = 0.20                                      # key: header row
GAP = 0.50                                     # between the two parts of the key
PW = SW + 7 * CW                               # width of one part
MT, MG, MB = 0.06, 0.34, 0.06                  # margins: top, between row 1 and the key (holds the disk captions), bottom
LEFT, RIGHT = CASES[:10], CASES[10:]           # the two parts of the key: cases 1-10 and 11-19
KH = HH + len(LEFT) * RH
FH = MT + ROW1 + MG + KH + MB
fig = plt.figure(figsize=(FW, FH))


def axin(x, y, w, h):
    return fig.add_axes([x / FW, y / FH, w / FW, h / FH])


# ------------------------------------------------------------------ a: the general case (the geometry of other/fig1_old.py panel a)
D, RC = 1.15, 1.75                             # efficient centre (-D, 0), competitive (D, 0), both radius RC
ECIRC, CCIRC = (-D, 0.0, RC), (D, 0.0, RC)
n_in, n_bd = el.circle(0.0, 0.0, 1.90)         # stable: a circle over the lens
ANCH = {"111": (0, 0), "110": (-1.25, 0), "011": (1.25, 0), "100": (-2.4, 0), "001": (2.4, 0), "010": (0, 1.6), "000": (2.75, 1.5)}
NAMES = [("efficient", -2.35, -1.98, el.COL_E, "center", "top"), ("competitive", 2.35, -1.98, el.COL_C, "center", "top"),
         ("stable", 0.0, 2.00, el.COL_N, "center", "bottom")]
XL, YL = 3.5, 2.35
ya = FH - MT - ROW1
HA = WA * (2 * YL) / (2 * XL)                  # the height that keeps the units square
axa = axin(0.02, ya + (ROW1 - HA) / 2, WA, HA)
el.euler(axa, "1111111", ECIRC, CCIRC, (n_in, [n_bd]), ANCH, XL, YL, big=True, letter="a", names=NAMES)

# ------------------------------------------------------------------ where the case numbers go
from PIL import Image, ImageDraw                                   # noqa: E402
from scipy import ndimage                                          # noqa: E402


LEADER = {                                 # labels of regions too thin to hold them: where the number is printed instead,
    ("b", "17"): (0.33, 0.27),             # in disk units, with a thin line leading to the region (to its most interior
    ("b", "18"): (0.36, -0.20),            # point, or to the point given second)
    ("c", "11"): (0.50, -0.80),
    ("c", "13"): ((0.31, -0.36), (0.18, -0.28))}


def labels(panel, faces, key, cases, minshare=0.005, n=1600):
    """one label per connected component of a case's region that covers at least `minshare` of the disk (its
    largest component if none does).  The label sits at a point of the component at least 0.8 of the way to
    its most interior point, chosen as far as possible from the labels already placed (big components first);
    components listed in LEADER get their number printed at the given position with a leader line to them.
    Returns [(x, y, text, anchor)] with anchor None or the (x, y) the leader points to."""
    idx = {k: i + 1 for i, k in enumerate(cases)}
    im = Image.new("I", (n, n), 0); dr = ImageDraw.Draw(im)
    s = n / 2.0 / 1.001
    for f, k in zip(faces, key):
        if len(f) >= 3:
            dr.polygon([(n / 2 + s * x, n / 2 - s * y) for x, y in f], fill=idx[k])
    L = np.array(im, dtype=np.int64)
    ndisk = (L > 0).sum()
    comps = []
    for k in cases:
        comp, ncomp = ndimage.label(L == idx[k])
        sizes = ndimage.sum(np.ones_like(comp), comp, index=np.arange(1, ncomp + 1))
        chosen = [c + 1 for c in range(ncomp) if sizes[c] / ndisk >= minshare] or [int(np.argmax(sizes)) + 1]
        for c in chosen:
            comps.append((sizes[c - 1], k, comp == c))
    comps.sort(key=lambda t: -t[0])
    placed, out = [], []
    for sz, k, m in comps:
        dist = ndimage.distance_transform_edt(m)
        iy, ix = np.unravel_index(np.argmax(dist), dist.shape)
        px, py = (ix + 0.5 - n / 2) / s, (n / 2 - iy - 0.5) / s
        if (panel, NUM[k]) in LEADER:
            spec = LEADER[(panel, NUM[k])]
            (lx, ly), (ax_, ay_) = spec if isinstance(spec[0], tuple) else (spec, (px, py))
            assert m[int(round(n / 2 - ay_ * s - 0.5)), int(round(n / 2 + ax_ * s - 0.5))], (panel, NUM[k], "anchor off the region")
            out.append((lx, ly, NUM[k], (ax_, ay_))); placed.append((lx, ly))
            continue
        cy, cx = np.nonzero(dist >= 0.8 * dist.max())
        cx, cy = (cx + 0.5 - n / 2) / s, (n / 2 - cy - 0.5) / s
        if placed:
            P = np.array(placed)
            dmin = np.sqrt((cx[:, None] - P[None, :, 0]) ** 2 + (cy[:, None] - P[None, :, 1]) ** 2).min(1)
            j = int(np.argmax(dmin)); px, py = cx[j], cy[j]
        out.append((px, py, NUM[k], None)); placed.append((px, py))
    return out


# ------------------------------------------------------------------ b, c: the two disks
LIM = 1.19
dpu = 2 * LIM / ((WD - 0.05) * 72.0)
CAPTION = {"b": "Memory-1, 16 strategies", "c": "Memory-2, 65536 strategies"}
for x0, letter, faces, key, cases, piece, da, cen in ((WA, "b", FACES1, KEY1, CASES1, PIECE1, DA1, CEN1),
                                                      (WA + WD, "c", FACES2, KEY2, CASES2, PIECE2, DA2, CEN2)):
    ax = axin(x0 + 0.025, ya + (ROW1 - (WD - 0.05)) / 2, WD - 0.05, WD - 0.05)
    fig.text((x0 + WD / 2) / FW, (ya - 0.04) / FH, CAPTION[letter], ha="center", va="top", fontsize=8.4, color="0.15")
    cols = [PAL[k] for k in key]
    lab = labels(letter, faces, key, cases)
    el.draw_map(ax, faces, cols, [(x, y, t) for x, y, t, a in lab], letter, LIM, dpu, K, lfs=7.2)
    for x, y, t, a in lab:
        if a is not None:
            ax.plot([x, a[0]], [y, a[1]], color="0.15", lw=0.6, zorder=25, solid_capstyle="round")
            ax.plot([a[0]], [a[1]], "o", color="0.15", ms=1.6, zorder=25)

# ------------------------------------------------------------------ the key, in two parts
axt = axin(0, MB, FW, KH); axt.set_xlim(0, FW); axt.set_ylim(0, KH); axt.set_aspect("equal"); axt.axis("off")
TINT = dict(el.TINT); TINT["000"] = "white"
X0 = (FW - 2 * PW - GAP) / 2


def part(x0, cases):
    ytop = KH
    y = ytop - HH
    axt.text(x0 + SW / 2, y + HH / 2, "case", ha="center", va="center", fontsize=6.8, color="0.25")
    for j, c in enumerate(ORDER):
        axt.text(x0 + SW + (j + 0.5) * CW, y + HH / 2, c, ha="center", va="center", fontsize=6.8, family="monospace", color="0.25")
    for i, k in enumerate(cases):
        y = ytop - HH - (i + 1) * RH
        axt.add_patch(Rectangle((x0, y), SW, RH, fc=PAL[k], ec="white", lw=0.6))
        axt.text(x0 + SW / 2, y + RH / 2, NUM[k], ha="center", va="center", fontsize=7.5, fontweight="bold", color="0.05")
        for j, c in enumerate(ORDER):
            x = x0 + SW + j * CW
            if k[j] == "1":
                axt.add_patch(Rectangle((x, y), CW, RH, fc=TINT[c], ec="white", lw=0.6))
                axt.text(x + CW / 2, y + RH / 2, c, ha="center", va="center", fontsize=6.3, family="monospace", color="0.15",
                         fontweight="bold" if c == "111" else "normal")
            else:
                axt.add_patch(Rectangle((x, y), CW, RH, fc="white", ec="0.85", lw=0.5))
                axt.text(x + CW / 2, y + RH / 2, "∅", ha="center", va="center", fontsize=7.0, color="0.45")
    # a frame around the atom cells
    n = len(cases)
    axt.add_patch(Rectangle((x0, ytop - HH - n * RH), PW, n * RH, fc="none", ec="0.6", lw=0.6))


part(X0, LEFT)
part(X0 + PW + GAP, RIGHT)

fig.savefig(os.path.join(HERE, "Fig1.pdf")); fig.savefig(os.path.join(HERE, "Fig1.png"), dpi=220)
print("wrote Figure1/Fig1.pdf and Fig1.png (%.2f x %.2f in)" % (FW, FH))
