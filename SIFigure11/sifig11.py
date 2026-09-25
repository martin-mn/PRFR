#!/usr/bin/env python3
"""
SI Figure 11: how certain the two memory-two maps of main text Figure 4 and SI Figure 4 are, game by game.

    python3 SIFigure11/sifig11.py [run ...]    ->  SIFigure11/SIFig11.pdf and SIFig11.png, and the numbers the text quotes

Rows: the two memory-two runs, N = 100 (f2_e4 = DiskM2WF dw2, SI Figure 4d-f) above N = 1000 (f1_e4 = dw1, main text
Figure 4d-f).  Columns:
    a, d  the margin between the largest and the second-largest atom share of the pooled population (how far the
          winner of SI Figure 4e / main text Figure 4e is from the runner-up);
    b, e  the standard deviation of the realised efficiency over the ten replicates, saturated at 0.2;
    c, f  the number of the ten replicates whose own most abundant atom (their exact per-replicate atom shares) is the
          pooled map's.
Printed, per run: the margin, the efficiency spread, the agreement of the ten replicates (exact, and the rank-1 proxy:
replicates whose own most abundant STRATEGY lies in the map's most abundant atom), and the range over the ten
single-replicate maps of the games 111 and 110 lead -- for the two runs drawn and then for every further run with
per-replicate output (default; extra arguments name the runs to report on).  These are the numbers of the paragraph
"Replicates" of the SI.

Data: data/robustness/games_<run>.csv and replicates_<run>.csv (data/robustness/wfruns.py).  The drawing is the original
FinalFigures/sifig11.py unchanged; the loading (pooled shares and efficiency, and the per-replicate output of the
bit-for-bit regenerations f1_e4 and f2_e4, from the deposited tables) and the output path differ.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
from common import furniture as A                                   # noqa: E402  Agg + the figures' rcParams; frame
from common import wfsheet as fig4                                  # noqa: E402
from common import games                                            # noqa: E402
from common.games import cells_keep                                 # noqa: E402
import wfruns                                                       # noqa: E402

import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.cm import ScalarMappable                            # noqa: E402
from matplotlib.collections import PolyCollection                   # noqa: E402
from matplotlib.colors import BoundaryNorm, Normalize, ListedColormap   # noqa: E402

PW, LIM, EXTT, EXTB = A.PW, A.LIM, A.EXTT, fig4.EXTB
PH = PW * (2 * LIM + EXTT + EXTB) / (2 * LIM)
ML, MR, MT, MB, COLGAP, ROWGAP, LEG = 0.95, 0.15, 0.15, 0.20, 0.45, 0.15, 0.80
MARGIN = (plt.get_cmap("cividis"), Normalize(0.0, 1.0))
SD = (plt.get_cmap("viridis"), Normalize(0.0, 0.2))
AGREE = (ListedColormap(plt.get_cmap("magma")(np.linspace(0.15, 0.97, 11))), BoundaryNorm(np.arange(-0.5, 11.5, 1.0), 11))
COLS = [("margin of the most abundant atom", MARGIN, [0, 0.25, 0.5, 0.75, 1.0], ["0", "0.25", "0.5", "0.75", "1"],
         "largest atom share minus the second largest"),
        ("s.d. of efficiency over replicates", SD, [0, 0.05, 0.1, 0.15, 0.2], ["0", "0.05", "0.1", "0.15", "0.2+"],
         "s.d. of the efficiency over the 10 replicates"),
        ("replicates agreeing with the map", AGREE, list(range(0, 11, 2)), [str(t) for t in range(0, 11, 2)],
         "replicates, of 10, whose leading atom is the map's")]
NCOL = 2                     # 3 when every row has the exact per-replicate atom shares (it does: f1_e4, f2_e4)


def main_run(run):
    """the pooled shares, the efficiency spread and the replicates of one of Figure 4's memory-two runs"""
    r = wfruns.load(run)
    D = r["D"]
    label = "Memory-2, $N = %d$\n$\\beta = %d$, $\\mu = %s$" % (D["N"], D["beta"], D["mu"])
    g = dict(S=r["S"], E=r["E"], sd=np.nanstd(r["ER"], axis=1, ddof=1), LEAD=r["LEAD"], label=label,
             name="%s (N = %d)" % (run, D["N"]), R=r["R"])
    return g


def margin(S):
    t = np.sort(S, axis=1)
    return t[:, -1] - t[:, -2]


