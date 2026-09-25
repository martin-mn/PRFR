#!/usr/bin/env python3
"""sitable2.py -- SI Table 2, the four quarter-planes, recomputed from the census (data/census/census.csv).

    python3 sitable2.py          prints the table next to the paper's, writes SITable2.csv; exit status 1 on a mismatch

For each open quarter-plane (wedge) cut by the switch line u+v = 1 and the line u-v = 1 (T = S) the script derives, at
a test game far along the direction in which the wedge opens, the side of each line, the direction, what efficiency
means there (Emax = max(1, (1+u+v)/2): R, mutual cooperation, or (T+S)/2, alternation) and which reading of rivalry
applies (the sign of T - S = 1 + v - u), and counts the friendly rivals among the 65536 binary memory-two strategies:
efficient (mutual cooperator below the switch line, alternator above) and rival in the limit (riv_p for T>S, riv_m for
T<S) or defensible (def_p, def_m).  It also checks the counts of the paragraph "The two lines" that precedes the table.
Games are (R, S, T, P) = (1, u, 1 + v, 0).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "census"))
import censuslib as cl                            # noqa: E402
from common.tables import write_table            # noqa: E402

# SI Table 2 as printed in ms.tex
PAPER = [
    ("W", "<1", "<1", "u->-inf", "mutual cooperation", "T>S", 8, 8),
    ("S", "<1", ">1", "v->-inf", "mutual cooperation", "T<S", 1519, 1036),
    ("E", ">1", ">1", "u->+inf", "alternation", "T<S", 80, 80),
    ("N", ">1", "<1", "v->+inf", "alternation", "T>S", 80, 80),
]
DIRS = {"u->-inf": (-1.0, 0.0), "v->-inf": (0.0, -1.0), "u->+inf": (1.0, 0.0), "v->+inf": (0.0, 1.0)}


def side(x):
    return "<1" if x < 1 else ">1"


def wedge_of(u, v):
    for w, (_, _, a, b) in cl.WEDGE.items():
        if side(u + v) == a and side(u - v) == b:
            return w


M = cl.masks(cl.load())
ok = True
rows = []
for w, (eff, riv, spv, smv) in cl.WEDGE.items():
    # the direction at infinity inside the wedge: the ray t*d lies in it for every large t, for exactly one axis dir.
    opens = [n for n, (du, dv) in DIRS.items() if all(wedge_of(t * du, t * dv) == w for t in (10.0, 1e3, 1e6))]
    assert len(opens) == 1, (w, opens)
    du, dv = DIRS[opens[0]]
    u, v = 10.0 * du, 10.0 * dv                                  # a test game in the wedge
    assert wedge_of(u, v) == w
    R, S, T, P = 1.0, u, 1.0 + v, 0.0
    emax = max(R, (S + T) / 2)
    means = "mutual cooperation" if emax == R and (S + T) / 2 < R else "alternation"
    # the efficient set on this side of the switch line is the one the wedge uses
    assert (eff == "eff_cc") == (means == "mutual cooperation")
    rivalry = "T>S" if T > S else "T<S"
    assert (riv == "riv_p") == (rivalry == "T>S")
    lim = int((M[eff] & M[riv]).sum())
    dfn = int((M[eff] & M[cl.DEFREAD[riv]]).sum())
    rows.append((w, spv, smv, opens[0], means, rivalry, lim, dfn))

print("SI Table 2: the four quarter-planes (computed | paper)")
print("%-5s %-4s %-4s %-9s %-19s %-7s %6s %11s" % ("wedge", "u+v", "u-v", "opens", "efficient means", "rivalry",
                                                    "limit", "defensible"))
for r, p in zip(rows, PAPER):
    same = r == p
    ok &= same
    print("%-5s %-4s %-4s %-9s %-19s %-7s %6d %11d   %s" % (r + ("agrees" if same else "DIFFERS from %s" % (p,),)))

print("\nThe two lines (the paragraph before the table)")
line, cc, alt, rp, rm = M["eff_line"], M["eff_cc"], M["eff_alt"], M["riv_p"], M["riv_m"]
checks = [
    ("efficient on the switch line (w_DD = 0)", int(line.sum()), 14757),
    ("friendly rivals on the switch line, part with T>S", int((line & rp).sum()), 116),
    ("friendly rivals on the switch line, part with T<S", int((line & rm).sum()), 2067),
    ("friendly rivals on T=S (every strategy a rival): efficient below the switch line", int(cc.sum()), 7639),
    ("friendly rivals on T=S: efficient above the switch line", int(alt.sum()), 3072),
]
for lab, got, paper in checks:
    ok &= got == paper
    print("  %-82s %6d %6d %s" % (lab, got, paper, "" if got == paper else "  <-- DIFFERS"))

write_table(os.path.join(HERE, "SITable2.csv"), {
    "wedge": [r[0] for r in rows], "u_plus_v": [r[1] for r in rows], "u_minus_v": [r[2] for r in rows],
    "opens_towards": [r[3] for r in rows], "efficient_means": [r[4] for r in rows], "rivalry": [r[5] for r in rows],
    "friendly_rivals_limit": [r[6] for r in rows], "friendly_rivals_defensible": [r[7] for r in rows]}, [
    "SI Table 2, the four open quarter-planes, recomputed by SITable2/sitable2.py from data/census/census.csv.",
    "u_plus_v, u_minus_v: the side of the switch line u+v=1 and of the line u-v=1 (T=S); opens_towards: the direction",
    "at infinity inside the wedge; efficient_means: what attains Emax there; rivalry: the sign of T-S there;",
    "friendly_rivals_limit / _defensible: the efficient strategies that are rivals in the limit eps->0 / defensible."])
print("\nwrote SITable2.csv")
print("ALL AGREE" if ok else "DISAGREEMENT FOUND")
sys.exit(0 if ok else 1)
