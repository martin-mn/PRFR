#!/usr/bin/env python3
"""sitable5.py -- SI Table 5, where the four atoms that can be empty at memory two have members, recomputed.

    python3 sitable5.py          prints the table next to the paper's, writes SITable5.csv; exit status 1 on a mismatch
                                 (about 1 s; numpy only)

Input: the exact eps -> 0 arrangement of the stability regions of the memory-two strategies, deposited in ../data/arrangement/ (not by this
folder): m2_faces.csv (per face an interior game (u, v) and the seven atom counts A_000 ... A_111), the face polygons
m2_faces_k4.npz, and m2_strategies.csv (for the atom totals on an open set, printed with the text checks).  The atom
counts of a face combine the face's stable strategies (imported from the exact map of the Nash equilibria of the
companion work) with the efficient set of
its side of the switch line and the competitive set of its side of T = S (data/census/).

The switch line u+v = 1, the line T = S (u-v = 1) and the two axes u = 0, v = 0 are all lines of the arrangement, so
every face lies in one of the pieces cut by them; the script asserts this vertex by vertex.  An entry of the table is
"all" if the atom is non-empty on every face of the piece, "none" if on no face, "part" otherwise.  Faces are open
2-cells; the lines between them, of measure zero, are not games of any face.  The text of SI section 8 about the
table (where each atom is empty, the bays of 110, the ranges and totals) is checked as well.
Games are (R, S, T, P) = (1, u, 1 + v, 0).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, ROOT)
from common import disk                                      # noqa: E402
from common.tables import read_table, write_table           # noqa: E402

ARR = os.path.join(ROOT, "data", "arrangement")             # the deposited arrangement (read only)
FACES_CSV, FACES_NPZ, STRAT_CSV = "m2_faces.csv", "m2_faces_k4.npz", "m2_strategies.csv"

ATOMS = ["100", "010", "011", "110"]
# SI Table 5 as printed in ms.tex: (wedge, quadrant) -> entries for 100, 010, 011, 110
PAPER = [
    ("W", "PD", "all", "part", "all", "part"),
    ("W", "SH", "none", "all", "all", "all"),
    ("W", "SD", "all", "all", "all", "all"),
    ("W", "HA", "none", "all", "part", "all"),
    ("S", "SH", "none", "all", "none", "all"),
    ("S", "HA", "part", "part", "none", "part"),
    ("E", "SD", "all", "none", "none", "all"),
    ("E", "HA", "all", "part", "all", "part"),
    ("N", "PD", "all", "part", "all", "part"),
    ("N", "SD", "all", "part", "none", "all"),
]

ok = True


def check(label, got, want):
    global ok
    same = got == want
    ok &= bool(same)
    print("  %-86s %s" % (label, "agrees" if same else "DIFFERS: %s, paper %s" % (got, want)))


def quadrant(u, v):
    return np.where((u < 0) & (v > 0), "PD", np.where((u > 0) & (v > 0), "SD",
                    np.where((u < 0) & (v < 0), "SH", np.where((u > 0) & (v < 0), "HA", "??"))))


def wedge(u, v):
    a, b = u + v < 1, u - v < 1
    return np.where(a & b, "W", np.where(a & ~b, "S", np.where(~a & ~b, "E", "N")))


T = read_table(os.path.join(ARR, FACES_CSV))
nf = len(T["face"])
u, v = T["u"], T["v"]
A = {c: T["A_" + c] for c in ["000", "100", "010", "001", "110", "011", "111"]}
q, w = quadrant(u, v), wedge(u, v)
print("the arrangement drawn as %d polygons (data/arrangement/%s)" % (nf, FACES_CSV))
check("no interior game on an axis; quadrant and wedge as in m2_faces.csv",
      (bool((q != "??").all()), bool((q == T["quadrant"]).all()), bool((w == T["wedge"]).all())), (True, True, True))
check("the seven atom counts add up to 65536 on every face", bool((sum(A.values()) == 65536).all()), True)

# every face lies on one side of each of the four lines: test all vertices against the interior game's side
Z = np.load(os.path.join(ARR, FACES_NPZ), allow_pickle=False)
V, OFF = Z["verts"], Z["offsets"]
assert len(OFF) == nf + 1 and float(Z["K"]) == disk.K
P = disk.plane(V)                                                    # the vertices as games
fid = np.repeat(np.arange(nf), np.diff(OFF))
tol = 1e-6 * (1.0 + np.abs(P).max(1))


def straddling(lines):
    """the number of face vertices on the other side of a line a u + b v = c than the face's interior game"""
    bad = 0
    for a, b_, c in lines:
        s = np.sign(a * u + b_ * v - c)[fid]
        bad += int((s * (a * P[:, 0] + b_ * P[:, 1] - c) < -tol).sum())
    return bad


