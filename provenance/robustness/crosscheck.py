#!/usr/bin/env python3
"""
crosscheck.py -- compare the tables of data/robustness/ with what the ORIGINAL figure scripts' loaders return from the
private full outputs, run by run and array by array.

    python3 -B provenance/robustness/crosscheck.py        (from the repository root; about half a minute, one process)

The originals (PartnersRivals1/FinalFigures, read-only, imported with bytecode writing off):
    wfdata.load("m2", "F1"/"F2")   Figure 4's two memory-two runs (DiskM2WF dw1, dw2; shares through the exact masks)
    sifig8.load_idx                dw3, dw4 (DiskM2WF/Opt wfload + exact masks)
    wfrep.load                     c1..c4, eh, el, f1, f2 and the lm packs (atoms512.bin)
and DiskM2WF/Opt/exact.masks, the eps -> 0 classification itself, against which atoms512.bin is checked strategy by
strategy at all 512 games.  Also compares the packs of f1_e4 and f2_e4 byte for byte with those of Figure 4's
original runs, DiskM2WF/Data/dw1_e4.* (its 512 sampled games) and dw2_e4.*.  Prints one line per comparison and stops at the first mismatch that would change a figure
or a table (a different atom size, efficiency, game, replicate value or winning atom).  Pooled shares computed by the
two routes (np.bincount over atoms512.bin, or a masked sum over the exact masks) may differ in the last bits of a
double; the largest difference is printed.

AUTHOR'S ENVIRONMENT: AUTHOR_ROOT below is the only path into the private tree.
"""
import os
import sys

sys.dont_write_bytecode = True

import numpy as np

# ---------------------------------------------------------------------------------------------- author's environment
AUTHOR_ROOT = "/Users/martin/Documents/CL1"          # author's environment: the private project tree
# ---------------------------------------------------------------------------------------------------------------------
FINALFIGURES = os.path.join(AUTHOR_ROOT, "PartnersRivals1", "FinalFigures")
LMPACKED = os.path.join(AUTHOR_ROOT, "PartnersRivals1", "Cannon", "lm", "packed")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir)
sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
sys.path.insert(0, ROOT)
import wfruns                                        # noqa: E402  the reader of the deposited tables
from common import games                             # noqa: E402

sys.path.insert(1, FINALFIGURES)
import wfdata, wfrep, sifig8                         # noqa: E402  the originals, read-only
import exact                                         # noqa: E402  DiskM2WF/Opt, on sys.path through wfdata

ORIG = {"f1_e4": ("wfdata", ("m2", "F1")), "f2_e4": ("wfdata", ("m2", "F2")),
        "dw3_e4": ("load_idx", "dw3"), "dw4_e4": ("load_idx", "dw4")}
for r in ("lm_g0_e4", "lm_g01_e4", "lm_g05_e4"):
    wfrep.RUNS[r] = dict(N=1000, beta=100, mu="10^{-2}", muplain="1e-2", eps="10^{-4}", epsplain="1e-4")


def winners(S, N):
    return np.where(N > 0, S, -np.inf).argmax(1), np.where(N > 0, S / np.maximum(N, 1), -np.inf).argmax(1)


def check(run):
    g = wfruns.load(run)
    out = []
    # the original arrays through the route the figure scripts used
    if run in ORIG and ORIG[run][0] == "wfdata":
        S, N, E, UV, D = wfdata.load(*ORIG[run][1]); route = "wfdata.load%r" % (ORIG[run][1],)
    elif run in ORIG:
        path = [r[1] for r in sifig8.RUNS if r[0] == ORIG[run][1]][0]
        S, N, E, UV = sifig8.load_idx(path); route = "sifig8.load_idx(%s)" % ORIG[run][1]
    else:
        o = wfrep.load(run, data=LMPACKED) if run.startswith("lm_") else wfrep.load(run)
        S, N, E, UV = o["S"], o["N"], o["E"], o["UV"]; route = "wfrep.load(%s)" % run
    assert np.array_equal(UV, games.uv()), (run, "games")
    assert np.array_equal(N, g["N"]), (run, "atom sizes")
    assert np.array_equal(E, g["E"]), (run, "efficiency")
    dS = np.abs(S - g["S"]).max()
    wa0, we0 = winners(S, N); wa1, we1 = winners(g["S"], g["N"])
    assert np.array_equal(wa0, wa1) and np.array_equal(we0, we1), (run, "winning atoms")
    out.append("%-10s vs %-28s games, N, E identical; S max|diff| %.1e%s; most abundant and most enriched atom identical"
               % (run, route, dS, " (bit-identical)" if dS == 0 else ""))
    # the replicate arrays: wfrep's R, ER, LEAD (and for f1/f2 also wfrep, which the SI Figure 11 script used)
    if run not in ("dw3_e4", "dw4_e4"):
        o = wfrep.load(run, data=LMPACKED) if run.startswith("lm_") else wfrep.load(run)
        assert np.array_equal(o["R"], g["R"]) and np.array_equal(o["ER"], g["ER"]), (run, "replicates")
        assert np.array_equal(o["LEAD"], g["LEAD"]), (run, "replicate leaders")
        dS2 = np.abs(o["S"] - g["S"]).max()
        out.append("%-10s vs wfrep.load: R, ER, LEAD identical; S max|diff| %.1e" % (run, dS2))
    return out


def figure4_packs():
    """the packs of f1_e4 / f2_e4 against the originals of Figure 4's runs, DiskM2WF dw1 (its 512 sampled rows) / dw2"""
    out = []
    for new, old in (("f1_e4", "dw1_e4"), ("f2_e4", "dw2_e4")):
        a = os.path.join(AUTHOR_ROOT, "PartnersRivals", "Data", new)
        b = os.path.join(AUTHOR_ROOT, "DiskM2WF", "Data", old)
        rows = {}
        for ext in (".idx", ".win"):
            ra = [l for l in open(a + ext) if not l.startswith("#")]
            rb = [l for l in open(b + ext) if not l.startswith("#") and int(l.split()[0]) >= 2000]
            assert ra == rb, (new, old, ext)
            rows[ext] = len(ra)
        keep = [k for k, l in enumerate(l for l in open(b + ".idx") if not l.startswith("#")) if int(l.split()[0]) >= 2000]
        A = np.fromfile(a + ".bin", dtype="<f4").reshape(-1, 65536)
        B = np.fromfile(b + ".bin", dtype="<f4").reshape(-1, 65536)[keep]
        assert A.tobytes() == B.tobytes(), (new, old, ".bin")
        out.append("%s == %s (its %d sampled games): .idx rows, .win rows (%d) and .bin rows byte-identical"
                   % (new, old, rows[".idx"], rows[".win"]))
    return out


def atoms_vs_masks():
    """atoms512.bin against DiskM2WF/Opt/exact.masks, strategy by strategy, at every sampled game"""
    A = wfrep.atoms()
    d = exact.load()
    UV = games.uv()
    bad = 0
    for i in range(512):
        eff, riv, ne = exact.masks(d, UV[i, 0], UV[i, 1])
        lab = eff.astype(np.int64) * 4 + ne.astype(np.int64) * 2 + riv.astype(np.int64)
        bad += int((lab != A[i]).sum())
    assert bad == 0, "%d strategy-game pairs differ" % bad
    return "atoms512.bin == exact.masks at all 512 x 65536 (strategy, game) pairs"


if __name__ == "__main__":
    print(atoms_vs_masks())
    for line in figure4_packs():
        print(line)
    for run in sys.argv[1:] or wfruns.RUNS:
        for line in check(run):
            print(line)
    print("all checks passed")
