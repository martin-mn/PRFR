#!/usr/bin/env python3
"""
SI Table 1: classical strategies of the repeated Prisoner's Dilemma and their properties -- every row checked at
donation games (R, S, T, P) = (b - c, -c, b, 0), exactly, in the limit of rare errors (and, for the one row that
says so, without errors from a cooperative start), and compared with the table as printed in the paper.

    python3 sitable1.py            prints every check and the comparison with the printed table
    python3 sitable1.py --tex F    ... compares with SI Table 1 as typeset in the LaTeX file F instead of the copy below

All ten strategies of the table are memory-one strategies, written by their probabilities of cooperating after CC,
CD, DC and DD (own action first); four of them (generous tit-for-tat and the three zero-determinant strategies) are
stochastic, and one representative of each is checked at each game, with the parameters printed.

METHOD.  With implementation errors at rate eps, a player who intends to cooperate with probability p cooperates with
probability p + (1 - 2p) eps.  For a pair of memory-one strategies the stationary distribution of the four-state chain
is, by the Markov chain tree theorem, proportional to the diagonal cofactors of I - P(eps), polynomials in eps with
rational coefficients, and its limit eps -> 0 is the ratio of their lowest-order coefficients (the pair computation of
SI Table 8, ../SITable8/sitable8.py, extended from binary to probabilistic answers).  Everything is exact (Fraction).

The co-players.  Against a memory-one strategy sigma, stochastic or not, the co-player controls a Markov decision
process on the four outcomes of the last round.  Its best reply and its best exploiter over all strategies, of any
memory, are attained at every eps > 0 by a deterministic stationary policy, i.e. one of the sixteen binary memory-one
strategies (the argument of the proposition of SI section 2, read on four states), and the limit exchanges with the
maximum over these finitely many rational functions.  So

    efficient     pi(sigma, sigma) = Emax = max(R, (T + S)/2)   (= R = b - c at a donation game)
    stable        pi(tau, sigma) <= pi(sigma, sigma)            for the 16 binary memory-one tau
    competitive   pi(sigma, tau) >= pi(tau, sigma)              for the 16 binary memory-one tau
    submissive    pi(sigma, tau) <= pi(tau, sigma)              for the 16 binary memory-one tau

are decided exactly and hold against co-players of any memory.  Without errors (the tit-for-tat row) the play is
deterministic; the co-player chooses its first move and then, from the outcome of the first round, faces a
deterministic decision process on the same four states, whose best long-run average is again attained by a
stationary policy, so the 16 binary memory-one co-players with either first move (32 in all) suffice.

Standard library only.
"""
import argparse
import re
import sys
from fractions import Fraction as F

NS = 4


def swapo(o):
    """the same round seen from the co-player's side: CD <-> DC"""
    return ((o & 1) << 1) | (o >> 1)


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


def transition(p, q):
    """P[o][o'] as polynomials in eps; p, q: the cooperation probabilities of the two players at CC, CD, DC, DD, each
    seen from its own side"""
    P = [[[F(0)] for _ in range(NS)] for _ in range(NS)]
    for o in range(NS):
        cs, ct = F(p[o]), F(q[swapo(o)])
        sc, sd = [cs, 1 - 2 * cs], [1 - cs, 2 * cs - 1]              # realised C / D of the first player
        tc, td = [ct, 1 - 2 * ct], [1 - ct, 2 * ct - 1]
        for a, pa in ((1, sc), (0, sd)):
            for b, pb in ((1, tc), (0, td)):
                nxt = 2 * (1 - a) + (1 - b)
                P[o][nxt] = padd(P[o][nxt], pmul(pa, pb))
    return P


def det3(M):
    (a, b, c), (d, e, f), (g, h, i) = M
    return padd(padd(pmul(a, padd(pmul(e, i), pneg(pmul(f, h)))),
                     pneg(pmul(b, padd(pmul(d, i), pneg(pmul(f, g)))))),
                pmul(c, padd(pmul(d, h), pneg(pmul(e, g)))))


