#!/usr/bin/env python3
"""
SI Table 8: the sixteen binary memory-one strategies -- where each is efficient, where it is a Nash equilibrium,
for which sign of T - S it is competitive (a rival), and its class -- computed from first principles, exactly, in
the limit of rare errors, and compared with the table as printed in the paper.

    python3 sitable8.py            prints the table and the checks, compares with the paper, writes the two CSVs
    python3 sitable8.py --m2       ... and repeats the stability and rivalry tests against all 65536 memory-two co-players
    python3 sitable8.py --tex F    ... compares with SI Table 8 as typeset in the LaTeX file F instead of the copy below

CONVENTION.  A memory-one strategy answers the last round's outcome, seen from its own side (own action first), CC,
CD, DC, DD; it is written by its four answers, so ALLC is CCCC, ALLD DDDD, tit-for-tat CDCD, win-stay lose-shift
CDDC and Grim CDDD.  Internally bit k of s (k = 0..3 for CC, CD, DC, DD) is 1 for C.  The game is
(R, S, T, P) = (1, u, 1 + v, 0); the switch line is u + v = 1 and T = S is the line u - v = 1.

METHOD (the pair computation is m1atoms.py of the paper's figure scripts, unchanged).  For every ordered pair of the
sixteen, the stationary distribution of the four-state chain with independent implementation errors, rate eps, is
an exact rational function of eps: by the Markov chain tree theorem the weight of outcome o is proportional to the
(o, o) cofactor of I - P(eps), a polynomial in eps with integer coefficients, and the limit eps -> 0 is the ratio of
the lowest-order coefficients.  Everything is done in Python's Fraction; there is no threshold anywhere.  The limit
payoffs are then linear in (u, v) with rational coefficients, and

    efficient    pi(i, i) = Emax = max(R, (T + S)/2): self-play all CC below the switch line, w_CC = w_DD = 0 above
    stable       pi(j, i) <= pi(i, i) for all 16 j: an intersection of 15 closed half-planes, computed as an exact
                 polygon (which may be a segment or a single point)
    rival        pi(i, j) >= pi(j, i) for all 16 j, i.e. sign(T - S) (w_DC - w_CD) >= 0 against every j

For a memory-one strategy the sixteen memory-one co-players suffice: the co-player of a memory-one strategy controls a
Markov decision process on the four outcomes of the last round, whose best replies and best exploiters can be taken
deterministic and stationary, i.e. binary memory-one (the proposition of SI section 2, read on four states).
--m2 checks this directly against the 65536 binary memory-two co-players (a numpy version of the leading-order
state-reduction of the census, in double precision with the census's tolerance 1e-9).

Output: the table (this folder's sitable8.csv), the exact pair limits (m1_pairs.csv), the statements of SI section 10
(Memory one, for contrast) that rest on the table, and a comparison with every cell of the printed table.  The exit
status is 1 if any cell differs from the printed table or any statement check fails, and 0 otherwise.
Standard library only, except --m2, which needs numpy.
"""
import argparse
import csv
import os
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
NS = 4
NICK = {15: "ALLC", 0: "ALLD", 5: "TFT", 9: "WSLS", 1: "Grim"}
B = F(10 ** 6)             # regions are computed inside the box |u|, |v| <= B: every true vertex is far inside, and
                           # membership (inside) is exact for any game in the box


def genome(s):
    return "".join("C" if (s >> k) & 1 else "D" for k in range(NS))


def sid(g):
    return sum(1 << k for k, ch in enumerate(g) if ch == "C")


def swapo(o):
    """the same round seen from the co-player's side: CD <-> DC"""
    return ((o & 1) << 1) | (o >> 1)


# ------------------------------------------------------------- polynomials in eps, exact (m1atoms.py)
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


def cofactors(sig, tau):
    """the four (o, o) cofactors of I - P(eps): the weighted in-tree counts, polynomials in eps"""
    P = transition(sig, tau)
    L = [[padd([F(1) if o == p else F(0)], pneg(P[o][p])) for p in range(NS)] for o in range(NS)]
    cof = []
    for o in range(NS):
        M = [[L[r][c] for c in range(NS) if c != o] for r in range(NS) if r != o]
        cof.append(det3(M))
    return cof


def limit_weights(sig, tau):
    """the eps -> 0 limit of the stationary distribution (w_CC, w_CD, w_DC, w_DD) from sig's side"""
    cof = cofactors(sig, tau)
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


def payoff(w):
    """the limit payoff seen from the side of w, as a linear form (c0, cu, cv): c0 + cu u + cv v"""
    return (w[0] + w[2], w[1], w[2])                                  # R w_CC + S w_CD + T w_DC + P w_DD


def pay_at(w, u, v):
    c0, cu, cv = payoff(w)
    return c0 + cu * u + cv * v


# ------------------------------------------------------------- exact convex regions of the (u, v) plane
def hull(pts):
    """the convex hull of a set of exact points, counter-clockwise from the lexicographically smallest; a segment is
    returned as its two ends, a point as itself"""
    P = sorted(set(pts))
    if len(P) <= 2:
        return P

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    h = lo[:-1] + up[:-1]
    return h if len(h) >= 2 else P[:1] + P[-1:]


def clip(poly, a0, au, av):
    """the part of the convex polygon (exact vertices in cyclic order; possibly a segment or a point) on which
    a0 + au u + av v <= 0"""
    f = [a0 + au * p[0] + av * p[1] for p in poly]
    if len(poly) == 1:
        return list(poly) if f[0] <= 0 else []
    out = []
    n = len(poly)
    for i in range(n):
        p, q, fp, fq = poly[i], poly[(i + 1) % n], f[i], f[(i + 1) % n]
        if fp <= 0:
            out.append(p)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return hull(out)


