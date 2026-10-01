#!/usr/bin/env python3
"""
Figure 2: how many strategies fall in each of the seven atoms of the three properties --
efficient, stable, competitive -- at each game, in the limit eps -> 0, for memory one and for memory two.

    python3 fig2.py            ->  Fig2.pdf / Fig2.png  (here; reads ../data/arrangement/)
    python3 fig2.py --wide     ->  Fig2_wide.pdf / Fig2_wide.png: the sheet of release 1.0.0, 26.47 x 22.55 in

Four rows of four cells.  Rows 1-2: the 2^4 = 16 binary memory-one strategies (the 45 faces of the exact arrangement of
m1atoms.py, ../data/arrangement/m1_faces*); rows 3-4: the 2^16 = 65536 binary memory-two strategies (the 22872 faces of
the arrangement of NEmap, drawn as 27598 polygons, with their atom counts, ../data/arrangement/m2_faces*).  Within each pair of rows the panels are the atoms in the order 000, 100, 010, 001 / 110, 011,
111, and the eighth cell is empty: 101, efficient and competitive but not stable, has no member at any game (the theorem).
Drawing: atomcounts.py (one colour scale per panel, bands for at most twelve values, an equal-area ramp otherwise, grey where
the atom is empty; under each disk the number of different strategies that belong to the atom somewhere).  Panel letters a-g
(memory one) and h-n (memory two).

This is FinalFigures/fig2.py of the working tree with its data loading changed (atomcounts.py is common/counts.py)
and, on 2026-09-30, the page type added.  With --wide the drawing is that of release 1.0.0.  By default the sheet is
set for the page: the same disks, lines, scales and data, taller colour bars, with the type and its room of
common.counts.page_type(), so that printed 6.89 in wide (17.5 cm) its type is 6 pt or larger, apart from the guide
labels (5.5 pt) and the rim names (5.0 pt); the long heads are set on two lines (HEAD2) and the line under each disk
on two.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, os.path.join(ROOT, "data", "arrangement"))
sys.path.insert(0, ROOT)
from common import counts as C                                     # noqa: E402  atomcounts.py
from common import geometry as el                                  # noqa: E402  polyarea (eulerlib.polyarea)
import arrangement                                                 # noqa: E402  the deposited arrangements

WIDE = "--wide" in sys.argv[1:]
TY = None if WIDE else C.page_type()                               # the type: as in release 1.0.0, or for the page
T = C.WIDE if WIDE else TY
HEAD_DX = {"111": 0.03}   # data units: the head of the 111 panels, two letters longer since "Nash" became "stable",
                           # would come within 0.08 in of its panel letter if centred; 0.03 (0.055 in) to the right
                           # gives back the 0.13 in it had (--wide only; for the page the heads are left-aligned)
HEAD2 = {"110": "efficient and\nstable only", "011": "stable and\ncompetitive only",   # for the page: the heads that
         "111": "efficient, stable\nand competitive"}                                  # are set on two lines

# ------------------------------------------------------------------ memory one
D1 = arrangement.m1()                                              # m1atoms.load()
F1, DA1, A1, CODES1 = D1["faces"], np.asarray(D1["diskarea"], float), np.asarray(D1["atoms"], float), D1["codes"]
assert A1.shape == (len(F1), 8) and (A1.sum(1) == 16).all() and not A1[:, 5].any()
T1 = np.array([len({i for f in range(len(F1)) for i in range(16) if CODES1[f, i] == c}) for c in range(8)])
assert T1[5] == 0

# ------------------------------------------------------------------ memory two
D2 = arrangement.m2()                          # the faces of ca4_arrangement_k4.npz, ATOMS and ATOM_TOTAL of Count6_faces.npz
assert arrangement.K == C.K
F2 = D2["faces"]
DA2 = np.array([el.polyarea(f) for f in F2])
A2, T2 = D2["atoms"].astype(float), D2["atom_total"].astype(int)
assert A2.shape == (len(F2), 8) and (A2.sum(1) == 65536).all() and not A2[:, 5].any() and T2[5] == 0

# ------------------------------------------------------------------ the sheet
fig, W, H, xy = C.sheet(4, 4, labw=0.75, ty=TY)
letters = iter("abcdefghijklmn")
for block, (label, FACES, DA, ATOMS, TOT) in enumerate((("Memory-1, 16 strategies", F1, DA1, A1, T1),
                                                         ("Memory-2, 65536 strategies", F2, DA2, A2, T2))):
    print(label)
    for i, code in enumerate(C.ATOM_ORDER):
        row, col = divmod(i, 4)
        x, y = xy(2 * block + row, col)
        c = int(code, 2)
        head = r"$\mathbf{%s}$   %s" % (code, C.ATOM_NAME[code] if WIDE else HEAD2.get(code, C.ATOM_NAME[code]))
        st = C.panel(fig, W, H, x, y, FACES, DA, ATOMS[:, c], next(letters), head,
                     "%d different strategies%sover the disk" % (TOT[c], " " if WIDE else "\n"), ty=TY)
        if WIDE and code in HEAD_DX:                               # the longest head, clear of the panel letter
            (t_,) = [t_ for t_ in fig.axes[-2].texts if t_.get_text() == head]      # the disk just drawn
            t_.set_x(HEAD_DX[code])
        print("   atom %s: %d strategies somewhere; %d-%d per game where present; %d levels; empty on %.1f%% of the disk"
              % (code, TOT[c], st["min"], st["max"], st["levels"], 100 * st["zshare"]))
    x0, y0 = xy(2 * block, 0); x1, y1 = xy(2 * block + 1, 0)        # the label, centred between the block's two disks
    yc = 0.5 * (y0 + y1) + C.PH * (C.LIM + C.EXTB) / (2 * C.LIM + C.EXTT + C.EXTB)
    fig.text((x0 - T["row_dx"]) / W, yc / H, label, rotation=90, ha="center", va="center", fontsize=T["row"], color="0.12")
C.finish(fig, W, H, os.path.join(HERE, "Fig2_wide.pdf" if WIDE else "Fig2.pdf"))
