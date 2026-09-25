#!/usr/bin/env python3
"""
Writes data/arrangement/ from the author's working files: the exact eps -> 0 arrangements behind Figures 1, 2 and 3.

    python3 reduce.py            (about 15 s; run in the author's environment only, see AUTHOR_ENV)

This script is the record of how the deposited tables were made.  It is not needed to reproduce the figures: the
figure scripts and data/arrangement/check.py read only data/arrangement/.

Sources (all under AUTHOR_ENV):

  CL1/PartnersRivals/Figures/ca4_arrangement_k4.npz
      the arrangement of the companion work (NEmap; github.com/martin-mn/MapBinM2, Figure3/ca4_arrangement_k4.npz,
      byte-identical): the 27598 polygons on the K = 4 disk (verts, offsets) with the number of stable strategies N
      and of efficient stable strategies NEFF on each.  Built by MapBinM2's Figure3/computation/arrangement/p3disk.py
      from the 254 facet lines of the exact stability polygons: the lines cut the plane into 22872 cells, and 771 of
      these were cut further into bands of a mean-efficiency field that the companion paper draws, so that the dump
      holds 27598 polygons, each inside one cell.
  CL1/PartnersRivals/Figures/Count6_faces.npz
      the per-face counts of the eight atoms (ATOMS, 27598 x 8, by code 4e + 2n + c), and ATOM_TOTAL, NE_TOTAL,
      computed by CL1/PartnersRivals/Figures/count6.py with DiskM2WF/Opt/exact.masks at one interior game of each
      face (the same interior game as below).
  CL1/PartnersRivals/Figures/m2_masks.npz
      efficiency and rivalry of the 65536 memory-two strategies in the limit (the first computation, 2026-09-03, with
      PartnersRivals/check/pairs.c, which is byte-identical to census/pairs.c; data/census/m2_masks.npz, from the
      exact census, is bit-identical to it).
  CL/BinM2NE1/Final/Github/exact/ca1_regions.csv
      the exact stability region of every memory-two strategy (NEmap's census; MapBinM2 exact/ca1_regions.csv): its
      dimension and, for dimension 2, the integer facets (a, b, c) of the convex polygon a + b u + c v <= 0; for
      dimension 1 the line and the interval; for dimension 0 the point.
  CL1/PartnersRivals/Figures/m1_atoms_k4.npz
      the memory-one arrangement, as FinalFigures/m1atoms.py wrote it (45 faces, the atom codes of the 16 strategies
      on each).  data/arrangement/m1atoms.py recomputes it from scratch and compares.

What is written (data/arrangement/, see its README.md): m2_faces_k4.npz, m2_faces.csv, m2_cells.csv, m2_lines.csv,
m2_strategies.csv, m2_nash_facets.csv, m2_nash_lowdim.csv, m1_faces_k4.npz, m1_faces.csv, m1_lines.csv, cases.csv.

Every per-face number written is recomputed here from the combinatorial description (the side of each cell of every
line, and the facets of every strategy's stability polygon), and asserted equal to the dump's N and NEFF and to Count6's
ATOMS, before anything is written.
"""
import csv
import os
import sys
from math import gcd

import numpy as np

# ---------------------------------------------------------------------------------------------------------------
# AUTHOR'S ENVIRONMENT: the one place where this repository points outside itself.  Nothing else reads these files.
AUTHOR_ENV = "/Users/martin/Documents"
# ---------------------------------------------------------------------------------------------------------------
FIGSRC = os.path.join(AUTHOR_ENV, "CL1", "PartnersRivals", "Figures")
CA1 = os.path.join(AUTHOR_ENV, "CL", "BinM2NE1", "Final", "Github", "exact", "ca1_regions.csv")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir)
OUT = os.path.join(ROOT, "data", "arrangement")
sys.path.insert(0, ROOT)
from common import atoms, tables                                   # noqa: E402
from common.geometry import polyarea                               # noqa: E402

K = 4.0
ORDER = atoms.ORDER
NC = 65536


def plane(q):
    """fig1.py's / count6.py's inverse map, disk -> game"""
    q = np.atleast_2d(np.asarray(q, float)); r2 = (q ** 2).sum(1)
    return q * (K / np.sqrt(np.maximum(1.0 - r2, 1e-12)))[:, None]


def interior(f):
    """fig1.py's / count6.py's interior game of a face: generic convex weights of its plane vertices"""
    p = plane(f); w = 1.0 + 0.1 * np.sin(np.arange(len(p)) + 1.0)
    return (p * w[:, None]).sum(0) / w.sum()


