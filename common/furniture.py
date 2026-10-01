"""
The frame of every disk panel on the sunflower cells (Figures 4 and 5, SI Figures 2-4 and 6-12) and of the count
maps (Figures 2 and 3): the axes, the special lines, the guide circles at |u|, |v| = 1, 2, 4, 10 with their ticks and
labels, u and v, the panel letter, the head, the names of the four games on the rim -- atomshares.py's furniture()
and layout constants, moved here unchanged.  furniture(ty=...) takes another type (font sizes and text positions);
without it every figure is drawn as published.  common.counts.page_type() is the type of Figures 2 and 3.

IMPORTING THIS MODULE selects the Agg backend and sets the rcParams the original atomshares.py / atomcounts.py set on
import (RC below: TrueType fonts in the PDF, font.size 15, axes.linewidth 1.2), so a script that draws with it
renders as the original did.  Import it before creating the figure.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe                                 # noqa: E402
import numpy as np                                                  # noqa: E402
from matplotlib.font_manager import FontProperties                  # noqa: E402
from matplotlib.patches import Rectangle                            # noqa: E402
from matplotlib.textpath import TextPath, TextToPath                # noqa: E402

from . import disk as _disk                                         # noqa: E402
from .atoms import ORDER                                            # noqa: E402
from .disk import NAMES, arc_text, draw_conics, phi                 # noqa: E402
from .style import WINCOL                                           # noqa: E402

RC = {"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 15, "axes.linewidth": 1.2}
matplotlib.rcParams.update(RC)

# ------------------------------------------------------------------- layout (inches; Figure 2's rules)
PW = 4.3                                         # the width of a disk panel
LIM = 1.175                                      # data limits of a panel: x in [-LIM, LIM]
EXTT, EXTB = 0.22, 0.34                          # extra room above / below the disk, data units (fig4.py trims EXTB to 0.08)
PH = PW * (2 * LIM + EXTT + EXTB) / (2 * LIM)    # the height of a panel, inches
COLGAP, ROWGAP = 0.55, 0.25
ML, MR, MB, MT = 0.30, 0.20, 0.25, 0.25
NCOL, NROW = 4, 2
FIG_W = ML + NCOL * PW + (NCOL - 1) * COLGAP + MR
FIG_H = MB + NROW * PH + (NROW - 1) * ROWGAP + MT
DPU = (2 * LIM / PW) / 72.0                      # data units per point
SC = PW / 13.46
NM_FS = _disk.NM_FS * SC * 1.25                  # the rim names' font size
FS = max(9.0, 13.0 * SC * 1.9) * 1.45            # the base font size of the sheets (head 1.05 FS, letter 1.7 FS, ...)

th = np.linspace(0, 2 * np.pi, 4001)
GUIDE = (1, 2, 4, 10)                            # guide circles at |(u, v)| = 1, 2, 4, 10
PEL = [pe.withStroke(linewidth=2.4, foreground="white")]
HALO = [pe.withStroke(linewidth=2.7, foreground="0.35")]    # dark rim on the white T = S dashes (sunflower maps)
GUIDE_C, GUIDE_LW, GUIDE_A = "white", 0.6, 0.28

# the swatch legend of the seven atoms under a disk (atomshares' panel h) and the horizontal colour bar beside it
CBH = 0.22                                       # the horizontal colour bar's height, inches
SW = CBH * 2 * LIM / PW                          # swatch side = the bar's height, in data units
LFS = FS * 0.82                                  # the codes at the size of the bar's tick labels
LW = TextPath((0, 0), "000", size=LFS, prop=FontProperties(family="DejaVu Sans", weight="bold")).get_extents().width * DPU
PITCH = SW + 0.02 + LW + 0.035                   # swatch, gap, code, gap to the next swatch (data units)
X0 = -0.5 * (6 * PITCH + SW + 0.02 + LW)         # the row of seven centred under the disk
YL = -LIM - 0.04 - 0.5 * SW - 0.01               # its centre line (data units); the colour bar sits level with it


# the type of furniture(): font sizes in points of the drawing, positions in data units.  TYPE is that of every figure
# as published; furniture(ty=d) replaces the entries named in d (common.counts.page_type()["furniture"], Figures 2, 3).
#   guide, guide_off      the labels of the guide circles, and their distance from the axis they label
#   guide_above           the labels of the u axis set above it rather than below (values of u, e.g. (-1, -4))
#   uv, v_x, v_ha         the axis names u and v; v is set at x = v_x with alignment v_ha
#   letter, head          the panel letter and the head
#   head_x                None: the head centred over the disk, letter and head on one bottom line (as published);
#                         a number: the head left-aligned at x = head_x on the letter's baseline head_y, one line per
#                         line of the title, head_lead apart, lines after the first indented to the text that follows
#                         the first three spaces of the first line (the code of the atom)
#   names, names_gap, names_gap_low, names_trk   the rim names: size, gap to the rim on the upper / lower half, tracking
TYPE = dict(guide=FS * 0.7, guide_off=0.048, guide_above=(), uv=FS * 1.4, v_x=0.0, v_ha="center", letter=FS * 1.7,
            head=FS * 1.05, head_x=None, head_y=LIM + 0.055, head_lead=0.0, names=NM_FS, names_gap=_disk.NM_GAP,
            names_gap_low=_disk.NM_GAP, names_trk=_disk.NM_TRK)


def furniture(ax, letter, title, halo=True, ty=None):
    """everything on a disk panel but the cells: axes, the special lines (common.disk.CONICS; halo=True as the
    sunflower maps, halo=False as the count maps of Figures 2 and 3), the guide circles with ticks and labels,
    u and v, the panel letter (top left), the head `title` (top centre; "" for none), the four game names on the rim;
    sets the limits x in [-LIM, LIM], y in [-(LIM + EXTB), LIM + EXTT], equal aspect, axis off.
    ty: None, the type as published, or a dict of the entries of TYPE to change.
    Draw the cells first (zorder 1); this draws at zorder 5-12."""
    assert ty is None or set(ty) <= set(TYPE), "not an entry of TYPE: %s" % sorted(set(ty) - set(TYPE))
    t = TYPE if ty is None else dict(TYPE, **ty)
    ax.plot([-1, 1], [0, 0], color=GUIDE_C, lw=GUIDE_LW, zorder=5, alpha=GUIDE_A)
    ax.plot([0, 0], [-1, 1], color=GUIDE_C, lw=GUIDE_LW, zorder=5, alpha=GUIDE_A)
    draw_conics(ax, halo=halo)
    for r in GUIDE:
        rr = float(np.hypot(*phi([[r, 0.0]])[0]))
        ax.plot(rr * np.cos(th), rr * np.sin(th), "-", color=GUIDE_C, lw=GUIDE_LW, zorder=5, alpha=GUIDE_A)
        for sg in (-1, 1):
            ax.plot([sg * rr, sg * rr], [-0.016, 0.016], color="0.2", lw=1.4, zorder=8, path_effects=PEL)
            ax.plot([-0.016, 0.016], [sg * rr, sg * rr], color="0.2", lw=1.4, zorder=8, path_effects=PEL)
            lab = ("%g" % r) if sg > 0 else "$-$%g" % r
            if sg * r in t["guide_above"]:
                ax.text(sg * rr, t["guide_off"], lab, fontsize=t["guide"], color="0.2", ha="center", va="bottom", zorder=9,
                        path_effects=PEL)
            else:
                ax.text(sg * rr, -t["guide_off"], lab, fontsize=t["guide"], color="0.2", ha="center", va="top", zorder=9,
                        path_effects=PEL)
            ax.text(-t["guide_off"], sg * rr, lab, fontsize=t["guide"], color="0.2", ha="right", va="center", zorder=9,
                    path_effects=PEL)
    ax.text(1.055, 0.0, "$u$", fontsize=t["uv"], ha="left", va="center")
    ax.text(t["v_x"], 1.055, "$v$", fontsize=t["uv"], ha=t["v_ha"], va="bottom")
    if t["head_x"] is None:                                    # as published
        ax.text(-LIM + 0.01, t["head_y"], letter, fontsize=t["letter"], fontweight="bold", ha="left", va="bottom")
        ax.text(0.0, t["head_y"], title, fontsize=t["head"], color="0.12", ha="center", va="bottom")
    else:                                                      # the letter, then the head left-aligned on its baseline
        ax.text(-LIM + 0.01, t["head_y"], letter, fontsize=t["letter"], fontweight="bold", ha="left", va="baseline")
        lines = title.split("\n")
        ind = 0.0
        if len(lines) > 1 and "   " in lines[0]:               # the hanging indent: the width of "code   " in data units
            ind = TextToPath().get_text_width_height_descent(lines[0].split("   ")[0] + "   ",
                                                             FontProperties(size=t["head"]), ismath=True)[0] * DPU
        for i, line in enumerate(lines):
            ax.text(t["head_x"] + (ind if i else 0.0), t["head_y"] - i * t["head_lead"], line, fontsize=t["head"],
                    color="0.12", ha="left", va="baseline")
    for a0, nm in NAMES:
        gap = t["names_gap"] if a0 < 180.0 else t["names_gap_low"]
        _, _, ro = arc_text(ax, nm, a0, 1.0, t["names"], DPU, gap, t["names_trk"])
        assert ro < LIM, "%s reaches r = %.4f" % (nm, ro)
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-(LIM + EXTB), LIM + EXTT)
    ax.set_aspect("equal")
    ax.axis("off")


def disk_legend(ax):
    """the swatch legend of the seven atoms (WINCOL, in ORDER) centred under the disk of ax, in its bottom margin,
    exactly as under panel h of atomshares.draw / draw_runs (SI Figures 2 and 3); returns the seven code Texts"""
    legend = []
    for i, code in enumerate(ORDER):
        xi = X0 + i * PITCH
        ax.add_patch(Rectangle((xi, YL - 0.5 * SW), SW, SW, fc=WINCOL[code], ec="0.25", lw=0.6, zorder=12, clip_on=False))
        legend.append(ax.text(xi + SW + 0.02, YL, code, fontsize=LFS, fontweight="bold", color="0.12", ha="left", va="center",
                              zorder=12))
    return legend


def disk_legend_check(ax, legend, renderer):
    """assert that no code of disk_legend runs into the next swatch (atomshares' check); call after fig.canvas.draw()"""
    for i_ in range(len(legend) - 1):
        nxt = ax.transData.transform((X0 + (i_ + 1) * PITCH, YL))[0]
        assert legend[i_].get_window_extent(renderer).x1 < nxt - 2, "legend entry %d runs into the next swatch" % i_
