#!/usr/bin/env python3
"""
Figure 5: the share of the population with each property, in the two runs of Figure 4.

    python3 fig5.py             ->  Fig5.pdf / Fig5.png  (here)

Six disks: the two Wright-Fisher runs at N = 1000, beta = 100, mu = 1e-2, eps = 1e-4 (memory one above memory two,
data/runs/m1_N1000.csv and m2_N1000.csv); the columns the three properties, 1** efficient (the atoms 100, 110,
111), *1* stable (010, 110, 011, 111) and **1 competitive (001, 011, 111).  A panel shows the share of the population
held by the strategies that have the property, the sum of the shares of its atoms, on a linear viridis scale from 0
to 1; grey where no strategy of the space has the property at that game (memory one: no efficient strategy above
the switch line, no stable strategy on the Snowdrift games outside the unit square).  The properties overlap, so the
three panels of a row add up to more than one where the population holds strategies with two or three of them.
Frame, furniture and layout are those of Figure 4 (common.furniture, common.wfsheet's layout constants).  Panel
letters a-f row by row.

This is the original FinalFigures/fig5.py with the data loading replaced (the runs are read from the deposited tables
through data/runs/wfdata.py, which returns the arrays the original loader returned, bit for bit) and the output
path; the drawing is unchanged.  The original also drew SI Figure 5 (N = 100), which is SIFigure5/sifig5.py.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))                          # common/
sys.path.insert(0, os.path.join(HERE, os.pardir, "data", "runs"))          # wfdata.py
import wfdata                                                      # noqa: E402  the four runs, read from data/runs
from common import furniture as A                                  # noqa: E402  frame, furniture (Agg, rcParams)
from common.style import GREY                                      # noqa: E402  "0.84": no strategy has the property
import matplotlib.pyplot as plt                                    # noqa: E402
from matplotlib.cm import ScalarMappable                           # noqa: E402
from matplotlib.collections import PolyCollection                  # noqa: E402
from matplotlib.colors import Normalize                            # noqa: E402

ORDER = wfdata.ORDER
PROPS = [("efficient", "1**", ["100", "110", "111"]), ("stable", "*1*", ["010", "110", "011", "111"]),
         ("competitive", "**1", ["001", "011", "111"])]
CMAP, NORM = plt.get_cmap("viridis"), Normalize(vmin=0.0, vmax=1.0)


def shares(space, which):
    """per cell: the share of the population with each property and the number of strategies that have it"""
    S, N, E, UV, D = wfdata.load(space, which)
    PS = np.stack([S[:, [ORDER.index(a) for a in atoms]].sum(1) for _, _, atoms in PROPS], 1)
    PN = np.stack([N[:, [ORDER.index(a) for a in atoms]].sum(1) for _, _, atoms in PROPS], 1)
    print("%s %s (N = %d, beta = %d, mu = %s): share of the population with the property" % (space, which, D["N"], D["beta"], D["muplain"]))
    for j, (name, code, _) in enumerate(PROPS):
        v, gap = PS[:, j], PN[:, j] == 0
        print("   %-12s %s  mean %.3f  median %.3f  min %.4f  max %.3f  above 1/2 at %3d games  no strategy at %3d"
              % (name, code, v.mean(), np.median(v), v[~gap].min() if (~gap).any() else np.nan, v.max(), (v > 0.5).sum(), gap.sum()))
    return PS, PN


# ------------------------------------------------------------------- layout (inches; the panel of Figure 4)
PW, LIM, EXTT = A.PW, A.LIM, A.EXTT
EXTB = 0.08
PH = PW * (2 * LIM + EXTT + EXTB) / (2 * LIM)
ML, MR, MT, MB = 0.95, 0.15, 0.15, 0.20
COLGAP, ROWGAP = 0.45, 0.15
LEG = 0.80


def draw(rows, out):
    """the sheet: rows = [(space, which)] top to bottom, three property panels each; writes out (.pdf) and the .png"""
    NR = len(rows)
    FIG_W = ML + 3 * PW + 2 * COLGAP + MR
    FIG_H = MB + LEG + NR * PH + (NR - 1) * ROWGAP + MT
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    def cell(row, col):
        x = ML + col * (PW + COLGAP)
        y = MB + LEG + (NR - 1 - row) * (PH + ROWGAP)
        return fig.add_axes([x / FIG_W, y / FIG_H, PW / FIG_W, PH / FIG_H]), x, y

    pol, keep = wfdata.cells()
    letters = iter("abcdefghijklmnopqrstuvwxyz"[:3 * NR])
    for r, key in enumerate(rows):
        PS, PN = shares(*key)
        for c, (name, code, _) in enumerate(PROPS):
            ax, x, y = cell(r, c)
            fc = [GREY if PN[i, c] == 0 else CMAP(NORM(PS[i, c])) for i in keep]
            ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
            A.furniture(ax, next(letters), (r"$\mathbf{%s}$   %s" % (code.replace("*", r"{*}"), name)) if r == 0 else "")
            ax.set_ylim(-(LIM + EXTB), LIM + EXTT)
            if c == 0:
                fig.text((ML - 0.62) / FIG_W, (y + PH * (EXTB + LIM) / (2 * LIM + EXTT + EXTB)) / FIG_H, wfdata.LABEL[key], rotation=90,
                         ha="center", va="center", fontsize=A.FS * 1.25, color="0.12")

    # --------------------------------------------------------------- the colour bar, centred under the middle column
    CBH = A.CBH
    YLEG = MB + 0.5 * LEG
    xc = ML + PW + COLGAP + 0.5 * PW
    cax = fig.add_axes([(xc - 0.45 * PW) / FIG_W, (YLEG - 0.5 * CBH) / FIG_H, 0.9 * PW / FIG_W, CBH / FIG_H])
    cb = fig.colorbar(ScalarMappable(norm=NORM, cmap=CMAP), cax=cax, orientation="horizontal")
    cb.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]); cb.ax.set_xticklabels(["0", "20%", "40%", "60%", "80%", "100%"])
    cb.ax.minorticks_off(); cb.ax.tick_params(labelsize=A.FS * 0.82, length=5, width=1.0); cb.outline.set_linewidth(1.0)
    cax.text(-0.03, 0.5, "share of the population with the property", transform=cax.transAxes, ha="right", va="center", fontsize=A.FS * 0.95, color="0.12")
    cax.text(1.03, 0.5, "grey: no strategy has it", transform=cax.transAxes, ha="left", va="center", fontsize=A.FS * 0.95, color="0.12")

    # --------------------------------------------------------------- checks: nothing off the sheet
    fig.canvas.draw()
    R = fig.canvas.get_renderer()
    for ax_ in fig.axes:
        for t_ in list(ax_.texts) + (ax_.get_xticklabels() if ax_.axison else []):
            if t_.get_text() and t_.get_visible():
                bb = t_.get_window_extent(R)
                assert 0 < bb.x0 and bb.x1 < FIG_W * fig.dpi and 0 < bb.y0 and bb.y1 < FIG_H * fig.dpi, "text runs off the sheet: %r" % t_.get_text()
    for t_ in fig.texts:
        bb = t_.get_window_extent(R)
        assert 0 < bb.x0 and bb.x1 < FIG_W * fig.dpi and 0 < bb.y0 and bb.y1 < FIG_H * fig.dpi, "text runs off the sheet: %r" % t_.get_text()

    fig.savefig(out); fig.savefig(out.replace(".pdf", ".png"), dpi=110)
    plt.close(fig)
    print("wrote %s and .png (%.2f x %.2f in)" % (out, FIG_W, FIG_H))


if __name__ == "__main__":
    draw([k for k in wfdata.ROWS if k[1] == "F1"], os.path.join(HERE, "Fig5.pdf"))     # Figure 5: the large population
