#!/usr/bin/env python3
"""sitable4.py -- SI Table 4, the families of friendly rivals, recomputed from the census (data/census/census.csv).

    python3 sitable4.py          prints the table next to the paper's, writes SITable4.csv and SITable4.txt;
                                 exit status 1 on a mismatch            (about 2 s; numpy and scipy)

The sets are the friendly rivals of the wedges W (mutual cooperators that are rivals for T>S) and N (alternators that
are rivals for T>S).  Their prime patterns and minimum covers are recomputed here with the functions of
families/families.py (Quine-McCluskey merging, an exact set cover by integer programming, uniqueness by forbidding each
chosen pattern in turn), independently of the deposited families/covers.csv, which is then compared with the result.
Each pattern is also checked directly against the census: every strategy it names is in the set, no fixed position can
be made a wildcard, and the union of the cover is the set.  A genome is laid out as in the paper: rows the most recent
outcome, columns the outcome before, own action first; the text of SI section 7 about the table is checked as well.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "families"))
import families as fam                            # noqa: E402  (loads the census; runs no analysis)
import censuslib as cl                            # noqa: E402  (put on the path by families)
from common.tables import read_table, write_table  # noqa: E402

OUT = ["CC", "CD", "DC", "DD"]

# SI Table 4 as printed in ms.tex: pattern, members, and the 4x4 table by rows CC, CD, DC, DD
PAPER = {
    ("a", 1): ("111*000101*1*010", 8, ["CCC*", "DDDC", "DC*C", "*DCD"]),
    ("b", 1): ("*10*0000*1*1*010", 32, ["*CD*", "DDDD", "*C*C", "*DCD"]),
    ("b", 2): ("*01*0000*1*1*010", 32, ["*DC*", "DDDD", "*C*C", "*DCD"]),
    ("b", 3): ("*10*000*11*10010", 16, ["*CD*", "DDD*", "CC*C", "DDCD"]),
    ("b", 4): ("*01*000*11*10010", 16, ["*DC*", "DDD*", "CC*C", "DDCD"]),
}
# the wedge E in the text of SI section 7 and the caption: the mirror images of the patterns of N
PAPER_E = ["101*0*0*1111*10*", "101*0*0*1111*01*", "10110*00*111*10*", "10110*00*111*01*"]

ok = True


def check(label, got, want):
    global ok
    same = got == want
    ok &= bool(same)
    print("  %-78s %s" % (label, "agrees" if same else "DIFFERS: %s, paper %s" % (got, want)))


def grid(p):
    sym = {"1": "C", "0": "D", "*": "*"}
    return ["".join(sym[p[4 * r + b]] for b in range(4)) for r in range(4)]


def names(p):
    """the codes a pattern names"""
    d = sum(1 << j for j, c in enumerate(p) if c == "*")
    v = sum(1 << j for j, c in enumerate(p) if c == "1")
    return set(fam.members(d, v))


def is_prime(p, S):
    """every strategy named is in S, and no fixed position can be turned into a wildcard"""
    if not names(p) <= S:
        return False
    return all(not names(p[:j] + "*" + p[j + 1:]) <= S for j in range(16) if p[j] != "*")


def mirror_pattern(p):
    return "".join({"1": "0", "0": "1", "*": "*"}[c] for c in p[::-1])


def cover(mask):
    """(prime patterns, a minimum cover as patterns in families.txt order, unique?) of a set"""
    pts = fam.ids[mask]
    pr = fam.primes_of(pts)
    chosen = fam.min_cover(pts, pr)
    unique = all(not (alt is not None and len(alt) == len(chosen))
                 for alt in (fam.min_cover(pts, pr, forbid=[k]) for k in chosen))
    chosen = sorted(chosen, key=lambda k: (-bin(pr[k][0]).count("1"), pr[k][1]))
    return pr, [fam.pattern(*pr[k]) for k in chosen], unique


sets = {w: set(fam.ids[m].tolist()) for w, m in (("W", fam.W), ("N", fam.N), ("E", fam.E), ("S", fam.S))}
rows = []
print("SI Table 4: the families of friendly rivals (recomputed from data/census/census.csv)")
for panel, w in (("a", "W"), ("b", "N")):
    pr, pats, unique = cover(fam.W if w == "W" else fam.N)
    print("\n %s  the wedge %s: %d strategies, %d prime patterns, a minimum cover of %d (unique: %s)"
          % (panel, w, len(sets[w]), len(pr), len(pats), unique))
    check("the cover of %s is unique" % w, unique, True)
    check("number of families of %s" % w, len(pats), 1 if w == "W" else 4)
    union = set()
    for i, p in enumerate(pats, 1):
        g = grid(p)
        n = len(names(p))
        union |= names(p)
        rows.append((panel, w, i, p, n, g))
        want = PAPER.get((panel, i))
        print("   family %d (%d)  %s" % (i, n, p))
        for r in range(4):
            print("     %s | %s" % (OUT[r], " ".join(g[r])))
        check("family %d: pattern, size and table as printed" % i, (p, n, g), want)
        check("family %d is prime for the set" % i, is_prime(p, sets[w]), True)
    check("the union of the families of %s is the set" % w, union == sets[w], True)

print("\n the wedge E: the mirror images of the families of N")
pe = [mirror_pattern(r[3]) for r in rows if r[1] == "N"]
check("mirror images of the four patterns of N", pe, PAPER_E)
check("they are prime for E and cover it", all(is_prime(p, sets["E"]) for p in pe)
      and set().union(*(names(p) for p in pe)) == sets["E"], True)
_, pats_e, unique_e = cover(fam.E)
check("the recomputed minimum cover of E is these four, and unique", (sorted(pats_e), unique_e), (sorted(pe), True))

print("\n the text of SI section 7 about the table")
wfam = rows[0][3]
Wm = sorted(names(wfam))
check("W: the eight integer codes", Wm, cl.EIGHT)
check("W: the wildcards sit at positions 3, 10, 12", [j for j, c in enumerate(wfam) if c == "*"], [3, 10, 12])
check("W: ... the states (CC,DD), (DC,DC), (DD,CC)",
      [(OUT[j >> 2], OUT[j & 3]) for j, c in enumerate(wfam) if c == "*"], [("CC", "DD"), ("DC", "DC"), ("DD", "CC")])
check("W: the four that defect at (DC,DC)", sorted(s for s in Wm if not s >> 10 & 1), [19079, 19087, 23175, 23183])
check("W: of the four that cooperate there, 20111 and 24207 are fair and in S",
      sorted(s for s in Wm if s >> 10 & 1 and s in sets["S"]), [20111, 24207])
F = {r[2]: names(r[3]) for r in rows if r[1] == "N"}
P = {r[2]: r[3] for r in rows if r[1] == "N"}
diff = lambda a, b: [j for j in range(16) if P[a][j] != P[b][j]]
check("N: the two families of a pair differ only at (CC,CD) and (CC,DC)", (diff(1, 2), diff(3, 4)), ([1, 2], [1, 2]))
check("N: the pairs differ at three further states", (len(diff(1, 3)), len(diff(2, 4))), (3, 3))
check("N: the families of 32 and 16 on the left share 8, as do the two on the right",
      (len(F[1] & F[3]), len(F[2] & F[4])), (8, 8))
check("N: 32 + 32 + 16 + 16 - 16 = 80",
      (sum(len(F[i]) for i in F), len(F[1] & F[3]) + len(F[2] & F[4]), len(set().union(*F.values()))), (96, 16, 80))
bits = (fam.ids[fam.N][:, None] >> np.arange(16)) & 1
common = "".join("1" if bits[:, j].all() else "0" if not bits[:, j].any() else "*" for j in range(16))
check("N: all 80 agree at the eight positions ****000**1*1*010", (common, 16 - common.count("*")), ("****000**1*1*010", 8))
ncoop = [bin(s).count("1") for s in sets["N"]]
check("N: the 80 cooperate at between 4 and 9 of their 16 states", (min(ncoop), max(ncoop)), (4, 9))
check("N: eight of them are friendly rivals in E as well", len(sets["N"] & sets["E"]), 8)

print("\n the wedge S, not in the table (text of SI section 7, 'The wedge S: no compact description')")
prS, patsS, uniqueS = cover(fam.S)
bitsS = (fam.ids[fam.S][:, None] >> np.arange(16)) & 1
commonS = "".join("1" if bitsS[:, j].all() else "0" if not bitsS[:, j].any() else "*" for j in range(16))
check("S: 1519 strategies with two positions in common, C at (CC,CC) and (CC,DC)", (len(sets["S"]), commonS),
      (1519, "1*1*************"))
wc = [bin(d).count("1") for d, v in prS]
check("S: 56 prime patterns with 4 to 9 wildcards", (len(prS), min(wc), max(wc)), (56, 4, 9))
check("S: a family description needs 42 of them, and it is not unique", (len(patsS), uniqueS), (42, False))
check("S: the largest pattern 111*1***11*1**** names 512 strategies", (patsS[0], len(names(patsS[0]))),
      ("111*1***11*1****", 512))
check("S: ALLC and tit-for-two-tats among them", [cl.NAMED[k] in names(patsS[0]) for k in ("ALLC", "TF2T")], [True] * 2)
check("S: WSLS and AON2 are not in the set", [cl.NAMED[k] in sets["S"] for k in ("WSLS", "AON2")], [False] * 2)
prD, patsD, uniqueD = cover(fam.effCC & fam.defM)
check("S, defensible reading: 1036 strategies, 33 prime patterns, a description of 24",
      (int((fam.effCC & fam.defM).sum()), len(prD), len(patsD)), (1036, 33, 24))
Cd = read_table(os.path.join(HERE, os.pardir, "families", "covers.csv"))
dep = [p for s, p in zip(Cd["set"], Cd["pattern"]) if s == "S"]
check("S: the deposited cover (covers.csv) is a cover of 42 prime patterns",
      (len(dep), all(is_prime(p, sets["S"]) for p in dep), set().union(*(names(p) for p in dep)) == sets["S"]),
      (42, True, True))
print("  (the cover returned here %s the deposited one)" % ("is" if sorted(dep) == sorted(patsS) else "differs from"))

print("\n the deposited covers (families/covers.csv) against this recomputation")
C = read_table(os.path.join(HERE, os.pardir, "families", "covers.csv"))
for w in ("W", "N", "E"):
    dep = [p for s, p in zip(C["set"], C["pattern"]) if s == w]
    mine = [r[3] for r in rows if r[1] == w] if w != "E" else sorted(pats_e, key=lambda p: -p.count("*"))
    check("covers.csv, %s" % w, sorted(dep), sorted(mine))

lines = ["SI Table 4: the families of friendly rivals (recomputed by SITable4/sitable4.py)", ""]
for panel, w, i, p, n, g in rows:
    lines.append("%s  wedge %s  family %d (%d)  %s" % (panel, w, i, n, p))
    lines.append("       most recent | the round before: CC CD DC DD")
    lines += ["       %-11s |                   %s" % (OUT[r], "  ".join(g[r])) for r in range(4)]
    lines.append("")
lines.append("E  the mirror images of the families of N: " + ", ".join(pe))
open(os.path.join(HERE, "SITable4.txt"), "w").write("\n".join(lines) + "\n")
write_table(os.path.join(HERE, "SITable4.csv"), {
    "panel": [r[0] for r in rows], "wedge": [r[1] for r in rows], "family": [r[2] for r in rows],
    "pattern": [r[3] for r in rows], "members": [r[4] for r in rows],
    "row_CC": [r[5][0] for r in rows], "row_CD": [r[5][1] for r in rows],
    "row_DC": [r[5][2] for r in rows], "row_DD": [r[5][3] for r in rows]}, [
    "SI Table 4, recomputed by SITable4/sitable4.py from data/census/census.csv.",
    "pattern: position j = state j = 4*(most recent outcome) + (the outcome before), 1 = C, 0 = D, * = either.",
    "row_XY: the answers after the most recent outcome XY, for the outcome before CC, CD, DC, DD (C, D or *).",
    "The families of the wedge E are the mirror images of those of N (each pattern reversed and complemented):",
    ", ".join(pe)])
print("\nwrote SITable4.csv and SITable4.txt")
print("ALL AGREE" if ok else "DISAGREEMENT FOUND")
sys.exit(0 if ok else 1)