def limit_weights(p, q):
    """the eps -> 0 limit of the stationary distribution (w_CC, w_CD, w_DC, w_DD), seen from p's side"""
    P = transition(p, q)
    L = [[padd([F(1) if o == r else F(0)], pneg(P[o][r])) for r in range(NS)] for o in range(NS)]
    cof = [det3([[L[r][c] for c in range(NS) if c != o] for r in range(NS) if r != o]) for o in range(NS)]
    order = [next((k for k, a in enumerate(c) if a != 0), None) for c in cof]
    kmin = min(k for k in order if k is not None)
    lead = [cof[o][kmin] if order[o] == kmin else F(0) for o in range(NS)]
    assert all(a >= 0 for a in lead) and sum(lead) > 0, (p, q, lead)
    return tuple(a / sum(lead) for a in lead)


def pay(w, g):
    R, S, T, P = g
    return R * w[0] + S * w[1] + T * w[2] + P * w[3]


BINARY = [tuple(F((s >> k) & 1) for k in range(NS)) for s in range(16)]


def genome(p):
    return "".join("C" if x == 1 else ("D" if x == 0 else "?") for x in p)


def properties(p, g):
    """efficient, stable, competitive, submissive of the memory-one strategy p at the game g, in the limit eps -> 0"""
    R, S, T, P = g
    emax = max(R, (T + S) / 2)
    E = pay(limit_weights(p, p), g)
    dev = max(pay(limit_weights(q, p), g) for q in BINARY if q != tuple(map(F, p)))   # the best other reply's payoff
    rel = []
    for q in BINARY:
        w = limit_weights(p, q)
        rel.append(pay(w, g) - pay((w[0], w[2], w[1], w[3]), g))       # pi(p, q) - pi(q, p)
    return dict(eff=E == emax, nash=dev <= E, comp=min(rel) >= 0, subm=max(rel) <= 0, E=E, emax=emax, dev=dev,
                tie=dev == E)


def play0(p, q, first_p, first_q):
    """without errors: the long-run average payoffs (own, co-player's) of the deterministic memory-one p against q from
    the first moves given, exactly (the play is eventually periodic on the four outcomes)"""
    o = 2 * (1 - first_p) + (1 - first_q)
    seen, seq = {}, []
    while o not in seen:
        seen[o] = len(seq)
        seq.append(o)
        a, b = int(p[o]), int(q[swapo(o)])
        o = 2 * (1 - a) + (1 - b)
    return seq[seen[o]:]


def properties0(p, first, g):
    """efficient, stable, competitive at eps = 0 for the deterministic memory-one p opening with `first` (1 = C)"""
    R, S, T, P = g
    val = {0: (R, R), 1: (S, T), 2: (T, S), 3: (P, P)}                  # (own, co-player's) payoff of each outcome
    cyc = play0(p, p, first, first)
    E = sum(val[o][0] for o in cyc) / F(len(cyc))
    dev, rel = [], []
    for q in BINARY:
        for fq in (0, 1):
            cyc = play0(p, q, first, fq)
            own = sum(val[o][0] for o in cyc) / F(len(cyc))
            other = sum(val[o][1] for o in cyc) / F(len(cyc))
            if not (q == tuple(map(F, p)) and fq == first):
                dev.append(other)                                       # a co-player other than p itself
            rel.append(own - other)
    emax = max(R, (T + S) / 2)
    return dict(eff=E == emax, nash=max(dev) <= E, comp=min(rel) >= 0, subm=max(rel) <= 0, E=E, emax=emax,
                dev=max(dev), tie=max(dev) == E)


def donation(b, c=F(1)):
    b, c = F(b), F(c)
    return (b - c, -c, b, F(0))


# ------------------------------------------------------------- the strategies of the table
ALLD, ALLC, TFT, WSLS = (0, 0, 0, 0), (1, 1, 1, 1), (1, 0, 1, 0), (1, 0, 0, 1)


def gtft(q):
    return (F(1), F(q), F(1), F(q))


def zd_generous(b, c, chi):
    """p - (1, 1, 0, 0) = phi [(S_X - R) - chi (S_Y - R)], phi = 1/(2 (1 + chi) b): pi_X - R = chi (pi_Y - R)"""
    phi = F(1) / (2 * (1 + chi) * b)
    t = [0, -(b + chi * c), c + chi * b, (chi - 1) * (b - c)]
    return (1 + phi * t[0], 1 + phi * t[1], phi * t[2], phi * t[3])


