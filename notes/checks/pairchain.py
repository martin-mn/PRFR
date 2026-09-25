"""
pairchain.py -- the 16-state Markov chain of two binary memory-two strategies playing with execution errors, in
numpy, for checking the numbers in the notes.

Convention (the paper's Methods and the simulator's payf2.f/payf3.f): the state is j = 4 (most recent outcome) +
(the outcome before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 seen from the player's own side (own move first); bit j
of a strategy's code is 1 if it cooperates in state j, so that the genome, read as the positions 0..15 from the left,
is the binary expansion of the code with the lowest bit first.  ALLD = 0, ALLC = 65535, TFT = 3855, WSLS = 61455,
Grim = 1.  Each intended move is flipped with probability eps, independently.  The game is (R, S, T, P) = (1, u, 1 + v, 0).

stationary(sig, taus, eps) returns W, shape (n, 4): the stationary frequencies of the most recent outcome CC, CD, DC,
DD from sig's side, for sig against every tau in taus.  The chain is solved by the state-reduction algorithm of
Grassmann, Taksar and Heyman (subtraction-free), vectorised over the co-players, so small eps (1e-6) is safe.
sig's per-round payoff is W @ (R, S, T, P) and tau's is W @ (R, T, S, P).
"""
import numpy as np

NC = 65536
ALLD, ALLC, TFT, WSLS, GRIM = 0, 65535, 3855, 61455, 1
EIGHT = [19079, 19087, 20103, 20111, 23175, 23183, 24199, 24207]
SW = [0, 2, 1, 3]                                   # CD <-> DC: the co-player's view of an outcome


def genome(s):
    return "".join("C" if (s >> j) & 1 else "D" for j in range(16))


def code(g):
    """code of a genome written with 1/0 or C/D, position 0 first"""
    g = g.replace("C", "1").replace("D", "0")
    assert len(g) == 16 and set(g) <= {"0", "1"}, g
    return sum(1 << j for j, c in enumerate(g) if c == "1")


def transition(sig, taus, eps):
    """(n, 16, 16) transition matrices of sig (an int, or an array like taus) against each tau in taus"""
    taus = np.atleast_1d(np.asarray(taus, dtype=np.int64))
    sigs = np.broadcast_to(np.asarray(sig, dtype=np.int64), taus.shape)
    n = taus.size
    P = np.zeros((n, 16, 16))
    rows = np.arange(n)
    for j in range(16):
        o1, o0 = j >> 2, j & 3
        jt = 4 * SW[o1] + SW[o0]
        ps = np.where((sigs >> j) & 1 == 1, 1 - eps, eps)       # prob that sig plays C
        pt = np.where((taus >> jt) & 1 == 1, 1 - eps, eps)      # prob that tau plays C
        for dS in (0, 1):                                        # 0: sig plays C, 1: D
            for dT in (0, 1):
                p = (ps if dS == 0 else 1 - ps) * (pt if dT == 0 else 1 - pt)
                P[rows, j, 4 * (2 * dS + dT) + o1] += p
    return P


def gth(P):
    """stationary distributions of a batch of stochastic matrices (n, m, m), Grassmann-Taksar-Heyman"""
    P = P.copy()
    n, m, _ = P.shape
    for k in range(m - 1, 0, -1):
        s = P[:, k, :k].sum(axis=1)                  # (n,)
        P[:, :k, k] /= s[:, None]
        P[:, :k, :k] += P[:, :k, k][:, :, None] * P[:, k, :k][:, None, :]
    x = np.zeros((n, m)); x[:, 0] = 1.0
    for k in range(1, m):
        x[:, k] = (x[:, :k] * P[:, :k, k]).sum(axis=1)
    return x / x.sum(axis=1, keepdims=True)


def stationary(sig, taus, eps, chunk=16384):
    taus = np.atleast_1d(np.asarray(taus, dtype=np.int64))
    out = np.empty((taus.size, 4))
    for a in range(0, taus.size, chunk):
        x = gth(transition(sig, taus[a:a + chunk], eps))
        out[a:a + chunk] = x.reshape(-1, 4, 4).sum(axis=2)      # the most recent outcome is j >> 2
    return out


def selfplay_all(eps, chunk=16384):
    """W of every strategy against itself, (65536, 4)"""
    out = np.empty((NC, 4))
    for a in range(0, NC, chunk):
        s = np.arange(a, min(NC, a + chunk))
        out[a:a + chunk] = gth(transition(s, s, eps)).reshape(-1, 4, 4).sum(axis=2)
    return out


def game(u, v):
    return np.array([1.0, u, 1.0 + v, 0.0])


def pays(W, u, v):
    """(own payoff, co-player's payoff) per round from W (own view)"""
    R, S, T, P = game(u, v)
    return W @ np.array([R, S, T, P]), W @ np.array([R, T, S, P])