BOX = hull([(-B, -B), (B, -B), (B, B), (-B, B)])


def region(constraints):
    """the closed convex set {a0 + au u + av v <= 0 for all constraints} within the box, as its hull"""
    poly = BOX
    for a0, au, av in constraints:
        if au == 0 and av == 0:
            if a0 > 0:
                return []
            continue
        poly = clip(poly, a0, au, av)
        if not poly:
            return []
    return poly


def dim(poly):
    return len(poly) - 1 if len(poly) <= 2 else 2


def onbox(p):
    return abs(p[0]) == B or abs(p[1]) == B


def boxedge(p, q):
    """is the segment p-q part of the boundary of the box"""
    return (p[0] == q[0] and abs(p[0]) == B) or (p[1] == q[1] and abs(p[1]) == B)


def fmt(x):
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def intline(p, q):
    """integer (a, b, c), gcd 1, with a u + b v = c through p and q"""
    a, b = q[1] - p[1], p[0] - q[0]
    c = a * p[0] + b * p[1]
    den = 1
    for x in (a, b, c):
        den = den * F(x).denominator // _gcd(den, F(x).denominator)
    a, b, c = int(a * den), int(b * den), int(c * den)
    g = _gcd(_gcd(abs(a), abs(b)), abs(c)) or 1
    return a // g, b // g, c // g


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lin(a, b):
    """the text of a u + b v"""
    s = ""
    for coef, var in ((a, "u"), (b, "v")):
        if coef == 0:
            continue
        sgn = "-" if coef < 0 else ("+" if s else "")
        mag = "" if abs(coef) == 1 else str(abs(coef))
        s += sgn + mag + var
    return s


def describe(poly):
    """the region in the paper's notation, ASCII: '--', 'u=a & v=b' (a point), 'u+v=-1 & u<=-1', 'u<=1 & v<=1', ..."""
    d = dim(poly)
    assert all(onbox(p) or (abs(p[0]) < B / 10 and abs(p[1]) < B / 10) for p in poly), "enlarge the box"
    if d < 0:
        return "--"
    if d == 0:
        return "u=%s & v=%s" % (fmt(poly[0][0]), fmt(poly[0][1]))
    if d == 1:
        p, q = poly
        a, b, c = intline(p, q)
        if a < 0 or (a == 0 and b < 0):
            a, b, c = -a, -b, -c
        if b == 0:                                              # a vertical line u = c/a, bounded in v
            head, x, var = "u=%s" % fmt(F(c, a)), 1, "v"
        elif abs(a) == abs(b) == 1 or abs(b) != 1 and abs(a) != 1:
            head, x, var = "%s=%s" % (lin(a, b), fmt(c)), 0, "u"
        elif abs(b) == 1:                                       # v = (c - a u)/b
            head = "v=" + _affine(F(-a, b), F(c, b), "u")
            x, var = 0, "u"
        else:                                                   # u = (c - b v)/a
            head = "u=" + _affine(F(-b, a), F(c, a), "v")
            x, var = 1, "v"
        bounds = []
        ends = sorted([p, q], key=lambda r: r[x])
        if not onbox(ends[0]):
            bounds.append("%s>=%s" % (var, fmt(ends[0][x])))
        if not onbox(ends[1]):
            bounds.append("%s<=%s" % (var, fmt(ends[1][x])))
        return " & ".join([head] + bounds)
    facets = []
    n = len(poly)
    cx = sum(p[0] for p in poly) / n
    cy = sum(p[1] for p in poly) / n
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        if boxedge(p, q):
            continue
        a, b, c = intline(p, q)
        if a * cx + b * cy > c:                                 # orient: the region is a u + b v <= c
            a, b, c = -a, -b, -c
        if b == 0:
            facets.append(("u<=%s" % fmt(F(c, a))) if a > 0 else ("u>=%s" % fmt(F(c, a))))
        elif a == 0:
            facets.append(("v<=%s" % fmt(F(c, b))) if b > 0 else ("v>=%s" % fmt(F(c, b))))
        else:
            facets.append("%s<=%s" % (lin(a, b), fmt(c)))
    order = {"u": 0, "v": 1}
    facets.sort(key=lambda s: (order.get(s[0], 2) if s[1] in "<>=" else 2, s))
    return " & ".join(facets)


def _affine(k, c, var):
    """the text of k var + c, e.g. '3u-1'"""
    s = ""
    if k != 0:
        s = ("-" if k < 0 else "") + ("" if abs(k) == 1 else fmt(abs(k))) + var
    if c != 0 or not s:
        s = (s + ("+" if c > 0 else "-") + fmt(abs(c))) if s else fmt(c)
    return s


# ------------------------------------------------------------- the three properties and the class of each strategy
SELF = {i: W[(i, i)] for i in range(16)}
EFF_LO = [i for i in range(16) if SELF[i] == (1, 0, 0, 0)]                   # all-CC self play
EFF_HI = [i for i in range(16) if SELF[i][0] == 0 and SELF[i][3] == 0]        # perfect alternation
EFF_ON = [i for i in range(16) if SELF[i][3] == 0]                            # on the switch line: no DD
RIVP = [i for i in range(16) if all(W[(i, j)][2] >= W[(i, j)][1] for j in range(16))]    # rival where T > S
RIVM = [i for i in range(16) if all(W[(i, j)][2] <= W[(i, j)][1] for j in range(16))]    # rival where T < S
FAIR = [i for i in range(16) if all(W[(i, j)][2] == W[(i, j)][1] for j in range(16))]


