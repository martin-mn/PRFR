"""
The count maps: how many strategies are in an atom (or a union of atoms) at each game, one colour scale per panel --
atomcounts.py's machinery (Figures 2 and 3), whose scale atom_scale() SI Figures 6 and 7 use as well; moved here
unchanged, with the page type (page_type(), WIDE and the ty arguments) added on 2026-09-30.

A panel's scale is chosen from the values the field takes where it is positive: one band if it takes one value,
discrete magma bands (by rank) if it takes at most twelve, otherwise an equal-area magma ramp (the colormap spread over
the field's own area-weighted distribution, NB = 256 bands).  Zero is the under-colour GREY, marked 0 on the bar.

    sheet(nrow, ncol, labw, ty)   -> (fig, W, H, xy)       a sheet of count panels (Figure 2's cell size)
    panel(fig, W, H, x, y, FACES, DA, vals, letter, head, sub, barlabel, ty)  one disk with its vertical colour bar
    rowlabel(fig, W, H, x, y, text, ty)                    a rotated row label left of a disk
    finish(fig, W, H, out)                                 text checks, then out (.pdf) and its .png at 150 dpi
    atom_scale(vals, weights, mingap) -> (cmap, norm, ticks, labels, discrete)
    page_type(width)  -> ty                                the type of Figures 2 and 3 for a page `width` inches wide

ty is the type of the sheet: None (WIDE) draws it as in release 1.0.0, 26.47 in wide for four columns, type 9.1 to
22 pt; page_type() keeps the sizes of the disks, the lines and the bar widths (in inches and points), makes the bars
as tall as the disk (0.85 PW) with a longer grey triangle, and sets the type, and the room it takes, so that the sheet
printed `width` inches wide shows each text at a stated size in points.

Importing this module imports common.furniture, which selects Agg and sets the figures' rcParams.
"""
import os

import numpy as np

from . import furniture as _F                                       # Agg + rcParams, as atomcounts.py set them
import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.cm import ScalarMappable                            # noqa: E402
from matplotlib.collections import PolyCollection                   # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap          # noqa: E402
from matplotlib.patches import PathPatch                            # noqa: E402

from .atoms import NAME, ORDER                                      # noqa: E402
from .style import GREY                                             # noqa: E402

K = 4.0


def grp(x):
    return "%d" % round(x)


# --------------------------------------------------------------- colour bars
NB = 256


def ladder(lo, hi):
    """candidate ticks 1, 2, 5 x 10^d strictly inside (1.25 lo, hi / 1.25), with lo and hi at the ends"""
    t, d = [], int(np.floor(np.log10(lo)))
    while 10.0 ** d <= hi * 10:
        for m in (1, 2, 5):
            x = m * 10.0 ** d
            if lo * 1.25 < x < hi / 1.25:
                t.append(x)
        d += 1
    return [lo] + t + [hi]


def thin(ticks, norm, nbands, mingap=0.052):
    """keep the two end ticks and, from the top, every tick at least mingap (fraction of the bar) from those kept"""
    pos = [(float(norm(t)) / float(nbands), t) for t in ticks]
    keep = [pos[0], pos[-1]]
    for q, t in sorted(pos[1:-1], key=lambda z: -z[0]):
        if all(abs(q - k[0]) >= mingap for k in keep):
            keep.append((q, t))
    return [t for _, t in sorted(keep)]


def equalised(vals, weights, cmap="magma", name="", mingap=0.052):
    """the equal-area scale: the colormap spread over the field's own area-weighted distribution;
    returns (ListedColormap, BoundaryNorm, ticks); mingap as in thin()"""
    v = np.asarray(vals, dtype=float); w = np.asarray(weights, dtype=float)
    o = np.argsort(v, kind="stable")
    cum = np.cumsum(w[o]); cum /= cum[-1]
    bnd = np.interp(np.linspace(0.0, 1.0, NB + 1), cum, v[o])
    bnd[0], bnd[-1] = v.min(), v.max()
    bnd = np.unique(bnd); nb = len(bnd) - 1
    norm = BoundaryNorm(bnd, nb)
    cm = ListedColormap(plt.get_cmap(cmap)(np.linspace(0.0, 1.0, nb)))
    ticks = thin(ladder(float(v.min()), float(v.max())), norm, nb, mingap)
    print("bar %s: %d equal-area bands over %g to %g" % (name, nb, v.min(), v.max()))
    return cm, norm, ticks


