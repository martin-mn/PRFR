#!/usr/bin/env python3
"""
recompute_sets.py -- recomputes the strict-equilibrium sets of m1_sets.csv and m2_sets.csv from the 512 games alone
(data/games). It does not use the tables' own provenance: the pair chains are written out here from the definition,
and nothing is read but data/games/games.csv. It then compares the result with the deposited tables, (game, strategy)
by (game, strategy).

    python3 recompute_sets.py            (about 20 seconds; needs numpy)

The shares cannot be recomputed this way: they need the full abundance vectors of the runs, which are not deposited
(see ../../provenance/strict).

MEMORY ONE, exactly. A strategy s = 0..15 cooperates after outcome j (0 CC, 1 CD, 2 DC, 3 DD, own action first) if
bit j of s is 1. For every ordered pair the four-state chain at eps = 1/10000 is solved in rational arithmetic
(fractions.Fraction). The payoff of s against t is then a + b u + c v with rational coefficients, since
(R, S, T, P) = (1, u, 1 + v, 0). Here s is strict at the game (u, v), read as the exact rational the double is, if
pi(s, s) > pi(t, s) for all 15 other t, and weak if pi(s, s) >= pi(t, s). The same sixteen are then embedded in memory two
(code 15 x sum_j b_j 16^j) and tested against all 65536 memory-two strategies by the one-flip test below, in exact
arithmetic.

MEMORY TWO. A strategy s = 0..65535 intends C in state k if bit k of s is 1, where k = 4 x (the most recent outcome) +
(the outcome before). The resident s is strict if every one of the 65535 other strategies t earns strictly less against
it than it earns against itself, pi(t, s) < pi(s, s). At eps > 0 this holds if and only if each of the sixteen one-flip
deviations (s with the answer at one state k reversed) earns strictly less. The reason: every chain is irreducible at
eps > 0, so the deviator faces a unichain average-reward decision problem on the sixteen states, and the identity
g(t) - g(s) = sum_k nu_t(k) phi_s(k, t(k)) holds with nu_t > 0 everywhere (the proposition of the companion paper,
github.com/martin-mn/MapBinM2, cited in the Methods; strictness follows from it because nu_t > 0 at every state).
The gain of the one-flip at state k is

    pi(s^k, s) - pi(s, s) = nu(k) * (p' - p) * sum_o dP_o * h(4 o + k // 4)

by the same identity. Here h is the bias (relative value) of the resident's self-play chain for the focal player's
reward, p -> p' the flipped cooperation probability at k, dP = (q, 1 - q, -q, -(1 - q)) the change of the row of k per
unit of p, q the co-player's cooperation probability at k, and nu(k) > 0. So the sign of the gain is the sign of
(p' - p) times a bracket that is linear in (u, v). That bracket is computed here in double precision, from the resident's
self-play chain only, without subtracting two payoffs of order one. It is computed twice, with h fixed by two
different normalisations. A sign counts as decided when |bracket| exceeds a margin built from the difference of the
two computations (x 10^4) plus 1e-12 of the sum of the absolute terms. Every sign not decided so is referred to exact
rational arithmetic: the sixteen deviant chains and the resident's own are solved in Fractions, and the gain is
evaluated exactly at the game. The receipt says how many signs that took.
"""
import os
import sys
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))
from common import games, tables                                   # noqa: E402

