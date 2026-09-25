#!/usr/bin/env python3
"""
reduce_strict.py -- how the tables of data/strict/ were made from the author's private full outputs.  They are the
data of SI Figures 6 and 7 and of the Methods paragraph "Strict equilibria".

    python3 -B reduce_strict.py [outdir]          (default outdir: ../../data/strict)

This script runs only in the author's environment (AUTHOR_ENV below). It reads outputs that are not deposited:

  * the full abundance vectors pi (65536 numbers per game) of the two memory-two Wright-Fisher runs, DiskM2WF runs F2
    (N = 100, beta = 3, mu = 1e-4) and F1 (N = 1000, beta = 100, mu = 1e-2), both at eps = 1e-4
    (Data/dw2_e4.*, dw1_e4.*: 128 MB and 242 MB of .bin);
  * the memory-one run packs of DiskM1WF (Data/mw2_e4.tsv, mw1_e4.tsv: counts of the 16 strategies per game);
  * the sixteen one-flip half-planes of every memory-two resident at eps = 1/10000, as exact integer triples
    (DiskM2WF/Data/ne16_e4, 27 MB, built by exact/exactcoef.py of github.com/martin-mn/MapBinM2);
  * the exact eps -> 0 census of the memory-two strategies (DiskM2WF/Data/exactlayer.npz, from MapBinM2's
    exact/ca1_regions.csv), which decides efficiency in the limit;
  * the double-precision brute-force margins pi(s,s) - max_{t != s} pi(t,s) of all 65536 residents at the 512 games
    (DiskM2IN/Data/ne/n100b3sun/ne_<gid>.bin, 256 MB; the program is in bruteforce/) and the quadruple-precision
    re-adjudication of its borderline verdicts (QUADFIX.dat in the same folder).

The original modules are used read-only and unchanged, and no bytecode is written:

  * FinalFigures/strictne.py, the data module of the figure script figstrict.py.  It gives the memory-one sets
    (exact in Fractions), the memory-one shares and the two memory-two caches the figures were drawn from
    (Figures/strictne_m2.npz, strictne_m2eff.npz);
  * DiskM2WF/Opt/ne16.py, exact.py and wfload.py (through strictne._walk);
  * DiskM1WF/Opt/m1load.py and m1disk.py.

Every per-game number the figure scripts read is copied from the object the original figstrict.data() used, so the
figures redrawn from the tables are the published ones. The per-strategy rows are recomputed here: the memory-two
strict sets come from ne16.verdicts and the efficient sets from exact.masks, and the abundances from the runs. They are
then checked against those per-game numbers (counts exactly, shares to the last bit; see the receipt this prints).
"""
import os
import sys

sys.dont_write_bytecode = True

# ---------------------------------------------------------------------------------------------- author's environment
AUTHOR_ENV = "/Users/martin/Documents/CL1"          # the private project tree; everything below is read-only
# ------------------------------------------------------------------------------------------------------------------
FF = os.path.join(AUTHOR_ENV, "PartnersRivals", "FinalFigures")          # strictne.py, figstrict.py
M1OPT = os.path.join(AUTHOR_ENV, "DiskM1WF", "Opt")                      # m1load.py, m1disk.py
M2OPT = os.path.join(AUTHOR_ENV, "DiskM2WF", "Opt")                      # ne16.py, exact.py, wfload.py, finalpanels.py
NEDIR = os.path.join(AUTHOR_ENV, "DiskM2IN", "Data", "ne", "n100b3sun")  # ne_<gid>.bin/.dat, QUADFIX.dat
SUNGAMES = os.path.join(AUTHOR_ENV, "DiskM2IN", "Cannon", "dk1", "games_sun.dat")  # the games the scan read

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
for p in (REPO, FF, M1OPT, M2OPT):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                                       # noqa: E402

from common import games, tables                                         # noqa: E402
import strictne                                                          # noqa: E402  (FinalFigures, read-only)

NG, NC = 512, 65536
RUNS = (("F2", 100), ("F1", 1000))                                       # (DiskM2WF / DiskM1WF run name, N)


