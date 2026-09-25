"""
Loads the exact eps -> 0 arrangements of this folder for the figure scripts (Figures 1, 2, 3) and for check.py.

    import os, sys
    sys.path.insert(0, os.path.join(<repository root>, "data", "arrangement"))
    import arrangement
    D1 = arrangement.m1()          memory one: 45 faces, 16 strategies
    D2 = arrangement.m2()          memory two: 27598 polygons (the 22872 faces, some in bands), 65536 strategies
    S2 = arrangement.m2_strategies()

The arrays come back in the shapes the original figure scripts used: the atom counts as an (n, 8) array indexed by
the integer code 4 efficient + 2 stable + competitive (column 5, the atom 101, is zero), the faces as a list of
(n_i, 2) arrays of disk points.  Side-effect free (numpy only, plus common.tables).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))
from common import tables                                          # noqa: E402
from common.atoms import IDX, ORDER                                # noqa: E402

K = 4.0


def _faces(name):
    Z = np.load(os.path.join(HERE, name), allow_pickle=False)
    assert float(Z["K"]) == K
    V, OFF = Z["verts"], Z["offsets"]
    return [V[OFF[i]:OFF[i + 1]] for i in range(len(OFF) - 1)]


def _atoms8(T):
    """the (n, 8) array by integer code from the seven columns A_000 ... A_111"""
    A7 = tables.atom_array(T, "A")
    A8 = np.zeros((len(A7), 8), np.int64)
    A8[:, IDX] = A7
    return A8


def m1():
    """memory one: dict with faces (list of 45 disk polygons), diskarea (45,), area (45,) plane area within the box,
    uvc (45, 2) an interior game, codes (45, 16) the atom code of each strategy (index s: bit k of s is the answer
    after CC, CD, DC, DD, 1 = C), atoms (45, 8) by code, case (45,), lines (11, 3), genomes (16 strings)"""
    T = tables.read_table(os.path.join(HERE, "m1_faces.csv"))
    faces = _faces("m1_faces_k4.npz")
    gen = ["".join("C" if (s >> k) & 1 else "D" for k in range(4)) for s in range(16)]
    codes = np.column_stack([T["code_" + g] for g in gen])
    L = tables.read_table(os.path.join(HERE, "m1_lines.csv"))
    D = dict(faces=faces, diskarea=T["disk_area"], area=T["area"], uvc=np.column_stack([T["u"], T["v"]]),
             codes=codes, atoms=_atoms8(T), case=T["case"], lines=np.column_stack([L["a"], L["b"], L["c"]]),
             genomes=gen, quadrant=T["quadrant"], wedge=T["wedge"])
    assert len(faces) == len(codes) == 45
    return D


def m2():
    """memory two: dict with faces (list of 27598 disk polygons), cell (27598,), uvc (27598, 2) an interior game,
    nash, partners (27598,), atoms (27598, 8) by code, case (27598,), atom_total (8,) the strategies in each atom on
    some face, ne_total the strategies that are stable on some face"""
    T = tables.read_table(os.path.join(HERE, "m2_faces.csv"))
    faces = _faces("m2_faces_k4.npz")
    assert len(faces) == len(T["face"]) == 27598
    S = m2_strategies()
    atom_total = np.zeros(8, np.int64)
    atom_total[IDX] = [int(S["open_" + c].sum()) for c in ORDER]
    ne_total = int((S["open_010"] | S["open_011"] | S["open_110"] | S["open_111"]).sum())
    return dict(faces=faces, cell=T["cell"], uvc=np.column_stack([T["u"], T["v"]]), nash=T["nash"],
                partners=T["partners"], atoms=_atoms8(T), case=T["case"], quadrant=T["quadrant"], wedge=T["wedge"],
                atom_total=atom_total, ne_total=ne_total)


_S = {}


def m2_strategies():
    """m2_strategies.csv as a dict of (65536,) arrays; the 0/1 columns as bool"""
    if "s" not in _S:
        T = tables.read_table(os.path.join(HERE, "m2_strategies.csv"))
        for k in list(T):
            if k.startswith(("eff_", "riv_", "open_")):
                T[k] = T[k].astype(bool)
        assert len(T["genotype"]) == 65536 and (T["genotype"] == np.arange(65536)).all()
        _S["s"] = T
    return _S["s"]