def line_of(a, b, c):
    """the facet a + b u + c v <= 0 as (line (A, B, C) with A u + B v = C, gcd 1, (A, B, C) > (-A, -B, -C)),
    bit): the facet holds strictly exactly where the sign bit of the line, [A u + B v > C], equals bit"""
    A, B, C = b, c, -a
    q = gcd(gcd(abs(A), abs(B)), abs(C)) or 1
    A, B, C = A // q, B // q, C // q
    s = 1
    if (A, B, C) < (-A, -B, -C):
        A, B, C, s = -A, -B, -C, -1
    # s (A u + B v - C) <= 0: strictly, A u + B v - C has the sign -s
    return (A, B, C), (1 if -s > 0 else 0)


def genome(g):
    """the paper's genome: position j from the left is the answer at state j (1 = C)"""
    return "".join("1" if (g >> j) & 1 else "0" for j in range(16))


# =============================================================================== memory two
Z = np.load(os.path.join(FIGSRC, "ca4_arrangement_k4.npz"), allow_pickle=False)
assert float(Z["K"]) == K and not Z["EMPTY"].any()
V, OFF = Z["verts"], Z["offsets"]
NF = len(OFF) - 1
FACES = [V[OFF[i]:OFF[i + 1]] for i in range(NF)]
C6 = np.load(os.path.join(FIGSRC, "Count6_faces.npz"), allow_pickle=False)
M = np.load(os.path.join(FIGSRC, "m2_masks.npz"), allow_pickle=False)
effCC, effALT, rivP, rivM = (M[k].astype(bool) for k in ("effCC", "effALT", "rivP", "rivM"))
R1 = list(csv.DictReader(open(CA1)))
assert len(R1) == NC and all(int(r["genotype"]) == g for g, r in enumerate(R1))
dim = np.array([int(r["dim"]) for r in R1])
Wself = np.array([[int(r["w%d" % i]) for i in range(4)] for r in R1])
# efficiency from NEmap's own self-play distributions agrees with pairs.c
assert (((Wself[:, 1] == 0) & (Wself[:, 2] == 0) & (Wself[:, 3] == 0)) == effCC).all()
assert (((Wself[:, 0] == 0) & (Wself[:, 3] == 0) & (Wself[:, 1] == Wself[:, 2]) & (Wself[:, 1] > 0)) == effALT).all()

# ---- the lines and the facets
FAC = {}                                     # genotype -> [(a, b, c, (A, B, C), bit)]
LINES = set()
for g, r in enumerate(R1):
    if r["dim"] == "2":
        FAC[g] = []
        for h in r["facets"].split(";"):
            a, b, c = (int(x) for x in h.split(","))
            ln, bit = line_of(a, b, c)
            FAC[g].append((a, b, c, ln, bit))
            LINES.add(ln)
LINES = sorted(LINES)
LI = {ln: j for j, ln in enumerate(LINES)}
NL = len(LINES)
assert NL == 254 and (1, 1, 1) in LI and (1, -1, 1) in LI
LA = np.array(LINES, dtype=np.int64)
print("%d strategies with a two-dimensional stability polygon, %d facets on %d distinct lines"
      % (len(FAC), sum(len(v) for v in FAC.values()), NL))

# ---- the side of every face of every line, from all its drawn vertices mapped back to the plane
P = plane(V)
fid = np.repeat(np.arange(NF), np.diff(OFF))
val = P @ LA[:, :2].T.astype(float) - LA[:, 2].astype(float)[None, :]
scale = (1.0 + np.abs(P).sum(1))[:, None] * np.abs(LA[:, :2]).sum(1)[None, :] + np.abs(LA[:, 2])[None, :]
rel = val / scale
mx = np.full((NF, NL), -np.inf); mn = np.full((NF, NL), np.inf)
np.maximum.at(mx, fid, rel); np.minimum.at(mn, fid, rel)
TOL = 1e-9
assert not ((mx > TOL) & (mn < -TOL)).any(), "a face crosses a line"
assert ((mx > TOL) | (mn < -TOL)).all(), "a face lies on a line"
SIGN = mx > TOL                                                   # (NF, NL) bool: A u + B v > C on the face
print("every face lies strictly on one side of each of the %d lines (largest excursion across a line: %.1e, relative)"
      % (NL, np.minimum(mx, -mn).max()))
