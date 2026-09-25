#!/usr/bin/env python3
"""
Figure 3: how many strategies have each property, at every game, for memory one and memory two.

    python3 fig3.py             ->  Fig3.pdf / Fig3.png  (here; reads ../data/arrangement/)

Two rows of four disks.  Row 1, the 16 binary memory-one strategies (the 45 faces of the exact arrangement of m1atoms.py,
../data/arrangement/m1_faces*); row 2, the 65536 binary memory-two strategies (the 22872 faces of the arrangement of
NEmap, drawn as 27598 polygons, ../data/arrangement/m2_faces*).  The columns are the
sets 1** efficient (atoms 100 + 110 + 111), *1* stable (010 + 110 + 011 + 111), **1 competitive (001 + 011 + 111) and 11*
efficient and stable, the partners (110 + 111); a panel shows the number of strategies in the set at each game, exactly, in the
limit eps -> 0, in Figure 2's style (atomcounts.py: one colour scale per panel, discrete bands where the set takes at most
twelve values, an equal-area ramp otherwise; grey where the set is empty, marked 0 on the bar; under each disk the number of
different strategies that belong to the set somewhere).  The efficient set takes one value on each side of the switch line
(memory two: 7639 mutual cooperators below, 3072 alternators above; memory one: 3 below, none above) and the competitive set
one value off the line T = S (memory two 2640, memory one 4), so those panels are two- or one-colour maps by construction.
Panel letters a-h row by row.

This is FinalFigures/fig3.py of the working tree with only the data loading changed (atomcounts.py is common/counts.py,
moved unchanged); the drawing is untouched.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, os.path.join(ROOT, "data", "arrangement"))
sys.path.insert(0, ROOT)
from common import counts as C                                     # noqa: E402  atomcounts.py: Figure 2's layout, scales, furniture
from common import geometry as el                                  # noqa: E402  polyarea (eulerlib.polyarea)
import arrangement                                                 # noqa: E402  the deposited arrangements

SETS = [("efficient", r"$\mathbf{1{*}{*}}$", [4, 6, 7]), ("stable", r"$\mathbf{{*}1{*}}$", [2, 3, 6, 7]),
        ("competitive", r"$\mathbf{{*}{*}1}$", [1, 3, 7]), ("efficient and stable: partners", r"$\mathbf{11{*}}$", [6, 7])]

# ------------------------------------------------------------------ memory one: 45 faces, 16 strategies
D1 = arrangement.m1()                                                           # m1atoms.load()
F1, DA1, A1, CODES1 = D1["faces"], np.asarray(D1["diskarea"], float), np.asarray(D1["atoms"], float), D1["codes"]
assert A1.shape == (len(F1), 8) and (A1.sum(1) == 16).all() and not A1[:, 5].any()
TOT1 = [int(np.isin(CODES1, atoms).any(0).sum()) for _, _, atoms in SETS]       # strategies in the set at some game

# ------------------------------------------------------------------ memory two: 27598 polygons, 65536 strategies
D2 = arrangement.m2()                          # the faces of ca4_arrangement_k4.npz and the ATOMS of Count6_faces.npz
assert arrangement.K == C.K
F2 = D2["faces"]
DA2 = np.array([el.polyarea(f) for f in F2])
A2 = D2["atoms"].astype(float)
assert A2.shape == (len(F2), 8) and (A2.sum(1) == 65536).all() and not A2[:, 5].any()
M = arrangement.m2_strategies()                # the masks of m2_masks.npz
effCC, effALT, rivP, rivM = (M[k] for k in ("eff_cc", "eff_alt", "riv_plus", "riv_minus"))
TOT2 = [int((effCC | effALT).sum()), int(D2["ne_total"]), int((rivP | rivM).sum()), 9431]
assert int((M["open_110"] | M["open_111"]).sum()) == TOT2[3]          # 9431 partners on an open set, from the data
# 10711 efficient (7639 + 3072), 23861 stable and 9431 partners on an open set (NEmap, SI section 8), 5230 rivals (2640 + 2640 - 50 fair)
assert TOT2[:3] == [10711, 23861, 5230], TOT2
assert (A2[:, [4, 6, 7]].sum(1) == np.where(A2[:, [4, 6, 7]].sum(1) > 5000, 7639, 3072)).all() and (A2[:, [1, 3, 7]].sum(1) == 2640).all()

# ------------------------------------------------------------------ the sheet: Figure 2's grid with a label column on the left
fig, W, H, xy = C.sheet(2, 4, labw=0.75)
letters = iter("abcdefgh")
for row, (label, FACES, DA, ATOMS, TOT) in enumerate((("Memory-1, 16 strategies", F1, DA1, A1, TOT1),
                                                       ("Memory-2, 65536 strategies", F2, DA2, A2, TOT2))):
    for col, (name, code, atoms) in enumerate(SETS):
        x, y = xy(row, col)
        st = C.panel(fig, W, H, x, y, FACES, DA, ATOMS[:, atoms].sum(1), next(letters), "%s   %s" % (code, name),
                     "%d different strategies over the disk" % TOT[col])
        print("%-27s %-30s %5d strategies somewhere; %5d-%5d per game where present; %4d levels; empty on %5.1f%% of the disk"
              % (label, name, TOT[col], st["min"], st["max"], st["levels"], 100 * st["zshare"]))
    C.rowlabel(fig, W, H, *xy(row, 0), label)
C.finish(fig, W, H, os.path.join(HERE, "Fig3.pdf"))
