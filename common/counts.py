"""
The count maps: how many strategies are in an atom (or a union of atoms) at each game, one colour scale per panel --
atomcounts.py's machinery (Figures 2 and 3), whose scale atom_scale() SI Figures 6 and 7 use as well; moved here
unchanged.

A panel's scale is chosen from the values the field takes where it is positive: one band if it takes one value,
discrete magma bands (by rank) if it takes at most twelve, otherwise an equal-area magma ramp (the colormap spread over
the field's own area-weighted distribution, NB = 256 bands).  Zero is the under-colour GREY, marked 0 on the bar.

    sheet(nrow, ncol, labw)   -> (fig, W, H, xy)           a sheet of count panels (Figure 2's cell size)
    panel(fig, W, H, x, y, FACES, DA, vals, letter, head, sub, barlabel)  one disk with its vertical colour bar
    rowlabel(fig, W, H, x, y, text)                        a rotated row label left of a disk
    finish(fig, W, H, out)                                 text checks, then out (.pdf) and its .png at 150 dpi
    atom_scale(vals, weights) -> (cmap, norm, ticks, labels, discrete)

Importing this module imports common.furniture, which selects Agg and sets the figures' rcParams.
"""
import os

import numpy as np

from . import furniture as _F                                       # Agg + rcParams, as atomcounts.py set them
import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.cm import ScalarMappable                            # noqa: E402
from matplotlib.collections import PolyCollection                   # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap          # noqa: E402

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


def equalised(vals, weights, cmap="magma", name=""):
    """the equal-area scale: the colormap spread over the field's own area-weighted distribution;
    returns (ListedColormap, BoundaryNorm, ticks)"""
    v = np.asarray(vals, dtype=float); w = np.asarray(weights, dtype=float)
    o = np.argsort(v, kind="stable")
    cum = np.cumsum(w[o]); cum /= cum[-1]
    bnd = np.interp(np.linspace(0.0, 1.0, NB + 1), cum, v[o])
    bnd[0], bnd[-1] = v.min(), v.max()
    bnd = np.unique(bnd); nb = len(bnd) - 1
    norm = BoundaryNorm(bnd, nb)
    cm = ListedColormap(plt.get_cmap(cmap)(np.linspace(0.0, 1.0, nb)))
    ticks = thin(ladder(float(v.min()), float(v.max())), norm, nb)
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


def atom_scale(vals, weights):
    """the scale of one count panel: ramp or bands over the positive values of vals ((n,) array), weighted by the areas
    `weights` ((n,)); zero is the under-colour GREY.  Returns (cmap, norm, ticks, ticklabels, discrete) where
    discrete is True for bands (the labels are then every level)."""
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
        cm, norm, ticks = equalised(vals[pos], weights[pos], name="atom")
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


def cellxy(row, col):
    return (ML + col * (COLW + COLGAP), MB + (NROW - 1 - row) * (PH + ROWGAP))


def sheet(nrow, ncol=NCOL, labw=0.0):
    """a sheet of nrow x ncol cells of Figure 2's size, with a column of width labw (inches) on the left for row
    labels; returns (fig, W, H, xy) with xy(row, col) the lower-left corner of a disk in inches"""
    W = ML + labw + ncol * COLW + (ncol - 1) * COLGAP + MR
    H = MB + nrow * PH + (nrow - 1) * ROWGAP + MT
    fig = plt.figure(figsize=(W, H))

    def xy(row, col):
        return (ML + labw + col * (COLW + COLGAP), MB + (nrow - 1 - row) * (PH + ROWGAP))
    return fig, W, H, xy