UVC = np.array([interior(f) for f in FACES])
iv = UVC @ LA[:, :2].T.astype(float) - LA[:, 2].astype(float)[None, :]
assert ((iv > 0) == SIGN).all(), "an interior game is not on its face's side of a line"

# ---- the cells: the distinct sign vectors, numbered by first appearance
key = [s.tobytes() for s in np.packbits(SIGN, axis=1)]
cid, CELLS = {}, []
CELL = np.zeros(NF, np.int64)
for f, k in enumerate(key):
    if k not in cid:
        cid[k] = len(CELLS); CELLS.append(f)
    CELL[f] = cid[k]
NCELL = len(CELLS)
assert NCELL == 22872
print("%d faces in %d cells of the arrangement of the %d lines" % (NF, NCELL, NL))

# ---- the stable strategies on every face, the counts, the atoms
fs_id, fs_list = {}, []
for g, fl in FAC.items():
    k = tuple(sorted((LI[ln], bit) for a, b, c, ln, bit in fl))
    if k not in fs_id:
        fs_id[k] = len(fs_list); fs_list.append(k)
GK = np.full(NC, -1)
for g, fl in FAC.items():
    GK[g] = fs_id[tuple(sorted((LI[ln], bit) for a, b, c, ln, bit in fl))]
NEK = np.ones((NF, len(fs_list)), bool)
for i, k in enumerate(fs_list):
    for j, bit in k:
        NEK[:, i] &= SIGN[:, j] == bool(bit)
below = ~SIGN[:, LI[(1, 1, 1)]]                                   # u + v < 1
tgs = ~SIGN[:, LI[(1, -1, 1)]]                                    # u - v < 1, T > S
grp = {}
for g in range(NC):
    t = (GK[g], effCC[g], effALT[g], rivP[g], rivM[g])
    grp.setdefault(t, []).append(g)
N = np.zeros(NF, np.int64); PART = np.zeros(NF, np.int64); A8 = np.zeros((NF, 8), np.int64)
OPEN = np.zeros((NC, 8), bool)                                    # strategy in atom (by code) on some face
for (k, ec, ea, rp, rm), gs in grp.items():
    n = len(gs)
    ne = NEK[:, k] if k >= 0 else np.zeros(NF, bool)
    ef = np.where(below, ec, ea); rv = np.where(tgs, rp, rm)
    code = 4 * ef + 2 * ne + rv
    N += n * ne; PART += n * (ne & ef)
    for c in range(8):
        A8[:, c] += n * (code == c)
    for c in np.unique(code):
        OPEN[np.array(gs), c] = True
assert (N == Z["N"]).all() and (PART == Z["NEFF"]).all(), "N / NEFF differ from the dump"
assert (A8 == C6["ATOMS"]).all(), "the atoms differ from Count6_faces.npz"
assert (OPEN.sum(0) == C6["ATOM_TOTAL"]).all() and OPEN[:, [2, 3, 6, 7]].any(1).sum() == int(C6["NE_TOTAL"])
assert not A8[:, 5].any() and (A8.sum(1) == NC).all()
print("recomputed on every face from the facets and the sides: N and NEFF equal the dump's, the eight atom counts "
      "equal Count6_faces.npz; totals %s" % OPEN.sum(0))

# ---- cases (a key per face: which of the seven atoms of ORDER are non-empty), numbered with memory one below
def keys(A):
    present = np.stack([A[:, int(c, 2)] > 0 for c in ORDER], 1)
    return np.array(["".join("1" if x else "0" for x in row) for row in present])


KEY2 = keys(A8)
DA2 = np.array([polyarea(f) for f in FACES]); DA2 /= DA2.sum()

# =============================================================================== memory one
Z1 = np.load(os.path.join(FIGSRC, "m1_atoms_k4.npz"), allow_pickle=False)
assert float(Z1["K"]) == K
V1, OFF1 = Z1["verts"], Z1["offsets"]
NF1 = len(OFF1) - 1
CODES1, ATOMS1, UVC1 = Z1["codes"], Z1["atoms"], Z1["uvc"]
assert (ATOMS1 == np.array([np.bincount(c, minlength=8) for c in CODES1])).all()
KEY1 = keys(ATOMS1)
DA1 = Z1["diskarea"] / Z1["diskarea"].sum()

