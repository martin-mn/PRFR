#!/usr/bin/env python3
"""
SI Figure 6: the strict Nash equilibria at the error rate of the runs, eps = 1e-4, and the share of the population on
them. The 16 binary memory-one strategies are in row 1 (a-c) and the 65536 binary memory-two strategies in row 2 (d-f).
Column 1 is the number of strict equilibria at each of the 512 games, columns 2 and 3 the share of the population on
them at N = 100 and at N = 1000.

    python3 sifig6.py            ->  SIFig6.pdf  (here)
    python3 sifig6.py --png      ->  also SIFig6.png at 110 dpi

The drawing is figstrict.draw(), shared with SI Figure 7 (the efficient strict equilibria). The data are
../data/strict/m1_games.csv and m2_games.csv.
"""
import os
import sys

import figstrict

figstrict.draw(False, os.path.join(figstrict.HERE, "SIFig6.pdf"), png="--png" in sys.argv[1:])