def zd_extortionate(b, c, chi):
    """p - (1, 1, 0, 0) = phi [(S_X - P) - chi (S_Y - P)], phi = 1/(2 (1 + chi) b): pi_X - P = chi (pi_Y - P)"""
    phi = F(1) / (2 * (1 + chi) * b)
    t = [(b - c) * (1 - chi), -c - chi * b, b + chi * c, 0]
    return (1 + phi * t[0], 1 + phi * t[1], phi * t[2], phi * t[3])


def zd_equaliser(b, c):
    """p - (1, 1, 0, 0) = beta (S_Y - pi0), pi0 = (b - c)/2, beta = -1/(2 (b + c)): pi_Y = pi0 whatever Y does"""
    pi0, beta = (b - c) / 2, -F(1) / (2 * (b + c))
    t = [b - c - pi0, b - pi0, -c - pi0, -pi0]
    return (1 + beta * t[0], 1 + beta * t[1], beta * t[2], beta * t[3]), pi0


def zd_relation(p, g, kind, chi=None, pi0=None):
    """does the defining zero-determinant relation hold in the limit against all 16 co-players and against itself"""
    R, S, T, P = g
    ok = True
    for q in BINARY + [p]:
        w = limit_weights(p, q)
        x, y = pay(w, g), pay((w[0], w[2], w[1], w[3]), g)
        if kind == "generous":
            ok &= x - R == chi * (y - R)
        elif kind == "extortionate":
            ok &= x - P == chi * (y - P)
        else:
            ok &= y == pi0
    return ok


GAMES = [F(3, 2), F(2), F(3), F(5)]                                      # b/c, with c = 1


def cases():
    """for each row of the table, the list of (description, properties) it is checked on"""
    out = {}
    out[0] = [("b=%s" % b, properties(ALLD, donation(b))) for b in GAMES]
    out[1] = [("b=%s" % b, properties(ALLC, donation(b))) for b in GAMES]
    out[2] = [("b=%s, eps=0, TFT opens with C" % b, properties0(TFT, 1, donation(b))) for b in GAMES]
    out[3] = [("b=%s" % b, properties(TFT, donation(b))) for b in GAMES]
    out[4] = [("b=%s" % b, properties(WSLS, donation(b))) for b in (F(3), F(5), F(21, 10))]
    out[5] = [("b=%s" % b, properties(WSLS, donation(b))) for b in (F(3, 2), F(19, 10))]
    rows = []
    for b in GAMES:
        qs = 1 - 1 / b                                                   # q* = 1 - c/b
        for q in (qs / 100, qs / 2, qs * 99 / 100):
            rows.append(("b=%s, q=%s (q*=%s)" % (b, q, qs), properties(gtft(q), donation(b))))
    out[6] = rows
    rows = []
    for b in GAMES:
        for chi in (F(2), F(3)):
            p = zd_generous(b, F(1), chi)
            assert all(0 <= x <= 1 for x in p) and zd_relation(p, donation(b), "generous", chi=chi)
            rows.append(("b=%s, chi=%s, p=(%s)" % (b, chi, ", ".join(str(x) for x in p)), properties(p, donation(b))))
    out[7] = rows
    rows = []
    for b in GAMES:
        for chi in (F(2), F(3)):
            p = zd_extortionate(b, F(1), chi)
            assert all(0 <= x <= 1 for x in p) and zd_relation(p, donation(b), "extortionate", chi=chi)
            rows.append(("b=%s, chi=%s, p=(%s)" % (b, chi, ", ".join(str(x) for x in p)), properties(p, donation(b))))
    out[8] = rows
    rows = []
    for b in GAMES:
        p, pi0 = zd_equaliser(b, F(1))
        assert all(0 <= x <= 1 for x in p) and zd_relation(p, donation(b), "equaliser", pi0=pi0)
        rows.append(("b=%s, pi0=%s, p=(%s)" % (b, pi0, ", ".join(str(x) for x in p)), properties(p, donation(b))))
    out[9] = rows
    return out


def label(pr):
    code = (pr["eff"], pr["nash"], pr["comp"])
    if code[0] and code[2]:
        return "friendly rival"
    if code[0] and code[1]:
        return "partner"
    if code[2]:
        return "rival"
    if code == (False, True, False):
        return "stable only"
    if code == (True, False, False):
        return "submissive" if pr["subm"] else "efficient only"
    return "none"


