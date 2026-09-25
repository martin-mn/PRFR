"""censuslib.py -- reading the deposited census (data/census/) and the conventions shared by its users.

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "census"))
    import censuslib
    C = censuslib.load()            # dict: column name -> (65536,) array, the exact census (census.csv)
    M = censuslib.masks(C)          # dict: eff_cc, eff_alt, eff_line, riv_p, riv_m, def_p, def_m, nash, tie_ok -> bool
    F = censuslib.wedges(M)         # dict: W, S, E, N -> bool, the friendly rivals of each open quarter-plane

Strategy code: bit j is 1 when the strategy cooperates at state j = 4*(most recent outcome) + (the outcome before), with
the outcomes CC=0, CD=1, DC=2, DD=3 written own action first, so ALLC = 65535 and ALLD = 0.  The genome of the paper is
the string of the sixteen answers, position j from the left = state j, 1 = C, 0 = D.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))
from common.tables import read_table            # noqa: E402

DATA = os.path.normpath(os.path.join(HERE, os.pardir, "data", "census"))
NC = 65536
BOOL = ("eff_cc", "eff_alt", "eff_line", "riv_p", "riv_m", "def_p", "def_m", "nash", "tie_ok")

# named strategies (codes as above)
NAMED = {"ALLD": 0, "ALLC": 65535, "TFT": 3855, "WSLS": 61455, "TF2T": 24415, "AON2": 36873}
EIGHT = [19079, 19087, 20103, 20111, 23175, 23183, 24199, 24207]      # the friendly rivals of the wedge W

# the four open quarter-planes: (efficiency mask, rivalry mask, u+v side, u-v side)
WEDGE = {"W": ("eff_cc", "riv_p", "<1", "<1"), "S": ("eff_cc", "riv_m", "<1", ">1"),
         "E": ("eff_alt", "riv_m", ">1", ">1"), "N": ("eff_alt", "riv_p", ">1", "<1")}
DEFREAD = {"riv_p": "def_p", "riv_m": "def_m"}


def load(name="census.csv"):
    """a table of data/census as {column: (n,) array}; name 'census.csv' (exact) or 'census_double.csv'"""
    T = read_table(os.path.join(DATA, name))
    assert len(T["code"]) == NC and (T["code"] == np.arange(NC)).all(), name
    return T


def masks(T):
    """the boolean columns of a census table"""
    return {k: T[k].astype(bool) for k in BOOL if k in T}


def wedges(M, reading="limit"):
    """{wedge: bool mask of its friendly rivals}; reading 'limit' (riv_*) or 'defensible' (def_*)"""
    out = {}
    for w, (e, r, _, _) in WEDGE.items():
        rr = r if reading == "limit" else DEFREAD[r]
        out[w] = M[e] & M[rr]
    return out


def genome(code):
    """the paper's genome of a strategy: sixteen symbols, position j = state j, 1 = C"""
    return "".join("1" if int(code) >> j & 1 else "0" for j in range(16))


def code_of(genome):
    """the integer code of a genome of sixteen 0/1 symbols"""
    assert len(genome) == 16 and set(genome) <= set("01"), genome
    return sum(1 << j for j, c in enumerate(genome) if c == "1")


def mirror(codes):
    """the mirror image (C and D relabelled): the genome reversed and complemented"""
    codes = np.asarray(codes, dtype=np.int64)
    rev = np.zeros_like(codes)
    for j in range(16):
        rev |= ((codes >> j) & 1) << (15 - j)
    return 65535 - rev
