#!/usr/bin/env python3
"""
check_strict.py -- reads the tables of data/strict/ and checks that they agree with each other and with data/games.
Then it recomputes, from the tables alone, every number the paper states about the strict Nash equilibria at
eps = 1e-4 (Methods, "Strict equilibria"; SI, "Strict equilibria at memory one" and "Why partners and not strict
equilibria"; the legends of SI Figures 6 and 7) and prints it.

    python3 check_strict.py          (from any directory; about two seconds; needs numpy)

Each line printed is asserted: the script stops at the first number that the tables do not give.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir))
from common import games, tables                                   # noqa: E402

NICK = {0: "ALLD", 1: "Grim", 9: "WSLS", 15: "ALLC", 8: "DDDC", 14: "DCCC", 6: "DCCD", 7: "CCCD"}


def say(what, got, want=None):
    """print a checked number; want is the value the tables must give (default: got itself, i.e. a receipt)"""
    if want is not None:
        if isinstance(want, float):                                 # a quoted float: to the digits given (0.1 %)
            ok = abs(got - want) <= 1e-3 * abs(want) if want else got == 0.0
        else:
            ok = bool(got == want)
        assert ok, "%s: the tables give %r, expected %r" % (what, got, want)
    print("  %-86s %s" % (what, got if not isinstance(got, float) else "%.4g" % got))


def unpack(mask):
    """(n,) int masks -> (n, 16) bool"""
    return ((np.asarray(mask)[:, None] >> np.arange(16)) & 1).astype(bool)


def main():
    G = games.games()
    u, v, q, wedge = G["u"], G["v"], G["quadrant"], G["wedge"]
    below = u + v < 1                                               # no game lies on the switch line
    T1 = tables.read_table(os.path.join(HERE, "m1_games.csv"))
    S1 = tables.read_table(os.path.join(HERE, "m1_sets.csv"))
    T2 = tables.read_table(os.path.join(HERE, "m2_games.csv"))
    S2 = tables.read_table(os.path.join(HERE, "m2_sets.csv"))
    C2 = tables.read_table(os.path.join(HERE, "m2_float64_check.csv"))

    # ------------------------------------------------------------------------------------------ consistency
    for T in (T1, T2):
        assert np.array_equal(T["ipt"], np.arange(512)) and np.array_equal(T["u"], u) and np.array_equal(T["v"], v)
    for S in (S1, S2):
        key = S["ipt"] * 65536 + S["s"]
        assert (np.diff(key) > 0).all(), "set rows not sorted by (ipt, s)"
    M1 = unpack(T1["strict_mask"])
    E1 = unpack(T1["eff_strict_mask"])
    assert np.array_equal(T1["n_strict"], M1.sum(1)) and np.array_equal(T1["n_eff_strict"], E1.sum(1))
    assert np.array_equal(E1, M1 & unpack(T1["eff_mask"]))
    assert np.array_equal(T1["eff_mask"], np.where(below, 2 ** 15 + 2 ** 9 + 2 ** 7, 0)), "memory one: efficient = CCCC, CDDC, CCCD below"
    assert np.array_equal(T1["n_strict"], np.bincount(S1["ipt"], minlength=512))
    assert np.array_equal(M1[S1["ipt"], S1["s"]], np.ones(len(S1["s"]), bool)) and M1.sum() == len(S1["s"])
    assert np.array_equal(E1[S1["ipt"], S1["s"]], S1["efficient"].astype(bool))
    for w in ("F2", "F1"):
        for key, sel in (("share_", np.ones(len(S1["s"]), bool)), ("share_eff_", S1["efficient"] == 1)):
            c = np.bincount(S1["ipt"][sel], weights=S1["c_" + w][sel].astype(float), minlength=512)
            assert np.array_equal(c / T1["ntot_" + w].astype(float), T1[key + w]), "memory-one share differs from the counts"
    assert np.array_equal(T2["n_strict"], np.bincount(S2["ipt"], minlength=512))
    assert np.array_equal(T2["n_eff_strict"], np.bincount(S2["ipt"], weights=S2["efficient"], minlength=512).astype(int))
    effrule = np.where(below[S2["ipt"]], S2["mutual_cooperator"], S2["alternator"]).astype(bool)
    assert np.array_equal(S2["efficient"].astype(bool), effrule), "efficient is not 'mutual cooperator below, alternator above'"
    assert np.array_equal(T2["n_eff"], np.where(below, 7639, 3072))
    start = np.searchsorted(S2["ipt"], np.arange(513))
    for i in range(512):                                            # the shares are sums of the rows, bit for bit
        r = slice(start[i], start[i + 1])
        e = S2["efficient"][r] == 1
        for w in ("F2", "F1"):
            pi = S2["pi_" + w][r]
            assert np.sum(pi) == T2["share_" + w][i] and np.sum(pi[e]) == T2["share_eff_" + w][i], (i, w)
    nf = np.bincount(S2["ipt"], weights=S2["float64_strict"], minlength=512).astype(int)
    assert np.array_equal(nf, T2["n_strict_float64"])
    off = S2["float64_strict"] == 0
    assert np.array_equal(S2["ipt"][off], C2["ipt"]) and np.array_equal(S2["s"][off], C2["s"])
    assert np.array_equal(S2["pi_F2"][off], C2["pi_F2"]) and np.array_equal(S2["pi_F1"][off], C2["pi_F1"])
    assert np.array_equal(C2["gid"], 2000 + C2["ipt"])
    print("the five tables are consistent with each other and with data/games")

    # ------------------------------------------------------------------------------------------ memory two
    n2 = T2["n_strict"]
    print("\nmemory two, strict Nash equilibria among the 65536 at eps = 1e-4 (Methods, 'Strict equilibria'; SI Figure 6d-f)")
    say("weak and strict equilibria coincide: games where they differ", int((T2["n_weak"] != n2).sum()), 0)
    say("strict equilibria per game, largest", int(n2.max()), 645)
    say("strict equilibria per game, median", float(np.median(n2)), 15.0)
    say("strict (game, strategy) pairs, all games", int(n2.sum()), 65547)
    say("games with none", int((n2 == 0).sum()), 111)
    say("Snowdrift games / Snowdrift games with none", ((q == "SD").sum(), int(((q == "SD") & (n2 == 0)).sum())), (127, 111))
    say("games with none outside the Snowdrift quadrant", int(((q != "SD") & (n2 == 0)).sum()), 0)
    m = (q == "SD") & (n2 > 0)
    say("Snowdrift games with strict equilibria", int(m.sum()), 16)
    say("  their largest |(u, v)|", float(np.hypot(u[m], v[m]).max()), 1.9525)
    say("  strict equilibria per game there, fewest and most", (int(n2[m].min()), int(n2[m].max())), (4, 16))
    say("  of them below the switch line", int((m & below).sum()), 5)
    rows = m[S2["ipt"]]
    mc = S2["mutual_cooperator"][rows] == 1
    say("  their strict equilibria: all / mutual cooperators", (int(rows.sum()), int(mc.sum())), (127, 112))
    nmc = rows & (S2["mutual_cooperator"] == 0)
    say("  the others (neither mutual cooperators nor alternators) at the games ipt", sorted(set(S2["ipt"][nmc].tolist())),
        [2, 7, 10, 15])
    say("  ... all below the switch line, where the mutual cooperators are efficient", bool(below[S2["ipt"][nmc]].all()), True)
    say("strict (game, strategy) pairs that are alternators", int(S2["alternator"].sum()), 0)
    for w, N, top in (("F2", 100, 0.03998), ("F1", 1000, 0.19325)):
        say("share of the population on strict equilibria, N = %d: largest" % N, float(T2["share_" + w].max()), top)
    say("  ... N = 1000: below one fifth at every game", bool((T2["share_F1"] < 0.2).all()), True)
    say("  ... N = 100: below 0.04 at every game", bool((T2["share_F2"] < 0.04).all()), True)
    for w, N, med in (("F2", 100, 0.001126), ("F1", 1000, 0.003356)):
        say("  ... N = %d: median over the 512 games" % N, float(np.median(T2["share_" + w])), med)

    print("\nmemory two, the double-precision brute force against the exact one-flip test (Methods; m2_float64_check.csv)")
    say("pairs at which they disagree", len(C2["s"]), 160)
    say("  in how many games", len(set(C2["ipt"].tolist())), 102)
    say("  exact strict and float64 not / float64 strict and exact not", (int(off.sum()), 0), (160, 0))
    say("  the residents (code: pairs)", dict(zip(*[x.tolist() for x in np.unique(C2["s"], return_counts=True)])),
        {61449: 1, 63359: 50, 63903: 8, 65535: 101})
    say("  ... all of them mutual cooperators", bool(S2["mutual_cooperator"][off].all()), True)
    say("  quadrants (Stag Hunt, Harmony)", (int((q[C2["ipt"]] == "SH").sum()), int((q[C2["ipt"]] == "HA").sum())), (107, 53))
    say("  float64 margins", sorted(set(C2["margin_float64"].tolist())), [-2.220446049250313e-16, -1.1102230246251565e-16, 0.0])
    say("  quadruple-precision margins: all positive", bool((C2["margin_quad"] > 0).all()), True)
    say("  ... smallest, largest", (float("%.3g" % C2["margin_quad"].min()), float("%.3g" % C2["margin_quad"].max())),
        (1.55e-18, 2.86e-16))
    say("  ... below one ulp of 1.0 (2.2e-16)", int((C2["margin_quad"] < 2.0 ** -52).sum()), 143)
    say("strict pairs in the float64 scan / games with none there", (int(T2["n_strict_float64"].sum()),
                                                                     int((T2["n_strict_float64"] == 0).sum())), (65387, 147))
    for w, N, top, dmed in (("F2", 100, 0.001279, 4.19e-05), ("F1", 1000, 0.02155, 6.56e-06)):
        d = np.bincount(C2["ipt"], weights=C2["pi_" + w], minlength=512)
        say("population on the 160 at a game, N = %d: largest" % N, float(d.max()), top)
        say("  ... median over the 102 games", float("%.3g" % np.median(d[d > 0])), dmed)
        say("  ... largest share on strict equilibria with the float64 sets instead", float((T2["share_" + w] - d).max()),
            float(T2["share_" + w].max()))
        say("  ... median share with the float64 sets instead", float(np.median(T2["share_" + w] - d)),
            {"F2": 0.001126, "F1": 0.0003748}[w])

    ne = T2["n_eff_strict"]
    print("\nmemory two, efficient strict equilibria (SI Figure 7d-f; SI, 'Why partners and not strict equilibria')")
    say("per game, largest", int(ne.max()), 128)
    say("games above the switch line with one", int((ne[~below] > 0).sum()), 0)
    say("Stag Hunt games with 128 of them / Stag Hunt games", (int(((q == "SH") & (ne == 128)).sum()), int((q == "SH").sum())),
        (71, 128))
    pd = q == "PD"
    say("Prisoner's Dilemmas with one: largest v (all have T < 3R - 2P, i.e. v < 2)", float(v[pd & (ne > 0)].max()), 1.9961)
    say("Prisoner's Dilemmas with v >= 2: strict equilibria there that are mutual cooperators",
        int(S2["mutual_cooperator"][(pd & (v >= 2))[S2["ipt"]]].sum()), 0)
    for w, N, top, frac in (("F2", 100, 0.03810, 0.8533), ("F1", 1000, 0.19325, 0.9887)):
        say("share on them, N = %d: largest" % N, float(T2["share_eff_" + w].max()), top)
        say("  ... summed over the games, as a fraction of the share on all strict equilibria",
            float(T2["share_eff_" + w].sum() / T2["share_" + w].sum()), frac)

    # ------------------------------------------------------------------------------------------ memory one
    n1 = T1["n_strict"]
    print("\nmemory one, strict Nash equilibria among the 16 at eps = 1e-4 (Methods; SI, 'Strict equilibria at memory one'; "
          "SI Figure 6a-c)")
    say("weak and strict equilibria coincide: games where they differ", int((T1["n_weak"] != n1).sum()), 0)
    say("strict equilibria per game, fewest and most", (int(n1.min()), int(n1.max())), (0, 7))
    who = [s for s in range(16) if M1[:, s].any()]
    say("strategies strict at some game", [NICK.get(s, s) for s in who], ["ALLD", "Grim", "DCCD", "DDDC", "WSLS", "DCCC", "ALLC"])
    say("  ALLD strict exactly where u < 0 (games)", (bool(np.array_equal(M1[:, 0], u < 0)), int(M1[:, 0].sum())), (True, 257))
    say("  ALLC strict exactly where v < 0 (games)", (bool(np.array_equal(M1[:, 15], v < 0)), int(M1[:, 15].sum())), (True, 256))
    say("  WSLS strict exactly where u < 1 and v < 1 (games)", (bool(np.array_equal(M1[:, 9], (u < 1) & (v < 1))),
                                                                int(M1[:, 9].sum())), (True, 199))
    say("  Grim, DDDC, DCCC, DCCD: games", tuple(int(M1[:, s].sum()) for s in (1, 8, 14, 6)), (224, 143, 113, 71))
    say("games with seven, all Stag Hunt", (int((n1 == 7).sum()), sorted(set(q[n1 == 7].tolist()))), (71, ["SH"]))
    out = (q == "SD") & ~((u < 1) & (v < 1))
    say("games with none = the Snowdrift games outside the unit square", (bool(np.array_equal(n1 == 0, out)), int(out.sum())),
        (True, 119))
    NL = unpack(T1["nash_limit_mask"])
    say("CCCD: stable in the limit exactly where v <= 0 / strict (or weak) at eps = 1e-4 anywhere",
        (bool(np.array_equal(NL[:, 7], v <= 0)), bool(M1[:, 7].any())), (True, False))
    say("strict at eps = 1e-4 but not stable in the limit: (game, strategy) pairs", int((M1 & ~NL).sum()), 0)
    say("wedge S: games / ALLC strict at all of them", (int((wedge == "S").sum()), bool(M1[wedge == "S", 15].all())), (126, True))
    for w, N, k in (("F2", 100, 258), ("F1", 1000, 246)):
        say("share of the population on strict equilibria above 1/2, N = %d: games" % N, int((T1["share_" + w] > 0.5).sum()), k)
    say("efficient strict equilibria per game, most", int(T1["n_eff_strict"].max()), 2)
    say("  which: ALLC exactly where v < 0 below the switch line (games)",
        (bool(np.array_equal(E1[:, 15], (v < 0) & below)), int(E1[:, 15].sum())), (True, 214))
    say("  WSLS exactly where it is strict below the switch line (games)",
        (bool(np.array_equal(E1[:, 9], M1[:, 9] & below)), int(E1[:, 9].sum())), (True, 196))
    say("  no other", [s for s in range(16) if E1[:, s].any()], [9, 15])
    for w, N, k in (("F2", 100, 117), ("F1", 1000, 163)):
        say("share on the efficient ones above 1/2, N = %d: games" % N, int((T1["share_eff_" + w] > 0.5).sum()), k)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