# ------------------------------------------------------------- SI Table 1 as printed (ms.tex, 2026-09-25)
PAPER = r"""
\ALLD                          & --         & $\checkmark$ & $\checkmark$ & rival\\
\ALLC                          & $\checkmark$ & --         & --         & submissive\\
tit-for-tat, no errors, cooperative start & $\checkmark$ & $\checkmark$ & $\checkmark$ & friendly rival\\
tit-for-tat, rare errors       & --         & --         & $\checkmark$ & rival\\
win-stay, lose-shift, $b>2c$   & $\checkmark$ & $\checkmark$ & --         & partner\\
win-stay, lose-shift, $b<2c$   & $\checkmark$ & --         & --         & efficient only\\
generous tit-for-tat, $0<q<q^*$  & $\checkmark$ & $\checkmark$ & --         & partner\\
generous zero-determinant      & $\checkmark$ & $\checkmark$ & --         & partner\\
extortionate zero-determinant  & --         & --         & $\checkmark$ & rival\\
equaliser zero-determinant     & --         & $\checkmark$ & --         & stable only\\
"""
LABELS = ["\\ALLD", "\\ALLC", "tit-for-tat, no errors, cooperative start", "tit-for-tat, rare errors",
          "win-stay, lose-shift, $b>2c$", "win-stay, lose-shift, $b<2c$", "generous tit-for-tat, $0<q<q^*$",
          "generous zero-determinant", "extortionate zero-determinant", "equaliser zero-determinant"]


def paper_rows(text):
    if "SI Table 1:" in text:
        text = text[text.index("SI Table 1:"):]
        text = text[text.index("\\midrule") + len("\\midrule"):text.index("\\bottomrule")]
    rows = []
    for line in text.strip().splitlines():
        line = line.strip().rstrip("\\").strip()
        if line:
            cells = [c.strip() for c in line.split("&")]
            assert len(cells) == 5, line
            rows.append(cells)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tex", help="compare with SI Table 1 in this LaTeX file instead of the built-in copy")
    args = ap.parse_args()
    rows = paper_rows(open(args.tex).read() if args.tex else PAPER)
    assert [r[0] for r in rows] == LABELS, "the printed rows are not the expected ten"
    mark = lambda x: "yes" if x else "--"
    C = cases()
    nbad = 0
    print("SI Table 1, checked at donation games (R,S,T,P) = (b-c, -c, b, 0), c = 1, exact, eps -> 0 unless stated\n")
    for k, (lab, pe, pn, pc, pcls) in enumerate(rows):
        want = tuple("checkmark" in x for x in (pe, pn, pc))
        print("%s  [printed: efficient %s, stable %s, competitive %s, %s]"
              % (re.sub(r"[\\$]", "", lab), mark(want[0]), mark(want[1]), mark(want[2]), pcls))
        for desc, pr in C[k]:
            got = (pr["eff"], pr["nash"], pr["comp"])
            ok = got == want and label(pr) == pcls
            nbad += not ok
            extra = "  pi(self)=%s, best other co-player earns %s%s" % (pr["E"], pr["dev"], " (a tie)" if pr["tie"] else "")
            print("    %-4s %-60s efficient %-3s stable %-3s competitive %-3s %-15s%s"
                  % ("ok" if ok else "DIFF", desc, mark(got[0]), mark(got[1]), mark(got[2]), label(pr), extra))
    # the boundaries named in the caption and the text
    print("\nBoundaries:")
    for b in GAMES:
        qs = 1 - 1 / b
        at, above, zero = properties(gtft(qs), donation(b)), properties(gtft(qs * 101 / 100), donation(b)), properties(gtft(0), donation(b))
        print("  generous tit-for-tat, b=%s: at q=q*=%s stable with a tie %s; just above q* stable %s; at q=0 (tit-for-tat) efficient %s"
              % (b, qs, at["nash"] and at["tie"], above["nash"], zero["eff"]))
    tie = properties(WSLS, donation(2))
    print("  win-stay, lose-shift at b=2c: efficient %s, stable %s with a tie %s (T+P = 2R: ALLD earns (T+P)/2 = R against it)"
          % (tie["eff"], tie["nash"], tie["tie"]))
    print("\n%s" % ("every row agrees with the printed table" if not nbad else "%d case(s) DIFFER from the printed table" % nbad))
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