def m1():
    """memory one: per-game arrays and the rows of the strict sets"""
    G = games.games()
    UV, weak, strict, share, strict16 = strictne.m1(compare_m2=True)
    assert np.array_equal(UV, games.uv()), "the memory-one packs list other games than data/games"
    assert np.array_equal(weak, strict), "weak and strict equilibria differ somewhere (memory one)"
    assert np.array_equal(strict16, strict), "strictness among the 16 differs from strictness against all 65536"
    eff, nashlim = strictne.m1_efficient()
    effstrict = strict & eff
    share_eff = strictne.m1_shares(effstrict)
    import m1load
    cnt, ntot = {}, {}
    for which, _ in RUNS:
        rows, _ = m1load.read_pack(which)
        assert [r[0] for r in rows] == list(range(NG))
        assert np.array_equal(np.array([(r[3], r[4]) for r in rows]), UV)
        cnt[which] = np.array([r[9] for r in rows], dtype=np.int64)                     # (512, 16)
        ntot[which] = np.array([r[8] for r in rows], dtype=np.int64)
        assert (cnt[which].sum(1) == ntot[which]).all()
        for mask, sh in ((strict, share), (effstrict, share_eff)):
            again = (cnt[which].astype(float) * mask).sum(1) / ntot[which].astype(float)
            assert np.array_equal(again, sh[which]), "memory-one share not reproduced from the counts"
    bits = 1 << np.arange(16, dtype=np.int64)
    per_game = dict(
        ipt=G["ipt"], u=G["u"], v=G["v"],
        n_strict=strict.sum(1), n_weak=weak.sum(1), strict_mask=(strict * bits).sum(1),
        n_eff_strict=effstrict.sum(1), eff_strict_mask=(effstrict * bits).sum(1),
        eff_mask=(eff * bits).sum(1), nash_limit_mask=(nashlim * bits).sum(1),
        ntot_F2=ntot["F2"], ntot_F1=ntot["F1"],
        share_F2=share["F2"], share_F1=share["F1"], share_eff_F2=share_eff["F2"], share_eff_F1=share_eff["F1"])
    ii, ss = np.nonzero(strict)
    sets = dict(ipt=ii, s=ss, strategy=[strictne.name(int(s)) for s in ss], efficient=eff[ii, ss],
                c_F2=cnt["F2"][ii, ss], c_F1=cnt["F1"][ii, ss])
    return per_game, sets