def discrete_bands(vals, weights, cmap="magma", vmin=None, vmax=None, minshare=0.010, group=str, by="value", share=True):
    """one colour band per distinct level of a piecewise-constant field (PartnersRivals/Figures/disklib.py, verbatim).

    Band boundaries sit at the geometric midpoints of consecutive levels, the outer two placed symmetrically.  by="value"
    colours by the log of the level, by="rank" spreads the colormap uniformly over the bands.  Ticks: the levels that
    cover the most area, at least MINSEP bands apart, plus the two extremes.
    Returns (ListedColormap, BoundaryNorm, ticks, ticklabels, receipt)."""
    assert by in ("value", "rank"), "by must be value or rank"
    from matplotlib.colors import LogNorm
    vals = np.asarray(vals)
    lv, inv = np.unique(vals, return_inverse=True)
    ash = np.zeros(len(lv))
    np.add.at(ash, inv, np.asarray(weights, dtype=float))
    ash /= ash.sum()
    g = np.sqrt(lv[:-1] * lv[1:])
    bnd = np.concatenate(([lv[0] ** 2 / g[0]], g, [lv[-1] ** 2 / g[-1]]))
    lo = float(vals.min()) if vmin is None else vmin
    hi = float(vals.max()) if vmax is None else vmax
    if by == "rank":
        t = np.linspace(0.0, 1.0, len(lv)) if len(lv) > 1 else np.zeros(1)
        cols = plt.get_cmap(cmap)(t)
    else:
        cols = plt.get_cmap(cmap)(LogNorm(lo, hi)(lv))
    minsep = max(2, int(round(len(lv) / 38.0)))
    keep, lost = [0, len(lv) - 1], []
    for i in np.argsort(ash)[::-1]:
        if ash[i] < minshare:
            break
        if all(abs(i - j) >= minsep for j in keep):
            keep.append(int(i))
        elif int(i) not in keep:
            lost.append(int(i))
    keep = sorted(keep)
    receipt = ("discrete bar: %d bands, %d labelled (>= %.1f%% of the disk, at least %d bands apart); labelled levels cover "
               "%.1f%% of it%s" % (len(lv), len(keep), 100 * minshare, minsep, 100 * sum(ash[i] for i in keep),
                                   "" if not lost else ".  Largest unlabelled: %s"
                                   % ", ".join("%g (%.1f%%)" % (lv[i], 100 * ash[i]) for i in lost[:3])))
    return (ListedColormap(cols), BoundaryNorm(bnd, len(lv)), [lv[i] for i in keep],
            [("%s  (%.1f%%)" % (group(lv[i]), 100 * ash[i])) if share else group(lv[i]) for i in keep], receipt)


def atom_scale(vals, weights, mingap=0.052):
    """the scale of one count panel: ramp or bands over the positive values of vals ((n,) array), weighted by the areas
    `weights` ((n,)); zero is the under-colour GREY.  Returns (cmap, norm, ticks, ticklabels, discrete) where
    discrete is True for bands (the labels are then every level).  mingap: the least distance of two ticks of a ramp,
    as a fraction of the bar (thin())."""
    pos = vals > 0
    lv = np.unique(vals[pos])
    if len(lv) == 1:                                                  # one band (memory one: 111 is always 2)
        cm = ListedColormap([plt.get_cmap("magma")(0.75)])
        norm = BoundaryNorm([lv[0] - 0.5, lv[0] + 0.5], 1)
        ticks, lab, disc = [float(lv[0])], [grp(lv[0])], True
    elif len(lv) <= 12:
        cm, norm, ticks, lab, rec = discrete_bands(vals[pos], weights[pos], cmap="magma", vmin=lv.min(), vmax=lv.max(),
                                                   group=grp, by="rank", share=False)
        ticks, lab, disc = [float(x) for x in lv], [grp(x) for x in lv], True
        cm = ListedColormap(cm.colors)
    else:
        cm, norm, ticks = equalised(vals[pos], weights[pos], name="atom", mingap=mingap)
        lab, disc = [grp(t) for t in ticks], False
    cm.set_under(GREY)
    return cm, norm, ticks, lab, disc


