"""
The 512 sampled games of the Wright-Fisher maps and their Voronoi cells on the disk (data/games/).

    python3 -m common          (from the repository root) self-test: reads data/games/, recomputes the cells
                                     from the points with scipy, checks the tags, the regions and the tiling

Every per-game array in this repository is in ipt order 0..511.  The packed runs of the simulator identify a game by
gid = 2000 + ipt (or by its tag V_pNNN_QQW, NNN = ipt); index_of() and ipt_of_gid() translate.
"""
import csv
import math
import os

import numpy as np

from . import atoms as _atoms
from .disk import to_disk
from .geometry import polyarea

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "games")
GAMES_CSV = os.path.join(DATA, "games.csv")
CELLS_CSV = os.path.join(DATA, "cells.csv")
NGAME = 512
GID0 = 2000                     # gid = GID0 + ipt
IG0 = 456                       # ig = IG0 + ipt: the 1-based row in the 967-row games.dat of the memory-two kits
_CACHE = {}


def _rows(path):
    with open(path) as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))


def games():
    """the game table (data/games/games.csv) as a dict of (512,) numpy arrays in ipt order:
    ipt, gid, ig, u1024, v1024 (int64); u, v, emax, x, y, cell_area (float64); tag, quadrant, wedge (str).
    The floats are read with Python's float(), so they are the exact doubles that were written."""
    if "g" not in _CACHE:
        R = _rows(GAMES_CSV)
        assert len(R) == NGAME, "%s has %d rows" % (GAMES_CSV, len(R))
        g = {}
        for k in ("ipt", "gid", "ig", "u1024", "v1024"):
            g[k] = np.array([int(r[k]) for r in R], dtype=np.int64)
        for k in ("u", "v", "emax", "x", "y", "cell_area"):
            g[k] = np.array([float(r[k]) for r in R], dtype=np.float64)
        for k in ("tag", "quadrant", "wedge"):
            g[k] = np.array([r[k] for r in R])
        assert (g["ipt"] == np.arange(NGAME)).all() and (g["gid"] == GID0 + g["ipt"]).all() and (g["ig"] == IG0 + g["ipt"]).all()
        assert (g["u"] * 1024 == g["u1024"]).all() and (g["v"] * 1024 == g["v1024"]).all()
        _CACHE["g"] = g
    return _CACHE["g"]


def uv():
    """(512, 2) float64: the games (u, v), S = u, T = 1 + v"""
    g = games()
    return np.column_stack([g["u"], g["v"]])


def xy():
    """(512, 2) float64: the games on the unit disk, exactly vor.xy() (to_disk of the points)"""
    g = games()
    return np.column_stack([g["x"], g["y"]])


def emax():
    """(512,) float64: Emax = max(1, (1 + u + v)/2) of each game"""
    return games()["emax"]


def tags():
    return games()["tag"]


def index_of(tag):
    """V_pNNN_QQW -> NNN (int); None for any other tag (vor.index_of)"""
    if not tag.startswith("V_p"):
        return None
    return int(tag.split("_")[1][1:])


def ipt_of_gid(gid):
    """the cell of a packed-run gid (2000..2511); raises for a gid outside the sunflower block"""
    i = int(gid) - GID0
    if not 0 <= i < NGAME:
        raise ValueError("gid %r is not a sunflower game" % gid)
    return i


def cells():
    """the 512 Voronoi polygons on the unit disk, in ipt order: a list of (n_i, 2) float64 arrays, n_i = 5..8
    (data/games/cells.csv; identical to DiskM2WF's vor.cells())"""
    if "c" not in _CACHE:
        pts = {}
        for r in _rows(CELLS_CSV):
            pts.setdefault(int(r["ipt"]), []).append((int(r["k"]), float(r["x"]), float(r["y"])))
        assert sorted(pts) == list(range(NGAME))
        out = []
        for i in range(NGAME):
            v = sorted(pts[i])
            assert [k for k, _, _ in v] == list(range(len(v)))
            out.append(np.array([(x, y) for _, x, y in v], dtype=np.float64))
        _CACHE["c"] = out
    return _CACHE["c"]


def cells_keep():
    """(pol, keep): the polygons with at least three vertices and their ipt indices -- wfdata.cells()'s return value.
    All 512 cells qualify, so pol == cells() and keep == list(range(512))."""
    c = cells()
    keep = [i for i in range(NGAME) if len(c[i]) >= 3]
    return [c[i] for i in keep], keep