def m2():
    """memory two: per-game arrays (the figure's caches), the rows of the strict sets, and the float64 disagreements"""
    import exact
    import ne16
    G = games.games()
    UV, nstrict, nweak, share = strictne.m2()
    UVe, neffstrict, neff, share_eff = strictne.m2eff()
    assert np.array_equal(UV, games.uv()) and np.array_equal(UVe, games.uv()), "the caches list other games"
    assert np.array_equal(nweak, nstrict), "weak and strict equilibria differ somewhere (memory two)"
    assert not ((G["u"] + G["v"]) == 1).any() and not ((G["u"] - G["v"]) == 1).any(), "a game on a special line"
    d = exact.load()
    pis = {which: strictne._walk(which) for which, _ in RUNS}
    for which, _ in RUNS:
        for i in range(NG):
            assert (pis[which][i][0], pis[which][i][1]) == (G["u"][i], G["v"][i])
    # the brute-force double-precision scan and its quadruple-precision re-adjudication
    sun = {}
    for line in open(SUNGAMES):
        if line.startswith("#") or not line.strip():
            continue
        f = line.split()
        sun[int(f[0])] = (float(f[2]), float(f[3]), float(f[4]))
    fix = {}
    for line in open(os.path.join(NEDIR, "QUADFIX.dat")):
        if line.startswith("#") or not line.strip():
            continue
        f = line.split()
        fix[(int(f[0]), int(f[1]))] = (float(f[2]), float(f[3]))
    rows = {k: [] for k in ("ipt", "s", "efficient", "mutual_cooperator", "alternator", "float64_strict",
                            "pi_F2", "pi_F1")}
    chk = {k: [] for k in ("ipt", "gid", "s", "margin_float64", "margin_quad", "pi_F2", "pi_F1")}
    nfloat = np.zeros(NG, np.int64)
    dshare = {("all", w): 0.0 for w, _ in RUNS}
    dshare.update({("eff", w): 0.0 for w, _ in RUNS})
    only_theirs = 0
    for i in range(NG):
        u, v = G["u"][i], G["v"][i]
        weak, strict = ne16.verdicts(u, v)
        eff, _, _ = exact.masks(d, u, v)
        assert np.array_equal(weak, strict)
        assert strict.sum() == nstrict[i] and (strict & eff).sum() == neffstrict[i] and eff.sum() == neff[i]
        for which, _ in RUNS:
            pi = pis[which][i][2]
            dshare[("all", which)] = max(dshare[("all", which)], abs(float(pi[strict].sum()) - share[which][i]))
            dshare[("eff", which)] = max(dshare[("eff", which)], abs(float(pi[strict & eff].sum()) - share_eff[which][i]))
        gid = games.GID0 + i
        m = np.fromfile(os.path.join(NEDIR, "ne_%d.bin" % gid), dtype=np.float64)
        assert m.size == NC
        cR, cS, cT = sun[gid]                                   # the game the scan read, exactly
        assert cR == 1.0 and cS == u and cT == 1.0 + v, (gid, sun[gid], u, v)
        dat = open(os.path.join(NEDIR, "ne_%d.dat" % gid)).read().split()          # its receipt, 4 decimals
        assert int(dat[0]) == gid and abs(float(dat[2]) - u) <= 5.0001e-5 and abs(float(dat[3]) - v) <= 5.0001e-5, dat[:4]
        theirs = m > 0.0
        nfloat[i] = theirs.sum()
        only_theirs += int((theirs & ~strict).sum())
        for s in np.nonzero(strict & ~theirs)[0]:
            md, mq = fix.pop((gid, int(s)))                     # every disagreement must be a line of QUADFIX.dat
            assert abs(md - m[s]) <= 1e-11 * abs(m[s]) and mq > 0.0      # QUADFIX prints 13 significant digits
            chk["ipt"].append(i); chk["gid"].append(gid); chk["s"].append(int(s))
            chk["margin_float64"].append(float(m[s])); chk["margin_quad"].append(mq)
            chk["pi_F2"].append(float(pis["F2"][i][2][s])); chk["pi_F1"].append(float(pis["F1"][i][2][s]))
        for s in np.nonzero(strict)[0]:
            rows["ipt"].append(i); rows["s"].append(int(s)); rows["efficient"].append(bool(eff[s]))
            rows["mutual_cooperator"].append(bool(d["eff_lo"][s])); rows["alternator"].append(bool(d["eff_hi"][s]))
            rows["float64_strict"].append(bool(theirs[s]))
            rows["pi_F2"].append(float(pis["F2"][i][2][s])); rows["pi_F1"].append(float(pis["F1"][i][2][s]))
    assert not fix, "QUADFIX.dat lists %d verdicts that are not disagreements: %s" % (len(fix), sorted(fix)[:5])
    assert only_theirs == 0, "the double-precision scan calls %d pairs strict that the exact test does not" % only_theirs
    print("memory two: %d signs referred to exact integers by ne16 (0 = every verdict certified by the float screen)"
          % ne16.nrefer())
    print("memory two: per-game shares recomputed from pi vs the figure's caches, max |diff|: %s"
          % ", ".join("%s %s %.3g" % (k[0], k[1], dshare[k]) for k in sorted(dshare)))
    per_game = dict(ipt=G["ipt"], u=G["u"], v=G["v"], n_strict=nstrict, n_weak=nweak, n_eff=neff,
                    n_eff_strict=neffstrict, n_strict_float64=nfloat,
                    share_F2=share["F2"], share_F1=share["F1"], share_eff_F2=share_eff["F2"], share_eff_F1=share_eff["F1"])
    return per_game, rows, chk, dshare


