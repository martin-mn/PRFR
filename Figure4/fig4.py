#!/usr/bin/env python3
"""
Figure 4: what evolution selects, for memory one and memory two, in a large population.

    python3 fig4.py             ->  Fig4.pdf / Fig4.png  (here)

Six disks, one per (run, quantity), the two Wright-Fisher runs at N = 1000, beta = 100, mu = 1e-2, eps = 1e-4:

    row 1   memory one, N = 1000    (data/runs/m1_N1000.csv)
    row 2   memory two, N = 1000    (data/runs/m2_N1000.csv)

    column 1   efficiency: the mean per-round payoff of the population over the second half of the run, divided
               by the joint optimum Emax = max(R, (S + T)/2) of the game (the realised efficiency of the Methods);
               viridis from 0 to 1, black where it is negative
    column 2   the most abundant atom: the atom whose strategies hold the largest share of the population
    column 3   the most enriched atom: the atom with the largest share divided by its share of the strategy space

The 512 games are the Voronoi cells of the Fermat sunflower (data/games); the sheet is common.wfsheet.draw (the
original fig4.py's draw(), moved to common/ because SI Figures 4, 8-10 and 12 share it).  Panel letters a-f row
by row.  This is the original FinalFigures/fig4.py with the data loading replaced: the runs are read from the
deposited tables through data/runs/wfdata.py, which returns the arrays the original loader returned, bit for bit.
SI Figure 4 (the same sheet for N = 100) is SIFigure4/sifig4.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))                          # common/
sys.path.insert(0, os.path.join(HERE, os.pardir, "data", "runs"))          # wfdata.py
import wfdata                                                      # noqa: E402  the four runs, read from data/runs
from common import wfsheet                                         # noqa: E402  the sheet (imports furniture: Agg, rcParams)

ROWS = [(wfdata.LABEL[k],) + k for k in wfdata.ROWS if k[1] == "F1"]      # Figure 4: the large population


def run(space, which):
    """per cell (in ipt order 0..511): efficiency, the most abundant atom, the most enriched atom (indices into ORDER)"""
    S, N, E, UV, D = wfdata.load(space, which)
    wa, we = wfsheet.winners(S, N, E, D, "%s %s" % (space, which))
    return E, wa, we, UV


if __name__ == "__main__":
    wfsheet.draw([(label,) + run(space, which)[:3] for label, space, which in ROWS], os.path.join(HERE, "Fig4.pdf"))
