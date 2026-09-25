"""
wfruns.py -- the reader of the tables in data/robustness/: one memory-two Wright-Fisher run as the arrays the figure
scripts of SI Figures 8-12 and SI Tables 6 and 7 use (the arrays the original loaders wfdata.py and wfrep.py returned).

    import os, sys
    ROOT = <the repository root>
    sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
    import wfruns
    g = wfruns.load("f1_e4")

returns a dict, every per-game array in ipt order 0..511 (data/games/games.csv):
    S      (512, 7)      pooled share of the population in each atom, in ORDER = 000 100 010 001 110 011 111
    N      (512, 7)      number of the 65536 strategies in each atom at the game (eps -> 0 atoms; m2_atom_sizes.csv)
    E      (512,)        realised efficiency of the pooled run
    efsd   (512,)        s.d. of the efficiency over the replicates, as the simulator wrote it
    UV     (512, 2)      the games (u, v) (common.games.uv())
    R      (512, 10, 7)  each replicate's atom shares, or None for a run without per-replicate output (dw3, dw4)
    ER     (512, 10)     each replicate's efficiency, or None
    LEAD   (512, 10)     the atom (index into ORDER) of each replicate's most abundant strategy
    TOP, TOPSHARE        (512, 10) that strategy (the simulator's index 0..65535) and its share of the replicate
    seed   (512, 10)     the seed of each replicate
    D      the run's row of runs.csv, with the keys the figure scripts' receipts use: N, beta, mu ("10^{-2}"),
           muplain ("1e-2"), eps, epsplain, nu, label
RUNS lists the runs in the order of runs.csv.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from common import games, tables                    # noqa: E402
from common.atoms import IDX, ORDER                 # noqa: E402

NG, NREP = 512, 10
_CACHE = {}


def _runs():
    if "runs" not in _CACHE:
        t = tables.read_table(os.path.join(HERE, "runs.csv"))
        _CACHE["runs"] = {r: {k: t[k][i] for k in t} for i, r in enumerate(t["run"])}
    return _CACHE["runs"]


RUNS = list(_runs())


def sizes():
    """(512, 7) int64: the atom sizes N in ORDER"""
    if "N" not in _CACHE:
        t = tables.read_table(os.path.join(HERE, "m2_atom_sizes.csv"))
        assert (t["ipt"] == np.arange(NG)).all()
        N = tables.atom_array(t, "N")
        assert (N.sum(1) == 65536).all()
        _CACHE["N"] = N
    return _CACHE["N"]


def _power(x):
    """1e-2 -> ("10^{-2}", "1e-2")"""
    k = int(round(np.log10(float(x))))
    assert float(x) == 10.0 ** k, x
    return "10^{%d}" % k, "1e%d" % k


def load(run):
    meta = _runs()[run]
    D = dict(N=int(meta["N"]), beta=int(meta["beta"]), nu=float(meta["nu"]), generations=float(meta["generations"]),
             seed_base=int(meta["seed_base"]), jobid=int(meta["jobid"]), kit=str(meta["kit"]))
    D["mu"], D["muplain"] = _power(meta["mu"])
    D["eps"], D["epsplain"] = _power(meta["eps"])
    D["label"] = "Memory-2, $N = %d$\n$\\beta = %d$, $\\mu = %s$, $\\epsilon = %s$" % (D["N"], D["beta"], D["mu"], D["eps"])
    g = tables.read_table(os.path.join(HERE, "games_%s.csv" % run))
    assert (g["ipt"] == np.arange(NG)).all() and (g["nrep"] == NREP).all(), run
    out = dict(S=tables.atom_array(g, "S"), N=sizes(), E=g["E"], efsd=g["efsd"], UV=games.uv(), D=D)
    r = tables.read_table(os.path.join(HERE, "replicates_%s.csv" % run))
    assert (r["ipt"] == np.repeat(np.arange(NG), NREP)).all() and (r["rep"] == np.tile(np.arange(1, NREP + 1), NG)).all(), run
    code = r["top_atom"].reshape(NG, NREP)
    assert not (code == 5).any()
    out["LEAD"] = np.array([IDX.index(int(c)) for c in code.ravel()], dtype=np.int64).reshape(NG, NREP)
    out["TOP"] = r["top"].reshape(NG, NREP)
    out["TOPSHARE"] = r["top_share"].reshape(NG, NREP)
    out["seed"] = r["seed"].reshape(NG, NREP)
    if "E" in r:
        out["ER"] = r["E"].reshape(NG, NREP)
        out["R"] = tables.atom_array(r, "R").reshape(NG, NREP, 7)
        assert np.allclose(out["R"].mean(1), out["S"], atol=2e-6), run      # the replicates average to the pooled run
    else:
        out["ER"] = out["R"] = None
    return out