check("no face straddles the switch line, T = S or an axis (vertices on the wrong side)",
      straddling([(1, 0, 0), (0, 1, 0), (1, 1, 1), (1, -1, 1)]), 0)
# the lines of the bays of 110 below: v = 2, u + 2v = 2, 3u + v = -1, u + 3v = -1, u = 6, 5u + 4v = 6
check("nor any of the six lines that bound the bays of 110 (so an interior game decides a face)",
      straddling([(0, 1, 2), (1, 2, 2), (3, 1, -1), (1, 3, -1), (1, 0, 6), (5, 4, 6)]), 0)

# the efficiency and rivalry sides of the arrangement are those of the census (data/census/census.csv)
sys.path.insert(0, os.path.join(ROOT, "census"))
import censuslib as cl                                       # noqa: E402
M = cl.masks(cl.load())
S = read_table(os.path.join(ARR, STRAT_CSV))
check("m2_strategies.csv: eff_cc, eff_alt, riv_plus, riv_minus are those of data/census",
      [bool((S[a].astype(bool) == M[b]).all()) for a, b in
       (("eff_cc", "eff_cc"), ("eff_alt", "eff_alt"), ("riv_plus", "riv_p"), ("riv_minus", "riv_m"))], [True] * 4)
check("on every face the efficient atoms hold 7639 (below the switch line) or 3072 (above)",
      bool(((A["100"] + A["110"] + A["111"]) == np.where(u + v < 1, int(M["eff_cc"].sum()),
                                                            int(M["eff_alt"].sum()))).all()), True)
check("on every face the competitive atoms hold the 2640 rivals of its side of T = S",
      bool(((A["001"] + A["011"] + A["111"]) == np.where(u - v < 1, int(M["riv_p"].sum()),
                                                            int(M["riv_m"].sum()))).all()), True)
FR = {k: int(m.sum()) for k, m in cl.wedges(M).items()}
check("on every face the friendly rivals (111) are those of its wedge, 8 / 1519 / 80 / 80",
      bool((A["111"] == np.array([FR[x] for x in w])).all()), True)

pieces = sorted(set(zip(w.tolist(), q.tolist())))
check("the four lines cut the plane into ten pieces", len(pieces), 10)
rows = []
for wd, qd, *_ in PAPER:
    m = (w == wd) & (q == qd)
    ent = []
    for c in ATOMS:
        k = int((A[c][m] > 0).sum())
        ent.append("all" if k == m.sum() else "none" if k == 0 else "part")
    rows.append((wd, qd) + tuple(ent) + (int(m.sum()),))

print("\nSI Table 5 (computed; the last column is the number of polygons of the piece)")
print("  wedge quadrant   100   010   011   110   polygons")
for r, p in zip(rows, PAPER):
    same = r[:6] == p
    ok &= same
    print("  %-5s %-8s %5s %5s %5s %5s %7d   %s" % (r + ("agrees" if same else "DIFFERS from %s" % (p[2:],),)))
check("the table covers every face", sum(r[6] for r in rows), nf)

print("\nThe text of SI section 8 ('The atoms of the three properties, and where they are empty')")
check("000, 001 and 111 have members at every game", [bool((A[c] > 0).all()) for c in ("000", "001", "111")],
      [True] * 3)
pat = set(zip(*[(A[c] == 0).tolist() for c in ATOMS]))
check("ten of the sixteen combinations of empty atoms occur", len(pat), 10)
check("none with 100 and 110 both empty", any(p[0] and p[3] for p in pat), False)
tot = {c: int(S["open_" + c].sum()) for c in ATOMS}
rng = {c: (int(A[c][A[c] > 0].min()), int(A[c][A[c] > 0].max())) for c in ATOMS}
# 100
check("100 is empty exactly where T <= R and S <= R (u <= 1, v <= 0)",
      bool(((A["100"] == 0) == ((u < 1) & (v < 0))).all()), True)