def cell_areas():
    """(512,) float64: the area of each cell on the disk (the cell_area column; polyarea of cells())"""
    return games()["cell_area"]


# ------------------------------------------------------------------ the construction of the cells, for the record
def clip_disk(poly, nseg=64):
    """Sutherland-Hodgman against the unit circle, approximated from outside by an nseg-gon, then the cut vertices
    pushed onto the circle so that the cells leave no white seam at the rim (vor.clip_disk)"""
    if len(poly) < 3:
        return poly
    for k in range(nseg):
        t = 2 * math.pi * k / nseg
        a, b, c = math.cos(t), math.sin(t), 1.0
        out, n = [], len(poly)
        for i in range(n):
            p, q = poly[i], poly[(i + 1) % n]
            sp = a * p[0] + b * p[1] - c
            sq = a * q[0] + b * q[1] - c
            if sp <= 0:
                out.append(p)
            if (sp > 0) != (sq > 0):
                out.append(p + (sp / (sp - sq)) * (q - p))
        poly = np.array(out)
        if len(poly) < 3:
            return poly
    rr = np.hypot(*poly.T)
    hot = rr > 1.0 - 1e-9
    poly[hot] /= rr[hot][:, None]
    return poly


def compute_cells(p=None):
    """recompute the cells from the disk points p ((512, 2); default xy()): the Voronoi diagram of the points, their
    inversions in the unit circle (the missing neighbours of the outer cells) and 32 far points on the circle of
    radius 3, each real point's region clipped to the disk (vor.cells).  Needs scipy.  With the scipy/Qhull of the
    original (scipy 1.10) the result is bit-identical to cells(); another Qhull may order or round differently."""
    from scipy.spatial import Voronoi
    p = xy() if p is None else np.asarray(p, float)
    r2 = (p ** 2).sum(1)
    mir = p / r2[:, None]
    far = 3.0 * np.column_stack([np.cos(np.linspace(0, 2 * math.pi, 33)[:-1]), np.sin(np.linspace(0, 2 * math.pi, 33)[:-1])])
    vor = Voronoi(np.vstack([p, mir, far]))
    out = []
    for i in range(len(p)):
        reg = vor.regions[vor.point_region[i]]
        q = vor.vertices[reg] if reg and -1 not in reg else np.empty((0, 2))
        out.append(clip_disk(np.asarray(q, float)))
    return out


def selftest():
    g = games()
    u, v = g["u"], g["v"]
    x, y = to_disk(u, v)
    assert (x == g["x"]).all() and (y == g["y"]).all(), "x, y are not to_disk(u, v)"
    q, w = _atoms.pieces(uv())
    assert (q == g["quadrant"]).all() and (w == g["wedge"]).all()
    assert all(t == "V_p%03d_%s%s" % (i, a, b) for i, t, a, b in zip(g["ipt"], g["tag"], q, w))
    assert (_atoms.emax(u, v) == g["emax"]).all()
    C = cells()
    A = np.array([polyarea(c) for c in C])
    assert (A == g["cell_area"]).all()
    assert (A > 0).all() and abs(A.sum() - math.pi) < 0.01
    print("games.csv: 512 games, |(u,v)| %.4f .. %.4f; quadrants %s; wedges %s"
          % (np.hypot(u, v).min(), np.hypot(u, v).max(),
             " ".join("%s %d" % (k, (q == k).sum()) for k in ("PD", "SD", "SH", "HA")),
             " ".join("%s %d" % (k, (w == k).sum()) for k in ("W", "S", "N", "E"))))
    print("cells.csv: %d vertices, %d..%d per cell, total area %.5f = %.3f%% of pi"
          % (sum(len(c) for c in C), min(len(c) for c in C), max(len(c) for c in C), A.sum(), 100 * A.sum() / math.pi))
    try:
        D = compute_cells()
    except ImportError:
        print("scipy not available: the cells were not recomputed")
        return
    same = all(len(a) == len(b) and np.array_equal(a, b) for a, b in zip(C, D))
    if same:
        print("recomputed from the points with scipy: bit-identical to cells.csv")
    else:
        dev = max(np.abs(a - b).max() if a.shape == b.shape else np.inf for a, b in zip(C, D))
        print("recomputed from the points with scipy: NOT bit-identical (max deviation %.3g); another Qhull?" % dev)
    print("OK")


if __name__ == "__main__":
    selftest()
