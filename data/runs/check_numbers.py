#!/usr/bin/env python3
"""
The numbers the paper quotes from the four main Wright-Fisher runs, recomputed from the deposited tables of this
folder and compared with the text of the paper.

    python3 check_numbers.py      (from this folder, or from anywhere: paths are relative to this file)

First the tables are checked for consistency (the shares add to one, the atom sizes to the size of the space, the
derived columns P_*, abundant and enriched equal their recomputation from S and N).  Then every quoted number is
recomputed and printed next to the value in the text, with OK or DIFF; the exit status is the number of DIFFs.
The place in the paper is given by section: Abstract, Results (main text), Conclusion, Methods, SI section 'The
evolutionary maps' (SI evol.), SI Table 6, SI Table 7a, SI section 'Memory one, for contrast' (SI m1), and the
figure legends.  Counts are of the 512 sampled games; a game counts for its most abundant (most enriched) atom.

Regions (common.atoms, data/games/games.csv): quadrants PD (u < 0 < v), SD, SH, HA; wedges W (below the switch line
u + v = 1, T > S), S (below it, T < S), N (above it, T > S), E (above it, T < S).  "Above the switch line" is N or E.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))
from common import atoms, games, tables                             # noqa: E402

ORDER, IDX = atoms.ORDER, atoms.IDX
NSTRAT = {"m1": 16, "m2": 65536}
G = games.games()
QUAD, WEDGE = G["quadrant"], G["wedge"]
U, V = G["u"], G["v"]
RAD = np.hypot(U, V)
PIECES = [("PD/W", (QUAD == "PD") & (WEDGE == "W")), ("PD/N", (QUAD == "PD") & (WEDGE == "N")),
          ("SH/W", (QUAD == "SH") & (WEDGE == "W")), ("SH/S", (QUAD == "SH") & (WEDGE == "S")),
          ("HA/W", (QUAD == "HA") & (WEDGE == "W")), ("HA/S", (QUAD == "HA") & (WEDGE == "S")),
          ("HA/E", (QUAD == "HA") & (WEDGE == "E")), ("SD", QUAD == "SD")]
PIECE = dict(PIECES)
WS = WEDGE == "S"
ABOVE = (WEDGE == "N") | (WEDGE == "E")
RESULTS = []


class Run:
    def __init__(self, name):
        self.name, self.space = name, name[:2]
        T = tables.read_table(os.path.join(HERE, name + ".csv"))
        self.T = T
        self.S, self.N, self.E = tables.atom_array(T, "S"), tables.atom_array(T, "N"), T["E"]
        self.wa = np.array([IDX.index(c) for c in T["abundant"]])       # ORDER indices
        self.we = np.array([IDX.index(c) for c in T["enriched"]])
        self.P = {k: T[k] for k in ("P_eff", "P_nash", "P_comp")}
        self.enr = np.where(self.N > 0, self.S * NSTRAT[self.space] / np.maximum(self.N, 1), np.nan)

    def lead(self, code, mask=None, enriched=False):
        w = self.we if enriched else self.wa
        m = np.ones(512, bool) if mask is None else mask
        return int(((w == ORDER.index(code)) & m).sum())


def check(where, what, got, want):
    ok = str(got) == str(want)
    RESULTS.append(ok)
    print("  %-4s %-16s %-78s %10s   text %s" % ("OK" if ok else "DIFF", where, what, got, want))


def consistency(R):
    S, N = R.S, R.N
    assert (R.T["ipt"] == np.arange(512)).all()
    assert (np.column_stack([R.T["u"], R.T["v"]]) == games.uv()).all(), "the games are those of data/games"
    assert np.allclose(S.sum(1), 1.0, rtol=0, atol=1e-9) and (S >= 0).all()
    assert (N.sum(1) == NSTRAT[R.space]).all() and (N >= 0).all()
    assert not S[N == 0].any(), "an empty atom holds population"
    for k, (nm, _, a) in zip(("P_eff", "P_nash", "P_comp"), atoms.PROPS):
        assert (S[:, atoms.members(a)].sum(1) == R.P[k]).all(), (R.name, k)
    assert (np.where(N > 0, S, -np.inf).argmax(1) == R.wa).all(), R.name
    assert (np.where(N > 0, S / np.maximum(N, 1), -np.inf).argmax(1) == R.we).all(), R.name
    assert (R.T["nrep"] == 10).all()
    print("  %-9s consistent: shares add to 1, sizes to %d, P_*, abundant, enriched recomputed" % (R.name, NSTRAT[R.space]))


def f(x, nd):
    return "%.*f" % (nd, x)


def main():
    R = {n: Run(n) for n in ("m1_N100", "m1_N1000", "m2_N100", "m2_N1000")}
    m1s, m1, m2s, m2 = R["m1_N100"], R["m1_N1000"], R["m2_N100"], R["m2_N1000"]
    print("Table consistency")
    for r in R.values():
        consistency(r)
    # the m1 counts tables and the atoms give the m1 atom shares bit for bit
    A = tables.read_table(os.path.join(HERE, "m1_strategy_atoms.csv"))
    codes = np.column_stack([A["a%d" % k] for k in range(16)])
    for r, cn in ((m1, "m1_N1000_counts"), (m1s, "m1_N100_counts")):
        C = tables.read_table(os.path.join(HERE, cn + ".csv"))
        cnt = np.column_stack([C["c%d" % k] for k in range(16)])
        assert (cnt.sum(1) == C["ntot"]).all()
        S8 = np.zeros((512, 8))
        for i in range(512):
            for k in range(16):
                S8[i, codes[i, k]] += cnt[i, k]
            S8[i] /= float(C["ntot"][i])
        assert (S8[:, IDX] == r.S).all(), cn
        N8 = np.array([np.bincount(codes[i], minlength=8) for i in range(512)])
        assert (N8[:, IDX] == r.N).all(), cn
        p = cnt / C["ntot"][:, None].astype(float)
        assert (p.argmax(1) == r.T["top"]).all() and (p.max(1) == r.T["maxpi"]).all()
        print("  %-9s the per-strategy counts and atoms give S, N, top and maxpi bit for bit" % cn[:-7])

    print("\nAbstract")
    check("Abstract", "m2 N=1000: 110 most abundant at", m2.lead("110"), 323)
    check("Abstract", "m2 N=1000: 111 most abundant at", m2.lead("111"), 186)
    check("Abstract", "m2 N=1000: 111 most enriched at", m2.lead("111", enriched=True), 261)
    check("Abstract", "m2 N=1000: efficiency below 0.9 at", int((m2.E < 0.9).sum()), 10)
    check("Abstract", "m1 N=1000: efficiency below 0.9 at", int((m1.E < 0.9).sum()), 324)

    print("\nResults, 'Evolution of memory one' (Figure 4a-c)")
    check("Results", "m1 N=1000: efficiency below 0.9 at", int((m1.E < 0.9).sum()), 324)
    check("Results", "m1 N=1000: mean payoff negative at", int((m1.E < 0).sum()), 77)
    check("Results", "m1 N=1000: 111 most abundant at games of wedge S", "%d/%d" % (m1.lead("111", WS), WS.sum()), "126/126")
    check("Results", "m1 N=1000: 110 most abundant at", m1.lead("110"), 60)
    order = sorted([c for c in ORDER if m1.lead(c)], key=lambda c: -m1.lead(c))
    check("Results", "m1 N=1000: the atoms by the number of games they lead", " > ".join(order), "000 > 111 > 001 > 011 > 110")
    sh = PIECE["SH/W"] & (m1.wa == ORDER.index("011"))
    check("Results", "m1 N=1000: SH with T>S led by 011 whose top strategy is ALLD (0) or Grim (1)",
          "%d/%d" % (np.isin(m1.T["top"][sh], [0, 1]).sum(), sh.sum()), "%d/%d" % (sh.sum(), sh.sum()))
    wsls = np.isin(codes[:, 9], [6, 7])                                  # WSLS (strategy 9) is a partner, 110 or 111
    check("Results", "m1 N=1000: WSLS a partner, 011 (ALLD, Grim) most abundant, games / of them SH", "%d / %d"
          % ((wsls & (m1.wa == ORDER.index("011"))).sum(), (wsls & (m1.wa == ORDER.index("011")) & (QUAD == "SH")).sum()), "63 / 52")

    print("\nResults, 'Evolution of memory two' (Figure 4d-f)")
    check("Results", "m2 N=1000: 110 most abundant at", m2.lead("110"), 323)
    check("Results", "m2 N=1000: 111 most abundant at", m2.lead("111"), 186)
    check("Results", "m2 N=1000: 111 most abundant at games of wedge S", "%d/%d" % (m2.lead("111", WS), WS.sum()), "126/126")
    n111S = sorted(set(m2.N[WS, ORDER.index("111")].tolist()))
    check("Results", "m2: friendly rivals (N_111) at every game of wedge S", n111S, [1519])
    check("Results", "m2 N=1000: 111 most abundant at Harmony games above the switch line", m2.lead("111", PIECE["HA/E"]), 27)
    check("Results", "m2 N=1000: 111 most abundant at PDs above the switch line", m2.lead("111", PIECE["PD/N"]), 14)
    eight = (m2.N[:, ORDER.index("110")] == 0) & (m2.N[:, ORDER.index("111")] == 8)
    check("Results", "m2: games at which the eight friendly rivals are the only partners", int(eight.sum()), 20)
    check("Results", "m2 N=1000: ... of which 111 is the most abundant atom", m2.lead("111", eight), 19)
    check("Results", "m2 N=1000: efficiency below 0.9 at", int((m2.E < 0.9).sum()), 10)
    print("       (the 10: radii %s; all in %s)" % (", ".join("%.1f" % r for r in np.sort(RAD[m2.E < 0.9])),
                                                   ", ".join(sorted(set(QUAD[m2.E < 0.9].tolist())))))
    check("Results", "m2 N=1000: mean efficiency in the PD below the switch line (PD/W)", "%.0f%%" % (100 * m2.E[PIECE["PD/W"]].mean()), "96%")

    print("\nResults, 'Which properties the population has' (Figure 5)")
    both = (m2.P["P_eff"] > 0.5) & (m2.P["P_nash"] > 0.5)
    check("Results", "m2 N=1000: shares of the efficient and of the stable strategies both above 1/2 at", int(both.sum()), 509)
    check("Results", "m2 N=1000: mean efficient share", f(m2.P["P_eff"].mean(), 2), "0.95")
    check("Results", "m2 N=1000: mean share on stable strategies", f(m2.P["P_nash"].mean(), 2), "0.94")
    check("Results", "m2 N=1000: mean competitive share", f(m2.P["P_comp"].mean(), 2), "0.37")
    c5 = m2.P["P_comp"] > 0.5
    check("Results", "m2 N=1000: competitive share above 1/2 at", int(c5.sum()), 186)
    check("Results", "m2 N=1000: ... of which 111 is the most abundant atom", m2.lead("111", c5), 185)
    e5 = m1.P["P_eff"] > 0.5
    check("Results", "m1 N=1000: efficient share above 1/2 at", int(e5.sum()), 186)
    check("Results", "m1 N=1000: ... at all of which the share on stable strategies is above 1/2", "%d/%d" % ((m1.P["P_nash"][e5] > 0.5).sum(), e5.sum()), "186/186")
    noeff = sum(m1.N[:, i] for i in atoms.members(atoms.PROPS[0][2])) == 0
    check("Results", "m1: games with no efficient strategy = the games above the switch line", "%d/%d" % ((noeff == ABOVE).sum(), 512), "512/512")
    check("Results", "m1 N=1000: share on stable strategies above 1/2 at", int((m1.P["P_nash"] > 0.5).sum()), 268)
    check("Results", "m1 N=1000: competitive share above 1/2 at", int((m1.P["P_comp"] > 0.5).sum()), 315)
    none = (m1.P["P_eff"] <= 0.5) & (m1.P["P_nash"] <= 0.5) & (m1.P["P_comp"] <= 0.5)
    check("Results", "m1 N=1000: games at which no property holds half the population", int(none.sum()), 137)
    check("Results", "m1 N=1000: ... of them in the Snowdrift quadrant", int((none & (QUAD == "SD")).sum()), 105)

    print("\nResults, 'Enrichment' (Figure 4c, f)")
    n0 = m2.N[:, 0] / 65536.0
    check("Results", "m2: share of the space in 000, mean over the games ('four fifths')", "%.1f" % n0.mean(), "0.8")
    print("       (per game %.2f to %.2f, median %.2f, mean %.3f)" % (n0.min(), n0.max(), np.median(n0), n0.mean()))
    check("Results", "m2: friendly rivals at every game of the PD wedge W", sorted(set(m2.N[PIECE["PD/W"], 6].tolist())), [8])
    check("Results", "m2 N=1000: 111 most enriched at", m2.lead("111", enriched=True), 261)
    check("Results", "m2 N=1000: 110 most enriched at", m2.lead("110", enriched=True), 249)
    for code, want in (("111", 18), ("110", 15)):
        e = m2.enr[:, ORDER.index(code)]
        check("Results", "m2 N=1000: geometric-mean enrichment of %s (over the games where it is non-empty)" % code,
              "%.0f" % 10 ** np.nanmean(np.log10(e)), want)
    oth = [ORDER.index(c) for c in ("000", "100", "010", "001", "011")]
    print("       (other atoms enriched above 1: %s games of 512, where non-empty)"
          % ", ".join("%s %d" % (ORDER[i], int(np.sum(m2.enr[:, i] > 1))) for i in oth))
    check("Results", "m2: 111 more often most enriched than most abundant (261 vs 186)",
          "%d vs %d" % (m2.lead("111", enriched=True), m2.lead("111")), "261 vs 186")
    e0, e1 = m2.enr[:, ORDER.index("110")], m2.enr[:, ORDER.index("111")]
    both = m2.N[:, ORDER.index("110")] > 0
    check("Results", "m2 N=1000: 110 more enriched than 111 per strategy, games of W / of N",
          " ".join("%d/%d" % ((both & (WEDGE == w) & (e0 > e1)).sum(), (WEDGE == w).sum()) for w in "WN"), "152/179 98/121")
    check("Results", "m2 N=1000: 111 more enriched than 110 at every game of S and E with a 110",
          " ".join("%d/%d" % ((both & (WEDGE == w) & (e1 > e0)).sum(), (both & (WEDGE == w)).sum()) for w in "SE"), "124/124 71/71")
    for code, want in (("001", 154), ("111", 126), ("011", 95), ("000", 77), ("110", 60)):
        check("Results", "m1 N=1000: %s most enriched at" % code, m1.lead(code, enriched=True), want)

    print("\nResults, 'Additional evolutionary simulations'")
    check("Results", "m2 N=100: mean efficiency in PD/W ('about 60%', one decimal)", f(m2s.E[PIECE["PD/W"]].mean(), 1), "0.6")
    check("Results", "m2 N=1000: mean efficiency in PD/W", "%.0f%%" % (100 * m2.E[PIECE["PD/W"]].mean()), "96%")

    print("\nConclusion")
    check("Conclusion", "m2 N=1000: at least 0.9 of the attainable payoff at all but", int((m2.E < 0.9).sum()), 10)
    check("Conclusion", "m2 N=1000: 110 / 111 most abundant at", "%d / %d" % (m2.lead("110"), m2.lead("111")), "323 / 186")
    check("Conclusion", "m2 N=1000: 111 leads wedge S / HA above / PD above / eight-only",
          "%d %d %d %d/%d" % (m2.lead("111", WS), m2.lead("111", PIECE["HA/E"]), m2.lead("111", PIECE["PD/N"]),
                              m2.lead("111", eight), eight.sum()), "126 27 14 19/20")
    check("Conclusion", "m2 N=1000: 111 most enriched at", m2.lead("111", enriched=True), 261)
    check("Conclusion", "m1 N=1000: 111 at all games of wedge S / 110 at / E < 0.9 at",
          "%d/%d %d %d" % (m1.lead("111", WS), WS.sum(), m1.lead("110"), (m1.E < 0.9).sum()), "126/126 60 324")

    print("\nMethods")
    check("Methods", "m2 N=1000: effective number of strategies, median", "%.0f" % np.median(m2.T["neff"]), "68")
    check("Methods", "m2 N=1000: share of the most abundant strategy, median", f(np.median(m2.T["maxpi"]), 2), "0.05")
    check("Methods", "m1: games whose ten replicates split between basins, N=100 / N=1000",
          "%d / %d" % (m1s.T["split"].sum(), m1.T["split"].sum()), "59 / 11")
    for r, nm, med, n5 in ((m2s, "m2 N=100", "0.77", 30), (m2, "m2 N=1000", "0.92", 1),
                           (m1s, "m1 N=100", "1.00", 19), (m1, "m1 N=1000", "0.96", 18)):
        srt = np.sort(np.where(r.N > 0, r.S, -np.inf), 1)
        check("Methods", "%s: share of the most abundant atom, median" % nm, f(np.median(srt[:, -1]), 2), med)
        check("Methods", "%s: games decided by less than five points" % nm, int(((srt[:, -1] - srt[:, -2]) < 0.05).sum()), n5)
    for r, nm, want in ((m1, "m1 N=1000", "1.4"), (m2, "m2 N=1000", "1.5"), (m1s, "m1 N=100", "2.4"), (m2s, "m2 N=100", "0.2")):
        le = np.sort(np.where(np.isnan(r.enr), -np.inf, np.log10(np.where(np.isnan(r.enr), 1.0, np.maximum(r.enr, 1e-300)))), 1)
        check("Methods", "%s: most enriched atom's lead over the runner-up, median decades" % nm, f(np.median(le[:, -1] - le[:, -2]), 1), want)
    check("Methods", "m1: enrichment ceiling of the friendly rivals, 16/|111| (|111| = 2)",
          "%g" % (16.0 / m1.N[WS, ORDER.index("111")].max()), "8")
    for r, nm, mu in ((m1s, "m1 N=100", 1e-4), (m2s, "m2 N=100", 1e-4), (m1, "m1 N=1000", 1e-2), (m2, "m2 N=1000", 1e-2)):
        print("       (%s: smallest enrichment %.2g; the floor mu = %g)" % (nm, np.nanmin(r.enr), mu))
    check("Methods", "m2 N=100: efficiency not above 0.9 at", int((m2s.E < 0.9).sum()), 91)
    check("Methods", "m2 N=100: ... of them in PD/W", int(((m2s.E < 0.9) & PIECE["PD/W"]).sum()), 74)
    check("Methods", "m2 N=100: median efficiency in PD/W", f(np.median(m2s.E[PIECE["PD/W"]]), 2), "0.63")
    check("Methods", "m2 N=1000: efficiency not above 0.9 at", int((m2.E < 0.9).sum()), 10)
    check("Methods", "m1: efficiency above 0.9 at, N=100 / N=1000", "%d / %d" % ((m1s.E > 0.9).sum(), (m1.E > 0.9).sum()), "181 / 188")
    check("Methods", "m1: median efficiency in PD/W, N=100 / N=1000",
          "%s / %s" % (f(np.median(m1s.E[PIECE["PD/W"]]), 2), f(np.median(m1.E[PIECE["PD/W"]]), 2)), "0.08 / 0.41")
    check("Methods", "m1: mean payoff negative at, N=100 / N=1000", "%d / %d" % ((m1s.E < 0).sum(), (m1.E < 0).sum()), "57 / 77")
    neg = np.unique(QUAD[(m1.E < 0) | (m1s.E < 0)]).tolist()
    check("Methods", "m1: the quadrants of the negative games", neg, ["PD", "SH"])

    print("\nSI evol., 'The maps by region'")
    check("SI evol.", "m2 N=1000: 111 leads wedge S, PD above, HA above", "%d %d %d" % (m2.lead("111", WS), m2.lead("111", PIECE["PD/N"]),
                                                                                   m2.lead("111", PIECE["HA/E"])), "126 14 27")
    r19 = RAD[eight & (m2.wa == ORDER.index("111"))]
    check("SI evol.", "m2 N=1000: radii of the 19 eight-only games the eight lead", "%.1f-%.1f" % (r19.min(), r19.max()), "2.4-16.2")
    l100 = m2.wa == ORDER.index("100")
    check("SI evol.", "m2 N=1000: the quadrant of the games 100 leads", sorted(set(QUAD[l100].tolist())), ["SD"])
    print("       (their distance from the line T = S, |u - v - 1|: %s)" % ", ".join("%.2f" % abs(U[i] - V[i] - 1) for i in np.nonzero(l100)[0]))
    check("SI evol.", "mean efficiency over PD/W, N=100 / N=1000", "%s / %s" % (f(m2s.E[PIECE["PD/W"]].mean(), 3), f(m2.E[PIECE["PD/W"]].mean(), 3)),
          "0.595 / 0.961")
    worst = int(np.argmin(m2s.E + m2.E))
    check("SI evol.", "the worst game of both maps, (u, v)", "(%.2f,%.2f)" % (U[worst], V[worst]), "(-26.99,14.68)")
    check("SI evol.", "its efficiency, N=100 / N=1000", "%s / %s" % (f(m2s.E[worst], 3), f(m2.E[worst], 2)), "-0.021 / 0.19")
    check("SI evol.", "it is the worst game at both sizes", "%s" % (int(np.argmin(m2s.E)) == worst == int(np.argmin(m2.E))), "True")
    check("SI evol.", "it is the one eight-only game the eight do not lead at N=1000",
          "%s" % (np.nonzero(eight & (m2.wa != ORDER.index("111")))[0].tolist() == [worst]), "True")
    check("SI evol.", "efficient share above 1/2, N=100 / N=1000", "%d / %d" % ((m2s.P["P_eff"] > 0.5).sum(), (m2.P["P_eff"] > 0.5).sum()), "458 / 511")
    check("SI evol.", "share on stable strategies above 1/2, N=100 / N=1000", "%d / %d" % ((m2s.P["P_nash"] > 0.5).sum(), (m2.P["P_nash"] > 0.5).sum()), "468 / 510")

    print("\nSI Table 6 (the two memory-two maps by piece of the plane)")
    TAB6 = {  # piece: games, N=100 (110, 111, other, eff), N=1000 (110, 111, other, eff) -- as typeset
        "PD/W": (86, (44, 0, "000 23, 011 15, 010 3, 001 1", 74), (66, 19, "011 1", 3)),
        "PD/N": (43, (20, 23, "--", 12), (29, 14, "--", 0)),
        "SH/W": (84, (84, 0, "--", 5), (84, 0, "--", 3)),
        "SH/S": (44, (44, 0, "--", 0), (0, 44, "--", 3)),
        "HA/W": (4, (4, 0, "--", 0), (4, 0, "--", 0)),
        "HA/S": (82, (40, 42, "--", 0), (0, 82, "--", 1)),
        "HA/E": (42, (17, 24, "001 1", 0), (15, 27, "--", 0)),
        "SD": (127, (111, 0, "100 15, 000 1", 0), (125, 0, "100 2", 0)),
        "all": (512, (364, 89, "000 24, 100 15, 011 15, 010 3, 001 2", 91), (323, 186, "100 2, 011 1", 10)),
    }

    def row(r, m):
        oth = [(c, r.lead(c, m)) for c in ORDER if c not in ("110", "111") and r.lead(c, m)]
        oth.sort(key=lambda t: (-t[1], ORDER.index(t[0])))
        return (r.lead("110", m), r.lead("111", m), ", ".join("%s %d" % t for t in oth) or "--", int(((r.E < 0.9) & m).sum()))

    for piece, m in PIECES + [("all", np.ones(512, bool))]:
        got = (int(m.sum()), row(m2s, m), row(m2, m))
        check("SI Table 6", piece, str(got), str(TAB6[piece]))

    print("\nSI Table 7a, rows 1 and 8 (the two runs of Figure 4 and SI Figure 4)")
    for r, want in ((m2s, "359 89 364 91 42 0 74"), (m2, "512 186 323 10 126 19 3")):
        got = "%d %d %d %d %d %d %d" % ((r.wa == m2.wa).sum(), r.lead("111"), r.lead("110"), (r.E < 0.9).sum(),
                                        r.lead("111", WS), r.lead("111", PIECE["PD/W"]), ((r.E < 0.9) & PIECE["PD/W"]).sum())
        check("SI Table 7a", "%s: agree, led by 111, 110, eff<0.9, 111 in S, in PD/W, PD/W eff<0.9" % r.name, got, want)

    print("\nSI evol., 'Which partners win'")
    check("SI evol.", "m2 N=100: median share of 111 in wedge S", f(np.median(m2s.S[WS, ORDER.index("111")]), 2), "0.36")
    check("SI evol.", "m2 N=100: games of PD/W the eight lead", m2s.lead("111", PIECE["PD/W"]), 0)
    n110 = m2.N[PIECE["PD/W"], ORDER.index("110")]
    check("SI evol.", "m2: other partners (110) beside the eight in PD/W, where there are any",
          "%d to %d" % (n110[n110 > 0].min(), n110.max()), "28 to 2732")
    w = (WEDGE == "W") & (m2.N[:, ORDER.index("110")] > 0)
    check("SI evol.", "m2 N=1000: wedge-W games with other partners that 110 leads", "%d/%d" % ((m2.wa[w] == ORDER.index("110")).sum(), w.sum()),
          "%d/%d" % (w.sum(), w.sum()))
    check("SI evol.", "m2: fewest other partners at such a game", int(m2.N[w, ORDER.index("110")].min()), 28)
    dep = m2.enr[:, ORDER.index("111")] < 1
    check("SI evol.", "m2 N=1000: the eight depleted at SH/W games", "%d/%d" % ((dep & PIECE["SH/W"]).sum(), PIECE["SH/W"].sum()), "84/84")
    check("SI evol.", "m2 N=1000: the eight depleted at PD/W games", "%d/%d" % ((dep & PIECE["PD/W"]).sum(), PIECE["PD/W"].sum()), "32/86")

    print("\nSI evol., 'Replicates' (what the per-game tables can give; the per-replicate counts are SI Figure 11's)")
    for r, want in ((m2s, "0.58"), (m2, "0.87")):
        srt = np.sort(np.where(r.N > 0, r.S, -np.inf), 1)
        check("SI evol.", "%s: margin between the two largest atom shares, median" % r.name, f(np.median(srt[:, -1] - srt[:, -2]), 2), want)
    for r, want in ((m2s, 14), (m2, 3)):
        m = r.T["efsd"] > 0.1
        check("SI evol.", "%s: s.d. of the efficiency over the replicates above 0.1, at Stag Hunts / all" % r.name,
              "%d / %d" % ((m & (QUAD == "SH")).sum(), m.sum()), "%d / %d" % (want, want))

    print("\nSI m1, 'Evolution at memory one'")
    for r, want in ((m1s, "011 141, 111 126, 000 120, 110 63, 001 62"), (m1, "000 154, 111 126, 001 90, 011 82, 110 60")):
        got = sorted([(c, r.lead(c)) for c in ORDER if r.lead(c)], key=lambda t: (-t[1], ORDER.index(t[0])))
        check("SI m1", "%s: most abundant atom" % r.name, ", ".join("%s %d" % t for t in got), want)
    check("SI m1", "the two memory-one runs agree on the most abundant atom at", int((m1s.wa == m1.wa).sum()), 413)
    check("SI m1", "replicates split between basins, N=100 / N=1000", "%d / %d" % (m1s.T["split"].sum(), m1.T["split"].sum()), "59 / 11")
    spl = (m1s.T["split"] == 1) | (m1.T["split"] == 1)
    print("       (the split games by quadrant: %s)" % ", ".join("%s %d" % (q, ((QUAD == q) & spl).sum()) for q in ("PD", "SD", "SH", "HA")))
    for r, want in ((m1s, "0.37 0.62 0.61"), (m1, "0.35 0.54 0.59")):
        check("SI m1", "%s: mean efficient, stable, competitive shares" % r.name,
              " ".join(f(r.P[k].mean(), 2) for k in ("P_eff", "P_nash", "P_comp")), want)
    check("SI m1", "111 leads all games of wedge S, N=100 / N=1000", "%d %d /%d" % (m1s.lead("111", WS), m1.lead("111", WS), WS.sum()), "126 126 /126")
    check("SI m1", "median share of 111 in wedge S, N=100 / N=1000",
          "%s / %s" % (f(np.median(m1s.S[WS, 6]), 2), f(np.median(m1.S[WS, 6]), 2)), "1.00 / 0.97")
    l110 = (m1s.wa == ORDER.index("110")) | (m1.wa == ORDER.index("110"))
    check("SI m1", "the 110 games lie within |(u, v)| < 9", "%s" % (RAD[l110].max() < 9), "True")
    check("SI m1", "110 games in SH/W, N=100 / N=1000", "%d / %d" % (m1s.lead("110", PIECE["SH/W"]), m1.lead("110", PIECE["SH/W"])), "39 / 32")
    m110 = (codes == 6)                                              # (512, 16): strategy k in atom 110 at the game
    want110 = np.zeros((512, 16), bool)
    want110[:, 9] = True                                             # WSLS
    want110[:, 15] = want110[:, 7] = V < 0                           # ALLC and CCCD where v < 0
    check("SI m1", "at every 110 game the atom 110 is WSLS and, where v < 0, also ALLC and CCCD",
          "%s" % (m110[l110] == want110[l110]).all(), "True")
    for r, want in ((m1s, "39/63"), (m1, "35/60")):
        l = r.wa == ORDER.index("110")
        t = r.T["top"][l]
        check("SI m1", "%s: 110 games whose most abundant strategy is WSLS (9)" % r.name, "%d/%d" % ((t == 9).sum(), l.sum()), want)
        rest = t[t != 9]
        check("SI m1", "%s: ... ALLC (15) or CCCD (7) at most of the others" % r.name,
              "%s" % (np.isin(rest, [15, 7]).sum() > len(rest) / 2), "True")
        print("       (%s: the others ALLC at %d, CCCD at %d, other strategies at %d)"
              % (r.name, (rest == 15).sum(), (rest == 7).sum(), (~np.isin(rest, [15, 7])).sum()))
    check("SI m1", "011 games in SH/W, N=100 / N=1000 (the other ones of 84)",
          "%d / %d" % (m1s.lead("011", PIECE["SH/W"]), m1.lead("011", PIECE["SH/W"])), "45 / 52")
    check("SI m1", "011 games in PD/W, N=100 / N=1000", "%d / %d" % (m1s.lead("011", PIECE["PD/W"]), m1.lead("011", PIECE["PD/W"])), "70 / 30")
    check("SI m1", "m1 N=1000: 001 games in PD/W", m1.lead("001", PIECE["PD/W"]), 34)
    check("SI m1", "m1 N=1000: 000 games in PD above the switch line", "%d/%d" % (m1.lead("000", PIECE["PD/N"]), PIECE["PD/N"].sum()), "32/43")
    for r in (m1s, m1):
        he = PIECE["HA/E"]
        check("SI m1", "%s: 001 leads most Harmony games above the switch line" % r.name,
              "%s" % (r.lead("001", he) > he.sum() / 2), "True")
        print("       (%s HA/E: %s)" % (r.name, ", ".join("%s %d" % (c, r.lead(c, he)) for c in ORDER if r.lead(c, he))))
        check("SI m1", "%s: 000 leads Snowdrift games" % r.name, "%d/%d" % (r.lead("000", QUAD == "SD"), (QUAD == "SD").sum()), "105/127")
    check("SI m1", "memory one and two agree on the most abundant atom, N=100 / N=1000",
          "%d / %d" % ((m1s.wa == m2s.wa).sum(), (m1.wa == m2.wa).sum()), "120 / 187")

    print("\nFigure legends")
    RR = tables.read_table(os.path.join(HERE, "runs.csv"))
    for k, nm in enumerate(RR["name"]):
        want = {"m1_N100": "100 3 0.0001 0.0001 100000000 10", "m1_N1000": "1000 100 0.01 0.0001 10000000 10",
                "m2_N100": "100 3 0.0001 0.0001 100000000 10", "m2_N1000": "1000 100 0.01 0.0001 10000000 10"}[nm]
        got = " ".join(repr(RR[c][k].item()) for c in ("N", "beta", "mu", "eps", "generations", "replicates"))
        check("Fig. 4, SI 2-5", "%s: N, beta, mu, eps, generations, replicates" % nm, got, want)
    check("SI Fig. 4", "m2 N=100: most enriched 111 / 110", "%d / %d" % (m2s.lead("111", enriched=True), m2s.lead("110", enriched=True)), "379 / 120")
    b = (m2s.P["P_eff"] > 0.5) & (m2s.P["P_nash"] > 0.5)
    check("SI Fig. 5", "m2 N=100: shares of the efficient and of the stable strategies both above 1/2 at", int(b.sum()), 442)
    check("SI Fig. 5", "m2 N=100: competitive share above 1/2 at", int((m2s.P["P_comp"] > 0.5).sum()), 101)
    check("SI Fig. 5", "m1 N=100: efficient / stable / competitive share above 1/2 at",
          "%d / %d / %d" % tuple((m1s.P[k] > 0.5).sum() for k in ("P_eff", "P_nash", "P_comp")), "186 / 314 / 342")
    none = (m1s.P["P_eff"] <= 0.5) & (m1s.P["P_nash"] <= 0.5) & (m1s.P["P_comp"] <= 0.5)
    check("SI Fig. 5", "m1 N=100: no property holds half, games / of them SD", "%d / %d" % (none.sum(), (none & (QUAD == "SD")).sum()), "109 / 105")
    nonash = sum(m1.N[:, i] for i in atoms.members(atoms.PROPS[1][2])) == 0
    outside = (QUAD == "SD") & ((U > 1) | (V > 1))
    check("Fig. 5", "m1: no stable strategy exactly at the Snowdrift games outside the unit square", "%s" % (nonash == outside).all(), "True")

    nd = RESULTS.count(False)
    print("\n%d numbers checked: %d agree with the text, %d differ" % (len(RESULTS), RESULTS.count(True), nd))
    return nd


if __name__ == "__main__":
    sys.exit(main())