def nash_constraints(i, cop=None):
    """pi(j, i) - pi(i, i) <= 0 for every co-player j, as (a0, au, av)"""
    s0, su, sv = payoff(SELF[i])
    out = []
    for j in (range(16) if cop is None else cop):
        if j == i:
            continue
        c0, cu, cv = payoff(W[(j, i)])
        out.append((c0 - s0, cu - su, cv - sv))
    return out


NASH = {i: region(nash_constraints(i)) for i in range(16)}
SWITCH = (F(-1), F(1), F(1))              # u + v - 1 <= 0: the closed side of the switch line with u + v < 1
ABOVE = (F(1), F(-1), F(-1))              # 1 - u - v <= 0
TLS = (F(1), F(-1), F(1))                 # 1 - u + v <= 0: u - v >= 1, the side T < S
TGS = (F(-1), F(1), F(-1))                # u - v - 1 <= 0: the side T > S


def efficient_text(i):
    return "u+v<1" if i in EFF_LO else ("u+v>1" if i in EFF_HI else "--")


def rival_text(i):
    return {(1, 1): "both", (1, 0): "T>S", (0, 1): "T<S", (0, 0): "--"}[(i in RIVP, i in RIVM)]


def wedge_of_fr(i):
    """the quarter-plane on which i is a friendly rival (efficient and a rival), or None"""
    if i in EFF_LO and i in RIVP:
        return "W"
    if i in EFF_LO and i in RIVM:
        return "S"
    if i in EFF_HI and i in RIVM:
        return "E"
    if i in EFF_HI and i in RIVP:
        return "N"
    return None


def partner_region(i):
    """the closure of the games off the switch line at which i is efficient and stable"""
    if i in EFF_LO:
        return region(nash_constraints(i) + [SWITCH])
    if i in EFF_HI:
        return region(nash_constraints(i) + [ABOVE])
    return []


def klass(i):
    """(partner region, friendly-rival wedge, rival, fair) and the text of the class column"""
    pr = partner_region(i)
    wd = wedge_of_fr(i)
    riv = i in RIVP or i in RIVM
    parts = []
    if pr:
        side = "u+v<1" if i in EFF_LO else "u+v>1"
        parts.append("partner on %s & %s" % (describe(NASH[i]), side))
    if wd:
        parts.append("friendly rival on " + wd)
    if not parts and riv:
        parts.append("rival" + (" (fair)" if i in FAIR else ""))
    return dict(partner=pr, wedge=wd, rival=riv and not pr and not wd, fair=i in FAIR), "; ".join(parts) or "none"


ROWS = ["CCCC", "CCCD", "CDDC", "CDCD", "CDDD", "DDDD", "DDCD", "CDCC",
        "DDDC", "DCCC", "DCCD", "DCDD", "DDCC", "DCDC", "CCDD", "CCDC"]

# ------------------------------------------------------------- SI Table 8 as printed (ms.tex, 2026-09-24)
PAPER = r"""
$CCCC$ & \ALLC & $u+v<1$ & $v\le0$ & $T<S$ & partner on $v\le0$, $u+v<1$; friendly rival on $S$\\
$CCCD$ & & $u+v<1$ & $v\le0$ & $T<S$ & as \ALLC\\
$CDDC$ & \WSLS & $u+v<1$ & $u\le1$, $v\le1$ & -- & partner on $u\le1$, $v\le1$, $u+v<1$\\
$CDCD$ & tit-for-tat & -- & -- & both & rival, fair\\
$CDDD$ & \Grim & -- & $u\le-\tfrac12$ & $T>S$ & rival\\
$DDDD$ & \ALLD & -- & $u\le0$ & $T>S$ & rival\\
$DDCD$ & & -- & $u+v=-1$, $u\le-1$ & $T>S$ & rival\\
$CDCC$ & & -- & $u+v=1$, $u\ge0$ & $T<S$ & rival\\
$DDDC$ & & -- & $u\le\tfrac12$, $v\le0$ & -- & none\\
$DCCC$ & & -- & $u\le0$, $v\le-\tfrac12$ & -- & none\\
$DCCD$ & & -- & $u\le-1$, $v\le-1$ & -- & none\\
$DCDD$ & & -- & $v=3u-1$, $u\ge0$ & -- & none\\
$DDCC$ & & -- & $(0,0)$ & -- & none\\
$DCDC$ & & -- & $(\tfrac12,-\tfrac12)$ & -- & none\\
$CCDD$ & & -- & $(0,0)$ & -- & none\\
$CCDC$ & & -- & $u=3v+1$, $v\ge0$ & -- & none\\
"""


def paper_rows(text):
    """the rows of SI Table 8 from LaTeX source: a dict genome -> [name, efficient, nash, rival, class]"""
    if "SI Table 8" in text:
        text = text[text.index("SI Table 8"):]
        text = text[text.index("\\midrule") + len("\\midrule"):text.index("\\bottomrule")]
    rows = {}
    for line in text.strip().splitlines():
        line = line.strip().rstrip("\\").strip()
        if not line:
            continue
        cells = [c.strip() for c in line.split("&")]
        assert len(cells) == 6, line
        rows[cells[0].strip("$")] = cells[1:]
    return rows


def tex_to_ascii(s):
    return (s.replace("$", "").replace("\\tfrac12", "1/2").replace("\\le", "<=").replace("\\ge", ">=")
            .replace("{", "").replace("}", "").strip())


