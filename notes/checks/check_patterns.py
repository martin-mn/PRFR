#!/usr/bin/env python3
"""
check_patterns.py -- the arithmetic of the family patterns quoted in ../families.md.

A pattern is 16 symbols 1/0/*, position j from the left the answer in state j (1 = C); it names every code whose bit j
matches each fixed position.  Checked here: the members of the pattern of the eight friendly rivals of W, which of them
defect at (DC, DC), the sizes, overlaps and union of the four patterns of N, the eight positions they share, the range
of cooperating states among the 80, and the size of the largest pattern of S.  Then, against the census output in
../../families/ (covers.csv and families.txt, read-only), the counts the paragraphs of the note quote: the covers of W
and N, and for S its size, fixed positions, prime patterns, minimal cover, the multiplicity of that cover, the
strategies it contains and does not contain, and the defensible reading.  (Whether the patterns are the exact covers
of the families is a result of the census; see the folder families/ of the repository.)

    python3 check_patterns.py
"""
import csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pairchain as pc

ok = True


def report(cond, text):
    global ok
    ok &= bool(cond)
    print("%s  %s" % ("PASS" if cond else "FAIL", text))


def members(p):
    assert len(p) == 16
    return {c for c in range(pc.NC) if all(ch == "*" or int(ch) == (c >> j) & 1 for j, ch in enumerate(p))}


W8 = members("111*000101*1*010")
report(sorted(W8) == pc.EIGHT, "111*000101*1*010 names %s" % sorted(W8))
report([j for j, ch in enumerate("111*000101*1*010") if ch == "*"] == [3, 10, 12], "its wildcards are at positions 3, 10, 12")
dcdc = sorted(c for c in W8 if not (c >> 10) & 1)
report(dcdc == [19079, 19087, 23175, 23183], "the four that defect at (DC, DC), position 10: %s" % dcdc)
N4 = ["*10*0000*1*1*010", "*01*0000*1*1*010", "*10*000*11*10010", "*01*000*11*10010"]
M = [members(p) for p in N4]
report([len(m) for m in M] == [32, 32, 16, 16], "the four patterns of N name 32, 32, 16, 16 strategies")
report(len(M[0] & M[2]) == 8 and len(M[1] & M[3]) == 8 and not (M[0] & M[1]) and not (M[2] & M[3])
       and not (M[0] & M[3]) and not (M[1] & M[2]),
       "the pairs (32, 16) with the same first symbols share 8 each, and no other pair overlaps")
U = set().union(*M)
report(len(U) == 80, "their union has %d members (32 + 32 + 16 + 16 - 16 = 80)" % len(U))
report(U <= members("****000**1*1*010"), "all 80 agree at the eight positions ****000**1*1*010")
nc = [bin(c).count("1") for c in U]
report((min(nc), max(nc)) == (4, 9), "they cooperate at between %d and %d of their 16 states" % (min(nc), max(nc)))
report(len(members("111*1***11*1****")) == 512, "the largest pattern of S, 111*1***11*1****, names 512 strategies")

# the census output in families/
FAM = os.path.join(HERE, os.pardir, os.pardir, "families")
cov = {}
for r in csv.DictReader(l for l in open(os.path.join(FAM, "covers.csv")) if not l.startswith("#")):
    cov.setdefault(r["set"], []).append(r)
report([r["pattern"] for r in cov["W"]] == ["111*000101*1*010"] and cov["W"][0]["cover_unique"] == "1",
       "families/: the cover of W is the single pattern 111*000101*1*010, unique")
report(sorted(r["pattern"] for r in cov["N"]) == sorted(N4) and cov["N"][0]["cover_unique"] == "1",
       "families/: the cover of N is the four patterns above, unique")
cS = cov["S"]
US = set().union(*(members(r["pattern"]) for r in cS))
report(int(cS[0]["set_size"]) == 1519 and len(US) == 1519, "families/: S has 1519 strategies, the union of its cover too")
report(len(cS) == 42 and cS[0]["cover_unique"] == "0", "families/: the minimal cover of S has 42 patterns and is not unique")
report(sum(int(r["members"]) for r in cS) == 4368, "families/: its 42 patterns name %d strategies with multiplicity"
       % sum(int(r["members"]) for r in cS))
report("111*1***11*1****" in [r["pattern"] for r in cS] and max(int(r["members"]) for r in cS) == 512,
       "families/: its largest pattern is 111*1***11*1****, 512 strategies")
TF2T = sum(1 << j for j in range(16) if not ((j >> 2) in (1, 3) and (j & 3) in (1, 3)))   # C unless defected on twice
AON2 = sum(1 << j for j in range(16) if (j >> 2) in (0, 3) and (j & 3) in (0, 3))         # C iff both rounds matched
have = {"ALLC": pc.ALLC, "tit-for-two-tats": TF2T, "20111": 20111, "24207": 24207}
lack = {"WSLS": pc.WSLS, "AON2": AON2}
report(all(c in US for c in have.values()) and not any(c in US for c in lack.values()),
       "S contains ALLC, tit-for-two-tats (%d), 20111 and 24207, but not WSLS or AON2 (%d)" % (TF2T, AON2))
fixed = [j for j in range(16) if len({(c >> j) & 1 for c in US}) == 1]
report(fixed == [0, 2] and all((c & 1) and (c >> 2) & 1 for c in US),
       "only two positions are fixed across S, cooperation at (CC, CC) and at (CC, DC) (positions %s)" % fixed)
txt = open(os.path.join(FAM, "families.txt")).read()
blocks = re.split(r"\n=+\n", txt)


def block(head):
    hits = [blocks[i + 1] for i, b in enumerate(blocks[:-1]) if b.strip().startswith(head)]
    assert len(hits) == 1, head
    return hits[0]


m = re.search(r"prime patterns: (\d+); wildcard counts: \{([^}]*)\}", block("S (u+v<1, u-v>1)"))
wc = sorted(int(k.split(":")[0]) for k in m.group(2).split(","))
report(int(m.group(1)) == 56 and (wc[0], wc[-1]) == (4, 9),
       "families/: S has 56 prime patterns, with %d to %d wildcards each" % (wc[0], wc[-1]))
m = re.search(r"prime patterns: (\d+);", block("S restricted to the defensible reading"))
report(int(cov["S_def"][0]["set_size"]) == 1036 and int(m.group(1)) == 33 and len(cov["S_def"]) == 24,
       "families/: the defensible reading of S has 1036 strategies, 33 prime patterns and a cover of 24")
print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