area1 = {k: DA1[KEY1 == k].sum() for k in set(KEY1)}
area2 = {k: DA2[KEY2 == k].sum() for k in set(KEY2)}
CASES = sorted(set(KEY1) | set(KEY2), key=lambda k: (k.count("0"), -(area1.get(k, 0) + area2.get(k, 0))))
assert len(CASES) == 19 and len(set(KEY1)) == 12 and len(set(KEY2)) == 10 and len(set(KEY1) & set(KEY2)) == 3
NUM = {k: i + 1 for i, k in enumerate(CASES)}

# =============================================================================== write
os.makedirs(OUT, exist_ok=True)
CONV = ["Conventions: a game is (R, S, T, P) = (1, u, 1 + v, 0); the limit eps -> 0.  An atom is written",
        "efficient-stable-competitive; A_xyz is the number of strategies in atom xyz, in the order 000 100 010 001 110 011",
        "111 (the atom 101 is empty everywhere, so the seven add up to the number of strategies)."]

# ---- memory two: geometry
np.savez_compressed(os.path.join(OUT, "m2_faces_k4.npz"), verts=V, offsets=OFF, K=np.array(K))

# ---- memory two: lines
name = {(1, 1, 1): "switch", (1, -1, 1): "TeqS", (1, 0, 1): "u=1", (0, 1, 0): "v=0"}
tables.write_table(os.path.join(OUT, "m2_lines.csv"), {
    "line": np.arange(NL), "A": LA[:, 0], "B": LA[:, 1], "C": LA[:, 2],
    "nfacets": [sum(1 for fl in FAC.values() for x in fl if x[3] == ln) for ln in LINES],
    "name": [name.get(ln, "-") for ln in LINES]}, [
    "The 254 lines of the memory-two arrangement: every line that carries a facet of the stability polygon of some",
    "binary memory-two strategy (m2_nash_facets.csv), in the limit eps -> 0 (the exact census of NEmap).",
    "line: index 0..253, the bit position in m2_cells.csv.  A, B, C: integers, gcd 1, the line A u + B v = C,",
    "normalised so that (A, B, C) is lexicographically larger than (-A, -B, -C).  nfacets: how many strategies'",
    "polygons have a facet on the line.  name: switch = u + v = 1 (S + T = 2R), TeqS = u - v = 1 (T = S),",
    "u=1 (S = R), v=0 (T = R), '-' otherwise."])

# ---- memory two: cells
def hexbits(row):
    x = 0
    for j in np.nonzero(row)[0]:
        x |= 1 << int(j)
    return "0x%064x" % x


tables.write_table(os.path.join(OUT, "m2_cells.csv"), {
    "cell": np.arange(NCELL), "sides": [hexbits(SIGN[f]) for f in CELLS]}, [
    "The 22872 cells of the arrangement of the 254 lines of m2_lines.csv over the plane of games (u, v).  A cell is",
    "an open convex region on which no line vanishes; it is identified by its sign vector.",
    "cell: index 0..22871 (numbered by first appearance in m2_faces.csv).",
    "sides: the sign vector as a hexadecimal integer, 0x followed by 64 hex digits: bit j (value 2^j) is 1 if",
    "A_j u + B_j v > C_j on the cell and 0 if A_j u + B_j v < C_j, for line j of m2_lines.csv.",
    "Read it with int(s, 16) >> j & 1."])

# ---- memory two: faces
Q2, W2 = atoms.pieces(UVC)
A7 = A8[:, atoms.IDX]
cols = {"face": np.arange(NF), "cell": CELL, "u": UVC[:, 0], "v": UVC[:, 1], "quadrant": Q2, "wedge": W2,
        "nash": N, "partners": PART}
cols.update(tables.atom_columns("A", A7))
cols["case"] = [NUM[k] for k in KEY2]
tables.write_table(os.path.join(OUT, "m2_faces.csv"), cols, [
    "The 27598 polygons of the memory-two arrangement drawn in Figures 1c, 2h-n and 3e-h (they draw its 22872 faces, the",
    "cells of m2_cells.csv), in the order of m2_faces_k4.npz, with the counts over the 65536 binary memory-two",
    "strategies on each.  The columns call a polygon a face, as the companion drawing does.",
    CONV[0], CONV[1], CONV[2],
    "face: index 0..27597.  cell: the cell of m2_cells.csv the face lies in (a cell is one face, or, for 771 cells,",
    "several bands of it: the companion work cut them for a field it draws; every count below is constant on a cell).",
    "u, v: a game strictly inside the face (a convex combination of its vertices mapped to the plane, with the weights",
    "1 + 0.1 sin(j + 1) of fig1.py; repr of a double).  quadrant: PD (u < 0 < v), SD (u, v > 0), SH (u, v < 0), HA",
    "(v < 0 < u).  wedge: W (u+v < 1, u-v < 1), S (u+v < 1, u-v > 1), N (u+v > 1, u-v < 1), E (u+v > 1, u-v > 1).",
    "nash: the number of stable strategies on the face (299 to 22069).  partners: efficient and stable (8 to 7639).",
    "A_000 ... A_111: the atoms.  case: the case number of Figure 1 (cases.csv), the set of non-empty atoms."])