# ------------------------------------------------------------------- layout (inches)
PW, LIM, EXTT, EXTB, PH = _F.PW, _F.LIM, _F.EXTT, _F.EXTB, _F.PH
CBW, CBGAP, CBLAB = 0.22, 0.26, 1.30             # the vertical colour bar: width, gap to the disk, room for its labels
COLW = PW + CBGAP + CBW + CBLAB                  # one column: disk + bar
COLGAP, ROWGAP = 0.30, 0.25
ML, MR, MB, MT = 0.30, 0.20, 0.25, 0.25
NCOL, NROW = 4, 2
FIG_W = ML + NCOL * COLW + (NCOL - 1) * COLGAP + MR
FIG_H = MB + NROW * PH + (NROW - 1) * ROWGAP + MT
DPU, SC, NM_FS, FS = _F.DPU, _F.SC, _F.NM_FS, _F.FS
CBH = 0.80 * PW                                  # the vertical colour bar's height (NOT furniture.CBH)
ATOM_ORDER, ATOM_NAME = ORDER, NAME

# the type of the sheets as in release 1.0.0 (ty=None): font sizes in points of the drawing, positions in data units
# (sub_y, the top of the line under a disk) or inches (the room: cblab, colgap, rowgap, margins; row_dx, the centre of
# a row label left of the disk), CBH the bar's height (inches), extendfrac the length of the grey triangle under the
# bar and zero_y the height of its label "0" (fractions of the bar), mingap that of atom_scale, furniture that of
# furniture()
WIDE = dict(sub=FS * 0.82, sub_y=-LIM - 0.06, tick_disc=FS * 0.72, tick_ramp=FS * 0.82, zero=FS * 0.72, barlab=FS * 0.95,
            row=FS * 1.25, row_dx=0.45, cbh=CBH, extendfrac=0.06, zero_y=-0.045, mingap=0.052, cblab=CBLAB,
            colgap=COLGAP, rowgap=ROWGAP, ml=ML, mr=MR, mb=MB, mt=MT, labw=0.75, furniture=None)

# ------------------------------------------------------------------- the type for the page
PAGE_W = 6.89                                    # inches: the full text width, 17.5 cm
# printed sizes (points at PAGE_W) of page_type(); the rim names are as large as the room between the rim and the edge
# of the panel allows (furniture's assert r < LIM); the guide labels as large as the room between the rim names and
# the other labels of the axes allows
PAGE_PT = dict(letter=8.5, head=7.0, sub=6.0, tick=6.0, zero=6.0, barlab=6.5, row=7.5, uv=7.0, guide=5.5, names=5.0)
# the room, printed inches at PAGE_W: bar labels (tick, pad, the widest label, bold 65486 at 6 pt, labelpad, the bar
# label), the gap between columns, the margins, the label column and the offset of the row labels
PAGE_IN = dict(cblab=0.47, colgap=0.03, ml=0.02, labw=0.14, mr=0.02, rowgap=0.255, mt=0.205, mb=0.12, row_dx=0.08)


def page_type(width=PAGE_W, ncol=NCOL):
    """the type of a sheet of ncol columns (Figures 2 and 3) to be printed `width` inches wide.  The disks, lines and
    bar widths keep their sizes in inches and points; the bars are 0.85 PW tall and their triangle 0.14; otherwise only
    the type and the room it takes change.
    The sheet is W = A + B/s inches wide, A the ncol disks and bars (ncol (PW + CBGAP + CBW)), B the printed room of
    PAGE_IN; printed at `width` it is scaled by s = (width - B) / A, and every text is set at PAGE_PT / s.
    Returns the ty of sheet(), panel() and rowlabel(), with its scale as ty["s"]."""
    A = ncol * (PW + CBGAP + CBW)
    B = ncol * PAGE_IN["cblab"] + (ncol - 1) * PAGE_IN["colgap"] + PAGE_IN["ml"] + PAGE_IN["labw"] + PAGE_IN["mr"]
    s = (width - B) / A
    pt = {k: v / s for k, v in PAGE_PT.items()}                     # points of the drawing
    room = {k: v / s for k, v in PAGE_IN.items()}                   # inches of the drawing
    dpu = DPU / s                                                   # data units per printed point
    cbh, ext = 0.85 * PW, 0.14                                      # the bar as tall as the disk; its triangle
    fur = dict(guide=pt["guide"], guide_off=0.035, guide_above=(-1, -4), uv=pt["uv"], v_x=0.03, v_ha="left",
               letter=pt["letter"], head=pt["head"], head_x=-LIM + 0.01 + 12.0 * dpu, head_y=1.60,  # 12 pt after the
                                                                                                # start of the letter
               head_lead=1.2 * PAGE_PT["head"] * dpu, names=pt["names"], names_gap=0.05, names_gap_low=0.022,
               names_trk=0.02)
    return dict(sub=pt["sub"], sub_y=-1.2, tick_disc=pt["tick"], tick_ramp=pt["tick"], zero=pt["zero"],
                barlab=pt["barlab"], row=pt["row"], row_dx=room["row_dx"], cbh=cbh, extendfrac=ext, zero_y=-0.11,
                mingap=1.2 * PAGE_PT["tick"] * (1 + ext) / (cbh * s * 72.0), cblab=room["cblab"], colgap=room["colgap"],
                rowgap=room["rowgap"], ml=room["ml"], mr=room["mr"], mb=room["mb"], mt=room["mt"], labw=room["labw"],
                furniture=fur, s=s, width=width)


