#!/usr/bin/env python3
"""
SI Figure 8: the whole cube {N} x {beta} x {mu} of the memory-two Wright-Fisher process at eps = 1e-4 in one figure,
24 disks in three groups of eight:

    group 1 (a-h)  efficiency          group 2 (i-p)  most abundant atom          group 3 (q-x)  most enriched atom
    within a group: rows beta = 3 (top), beta = 100 (bottom); columns N = 100 (left pair), N = 1000 (right pair),
    mu = 1e-4 then 1e-2 within a pair.  Figure 4's two runs are the top-left and bottom-right corners of every group.

    python3 SIFigure8/sifig8.py          ->  SIFigure8/SIFig8.pdf and SIFig8.png

Data: data/robustness/games_<run>.csv of the eight corners (runs.csv) and m2_atom_sizes.csv, read by
data/robustness/wfruns.py.  Frame and colours of main text Figure 4 (common.wfsheet, common.furniture).  Only the
first disk of each group carries the rim names and tick labels; the other disks carry the letter and, in the top row of
a group, the run's N and mu.  The drawing is the original FinalFigures/sifig8.py unchanged; only the loading (the
eight corners from the deposited tables instead of the private packs) and the output path differ.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
from common import furniture as A                                   # noqa: E402  Agg + the figures' rcParams; frame
from common import wfsheet as fig4                                  # noqa: E402  the sheet of Figure 4
from common.atoms import ORDER                                      # noqa: E402
from common.games import cells_keep                                 # noqa: E402
from common.style import WINCOL                                     # noqa: E402
import wfruns                                                       # noqa: E402  the deposited runs

import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.cm import ScalarMappable                            # noqa: E402
from matplotlib.collections import PolyCollection                   # noqa: E402
from matplotlib.patches import Rectangle                            # noqa: E402

# the eight corners in reading order within a group: (beta row, N pair, mu) -> run (data/robustness/runs.csv)
CUBE = [((3, 100, "1e-4"), "f2_e4"), ((3, 100, "1e-2"), "c2_e4"),
        ((3, 1000, "1e-4"), "c4_e4"), ((3, 1000, "1e-2"), "dw4_e4"),
        ((100, 100, "1e-4"), "c3_e4"), ((100, 100, "1e-2"), "c1_e4"),
        ((100, 1000, "1e-4"), "dw3_e4"), ((100, 1000, "1e-2"), "f1_e4")]
GROUPS = ["efficiency", "most abundant atom", "most enriched atom"]
PW, LIM, EXTT, EXTB = A.PW, A.LIM, A.EXTT, fig4.EXTB
PH = PW * (2 * LIM + EXTT + EXTB) / (2 * LIM)
ML, MR, MT, MB, COLGAP, PAIRGAP, ROWGAP, GROUPGAP, LEG = 0.95, 0.15, 0.95, 0.20, 0.30, 0.75, 0.10, 0.85, 0.80   # MT holds the first group's title


def load_corner(run):
    g = wfruns.load(run)
    return g["S"], g["N"], g["E"], g["UV"], g["D"]


def draw_cube(out):
    S1, N1, E1, UV1, D1 = load_corner("f1_e4")
    corners = []
    for (beta, npop, mu), run in CUBE:
        S, N, E, UV, D = load_corner(run)
        assert (D["N"], D["beta"], D["muplain"], D["epsplain"]) == (npop, beta, mu, "1e-4"), run
        assert np.array_equal(N, N1) and np.allclose(UV, UV1), "the games or the census differ from Figure 4's"
        wa, we = fig4.winners(S, N, E, D, "N = %d, beta = %d, mu = %s" % (npop, beta, mu))
        corners.append((beta, npop, mu, E, wa, we))
    NR = 6
    FIG_W = ML + 4 * PW + 2 * COLGAP + PAIRGAP + MR
    FIG_H = MB + LEG + NR * PH + 3 * ROWGAP + 2 * GROUPGAP + MT
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    pol, keep = cells_keep()
    letters = iter("abcdefghijklmnopqrstuvwxyz")
    ECMAP, ENORM, ORDER_ = fig4.ECMAP, fig4.ENORM, ORDER

    def xy(g, r, c):                                                # group g (0..2), row r (0..1), column c (0..3)
        x = ML + c * (PW + COLGAP) + (PAIRGAP - COLGAP if c >= 2 else 0)
        y = MB + LEG + (NR - 1 - (2 * g + r)) * PH + (3 - (2 * g + r) - (1 if 2 * g + r >= 2 else 0) - (1 if 2 * g + r >= 4 else 0)) * ROWGAP \
            + (2 - g) * GROUPGAP
        return x, y

    for g, gname in enumerate(GROUPS):
        for k, (beta, npop, mu, E, wa, we) in enumerate(corners):
            r, c = k // 4, k % 4
            x, y = xy(g, r, c)
            ax = fig.add_axes([x / FIG_W, y / FIG_H, PW / FIG_W, PH / FIG_H])
            if g == 0:
                fc = [ECMAP(ENORM(E[i])) if E[i] >= 0 else ECMAP.get_under() for i in keep]
            else:
                win = wa if g == 1 else we
                fc = [WINCOL[ORDER_[win[i]]] for i in keep]
            ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
            letter = next(letters)
            title = "$N = %d$, $\\mu = 10^{%s}$" % (npop, mu[2:]) if r == 0 else ""
            A.furniture(ax, letter, title)
            ax.set_ylim(-(LIM + EXTB), LIM + EXTT)
            if k != 0:                                              # rim names and tick labels on the first disk of a group only
                for txt in list(ax.texts):
                    if txt.get_text() not in (letter, title):
                        txt.remove()
                for patch in list(ax.patches):                      # the rim names are arc_text patches
                    patch.remove()
            if c == 0:
                fig.text((ML - 0.62) / FIG_W, (y + PH * (EXTB + LIM) / (2 * LIM + EXTT + EXTB)) / FIG_H, "$\\beta = %d$" % beta,
                         rotation=90, ha="center", va="center", fontsize=A.FS * 1.25, color="0.12")
        x0, y0 = xy(g, 0, 0); x3, _ = xy(g, 0, 3)
        fig.text((x0 + 0.5 * (x3 + PW - x0)) / FIG_W, (y0 + PH + 0.42) / FIG_H, gname, ha="center", va="bottom",
                 fontsize=A.FS * 1.6, fontweight="bold", color="0.12")
        xl, _ = xy(g, 0, 0); xr, _ = xy(g, 0, 2)
        for xx, lab in ((xl + PW + 0.5 * COLGAP, "$N = 100$"), (xr + PW + 0.5 * COLGAP, "$N = 1000$")):
            fig.text(xx / FIG_W, (y0 + PH + 0.42) / FIG_H, lab, ha="center", va="bottom", fontsize=A.FS * 1.1, color="0.35")
    # legends
    CBH = A.CBH; YLEG = MB + 0.5 * LEG
    cax = fig.add_axes([(ML + 0.18 * PW) / FIG_W, (YLEG - 0.5 * CBH) / FIG_H, 0.64 * PW / FIG_W, CBH / FIG_H])
    cb = fig.colorbar(ScalarMappable(norm=ENORM, cmap=ECMAP), cax=cax, orientation="horizontal", extend="min", extendfrac=0.05)
    cb.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]); cb.ax.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])
    cb.ax.minorticks_off(); cb.ax.tick_params(labelsize=A.FS * 0.82, length=5, width=1.0); cb.outline.set_linewidth(1.0)
    cax.text(0.5, 1.45, "efficiency (a-h); black: below 0", transform=cax.transAxes, ha="center", va="bottom", fontsize=A.FS * 0.95, color="0.12")
    axL = fig.add_axes([0, 0, 1, 1]); axL.set_xlim(0, FIG_W); axL.set_ylim(0, FIG_H); axL.set_aspect("equal"); axL.axis("off")
    SW, LFS = CBH, A.LFS
    LW = A.LW * PW / (2 * LIM); PITCH = SW + 0.03 + LW + 0.06
    xc = ML + 2 * PW + COLGAP + PAIRGAP + 0.5 * PW                # centre of columns 3-4
    x0 = xc - 0.5 * (6 * PITCH + SW + 0.03 + LW)
    for i, code in enumerate(ORDER_):
        xi = x0 + i * PITCH
        axL.add_patch(Rectangle((xi, YLEG - 0.5 * SW), SW, SW, fc=WINCOL[code], ec="0.25", lw=0.6, zorder=12))
        axL.text(xi + SW + 0.03, YLEG, code, fontsize=LFS, fontweight="bold", color="0.12", ha="left", va="center", zorder=12)
    axL.text(xc, YLEG + 0.5 * SW + 0.12, "the atom (i-x)", ha="center", va="bottom", fontsize=A.FS * 0.95, color="0.12")
    fig.savefig(out); fig.savefig(out.replace(".pdf", ".png"), dpi=72); plt.close(fig)
    print("wrote %s and .png (%.2f x %.2f in)" % (out, FIG_W, FIG_H))


if __name__ == "__main__":
    draw_cube(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "SIFig8.pdf"))