# ---- memory two: strategies, facets, low-dimensional stability regions
cols = {"genotype": np.arange(NC), "genome": [genome(g) for g in range(NC)],
        "eff_cc": effCC, "eff_alt": effALT, "riv_plus": rivP, "riv_minus": rivM,
        "nash_dim": dim, "nash_nfacets": [len(FAC.get(g, ())) for g in range(NC)]}
cols.update({"open_%s" % c: OPEN[:, int(c, 2)] for c in ORDER})
tables.write_table(os.path.join(OUT, "m2_strategies.csv"), cols, [
    "The 65536 binary memory-two strategies in the limit eps -> 0.",
    "genotype: the integer code sum_j c_j 2^j.  genome: the sixteen answers c_0 ... c_15 (1 = C, 0 = D) at the states",
    "j = 4 (most recent outcome) + (the outcome before), CC = 0, CD = 1, DC = 2, DD = 3; ALLC = 65535, ALLD = 0.",
    "eff_cc: limiting self-play is permanent mutual cooperation (efficient where u + v < 1; 7639 strategies).",
    "eff_alt: limiting self-play is perfect alternation (efficient where u + v > 1; 3072).",
    "riv_plus / riv_minus: a rival (competitive, never outearned by any memory-two co-player) where T > S / T < S",
    "(2640 each).  These four columns are computed in this paper (census/pairs.c; the masks of data/census/m2_masks.npz);",
    "eff_cc and eff_alt agree with the self-play distributions of NEmap's exact census.",
    "nash_dim: the dimension of the strategy's stability region in the plane of games (NEmap, ca1_regions.csv): 2 = a convex",
    "polygon with interior (its facets in m2_nash_facets.csv), 1 = a segment or ray of one line, 0 = one game (both in",
    "m2_nash_lowdim.csv), -1 = stable at no game.  nash_nfacets: the number of facets of the polygon (0 = the whole plane).",
    "open_xyz: 1 if the strategy is in atom xyz on some face of the arrangement (on an open set of games)."])
rows = [(g, a, b, c, LI[ln], bit) for g in sorted(FAC) for a, b, c, ln, bit in FAC[g]]
R = np.array(rows, dtype=np.int64)
tables.write_table(os.path.join(OUT, "m2_nash_facets.csv"), {
    "genotype": R[:, 0], "a": R[:, 1], "b": R[:, 2], "c": R[:, 3], "line": R[:, 4], "bit": R[:, 5]}, [
    "The stability polygons of the 23861 binary memory-two strategies whose stability region in the limit eps -> 0 has an",
    "interior (NEmap's exact census, ca1_regions.csv, facets exactly as recorded there): one row per facet.",
    "The strategy (genotype) is a Nash equilibrium, against all 65535 other memory-two strategies with ties admitted,",
    "exactly at the games (u, v) with a + b u + c v <= 0 for all its facets; a strategy without rows (nash_nfacets = 0",
    "in m2_strategies.csv) is stable everywhere.",
    "line: the line of m2_lines.csv that carries the facet.  bit: the side of that line on which the facet holds",
    "strictly, as the sign bit of m2_cells.csv (1: A u + B v > C).  So the strategy is stable on a cell exactly when",
    "the cell's bit of every one of its facets' lines equals the facet's bit."])
low = [(g, r) for g, r in enumerate(R1) if r["dim"] in ("0", "1")]


def lin(r, j):
    return int(r["line"].split(",")[j]) if r["line"] else 0


