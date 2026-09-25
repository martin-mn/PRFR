#!/usr/bin/env python3
"""
Shared drawing machinery of Figure 1 (FinalFigures/eulerlib.py of the working tree; only the import of the disk map
changed, to common.disk): exact Euler diagrams of the three properties --
efficient (blue circle), competitive (red circle), stable (dashed black curve) -- and the map of the disk
coloured by pattern.

A panel is specified by the two circles (or None for an empty set), the set of stable strategies as a membership
function with the extra boundary curves to sample (or None for an empty set), and the anchors of the
codes.  euler() fills each present atom as a filled contour of its indicator on a fine grid, draws the
outlines on top, and checks that the drawing realises exactly the atoms of the pattern and that every
printed code sits in its own region.  Colours, tints, line widths and font sizes live here so that the
two figures cannot drift apart.
"""
import os
import sys

import numpy as np
import matplotlib.patheffects as pe
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))
from common import disk as disklib                                 # noqa: E402  phi, NAMES, arc_text (disklib.py, moved unchanged)

ORDER = ["000", "100", "010", "001", "110", "011", "111"]
CODE = np.array(["000", "001", "010", "011", "100", "101", "110", "111"])
COL_E, COL_C, COL_N = "#1f4e9c", "#b3232b", "0.10"
TINT = {"000": "white", "100": "#d2dff5", "001": "#f8d7d3", "010": "#e6e6e6", "110": "#b9c8ea", "011": "#ebbcbc", "111": "#cbbbe6"}
PAL = {"a": "#8dd3c7", "b": "#ffffb3", "c": "#bebada", "d": "#fb8072", "e": "#80b1d3", "f": "#fdb462", "g": "#b3de69",
       "h": "#fccde5", "i": "#d9d9d9", "j": "#bc80bd", "k": "#ccebc5", "l": "#ffed6f"}
DASH = (0, (3.2, 2.2))


