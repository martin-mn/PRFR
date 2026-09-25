#!/usr/bin/env python3
"""check.py -- the census counts of SI section 6 (and the numbers of the Methods), recomputed from data/census/.

    python3 check.py            (about 2 s; numpy only)

1. The exact run against the double-precision run, strategy by strategy and pass by pass, with the decisions of
   compare.py: the self-play support and the weights to 1e-12, the first outperforming co-player for T>S and for T<S,
   and at (u,v) = (-2,2) the stability decision, the number of tying co-players, the tie-clause verdict and the self-play
   payoff to 1e-12.  (compare.py does the same on the raw outputs of the two programs.)  Also, in both tables, the
   0/1 decision columns against the program outputs they are read from.
2. m2_masks.npz against census.csv.
3. Every count of the census that the four passes and defensibility decide, from the exact table, next to the number
   printed in the paper.  The paper's numbers are written out below with the words of ms.tex they stand for.
4. The receipts of the passes (data/census/passes.csv): chains per rivalry pass, the smallest nonzero |w_DC - w_CD|
   met, the largest integer met by the exact program.
5. The stability test at (u,v) = (-2,2) against the exact arrangement of the companion work (data/arrangement),
   strategy by strategy: every strategy's exact stability region there (its polygon, segment, ray or single game,
   closed, ties admitted) is evaluated at (-2,2) in integer and rational arithmetic, and the stable strategies it
   gives are compared
   with the column nash of census.csv.  Also the efficiency and rivalry columns of data/arrangement/m2_strategies.csv
   against census.csv.

Exit status 0 if everything agrees, 1 otherwise.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import censuslib as cl                    # noqa: E402
from common.tables import read_table      # noqa: E402

ok = True


def report(label, got, paper):
    global ok
    same = got == paper
    ok &= bool(same)
    print("  %-66s %12s %12s%s" % (label, got, paper, "" if same else "   <-- DIFFERS"))


q, d = cl.load("census.csv"), cl.load("census_double.csv")

print("1. exact (pairsq) against double precision (pairs), strategy by strategy")
W = ["w_CC", "w_CD", "w_DC", "w_DD"]
wq, wd = np.stack([q[k] for k in W], 1), np.stack([d[k] for k in W], 1)
diff_self = ((wq > 0) != (wd > 0)).any(1) | (np.abs(wq - wd).max(1) > 1e-12)
diff_p = q["beat_p"] != d["beat_p"]
diff_m = q["beat_m"] != d["beat_m"]
diff_n = ((q["ne_tieviol"] != d["ne_tieviol"]) | (q["ne_ntie"] != d["ne_ntie"]) | (q["ne_beat"] != d["ne_beat"])
          | (np.abs(q["ne_self"] - d["ne_self"]) > 1e-12))
for name, dd in (("self   (support and weights)", diff_self), ("rivP   (first beater, T>S)", diff_p),
                 ("rivM   (first beater, T<S)", diff_m), ("nash   (stability, ties, tie clause at (-2,2))", diff_n)):
    report("decisions differing, %s" % name, int(dd.sum()), 0)
print("  largest |exact - double| of a self-play weight: %.3g, of a payoff at (-2,2): %.3g (self) %.3g (max co-player)"
      % (np.abs(wq - wd).max(), np.abs(q["ne_self"] - d["ne_self"]).max(),
         np.abs(q["ne_maxpay"] - d["ne_maxpay"]).max()))

for name, T in (("census.csv", q), ("census_double.csv", d)):
    w = np.stack([T[k] for k in W], 1)
    derived = {"eff_cc": w[:, 0] == 1, "eff_alt": (w[:, 0] == 0) & (w[:, 3] == 0) & (w[:, 1] == 0.5),
               "eff_line": w[:, 3] == 0, "riv_p": T["beat_p"] == -1, "riv_m": T["beat_m"] == -1,
               "nash": T["ne_beat"] == -1, "tie_ok": (T["ne_beat"] == -1) & (T["ne_tieviol"] == 0)}
    report("%s: the 0/1 columns follow from the program outputs" % name,
           [k for k, v in derived.items() if not (T[k].astype(bool) == v).all()], [])

print("\n2. m2_masks.npz against census.csv")
Z = np.load(os.path.join(cl.DATA, "m2_masks.npz"))
M = cl.masks(q)
for k, c in (("effCC", "eff_cc"), ("effALT", "eff_alt"), ("rivP", "riv_p"), ("rivM", "riv_m"),
             ("defP", "def_p"), ("defM", "def_m")):
    report("%s == %s" % (k, c), bool((Z[k] == M[c]).all()), True)

print("\n3. the census from the exact table                                        computed        paper")
ids = np.arange(cl.NC)
cc, alt, line = M["eff_cc"], M["eff_alt"], M["eff_line"]
rp, rm, dp, dm = M["riv_p"], M["riv_m"], M["def_p"], M["def_m"]
ne, tie = M["nash"], M["tie_ok"]
fr = cl.wedges(M)
frd = cl.wedges(M, "defensible")
setof = lambda m: sorted(ids[m].tolist())
N = cl.NAMED
print(" efficiency (self-play)")
report("mutual cooperators, efficient below the switch line ('7639 mutual cooperators')", int(cc.sum()), 7639)
report("alternators, efficient above ('3072 alternators')", int(alt.sum()), 3072)
report("efficient on the switch line ('14757 strategies are efficient on the switch line')", int(line.sum()), 14757)
report("no mutual cooperator is an alternator", int((cc & alt).sum()), 0)
report("ALLC, WSLS, tit-for-two-tats and AON2 are mutual cooperators",
       [bool(cc[N[k]]) for k in ("ALLC", "WSLS", "TF2T", "AON2")], [True] * 4)
print("  (strategies efficient on an open set of games, below or above the switch line: %d)" % int((cc | alt).sum()))
print(" rivalry (limit reading)")
report("rivals for T>S ('exactly 2640 of the 65536')", int(rp.sum()), 2640)
report("rivals for T<S", int(rm.sum()), 2640)
report("the rivals for T<S are the mirror images of those for T>S",
       set(cl.mirror(ids[rp]).tolist()) == set(ids[rm].tolist()), True)
report("rivals for one sign of T-S or the other ('In all, 5230')", int((rp | rm).sum()), 5230)
report("rivals for both ('and 50 for both')", int((rp & rm).sum()), 50)
fair = rp & rm
report("  of the 50: mutual cooperators, alternators, neither ('two ... eight ... forty')",
       (int((fair & cc).sum()), int((fair & alt).sum()), int((fair & ~cc & ~alt).sum())), (2, 8, 40))
report("  tit-for-tat among them", bool(fair[N["TFT"]]), True)
print(" defensibility (Floyd-Warshall)")
report("defensible for T>S ('the 2144 strategies without a negative cycle')", int(dp.sum()), 2144)
report("defensible for T<S", int(dm.sum()), 2144)
report("defensible strategies are all rivals (T>S and T<S)", bool((dp <= rp).all() and (dm <= rm).all()), True)
report("rivals with a negative cycle ('the other 496 rivals')", int((rp & ~dp).sum()), 496)
print("  (defensible for one sign or the other: %d; for both: %d)" % (int((dp | dm).sum()), int((dp & dm).sum())))
print(" friendly rivals of the four open wedges (SI Table 2)")
for w, n in (("W", 8), ("S", 1519), ("E", 80), ("N", 80)):
    report("wedge %s, limit reading" % w, int(fr[w].sum()), n)
for w, n in (("W", 8), ("S", 1036), ("E", 80), ("N", 80)):
    report("wedge %s, defensible reading" % w, int(frd[w].sum()), n)
report("S: rivals in the limit without being defensible ('483 of the 1519')", int((fr["S"] & ~frd["S"]).sum()), 483)
report("limit and defensible readings name the same strategies in W, N and E",
       all((fr[w] == frd[w]).all() for w in "WNE"), True)
report("friendly rivals in at least one wedge ('In all, 1677')", int((fr["W"] | fr["S"] | fr["E"] | fr["N"]).sum()), 1677)
report("the eight of W", setof(fr["W"]), cl.EIGHT)
report("W and S share exactly the two fair mutual cooperators", setof(fr["W"] & fr["S"]), [20111, 24207])
report("E and N share the eight fair alternators", setof(fr["E"] & fr["N"]), setof(fair & alt))
report("the 80 of E are the mirror images of the 80 of N",
       set(cl.mirror(ids[fr["N"]]).tolist()) == set(ids[fr["E"]].tolist()), True)
report("the 80 of N cooperate at 4 to 9 of their 16 states ('between 4 and 9')",
       (min(bin(s).count("1") for s in ids[fr["N"]]), max(bin(s).count("1") for s in ids[fr["N"]])), (4, 9))
print(" on the two lines (SI section 5)")
report("friendly rivals on the switch line, part with T>S ('116')", int((line & rp).sum()), 116)
report("friendly rivals on the switch line, part with T<S ('2067')", int((line & rm).sum()), 2067)
print(" at the donation game (u,v) = (-2,2), T>S, below the switch line (SI Table 3)")
report("competitive", int(rp.sum()), 2640)
report("efficient", int(cc.sum()), 7639)
report("stable", int(ne.sum()), 672)
report("efficient and stable (partner)", int((ne & cc).sum()), 187)
report("efficient and competitive (friendly rival)", int((cc & rp).sum()), 8)
report("efficient, stable and competitive", int((cc & ne & rp).sum()), 8)
report("stable and competitive, efficiency dropped", int((ne & rp).sum()), 493)
report("partners satisfying the tie clause", int((ne & cc & tie).sum()), 8)
report("  'dropping efficiency instead lets in 485 more strategies'", int((ne & rp & ~cc).sum()), 485)
report("  ALLD among them", bool((ne & rp & ~cc)[N["ALLD"]]), True)
report("  the eight tie-clause partners are the friendly rivals of W", setof(ne & cc & tie), cl.EIGHT)
report("  every efficient competitive strategy is stable at (-2,2) (the theorem)", bool(((cc & rp) <= ne).all()), True)
report("  the stability scan ran to the end for every stable strategy (max co-player payoff <= self)",
       bool((q["ne_maxpay"][ne] <= q["ne_self"][ne] + 1e-12).all()), True)

print("\n4. the passes (data/census/passes.csv)")
P = read_table(os.path.join(cl.DATA, "passes.csv"))
sel = lambda prog, ps: (P["program"] == prog) & (P["pass"] == ps)
cp, cm = int(P["chains"][sel("pairsq", "rivP")].sum()), int(P["chains"][sel("pairsq", "rivM")].sum())
report("chains of the rivalry pass for T>S, exact ('206,891,410' in RESULT.md)", cp, 206891410)
report("chains of the rivalry pass for T<S, exact ('228,253,906')", cm, 228253906)
report("  the same numbers from the double-precision run",
       (int(P["chains"][sel("pairs", "rivP")].sum()), int(P["chains"][sel("pairs", "rivM")].sum())), (cp, cm))
# a candidate's scan stops at its first beater tau (tau + 1 chains), a rival's runs over all 65536 co-players
for ps, col in (("rivP", "beat_p"), ("rivM", "beat_m")):
    b = q[col]
    report("  %s chains = sum over non-rivals of (first beater + 1) + 65536 x rivals" % ps,
           int((b[b >= 0] + 1).sum() + 65536 * (b == -1).sum()), cp if ps == "rivP" else cm)
report("  of which the rivals' full scans, 2640 x 65536 ('1.7e8 of them for the 2640 rivals')",
       "%.1e" % (65536 * int(rp.sum())), "1.7e+08")
print("  -> 'a pass computes about 2e8 chains, 1.7e8 of them for the 2640 rivals': %.2e and %.2e, 1.73e8" % (cp, cm))
gq = P["gap_min"][(P["program"] == "pairsq") & np.isfinite(P["gap_min"])].min()
gd = P["gap_min"][(P["program"] == "pairs") & np.isfinite(P["gap_min"])].min()
report("smallest nonzero |w_DC - w_CD| met, exact ('2.93e-3')", "%.2e" % gq, "2.93e-03")
print("  smallest nonzero |w_DC - w_CD| met, double: %.2e (a spurious nonzero where the exact value is 0,"
      " absorbed by the 1e-9 tolerance)" % gd)
report("largest numerator or denominator met by the exact program ('831097')", int(P["max_int"].max()), 831097)
report("stripes per pass and program", sorted(set(np.unique(P["stripe"], return_counts=True)[1].tolist())), [8])

print("\n5. the stable strategies at (-2,2) against the exact arrangement (data/arrangement), strategy by strategy")
ARR = os.path.join(cl.DATA, os.pardir, "arrangement")
S2 = read_table(os.path.join(ARR, "m2_strategies.csv"))
FC = read_table(os.path.join(ARR, "m2_nash_facets.csv"))
LD = read_table(os.path.join(ARR, "m2_nash_lowdim.csv"))
assert (S2["genotype"] == ids).all()
for k, c in (("eff_cc", "eff_cc"), ("eff_alt", "eff_alt"), ("riv_plus", "riv_p"), ("riv_minus", "riv_m")):
    report("m2_strategies.csv %s == census %s" % (k, c), bool((S2[k].astype(bool) == M[c]).all()), True)
u0, v0 = -2, 2
dimA = S2["nash_dim"]
viol = np.zeros(cl.NC, bool)                                    # a facet a + b u + c v <= 0 fails at (u0, v0)
np.logical_or.at(viol, FC["genotype"], FC["a"] + FC["b"] * u0 + FC["c"] * v0 > 0)
nash_arr = (dimA == 2) & ~viol                                  # a polygon without facets is the whole plane
from fractions import Fraction                                  # noqa: E402
rat = lambda t: None if t in ("inf", "-inf") else Fraction(t)
for k in range(len(LD["genotype"])):                            # the stability regions of measure zero
    g, dd = int(LD["genotype"][k]), int(LD["dim"][k])
    assert dimA[g] == dd
    if dd == 1:                                                 # A u + C v = E, x0 <= x <= x1, x = u if C != 0 else v
        A_, C_, E_ = int(LD["A"][k]), int(LD["C"][k]), int(LD["E"][k])
        x = u0 if C_ != 0 else v0
        lo, hi = rat(LD["x0"][k]), rat(LD["x1"][k])
        on = A_ * u0 + C_ * v0 == E_ and (lo is None or lo <= x) and (hi is None or x <= hi)
    else:                                                       # a single game (pu, pv)
        on = (Fraction(LD["pu"][k]), Fraction(LD["pv"][k])) == (u0, v0)
    nash_arr[g] = on
report("strategies stable at (-2,2) by the arrangement", int(nash_arr.sum()), 672)
print("  (of them %d with a two-dimensional stability region, %d with a segment or ray through (-2,2), %d stable only there)"
      % ((nash_arr & (dimA == 2)).sum(), (nash_arr & (dimA == 1)).sum(), (nash_arr & (dimA == 0)).sum()))
report("  symmetric difference with census.csv nash, strategy by strategy", int((nash_arr != ne).sum()), 0)

print("\nALL AGREE" if ok else "\nDISAGREEMENT FOUND")
sys.exit(0 if ok else 1)