def parse_lin(s):
    """'3u-1' -> (c0, cu, cv)"""
    s = s.replace(" ", "")
    c = [F(0), F(0), F(0)]
    pos = 0
    while pos < len(s):
        m = re.match(r"([+-]?)(\d+(?:/\d+)?)?([uv]?)", s[pos:])
        assert m and m.end() > 0 and (m.group(2) or m.group(3)), (s, pos)
        k = F(m.group(2)) if m.group(2) else F(1)
        k = -k if m.group(1) == "-" else k
        c[{"": 0, "u": 1, "v": 2}[m.group(3)]] += k
        pos += m.end()
    return tuple(c)


def parse_constraints(s):
    """'u+v=-1, u<=-1' -> [(a0, au, av)] meaning a0 + au u + av v <= 0 (an equality gives two; '<' is read as '<=')"""
    out = []
    for piece in re.split(r"[,&]", tex_to_ascii(s)):
        piece = piece.strip()
        if not piece:
            continue
        m = re.match(r"^(.*?)(<=|>=|<|>|=)(.*)$", piece)
        assert m, piece
        l, op, r = parse_lin(m.group(1)), m.group(2), parse_lin(m.group(3))
        d = tuple(a - b for a, b in zip(l, r))                       # l - r
        if op in ("<=", "<"):
            out.append(d)
        elif op in (">=", ">"):
            out.append(tuple(-x for x in d))
        else:
            out += [d, tuple(-x for x in d)]
    return out


def paper_region(s):
    """a cell of the column stable of the table as an exact region: '--' (none), a single game '(a,b)', or constraints 'u<=1, v<=1'"""
    s = tex_to_ascii(s)
    if s in ("--", "-", ""):
        return []
    m = re.match(r"^\((.*),(.*)\)$", s.replace(" ", ""))
    if m:                                                           # a single game (u, v)
        u, v = (parse_lin(x) for x in m.groups())
        assert u[1:] == v[1:] == (0, 0), s
        return region([(-u[0], F(1), F(0)), (u[0], F(-1), F(0)), (-v[0], F(0), F(1)), (v[0], F(0), F(-1))])
    return region(parse_constraints(s))


def paper_class(s, rows):
    """(partner region, wedge, rival, fair) of a class cell"""
    s = s.strip()
    if s.startswith("as "):
        name = s[3:].strip().lstrip("\\")
        g = next(k for k, v in rows.items() if v[0].strip().lstrip("\\") == name)
        return paper_class(rows[g][4], rows)
    pr, wd, riv, fair = [], None, False, False
    for part in s.split(";"):
        part = part.strip()
        if part.startswith("partner on"):
            pr = region(parse_constraints(part[len("partner on"):]))
        elif part.startswith("friendly rival on"):
            wd = tex_to_ascii(part[len("friendly rival on"):])
        elif part.startswith("rival"):
            riv, fair = True, "fair" in part
        else:
            assert part == "none", part
    return dict(partner=pr, wedge=wd, rival=riv, fair=fair)


NAMEMAP = {"\\ALLC": "ALLC", "\\ALLD": "ALLD", "\\WSLS": "WSLS", "\\Grim": "Grim", "tit-for-tat": "TFT", "": ""}


# ------------------------------------------------------------- the statements of SI section 10 that rest on the table
def codes_at(u, v):
    """the atom code (4 efficient + 2 stable + competitive) of each of the 16 at the rational game (u, v), decided
    directly on the 16 x 16 limit payoff matrix (m1atoms.py)"""
    u, v = F(u), F(v)
    A = [[pay_at(W[(i, j)], u, v) for j in range(16)] for i in range(16)]
    em = max(F(1), (1 + u + v) / 2)
    assert max((A[i][j] + A[j][i]) / 2 for i in range(16) for j in range(16)) == em, (u, v)
    out = []
    for i in range(16):
        eff = A[i][i] == em
        nash = all(A[i][i] >= A[j][i] for j in range(16))
        comp = all(A[i][j] >= A[j][i] for j in range(16))
        out.append(4 * eff + 2 * nash + comp)
    return out


def inside(poly, p):
    """is the exact point p in the closed convex set poly"""
    if not poly:
        return False
    if len(poly) == 1:
        return poly[0] == p
    if len(poly) == 2:
        a, b = poly
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        return cr == 0 and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < 0:
            return False
    return True


def arrangement(lines):
    """the faces of the arrangement of lines (a, b, c): a u + b v = c, inside the box, exactly"""
    faces = [BOX]
    for a, b, c in lines:
        a, b, c = F(a), F(b), F(c)
        nxt = []
        for poly in faces:
            s = [a * p[0] + b * p[1] - c for p in poly]
            if min(s) >= 0 or max(s) <= 0:
                nxt.append(poly)
                continue
            for sg in (1, -1):
                q = clip(poly, sg * -c, sg * a, sg * b)
                if dim(q) == 2:
                    nxt.append(q)
        faces = nxt
    return faces


def interior(poly, seed):
    """a rational point strictly inside a convex face, with generic weights (as m1atoms.py)"""
    n = len(poly)
    w = [F(7 + ((seed * 13 + k * 5) % 11), 7) for k in range(n)]
    tot = sum(w)
    return (sum(p[0] * wk for p, wk in zip(poly, w)) / tot, sum(p[1] * wk for p, wk in zip(poly, w)) / tot)


