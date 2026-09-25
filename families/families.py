#!/usr/bin/env python3
"""Families of friendly rivals: minimal covers of each wedge's set by wildcard patterns.

A pattern is a string of 16 symbols over {0,1,*}, position j (left to right, j = 0..15)
being state j = 4*recent + before with outcomes CC=0, CD=1, DC=2, DD=3 (own action first);
1 = C, 0 = D, * = either.  So a pattern with w wildcards names 2^w strategies.  A pattern is
'prime' for a set if all its strategies lie in the set and no wildcard can be added.  A
minimum cover is a smallest collection of primes whose union is the set (an exact
set-cover solved as an integer programme); it need not be unique, and the script reports
whether it is.

    python3 families.py            reads ../data/census/census.csv, writes families.txt and covers.csv here

(Importing the module loads the sets W, S, E, N and defines the functions without running the analysis.)

The sets are read from the exact census (efficiency from self-play, rivalry in the limit for T>S and T<S,
defensibility); the original read the same six masks from m2_masks.npz, which data/census/m2_masks.npz reproduces bit
for bit.  covers.csv is the machine-readable form of the minimum covers printed in families.txt.  The minimum cover of
S (and of its defensible reading) is not unique; which one the integer programme returns depends on the solver, and the
one deposited here is what scipy 1.10.0 (HiGHS) returns.
"""
import collections, os, sys
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "census"))
import censuslib                                                    # noqa: E402
from common.tables import write_table                               # noqa: E402
M = censuslib.masks(censuslib.load())
effCC, effALT, rivP, rivM, defP, defM = (M[k] for k in ("eff_cc", "eff_alt", "riv_p", "riv_m", "def_p", "def_m"))
COVERS = []                                                         # (set, set size, unique, pattern, wildcards)
ids = np.arange(65536)
OUT = []
def say(s=""):
    print(s); OUT.append(s)

def pattern(d, v):
    return "".join("*" if d >> j & 1 else ("1" if v >> j & 1 else "0") for j in range(16))

def table(pat):
    rows = ["CC", "CD", "DC", "DD"]
    sym = {"1": "C", "0": "D", "*": "*"}
    return ["  %s | %s" % (rows[r], " ".join(sym[pat[4 * r + b]] for b in range(4))) for r in range(4)]

def primes_of(points):
    pts = set(int(p) for p in points)
    level = set((0, p) for p in pts)
    primes = set()
    while level:
        by_dash = collections.defaultdict(set)
        for d, v in level:
            by_dash[d].add(v)
        nxt, merged = set(), set()
        for d, vs in by_dash.items():
            for v in vs:
                for j in range(16):
                    b = 1 << j
                    if d & b or v & b:
                        continue
                    if (v | b) in vs:
                        nxt.add((d | b, v)); merged.add((d, v)); merged.add((d, v | b))
        primes |= (level - merged)
        level = nxt
    return sorted(primes, key=lambda t: (-bin(t[0]).count("1"), t[1]))

def members(d, v):
    free = [j for j in range(16) if d >> j & 1]
    out = []
    for m in range(1 << len(free)):
        x = v
        for k, j in enumerate(free):
            if m >> k & 1:
                x |= 1 << j
        out.append(x)
    return out

def min_cover(points, primes, forbid=()):
    pts = sorted(int(p) for p in points); idx = {p: i for i, p in enumerate(pts)}
    A = np.zeros((len(pts), len(primes)))
    for k, (d, v) in enumerate(primes):
        for x in members(d, v):
            A[idx[x], k] = 1
    ub = np.ones(len(primes))
    for k in forbid:
        ub[k] = 0
    res = milp(c=np.ones(len(primes)), constraints=LinearConstraint(A, lb=np.ones(len(pts)), ub=np.inf),
               integrality=np.ones(len(primes)), bounds=Bounds(np.zeros(len(primes)), ub))
    if not res.success:
        return None                      # infeasible: no cover without the forbidden primes
    chosen = [k for k in range(len(primes)) if res.x[k] > 0.5]
    return chosen