def cellxy(row, col):
    return (ML + col * (COLW + COLGAP), MB + (NROW - 1 - row) * (PH + ROWGAP))


def sheet(nrow, ncol=NCOL, labw=0.0, ty=None):
    """a sheet of nrow x ncol cells of Figure 2's size, with a column of width labw (inches) on the left for row
    labels; returns (fig, W, H, xy) with xy(row, col) the lower-left corner of a disk in inches.  ty: the type (None
    as in release 1.0.0, WIDE; or page_type(), whose room and label column replace those given here)"""
    if ty is None:
        colw, colgap, rowgap, ml, mr, mb, mt = COLW, COLGAP, ROWGAP, ML, MR, MB, MT
    else:
        colw, colgap, rowgap = PW + CBGAP + CBW + ty["cblab"], ty["colgap"], ty["rowgap"]
        ml, mr, mb, mt, labw = ty["ml"], ty["mr"], ty["mb"], ty["mt"], ty["labw"]
    W = ml + labw + ncol * colw + (ncol - 1) * colgap + mr
    H = mb + nrow * PH + (nrow - 1) * rowgap + mt
    fig = plt.figure(figsize=(W, H))

    def xy(row, col):
        return (ml + labw + col * (colw + colgap), mb + (nrow - 1 - row) * (PH + rowgap))
    return fig, W, H, xy


def panel(fig, W, H, x, y, FACES, DA, vals, letter, head, sub, barlabel="Number of strategies", ty=None):
    """one disk of Figure 2 at (x, y) inches on a sheet of W x H inches: the faces FACES (list of disk polygons)
    coloured by vals ((nfaces,)) with the scale of atom_scale weighted by the face areas DA (grey where zero), the
    furniture (no halo on T = S), the head and the sub-line, and the vertical colour bar to its right.
    ty: the type (None as in release 1.0.0, WIDE; or page_type()).
    Returns dict(min, max, levels, zshare) of the positive values and the zero share of the area."""
    t = WIDE if ty is None else ty
    vals = np.asarray(vals, float)
    ax = fig.add_axes([x / W, y / H, PW / W, PH / H])
    zero = vals == 0
    cm, norm, ticks, lab, disc = atom_scale(vals, DA, t["mingap"])
    c = cm(norm(vals))
    ax.add_collection(PolyCollection(FACES, facecolors=c, edgecolors=c, linewidths=0.30, antialiased=True, zorder=1))
    _F.furniture(ax, letter, head, halo=False, ty=t["furniture"])
    ax.text(0.0, t["sub_y"], sub, fontsize=t["sub"], color="0.12", ha="center", va="top", zorder=12, linespacing=1.35)
    # the colour bar
    xb = x + PW + CBGAP
    yc = y + PH * (LIM + EXTB) / (2 * LIM + EXTT + EXTB)
    cbh = t["cbh"]
    cax = fig.add_axes([xb / W, (yc - 0.5 * cbh) / H, CBW / W, cbh / H])
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cm), cax=cax, ticks=ticks, spacing="uniform", drawedges=disc,
                      extend="min" if zero.any() else "neither", extendfrac=t["extendfrac"])
    cb.ax.set_yticklabels(lab)
    cb.ax.minorticks_off()
    for lb in (cb.ax.get_yticklabels()[0], cb.ax.get_yticklabels()[-1]):
        lb.set_fontweight("bold")
    cb.set_label(barlabel, fontsize=t["barlab"], labelpad=10)
    cb.ax.tick_params(labelsize=t["tick_disc"] if disc else t["tick_ramp"], length=5, width=1.0)
    if disc:
        cb.outline.set_linewidth(1.0)
        cb.dividers.set_color("white")
        cb.dividers.set_linewidth(0.6)
    if zero.any():
        cb.ax.text(1.45, t["zero_y"], "0", transform=cb.ax.transAxes, fontsize=t["zero"], ha="left", va="center", color="0.25")
    return dict(min=vals[~zero].min() if (~zero).any() else np.nan, max=vals.max(), levels=len(np.unique(vals[~zero])),
                zshare=DA[zero].sum() / DA.sum())


