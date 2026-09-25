"""
wfdata -- the four main Wright-Fisher runs, read from the deposited tables of this folder (data/runs/*.csv).

The figure scripts of Figures 4 and 5 and SI Figures 2 to 5 import this module in place of the loader the published
figures were drawn with (FinalFigures/wfdata.py of the author's project, which read the full outputs of the runs);
it has the same interface and returns the same arrays, bit for bit:

    load("m1", "F2")   memory one, N = 100,  beta = 3,   mu = 1e-4     -> m1_N100.csv
    load("m1", "F1")   memory one, N = 1000, beta = 100, mu = 1e-2     -> m1_N1000.csv
    load("m2", "F2")   memory two, N = 100,  beta = 3,   mu = 1e-4     -> m2_N100.csv
    load("m2", "F1")   memory two, N = 1000, beta = 100, mu = 1e-2     -> m2_N1000.csv

returns, per game in ipt order 0..511:
    S     (512, 7)  the share of the population in each atom, in ORDER = 000 100 010 001 110 011 111
    N     (512, 7)  how many strategies of the space are in the atom at that game (exact eps -> 0 classification)
    E     (512,)    the efficiency: mean per-round payoff over the sampled halves / Emax
    UV    (512, 2)  the game (u, v)
    D     the run's row of runs.csv as a dict (N, beta, mu, muplain = "1e-2" ..., itplain, name, ...)

"F1" and "F2" are the original names of the runs (F1: N = 1000, F2: N = 100), kept so that the figure scripts read as
the originals did.  table(name) returns every column of a run's table; cells() the 512 Voronoi cells.

Usage from a figure folder next to data/:

    sys.path.insert(0, os.path.join(HERE, os.pardir, "data", "runs"))
    import wfdata
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))        # the repository root, for common/
from common import atoms, games, tables                             # noqa: E402  (side-effect free)

ORDER = atoms.ORDER
IDX = atoms.IDX
NSTRAT = {"m1": 16, "m2": 65536}
NAME = {("m1", "F2"): "m1_N100", ("m1", "F1"): "m1_N1000", ("m2", "F2"): "m2_N100", ("m2", "F1"): "m2_N1000"}
LABEL = {("m1", "F2"): "Memory-1, $N = 100$", ("m1", "F1"): "Memory-1, $N = 1000$",
         ("m2", "F2"): "Memory-2, $N = 100$", ("m2", "F1"): "Memory-2, $N = 1000$"}
ROWS = [("m1", "F2"), ("m1", "F1"), ("m2", "F2"), ("m2", "F1")]   # the rows of Figures 4 and 5 (and SI 4, 5), top to bottom
_CACHE = {}


def path(name):
    return os.path.join(HERE, name + ".csv")


def table(name):
    """every column of the run's table (common.tables.read_table), e.g. table("m2_N1000")["enriched"]"""
    if name not in _CACHE:
        _CACHE[name] = tables.read_table(path(name))
    return _CACHE[name]


def run(name):
    """the run's row of runs.csv, as a dict, with the plain strings the receipts print (muplain "1e-4", itplain "1e8")"""
    R = tables.read_table(path("runs"))
    k = list(R["name"]).index(name)
    D = {c: (R[c][k].item() if hasattr(R[c][k], "item") else R[c][k]) for c in R}
    D["muplain"] = "1e%d" % round(math.log10(D["mu"]))
    D["epsplain"] = "1e%d" % round(math.log10(D["eps"]))
    D["itplain"] = "1e%d" % round(math.log10(D["generations"]))
    return D


def load(space, which):
    name = NAME[(space, which)]
    T = table(name)
    assert (T["ipt"] == np.arange(games.NGAME)).all(), name
    S, N, E = tables.atom_array(T, "S"), tables.atom_array(T, "N"), T["E"]
    UV = np.column_stack([T["u"], T["v"]])
    assert (UV == games.uv()).all(), name                           # the games of data/games, bit for bit
    assert np.allclose(S.sum(1), 1.0) and (N.sum(1) == NSTRAT[space]).all(), name
    return S, N, E, UV, run(name)


def cells():
    """the 512 Voronoi polygons and the indices of those with at least three vertices (all 512)"""
    return games.cells_keep()