def analyse(name, mask, note="", key=None):
    pts = ids[mask]
    say("=" * 78); say("%s: %d strategies %s" % (name, len(pts), note)); say("=" * 78)
    if len(pts) == 0:
        return
    # positions fixed across the whole set
    bits = (pts[:, None] >> np.arange(16)) & 1
    fixed = "".join(("1" if bits[:, j].all() else "0" if (~bits[:, j].astype(bool)).all() else "*") for j in range(16))
    say("common pattern (fixed positions of the whole set): %s   (%d fixed)" % (fixed, 16 - fixed.count("*")))
    pr = primes_of(pts)
    say("prime patterns: %d; wildcard counts: %s" % (len(pr), dict(collections.Counter(bin(d).count("1") for d, v in pr))))
    chosen = min_cover(pts, pr)
    say("minimum cover: %d patterns" % len(chosen))
    # uniqueness: forbidding any chosen prime, does the optimum grow?
    unique = True
    for k in chosen:
        alt = min_cover(pts, pr, forbid=[k])
        if alt is not None and len(alt) == len(chosen):
            unique = False; break
    say("minimum cover unique: %s" % unique)
    tot = 0
    for n, k in enumerate(sorted(chosen, key=lambda k: (-bin(pr[k][0]).count("1"), pr[k][1]))):
        d, v = pr[k]; w = bin(d).count("1"); tot += 1 << w
        mem = members(d, v)
        say("  family %2d: %s   %d wildcards -> %d strategies; ids %s%s"
            % (n + 1, pattern(d, v), w, 1 << w, mem[:4], " ..." if len(mem) > 4 else ""))
        for line in table(pattern(d, v)):
            say("           " + line)
    say("  sum of family sizes %d (set size %d; overlap %d)" % (tot, len(pts), tot - len(pts)))
    for k in sorted(chosen, key=lambda k: (-bin(pr[k][0]).count("1"), pr[k][1])):
        COVERS.append((key, len(pts), unique, pattern(*pr[k]), bin(pr[k][0]).count("1")))
    return pr, [pr[k] for k in chosen]

W = effCC & rivP; S = effCC & rivM; E = effALT & rivM; N = effALT & rivP


def main():
    res = {}
    res["W"] = analyse("W (u+v<1, u-v<1): mutual cooperators, rivals for T>S", W, key="W")
    res["N"] = analyse("N (u+v>1, u-v<1): alternators, rivals for T>S", N, key="N")
    res["E"] = analyse("E (u+v>1, u-v>1): alternators, rivals for T<S", E, "(mirror image of N)", key="E")
    res["S"] = analyse("S (u+v<1, u-v>1): mutual cooperators, rivals for T<S", S, key="S")
    analyse("S restricted to the defensible reading (efficient and defensible, T<S)", effCC & defM, key="S_def")
    analyse("W and S both: friendly rivals on both sides of T=S", W & S, key="W_and_S")
    analyse("E and N both: alternators that are rivals both ways", E & N, key="E_and_N")
    open(os.path.join(HERE, "families.txt"), "w").write("\n".join(OUT) + "\n")
    assert all(w >= 1 for *_, w in COVERS)          # a pattern without a wildcard would read back as an integer
    fam = [sum(1 for c in COVERS[:i + 1] if c[0] == COVERS[i][0]) for i in range(len(COVERS))]
    write_table(os.path.join(HERE, "covers.csv"), {
        "set": [c[0] for c in COVERS], "set_size": [c[1] for c in COVERS], "cover_unique": [c[2] for c in COVERS],
        "family": fam, "pattern": [c[3] for c in COVERS], "wildcards": [c[4] for c in COVERS],
        "members": [1 << c[4] for c in COVERS]}, [
        "The minimum covers of the sets of friendly rivals by prime wildcard patterns (families/families.py; the same",
        "covers, with the 4x4 tables and the member codes, are printed in families.txt).",
        "set           W, N, E, S: the friendly rivals of the open wedge (limit reading); S_def: the efficient strategies",
        "              defensible for T<S; W_and_S: in both W and S; E_and_N: in both E and N",
        "set_size      the number of strategies in the set",
        "cover_unique  1 if the minimum cover is unique (decided by forbidding each chosen pattern in turn)",
        "family        the number of the pattern within the cover, in the order of families.txt (largest first)",
        "pattern       sixteen symbols, position j = state j = 4*(most recent outcome) + (the outcome before), outcomes",
        "              CC=0 CD=1 DC=2 DD=3 own action first; 1 = C, 0 = D, * = either",
        "wildcards     the number of * in the pattern",
        "members       2^wildcards, the number of strategies the pattern names (patterns of one cover may overlap)"])


if __name__ == "__main__":
    main()