def rowlabel(fig, W, H, x, y, text, ty=None):
    """a rotated label centred on the disk whose lower-left corner is at (x, y) inches, printed 0.45 in to its left
    (ty: the type, None as in release 1.0.0; page_type() sets the size and the offset)"""
    t = WIDE if ty is None else ty
    fig.text((x - t["row_dx"]) / W, (y + PH * (LIM + EXTB) / (2 * LIM + EXTT + EXTB)) / H, text, rotation=90,
             ha="center", va="center", fontsize=t["row"], color="0.12")


def finish(fig, W, H, out):
    """check that no text leaves the sheet and no two heads overlap, then write out (.pdf) and its .png (150 dpi).
    The checks of the published sheets, and two that the page type needs, where the type fills the room: no text
    of one axes overlaps a text of another (the panels, their bars, the row labels), and no letter, head line, sub-line
    or label of the u axis overlaps a rim name (the extents of the texts and of the glyphs, in pixels)."""
    fig.canvas.draw()
    R = fig.canvas.get_renderer()
    for t_ in fig.texts:
        bb = t_.get_window_extent(R)
        assert 0 < bb.x0 and bb.x1 < W * fig.dpi and 0 < bb.y0 and bb.y1 < H * fig.dpi, "text runs off the sheet: %r" % t_.get_text()
    groups = [[t_] for t_ in fig.texts]                            # the texts of each axes, and each figure text
    for ax_ in fig.axes:
        for t_ in list(ax_.texts) + (ax_.get_yticklabels() if ax_.axison else []):
            if t_.get_text() and t_.get_visible():
                bb = t_.get_window_extent(R)
                assert 0 < bb.x0 and bb.x1 < W * fig.dpi and 0 < bb.y0 and bb.y1 < H * fig.dpi, \
                    "text runs off the sheet: %r" % t_.get_text()
        heads = [t_ for t_ in ax_.texts if t_.get_text() and t_.get_va() in ("bottom", "baseline")
                 and t_.get_ha() in ("center", "left")]
        for i_ in range(len(heads)):
            for j_ in range(i_ + 1, len(heads)):
                a_, b_ = heads[i_].get_window_extent(R), heads[j_].get_window_extent(R)
                assert not (a_.overlaps(b_)), "texts overlap: %r / %r" % (heads[i_].get_text(), heads[j_].get_text())
        mine = [t_ for t_ in list(ax_.texts) + (ax_.get_yticklabels() + [ax_.yaxis.label] if ax_.axison else [])
                if t_.get_text() and t_.get_visible()]
        groups.append(mine)
        glyphs = [p_.get_window_extent(R) for p_ in ax_.patches if isinstance(p_, PathPatch) and not ax_.axison]  # rim names
        for t_ in mine:     # all but the labels of the v axis (va "center"; their boxes, taller than their digits,
            if t_.get_va() != "center" or t_.get_text() == "$u$":     # reach the boxes of the rim glyphs near 100 deg)
                bb = t_.get_window_extent(R)
                assert not any(bb.overlaps(g_) for g_ in glyphs), "text overlaps a rim name: %r" % t_.get_text()
    boxes = [[t_.get_window_extent(R) for t_ in g_] for g_ in groups]
    for i_ in range(len(groups)):
        for j_ in range(i_ + 1, len(groups)):
            for a_, ta_ in zip(boxes[i_], groups[i_]):
                for b_, tb_ in zip(boxes[j_], groups[j_]):
                    assert not a_.overlaps(b_), "texts of two axes overlap: %r / %r" % (ta_.get_text(), tb_.get_text())
    fig.savefig(out)
    fig.savefig(out.replace(".pdf", ".png"), dpi=150)
    plt.close(fig)
    print("%s: %.2f x %.2f in, pdf %.1f MB" % (os.path.basename(out), W, H, os.path.getsize(out) / 1e6))
