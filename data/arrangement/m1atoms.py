#!/usr/bin/env python3
"""
The seven atoms of the three properties -- efficient, stable, competitive -- for the 2^4 = 16 binary memory-one
strategies, exactly, in the limit eps -> 0, over the whole plane of games: the data behind Figures 1b, 2a-g and 3a-d.

    python3 m1atoms.py          rebuilds the arrangement from scratch in rational arithmetic (about a minute), prints
                                the census and checks that it is, bit for bit, what m1_faces_k4.npz, m1_faces.csv and
                                m1_lines.csv of this folder hold
    python3 m1atoms.py m2       ... and checks the 16 against all 65536 memory-two co-players, with the memory-two
                                stability polygons, efficiency and rivalry of this folder (m2_*.csv)

This is FinalFigures/m1atoms.py of the working tree, unchanged in its computation.  Only the input and output
changed: it no longer caches its result in ../Figures/m1_atoms_k4.npz but compares it with the deposited files
(which provenance/census-figs/reduce.py copied from that cache), and the check against the memory-two layer reads
the deposited memory-two tables instead of DiskM2WF/Opt/exact.py.  A comparison with a sibling project's
independent memory-one census (CL1/PartnersRivalsM1, not deposited) is omitted; it agreed on all 256 pair limits.

CONVENTION.  A memory-one strategy answers the last round's outcome, own action first, CC, CD, DC, DD; we
write it by its four answers, so ALLC is CCCC, ALLD is DDDD, tit-for-tat CDCD, win-stay lose-shift CDDC and
Grim CDDD (the SI's notation).  Internally bit k of s (k = 0..3 for CC, CD, DC, DD) is 1 for C.  Payoffs
(R, S, T, P) = (1, u, 1 + v, 0).

METHOD.  For every ordered pair the stationary distribution of the four-state chain with independent
implementation errors is an exact rational function of eps: by the Markov chain tree theorem pi_o is
proportional to the (o, o) cofactor of I - P(eps), a polynomial in eps with integer coefficients, and the
limit eps -> 0 is the ratio of the leading coefficients.  Everything is done in Fractions; there is no
threshold anywhere.  The limit payoff of i against j is then a linear function of
(u, v) with rational coefficients, and at a rational game the three properties are decided exactly:
efficient   pi(i, i) = Emax = max(R, (S + T)/2), the largest average any pair of the 16 can earn;
stable      pi(i, i) >= pi(j, i) for all 16 j (ties allowed);
competitive pi(i, j) >= pi(j, i) for all 16 j.
The classification can change only across the lines pi(i, i) = pi(j, i) (stability), u - v = 1 (T = S, where
competitiveness changes: pi(i, j) - pi(j, i) = (T - S)(w_DC - w_CD)) and u + v = 1 (the switch line, where
Emax changes); the arrangement of the lines that actually matter is built by convex clipping over
|u|, |v| <= RB, each face is classified at two different interior rational points (which must agree, so no
face is judged on a measure-zero stability region), and the faces are mapped onto the projective disk
(K = 4) with the adaptive conic subdivision of common.disk.arc.  Faces of the arrangement are the regions on
which the 16 codes are constant, up to merging across a line that is active elsewhere.
"""
import os
import sys
from fractions import Fraction as F
from math import gcd

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))
from common import disk as disklib                               # noqa: E402  phi and arc, as in disklib.py

K = 4.0
RB = 2000.0            # the plane is clipped here; the image of the box is 1 - 2e-6 from the rim
TOL = 1e-5             # max departure of a drawn edge from its true conic
NS = 4
ORDER = ["000", "100", "010", "001", "110", "011", "111"]
NAME = {"000": "none of the three", "100": "efficient only", "010": "stable only", "001": "competitive only",
        "110": "efficient and stable only", "011": "stable and competitive only", "111": "efficient, stable and competitive"}
NICK = {15: "ALLC", 0: "ALLD", 5: "TFT", 9: "WSLS", 1: "Grim"}


def genome(s):
    return "".join("C" if (s >> k) & 1 else "D" for k in range(NS))


def swapo(o):
    """the same round seen from the co-player's side: CD <-> DC"""
    return ((o & 1) << 1) | (o >> 1)


# ------------------------------------------------------------- polynomials in eps, exact
def padd(p, q):
    n = max(len(p), len(q))
    return [(p[k] if k < len(p) else F(0)) + (q[k] if k < len(q) else F(0)) for k in range(n)]


