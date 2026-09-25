#!/usr/bin/env python3
"""
Provenance of SIFigure1/, SITable1/ and SITable8/: compares what those folders compute or contain with the private
sources they were taken from.  It runs only in the author's environment (the one variable below) and reads those
sources without modifying them; nothing in the three folders depends on it.

    python3 -B check_sources.py <manuscript>

<manuscript> is the folder of the paper's LaTeX source: it holds ms.tex and the published figures in figures/.

It checks, and prints:
  1. SITable8/sitable8.py reproduces the pair limits W of the original m1atoms.py (FinalFigures/, the script that
     wrote Figures/m1_atoms_k4.npz, the memory-one arrangement behind Figures 1b, 2a-g and 3a-d) exactly, and the
     atom codes of all sixteen strategies on each of the 45 faces of m1_atoms_k4.npz, and its eleven lines;
  2. the stability regions of SITable8 (computed against the 16 memory-one co-players) equal, strategy by strategy,
     those of the exact memory-two census of the companion paper (BinM2NE1 ca1_regions.csv, the census the paper's
     stability regions are taken from, computed against all 65536 memory-two co-players), and so do the self-play
     weights;
  3. the copies of SI Tables 1 and 8 inside sitable1.py and sitable8.py equal the tables as typeset in ms.tex;
  4. SIFigure1/SIFig1.tex differs from FinalFigures/SI/SIFig1.tex in comment lines only, and SIFigure1/SIFig1.pdf is
     byte-identical to the published figures/SI/SIFig1.pdf.
"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True

# ---- author's environment: the root under which the private sources live (read only) ----
AUTHOR_ROOT = "/Users/martin/Documents"
# -------------------------------------------------------------------------------------------
if len(sys.argv) != 2 or not os.path.isfile(os.path.join(sys.argv[1], "ms.tex")):
    sys.exit("usage: python3 -B check_sources.py <manuscript folder holding ms.tex and figures/>")
MANUSCRIPT = sys.argv[1]

PR1 = os.path.join(AUTHOR_ROOT, "CL1", "PartnersRivals1")
M1ATOMS_DIR = os.path.join(PR1, "FinalFigures")                               # m1atoms.py
M1NPZ = os.path.join(AUTHOR_ROOT, "CL1", "PartnersRivals", "Figures", "m1_atoms_k4.npz")
CENSUS = os.path.join(AUTHOR_ROOT, "CL", "BinM2NE1", "Final", "Github", "exact", "ca1_regions.csv")
MSTEX = os.path.join(MANUSCRIPT, "ms.tex")
SIFIG1_TEX = os.path.join(PR1, "FinalFigures", "SI", "SIFig1.tex")
SIFIG1_PDF = os.path.join(MANUSCRIPT, "figures", "SI", "SIFig1.pdf")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, os.pardir, os.pardir)
sys.path.insert(0, os.path.join(REPO, "SITable8"))
sys.path.insert(0, os.path.join(REPO, "SITable1"))
import sitable8 as T8                                                           # noqa: E402
import sitable1 as T1                                                           # noqa: E402
from fractions import Fraction as F                                             # noqa: E402

ok_all = True


def report(ok, text):
    global ok_all
    ok_all &= bool(ok)
    print("  %s  %s" % ("ok  " if ok else "FAIL", text))


print("1. against the original m1atoms.py and m1_atoms_k4.npz")
sys.path.insert(0, M1ATOMS_DIR)
import m1atoms                                                                  # noqa: E402
import numpy as np                                                              # noqa: E402
report(all(m1atoms.W[k] == T8.W[k] for k in T8.W), "the 256 exact pair limits are identical")
Z = np.load(M1NPZ, allow_pickle=False)
codes, uvc = Z["codes"], Z["uvc"]
bad = 0
for f in range(len(codes)):
    u, v = F(float(uvc[f, 0])), F(float(uvc[f, 1]))
    for i in range(16):
        e = (i in T8.EFF_LO and u + v < 1) or (i in T8.EFF_HI and u + v > 1)
        r = (i in T8.RIVP and u - v < 1) or (i in T8.RIVM and u - v > 1)
        bad += codes[f, i] != 4 * e + 2 * T8.inside(T8.NASH[i], (u, v)) + r
report(bad == 0 and len(codes) == 45, "the atom codes of the 16 on all %d faces of m1_atoms_k4.npz follow from the regions of SI Table 8"
       % len(codes))
mine = sorted(tuple(int(x) for x in m1atoms.normalise(F(a), F(b), F(-c))) for a, b, c in
              [(1, 0, -1), (2, 0, -1), (1, 0, 0), (2, 0, 1), (1, 0, 1), (0, 1, -1), (0, 2, -1), (0, 1, 0), (0, 1, 1), (1, 1, 1), (1, -1, 1)])
report(sorted(map(tuple, Z["lines"].tolist())) == mine, "its eleven lines are u=-1,-1/2,0,1/2,1; v=-1,-1/2,0,1; u+v=1; u-v=1")

print("2. against the exact memory-two census (BinM2NE1 ca1_regions.csv, vs all 65536 co-players)")
import csv                                                                      # noqa: E402
ids = {15 * sum(((s >> k) & 1) << (4 * k) for k in range(4)): s for s in range(16)}
seen = 0
for row in csv.DictReader(open(CENSUS)):
    g = int(row["genotype"])
    if g not in ids:
        continue
    s = ids[g]
    seen += 1
    d = int(row["dim"])
    if d == 2:
        cons = [tuple(F(int(x)) for x in t.split(",")) for t in row["facets"].split(";")]        # a + b u + c v <= 0
        reg = T8.region(cons)
    elif d == 1:
        A, C, E = (F(int(x)) for x in row["line"].split(","))                                    # A u + C v = E
        cons = [(-E, A, C), (E, -A, -C)]
        x = (1, 0) if C != 0 else (0, 1)                                                         # the parameter: u, else v
        if row["x0"]:
            cons.append((F(row["x0"]), -F(x[0]), -F(x[1])))                                     # x >= x0
        if row["x1"]:
            cons.append((-F(row["x1"]), F(x[0]), F(x[1])))                                      # x <= x1
        reg = T8.region(cons)
    elif d == 0:
        reg = [(F(row["pu"]), F(row["pv"]))]
    else:
        reg = []
    selfw = tuple(F(int(row["w%d" % k]), int(row["wden"])) for k in range(4))
    same = reg == T8.NASH[s] and selfw == T8.SELF[s]
    print("       %s  census dim %2d: %-22s %s" % (T8.genome(s), d, T8.describe(reg), "same" if same else "DIFFERENT"))
    ok_all &= same
report(seen == 16, "all sixteen found in the census; stability regions and self-play weights compared above")

print("3. the copies of the printed tables")
tex = open(MSTEX).read()
report(T8.paper_rows(tex) == T8.paper_rows(T8.PAPER), "SI Table 8 in sitable8.py = SI Table 8 in ms.tex")
report(T1.paper_rows(tex) == T1.paper_rows(T1.PAPER), "SI Table 1 in sitable1.py = SI Table 1 in ms.tex")

print("4. SI Figure 1")
strip = lambda path: [l for l in open(path).read().splitlines() if not l.lstrip().startswith("%")]
report(strip(os.path.join(REPO, "SIFigure1", "SIFig1.tex")) == strip(SIFIG1_TEX),
       "SIFig1.tex = FinalFigures/SI/SIFig1.tex apart from comment lines")
md5 = lambda path: hashlib.md5(open(path, "rb").read()).hexdigest()
report(md5(os.path.join(REPO, "SIFigure1", "SIFig1.pdf")) == md5(SIFIG1_PDF),
       "SIFig1.pdf = the published figures/SI/SIFig1.pdf (md5 %s)" % md5(SIFIG1_PDF))

print("\n%s" % ("all provenance checks pass" if ok_all else "SOME PROVENANCE CHECKS FAIL"))
sys.exit(0 if ok_all else 1)