STATE = ("bit k of s (k = 0..15) is 1 if the strategy intends C in state k = 4 x (the most recent outcome) + (the "
         "outcome before), outcomes 0 CC, 1 CD, 2 DC, 3 DD from the focal player's side (MapBinM2's exactcoef.py); ALLD "
         "0, ALLC 65535, the memory-one strategy with answers b_j embeds as 15 x sum_j b_j 16^j")


def main(out):
    os.makedirs(out, exist_ok=True)
    P1, S1 = m1()
    P2, S2, C2, dshare = m2()
    runs = ("F2 = the run at N = 100, beta = 3, mu = 1e-4; F1 = the run at N = 1000, beta = 100, mu = 1e-2; both eps = 1e-4 "
            "(the runs' names in the kits)")
    tables.write_table(os.path.join(out, "m1_games.csv"), P1, [
        "Memory one: the strict Nash equilibria among the 16 binary memory-one strategies at eps = 1e-4, at each of the",
        "512 games (data/games), and the share of the population on them (SI Figures 6a-c and 7a-c). One row per game,",
        "in ipt order. Strategy s = 0..15: bit j of s is 1 if s cooperates after outcome j = 0 CC, 1 CD, 2 DC, 3 DD",
        "(own action first); ALLD 0, Grim 1, TFT 5, WSLS 9, ALLC 15. A mask is sum over the strategies s in the set of 2^s.",
        runs + ".",
        "Made by provenance/strict/reduce_strict.py from FinalFigures/strictne.py (exact rational arithmetic).",
        "Columns:",
        "  ipt, u, v          the game, (R, S, T, P) = (1, u, 1 + v, 0), as in data/games/games.csv",
        "  n_strict           number of strict Nash equilibria among the 16 at eps = 1/10000 (SI Figure 6a)",
        "  n_weak             number of weak (non-strict inequality) equilibria; equal to n_strict at every game",
        "  strict_mask        the strict equilibria, as a mask",
        "  n_eff_strict       number of them that are efficient in the limit eps -> 0 (SI Figure 7a)",
        "  eff_strict_mask    those, as a mask",
        "  eff_mask           the strategies efficient in the limit at this game (CCCC, CDDC, CCCD below the switch line)",
        "  nash_limit_mask    the strategies stable in the limit eps -> 0, ties admitted (DiskM1WF's exact classification)",
        "  ntot_F2, ntot_F1   the number of sampled individual-generations of the run (the denominator of a share)",
        "  share_F2, share_F1         the share of the population on the strict equilibria (SI Figure 6b, 6c)",
        "  share_eff_F2, share_eff_F1 the same for the efficient strict equilibria (SI Figure 7b, 7c)",
        "Each share equals sum of c_F2 (c_F1) over the game's rows of m1_sets.csv, divided by ntot_F2 (ntot_F1), exactly."])
    tables.write_table(os.path.join(out, "m1_sets.csv"), S1, [
        "Memory one: one row per (game, strategy) at which the strategy is a strict Nash equilibrium among the 16 at eps = 1e-4.",
        "Rows ordered by ipt, then s. " + runs + ".",
        "Columns:",
        "  ipt          the game (data/games/games.csv)",
        "  s            the strategy 0..15 (bit j = 1: cooperate after outcome j = CC, CD, DC, DD)",
        "  strategy     its answers after CC, CD, DC, DD (ALLD DDDD, Grim CDDD, WSLS CDDC, ALLC CCCC)",
        "  efficient    1 if it is efficient in the limit eps -> 0 at this game",
        "  c_F2, c_F1   the number of sampled individual-generations on s in the run (share = c / ntot of m1_games.csv)"])
    tables.write_table(os.path.join(out, "m2_games.csv"), P2, [
        "Memory two: the strict Nash equilibria among the 65536 binary memory-two strategies at eps = 1e-4, at each of the",
        "512 games (data/games), and the share of the population on them (SI Figures 6d-f and 7d-f). One row per game, in",
        "ipt order. " + runs + ".",
        "Strict: all sixteen one-flip deviations earn strictly less against the resident than it earns against itself, which",
        "at eps > 0 is strictness against all 65535 other memory-two strategies; decided exactly on the integer half-planes of",
        "MapBinM2's exact/exactcoef.py (DiskM2WF ne16.verdicts). Made by provenance/strict/reduce_strict.py.",
        "Columns:",
        "  ipt, u, v          the game, (R, S, T, P) = (1, u, 1 + v, 0), as in data/games/games.csv",
        "  n_strict           number of strict Nash equilibria at eps = 1/10000 (SI Figure 6d)",
        "  n_weak             number of weak equilibria (all sixteen one-flip gains <= 0); equal to n_strict at every game",
        "  n_eff              number of strategies efficient in the limit eps -> 0 at the game (7639 mutual cooperators below",
        "                     the switch line u + v = 1, 3072 alternators above it)",
        "  n_eff_strict       number of strict equilibria that are efficient in the limit (SI Figure 7d)",
        "  n_strict_float64   number with a positive margin pi(s,s) - max_t pi(t,s) in the double-precision brute-force scan",
        "                     of all 65535 deviations (provenance/strict/bruteforce), as the scan wrote it; see m2_float64_check.csv",
        "  share_F2, share_F1         share of the population on the strict equilibria (SI Figure 6e, 6f)",
        "  share_eff_F2, share_eff_F1 the same for the efficient strict equilibria (SI Figure 7e, 7f)",
        "Each share equals the sum (numpy.sum, rows in file order) of pi_F2 (pi_F1) over the game's rows of m2_sets.csv%s."
        % (", bit for bit" if max(dshare.values()) == 0 else " to %.1g" % max(dshare.values()))])
    tables.write_table(os.path.join(out, "m2_sets.csv"), S2, [
        "Memory two: one row per (game, strategy) at which the strategy is a strict Nash equilibrium at eps = 1e-4 (65547 rows).",
        "Rows ordered by ipt, then s. " + runs + ".",
        "Strategy code s = 0..65535: " + STATE + ".",
        "Columns:",
        "  ipt                the game (data/games/games.csv)",
        "  s                  the strategy",
        "  efficient          1 if efficient in the limit eps -> 0 at this game (SI Figure 7)",
        "  mutual_cooperator  1 if its self-play in the limit is all CC (one of the 7639)",
        "  alternator         1 if its self-play in the limit alternates CD, DC perfectly (one of the 3072); 0 in every row",
        "  float64_strict     1 if the double-precision brute-force scan also found it strict (0 in the 160 rows of m2_float64_check.csv)",
        "  pi_F2, pi_F1       its time-averaged abundance in the run, normalised so that the 65536 abundances sum to 1"])
    tables.write_table(os.path.join(out, "m2_float64_check.csv"), C2, [
        "Memory two: the 160 (game, strategy) pairs at which the double-precision brute-force scan (every resident against all",
        "65535 alternatives; provenance/strict/bruteforce/nescan.f90) disagrees with the exact one-flip test. At every other",
        "of the 512 x 65536 pairs the two agree. In all 160 the exact test finds a strict equilibrium and the scan does not.",
        "The re-adjudication in quadruple precision (bruteforce/neq.f90, the same payoff code compiled with every double",
        "promoted to real(16)) agrees with the exact test at all 160. " + runs + ".",
        "Columns:",
        "  ipt, gid           the game (gid = 2000 + ipt)",
        "  s                  the resident (the code of m2_sets.csv)",
        "  margin_float64     pi(s,s) - max_{t != s} pi(t,s) as the double-precision scan computed it (%s)"
        % ", ".join("%.3g" % x for x in sorted(set(C2["margin_float64"]))),
        "  margin_quad        the same margin in quadruple precision, as QUADFIX.dat prints it (all positive, %.2g to %.2g)"
        % (min(C2["margin_quad"]), max(C2["margin_quad"])),
        "  pi_F2, pi_F1       the resident's abundance in the two runs (as in m2_sets.csv)"])
    print("wrote %s: m1_games.csv, m1_sets.csv (%d rows), m2_games.csv, m2_sets.csv (%d rows), m2_float64_check.csv (%d rows)"
          % (out, len(S1["s"]), len(S2["s"]), len(C2["s"])))


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(REPO, "data", "strict"))
