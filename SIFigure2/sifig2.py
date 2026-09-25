#!/usr/bin/env python3
"""
SI Figure 2: the share of the population in each atom -- efficient, stable, competitive -- on the disk of games, and
the most abundant atom at each game, for the 16 binary memory-one strategies in the two Wright-Fisher runs:
N = 100, beta = 3, mu = 1e-4 (rows 1-2, panels a-h; data/runs/m1_N100.csv) and N = 1000, beta = 100, mu = 1e-2
(rows 3-4, panels i-p; data/runs/m1_N1000.csv), eps = 1e-4 in both.

    python3 sifig2.py            ->  SIFig2.pdf / SIFig2.png  (here)

Panels a-g, i-o: the time-averaged share of the population held by the strategies of one atom at each of the 512
games (the Voronoi cells of the Fermat sunflower, data/games), viridis on a linear scale from 0 to 1, grey where the
atom has no strategy at that game.  Panels h, p: each game coloured by the atom with the largest share, with the
swatch legend under the last one.

draw_runs() is the original FinalFigures/atomshares.draw_runs(), shared there by SI Figures 2 and 3 (SIFigure3/sifig3.py
carries the same function); the frame, furniture, colours and layout constants now come from common/ (furniture,
style, atoms), and the runs are read from the deposited tables through data/runs/wfdata.py, which returns the arrays
the original loader returned, bit for bit.  The drawing is unchanged.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))                          # common/
sys.path.insert(0, os.path.join(HERE, os.pardir, "data", "runs"))          # wfdata.py
import wfdata                                                      # noqa: E402  the four runs, read from data/runs
from common.furniture import (furniture, ML, MR, MB, MT, NCOL, PW, PH, COLGAP, ROWGAP, LIM, EXTB, EXTT, FS,  # noqa: E402
                              CBH, SW, LFS, PITCH, X0, YL)          # frame and layout (Agg, rcParams on import)
from common.style import GREY, WINCOL                              # noqa: E402
from common.atoms import ORDER, NAME                               # noqa: E402
import matplotlib.pyplot as plt                                    # noqa: E402
from matplotlib.cm import ScalarMappable                           # noqa: E402
from matplotlib.collections import PolyCollection                  # noqa: E402
from matplotlib.colors import Normalize                            # noqa: E402
from matplotlib.patches import Rectangle                           # noqa: E402

HEAD_DX = {"111": 0.03}   # data units: the head of the 111 panels, two letters longer since "Nash" became "stable",
                           # would come within 0.08 in of its panel letter if centred; 0.03 (0.055 in) to the right
                           # gives back the 0.13 in it had
CMAP = plt.get_cmap("viridis").copy()
CMAP.set_under("#270031")                        # (atomshares' logit variant only; never reached on the linear scale)


def draw_runs(runs, out, labels):
    """Two (or more) runs on one sheet, two rows of four per run: the shares of the seven atoms (viridis, linear, grey
    where the atom has no strategy) and the most abundant atom; the colour bar and the swatch legend once, at the
    bottom.  runs = [(space, which), ...] read through wfdata.load ("m1" or "m2", "F1" or "F2"); labels = the text
    printed rotated at the left of each block.  Writes out (.pdf) and the .png beside it."""
    NR = 2 * len(runs)
    LABW = 0.75
    W = ML + LABW + NCOL * PW + (NCOL - 1) * COLGAP + MR
    H = MB + NR * PH + (NR - 1) * ROWGAP + MT
    fig = plt.figure(figsize=(W, H))

    def xy(row, col):
        return (ML + LABW + col * (PW + COLGAP), MB + (NR - 1 - row) * (PH + ROWGAP))

    def cell(row, col):
        x, y = xy(row, col)
        return fig.add_axes([x / W, y / H, PW / W, PH / H])

    pol, keep = wfdata.cells()
    norm = Normalize(vmin=0.0, vmax=1.0)
    letters = iter("abcdefghijklmnopqrstuvwx")
    for b, (space, which) in enumerate(runs):
        S, N, E, UV, D = wfdata.load(space, which)                 # (512, 7) in ORDER, in cell order 0..511
        GAP = N == 0
        arg = np.where(GAP, -np.inf, S).argmax(1)
        print("%s %s (N = %d, beta = %d, mu = %s): share of the population per atom, 512 games" % (space, which, D["N"], D["beta"], D["muplain"]))
        print("%-4s %8s %8s %8s %8s  %6s  %6s" % ("atom", "mean", "median", "min", "max", "empty", "winner"))
        for i, code in enumerate(ORDER):
            row, col = divmod(i, NCOL)
            ax = cell(2 * b + row, col)
            fc = [GREY if GAP[k, i] else CMAP(norm(S[k, i])) for k in keep]
            ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
            head = r"$\mathbf{%s}$   %s" % (code, NAME[code])
            furniture(ax, next(letters), head)
            if code in HEAD_DX:                                    # the longest head, clear of the panel letter
                (t_,) = [t_ for t_ in ax.texts if t_.get_text() == head]
                t_.set_x(HEAD_DX[code])
            ok = S[~GAP[:, i], i]
            print("%-4s %8.4f %8.4f %8.5f %8.4f  %6d  %6d" % (code, S[:, i].mean(), np.median(S[:, i]), ok.min() if len(ok) else np.nan,
                                                            S[:, i].max(), GAP[:, i].sum(), (arg == i).sum()))
        ax = cell(2 * b + 1, 3)
        fc = [WINCOL[ORDER[arg[k]]] for k in keep]
        ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
        furniture(ax, next(letters), "most abundant atom")
        srt = np.sort(np.where(GAP, -np.inf, S), 1)
        print("most abundant atom: " + ", ".join("%s %d" % (c, (arg == i).sum()) for i, c in enumerate(ORDER) if (arg == i).any())
              + ";  its share: median %.3f; decided by < 0.05 at %d games" % (np.median(srt[:, -1]), ((srt[:, -1] - srt[:, -2]) < 0.05).sum()))
        x0, y0 = xy(2 * b, 0); x1, y1 = xy(2 * b + 1, 0)
        yc = 0.5 * (y0 + y1) + PH * (LIM + EXTB) / (2 * LIM + EXTT + EXTB)
        fig.text((x0 - 0.45) / W, yc / H, labels[b], rotation=90, ha="center", va="center", fontsize=FS * 1.25, color="0.12")
    # the bottom line, in the last row's own bottom margin: the swatch legend under the last panel h, the colour bar under columns 1-2
    legend = []
    for i, code in enumerate(ORDER):
        xi = X0 + i * PITCH
        ax.add_patch(Rectangle((xi, YL - 0.5 * SW), SW, SW, fc=WINCOL[code], ec="0.25", lw=0.6, zorder=12, clip_on=False))
        legend.append(ax.text(xi + SW + 0.02, YL, code, fontsize=LFS, fontweight="bold", color="0.12", ha="left", va="center", zorder=12))
    CBX0, CBX1 = ML + LABW + 0.72 * PW, ML + LABW + 2 * PW + COLGAP - 0.22 * PW
    ylast = xy(NR - 1, 0)[1]
    ycb = ylast + (YL + LIM + EXTB) * PW / (2 * LIM)
    cax = fig.add_axes([CBX0 / W, (ycb - 0.5 * CBH) / H, (CBX1 - CBX0) / W, CBH / H])
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP), cax=cax, orientation="horizontal")
    cb.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]); cb.ax.set_xticklabels(["0", "20%", "40%", "60%", "80%", "100%"])
    cb.ax.minorticks_off(); cb.ax.tick_params(labelsize=FS * 0.82, length=5, width=1.0); cb.outline.set_linewidth(1.0)
    cax.text(-0.025, 0.5, "share of the population (the atom panels)", transform=cax.transAxes, ha="right", va="center", fontsize=FS * 0.95, color="0.12")
    # checks: nothing off the sheet, no two heads overlapping, the legend entries apart
    fig.canvas.draw()
    R = fig.canvas.get_renderer()
    def on_sheet(t):
        bb = t.get_window_extent(R)
        assert 0 < bb.x0 and bb.x1 < W * fig.dpi and 0 < bb.y0 and bb.y1 < H * fig.dpi, "text runs off the sheet: %r" % t.get_text()
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
    for i_ in range(len(legend) - 1):
        nxt = ax.transData.transform((X0 + (i_ + 1) * PITCH, YL))[0]
        assert legend[i_].get_window_extent(R).x1 < nxt - 2, "legend entry %d runs into the next swatch" % i_
    fig.savefig(out)
    fig.savefig(out.replace(".pdf", ".png"), dpi=150)
    plt.close(fig)
    print("%s: %.2f x %.2f in, pdf %.1f MB" % (os.path.basename(out), W, H, os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    draw_runs([("m1", "F2"), ("m1", "F1")], os.path.join(HERE, "SIFig2.pdf"), ["Memory-1, $N = 100$", "Memory-1, $N = 1000$"])