def pmul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                out[i + j] += a * b
    return out


def pneg(p):
    return [-a for a in p]


def transition(sig, tau):
    """P[o][o'] as polynomials in eps: from outcome o (sig's side) sig intends bit o of sig, tau intends
    bit swapo(o) of tau, each realises the other action with probability eps, independently"""
    EPS, ONE_M = [F(0), F(1)], [F(1), F(-1)]
    P = [[[F(0)] for _ in range(NS)] for _ in range(NS)]
    for o in range(NS):
        cs, ct = (sig >> o) & 1, (tau >> swapo(o)) & 1
        for a in (0, 1):                                            # sig's realised action, 1 = C
            pa = ONE_M if a == cs else EPS
            for b in (0, 1):                                        # tau's
                pb = ONE_M if b == ct else EPS
                nxt = 2 * (1 - a) + (1 - b)
                P[o][nxt] = padd(P[o][nxt], pmul(pa, pb))
    return P


def det3(M):
    """Leibniz, for a 3 x 3 matrix of polynomials"""
    (a, b, c), (d, e, f), (g, h, i) = M
    t = padd(padd(pmul(a, padd(pmul(e, i), pneg(pmul(f, h)))),
                  pneg(pmul(b, padd(pmul(d, i), pneg(pmul(f, g)))))),
             pmul(c, padd(pmul(d, h), pneg(pmul(e, g)))))
    return t


def limit_weights(sig, tau):
    """the eps -> 0 limit of the stationary distribution (w_CC, w_CD, w_DC, w_DD) from sig's side"""
    P = transition(sig, tau)
    L = [[padd([F(1) if o == p else F(0)], pneg(P[o][p])) for p in range(NS)] for o in range(NS)]
    cof = []
    for o in range(NS):
        M = [[L[r][c] for c in range(NS) if c != o] for r in range(NS) if r != o]
        cof.append(det3(M))                                         # the weighted count of in-trees rooted at o
    order = [next((k for k, a in enumerate(c) if a != 0), None) for c in cof]
    kmin = min(k for k in order if k is not None)
    lead = [cof[o][kmin] if order[o] == kmin else F(0) for o in range(NS)]
    assert all(a >= 0 for a in lead) and sum(lead) > 0, (sig, tau, lead)
    tot = sum(lead)
    return tuple(a / tot for a in lead)


W = {(s, t): limit_weights(s, t) for s in range(16) for t in range(16)}
for (s, t), w in W.items():
    assert sum(w) == 1 and W[(t, s)] == (w[0], w[2], w[1], w[3]), (s, t)   # the co-player's view swaps CD and DC
for s in range(16):
    assert W[(s, s)][1] == W[(s, s)][2]


def pay(w, u, v):
    return w[0] + w[1] * u + w[2] * (1 + v)


def emax(u, v):
    return max(F(1), (1 + u + v) / 2)


def codes_at(u, v, check_emax=True):
    """the atom code (4 efficient + 2 stable + competitive) of each of the 16 at the rational game (u, v)"""
    u, v = F(u), F(v)
    A = [[pay(W[(i, j)], u, v) for j in range(16)] for i in range(16)]
    em = emax(u, v)
    if check_emax:
        assert max((A[i][j] + A[j][i]) / 2 for i in range(16) for j in range(16)) == em, (u, v)
    out = []
    for i in range(16):
        eff = A[i][i] == em
        nash = all(A[i][i] >= A[j][i] for j in range(16))
        comp = all(A[i][j] >= A[j][i] for j in range(16))
        out.append(4 * eff + 2 * nash + comp)
    return out


# ------------------------------------------------------------------- the candidate lines
def normalise(A, B, C):
    """integer (A, B, C) with A u + B v + C = 0, gcd 1, first non-zero positive"""
    den = 1
    for x in (A, B, C):
        den = den * x.denominator // gcd(den, x.denominator)
    A, B, C = int(A * den), int(B * den), int(C * den)
    q = gcd(gcd(abs(A), abs(B)), abs(C)) or 1
    A, B, C = A // q, B // q, C // q
    if (A, B, C) < (0, 0, 0) or (A == 0 and B < 0) or (A == 0 and B == 0 and C < 0) or (A < 0):
        A, B, C = -A, -B, -C
    return (A, B, C)


