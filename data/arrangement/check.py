#!/usr/bin/env python3
"""
Checks the deposited arrangements against themselves and recovers the numbers the paper quotes from them.

    python3 check.py            (from this folder or anywhere; about 30 s; numpy only)

Memory two.  From the combinatorial description alone -- the 254 lines (m2_lines.csv), the side of every line on
each of the 22872 cells (m2_cells.csv), the facets of the stability polygon of every strategy (m2_nash_facets.csv) and
the efficiency and rivalry of every strategy (m2_strategies.csv) -- the stable strategies of every face are rebuilt in
integer arithmetic: a strategy is stable on a cell exactly when the cell lies on the feasible side of the line of each of its
facets.  Combined with the efficient set of the face's side of the switch line u + v = 1 and the competitive set of
its side of T = S, this gives the seven atom counts of every face, which must equal the columns of m2_faces.csv.
Then the drawn polygons (m2_faces_k4.npz) are checked to lie, every vertex mapped back to the plane, on the
recorded side of every line, and the recorded interior game of each face as well.

Memory one.  The atom counts of every face (m1_faces.csv) must be the tallies of the 16 strategies' codes.  The exact
rebuild of the memory-one arrangement from scratch is m1atoms.py.

Printed at the end: the counts 23861, 9431, 299, 22069, 8 and 7639 of the Methods, the 27598 faces, the ten and the
twelve cases, the atom totals of SI section 8, and the regions of SI sections 6 and 8 that are exact polygons of
the arrangement.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))
sys.path.insert(0, HERE)
from common import tables                                          # noqa: E402
from common.atoms import IDX, ORDER                                # noqa: E402
from common.geometry import polyarea                               # noqa: E402
import arrangement                                                 # noqa: E402

NC = 65536
ok = []


def claim(cond, text):
    assert cond, "FAILED: " + text
    ok.append(text)
    print("  ok  " + text)


def T(name):
    return tables.read_table(os.path.join(HERE, name))


# ============================================================================================ memory two
print("memory two")
L, C, F, S, FA = T("m2_lines.csv"), T("m2_cells.csv"), T("m2_faces.csv"), arrangement.m2_strategies(), T("m2_nash_facets.csv")
LO = T("m2_nash_lowdim.csv")
NL, NCELL, NF = len(L["line"]), len(C["cell"]), len(F["face"])
LN = [(int(a), int(b), int(c)) for a, b, c in zip(L["A"], L["B"], L["C"])]
LIX = {ln: j for j, ln in enumerate(LN)}
claim((L["line"] == np.arange(NL)).all() and len(set(LN)) == NL == 254, "254 distinct lines")
SIDE = np.array([[int(s, 16) >> j & 1 for j in range(NL)] for s in C["sides"]], dtype=bool)   # (cells, lines)
claim(len({r.tobytes() for r in np.packbits(SIDE, axis=1)}) == NCELL == 22872, "22872 cells, each its own sign vector")


def nfaces(lines):
    """the number of faces of the arrangement of the lines A u + B v = C over the whole plane, exactly:
    1 + (number of lines) + sum over the intersection points p of (m_p - 1), m_p the lines through p"""
    from fractions import Fraction
    pts = {}
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            (a1, b1, c1), (a2, b2, c2) = lines[i], lines[j]
            det = a1 * b2 - a2 * b1
            if det:
                pts.setdefault((Fraction(c1 * b2 - c2 * b1, det), Fraction(a1 * c2 - a2 * c1, det)), set()).update((i, j))
    far = max(max(abs(u), abs(v)) for u, v in pts)
    return 1 + len(lines) + sum(len(m) - 1 for m in pts.values()), len(pts), far


nf_, npt, far = nfaces(LN)
claim(nf_ == NCELL and far < 2000, "the 254 lines cut the whole plane into exactly %d faces (%d intersection points, all with "
      "|u|, |v| <= %s): the cells of m2_cells.csv are all of them" % (nf_, npt, far))

# ---- the facets, re-derived from (a, b, c): a + b u + c v <= 0 is the line (b, c, -a) up to sign and gcd
from math import gcd                                               # noqa: E402
for a, b, c, j, bit in zip(FA["a"], FA["b"], FA["c"], FA["line"], FA["bit"]):
    A, B, Cc = int(b), int(c), -int(a)
    q = gcd(gcd(abs(A), abs(B)), abs(Cc)) or 1
    A, B, Cc, s = A // q, B // q, Cc // q, 1
    if (A, B, Cc) < (-A, -B, -Cc):
        A, B, Cc, s = -A, -B, -Cc, -1
    assert LIX[(A, B, Cc)] == j and bit == (1 if s < 0 else 0), (a, b, c, j, bit)
claim(True, "every facet (a, b, c) lies on its recorded line, feasible on its recorded side")
dim = S["nash_dim"]
nfac = np.bincount(FA["genotype"], minlength=NC)
claim(((dim == 2) == (nfac > 0)).all() and (nfac == S["nash_nfacets"]).all(),
      "the facet rows match nash_dim and nash_nfacets (every polygon has at least one facet)")
claim([int((dim == d).sum()) for d in (2, 1, 0, -1)] == [23861, 3774, 4875, 33026] and len(LO["genotype"]) == 3774 + 4875
      and set(LO["genotype"]) == set(np.nonzero((dim == 0) | (dim == 1))[0]),
      "stability regions: 23861 polygons with interior, 3774 on part of a line, 4875 at one game, 33026 nowhere")

# ---- the stable strategies of every cell
fs = {}
for g, j, bit in zip(FA["genotype"], FA["line"], FA["bit"]):
    fs.setdefault(int(g), []).append((int(j), bool(bit)))
key = {g: tuple(sorted(v)) for g, v in fs.items()}
uk = sorted(set(key.values()))
kid = {k: i for i, k in enumerate(uk)}
NEK = np.ones((NCELL, len(uk)), bool)                              # (cells, facet sets): stable on the cell
for i, k in enumerate(uk):
    for j, bit in k:
        NEK[:, i] &= SIDE[:, j] == bit
GK = np.full(NC, -1)
for g, k in key.items():
    GK[g] = kid[k]
below = ~SIDE[:, LIX[(1, 1, 1)]]                                   # u + v < 1
tgs = ~SIDE[:, LIX[(1, -1, 1)]]                                    # u - v < 1: T > S
ec, ea, rp, rm = S["eff_cc"], S["eff_alt"], S["riv_plus"], S["riv_minus"]
grp = {}
for g in range(NC):
    grp.setdefault((GK[g], ec[g], ea[g], rp[g], rm[g]), []).append(g)
N = np.zeros(NCELL, np.int64); P = np.zeros(NCELL, np.int64); A8 = np.zeros((NCELL, 8), np.int64)
OPEN = np.zeros((NC, 8), bool)
for (k, e1, e2, r1, r2), gs in grp.items():
    n = len(gs)
    ne = NEK[:, k] if k >= 0 else np.zeros(NCELL, bool)
    ef = np.where(below, e1, e2); rv = np.where(tgs, r1, r2)
    code = 4 * ef.astype(int) + 2 * ne.astype(int) + rv.astype(int)
    N += n * ne; P += n * (ne & ef)
    for c in range(8):
        A8[:, c] += n * (code == c)
    for c in np.unique(code):
        OPEN[gs, c] = True
print("       (%d distinct sets of stable strategies among the %d cells)" % (len({r.tobytes() for r in np.packbits(NEK[:, GK[GK >= 0]], axis=1)}), NCELL))
cell = F["cell"]
claim(NF == 27598 and set(cell) == set(range(NCELL)), "27598 faces, each in one of the 22872 cells, every cell drawn")
claim((F["nash"] == N[cell]).all() and (F["partners"] == P[cell]).all(),
      "the counts of stable strategies and of partners of every face follow from the facets and the sides")
claim((tables.atom_array(F, "A") == A8[cell][:, IDX]).all(), "the seven atom counts of every face follow as well")
claim(not A8[:, 5].any() and (A8.sum(1) == NC).all(), "101 is empty on every face and the seven add up to 65536")
claim(all((S["open_" + c] == OPEN[:, int(c, 2)]).all() for c in ORDER) and not OPEN[:, 5].any(),
      "open_xyz of m2_strategies.csv: the strategies in each atom on some face")

# ---- the drawn polygons against the lines
D2 = arrangement.m2()
V = np.vstack(D2["faces"]); OFF = np.cumsum([0] + [len(f) for f in D2["faces"]])
r2 = (V ** 2).sum(1)
Pl = V * (4.0 / np.sqrt(np.maximum(1.0 - r2, 1e-12)))[:, None]     # disk -> plane (fig1.py's plane)
LA = np.array(LN, float)
fid = np.repeat(np.arange(NF), np.diff(OFF))
worst = 0.0
for lo in range(0, NL, 32):                                        # in slices, to keep the memory small
    sl = slice(lo, min(lo + 32, NL))
    val = Pl @ LA[sl, :2].T - LA[sl, 2][None, :]
    sc = (1.0 + np.abs(Pl).sum(1))[:, None] * np.abs(LA[sl, :2]).sum(1)[None, :] + np.abs(LA[sl, 2])[None, :]
    want = np.where(SIDE[cell[fid], sl], 1.0, -1.0)                # +1: A u + B v > C
    bad = -(val / sc) * want                                       # > 0: on the wrong side
    worst = max(worst, float(bad.max()))
    uv = D2["uvc"] @ LA[sl, :2].T - LA[sl, 2][None, :]
    assert ((uv > 0) == SIDE[cell, sl]).all(), "an interior game is off its cell"
claim(worst < 1e-9, "every drawn vertex lies on its cell's side of all 254 lines (worst excursion %.1e, relative)" % worst)
claim(True, "the recorded interior game of every face lies strictly in its cell")

# ---- the numbers of the paper
print("\n  the counts of the Methods ('Nash equilibria, partners and atoms') and of SI section 6 (and 8):")
nopen = int((OPEN[:, [2, 3, 6, 7]].any(1)).sum()); popen = int((OPEN[:, [6, 7]].any(1)).sum())
claim(nopen == 23861, "23861 strategies are stable on an open set of games")
claim(popen == 9431, "9431 strategies are partners (efficient and stable) on an open set of games")
claim((N.min(), N.max()) == (299, 22069), "299 to 22069 stable strategies at a game in the interior of a face")
claim((P.min(), P.max()) == (8, 7639), "8 to 7639 partners at a game in the interior of a face")
u1, v0 = SIDE[:, LIX[(1, 0, 1)]], SIDE[:, LIX[(0, 1, 0)]]          # u > 1, v > 0
sq = ~u1 & ~v0                                                     # u < 1, v < 0: S < R and T < R
claim(((P == 7639) == sq).all() and ((A8[:, 4] == 0) == sq).all(),
      "7639 partners, and no 100, exactly on the cells with u < 1, v < 0 (S < R, T < R)")
FRW = np.nonzero(ec & rp)[0]                                      # the friendly rivals of W: efficient below the
m8 = P == 8                                                        # switch line and rivals for T > S
ok8 = np.all([NEK[m8, GK[g]] for g in FRW], axis=0)                # each of them stable on the cell
claim(len(FRW) == 8 and ok8.all() and (F["quadrant"][m8[cell]] == "PD").all() and below[m8].all(),
      "the 8 partners, where there are 8, are the 8 friendly rivals of W %s; all such faces are in the Prisoner's"
      " Dilemma below the switch line" % list(FRW))
sde = (F["quadrant"] == "SD") & (F["wedge"] == "E")
claim(sde.sum() == 557 and len(set(cell[sde])) == 557 and not (A8[cell[sde]][:, [2, 3]]).any(),
      "the Snowdrift part of E has 557 faces and no inefficient stable strategy (010, 011) on any of them")
tot = OPEN.sum(0)
print("\n  per atom: strategies in it on an open set; per game where present; share of the disk where empty")
DA = np.array([polyarea(f) for f in D2["faces"]]); DA /= DA.sum()
for c in ORDER:
    v = A8[cell, int(c, 2)]
    print("    %s  %6d   %5d-%5d   %5.1f%%" % (c, tot[int(c, 2)], v[v > 0].min(), v.max(), 100 * DA[v == 0].sum()))
keys = {tuple(r) for r in (A8[:, IDX] > 0)}
CS = T("cases.csv")
cas = {tuple(bool(CS["present_" + c][i]) for c in ORDER): int(CS["case"][i]) for i in range(len(CS["case"]))}
claim(len(keys) == 10 and (np.array([cas[tuple(r)] for r in (A8[cell][:, IDX] > 0)]) == F["case"]).all(),
      "ten cases at memory two, and each face's case number is its set of non-empty atoms")
claim(sorted({cas[k] for k in keys}) == [1, 2, 3, 4, 5, 6, 7, 9, 11, 13], "the memory-two cases are 1-7, 9, 11, 13")

# ============================================================================================ memory one
print("\nmemory one")
D1 = arrangement.m1()
A1 = np.array([np.bincount(c, minlength=8) for c in D1["codes"]])
claim(len(D1["faces"]) == 45 and (A1 == D1["atoms"]).all() and (A1.sum(1) == 16).all() and not A1[:, 5].any(),
      "45 faces; the atom counts are the tallies of the 16 codes, add up to 16, and 101 is empty")
k1 = [tuple(r) for r in (A1[:, IDX] > 0)]
claim(len(set(k1)) == 12 and all(cas[k] == c for k, c in zip(k1, D1["case"])), "twelve cases at memory one")
claim(len(set(k1) & keys) == 3 and sorted(cas[k] for k in set(k1) & keys) == [7, 11, 13],
      "three cases shared with memory two: 7, 11, 13")
claim(len(D1["lines"]) == 11 and abs(sum(polyarea(f) for f in D1["faces"]) / np.pi - 1) < 1e-4, "11 lines; the faces tile the disk")
claim(nfaces([(int(a), int(b), -int(c)) for a, b, c in D1["lines"]])[0] == 45,
      "the 11 lines cut the whole plane into exactly 45 faces, the 45 of m1_faces.csv")
uv1 = D1["uvc"]
eff1 = np.array([[(c >> 2) & 1 for c in row] for row in D1["codes"]])
claim(eff1.sum(1).max() == 3 and (eff1[uv1[:, 0] + uv1[:, 1] > 1].sum(1) == 0).all()
      and (((A1[:, 6] + A1[:, 7]) == 3) == ((uv1[:, 0] < 1) & (uv1[:, 1] < 0))).all(),
      "memory one: 3 mutual cooperators, no alternator; all 3 are partners exactly where u < 1, v < 0 (S < R, T < R)")
claim(all((D1["codes"][:, s] == 0).any() for s in range(16) if s != 5) and not (D1["codes"][:, 5] == 0).any(),
      "memory one: every strategy but tit-for-tat (CDCD) is in 000 somewhere")
ne1 = (D1["codes"] >> 1) & 1
claim(ne1.any(0).sum() == 8 and (ne1.sum(1).min(), ne1.sum(1).max()) == (0, 8),
      "memory one: 8 of the 16 are stable on an open set of games, 0 to 8 at a game")
sd = (uv1[:, 0] > 0) & (uv1[:, 1] > 0)
wsls = D1["genomes"].index("CDDC")
sq1 = sd & (uv1[:, 0] < 1) & (uv1[:, 1] < 1)
claim((ne1[sd].sum(1) == np.where(sq1[sd], 1, 0)).all() and ne1[sq1, wsls].all(),
      "memory one: in the Snowdrift quadrant the only stable strategy is WSLS (CDDC), on the unit square, and outside it none")
# the numbering: by the number of empty atoms, then by the summed shares of the two disks
share = {tuple(bool(CS["present_" + c][i]) for c in ORDER): CS["m1_share"][i] + CS["m2_share"][i] for i in range(19)}
order = sorted(share, key=lambda k: (7 - sum(k), -share[k]))
claim([cas[k] for k in order] == list(range(1, 20)), "the 19 cases are numbered by empty atoms, then by area")
print("\nall %d checks passed" % len(ok))
