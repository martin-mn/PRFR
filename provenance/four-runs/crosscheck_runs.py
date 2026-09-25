#!/usr/bin/env python3
"""
An independent second reduction of the four runs, checked against the deposited tables (author's environment only).

    python3 -B crosscheck_runs.py

reduce_runs.py wrote data/runs/ through the loader of the published figures (FinalFigures/wfdata.py: for memory two
figF4.collect, which classifies every strategy with DiskM2WF/Opt/exact.py).  This script does not use that loader
or that classification.  It reads the packed runs with its own parser and classifies with a second, independently
built table:

  memory two   the .idx/.bin packs parsed here; the atom of every strategy at every game from
               PartnersRivals/Cannon/atoms512.bin (512 x 65536 atom codes, written by Cannon/mkatoms.py for the
               robustness kits c1-c4, eh, el, f1, f2 and lm).  S = bincount(atom, weights = pi), exactly as the
               pack.py of those kits does it.
  memory one   the atoms of m1_strategy_atoms.csv compared with atoms512.bin at the sixteen memory-one strategies
               embedded as memory-two strategies (the answer after the last round repeated for every round before:
               genome bit 4 o + o' = bit o of the memory-one index).

It then compares S (to rounding: the summation order differs), N, E, pay, emax, neff, maxpi and top, and the
isl and seed columns against the kits' own summary lines.  Nothing is written.
"""
import os
import sys

# ------------------------------------------------------------------------------------------------------------------
AUTHOR_ENV = "/Users/martin/Documents/CL1"      # AUTHOR'S ENVIRONMENT: the private full outputs live under it
# ------------------------------------------------------------------------------------------------------------------
M2DATA = os.path.join(AUTHOR_ENV, "DiskM2WF", "Data")
ATOMS = os.path.join(AUTHOR_ENV, "PartnersRivals", "Cannon", "atoms512.bin")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
RUNS = os.path.join(REPO, "data", "runs")
sys.path.insert(0, REPO)

import numpy as np                                                   # noqa: E402

from common import atoms, games, tables                              # noqa: E402

IDX = atoms.IDX
NC = 65536


def m2_pack(stem):
    """{ipt: (gid, isl, emax, pay, ef, pi (65536,) float64)} for the sunflower games of a packed memory-two run"""
    rows = [l.split() for l in open(os.path.join(M2DATA, stem + ".idx")) if not l.startswith("#")]
    blob = np.fromfile(os.path.join(M2DATA, stem + ".bin"), dtype="<f4").reshape(len(rows), NC)
    out = {}
    for k, r in enumerate(rows):
        if not r[2].startswith("V_p"):
            continue
        ipt = int(r[2][3:6])
        p = blob[k].astype(np.float64)
        out[ipt] = (int(r[0]), int(r[1]), float(r[8]), float(r[9]), float(r[10]), p / p.sum())
    assert sorted(out) == list(range(512)), stem
    return out


def main():
    A = np.fromfile(ATOMS, dtype=np.uint8).reshape(512, NC)
    worst = {}
    for name, stem in (("m2_N100", "dw2_e4"), ("m2_N1000", "dw1_e4")):
        T = tables.read_table(os.path.join(RUNS, name + ".csv"))
        S, N = tables.atom_array(T, "S"), tables.atom_array(T, "N")
        P = m2_pack(stem)
        dS = 0.0
        for i in range(512):
            gid, isl, emax, pay, ef, p = P[i]
            s8 = np.bincount(A[i], weights=p, minlength=8)
            n8 = np.bincount(A[i], minlength=8)
            assert s8[5] == 0 and n8[5] == 0, (name, i)
            assert (n8[IDX] == N[i]).all(), (name, i, n8[IDX], N[i])
            dS = max(dS, float(np.abs(s8[IDX] - S[i]).max()))
            assert (gid, isl) == (2000 + i, T["isl"][i]) and T["seed1"][i] == (8000000 if name == "m2_N1000" else 9000000) + 10 * (isl - 1) + 1
            assert (emax, pay, ef) == (T["emax"][i], T["pay"][i], T["E"][i]), (name, i)
            assert int(np.argmax(p)) == T["top"][i] and float(p.max()) == T["maxpi"][i], (name, i)
            assert abs(1.0 / np.square(p).sum() - T["neff"][i]) <= 1e-9 * T["neff"][i], (name, i)
        worst[name] = dS
        print("%-9s atoms512.bin + own parser: N identical; S max |diff| %.2e; E, pay, emax, top, maxpi identical; neff to 1e-9"
              % (name, dS))
        assert dS < 1e-12, name

    # memory one: the deposited atoms of the sixteen against atoms512.bin at their memory-two embeddings
    M = tables.read_table(os.path.join(RUNS, "m1_strategy_atoms.csv"))
    emb = [sum(((k >> o) & 1) << (4 * o + o2) for o in range(4) for o2 in range(4)) for k in range(16)]
    assert emb[0] == 0 and emb[15] == 65535
    bad = [(i, k) for i in range(512) for k in range(16) if int(A[i, emb[k]]) != int(M["a%d" % k][i])]
    print("m1 atoms  the 16 x 512 memory-one atoms against atoms512.bin at the embedded strategies: %d of 8192 differ" % len(bad))
    for i, k in bad[:20]:
        g = games.games()
        print("          ipt %3d (u %.3f, v %.3f %s/%s) strategy %2d: m1 %s, atoms512 %s"
              % (i, g["u"][i], g["v"][i], g["quadrant"][i], g["wedge"][i], k, atoms.CODE[M["a%d" % k][i]], atoms.CODE[A[i, emb[k]]]))
    return len(bad)


if __name__ == "__main__":
    sys.exit(main())