CAND = {(1, 1, -1), (1, -1, -1)}                                     # the switch line and T = S
for i in range(16):
    for j in range(16):
        if i == j:
            continue
        d = [a - b for a, b in zip(W[(i, i)], W[(j, i)])]           # pi(i, i) - pi(j, i) = (d0 + d2) + d1 u + d2 v
        A, B, C = d[1], d[2], d[0] + d[2]
        if A == 0 and B == 0:
            continue                                                # a constant difference: no line
        CAND.add(normalise(A, B, C))
CAND = sorted(CAND)


# ------------------------------------------------------------------- the arrangement
def clip(poly, a, b, c, keep, tol):
    """the part of the convex polygon with keep * (a x + b y + c) >= 0"""
    out, n = [], len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        sp = (a * p[0] + b * p[1] + c) * keep
        sq = (a * q[0] + b * q[1] + c) * keep
        if sp >= -tol:
            out.append(p)
        if (sp > tol and sq < -tol) or (sp < -tol and sq > tol):
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out if len(out) >= 3 else None


def arrangement(lines):
    cells = [[(-RB, -RB), (RB, -RB), (RB, RB), (-RB, RB)]]
    for (a, b, c) in lines:
        nxt = []
        sc = max(abs(a), abs(b), 1) * RB * 1e-12
        for poly in cells:
            s = [a * x + b * y + c for x, y in poly]
            if min(s) >= -sc or max(s) <= sc:
                nxt.append(poly)
                continue
            for keep in (1, -1):
                p2 = clip(poly, a, b, c, keep, sc)
                if p2:
                    nxt.append(p2)
        cells = nxt
    area = np.array([abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1]
                             for i in range(len(p)))) / 2 for p in cells])
    assert abs(area.sum() / (4 * RB * RB) - 1) < 1e-9, "the faces do not tile the box"
    return cells, area


def interior(poly, seed):
    """a rational game strictly inside the convex face: a convex combination of its vertices with generic
    weights (a face symmetric about an axis has its plain centroid on the axis, where a measure-zero
    stability region may live)"""
    n = len(poly)
    w = [F(7 + ((seed * 13 + k * 5) % 11), 7) for k in range(n)]
    tot = sum(w)
    u = sum(F(x).limit_denominator(10 ** 9) * wk for (x, _), wk in zip(poly, w)) / tot
    v = sum(F(y).limit_denominator(10 ** 9) * wk for (_, y), wk in zip(poly, w)) / tot
    return u, v


def classify(cells):
    codes = []
    for poly in cells:
        c1 = codes_at(*interior(poly, 1))
        c2 = codes_at(*interior(poly, 2))
        assert c1 == c2, "a face is not constant between two interior points (a measure-zero stability region?)"
        codes.append(c1)
    return np.array(codes, int)


def active_lines(cand):
    """the candidate lines across which some strategy's code changes somewhere"""
    cells, _ = arrangement(cand)
    codes = classify(cells)
    cen = [interior(p, 1) for p in cells]
    act = []
    for (a, b, c) in cand:
        # faces with an edge on the line: a vertex pair on it
        onl = []
        for f, poly in enumerate(cells):
            s = [abs(a * x + b * y + c) for x, y in poly]
            if sum(1 for t in s if t < 1e-6 * RB) >= 2:
                onl.append(f)
        side = {}
        for f in onl:
            u, v = cen[f]
            sgn = 1 if a * u + b * v + c > 0 else -1
            side.setdefault(sgn, []).append(f)
        changes = False
        for f in side.get(1, []):
            # its neighbour across the line: the face on the other side sharing the edge
            pf = cells[f]
            ef = [(round(x, 6), round(y, 6)) for x, y in pf if abs(a * x + b * y + c) < 1e-6 * RB]
            for g in side.get(-1, []):
                eg = [(round(x, 6), round(y, 6)) for x, y in cells[g] if abs(a * x + b * y + c) < 1e-6 * RB]
                if len(set(ef) & set(eg)) >= 2 and (codes[f] != codes[g]).any():
                    changes = True
                    break
            if changes:
                break
        if changes:
            act.append((a, b, c))
    return act


def inside(poly, u, v):
    """is the plane point (u, v) inside the convex polygon (vertices in either orientation)"""
    n = len(poly)
    sgn = 0
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        c = (x1 - x0) * (v - y0) - (y1 - y0) * (u - x0)
        if abs(c) < 1e-9 * RB:
            continue
        if sgn == 0:
            sgn = 1 if c > 0 else -1
        elif (c > 0) != (sgn > 0):
            return False
    return True


