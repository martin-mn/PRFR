#!/usr/bin/env python3
"""
SI Figure 9: the large-population memory-two run of main text Figure 4 (N = 1000, beta = 100, mu = 1e-2) at three
error rates, eps = 1e-3, 1e-4, 1e-5.

    python3 SIFigure9/sifig9.py          ->  SIFigure9/SIFig9.pdf and SIFig9.png

The sheet has the layout and colours of main text Figure 4 (common.wfsheet.draw): one row per error rate, the middle
row being Figure 4's own run (f1_e4), the other two the runs eh_e3 and eh_e5; columns efficiency, most abundant atom,
most enriched atom.  The atom classification is the exact eps -> 0 one in every row: the question is whether the maps
drawn with those labels move when the error rate the process runs at changes.  Prints, for the text, the agreement of
the most abundant atom with the eps = 1e-4 row and the counts the legends quote (SI Table 7b).

Data: data/robustness/games_{f1_e4,eh_e3,eh_e5}.csv and m2_atom_sizes.csv (data/robustness/wfruns.py).  The code is
the original FinalFigures/sifig9.py (which drew SI Figures 9 and 10; SIFigure10/sifig10.py is its other half) with the
loading and the output path changed.
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

SHEETS = [("SIFig9", "f1_e4", "eh", 1000)]


def sheet(out, base, kit, npop):
    g0 = wfruns.load(base)
    S0, N0, E0, UV0, D0 = g0["S"], g0["N"], g0["E"], g0["UV"], g0["D"]
    rows, wins = [], {}
    for tag, eps in (("e3", "10^{-3}"), ("e4", "10^{-4}"), ("e5", "10^{-5}")):
        if tag == "e4":
            S, N, E, D, name = S0, N0, E0, dict(D0), base
        else:
            g = wfruns.load("%s_%s" % (kit, tag))
            assert np.array_equal(g["N"], N0) and np.allclose(g["UV"], UV0), "atom counts or games differ from Figure 4's"
            S, N, E, D, name = g["S"], g["N"], g["E"], g["D"], "%s_%s" % (kit, tag)
        assert D["eps"] == eps and D["N"] == npop, name
        wa, we = fig4.winners(S, N, E, D, name)
        wins[tag] = (wa, we, E, S)
        rows.append(("Memory-2, $N = %d$\n$\\epsilon = %s$" % (npop, eps), E, wa, we))
    wa4 = wins["e4"][0]
    for tag in ("e3", "e5"):
        wa, we, E, S = wins[tag]
        print("%s %s: most abundant atom agrees with eps = 1e-4 at %d of 512 games; friendly rivals win %d (1e-4: %d); "
              "efficiency below 0.9 at %d (1e-4: %d); mean efficiency %.3f (1e-4: %.3f)"
              % (kit, tag, (wa == wa4).sum(), (wa == 6).sum(), (wa4 == 6).sum(), (E < 0.9).sum(), (wins["e4"][2] < 0.9).sum(),
                 E.mean(), wins["e4"][2].mean()))
    fig4.draw(rows, out)


if __name__ == "__main__":
    for stem, base, kit, npop in SHEETS:
        sheet(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, stem + ".pdf"), base, kit, npop)