def statements():
    """check the statements of SI section 10 (and the memory-one ones of section 5) against the computation"""
    res = []

    def claim(text, ok):
        res.append((ok, text))

    G = genome
    # no alternator: self-play off-diagonal mass is exactly 1/4 or exactly eps(1 - eps), at every eps
    okq = True
    for s in range(16):
        cof = cofactors(s, s)
        tot = [F(0)]
        for c in cof:
            tot = padd(tot, c)
        differ = ((s >> 1) & 1) != ((s >> 2) & 1)
        target = pmul(tot, [F(1, 4)]) if differ else pmul(tot, [F(0), F(1), F(-1)])
        d = padd(cof[1], pneg(target))
        okq &= all(x == 0 for x in d)
    claim("self play: w_CD = w_DC is exactly 1/4 at every eps if the answers at CD and DC differ, exactly eps(1-eps) if they agree", okq)
    claim("no binary memory-one strategy is efficient above the switch line", EFF_HI == [])
    claim("below the switch line exactly CCCC, CDDC and CCCD are efficient",
          sorted(map(G, EFF_LO)) == sorted(["CCCC", "CDDC", "CCCD"]))
    claim("on the switch line the efficient ones are CCCC, CCCD, CDDC, CCDC, CDCC; CCDC and CDCC with self-play weights (1/2,1/4,1/4,0)",
          sorted(map(G, EFF_ON)) == sorted(["CCCC", "CCCD", "CDDC", "CCDC", "CDCC"])
          and SELF[sid("CCDC")] == SELF[sid("CDCC")] == (F(1, 2), F(1, 4), F(1, 4), 0))
    claim("on the switch line the friendly rivals are none where T>S and CCCC, CCCD, CDCC where T<S",
          [i for i in EFF_ON if i in RIVP] == [] and sorted(G(i) for i in EFF_ON if i in RIVM) == sorted(["CCCC", "CCCD", "CDCC"]))
    claim("on the line T=S every efficient strategy is a friendly rival: three below the switch line, none above",
          len(EFF_LO) == 3 and len(EFF_HI) == 0)
    claim("rival for T>S iff it defects at CD and at DD: DDDD, CDDD, DDCD, CDCD",
          sorted(map(G, RIVP)) == sorted(["DDDD", "CDDD", "DDCD", "CDCD"])
          and RIVP == [i for i in range(16) if not (i >> 1) & 1 and not (i >> 3) & 1])
    claim("rival for T<S iff it cooperates at CC and at DC: CCCC, CCCD, CDCC, CDCD",
          sorted(map(G, RIVM)) == sorted(["CCCC", "CCCD", "CDCC", "CDCD"])
          and RIVM == [i for i in range(16) if (i >> 0) & 1 and (i >> 2) & 1])
    claim("tit-for-tat is the only fair strategy (w_CD = w_DC against all 16)", list(map(G, FAIR)) == ["CDCD"])
    # defensibility: no negative cycle on the 4-node graph, weight +1 for a DC round, -1 for CD (T > S), reversed for T < S
    def defensible(s, sign):
        INF = 10 ** 9
        d = [[INF] * 4 for _ in range(4)]
        for o in range(4):
            a = (s >> o) & 1                                           # own intended action at o, 1 = C
            for b in (0, 1):                                           # the co-player's action
                nxt = 2 * (1 - a) + (1 - b)
                wgt = sign * {0: 0, 1: -1, 2: 1, 3: 0}[nxt]
                d[o][nxt] = min(d[o][nxt], wgt)
        for k in range(4):
            for i in range(4):
                for j in range(4):
                    if d[i][k] + d[k][j] < d[i][j]:
                        d[i][j] = d[i][k] + d[k][j]
        return all(d[i][i] >= 0 for i in range(4))
    DEFP = [s for s in range(16) if defensible(s, 1)]
    DEFM = [s for s in range(16) if defensible(s, -1)]
    claim("at memory one rivalry coincides with Murase and Baek's defensibility (both signs of T-S)", DEFP == RIVP and DEFM == RIVM)
    fr = {w: sorted(G(i) for i in range(16) if wedge_of_fr(i) == w) for w in "WSEN"}
    claim("friendly rivals on W, S, E, N: 0, 2, 0, 0 (CCCC and CCCD, in S)",
          [len(fr[w]) for w in "WSEN"] == [0, 2, 0, 0] and fr["S"] == ["CCCC", "CCCD"])
    wsls = sid("CDDC")
    claim("win-stay, lose-shift is a partner wherever u<=1, v<=1 and u+v<1, and a rival in neither direction",
          partner_region(wsls) == region(parse_constraints("u<=1, v<=1, u+v<=1")) and wsls not in RIVP + RIVM)
    two = sorted(G(i) for i in range(16) if dim(NASH[i]) == 2)
    claim("eight of the sixteen are stable on a two-dimensional set: CCCC CCCD CDDC CDDD DDDD DDDC DCCC DCCD",
          two == sorted("CCCC CCCD CDDC CDDD DDDD DDDC DCCC DCCD".split()))
    common8 = region([c for i in range(16) if dim(NASH[i]) == 2 for c in nash_constraints(i)])
    claim("0 to 8 of these eight at a game: all eight at (u,v)=(-2,-2), none at (2,2)",
          dim(common8) == 2 and inside(common8, (F(-2), F(-2)))
          and not any(inside(NASH[i], (F(2), F(2))) for i in range(16) if dim(NASH[i]) == 2))
    # the largest number of stable strategies at any game, the half-lines and single games included: the count is
    # constant on the cells of the arrangement of all boundary lines, and a closed set that contains a cell contains
    # its vertices, so the maximum is attained at a vertex of that arrangement
    bl = set()
    for i in range(16):
        P = NASH[i]
        for k in range(len(P) if len(P) > 2 else (1 if len(P) == 2 else 0)):
            p, q = P[k], P[(k + 1) % len(P)]
            if not boxedge(p, q):
                bl.add(intline(p, q))
    bl = sorted(bl)
    cand = {P[0] for i in range(16) for P in [NASH[i]] if dim(P) == 0}
    for x in range(len(bl)):
        for y in range(x + 1, len(bl)):
            (a1, b1, c1), (a2, b2, c2) = bl[x], bl[y]
            det = a1 * b2 - a2 * b1
            if det:
                cand.add((F(c1 * b2 - c2 * b1, det), F(a1 * c2 - a2 * c1, det)))
    most = max(sum(inside(NASH[i], p) for i in range(16)) for p in cand)
    claim("including the half-lines and the single games, at most 8 of the sixteen are stable at any game", most == 8)
    hl = {G(i): describe(NASH[i]) for i in range(16) if dim(NASH[i]) == 1}
    claim("four more are stable only on half-lines: DCDD v=3u-1, u>=0; CCDC u=3v+1, v>=0; DDCD u+v=-1, u<=-1; CDCC u+v=1, u>=0",
          hl == {"DCDD": "v=3u-1 & u>=0", "CCDC": "u=3v+1 & v>=0", "DDCD": "u+v=-1 & u<=-1", "CDCC": "u+v=1 & u>=0"})
    pts = {G(i): describe(NASH[i]) for i in range(16) if dim(NASH[i]) == 0}
    never = sorted(G(i) for i in range(16) if dim(NASH[i]) < 0)
    claim("the remaining four: tit-for-tat is stable at no game; DDCC and CCDD only at the single game "
          "(u,v)=(0,0), DCDC only at (u,v)=(1/2,-1/2), each with ties",
          never == ["CDCD"] and pts == {"DDCC": "u=0 & v=0", "CCDD": "u=0 & v=0", "DCDC": "u=1/2 & v=-1/2"})
    sd = region([(F(0), F(-1), F(0)), (F(0), F(0), F(-1))])                  # the closed Snowdrift quadrant u, v >= 0
    in_sd = [G(i) for i in range(16) if dim(NASH[i]) == 2 and dim(region(nash_constraints(i) + [(F(0), F(-1), F(0)), (F(0), F(0), F(-1))])) == 2]
    claim("off the half-lines the only equilibrium in the Snowdrift quadrant is WSLS, on the unit square",
          in_sd == ["CDDC"] and region(nash_constraints(wsls) + [(F(0), F(-1), F(0)), (F(0), F(0), F(-1))])
          == region(parse_constraints("u>=0, v>=0, u<=1, v<=1")) and bool(sd))
    far = lambda i: any(p[0] > 1 and p[1] > 1 for p in NASH[i]) if dim(NASH[i]) == 1 else False
    claim("of the half-lines those of DCDD and CCDC reach the Snowdrift games outside the unit square",
          sorted(G(i) for i in range(16) if far(i)) == ["CCDC", "DCDD"])
    offsw = sorted(G(i) for i in range(16) if partner_region(i))
    claim("off the switch line the partners are CCCC, CCCD and CDDC; none above the switch line, none with v>1",
          offsw == sorted(["CCCC", "CCCD", "CDDC"]) and all(p[1] <= 1 for i in range(16) for p in partner_region(i)))
    # WSLS on the donation game (b - c, -c, b, 0) / (b - c): u = -c/(b-c), v = c/(b-c)
    ok = True
    for b, c in ((F(3), 1), (F(5, 2), 1), (F(2), 1), (F(19, 10), 1), (F(3, 2), 1)):
        u, v = F(-c) / (b - c), F(c) / (b - c)
        ok &= inside(NASH[wsls], (u, v)) == (b >= 2 * c)
    u, v = F(-1), F(1)                                                    # b = 2c
    tie = pay_at(W[(sid("DDDD"), wsls)], u, v) == pay_at(SELF[wsls], u, v)
    claim("WSLS is a partner on the donation game exactly when b>=2c, with a tie (ALLD earns R against it) at b=2c", ok and tie)
    # the eleven lines, the 45 faces and the twelve cases
    facetlines = set()
    for i in range(16):
        if dim(NASH[i]) == 2:
            P = NASH[i]
            for k in range(len(P)):
                p, q = P[k], P[(k + 1) % len(P)]
                if not boxedge(p, q):
                    a, b, c = intline(p, q)
                    if a < 0 or (a == 0 and b < 0):
                        a, b, c = -a, -b, -c
                    facetlines.add((a, b, c))
    LINES = sorted(facetlines | {(1, 1, 1), (1, -1, 1)})
    want = sorted({(1, 0, -1), (2, 0, -1), (1, 0, 0), (2, 0, 1), (1, 0, 1), (0, 1, -1), (0, 2, -1), (0, 1, 0), (0, 1, 1), (1, 1, 1), (1, -1, 1)})
    claim("off the half-lines the classification changes only across eleven lines: u=-1,-1/2,0,1/2,1; v=-1,-1/2,0,1; u+v=1; u-v=1",
          LINES == want)
    faces = arrangement(LINES)
    cases, maxat, all0001, s111, no101 = set(), 0, True, True, True
    for poly in faces:
        c1, c2 = codes_at(*interior(poly, 1)), codes_at(*interior(poly, 2))
        assert c1 == c2
        u, v = interior(poly, 1)
        # the region description gives the same codes as the direct test
        for i in range(16):
            e = (i in EFF_LO and u + v < 1) or (i in EFF_HI and u + v > 1)
            r = (i in RIVP and u - v < 1) or (i in RIVM and u - v > 1)
            assert c1[i] == 4 * e + 2 * inside(NASH[i], (u, v)) + r, (G(i), u, v)
        present = frozenset(format(k, "03b") for k in set(c1))
        cases.add(present)
        maxat = max(maxat, len(present))
        all0001 &= "000" in present and "001" in present
        no101 &= 5 not in c1
        s111 &= ("111" in present) == (u + v < 1 and u - v > 1)
    claim("they cut the plane into 45 faces with twelve sets of non-empty atoms (the cases of Figure 1b)",
          len(faces) == 45 and len(cases) == 12)
    claim("a game has at most five atoms, 000 and 001 at every game and 111 exactly on S", maxat == 5 and all0001 and s111)
    claim("on every face the atom 101 is empty (the theorem)", no101)
    return res, faces


