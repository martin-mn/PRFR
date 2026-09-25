"""
The sheet of main text Figure 4 -- rows of three disks on the 512 sunflower cells: the efficiency, the most abundant
atom, the most enriched atom -- which SI Figures 4, 9, 10 and 12 reuse row for row and SI Figure 8 reuses in part
(fig4.py's draw() and winners(), moved here unchanged apart from the output path).

    winners(S, N, E, D, name) -> (wa, we)          the most abundant and the most enriched atom per game, and a receipt
    draw(rows, out)                                 the sheet, rows = [(label, E, wa, we)], written to out and out.png
    efficiency_bar(fig, W, H, x, yleg, label)       the horizontal efficiency colour bar under a column
    sheet_legend(fig, W, H, xc, yleg, title)        the swatch legend of the seven atoms centred at xc (inches)

Importing this module imports common.furniture (Agg backend, the figures' rcParams).
"""
import numpy as np

from . import furniture as A                                        # Agg + rcParams; frame, furniture, colours
import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.cm import ScalarMappable                            # noqa: E402
from matplotlib.collections import PolyCollection                   # noqa: E402
from matplotlib.colors import Normalize                             # noqa: E402
from matplotlib.patches import Rectangle                            # noqa: E402

from .atoms import ORDER                                            # noqa: E402
from .games import cells_keep                                       # noqa: E402
from .style import WINCOL                                           # noqa: E402

ECMAP = plt.get_cmap("viridis").copy()
ECMAP.set_under("black")                                           # a negative mean payoff
ENORM = Normalize(vmin=0.0, vmax=1.0)
COLS = ["efficiency", "most abundant atom", "most enriched atom"]

# the four main Wright-Fisher runs (wfdata.py): (space, which) -> row label; F1 = N 1000, beta 100, mu 1e-2; F2 = N 100,
# beta 3, mu 1e-4; eps = 1e-4 in all four.  ROWS is the order of the rows of Figures 4 and 5 and SI Figures 4 and 5.
LABEL = {("m1", "F2"): "Memory-1, $N = 100$", ("m1", "F1"): "Memory-1, $N = 1000$",
         ("m2", "F2"): "Memory-2, $N = 100$", ("m2", "F1"): "Memory-2, $N = 1000$"}
ROWS = [("m1", "F2"), ("m1", "F1"), ("m2", "F2"), ("m2", "F1")]


def winners(S, N, E, D, name):
    """per cell: the most abundant and the most enriched atom (indices into ORDER), with a printed summary.

    S (512, 7) atom shares in ORDER, N (512, 7) the number of strategies of the space in each atom at the game (an atom
    with N = 0 can win neither), E (512,) the efficiency, D a dict with keys N, beta, muplain (for the receipt).
    The enrichment is S / N (times the constant size of the space, which does not move the argmax)."""
    share = np.where(N > 0, S, -np.inf)
    enr = np.where(N > 0, S / np.maximum(N, 1), -np.inf)
    wa, we = share.argmax(1), enr.argmax(1)
    print("%s (N = %d, beta = %d, mu = %s): efficiency %.3f .. %.3f, median %.3f, negative at %d games, below 0.9 at %d"
          % (name, D["N"], D["beta"], D["muplain"], E.min(), E.max(), np.median(E), (E < 0).sum(), (E < 0.9).sum()))
    print("   most abundant: " + ", ".join("%s %d" % (ORDER[i], (wa == i).sum()) for i in range(7) if (wa == i).any()))
    print("   most enriched: " + ", ".join("%s %d" % (ORDER[i], (we == i).sum()) for i in range(7) if (we == i).any()))
    return wa, we


# ------------------------------------------------------------------- layout (inches; the panel of Figures 3 and 4)
PW, LIM, EXTT = A.PW, A.LIM, A.EXTT
EXTB = 0.08                                                        # no swatch row under the disks here: the legends sit at the bottom
PH = PW * (2 * LIM + EXTT + EXTB) / (2 * LIM)
ML, MR, MT, MB = 0.95, 0.15, 0.15, 0.20
COLGAP, ROWGAP = 0.45, 0.15
LEG = 0.80                                                         # the legend strip at the bottom