def report(name, S, sd, agree, R=None):
    win = S.argmax(1); m = margin(S)
    out = ("%s: margin median %.2f, below 0.05 at %d games and below 0.1 at %d; efficiency s.d. median %.3f, above 0.1 at %d; "
           "agreement (rank-1 proxy) all ten at %d games, five or fewer at %d" %
           (name, np.median(m), (m < 0.05).sum(), (m < 0.1).sum(), np.median(sd), (sd > 0.1).sum(), (agree == 10).sum(), (agree <= 5).sum()))
    if R is not None:
        ex = (R.argmax(2) == win[:, None]).sum(1)
        lead = R.argmax(2)                                            # (512, 10): each replicate's own leading atom
        n111 = (lead == 6).sum(0); n110 = (lead == 4).sum(0)
        out += ("; exact agreement all ten at %d, five or fewer at %d; single-replicate maps: 111 leads %d-%d games (pooled %d), "
                "110 leads %d-%d (pooled %d)" % ((ex == 10).sum(), (ex <= 5).sum(), n111.min(), n111.max(), (win == 6).sum(),
                                                n110.min(), n110.max(), (win == 4).sum()))
    print(out)


def draw(rows, out):
    NR = len(rows)
    ncol = 3 if all(g["R"] is not None for g in rows) else NCOL
    FIG_W = ML + ncol * PW + (ncol - 1) * COLGAP + MR
    FIG_H = MB + LEG + NR * PH + (NR - 1) * ROWGAP + MT
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    pol, keep = cells_keep()
    letters = iter("abcdefghijklmnopqrstuvwxyz")
    for r, g in enumerate(rows):
        win = g["S"].argmax(1)
        agree = (g["LEAD"] == win[:, None]).sum(1)                   # the rank-1 proxy (reported)
        exact = (g["R"].argmax(2) == win[:, None]).sum(1) if g["R"] is not None else agree
        vals = [margin(g["S"]), np.minimum(g["sd"], 0.2), exact]
        report(g["name"], g["S"], g["sd"], agree, g["R"])
        for c, ((title, (cmap, norm), _, _, _), v) in enumerate(zip(COLS[:ncol], vals)):
            x = ML + c * (PW + COLGAP); y = MB + LEG + (NR - 1 - r) * (PH + ROWGAP)
            ax = fig.add_axes([x / FIG_W, y / FIG_H, PW / FIG_W, PH / FIG_H])
            fc = [cmap(norm(v[i])) for i in keep]
            ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
            A.furniture(ax, next(letters), title if r == 0 else "")
            ax.set_ylim(-(LIM + EXTB), LIM + EXTT)
            if c == 0:
                fig.text((ML - 0.62) / FIG_W, (y + PH * (EXTB + LIM) / (2 * LIM + EXTT + EXTB)) / FIG_H, g["label"], rotation=90,
                         ha="center", va="center", fontsize=A.FS * 1.05, color="0.12")
    CBH = A.CBH; YLEG = MB + 0.5 * LEG
    for c, (_, (cmap, norm), ticks, labels, title) in enumerate(COLS[:ncol]):
        x = ML + c * (PW + COLGAP)
        cax = fig.add_axes([(x + 0.18 * PW) / FIG_W, (YLEG - 0.5 * CBH) / FIG_H, 0.64 * PW / FIG_W, CBH / FIG_H])
        cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal")
        cb.set_ticks(ticks); cb.ax.set_xticklabels(labels)
        cb.ax.minorticks_off(); cb.ax.tick_params(labelsize=A.FS * 0.82, length=5, width=1.0); cb.outline.set_linewidth(1.0)
        cax.text(0.5, 1.45, title, transform=cax.transAxes, ha="center", va="bottom", fontsize=A.FS * 0.95, color="0.12")
    fig.savefig(out); fig.savefig(out.replace(".pdf", ".png"), dpi=110); plt.close(fig)
    print("wrote %s and .png (%.2f x %.2f in)" % (out, FIG_W, FIG_H))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.endswith(".pdf")]
    outs = [a for a in sys.argv[1:] if a.endswith(".pdf")]
    rows = [main_run("f2_e4"), main_run("f1_e4")]
    draw(rows, outs[0] if outs else os.path.join(HERE, "SIFig11.pdf"))
    Q = games.games()["quadrant"]
    for g in rows:                                                    # the text: "only at 14 and 3 Stag Hunts"
        print("%s: the efficiency s.d. exceeds 0.1 at %s" % (g["name"], ", ".join("%d %s" % (int((Q[g["sd"] > 0.1] == q).sum()), q)
                                                                       for q in ("PD", "SH", "SD", "HA") if (Q[g["sd"] > 0.1] == q).any()) or "no game"))
    runs = args or [r for r in wfruns.RUNS if r not in ("f1_e4", "f2_e4")]
    for run in runs:
        g = wfruns.load(run)
        if g["R"] is None:
            continue                                                  # dw3, dw4: no per-replicate output
        win = g["S"].argmax(1)
        report(run, g["S"], np.nanstd(g["ER"], axis=1, ddof=1), (g["LEAD"] == win[:, None]).sum(1), g["R"])
