#!/usr/bin/env python3
"""
check_memory_one_atoms.py -- the reading of main text Figure 2a-g atom by atom (../memory-one-atoms.md), sentence by
sentence, against the exact memory-one arrangement ../../data/arrangement/m1_faces.csv (read-only).

That table gives, for each of the 45 faces of the memory-one arrangement, a game (u, v) strictly inside it, its area
on the disk of the main-text figures, and the atom of each of the 16 binary memory-one strategies there (code
4 efficient + 2 stable + competitive), computed exactly by data/arrangement/m1atoms.py.  Each sentence of the note that
names the members of an atom is written below as a rule that gives, for a game (u, v), the set of strategies in that
atom; the rule must give exactly the strategies of the table on every face.  Sentences that state a range, an
exception or a share are checked as stated.

Units: (R, S, T, P) = (1, u, 1 + v, 0), so T > R is v > 0, S > R is u > 1, T > S is u < 1 + v, 2S < R + P is u < 1/2,
T < 2R - P is v < 1, 2S + R <= 3P is u <= -1/2, and the switch line S + T = 2R is u + v = 1.  A strategy is written by
its answers after CC, CD, DC, DD, own move first: ALLD DDDD, Grim CDDD, TFT CDCD, WSLS CDDC, ALLC CCCC.

    python3 check_memory_one_atoms.py          (under a second; the standard library only)
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, os.pardir, os.pardir, "data", "arrangement", "m1_faces.csv")
NAME = {"DDDD": "ALLD", "CDDD": "Grim", "CDCD": "TFT", "CDDC": "WSLS", "CCCC": "ALLC"}
ATOM = {"000": 0, "100": 4, "010": 2, "001": 1, "110": 6, "011": 3, "111": 7}

rows = list(csv.DictReader(l for l in open(TABLE) if not l.startswith("#")))
GEN = [k[5:] for k in rows[0] if k.startswith("code_")]
assert len(GEN) == 16
F = []
for r in rows:
    code = {NAME.get(g, g): int(r["code_" + g]) for g in GEN}
    F.append(dict(u=float(r["u"]), v=float(r["v"]), q=r["quadrant"], w=r["wedge"], disk=float(r["disk_area"]), code=code))
ALL = sorted(F[0]["code"])

ok = True


def report(cond, text):
    global ok
    ok &= bool(cond)
    print("%s  %s" % ("PASS" if cond else "FAIL", text))


def members(f, atom):
    return {s for s, c in f["code"].items() if c == ATOM[atom]}


def rule(atom, fn, text):
    """fn(u, v, f) -> the set of strategies the sentence puts in the atom at the face f; compared on every face"""
    bad = [(round(f["u"], 3), round(f["v"], 3), sorted(members(f, atom)), sorted(fn(f["u"], f["v"], f)))
           for f in F if members(f, atom) != set(fn(f["u"], f["v"], f))]
    report(not bad, "%s: %s%s" % (atom, text, "" if not bad else "   (differs at %s)" % bad[:3]))


below = lambda u, v: u + v < 1                      # below the switch line, S + T < 2R
TgtS = lambda u, v: u < 1 + v
wedgeS = lambda u, v: below(u, v) and not TgtS(u, v)
square = lambda u, v: 0 < u < 1 and 0 < v < 1

report(len(F) == 45, "the arrangement has 45 faces")

# 000
n000 = [len(members(f, "000")) for f in F]
report((min(n000), max(n000)) == (6, 12), "000: between six and twelve of the sixteen strategies (%d to %d)" % (min(n000), max(n000)))
never = [s for s in ALL if all(f["code"][s] != 0 for f in F)]
report(never == ["TFT"], "000: tit-for-tat is the only strategy that never belongs to it (never in 000: %s)" % never)
report(all(f["code"]["TFT"] & 1 for f in F), "tit-for-tat is competitive at every game")

# 100
rule("100", lambda u, v, f: ({"ALLC", "CCCD"} if below(u, v) and v > 0 else set())
     | ({"WSLS"} if below(u, v) and (v > 1 or (f["q"] == "HA" and u > 1)) else set()),
     "ALLC and CCCD wherever T > R below the switch line, joined by WSLS where T > 2R - P, and WSLS alone in the "
     "Harmony games with S > R")
report(all(not members(f, "100") for f in F if not below(f["u"], f["v"])), "100 is empty above the switch line")
report(all(not (f["code"][s] & 4) for f in F if not below(f["u"], f["v"]) for s in ALL),
       "above the switch line no memory-one strategy is efficient")
low = [f for f in F if f["v"] < 0 and f["u"] < 1]
report(all(not members(f, "100") for f in low) and all(f["code"][s] & 2 for f in low for s in ("ALLC", "CCCD", "WSLS")),
       "100 is empty where T <= R and S <= R, where ALLC, CCCD and WSLS are all stable")

# 010
SH = [f for f in F if f["q"] == "SH"]
five = {"ALLD", "Grim", "DCCD", "DDDC", "DCCC"}
n_sh = [len(members(f, "010")) for f in SH]
report(all(members(f, "010") <= five for f in SH) and max(n_sh) == 5,
       "010 in the Stag Hunt: up to five, among ALLD, Grim, DCCD, DDDC and DCCC (at most %d at a face)" % max(n_sh))
report(all(("ALLD" in members(f, "010")) == (not TgtS(f["u"], f["v"])) for f in SH),
       "010 in the Stag Hunt: ALLD among them exactly where T < S")
rule("010", lambda u, v, f: (members(f, "010") if f["q"] == "SH" else set())
     | ({"DDDC"} if f["q"] == "HA" and u < 0.5 else set())
     | ({"WSLS"} if square(u, v) and not below(u, v) else set()),
     "outside the Stag Hunt, DDDC in the Harmony games with 2S < R + P and WSLS alone on the part of the unit square "
     "above the switch line, and nobody else")
report(all(f["code"]["WSLS"] == ATOM["010"] for f in F if square(f["u"], f["v"]) and not below(f["u"], f["v"])),
       "on the part of the unit square above the switch line WSLS is stable but not efficient")
tot = sum(f["disk"] for f in F)
e010 = 100 * sum(f["disk"] for f in F if not members(f, "010")) / tot
report(round(e010) == 71, "010 is empty on 71%% of the disk (%.1f%%)" % e010)

# 001
n001 = [len(members(f, "001")) for f in F]
report((min(n001), max(n001)) == (2, 4) and all("TFT" in members(f, "001") for f in F),
       "001: between two and four strategies (%d to %d), tit-for-tat always among them" % (min(n001), max(n001)))

# 110
rule("110", lambda u, v, f: ({"ALLC", "CCCD", "WSLS"} if v < 0 and u < 1 and TgtS(u, v) else set())
     | ({"WSLS"} if (f["q"] == "PD" and v < 1) or (f["q"] == "SD" and square(u, v) and below(u, v))
        or (wedgeS(u, v) and u < 1) else set()),
     "all three mutual cooperators where T <= R, S <= R and T > S, and WSLS alone in the Prisoner's Dilemma with "
     "T < 2R - P, in the Snowdrift games of the unit square below the switch line, and on the wedge S with S < R")

# 011
rule("011", lambda u, v, f: ({"ALLD"} if u < 0 and TgtS(u, v) else set())
     | ({"Grim"} if u < 0 and TgtS(u, v) and 2 * u + 1 <= 0 else set())
     | ({"ALLC", "CCCD"} if f["q"] == "HA" and not below(u, v) else set()),
     "ALLD and Grim in the Prisoner's Dilemma and in the Stag Hunt with T > S, Grim only where 2S + R <= 3P, and ALLC "
     "and CCCD in the Harmony games above the switch line")
report(all(not TgtS(f["u"], f["v"]) for f in F if f["q"] == "HA" and not below(f["u"], f["v"])),
       "in the Harmony games above the switch line T < S")

# 111
rule("111", lambda u, v, f: {"ALLC", "CCCD"} if wedgeS(u, v) else set(),
     "ALLC and CCCD on the wedge S and nobody elsewhere")

print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