def efficiency_bar(fig, FIG_W, FIG_H, x, yleg, label):
    """the efficiency colour bar (viridis 0-1, black below 0) under the column whose left edge is x inches, centred on
    the height yleg inches, 0.64 PW wide, with `label` above it (fig4.py / sifig8.py); returns the colorbar"""
    CBH = A.CBH
    cax = fig.add_axes([(x + 0.18 * PW) / FIG_W, (yleg - 0.5 * CBH) / FIG_H, 0.64 * PW / FIG_W, CBH / FIG_H])
    cb = fig.colorbar(ScalarMappable(norm=ENORM, cmap=ECMAP), cax=cax, orientation="horizontal", extend="min", extendfrac=0.05)
    cb.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]); cb.ax.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])
    cb.ax.minorticks_off(); cb.ax.tick_params(labelsize=A.FS * 0.82, length=5, width=1.0); cb.outline.set_linewidth(1.0)
    cax.text(0.5, 1.45, label, transform=cax.transAxes, ha="center", va="bottom", fontsize=A.FS * 0.95, color="0.12")
    return cb


def sheet_legend(fig, FIG_W, FIG_H, xc, yleg, title):
    """the seven atom swatches (WINCOL, ORDER) in one row centred at xc inches on the height yleg inches, with `title`
    above, on a full-sheet axes in inches (fig4.py / sifig8.py); returns that axes"""
    axL = fig.add_axes([0, 0, 1, 1]); axL.set_xlim(0, FIG_W); axL.set_ylim(0, FIG_H); axL.set_aspect("equal"); axL.axis("off")
    SW, LFS = A.CBH, A.LFS
    LW = A.LW * PW / (2 * LIM)                                     # the width of a bold code, inches
    PITCH = SW + 0.03 + LW + 0.06
    x0 = xc - 0.5 * (6 * PITCH + SW + 0.03 + LW)
    for i, code in enumerate(ORDER):
        xi = x0 + i * PITCH
        axL.add_patch(Rectangle((xi, yleg - 0.5 * SW), SW, SW, fc=WINCOL[code], ec="0.25", lw=0.6, zorder=12))
        axL.text(xi + SW + 0.03, yleg, code, fontsize=LFS, fontweight="bold", color="0.12", ha="left", va="center", zorder=12)
    axL.text(xc, yleg + 0.5 * SW + 0.12, title, ha="center", va="bottom", fontsize=A.FS * 0.95, color="0.12")
    return axL


def draw(rows, out, png_dpi=110):
    """the sheet: rows = [(label, E, wa, we)] top to bottom (E (512,) efficiency, wa / we (512,) ORDER indices from
    winners), three panels each, letters a, b, c, ... row by row, column heads on the first row only; writes out (a .pdf
    path) and the .png beside it at png_dpi"""
    NR = len(rows)
    FIG_W = ML + 3 * PW + 2 * COLGAP + MR
    FIG_H = MB + LEG + NR * PH + (NR - 1) * ROWGAP + MT
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    def cell(row, col):
        x = ML + col * (PW + COLGAP)
        y = MB + LEG + (NR - 1 - row) * (PH + ROWGAP)
        return fig.add_axes([x / FIG_W, y / FIG_H, PW / FIG_W, PH / FIG_H]), x, y

    pol, keep = cells_keep()
    LET = "abcdefghijklmnopqrstuvwxyz"[:3 * NR]
    letters = iter(LET)
    for r, (label, E, wa, we) in enumerate(rows):
        for c, title in enumerate(COLS):
            ax, x, y = cell(r, c)
            if c == 0:
                fc = [ECMAP(ENORM(E[i])) if E[i] >= 0 else ECMAP.get_under() for i in keep]
            else:
                win = wa if c == 1 else we
                fc = [WINCOL[ORDER[win[i]]] for i in keep]
            ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
            A.furniture(ax, next(letters), title if r == 0 else "")
            ax.set_ylim(-(LIM + EXTB), LIM + EXTT)                 # furniture set Figures 3-4's bottom extension; trim it
            if c == 0:
                fig.text((ML - 0.62) / FIG_W, (y + PH * (EXTB + LIM) / (2 * LIM + EXTT + EXTB)) / FIG_H, label, rotation=90,
                         ha="center", va="center", fontsize=A.FS * 1.25, color="0.12")

    # --------------------------------------------------------------- the legends: the efficiency bar under column 1, the atoms under columns 2-3
    YLEG = MB + 0.5 * LEG                                          # centre line of the legend strip
    efficiency_bar(fig, FIG_W, FIG_H, ML, YLEG, "efficiency (%s); black: below 0" % ", ".join(LET[0::3]))
    xc = ML + PW + COLGAP + 0.5 * (2 * PW + COLGAP)                # centre of columns 2-3
    sheet_legend(fig, FIG_W, FIG_H, xc, YLEG, "the atom (%s)" % ", ".join(l for i, l in enumerate(LET) if i % 3))

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

    fig.savefig(out); fig.savefig(out[:-4] + ".png" if out.endswith(".pdf") else out + ".png", dpi=png_dpi)
    plt.close(fig)
    print("wrote %s and .png (%.2f x %.2f in)" % (out, FIG_W, FIG_H))