def polyarea(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def circle(cx, cy, r):
    """(membership, boundary sampler) of a disk"""
    def inside(x, y):
        return (x - cx) ** 2 + (y - cy) ** 2 < r ** 2

    def boundary(t):
        return cx + r * np.cos(t), cy + r * np.sin(t), np.cos(t), np.sin(t)      # point and outward unit normal
    return inside, boundary


def ellipse(cx, a, b=None, yt=None):
    """axis-parallel ellipse centred on the x-axis; b = None makes it pass through the points (0, +-yt)"""
    if b is None:
        b = yt / np.sqrt(1.0 - cx ** 2 / a ** 2)

    def inside(x, y):
        return ((x - cx) / a) ** 2 + (y / b) ** 2 < 1.0

    def boundary(t):
        nx, ny = np.cos(t) / a, np.sin(t) / b
        nn = np.hypot(nx, ny)
        return cx + a * np.cos(t), b * np.sin(t), nx / nn, ny / nn
    return inside, boundary


def nothing(x, y):
    """the membership function of the empty set"""
    return np.zeros(np.shape(x), bool)


def atom_of(in_e, in_c, in_n, x, y):
    e, c, n = in_e(x, y), in_c(x, y), in_n(x, y)
    return CODE[e.astype(int) * 4 + n.astype(int) * 2 + c.astype(int)]


def euler(ax, key, E, C, N, anchors, XL, YL, big=False, letter=None, sub=None, names=(), ybot=None, suby=None):
    """one exact Euler diagram of the pattern `key` (seven bits, the atoms of ORDER present or not).

    E, C: (cx, cy, r) of the efficient and the competitive circle, or None when the set is empty;
    N: (membership, extra boundary curves) of the set of stable strategies, or None when it is empty;
    anchors: {code: (x, y)} where the codes are printed (000 only in a big panel);
    names: [(text, x, y, colour, ha, va)] printed at the size of the set names."""
    pres = {c for c, x in zip(ORDER, key) if x == "1"}
    in_e, e_bd = circle(*E) if E is not None else (nothing, None)
    in_c, c_bd = circle(*C) if C is not None else (nothing, None)
    in_n, curves = N if N is not None else (nothing, [])
    # --- fills: each present atom as a filled contour of its indicator on a fine grid
    gx, gy = np.meshgrid(np.linspace(-XL, XL, 1400), np.linspace(-YL, YL, 900))
    at = atom_of(in_e, in_c, in_n, gx, gy)
    got = set(np.unique(at))
    assert got == pres, (key, sorted(got), sorted(pres))           # the drawing realises exactly the pattern's atoms
    for c in ORDER:
        if c in pres and c != "000":
            ax.contourf(gx, gy, (at == c).astype(float), levels=[0.5, 1.5], colors=[TINT[c]], zorder=1)
    # --- outlines: efficient and competitive solid; stable dashed on top, sampled where membership flips
    lw = 1.4 if big else 1.15
    if E is not None:
        ax.add_patch(Circle(E[:2], E[2], fc="none", ec=COL_E, lw=lw, zorder=20))
    if C is not None:
        ax.add_patch(Circle(C[:2], C[2], fc="none", ec=COL_C, lw=lw, zorder=20))
    t = np.linspace(0, 2 * np.pi, 4000, endpoint=False)
    for bd in [b for b in (e_bd, c_bd) if b is not None] + list(curves):
        px, py, nx, ny = bd(t)
        d = 0.004
        flip = in_n(px + d * nx, py + d * ny) != in_n(px - d * nx, py - d * ny)
        if not flip.any():
            continue
        if flip.all():
            ax.plot(np.append(px, px[0]), np.append(py, py[0]), color=COL_N, lw=lw, ls=DASH, zorder=21)
            continue
        starts = np.where(flip & ~np.roll(flip, 1))[0]
        for s in starts:
            idx = [s]
            while flip[(idx[-1] + 1) % len(t)]:
                idx.append((idx[-1] + 1) % len(t))
            idx = np.array(idx)
            ax.plot(px[idx], py[idx], color=COL_N, lw=lw, ls=DASH, zorder=21, solid_capstyle="butt")
    # --- the codes
    fs = 9.0 if big else 7.2
    for c, (x, y) in anchors.items():
        assert c in pres, (key, c)
        assert atom_of(in_e, in_c, in_n, np.array([x]), np.array([y]))[0] == c, \
            (key, c, atom_of(in_e, in_c, in_n, np.array([x]), np.array([y]))[0])
        if c == "000" and not big:
            continue
        ax.text(x, y, c, ha="center", va="center", fontsize=fs, color="0.05", zorder=30, family="monospace",
                fontweight="bold" if c == "111" else "normal")
    assert set(anchors) == pres - ({"000"} if "000" not in anchors else set()), key
    # --- names, letter, caption
    for text, x, y, col, ha, va in names:
        ax.text(x, y, text, ha=ha, va=va, fontsize=8.4, color=col, zorder=30)
    if letter:
        ax.text(-XL + 0.05, YL - 0.05, letter, ha="left", va="top", fontsize=10.5, fontweight="bold", zorder=30)
    if sub:
        if suby is None:
            suby = -YL + 0.02 if big else -YL - 0.05
        ax.text(0.0, suby, sub, ha="center", va="top", fontsize=6.8 if big else 6.6, color="0.25", zorder=30, linespacing=1.3)
    if ybot is None:
        ybot = -YL if big else -YL - 1.25
    ax.set_xlim(-XL, XL); ax.set_ylim(ybot, YL); ax.set_aspect("equal"); ax.axis("off")


def piece_letters(patterns, KEY, PIECE, DA, CEN, LET, minshare=0.005):
    """where to print each pattern's letter on the map: in every piece (quadrant x wedge) where the pattern
    covers at least `minshare` of the disk, and in its largest piece otherwise"""
    TOT = DA.sum()
    out = []
    for k in patterns:
        pcs = np.unique(PIECE[KEY == k])
        largest = max(pcs, key=lambda pc: DA[(KEY == k) & (PIECE == pc)].sum())
        for pc in pcs:
            m = (KEY == k) & (PIECE == pc)
            if DA[m].sum() / TOT < minshare and pc != largest:
                continue
            cx, cy = (CEN[m] * DA[m][:, None]).sum(0) / DA[m].sum()
            out.append((cx, cy, LET[k]))
    return out


def draw_map(axk, faces, cols, letters, letter, LIM, dpu, K, lfs=8.0):
    """the disk coloured by pattern: faces (disk polygons) with their colours, the rim, the axes, the
    switch line (crimson) and T = S (dashed), the rim names, the pattern letters (font size lfs) and the panel letter"""
    axk.add_collection(PolyCollection(faces, facecolors=cols, edgecolors=cols, linewidths=0.3, antialiased=True, zorder=1))
    th = np.linspace(0, 2 * np.pi, 720)
    axk.plot(np.cos(th), np.sin(th), color="0.15", lw=1.0, zorder=10)
    axk.plot([-1, 1], [0, 0], color="0.35", lw=0.5, zorder=5, alpha=0.7); axk.plot([0, 0], [-1, 1], color="0.35", lw=0.5, zorder=5, alpha=0.7)
    tt = np.linspace(-2000, 2000, 40001)
    sw = disklib.phi(np.column_stack([tt, 1 - tt]), K); ts = disklib.phi(np.column_stack([tt, tt - 1]), K)
    axk.plot(sw[:, 0], sw[:, 1], color="crimson", lw=1.1, zorder=8)
    axk.plot(ts[:, 0], ts[:, 1], color="0.10", lw=0.9, ls=(0, (3, 2)), zorder=8)
    for a0, nm in disklib.NAMES:
        disklib.arc_text(axk, nm, a0, 1.0, 7.6, dpu, 0.02, 0.06, color="0.25")
    for cx, cy, L in letters:
        axk.text(cx, cy, L, ha="center", va="center", fontsize=lfs, fontweight="bold", color="0.05", zorder=30,
                 path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    axk.text(-LIM, LIM + 0.02, letter, ha="left", va="top", fontsize=10.5, fontweight="bold", zorder=30)
    axk.text(1.03, 0.0, "$u$", fontsize=8, ha="left", va="center"); axk.text(0.0, 1.03, "$v$", fontsize=8, ha="center", va="bottom")
    axk.set_xlim(-LIM, LIM); axk.set_ylim(-LIM, LIM); axk.set_aspect("equal"); axk.axis("off")