# ------------------------------------------------------------- the memory-two check (numpy)
def check_m2(tol=1e-9):
    """the stability regions and the rival signs of the sixteen, against all 65536 binary memory-two co-players"""
    import numpy as np
    ids = [15 * sum(((s >> k) & 1) << (4 * k) for k in range(4)) for s in range(16)]   # ignore the round before
    BIG = 10 ** 6
    sw = [0, 2, 1, 3]
    jt = np.array([4 * sw[j // 4] + sw[j % 4] for j in range(16)])    # the state seen from the co-player's side

    def weights(sig, taus):
        """eps -> 0 limit (w_CC, w_CD, w_DC, w_DD) from sig's side against each tau, by GTH in leading-order
        (coefficient, exponent) arithmetic"""
        n = len(taus)
        cs = np.array([(sig >> j) & 1 for j in range(16)])
        ct = (taus[:, None] >> jt[None, :]) & 1                         # (n, 16): tau's intended action, 1 = C
        A = np.zeros((n, 16, 16))
        E = np.full((n, 16, 16), BIG, dtype=np.int64)
        for j in range(16):
            for a in (0, 1):
                for b in (0, 1):
                    o = 2 * (1 - a) + (1 - b)
                    nxt = 4 * o + j // 4
                    e = (a != cs[j]) + (b != ct[:, j]).astype(np.int64)
                    A[:, j, nxt] = 1.0
                    E[:, j, nxt] = e
        for k in range(15, 0, -1):
            ek = E[:, k, :k]
            emin = ek.min(axis=1)
            s = np.where(ek == emin[:, None], A[:, k, :k], 0.0).sum(axis=1)
            nz = A[:, :k, k] > 0
            A[:, :k, k] = np.where(nz, A[:, :k, k] / s[:, None], 0.0)
            E[:, :k, k] = np.where(nz, E[:, :k, k] - emin[:, None], BIG)
            pa, pe = A[:, :k, k][:, :, None] * A[:, k, :k][:, None, :], E[:, :k, k][:, :, None] + E[:, k, :k][:, None, :]
            live = pa > 0
            pe = np.where(live, pe, BIG)
            qa, qe = A[:, :k, :k], E[:, :k, :k]
            m = np.minimum(qe, pe)
            A[:, :k, :k] = np.where(qe == m, qa, 0.0) + np.where(pe == m, pa, 0.0)
            E[:, :k, :k] = m
        xa = np.zeros((n, 16))
        xe = np.full((n, 16), BIG, dtype=np.int64)
        xa[:, 0], xe[:, 0] = 1.0, 0
        for j in range(1, 16):
            ta, te = xa[:, :j] * A[:, :j, j], xe[:, :j] + E[:, :j, j]
            te = np.where(ta > 0, te, BIG)
            m = te.min(axis=1)
            xa[:, j] = np.where(te == m[:, None], ta, 0.0).sum(axis=1)
            xe[:, j] = m
        m = xe.min(axis=1)
        lead = np.where(xe == m[:, None], xa, 0.0)
        lead /= lead.sum(axis=1, keepdims=True)
        return lead.reshape(n, 4, 4).sum(axis=2)                       # the outcome of the most recent round

    taus = np.arange(65536)
    bad = []
    for s in range(16):
        w = np.concatenate([weights(ids[s], taus[k:k + 8192]) for k in range(0, 65536, 8192)])
        # the numpy kernel reproduces the exact memory-one limits
        for t in range(16):
            assert np.allclose(w[ids[t]], [float(x) for x in W[(s, t)]], atol=1e-12), (genome(s), genome(t))
        d = w[:, 2] - w[:, 1]
        rp, rm = bool((d >= -tol).all()), bool((d <= tol).all())
        # stable: pi(tau, sig) - pi(sig, sig) <= 0, with pi(tau, sig) = w_CC + (1 + v) w_CD + u w_DC from sig's side
        s0, su, sv = payoff(SELF[s])
        co = np.stack([w[:, 0] + w[:, 1], w[:, 2], w[:, 1]], axis=1)
        uniq = np.unique(np.round(co, 9), axis=0)
        cons = []
        for c0, cu, cv in uniq:
            fr = [F(float(x)).limit_denominator(10 ** 6) for x in (c0, cu, cv)]
            assert all(abs(float(x) - y) < 1e-8 for x, y in zip(fr, (c0, cu, cv)))
            cons.append((fr[0] - s0, fr[1] - su, fr[2] - sv))
        # constraints are recovered as rationals; drop the exact duplicates of the self-play row
        reg = region(cons)
        same = reg == NASH[s] and rp == (s in RIVP) and rm == (s in RIVM)
        print("  %s %-5s vs 65536: stable %-22s rival %-4s  %s" % (genome(s), NICK.get(s, ""), describe(reg),
              {(1, 1): "both", (1, 0): "T>S", (0, 1): "T<S", (0, 0): "--"}[(rp, rm)], "same as vs 16" if same else "DIFFERS"))
        if not same:
            bad.append(genome(s))
    return bad


# ------------------------------------------------------------- output
def write_csv(path, comments, header, rows):
    with open(path, "w", newline="") as f:
        for c in comments:
            f.write("# " + c + "\n")
        wr = csv.writer(f, lineterminator="\n")
        wr.writerow(header)
        for r in rows:
            assert not any("," in str(x) for x in r), r
            wr.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--m2", action="store_true", help="also test against the 65536 memory-two co-players (numpy)")
    ap.add_argument("--tex", help="compare with SI Table 8 in this LaTeX file instead of the built-in copy")
    ap.add_argument("--nowrite", action="store_true", help="do not write the CSVs")
    args = ap.parse_args()

    rows = paper_rows(open(args.tex).read() if args.tex else PAPER)
    assert list(rows) == ROWS, "the paper's rows are not the sixteen in the expected order"

    print("SI Table 8, computed (exact, eps -> 0; regions closed, ties admitted; efficient and class off the two lines)\n")
    hdr = "%-5s %-5s %-8s %-24s %-5s %s" % ("", "name", "efficient", "stable", "rival", "class")
    print(hdr)
    out, ndiff = [], 0
    diffs = []
    for g in ROWS:
        i = sid(g)
        kc, ktext = klass(i)
        eff, nash, riv = efficient_text(i), describe(NASH[i]), rival_text(i)
        print("%-5s %-5s %-8s %-24s %-5s %s" % (g, NICK.get(i, ""), eff, nash, riv, ktext))
        out.append([g, i, NICK.get(i, ""), eff, nash, riv, ktext])
        # compare with the paper, cell by cell
        pname, peff, pnash, priv, pcls = rows[g]
        cmp = []
        cmp.append(("name", NAMEMAP.get(pname.strip(), pname.strip()) == NICK.get(i, "")))
        cmp.append(("efficient", tex_to_ascii(peff) == eff))
        cmp.append(("stable", paper_region(pnash) == NASH[i]))
        cmp.append(("rival for", tex_to_ascii(priv).replace("-", "") == riv.replace("-", "")))
        pc = paper_class(pcls, rows)
        cmp.append(("class", pc["partner"] == kc["partner"] and pc["wedge"] == kc["wedge"] and pc["rival"] == kc["rival"]
                    and pc["fair"] == kc["fair"]))
        for col, ok in cmp:
            if not ok:
                ndiff += 1
                diffs.append((g, col, {"name": pname, "efficient": peff, "stable": pnash, "rival for": priv, "class": pcls}[col],
                              {"name": NICK.get(i, ""), "efficient": eff, "stable": nash, "rival for": riv, "class": ktext}[col]))
    print("\nComparison with SI Table 8 as printed (%s): %d of %d cells agree"
          % ("--tex " + args.tex if args.tex else "the copy in this script", 5 * 16 - ndiff, 5 * 16))
    for g, col, p, c in diffs:
        print("  DIFFERS  %s, column %s: printed '%s', computed '%s'" % (g, col, p, c))

    print("\nStatements of SI section 10 (Memory one, for contrast) and of section 5 that rest on the table:")
    res, faces = statements()
    for ok, text in res:
        print("  %s  %s" % ("ok  " if ok else "FAIL", text))
    nfail = sum(1 for ok, _ in res if not ok)

    if not args.nowrite:
        write_csv(os.path.join(HERE, "sitable8.csv"),
                  ["SI Table 8: the sixteen binary memory-one strategies, computed by sitable8.py (exact, eps -> 0).",
                   "genome: the answers at CC, CD, DC, DD (own action first); id: sum of 2^k over the k with answer C.",
                   "efficient: where the strategy is efficient, off the two lines (u+v<1: self-play all CC).",
                   "nash: the closed set of games at which it is stable, a Nash equilibrium with ties admitted, '&' = and, '--' = none.",
                   "rival_for: the sign of T-S for which it is competitive against every co-player.",
                   "class: partner / friendly rival (with where) / rival / none; ';' separates the parts.",
                   "Games (R,S,T,P) = (1,u,1+v,0)."],
                  ["genome", "id", "name", "efficient", "nash", "rival_for", "class"], out)
        pr = []
        for s in range(16):
            for t in range(16):
                w = W[(s, t)]
                pr.append([genome(s), genome(t), s, t] + [fmt(x) for x in w])
        write_csv(os.path.join(HERE, "m1_pairs.csv"),
                  ["The exact eps -> 0 limit of the stationary distribution of every ordered pair of binary memory-one",
                   "strategies with independent implementation errors, computed by sitable8.py (Markov chain tree theorem,",
                   "exact rational arithmetic). sigma, tau: the genomes (answers at CC, CD, DC, DD); sigma_id, tau_id: their ids.",
                   "w_CC, w_CD, w_DC, w_DD: the limit frequencies of the four outcomes seen from sigma's side, as exact fractions.",
                   "sigma's payoff is R w_CC + S w_CD + T w_DC + P w_DD, tau's is R w_CC + T w_CD + S w_DC + P w_DD."],
                  ["sigma", "tau", "sigma_id", "tau_id", "w_CC", "w_CD", "w_DC", "w_DD"], pr)
        print("\nwrote sitable8.csv (16 rows) and m1_pairs.csv (256 rows)")

    if args.m2:
        print("\nThe sixteen against all 65536 binary memory-two co-players (numpy, leading-order GTH, tolerance 1e-9):")
        bad = check_m2()
        print("  %s" % ("the stability regions and rival signs are the same as against the 16 memory-one co-players, for all sixteen"
                        if not bad else "DIFFERENT for " + " ".join(bad)))
        nfail += len(bad)
    print("\n%d cell(s) differ from the printed table; %d statement check(s) failed" % (ndiff, nfail))
    return 1 if nfail or ndiff else 0


if __name__ == "__main__":
    sys.exit(main())
