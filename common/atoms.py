"""
The seven atoms of the three properties, and the regions of the plane of games.

A strategy's ATOM at a game is the three-bit code  efficient-stable-competitive,  written as a string "enc" and stored
as the integer  code = 4*efficient + 2*stable + competitive  (0..7).  101 (efficient and competitive but not stable) is
empty at every game by the theorem, so seven atoms remain.  Every figure lists them in ORDER:

    ORDER = 000 100 010 001 110 011 111          IDX = [0, 4, 2, 1, 6, 3, 7]   (the integer code of ORDER[i])

so an (n, 8) array indexed by integer code becomes an (n, 7) array in ORDER by A[:, IDX].  110 are the partners that
are not competitive, 111 the friendly rivals (partners that are competitive).

The regions of the plane (R, S, T, P) = (1, u, 1 + v, 0):
    quadrant   PD  u < 0 < v (Prisoner's Dilemma)   SD  u, v > 0 (Snowdrift)   SH  u, v < 0 (Stag Hunt)
               HA  v < 0 < u (Harmony)
    wedge      the four wedges cut by the switch line u + v = 1 and the line T = S, u - v = 1:
               W  u + v < 1, u - v < 1     S  u + v < 1, u - v > 1     N  u + v > 1, u - v < 1     E  u + v > 1, u - v > 1
The tag of a sunflower game, V_pNNN_QQW, carries its quadrant QQ and wedge W (common.games).
"""
import numpy as np

ORDER = ["000", "100", "010", "001", "110", "011", "111"]
IDX = [int(c, 2) for c in ORDER]                    # [0, 4, 2, 1, 6, 3, 7]
CODE = np.array(["000", "001", "010", "011", "100", "101", "110", "111"])     # integer code -> string
NAME = {"000": "none of the three", "100": "efficient only", "010": "stable only", "001": "competitive only",
        "110": "efficient and stable only", "011": "stable and competitive only", "111": "efficient, stable and competitive"}
EMPTY = 5                                           # the integer code of 101, empty at every game

# the three properties and the partners as unions of atoms (Figures 3 and 5): (name, pattern, atom codes as strings)
PROPS = [("efficient", "1**", ["100", "110", "111"]),
         ("stable", "*1*", ["010", "110", "011", "111"]),
         ("competitive", "**1", ["001", "011", "111"])]
PARTNERS = ("efficient and stable: partners", "11*", ["110", "111"])


def code(efficient, nash, competitive):
    """the integer atom code(s) of boolean arrays (or scalars): 4 e + 2 n + c"""
    return (np.asarray(efficient).astype(np.int64) * 4 + np.asarray(nash).astype(np.int64) * 2
            + np.asarray(competitive).astype(np.int64))


def to_order(A8):
    """an (..., 8) array indexed by integer code -> the (..., 7) array in ORDER (drops 101, which must be zero)"""
    A8 = np.asarray(A8)
    assert not np.any(A8[..., EMPTY]), "the 101 atom is not empty"
    return A8[..., IDX]


def members(atoms):
    """the ORDER indices of a list of atom strings, e.g. members(PROPS[0][2]) -> [1, 4, 6]"""
    return [ORDER.index(a) for a in atoms]


def pieces(uv):
    """(quadrant, wedge) string arrays for an (n, 2) array of games (m1atoms.pieces: exactly its tie-breaking --
    a game with u = 0 or v = 0 falls to HA, one on a line to the wedge on its '>' side)"""
    uv = np.asarray(uv, float)
    u, v = uv[:, 0], uv[:, 1]
    quad = np.where((u < 0) & (v > 0), "PD", np.where((u < 0) & (v < 0), "SH", np.where((u > 0) & (v > 0), "SD", "HA")))
    wedge = np.where(u + v < 1, np.where(u - v < 1, "W", "S"), np.where(u - v < 1, "N", "E"))
    return quad, wedge


def emax(u, v):
    """the joint optimum per round, Emax = max(R, (S + T)/2) = max(1, (1 + u + v)/2)"""
    return np.maximum(1.0, (1.0 + np.asarray(u, float) + np.asarray(v, float)) / 2.0)