check("100 holds 10701 strategies on an open set, 1504 to 7631 at a game where not empty",
      (tot["100"],) + rng["100"], (10701, 1504, 7631))
# 011
check("011 is empty on the whole wedge S", bool((A["011"][w == "S"] == 0).all()), True)
check("... and on the Snowdrift quadrant above the switch line (N and E)",
      bool((A["011"][(q == "SD") & (u + v > 1)] == 0).all()), True)
check("... and non-empty on the rest of the plane outside a small patch of W in the Harmony quadrant",
      bool((A["011"][~((w == "S") | ((q == "SD") & (u + v > 1)) | ((w == "W") & (q == "HA")))] > 0).all()), True)
check("the stable rivals number 1519 at every game of the wedge S",
      bool(((A["011"] + A["111"])[w == "S"] == 1519).all()), True)
esd = (w == "E") & (q == "SD")
check("the Snowdrift part of E: no inefficient equilibrium on any of its 557 faces",
      (int(esd.sum()), bool(((A["010"] + A["011"])[esd] == 0).all())), (557, True))
check("011 holds 1721 strategies on an open set, 1 to 987 at a game", (tot["011"],) + rng["011"], (1721, 1, 987))
# 110
pd, ha = q == "PD", q == "HA"
bay_pd = (v > 2) & (u + 2 * v > 2) & (3 * u + v < -1)
check("110 empty in the PD exactly on v > 2, u + 2v > 2, 3u + v < -1",
      bool(((A["110"] == 0)[pd] == bay_pd[pd]).all()), True)
bay_ha = ((w == "E") & (u + 3 * v < -1)) | ((w == "S") & (u > 6) & (5 * u + 4 * v > 6))
check("110 empty in HA exactly on E with u + 3v < -1 and on S with u > 6, 5u + 4v > 6",
      bool(((A["110"] == 0)[ha] == bay_ha[ha]).all()), True)
check("110 empty nowhere else: its empty set is the two bays",
      bool(((A["110"] == 0) == ((pd & bay_pd) | (ha & bay_ha))).all()), True)
b = pd & bay_pd
check("beyond the three lines of the PD the only partners are the friendly rivals, 8 below, 80 above",
      (sorted(set((A["110"] + A["111"])[b & (u + v < 1)].tolist())),
       sorted(set((A["110"] + A["111"])[b & (u + v > 1)].tolist()))), ([8], [80]))
check("110 holds 9389 strategies on an open set, 6 to 7631 at a game where present",
      (tot["110"],) + rng["110"], (9389, 6, 7631))
# 010
check("010 has members on the whole Stag Hunt quadrant", bool((A["010"][q == "SH"] > 0).all()), True)
check("... and on the two small triangles of W with S > P (u > 0)",
      bool((A["010"][(w == "W") & (u > 0)] > 0).all()), True)
check("010 holds 16013 strategies on an open set, 2 to 14430 at a game", (tot["010"],) + rng["010"], (16013, 2, 14430))
print("  (not checked here, since they need the stable strategies of each face and not only their counts: the 843 witnesses of"
      "\n   010 in the Stag Hunt above T = S, the 96 and 10 alternator witnesses in the two triangles of W)")

write_table(os.path.join(HERE, "SITable5.csv"), {
    "wedge": [r[0] for r in rows], "quadrant": [r[1] for r in rows],
    "atom_100": [r[2] for r in rows], "atom_010": [r[3] for r in rows], "atom_011": [r[4] for r in rows],
    "atom_110": [r[5] for r in rows], "faces": [r[6] for r in rows]}, [
    "SI Table 5, recomputed by SITable5/sitable5.py from the arrangement in data/arrangement/ (m2_faces.csv).",
    "wedge: W (u+v<1, u-v<1), S (u+v<1, u-v>1), E (u+v>1, u-v>1), N (u+v>1, u-v<1); quadrant: PD (u<0<v),",
    "SH (u,v<0), SD (u,v>0), HA (v<0<u).  atom_xyz: whether the atom xyz (efficient-stable-competitive) has members",
    "on all, part or none of the faces of the piece.  faces: the number of polygons of data/arrangement/m2_faces.csv in the piece",
    "(the drawing's 27598 polygons, bands of the 22872 faces; see data/arrangement/README.md)."])
print("\nwrote SITable5.csv")
print("ALL AGREE" if ok else "DISAGREEMENT FOUND")
sys.exit(0 if ok else 1)
