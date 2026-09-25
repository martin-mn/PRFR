#!/usr/bin/env python3
"""
SI Figure 7: the EFFICIENT strict Nash equilibria at the error rate of the runs, eps = 1e-4, and the share of the
population on them. The 16 binary memory-one strategies are in row 1 (a-c) and the 65536 binary memory-two strategies
in row 2 (d-f). This is SI Figure 6 restricted to the strict equilibria that are efficient in the paper's limit sense:
mutual cooperators below the switch line, alternators above it. None of the alternators is strict, so every game
above the switch line is grey.

    python3 sifig7.py            ->  SIFig7.pdf  (here)
    python3 sifig7.py --png      ->  also SIFig7.png at 110 dpi

The drawing is figstrict.draw(), shared with SI Figure 6. The data are ../data/strict/m1_games.csv and m2_games.csv.
"""
import os
import sys

import figstrict

figstrict.draw(True, os.path.join(figstrict.HERE, "SIFig7.pdf"), png="--png" in sys.argv[1:])
