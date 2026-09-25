#!/usr/bin/env python3
"""
check_bays.py -- the lines that bound the bays of the atom 110 (../bays-and-cycles.md), recomputed.

Each line is the stability condition of one "last forgiving" partner: on one side the partner is a Nash equilibrium, on
the other a co-player exploits its forgiveness with play that pays more than the partner's self-play.  For each
(strategy, line) this script takes two games just either side of the line, computes at eps = 1e-6 the partner's
payoff against itself and the payoff of its best co-player among all 65536 memory-two strategies (every co-player of
any memory is no better: SI section 2), and checks that

  * on the stable side the best co-player earns no more than the partner's self-play (up to 1e-4, the order of eps
    effects; ties are admitted in the limit), and
  * on the other side the best co-player earns more, and its gain in the limit eps -> 0 (from its limiting outcome
    frequencies, as exact fractions) is a positive multiple of the line's own linear form, so that the line is the
    boundary; and that the co-player's limiting play is the one the note gives: the cycles of the error-free pair
    (partner against co-player) between which it divides its time, each with the weight the limit eps -> 0 gives it.
    Every other co-player whose limiting play gives it the same shares of R, S, T, P is checked to play the same
    cycles.

The partner's self-play is also checked to be E_max = max(R, (S + T)/2) to 1e-4 (the partner is efficient).
Units: (R, S, T, P) = (1, u, 1 + v, 0).  Each game is placed at distance d = 0.02 (in v, or in u for the line u = 6)
from the line, at a point of the bay chosen here.

Finally, against the exact arrangement in ../../data/arrangement (m2_faces.csv and the disk polygons of
m2_faces_k4.npz): the atom 110 is empty on exactly the polygons of the three bays, the Prisoner's Dilemma with v > 2,
u + 2v > 2, 3u + v < -1, the part of E with u + 3v < -1 and the part of S with u > 6, 5u + 4v > 6, and the two
Harmony bays cover 3.0% and 0.3% of the area of the disk.

    python3 check_bays.py          (about 20 s)
"""
import csv, os, sys
import numpy as np
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pairchain as pc

EPS, TOL, D = 1e-6, 1e-4, 0.02
# strategy; the line, written so that the stable side is a + b u + c v >= 0; a point on the line; the step to the
# stable side; the exploiting play the note gives, as a list of (a cycle of the error-free pair, written as the co-player's
# payoffs round by round, and its weight in the limit eps -> 0); the bay
CASES = [
    (32777, "v <= 2", (2, 0, -1), (-3.0, 2.0), (0, -D), [("TPP", 1)], "Prisoner's Dilemma bay, below the switch line"),
    (18567, "u + 2v <= 2", (2, -1, -2), (-2.5, 2.25), (0, -D), [("TTSP", 1)],
     "Prisoner's Dilemma bay, below the switch line"),
    (18050, "3u + v >= -1", (1, 3, 1), (-3.0, 8.0), (0, +D), [("SPTTP", 1)],
     "Prisoner's Dilemma bay, above the switch line"),
    (11781, "u + 3v >= -1", (1, 1, 3), (3.0, -4 / 3), (0, +D), [("RSSTP", 1)], "Harmony bay, wedge E"),
    (15877, "u + 3v >= -1", (1, 1, 3), (3.0, -4 / 3), (0, +D), [("RSSTP", 1)], "Harmony bay, wedge E"),
    (24069, "u + 3v >= -1", (1, 1, 3), (3.0, -4 / 3), (0, +D), [("ST", F(5, 8)), ("SPR", F(3, 8))], "Harmony bay, wedge E"),
    (46919, "u <= 6", (6, -1, 0), (6.0, -5.5), (-D, 0), [("RP", F(4, 5)), ("SP", F(1, 5))], "Harmony sliver of the wedge S"),
    (4599, "5u + 4v <= 6", (6, -5, -4), (7.0, -7.25), (0, -D), [("TR", F(8, 15)), ("RP", F(2, 15)), ("S", F(1, 3))],
     "Harmony sliver of the wedge S"),
]
PAY = "RTSP"                     # the co-player's payoff when the partner's most recent outcome is CC, CD, DC, DD


def frac(x):
    return F(float(x)).limit_denominator(64)


def shares(x):
    return ", ".join("%s %s" % (n, q) for n, q in zip("RSTP", x))


def form(a, b, c):
    return " ".join(("%+d" % k) + t for k, t in ((a, ""), (b, " u"), (c, " v")) if k).lstrip("+")


def cycles(s, t):
    """the cycles of the error-free pair s against t (states of s's chain), and the weight of each in the limit"""
    nxt = [int(np.argmax(row)) for row in pc.transition(s, [t], 0.0)[0]]
    found = []
    for j in range(16):
        path, k = [], j
        while k not in path:
            path.append(k); k = nxt[k]
        cyc = path[path.index(k):]
        if set(cyc) not in [set(c) for c in found]:
            found.append(cyc)
    x = pc.gth(pc.transition(s, [t], 1e-10))[0]
    out = []
    for cyc in found:
        w = frac(sum(x[k] for k in cyc))
        if w > 0:
            out.append(("".join(PAY[k >> 2] for k in cyc), w))
    return out


def canon(play):
    """a play as a sorted list of (cycle up to rotation, weight)"""
    return sorted((min(c[i:] + c[:i] for i in range(len(c))), F(w)) for c, w in play)


def described(play):
    return "; ".join("%s with weight %s" % (", ".join(c), w) for c, w in play)


