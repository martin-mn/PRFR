#!/usr/bin/env python3
"""
SI Figure 4: main text Figure 4 for the small population.

    python3 sifig4.py           ->  SIFig4.pdf / SIFig4.png  (here)

Six disks, one per (run, quantity), the two Wright-Fisher runs at N = 100, beta = 3, mu = 1e-4, eps = 1e-4:

    row 1   memory one, N = 100     (data/runs/m1_N100.csv)
    row 2   memory two, N = 100     (data/runs/m2_N100.csv)

    column 1   efficiency: the mean per-round payoff of the population over the second half of the run, divided
               by the joint optimum Emax = max(R, (S + T)/2) of the game (the realised efficiency of the Methods);
               viridis from 0 to 1, black where it is negative
    column 2   the most abundant atom: the atom whose strategies hold the largest share of the population
    column 3   the most enriched atom: the atom with the largest share divided by its share of the strategy space

The 512 games are the Voronoi cells of the Fermat sunflower (data/games); the sheet is common.wfsheet.draw (the
original fig4.py's draw(), moved to common/ because SI Figures 4, 8-10 and 12 share it).  Panel letters a-f row
by row.  This is the original FinalFigures/fig4.py with the data loading replaced: the runs are read from the
deposited tables through data/runs/wfdata.py, which returns the arrays the original loader returned, bit for bit.
The original fig4.py drew Figure 4 and this figure in one run; main text Figure 4 (N = 1000) is Figure4/fig4.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))                          # common/
sys.path.insert(0, os.path.join(HERE, os.pardir, "data", "runs"))          # wfdata.py
import wfdata                                                      # noqa: E402  the four runs, read from data/runs
from common import wfsheet                                         # noqa: E402  the sheet (imports furniture: Agg, rcParams)

SIROWS = [(wfdata.LABEL[k],) + k for k in wfdata.ROWS if k[1] == "F2"]    # SI Figure 4: the small population


def run(space, which):
    """per cell (in ipt order 0..511): efficiency, the most abundant atom, the most enriched atom (indices into ORDER)"""
    S, N, E, UV, D = wfdata.load(space, which)
    wa, we = wfsheet.winners(S, N, E, D, "%s %s" % (space, which))
    return E, wa, we, UV


if __name__ == "__main__":
    wfsheet.draw([(label,) + run(space, which)[:3] for label, space, which in SIROWS], os.path.join(HERE, "SIFig4.pdf"))