def build():
    LINES = active_lines(CAND)
    cells, area = arrangement(LINES)
    codes = classify(cells)
    # completeness of the pruning: every face of the full candidate arrangement lies inside one final face
    # and carries its codes, so no line across which anything changes was dropped
    full, _ = arrangement(CAND)
    fcodes = classify(full)
    for f, poly in enumerate(full):
        u, v = interior(poly, 1)
        hits = [g for g, q in enumerate(cells) if inside(q, float(u), float(v))]
        assert len(hits) == 1 and (codes[hits[0]] == fcodes[f]).all(), "a face of the full arrangement is misclassified"
    uvc = np.array([[float(x) for x in interior(p, 1)] for p in cells])
    atoms = np.zeros((len(cells), 8), int)
    for f in range(len(cells)):
        atoms[f] = np.bincount(codes[f], minlength=8)
    assert (atoms[:, 5] == 0).all(), "101 is not empty: an efficient competitive strategy is stable"
    assert (atoms.sum(1) == 16).all()

    def phi(p):
        return disklib.phi(p, K)

    verts, off = [], [0]
    for p in cells:
        pts = []
        n = len(p)
        for i in range(n):
            pts.extend(disklib.arc(p[i], p[(i + 1) % n], phi, TOL))
        verts.append(np.asarray(pts, float))
        off.append(off[-1] + len(pts))
    da = np.array([abs(np.dot(q[:, 0], np.roll(q[:, 1], -1)) - np.dot(q[:, 1], np.roll(q[:, 0], -1))) / 2 for q in verts])
    assert 0 <= (np.pi - da.sum()) / np.pi < 1e-4, "the mapped faces do not tile the disk"
    return dict(cells=cells, area=area, codes=codes, uvc=uvc, atoms=atoms, faces=verts, offsets=np.array(off),
                diskarea=da, lines=np.array(LINES, int))


def pieces(uvc):
    u, v = uvc[:, 0], uvc[:, 1]
    quad = np.where((u < 0) & (v > 0), "PD", np.where((u < 0) & (v < 0), "SH", np.where((u > 0) & (v > 0), "SD", "HA")))
    wedge = np.where(u + v < 1, np.where(u - v < 1, "W", "S"), np.where(u - v < 1, "N", "E"))
    return quad, wedge


# ------------------------------------------------------------------- the census
def census(d):
    faces, da, uvc, codes, atoms, lines = d["faces"], d["diskarea"], d["uvc"], d["codes"], d["atoms"], d["lines"]
    tot = da.sum()
    print("%d active lines of %d candidates: %s" % (len(lines), len(CAND), " ".join("(%d,%d,%d)" % tuple(l) for l in lines)))
    print("%d faces; disk area %.6f" % (len(faces), tot))
    quad, wedge = pieces(uvc)
    piece = np.array([q + "∩" + w for q, w in zip(quad, wedge)])
    print("\natoms (per face count, where present; empty share of the disk; strategies on an open set):")
    for c in ORDER:
        k = int(c, 2)
        vals = atoms[:, k]
        pres = vals > 0
        members = sorted({i for f in range(len(faces)) for i in range(16) if codes[f, i] == k})
        print("  %s  %-33s %s per game; empty on %5.1f%%; %2d strategies: %s"
              % (c, NAME[c], ("%d-%d" % (vals[pres].min(), vals.max())) if pres.any() else "  -", 100 * da[~pres].sum() / tot,
                 len(members), " ".join(genome(i) for i in members)))
    print("\nper strategy: the codes it takes and where")
    for i in range(16):
        parts = {}
        for f in range(len(faces)):
            parts.setdefault(codes[f, i], 0.0)
            parts[codes[f, i]] += da[f]
        print("  %s %-5s %s" % (genome(i), NICK.get(i, ""), "  ".join("%s %5.1f%%" % (format(k, "03b"), 100 * a / tot) for k, a in sorted(parts.items(), key=lambda t: -t[1]))))
    present = np.stack([atoms[:, int(c, 2)] > 0 for c in ORDER], 1)
    key = np.array(["".join("1" if x else "0" for x in row) for row in present])
    uniq = sorted(set(key), key=lambda k: (k.count("0"), -da[key == k].sum()))
    print("\n%d distinct Euler diagrams (patterns of non-empty atoms):" % len(uniq))
    for k in uniq:
        m = key == k
        where = sorted({pc: da[m & (piece == pc)].sum() / tot for pc in np.unique(piece[m])}.items(), key=lambda t: -t[1])
        print("  %s  present %-28s empty %-16s area %5.1f%%  %s"
              % (k, " ".join(c for c, x in zip(ORDER, k) if x == "1"), ",".join(c for c, x in zip(ORDER, k) if x == "0") or "-",
                 100 * da[m].sum() / tot, "  ".join("%s %.1f%%" % (pc, 100 * a) for pc, a in where)))
    # the regions of constancy of the whole code vector
    vec = np.array(["".join(format(x, "03b") for x in row) for row in codes])
    uv = sorted(set(vec), key=lambda k: -da[vec == k].sum())
    print("\n%d distinct code vectors (regions on which who-is-what is constant):" % len(uv))
    for k in uv:
        m = vec == k
        where = sorted({pc: da[m & (piece == pc)].sum() / tot for pc in np.unique(piece[m])}.items(), key=lambda t: -t[1])
        cnt = np.bincount([int(k[3 * i:3 * i + 3], 2) for i in range(16)], minlength=8)
        print("  area %5.1f%%  atoms %s  %s" % (100 * da[m].sum() / tot, " ".join("%s:%d" % (c, cnt[int(c, 2)]) for c in ORDER if cnt[int(c, 2)]),
                                             "  ".join("%s %.1f%%" % (pc, 100 * a) for pc, a in where)))
    return key