ok = True
for s, line, (a, b, c), (u0, v0), (du, dv), spec, where in CASES:
    W = pc.stationary(s, np.arange(pc.NC), EPS)                # s's view against every co-player
    Wss = pc.stationary(s, [s], EPS)[0]
    print("%5d %s  %s, the line %s" % (s, pc.genome(s), where, line))
    for side, (u, v) in (("stable side", (u0 + du, v0 + dv)), ("other side", (u0 - du, v0 - dv))):
        R, S, T, P = pc.game(u, v)
        emax = max(R, (S + T) / 2)
        own, co = pc.pays(W, u, v)
        self_ = (Wss @ pc.game(u, v)).item()
        t_ = int(co.argmax())
        gain = co[t_] - self_
        eff = abs(self_ - emax) < TOL
        line_val = a + b * u + c * v
        if side == "stable side":
            this = eff and gain <= TOL and line_val > 0
            print("   %-11s (u, v) = (%6.3f, %6.3f): self-play %.6f = E_max %.6f; best co-player %5d earns %.6f   %s"
                  % (side, u, v, self_, emax, t_, co[t_], "PASS" if this else "FAIL"))
        else:
            # the best co-player's limiting play: its payoff shares (R, T, S, P from s's view: w0, w1, w2, w3)
            Wl = [frac(x) for x in pc.stationary(s, [t_], 1e-10)[0]]
            Ws = [frac(x) for x in pc.stationary(s, [s], 1e-10)[0]]
            got = (Wl[0], Wl[2], Wl[1], Wl[3])                 # the exploiter's shares of R, S, T, P
            want = tuple(sum(F(w) * F(c.count(x), len(c)) for c, w in spec) for x in "RSTP")
            # its gain over the partner's self-play in the limit, g0 + gu u + gv v (R = 1, S = u, T = 1 + v, P = 0)
            g0 = Wl[0] + Wl[1] - Ws[0] - Ws[2]; gu = Wl[2] - Ws[1]; gv = Wl[1] - Ws[2]
            k = -g0 / a if a else (-gu / b)
            same_line = k > 0 and (g0, gu, gv) == (-k * a, -k * b, -k * c)
            cyc = cycles(s, t_)
            same_play = got == want and canon(cyc) == canon(spec)
            # every co-player whose limiting play gives it the same shares: does it play the same cycles?
            Wall = pc.stationary(s, np.arange(pc.NC), 1e-10)
            tied = np.where(np.abs(Wall[:, [0, 2, 1, 3]] - np.array([float(x) for x in got])).max(axis=1) < 1e-6)[0]
            all_same = all(canon(cycles(s, int(x))) == canon(cyc) for x in tied)
            this = eff and gain > TOL and line_val < 0 and same_line and same_play and all_same
            print("   %-11s (u, v) = (%6.3f, %6.3f): self-play %.6f = E_max %.6f; best co-player %5d %s earns %.6f"
                  % (side, u, v, self_, emax, t_, pc.genome(t_), co[t_]))
            print("              its gain over the self-play in the limit: %s + %s u + %s v = %s x (%s): %s"
                  % (g0, gu, gv, k, form(-a, -b, -c), "the line of the note" if same_line else "NOT the line of the note"))
            print("              its limiting play: %s, in cycles of the error-free pair: %s"
                  % (shares(got), described(cyc)))
            print("              %d co-players get these shares, %s"
                  % (len(tied), "all with the same cycles" if all_same else "NOT all with the same cycles"))
            print("              the note's play, %s: %s   %s"
                  % (described(spec), "the same" if same_play else "DIFFERENT (%s)" % shares(want), "PASS" if this else "FAIL"))
        ok &= this

# the bays in the exact arrangement
ARR = os.path.join(HERE, os.pardir, os.pardir, "data", "arrangement")
rows = list(csv.DictReader(l for l in open(os.path.join(ARR, "m2_faces.csv")) if not l.startswith("#")))
Z = np.load(os.path.join(ARR, "m2_faces_k4.npz"))
V, OFF = Z["verts"], Z["offsets"]
assert len(rows) == len(OFF) - 1


def area(Pg):
    x, y = Pg[:, 0], Pg[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


A = np.array([area(V[OFF[i]:OFF[i + 1]]) for i in range(len(rows))])
u = np.array([float(r["u"]) for r in rows]); v = np.array([float(r["v"]) for r in rows])
q = np.array([r["quadrant"] for r in rows]); w = np.array([r["wedge"] for r in rows])
empty = np.array([int(r["A_110"]) == 0 for r in rows])
pd_bay = (q == "PD") & (v > 2) & (u + 2 * v > 2) & (3 * u + v < -1)
e_bay = (q == "HA") & (w == "E") & (u + 3 * v < -1)
s_bay = (q == "HA") & (w == "S") & (u > 6) & (5 * u + 4 * v > 6)
same = bool(np.array_equal(empty, pd_bay | e_bay | s_bay))
ok &= same
print("110 is empty on exactly the polygons of the three bays (%d of the %d polygons of m2_faces.csv): %s"
      % (int(empty.sum()), len(rows), "PASS" if same else "FAIL"))
tot = A.sum()
for name, m, want in (("the part of E with u + 3v < -1", e_bay, "3.0"), ("the sliver of S", s_bay, "0.3")):
    pc_ = 100 * A[m].sum() / tot
    this = "%.1f" % pc_ == want
    ok &= this
    print("the Harmony bay %s covers %.2f%% of the disk (the passage: %s%%)   %s"
          % (name, pc_, want, "PASS" if this else "FAIL"))
print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
