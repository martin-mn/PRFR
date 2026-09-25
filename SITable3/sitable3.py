#!/usr/bin/env python3
"""sitable3.py -- SI Table 3, the counts at one game, recomputed from the census (data/census/census.csv).

    python3 sitable3.py          prints the table next to the paper's, writes SITable3.csv; exit status 1 on a mismatch

The game is the donation game with b = 1, c = 2/3, the point (u,v) = (-2,2), (R,S,T,P) = (1,-2,3,0), in the limit
eps -> 0.  It lies below the switch line (u+v = 0 < 1), so the efficient strategies are the mutual cooperators
(eff_cc), and has T > S (u-v = -4 < 1), so the competitive strategies are the rivals for T>S (riv_p).  The stability
decision (nash) and the tie clause (tie_ok) are those of the census program's nash pass at (-2,2), against all 65536
memory-two co-players, in exact rational arithmetic.  The same counts from the double-precision run
(census_double.csv) are printed alongside.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "census"))
import censuslib as cl                            # noqa: E402
from common.tables import write_table            # noqa: E402

U, V = -2.0, 2.0
assert U + V < 1 and U - V < 1                    # below the switch line, T > S: the wedge W

# SI Table 3 as printed in ms.tex
PAPER = [
    ("competitive", 2640),
    ("efficient", 7639),
    ("stable", 672),
    ("efficient and stable (partner)", 187),
    ("efficient and competitive (friendly rival)", 8),
    ("efficient, stable and competitive", 8),
    ("stable and competitive, efficiency dropped", 493),
    ("partners satisfying the tie clause", 8),
]


def counts(M):
    e, c, n, t = M["eff_cc"], M["riv_p"], M["nash"], M["tie_ok"]
    sets = [c, e, n, e & n, e & c, e & n & c, n & c, e & n & t]
    return [int(s.sum()) for s in sets], sets


Mq = cl.masks(cl.load("census.csv"))
Md = cl.masks(cl.load("census_double.csv"))
cq, sq = counts(Mq)
cd, sd = counts(Md)
ok = True
print("SI Table 3: the counts at (u,v) = (-2,2)          exact   double    paper")
for (lab, paper), a, b, s1, s2 in zip(PAPER, cq, cd, sq, sd):
    same = a == paper and b == paper and bool((s1 == s2).all())
    ok &= same
    print("  %-44s %7d %8d %8d   %s" % (lab, a, b, paper, "agrees" if same else "DIFFERS"))

ids = np.arange(cl.NC)
e, c, n, t = Mq["eff_cc"], Mq["riv_p"], Mq["nash"], Mq["tie_ok"]
extra = [
    ("adding stability to 'efficient and rival' changes nothing (the theorem)", bool(((e & c) <= n).all()), True),
    ("dropping efficiency lets in 485 more strategies", int((n & c & ~e).sum()), 485),
    ("ALLD among them", bool((n & c & ~e)[cl.NAMED["ALLD"]]), True),
    ("the 8 tie-clause partners are the friendly rivals of W", sorted(ids[e & n & t].tolist()), cl.EIGHT),
    ("the 187 partners are the mutual cooperators that are stable here", int((e & n).sum()), 187),
]
print("\nThe text around the table (SI section 6, 'Nash equilibria and partners')")
for lab, got, paper in extra:
    ok &= got == paper
    print("  %-66s %s %s" % (lab, "agrees" if got == paper else "DIFFERS: %s vs %s" % (got, paper), ""))

KEY = ["competitive", "efficient", "Nash", "partner", "friendly_rival", "efficient_Nash_competitive",
       "Nash_competitive", "partner_tie_clause"]
write_table(os.path.join(HERE, "SITable3.csv"), {
    "row": KEY, "strategies": cq, "strategies_double": cd}, [
    "SI Table 3, the counts at the donation game (u,v) = (-2,2), b = 1, c = 2/3, in the limit eps -> 0, recomputed",
    "by SITable3/sitable3.py from data/census/census.csv (exact run; strategies) and census_double.csv",
    "(double-precision run; strategies_double).  The rows, in the order of the paper's table:"] +
    ["  %-27s %s" % (k, p[0]) for k, p in zip(KEY, PAPER)])
print("\nwrote SITable3.csv")
print("ALL AGREE" if ok else "DISAGREEMENT FOUND")
sys.exit(0 if ok else 1)