def panel(fig, W, H, x, y, FACES, DA, vals, letter, head, sub, barlabel="Number of strategies"):
    """one disk of Figure 2 at (x, y) inches on a sheet of W x H inches: the faces FACES (list of disk polygons)
    coloured by vals ((nfaces,)) with the scale of atom_scale weighted by the face areas DA (grey where zero), the
    furniture (no halo on T = S), the head and the sub-line, and the vertical colour bar to its right.
    Returns dict(min, max, levels, zshare) of the positive values and the zero share of the area."""
    vals = np.asarray(vals, float)
    ax = fig.add_axes([x / W, y / H, PW / W, PH / H])
    zero = vals == 0
    cm, norm, ticks, lab, disc = atom_scale(vals, DA)
    c = cm(norm(vals))
    ax.add_collection(PolyCollection(FACES, facecolors=c, edgecolors=c, linewidths=0.30, antialiased=True, zorder=1))
    _F.furniture(ax, letter, head, halo=False)
    ax.text(0.0, -LIM - 0.06, sub, fontsize=FS * 0.82, color="0.12", ha="center", va="top", zorder=12, linespacing=1.35)
    # the colour bar
    xb = x + PW + CBGAP
    yc = y + PH * (LIM + EXTB) / (2 * LIM + EXTT + EXTB)
    cax = fig.add_axes([xb / W, (yc - 0.5 * CBH) / H, CBW / W, CBH / H])
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cm), cax=cax, ticks=ticks, spacing="uniform", drawedges=disc,
                      extend="min" if zero.any() else "neither", extendfrac=0.06)
    cb.ax.set_yticklabels(lab)
    cb.ax.minorticks_off()
    for lb in (cb.ax.get_yticklabels()[0], cb.ax.get_yticklabels()[-1]):
        lb.set_fontweight("bold")
    cb.set_label(barlabel, fontsize=FS * 0.95, labelpad=10)
    cb.ax.tick_params(labelsize=FS * (0.72 if disc else 0.82), length=5, width=1.0)
    if disc:
        cb.outline.set_linewidth(1.0)
        cb.dividers.set_color("white")
        cb.dividers.set_linewidth(0.6)
    if zero.any():
        cb.ax.text(1.45, -0.045, "0", transform=cb.ax.transAxes, fontsize=FS * 0.72, ha="left", va="center", color="0.25")
    return dict(min=vals[~zero].min() if (~zero).any() else np.nan, max=vals.max(), levels=len(np.unique(vals[~zero])),
                zshare=DA[zero].sum() / DA.sum())


def rowlabel(fig, W, H, x, y, text):
    """a rotated label centred on the disk whose lower-left corner is at (x, y) inches, printed 0.45 in to its left"""
    fig.text((x - 0.45) / W, (y + PH * (LIM + EXTB) / (2 * LIM + EXTT + EXTB)) / H, text, rotation=90,
             ha="center", va="center", fontsize=FS * 1.25, color="0.12")


def finish(fig, W, H, out):
    """check that no text leaves the sheet and no two heads overlap, then write out (.pdf) and its .png (150 dpi)"""
    fig.canvas.draw()
    R = fig.canvas.get_renderer()
    for t_ in fig.texts:
        bb = t_.get_window_extent(R)
        assert 0 < bb.x0 and bb.x1 < W * fig.dpi and 0 < bb.y0 and bb.y1 < H * fig.dpi, "text runs off the sheet: %r" % t_.get_text()
    for ax_ in fig.axes:
        for t_ in list(ax_.texts) + (ax_.get_yticklabels() if ax_.axison else []):
            if t_.get_text() and t_.get_visible():
                bb = t_.get_window_extent(R)
                assert 0 < bb.x0 and bb.x1 < W * fig.dpi and 0 < bb.y0 and bb.y1 < H * fig.dpi, \
                    "text runs off the sheet: %r" % t_.get_text()
        heads = [t_ for t_ in ax_.texts if t_.get_text() and t_.get_va() == "bottom" and t_.get_ha() in ("center", "left")]
        for i_ in range(len(heads)):
            for j_ in range(i_ + 1, len(heads)):
                a_, b_ = heads[i_].get_window_extent(R), heads[j_].get_window_extent(R)
                assert not (a_.overlaps(b_)), "texts overlap: %r / %r" % (heads[i_].get_text(), heads[j_].get_text())
    fig.savefig(out)
    fig.savefig(out.replace(".pdf", ".png"), dpi=150)
    plt.close(fig)
    print("%s: %.2f x %.2f in, pdf %.1f MB" % (os.path.basename(out), W, H, os.path.getsize(out) / 1e6))