def compare(d):
    """the fresh build against the deposited m1_faces_k4.npz, m1_faces.csv and m1_lines.csv: everything bit for bit"""
    sys.path.insert(0, HERE)
    import arrangement
    D = arrangement.m1()
    Z = np.load(os.path.join(HERE, "m1_faces_k4.npz"), allow_pickle=False)
    same = [len(d["faces"]) == len(D["faces"]),
            np.array_equal(np.vstack(d["faces"]), Z["verts"]) and np.array_equal(d["offsets"], Z["offsets"]),
            np.array_equal(d["codes"], D["codes"]), np.array_equal(d["atoms"], D["atoms"]),
            np.array_equal(d["uvc"], D["uvc"]), np.array_equal(d["area"], D["area"]),
            np.array_equal(d["diskarea"], D["diskarea"]), np.array_equal(d["lines"], D["lines"])]
    assert all(same), same
    print("\nthe rebuild equals the deposited memory-one files bit for bit: faces (%d vertices), codes, atoms, interior "
          "games, areas, lines" % len(Z["verts"]))


def check_m2(d):
    """the sixteen against all 65536 memory-two co-players: with the memory-two layer of this folder (stability polygons,
    efficiency, rivalry) decide efficient, stable and competitive in the memory-two space at the interior game of each
    face, exactly; every memory-one strategy is the memory-two strategy that ignores the round before
    (id 15 * sum_k b_k 16^k), and its three properties must be the same against the 65536 as against the 16"""
    sys.path.insert(0, HERE)
    import arrangement
    from common import tables
    S = arrangement.m2_strategies()
    FA = tables.read_table(os.path.join(HERE, "m2_nash_facets.csv"))
    ids = [15 * sum(((s >> k) & 1) << (4 * k) for k in range(4)) for s in range(16)]
    assert ids[15] == 65535 and ids[0] == 0 and ids[5] == 3855 and ids[9] == 61455
    fac = {g: [] for g in ids}
    for g, a, b, c in zip(FA["genotype"], FA["a"], FA["b"], FA["c"]):
        if int(g) in fac:
            fac[int(g)].append((int(a), int(b), int(c)))
    for f, poly in enumerate(d["cells"]):
        u, v = interior(poly, 1)                                    # the exact rational interior game
        c = []
        for g in ids:
            eff = S["eff_cc"][g] if u + v < 1 else S["eff_alt"][g]
            riv = S["riv_plus"][g] if u - v < 1 else S["riv_minus"][g]
            ne = S["nash_dim"][g] == 2 and all(a + b * u + cc * v <= 0 for a, b, cc in fac[g])
            c.append(4 * int(eff) + 2 * int(ne) + int(riv))
        assert (np.array(c) == d["codes"][f]).all(), (f, u, v, c, d["codes"][f])
    print("against all 65536 memory-two co-players the 16 have the same three properties on all %d faces" % len(d["cells"]))


if __name__ == "__main__":
    d = build()
    census(d)
    compare(d)
    if "m2" in sys.argv[1:]:
        check_m2(d)
