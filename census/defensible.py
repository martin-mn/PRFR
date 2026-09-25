#!/usr/bin/env python3
"""defensible.py -- Murase and Baek's defensibility of the 65536 binary memory-two strategies, by Floyd--Warshall.

A deterministic strategy sigma is defensible if, at eps = 0, no co-player of any memory can make the cumulative payoff
difference pi(tau) - pi(sigma) diverge in its own favour, from any initial state (Murase and Baek 2018, 2020).  It is
decided on the graph g(sigma, *) of sigma's sixteen memory states: from state k = 4*(most recent outcome) + (the outcome
before), with outcomes CC=0, CD=1, DC=2, DD=3 written own action first, sigma plays its answer at k and the co-player
either action, so every node has two outgoing edges, to the states 4*o + (k >> 2) with o the new outcome.  An edge that
makes the outcome DC gains sigma T - S over the co-player, one that makes CD loses it, CC and DD are even:

    T > S reading:  weight +1 for DC, -1 for CD, 0 otherwise
    T < S reading:  the signs reversed (T - S < 0), -1 for DC, +1 for CD

sigma is defensible if and only if its graph has no cycle of negative total weight.  All 65536 graphs are relaxed at once
by Floyd--Warshall on (65536, 16, 16) arrays; a negative cycle shows as a negative diagonal entry.  The weights are
integers, and the distances are held as float64 integers with +inf for "no path", so the test is exact.

Strategy code: bit j of the 16-bit integer is 1 when the strategy cooperates at state j, so ALLC = 65535, ALLD = 0.

    python3 defensible.py         prints the counts (2144 for each sign; the second set is the mirror of the first)

Used by reduce.py, which writes the two masks into data/census/census.csv (columns def_p, def_m).
"""
import numpy as np

NS, NC = 16, 65536


def adjacency(sign=1):
    """(65536, 16, 16) float64: the weight of the edge k -> k' of g(sigma, *), +inf where there is none"""
    A = np.full((NC, NS, NS), np.inf)
    codes = np.arange(NC, dtype=np.int64)
    for k in range(NS):
        o1 = k >> 2                              # the most recent outcome becomes the outcome before
        x = (codes >> k) & 1                     # 1 = sigma cooperates at state k
        for y in (1, 0):                         # the co-player's action: 1 = C, 0 = D
            o = 2 * (1 - x) + (1 - y)            # new outcome, own action first: CC=0, CD=1, DC=2, DD=3
            w = np.where(o == 2, 1.0, np.where(o == 1, -1.0, 0.0)) * sign
            A[codes, k, 4 * o + o1] = w
    return A


def defensible(sign=1):
    """(65536,) bool: True where g(sigma, *) has no negative cycle, for T > S (sign = +1) or T < S (sign = -1)"""
    D = adjacency(sign)
    for k in range(NS):
        np.minimum(D, D[:, :, k:k + 1] + D[:, k:k + 1, :], out=D)
    return np.diagonal(D, axis1=1, axis2=2).min(axis=1) >= 0


def mirror(codes):
    """the mirror image of a strategy (C and D relabelled): state j -> 15 - j with the answer flipped, i.e. the genome
    reversed and complemented"""
    codes = np.asarray(codes, dtype=np.int64)
    rev = np.zeros_like(codes)
    for j in range(NS):
        rev |= ((codes >> j) & 1) << (NS - 1 - j)
    return 65535 - rev


if __name__ == "__main__":
    dp, dm = defensible(1), defensible(-1)
    ids = np.arange(NC)
    print("defensible for T>S: %d   (Murase and Baek: 2144)" % dp.sum())
    print("defensible for T<S: %d" % dm.sum())
    print("T<S set = mirror of the T>S set: %s" % (set(mirror(ids[dp]).tolist()) == set(ids[dm].tolist())))
    for name, code in (("ALLD", 0), ("ALLC", 65535), ("TFT", 3855), ("WSLS", 61455)):
        print("  %-5s %5d  defensible T>S %-5s T<S %s" % (name, code, bool(dp[code]), bool(dm[code])))
