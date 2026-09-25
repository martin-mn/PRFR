#!/usr/bin/env python3
"""
SI Figure 12: the large-population memory-two run of main text Figure 4 under four mutation kernels.

    python3 SIFigure12/sifig12.py        ->  SIFigure12/SIFig12.pdf and SIFig12.png

With probability mu an individual mutates; the mutant is global with probability nu (drawn uniformly from all 65536
strategies, its own included) and local with probability 1 - nu (one of the 16 positions of its own strategy flipped).
N = 1000, beta = 100, mu = 1e-2, eps = 1e-4, 10 replicates per game.  Rows nu = 0, 0.1, 0.5 are the runs lm_g0_e4,
lm_g01_e4, lm_g05_e4; the row nu = 1 is Figure 4's own run (f1_e4).  Layout and colours of main text Figure 4
(common.wfsheet.draw): columns efficiency, most abundant atom, most enriched atom; the atoms are the exact eps -> 0
classification in every row.  Prints, for the text, the agreement with the nu = 1 row and the counts (SI Table 7c).

Data: data/robustness/games_<run>.csv and m2_atom_sizes.csv (data/robustness/wfruns.py).  The code is the original
FinalFigures/sifiglm.py with the loading and the output path changed.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
from common import wfsheet as fig4                                  # noqa: E402  Agg + rcParams; the sheet of Figure 4
import wfruns                                                       # noqa: E402

KERNELS = [("lm_g0_e4", "0"), ("lm_g01_e4", "0.1"), ("lm_g05_e4", "0.5")]


def main(out):
    g1 = wfruns.load("f1_e4")
    S1, N1, E1, UV1, D1 = g1["S"], g1["N"], g1["E"], g1["UV"], g1["D"]
    rows, res = [], {}
    for run, nu in KERNELS:
        g = wfruns.load(run)
        assert g["D"]["nu"] == float(nu), run
        assert np.array_equal(g["N"], N1) and np.allclose(g["UV"], UV1), "atom counts or games differ from Figure 4's"
        wa, we = fig4.winners(g["S"], g["N"], g["E"], g["D"], "%s (nu = %s)" % (run, nu))
        res[nu] = (wa, we, g["E"])
        rows.append(("Memory-2, $N = 1000$\n$\\nu = %s$" % nu, g["E"], wa, we))
    wa1, we1 = fig4.winners(S1, N1, E1, D1, "Figure 4d-f (nu = 1)")
    rows.append(("Memory-2, $N = 1000$\n$\\nu = 1$ (Figure 4)", E1, wa1, we1))
    for nu, (wa, we, E) in res.items():
        print("nu = %s: most abundant atom as at nu = 1 at %d of 512 games; friendly rivals most abundant at %d (nu = 1: %d), "
              "most enriched at %d (nu = 1: %d); efficiency below 0.9 at %d (nu = 1: %d); mean %.3f (nu = 1: %.3f)"
              % (nu, (wa == wa1).sum(), (wa == 6).sum(), (wa1 == 6).sum(), (we == 6).sum(), (we1 == 6).sum(),
                 (E < 0.9).sum(), (E1 < 0.9).sum(), E.mean(), E1.mean()))
    fig4.draw(rows, out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "SIFig12.pdf"))
