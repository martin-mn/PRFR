#!/usr/bin/env python3
"""
check_discounting.py -- the bound of ../discounting.md, recomputed: with the discounted payoff
pi_delta = (1 - delta) sum_t delta^(t-1) pi_t, tit-for-tat, Grim and the eight friendly rivals of the wedge W, started
cooperatively and without errors, are behind their best-placed co-player by exactly one exploited round,
(1 - delta)(T - S), where T > S: the bound of the theorem is attained.

A strategy is taken with an explicit start, as in the notes: a first move and a second move after each first-round
outcome; "started cooperatively" is first move C and, after the first round, the strategy's own memory-two answer as
if the round before the first had been mutual cooperation (second move after outcome o = its answer in state (o, CC)).
Against a fixed sigma, the largest relative payoff max_tau [pi(tau, sigma) - pi(sigma, tau)] over ALL co-players is a
discounted Markov decision problem on sigma's 21 history states (the start, the four first-round outcomes, the 16
memory-two states), whose optimum is attained by a deterministic stationary policy; it is solved here by value
iteration to 1e-13.  In units of T - S the reward is +1 when sigma cooperates and tau defects and -1 in the reverse
case, so the result does not depend on the game as long as T > S.  With errors (eps = 1e-4) the same computation shows
that the deficit stays strictly positive (every intended cooperation is behind ALLD); it is of order one exploited
round, and ALLD comes within 1e-7 of the best co-player.  Finally, where T < S, ALLC is never behind any co-player at
any delta and any eps < 1/2 (the maximum is 0, attained by ALLC itself).

    python3 check_discounting.py          (a few seconds)
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairchain as pc

SW = [0, 2, 1, 3]


def own_action(s16, first, second, h):
    """sigma's intended action (1 = C) in history state h: 0..15 memory, 16 start, 17 + o after the first round"""
    if h < 16:
        return (s16 >> h) & 1
    if h == 16:
        return first
    return second[h - 17]


def nxt(h, o):
    """history state after outcome o (sigma's view)"""
    if h == 16:
        return 17 + o
    if h >= 17:
        return 4 * o + (h - 17)          # after the second game round: recent o, before = the first-round outcome
    return 4 * o + (h >> 2)


def max_relative(s16, delta, eps, first=1, second=None, tol=1e-13, sign=1):
    """max over all co-players of (pi(tau, sigma) - pi(sigma, tau)) / |T - S| (sign = +1: T > S, -1: T < S), and
    the value of ALLD's play"""
    if second is None:
        second = [(s16 >> (4 * o)) & 1 for o in range(4)]      # started cooperatively: as after (o, CC)
    H = 21
    a = np.array([own_action(s16, first, second, h) for h in range(H)])
    pC = np.where(a == 1, 1 - eps, eps)                           # prob sigma plays C in state h
    # for tau's intended action b (1 = C): probabilities of the four outcomes, and the reward
    P = np.zeros((2, H, 4)); r = np.zeros((2, H))
    for b in (0, 1):
        qC = (1 - eps) if b == 1 else eps
        for o, (sc, tc) in enumerate(((1, 1), (1, 0), (0, 1), (0, 0))):   # CC, CD, DC, DD from sigma's side
            P[b, :, o] = (pC if sc else 1 - pC) * (qC if tc else 1 - qC)
        r[b] = sign * (P[b, :, 1] - P[b, :, 2])                   # T > S: sigma exploited (+1), sigma exploiting (-1)
    N = np.array([[nxt(h, o) for o in range(4)] for h in range(H)])
    V = np.zeros(H)
    while True:
        Q = (1 - delta) * r + delta * (P * V[N][None]).sum(axis=2)
        Vn = Q.max(axis=0)
        if np.abs(Vn - V).max() < tol * (1 - delta):
            V = Vn
            break
        V = Vn
    # ALLD's value, the policy b = 0 everywhere
    Va = np.zeros(H)
    for _ in range(200000):
        Van = (1 - delta) * r[0] + delta * (P[0] * Va[N]).sum(axis=1)
        if np.abs(Van - Va).max() < tol * (1 - delta):
            Va = Van
            break
        Va = Van
    return V[16], Va[16]


ok = True
cases = [("TFT", pc.TFT), ("Grim", pc.GRIM)] + [(str(s), s) for s in pc.EIGHT]
print("max over all co-players of (pi(tau,sigma) - pi(sigma,tau)) / (T - S), started cooperatively, eps = 0:")
print("   %-7s %s" % ("sigma", "   ".join("delta = %-6g" % d for d in (0.9, 0.99, 0.999))))
for name, s in cases:
    vals = [max_relative(s, d, 0.0) for d in (0.9, 0.99, 0.999)]
    good = all(abs(v - (1 - d)) < 1e-10 and abs(va - (1 - d)) < 1e-10 for (v, va), d in zip(vals, (0.9, 0.99, 0.999)))
    ok &= good
    print("   %-7s %s   %s" % (name, "   ".join("%.10f  " % v for v, va in vals),
                                "= 1 - delta, attained by ALLD   PASS" if good else "FAIL"))
print("with errors, eps = 1e-4: the maximum, and by how much ALLD falls short of it:")
for name, s in cases:
    vals = [max_relative(s, d, 1e-4) for d in (0.9, 0.99, 0.999)]
    good = all(va > 0 and v - va < 1e-7 for v, va in vals)
    ok &= good
    print("   %-7s %s   %s" % (name, "   ".join("%.6f (%.1e)" % (v, v - va) for v, va in vals), "PASS" if good else "FAIL"))
print("where T < S (the wedge S): ALLC, started cooperatively, is never behind any co-player, at every delta and eps < 1/2:")
for d in (0.9, 0.99, 0.999):
    vals = [max_relative(pc.ALLC, d, e, sign=-1)[0] for e in (0.0, 1e-4, 0.1, 0.4)]
    good = all(v <= 1e-12 for v in vals)
    ok &= good
    print("   delta = %-6g  max relative payoff of a co-player at eps = 0, 1e-4, 0.1, 0.4: %s   %s"
          % (d, "  ".join("%.1e" % v for v in vals), "PASS" if good else "FAIL"))
print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
