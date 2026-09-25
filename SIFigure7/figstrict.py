#!/usr/bin/env python3
"""
figstrict.py -- the sheet of SI Figures 6 and 7: the strict Nash equilibria at the error rate of the runs,
eps = 1e-4, and how much of the population sits on them, for memory one and memory two. SI Figure 6 shows all strict
equilibria (sifig6.py), SI Figure 7 only the efficient ones (sifig7.py).

    python3 sifig6.py            ->  SIFig6.pdf        draw(efficient=False)
    python3 sifig7.py            ->  SIFig7.pdf        draw(efficient=True)
    (add --png to also write the 110-dpi PNG the original script wrote)

Six disks show the 512 games of the Wright-Fisher maps on their Voronoi cells, in the frame of Figures 4 and 5:

    row 1   the 16 binary memory-one strategies (a-c)     row 2   the 65536 binary memory-two strategies (d-f)
    column 1   the number of strategies that are strict Nash equilibria at eps = 1e-4 (and efficient, in SI Figure 7).
               Each panel has its own colour scale in Figure 2's style (common.counts.atom_scale: bands for a few
               values, an equal-area ramp otherwise, grey where there is none). The labels of a discrete bar are
               centred in their bands.
    column 2   the share of the population on those strategies in the run at N = 100 (beta = 3, mu = 1e-4)
    column 3   the same at N = 1000 (beta = 100, mu = 1e-2). Columns 2 and 3 are linear from 0 to 1, grey where the
               game has none

Data: ../data/strict/m1_games.csv and m2_games.csv (see ../data/strict/README.md), in ipt order. The games and cells
come from ../data/games through common.games.

This is the author's FinalFigures/figstrict.py. The drawing code is unchanged; only the data loading was replaced. The
original read the same numbers through strictne.py, from the private run outputs and caches that
../provenance/strict/reduce_strict.py reduces to the tables. The output path became an argument. This file is
identical in SIFigure6/ and SIFigure7/, so that each folder stands alone.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))
from common import furniture as A                                  # noqa: E402  frame, furniture (atomshares.py; sets its rcParams)
from common import counts as C                                     # noqa: E402  the count scales of Figure 2 (atomcounts.py)
from common import games, tables                                   # noqa: E402  the cells; the table reader
from common.style import GREY                                      # noqa: E402

DATA = os.path.join(HERE, os.pardir, "data", "strict")
CMAP, NORM = plt.get_cmap("viridis"), Normalize(vmin=0.0, vmax=1.0)

# ------------------------------------------------------------------- layout (inches; the panel of Figures 4 and 5)
PW, LIM, EXTT = A.PW, A.LIM, A.EXTT
EXTB = 0.08
PH = PW * (2 * LIM + EXTT + EXTB) / (2 * LIM)
ML, MR, MT, MB = 0.95, 0.15, 0.15, 0.20
COLGAP, ROWGAP = 0.45, 0.15
LEG = 0.80
CBW, CBGAP, CBLAB, CBHV = C.CBW, C.CBGAP, C.CBLAB, C.CBH               # the vertical count bars, as in Figure 2
COL1 = PW + CBGAP + CBW + CBLAB
FIG_W = ML + COL1 + 2 * PW + 2 * COLGAP + MR
FIG_H = MB + LEG + 2 * PH + ROWGAP + MT


def data(efficient):
    """the two rows: (label, counts (512,), shares {which: (512,)}) for memory one and memory two, in ipt order.
    which = "F2" is the run at N = 100, "F1" the run at N = 1000 (the runs' names in the kits)."""
    T1 = tables.read_table(os.path.join(DATA, "m1_games.csv"))
    T2 = tables.read_table(os.path.join(DATA, "m2_games.csv"))
    for T in (T1, T2):
        assert np.array_equal(T["ipt"], np.arange(games.NGAME)), "not in ipt order"
        assert np.array_equal(np.column_stack([T["u"], T["v"]]), games.uv()), "the table lists other games than data/games"
        assert (T["n_weak"] == T["n_strict"]).all(), "weak and strict equilibria differ somewhere"
    key = "eff_" if efficient else ""
    rows = []
    for label, T in (("Memory-1, 16 strategies", T1), ("Memory-2, 65536 strategies", T2)):
        rows.append((label, T["n_%sstrict" % key], {w: T["share_%s%s" % (key, w)] for w in ("F2", "F1")}))
    return rows


def draw(efficient, out, png=False):
    """the sheet; writes out (a .pdf path) and, if png, the same with .png at 110 dpi"""
    what = "efficient strict Nash equilibria" if efficient else "strict Nash equilibria"
    head = "efficient strict equilibria" if efficient else "strict Nash equilibria"      # the long form runs into the panel letter
    cols = [head + r" at $\epsilon = 10^{-4}$", "share of the population, $N = 100$", "share of the population, $N = 1000$"]
    rows = data(efficient)
    pol, keep = games.cells_keep()
    area = np.zeros(512)
    for i, p in zip(keep, pol):
        x, y = np.asarray(p)[:, 0], np.asarray(p)[:, 1]
        area[i] = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    def cell(row, col):
        x = ML + (0 if col == 0 else COL1 + COLGAP + (col - 1) * (PW + COLGAP))
        y = MB + LEG + (1 - row) * (PH + ROWGAP)
        return fig.add_axes([x / FIG_W, y / FIG_H, PW / FIG_W, PH / FIG_H]), x, y

    letters = iter("abcdef")
    for r, (label, n, share) in enumerate(rows):
        for c, title in enumerate(cols):
            ax, x, y = cell(r, c)
            if c == 0:
                vals = n.astype(float)
                cm, norm, ticks, lab, disc = C.atom_scale(vals, area)
                fc = [cm(norm(vals[i])) for i in keep]
            else:
                s = share["F2" if c == 1 else "F1"]
                fc = [GREY if n[i] == 0 else CMAP(NORM(s[i])) for i in keep]
            ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
            A.furniture(ax, next(letters), title if r == 0 else "")
            ax.set_ylim(-(LIM + EXTB), LIM + EXTT)
            if c == 0:
                fig.text((ML - 0.62) / FIG_W, (y + PH * (EXTB + LIM) / (2 * LIM + EXTT + EXTB)) / FIG_H, label, rotation=90,
                         ha="center", va="center", fontsize=A.FS * 1.25, color="0.12")
                # the count scale, to the right of the disk (Figure 2's bar)
                yc = y + PH * (LIM + EXTB) / (2 * LIM + EXTT + EXTB)
                cax = fig.add_axes([(x + PW + CBGAP) / FIG_W, (yc - 0.5 * CBHV) / FIG_H, CBW / FIG_W, CBHV / FIG_H])
                if disc:                                       # label each band at its centre, not at the level's position inside it
                    bnd = np.asarray(norm.boundaries, float)
                    ticks = [0.5 * (bnd[k] + bnd[k + 1]) for k in range(len(bnd) - 1)]
                    assert len(ticks) == len(lab)
                cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cm), cax=cax, ticks=ticks, spacing="uniform", drawedges=disc,
                                  extend="min" if (vals == 0).any() else "neither", extendfrac=0.06)
                cb.ax.set_yticklabels(lab)
                cb.ax.minorticks_off()
                for lb in (cb.ax.get_yticklabels()[0], cb.ax.get_yticklabels()[-1]):
                    lb.set_fontweight("bold")
                cb.set_label("Number of strategies", fontsize=A.FS * 0.95, labelpad=10)
                cb.ax.tick_params(labelsize=A.FS * (0.72 if disc else 0.82), length=5, width=1.0)
                if disc:
                    cb.outline.set_linewidth(1.0)
                    cb.dividers.set_color("white")
                    cb.dividers.set_linewidth(0.6)
                if (vals == 0).any():
                    cb.ax.text(1.45, -0.045, "0", transform=cb.ax.transAxes, fontsize=A.FS * 0.72, ha="left", va="center", color="0.25")
        zero = n == 0
        print("%s: %s per game %d..%d, median %d, none at %d games (%.1f%% of the cell area); share on them N = 100: max %.3f median %.3f, "
              "above 1/2 at %d games; N = 1000: max %.3f median %.3f, above 1/2 at %d games"
              % (label, what, n.min(), n.max(), np.median(n), zero.sum(), 100 * area[zero].sum() / area.sum(), share["F2"].max(),
                 np.median(share["F2"]), (share["F2"] > 0.5).sum(), share["F1"].max(), np.median(share["F1"]), (share["F1"] > 0.5).sum()))

    # the share bar, centred under column 2 (its labels reach left and right)
    CBH = A.CBH
    YLEG = MB + 0.5 * LEG
    xc = ML + COL1 + COLGAP + 0.5 * PW
    cax = fig.add_axes([(xc - 0.45 * PW) / FIG_W, (YLEG - 0.5 * CBH) / FIG_H, 0.9 * PW / FIG_W, CBH / FIG_H])
    cb = fig.colorbar(ScalarMappable(norm=NORM, cmap=CMAP), cax=cax, orientation="horizontal")
    cb.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]); cb.ax.set_xticklabels(["0", "20%", "40%", "60%", "80%", "100%"])
    cb.ax.minorticks_off(); cb.ax.tick_params(labelsize=A.FS * 0.82, length=5, width=1.0); cb.outline.set_linewidth(1.0)
    cax.text(-0.03, 0.5, "share of the population on " + what, transform=cax.transAxes, ha="right", va="center", fontsize=A.FS * 0.95, color="0.12")
    cax.text(1.03, 0.5, "grey: no %sstrict equilibrium at the game" % ("efficient " if efficient else ""), transform=cax.transAxes,
             ha="left", va="center", fontsize=A.FS * 0.95, color="0.12")

    # checks: nothing off the sheet, no head running into a letter or another head
    fig.canvas.draw()
    R = fig.canvas.get_renderer()

    def on_sheet(t):
        bb = t.get_window_extent(R)
        assert 0 < bb.x0 and bb.x1 < FIG_W * fig.dpi and 0 < bb.y0 and bb.y1 < FIG_H * fig.dpi, "text runs off the sheet: %r" % t.get_text()

    for t_ in fig.texts:
        on_sheet(t_)
    for ax_ in fig.axes:
        for t_ in list(ax_.texts) + (ax_.get_xticklabels() + ax_.get_yticklabels() if ax_.axison else []):
            if t_.get_text() and t_.get_visible():
                on_sheet(t_)
        heads = [t_ for t_ in ax_.texts if t_.get_text() and t_.get_va() == "bottom" and t_.get_ha() in ("center", "left")]
        for i_ in range(len(heads)):
            for j_ in range(i_ + 1, len(heads)):
                assert not heads[i_].get_window_extent(R).overlaps(heads[j_].get_window_extent(R)), \
                    "texts overlap: %r / %r" % (heads[i_].get_text(), heads[j_].get_text())
    fig.savefig(out)
    if png:
        fig.savefig(out[:-4] + ".png", dpi=110)
    plt.close(fig)
    print("wrote %s%s (%.2f x %.2f in)" % (out, " and .png" if png else "", FIG_W, FIG_H))