tables.write_table(os.path.join(OUT, "m2_nash_lowdim.csv"), {
    "genotype": [g for g, r in low], "dim": [int(r["dim"]) for g, r in low],
    "A": [lin(r, 0) for g, r in low], "C": [lin(r, 1) for g, r in low], "E": [lin(r, 2) for g, r in low],
    "x0": [r["x0"] if r["x0"] else "-inf" for g, r in low], "x1": [r["x1"] if r["x1"] else "inf" for g, r in low],
    "pu": [r["pu"] if r["pu"] else "-" for g, r in low], "pv": [r["pv"] if r["pv"] else "-" for g, r in low]}, [
    "The stability regions of measure zero (NEmap's exact census, ca1_regions.csv, as recorded there): the 3774 strategies",
    "that are Nash equilibria in the limit eps -> 0 only on part of one line, and the 4875 that are only at one game.",
    "They are stable on no face of the arrangement.",
    "dim 1: the games with A u + C v = E and x0 <= x <= x1, where x = u if C != 0 and x = v otherwise; x0, x1 are",
    "exact rationals p/q, -inf / inf for an unbounded end; A = C = E = 0 and pu, pv = '-' do not apply.",
    "dim 0: the single game (pu, pv), exact rationals; A = C = E = 0, x0, x1 do not apply."])

# ---- memory one
np.savez_compressed(os.path.join(OUT, "m1_faces_k4.npz"), verts=V1, offsets=OFF1, K=np.array(K))
Q1, W1_ = atoms.pieces(UVC1)
GEN1 = ["".join("C" if (s >> k) & 1 else "D" for k in range(4)) for s in range(16)]
cols = {"face": np.arange(NF1), "u": UVC1[:, 0], "v": UVC1[:, 1], "area": Z1["area"], "disk_area": Z1["diskarea"],
        "quadrant": Q1, "wedge": W1_}
cols.update(tables.atom_columns("A", ATOMS1[:, atoms.IDX]))
cols["case"] = [NUM[k] for k in KEY1]
cols.update({"code_%s" % GEN1[s]: CODES1[:, s] for s in range(16)})
tables.write_table(os.path.join(OUT, "m1_faces.csv"), cols, [
    "The 45 faces of the memory-one arrangement drawn in Figures 1b, 2a-g and 3a-d, in the order of the polygons of",
    "m1_faces_k4.npz, with the atom of each of the 16 binary memory-one strategies on each face.  Computed exactly, in",
    "rational arithmetic, by m1atoms.py (which rebuilds it and compares).",
    CONV[0], CONV[1], CONV[2],
    "face: index 0..44.  u, v: a rational game strictly inside the face (as a double).  area: the plane area of the",
    "face within |u|, |v| <= 2000.  disk_area: the area of its polygon on the K = 4 disk.  quadrant, wedge: as in",
    "m2_faces.csv.  A_000 ... A_111: the atoms.  case: the case number of Figure 1 (cases.csv).",
    "code_XXXX: the atom code 4 efficient + 2 stable + competitive (0..7) of the strategy XXXX, written by its answers",
    "after CC, CD, DC, DD (own action first): ALLC = CCCC, ALLD = DDDD, TFT = CDCD, WSLS = CDDC, Grim = CDDD."])
L1 = Z1["lines"]
tables.write_table(os.path.join(OUT, "m1_lines.csv"), {"a": L1[:, 0], "b": L1[:, 1], "c": L1[:, 2]}, [
    "The 11 lines of the memory-one arrangement (m1atoms.py): a u + b v + c = 0, integers with gcd 1.  Across no other",
    "line does the atom of any of the 16 strategies change on an open set of games."])

# ---- cases
cols = {"case": [NUM[k] for k in CASES]}
cols.update({"present_%s" % c: [int(k[i]) for k in CASES] for i, c in enumerate(ORDER)})
cols.update({"m1_faces": [int((KEY1 == k).sum()) for k in CASES], "m1_share": [float(area1.get(k, 0.0)) for k in CASES],
             "m2_faces": [int((KEY2 == k).sum()) for k in CASES], "m2_share": [float(area2.get(k, 0.0)) for k in CASES]})
tables.write_table(os.path.join(OUT, "cases.csv"), cols, [
    "The 19 cases of Figure 1: a case is the set of atoms that are non-empty at a game.  Twelve occur at memory one,",
    "ten at memory two, three at both; they are numbered once, by the number of empty atoms and then by the total",
    "share of the two disks, as fig1.py numbers them.",
    "present_xyz: 1 if atom xyz is non-empty in the case.  m1_faces, m2_faces: the number of faces of the case;",
    "m1_share, m2_share: the share of the disk's area (repr of a double; 0 where the case does not occur)."])

for f in sorted(os.listdir(OUT)):
    print("  %9d  data/arrangement/%s" % (os.path.getsize(os.path.join(OUT, f)), f))