EPS_Q = F(1, 10000)
EPS = 1e-4
NC = 65536
SWAP = (0, 2, 1, 3)                                                # an outcome seen from the other side: CD <-> DC
MAP = np.array([4 * SWAP[k // 4] + SWAP[k % 4] for k in range(16)])
MARGIN_DIFF, MARGIN_REL = 1e4, 1e-12


# ------------------------------------------------------------------------------------------ exact chains (Fractions)
def _solve_stationary(P):
    """the stationary distribution of the n x n stochastic matrix P (lists of Fractions), exactly"""
    n = len(P)
    A = [[P[k][j] - (1 if j == k else 0) for k in range(n)] + [F(0)] for j in range(n - 1)]
    A.append([F(1)] * n + [F(1)])
    for c in range(n):
        piv = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        inv = 1 / A[c][c]
        A[c] = [x * inv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [A[r][n] for r in range(n)]


def m1_weights(s, t, eps=EPS_Q):
    """(w_CC, w_CD, w_DC, w_DD) of memory-one s playing t, from s's side, exactly"""
    P = [[F(0)] * 4 for _ in range(4)]
    for o in range(4):
        ps = 1 - eps if (s >> o) & 1 else eps
        pt = 1 - eps if (t >> SWAP[o]) & 1 else eps
        P[o][0] += ps * pt; P[o][1] += ps * (1 - pt); P[o][2] += (1 - ps) * pt; P[o][3] += (1 - ps) * (1 - pt)
    return _solve_stationary(P)


def m2_weights(f, c, eps=EPS_Q):
    """(w_CC, w_CD, w_DC, w_DD) of memory-two f playing c, from f's side, exactly"""
    P = [[F(0)] * 16 for _ in range(16)]
    for k in range(16):
        a = k // 4
        p = 1 - eps if (f >> k) & 1 else eps
        q = 1 - eps if (c >> int(MAP[k])) & 1 else eps
        P[k][a] += p * q; P[k][4 + a] += p * (1 - q); P[k][8 + a] += (1 - p) * q; P[k][12 + a] += (1 - p) * (1 - q)
    pi = _solve_stationary(P)
    return [sum(pi[4 * o:4 * o + 4]) for o in range(4)]


def coef(w):
    """the payoff a + b u + c v of the weights w at (R, S, T, P) = (1, u, 1 + v, 0), as (a, b, c)"""
    return (w[0] + w[2], w[1], w[2])


_EX = {}


def m2_exact_gains(s):
    """the sixteen one-flip gains of resident s as exact (a, b, c): gain = a + b u + c v"""
    if s not in _EX:
        own = coef(m2_weights(s, s))
        _EX[s] = [tuple(x - y for x, y in zip(coef(m2_weights(s ^ (1 << k), s)), own)) for k in range(16)]
    return _EX[s]


def at(t, U, V):
    return t[0] + t[1] * U + t[2] * V


# ------------------------------------------------------------------------------------------ memory one
def memory_one(G):
    C = {(s, t): coef(m1_weights(s, t)) for s in range(16) for t in range(16)}
    strict = np.zeros((512, 16), bool)
    weak = np.zeros((512, 16), bool)
    for i in range(512):
        U, V = F(float(G["u"][i])), F(float(G["v"][i]))
        for s in range(16):
            own = at(C[(s, s)], U, V)
            d = [at(C[(t, s)], U, V) - own for t in range(16) if t != s]
            strict[i, s] = all(x < 0 for x in d)
            weak[i, s] = all(x <= 0 for x in d)
    emb = [15 * sum(((s >> j) & 1) << (4 * j) for j in range(4)) for s in range(16)]
    assert emb[0] == 0 and emb[15] == 65535 and emb[9] == 61455
    strict16 = np.zeros((512, 16), bool)
    for s in range(16):
        T = m2_exact_gains(emb[s])
        for i in range(512):
            U, V = F(float(G["u"][i])), F(float(G["v"][i]))
            strict16[i, s] = all(at(t, U, V) < 0 for t in T)
    return strict, weak, strict16


# ------------------------------------------------------------------------------------------ memory two
def selfplay(codes, eps=EPS):
    """self-play chains of the memory-two strategies `codes`: P (B, 16, 16), p (B, 16) own and q (B, 16) the
    co-player's cooperation probability in each state, both from the focal player's side"""
    B = len(codes)
    bits = ((codes[:, None] >> np.arange(16)) & 1).astype(bool)
    p = np.where(bits, 1.0 - eps, eps)
    q = p[:, MAP]
    P = np.zeros((B, 16, 16))
    k = np.arange(16)
    a = k // 4
    P[:, k, a] = p * q
    P[:, k, 4 + a] = p * (1 - q)
    P[:, k, 8 + a] = (1 - p) * q
    P[:, k, 12 + a] = (1 - p) * (1 - q)
    return P, p, q


def gth(P):
    """stationary distributions of the batch P (B, n, n) by state reduction (Grassmann-Taksar-Heyman): no subtraction"""
    A = P.copy()
    n = A.shape[1]
    for k in range(n - 1, 0, -1):
        s = A[:, k, :k].sum(1)
        A[:, :k, k] /= s[:, None]
        A[:, :k, :k] += A[:, :k, k][:, :, None] * A[:, k, :k][:, None, :]
    pi = np.zeros(A.shape[:2])
    pi[:, 0] = 1.0
    for k in range(1, n):
        pi[:, k] = (pi[:, :k] * A[:, :k, k]).sum(1)
    return pi / pi.sum(1, keepdims=True)


# the focal player's reward in state k, which records the round just played (its outcome k // 4), as 1*rA + u*rS + v*rT
REW = np.zeros((16, 3))
REW[np.arange(16) // 4 == 0, 0] = 1.0                              # CC: R = 1
REW[np.arange(16) // 4 == 1, 1] = 1.0                              # CD: S = u
REW[np.arange(16) // 4 == 2, 0] = 1.0                              # DC: T = 1 + v
REW[np.arange(16) // 4 == 2, 2] = 1.0


def brackets(codes):
    """(beta, dbeta), each (B, 16, 3): the one-flip gain of state k of resident s has the sign of
    beta[s, k] . (1, u, v); dbeta is the difference between two computations of beta"""
    B = len(codes)
    P, p, q = selfplay(codes)
    pi = gth(P)
    g = pi @ REW                                                    # (B, 3): the self-play payoff's coefficients
    rhs = REW[None, :, :] - g[:, None, :]
    I = np.eye(16)[None]
    h1 = np.linalg.solve(I - P + pi[:, None, :], rhs)               # normalised by pi . h = 0
    M = I - P                                                       # normalised by h = 0 at the most visited state
    k0 = pi.argmax(1)
    M = M.copy()
    M[np.arange(B), k0, :] = 0.0
    M[np.arange(B), k0, k0] = 1.0
    rhs2 = rhs.copy()
    rhs2[np.arange(B), k0, :] = 0.0
    h2 = np.linalg.solve(M, rhs2)
    k = np.arange(16)
    a = k // 4
    sign = np.where(p < 0.5, 1.0, -1.0)                             # p' - p = +-(1 - 2 eps)
    out = []
    for h in (h1, h2):
        dh = (q[:, :, None] * (h[:, a, :] - h[:, 8 + a, :]) + (1 - q[:, :, None]) * (h[:, 4 + a, :] - h[:, 12 + a, :]))
        out.append(sign[:, :, None] * dh)
    return out[0], out[0] - out[1]


def memory_two(G, chunk=4096):
    t0 = time.time()
    beta = np.zeros((NC, 16, 3))
    dbeta = np.zeros((NC, 16, 3))
    for lo in range(0, NC, chunk):
        codes = np.arange(lo, min(NC, lo + chunk))
        beta[codes], dbeta[codes] = brackets(codes)
    t1 = time.time()
    # the float brackets must point the way the exact gains do (same half-plane, positive factor)
    rng = np.random.default_rng(1)
    for s in [0, 65535, 9, 61455, 22, 32777, 36864] + rng.integers(0, NC, 13).tolist():
        for k, t in enumerate(m2_exact_gains(int(s))):
            ex = np.array([float(x) for x in t])
            fl = beta[s, k]
            cos = ex @ fl / (np.linalg.norm(ex) * np.linalg.norm(fl))
            assert cos > 1 - 1e-9, "resident %d, flip %d: float bracket %s vs exact gain %s" % (s, k, fl, ex)
    strict = np.zeros((512, NC), bool)
    weak = np.zeros((512, NC), bool)
    nref, refres = 0, set()
    rel, drel = np.inf, 0.0
    for i in range(512):
        u, v = float(G["u"][i]), float(G["v"][i])
        val = beta[:, :, 0] + u * beta[:, :, 1] + v * beta[:, :, 2]
        S = np.abs(beta[:, :, 0]) + abs(u) * np.abs(beta[:, :, 1]) + abs(v) * np.abs(beta[:, :, 2])
        D = np.abs(dbeta[:, :, 0]) + abs(u) * np.abs(dbeta[:, :, 1]) + abs(v) * np.abs(dbeta[:, :, 2])
        rel, drel = min(rel, float((np.abs(val) / S).min())), max(drel, float((D / S).max()))
        err = MARGIN_DIFF * D + MARGIN_REL * S
        pos, neg = val > err, val < -err
        und = ~(pos | neg)
        # a resident is decided without exact arithmetic if one flip certainly gains, or all certainly lose
        dec_not = pos.any(1)
        dec_strict = neg.all(1)
        todo = np.nonzero(~dec_not & ~dec_strict)[0]
        strict[i] = dec_strict
        weak[i] = dec_strict
        if len(todo):
            U, V = F(u), F(v)
            for s in todo:
                gains = [at(t, U, V) for t in m2_exact_gains(int(s))]
                strict[i, s] = all(x < 0 for x in gains)
                weak[i, s] = all(x <= 0 for x in gains)
            nref += int(und[todo].sum())
            refres.update(todo.tolist())
    # the exact route decides a sample of (game, resident) verdicts too, as a check on the float route: the pairs of
    # m2_float64_check.csv's kind (ALLC and its neighbours in the Stag Hunt and Harmony games), the Snowdrift strict
    # equilibria that cycle CC, DD, and random ones
    spot = [(1, 65535), (3, 63359), (3, 63903), (72, 65535), (2, 36864), (7, 36878), (0, 0), (0, 32777)]
    spot += list(zip(rng.integers(0, 512, 24).tolist(), rng.integers(0, NC, 24).tolist()))
    for i, s in spot:
        U, V = F(float(G["u"][i])), F(float(G["v"][i]))
        assert all(at(t, U, V) < 0 for t in m2_exact_gains(s)) == strict[i, s], (i, s)
    return strict, weak, dict(float_s=t1 - t0, total_s=time.time() - t0, referred_signs=nref, referred_residents=len(refres),
                              rel=rel, drel=drel, nspot=len(spot))


def main():
    G = games.games()
    t0 = time.time()
    strict1, weak1, strict16 = memory_one(G)
    T1 = tables.read_table(os.path.join(HERE, "m1_games.csv"))
    S1 = tables.read_table(os.path.join(HERE, "m1_sets.csv"))
    dep1 = np.zeros((512, 16), bool)
    dep1[S1["ipt"], S1["s"]] = True
    dmask = ((T1["strict_mask"][:, None] >> np.arange(16)) & 1).astype(bool)
    print("memory one (exact, %.1f s): %d strict (game, strategy) pairs; weak = strict at all games: %s; strict among the 16 "
          "= strict against all 65536 memory-two deviations: %s" % (time.time() - t0, strict1.sum(),
                                                                   np.array_equal(weak1, strict1), np.array_equal(strict16, strict1)))
    print("   agrees with m1_sets.csv and the masks of m1_games.csv at every (game, strategy): %s"
          % (np.array_equal(strict1, dep1) and np.array_equal(strict1, dmask)))
    assert np.array_equal(strict1, dep1) and np.array_equal(strict1, dmask)
    assert np.array_equal(weak1, strict1) and np.array_equal(strict16, strict1)

    strict2, weak2, rec = memory_two(G)
    S2 = tables.read_table(os.path.join(HERE, "m2_sets.csv"))
    dep2 = np.zeros((512, NC), bool)
    dep2[S2["ipt"], S2["s"]] = True
    print("memory two (%.0f s, of which %.0f s the float brackets of all 65536 residents): %d strict (game, strategy) pairs; "
          "weak = strict at all games: %s" % (rec["total_s"], rec["float_s"], strict2.sum(), np.array_equal(weak2, strict2)))
    print("   smallest |bracket| / (sum of its absolute terms) over all 512 x 65536 x 16 signs: %.3g; largest difference "
          "of the two float computations, relative to the same sum: %.3g" % (rec["rel"], rec["drel"]))
    print("   signs referred to exact arithmetic: %d, of %d residents; %d further (game, resident) verdicts decided exactly "
          "as a check, all agreeing" % (rec["referred_signs"], rec["referred_residents"], rec["nspot"]))
    only_here, only_dep = strict2 & ~dep2, dep2 & ~strict2
    print("   agrees with m2_sets.csv at every one of the 512 x 65536 (game, strategy) pairs: %s (%d found only here, %d only "
          "in the table)" % (not (only_here.any() or only_dep.any()), only_here.sum(), only_dep.sum()))
    assert not (only_here.any() or only_dep.any()) and np.array_equal(weak2, strict2)
    # the strict equilibria of the Snowdrift games: their self-play near the limit (eps = 1e-8, by state reduction)
    sd = np.nonzero(G["quadrant"] == "SD")[0]
    res = np.unique(np.nonzero(strict2[sd])[1])
    P, _, _ = selfplay(res, 1e-8)
    pi = gth(P)
    w = np.round(np.stack([pi[:, 4 * o:4 * o + 4].sum(1) for o in range(4)], 1), 4)
    kinds = {}
    for s, x in zip(res, map(tuple, w)):
        kinds.setdefault(x, []).append(int(s))
    print("   the %d strict equilibria of the %d Snowdrift games that have one, by self-play (w_CC, w_CD, w_DC, w_DD) at "
          "eps = 1e-8: %s" % (len(res), int(strict2[sd].any(1).sum()),
                              "; ".join("%s: %d" % (k, len(v)) for k, v in sorted(kinds.items(), reverse=True))))
    print("all sets reproduced")


if __name__ == "__main__":
    main()
