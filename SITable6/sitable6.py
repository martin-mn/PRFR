#!/usr/bin/env python3
"""
SI Table 6: the two memory-two maps by piece of the plane, and the numbers of the paragraph "The maps by region" of the
SI section "The evolutionary maps".

    python3 SITable6/sitable6.py         ->  SITable6/SITable6.csv, SITable6/SITable6.tex (the rows of the tabular),
                                             and the comparison with the published table on the terminal

The 512 sampled games of the two memory-two runs of SI Figure 4d-f (N = 100, beta = 3, mu = 1e-4; run f2_e4) and main
text Figure 4d-f (N = 1000, beta = 100, mu = 1e-2; run f1_e4), eps = 1e-4, grouped by quadrant and wedge
(data/games/games.csv).  For each piece and each run: the number of games whose most abundant atom is 110, 111 or
another atom (named, with its number of games), and the number of games with realised efficiency below 0.9.  The most
abundant atom is the one of the figures (common.wfsheet.winners: the largest pooled share among the atoms that have
strategies at the game).

Data: data/robustness/games_f2_e4.csv, games_f1_e4.csv, m2_atom_sizes.csv (data/robustness/wfruns.py) and
data/games/games.csv.  Nothing else is read.  PUBLISHED below is SI Table 6 as typeset in the paper; the script stops
if a single entry differs.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
from common import games, tables                                    # noqa: E402
from common.atoms import ORDER, members, PROPS                      # noqa: E402
import wfruns                                                       # noqa: E402

RUNS = [("f2_e4", "N = 100, beta = 3, mu = 1e-4"), ("f1_e4", "N = 1000, beta = 100, mu = 1e-2")]
PIECES = [("PD/$W$", "PD", "W"), ("PD/$N$", "PD", "N"), ("SH/$W$", "SH", "W"), ("SH/$S$", "SH", "S"), ("HA/$W$", "HA", "W"),
          ("HA/$S$", "HA", "S"), ("HA/$E$", "HA", "E"), ("SD", "SD", None), ("all", None, None)]

# SI Table 6 of the paper (ms.tex): piece -> games, then per run (110, 111, other, eff. < 0.9)
PUBLISHED = {
    "PD/$W$": (86, (44, 0, "000 23, 011 15, 010 3, 001 1", 74), (66, 19, "011 1", 3)),
    "PD/$N$": (43, (20, 23, "--", 12), (29, 14, "--", 0)),
    "SH/$W$": (84, (84, 0, "--", 5), (84, 0, "--", 3)),
    "SH/$S$": (44, (44, 0, "--", 0), (0, 44, "--", 3)),
    "HA/$W$": (4, (4, 0, "--", 0), (4, 0, "--", 0)),
    "HA/$S$": (82, (40, 42, "--", 0), (0, 82, "--", 1)),
    "HA/$E$": (42, (17, 24, "001 1", 0), (15, 27, "--", 0)),
    "SD": (127, (111, 0, "100 15, 000 1", 0), (125, 0, "100 2", 0)),
    "all": (512, (364, 89, "000 24, 100 15, 011 15, 010 3, 001 2", 91), (323, 186, "100 2, 011 1", 10)),
}


def most_abundant(g):
    """the most abundant atom (index into ORDER) per game, as common.wfsheet.winners computes it"""
    return np.where(g["N"] > 0, g["S"], -np.inf).argmax(1)


def others(wa, m):
    """the atoms other than 110 and 111 that lead games of the mask m, by number of games (ties in ORDER)"""
    c = [(int(((wa == i) & m).sum()), i) for i in range(7) if ORDER[i] not in ("110", "111")]
    c = sorted([x for x in c if x[0]], key=lambda x: (-x[0], x[1]))
    return ", ".join("%s %d" % (ORDER[i], n) for n, i in c) or "--"


def table():
    G = games.games()
    quad, wedge = G["quadrant"], G["wedge"]
    R = {run: wfruns.load(run) for run, _ in RUNS}
    WA = {run: most_abundant(R[run]) for run, _ in RUNS}
    out = []
    for name, q, w in PIECES:
        m = np.ones(512, bool) if q is None else (quad == q) & (np.ones(512, bool) if w is None else wedge == w)
        row = [name, int(m.sum())]
        for run, _ in RUNS:
            wa, E = WA[run], R[run]["E"]
            row += [int(((wa == 4) & m).sum()), int(((wa == 6) & m).sum()), others(wa, m), int(((E < 0.9) & m).sum())]
        out.append(row)
    return out, R, WA


def tex(rows):
    def other(s):
        return "--" if s == "--" else ", ".join("\\texttt{%s}\\,%s" % tuple(x.split()) for x in s.split(", "))
    lines = []
    for r in rows:
        if r[0] == "all":
            lines.append("\\midrule")
        lines.append("%s & %d & %d & %d & %s & %d & %d & %d & %s & %d\\\\" % (r[0], r[1], r[2], r[3], other(r[4]), r[5],
                                                                              r[6], r[7], other(r[8]), r[9]))
    return lines


def text_numbers(R, WA):
    """the numbers of the paragraph 'The maps by region' (and two of 'Which partners win') of the SI"""
    G = games.games()
    u, v, quad, wedge = G["u"], G["v"], G["quadrant"], G["wedge"]
    small, large = R["f2_e4"], R["f1_e4"]
    N = large["N"]
    i110, i111 = ORDER.index("110"), ORDER.index("111")
    pdw = (quad == "PD") & (wedge == "W")
    only8 = pdw & (N[:, i110] == 0) & (N[:, i111] == 8)                 # the eight of SI Table 4a are the only partners
    rad = np.hypot(u, v)[only8]
    lead8 = (WA["f1_e4"] == i111) & only8
    worst = int(np.argmin(small["E"]))
    print("The maps by region:")
    print("  N = 1000: 111 leads %d of the %d games of the wedge S, %d PDs and %d Harmony games above the switch line"
          % (((WA["f1_e4"] == i111) & (wedge == "S")).sum(), (wedge == "S").sum(),
             ((WA["f1_e4"] == i111) & (quad == "PD") & (wedge == "N")).sum(), ((WA["f1_e4"] == i111) & (quad == "HA") & (wedge == "E")).sum()))
    rad8 = np.hypot(u, v)[lead8]
    print("  the eight are the only partners at %d sampled PDs of W (radii %.1f to %.1f); 111 leads %d of them at N = 1000,"
          " at radii %.1f to %.1f" % (only8.sum(), rad.min(), rad.max(), lead8.sum(), rad8.min(), rad8.max()))
    print("  the other games 100 leads at N = 1000: %s (quadrant/wedge)" %
          ", ".join("%s/%s (u, v) = (%.2f, %.2f)" % (quad[i], wedge[i], u[i], v[i]) for i in np.nonzero(WA["f1_e4"] == ORDER.index("100"))[0]))
    print("  mean efficiency over the %d PDs of W: %.3f at N = 100, %.3f at N = 1000"
          % (pdw.sum(), small["E"][pdw].mean(), large["E"][pdw].mean()))
    print("  worst game of both maps: (u, v) = (%.2f, %.2f), efficiency %.3f at N = 100 (lowest: %s) and %.2f at N = 1000 (lowest: %s);"
          " one of the %d: %s; 111 leads it at N = 1000: %s"
          % (u[worst], v[worst], small["E"][worst], worst == np.argmin(small["E"]), large["E"][worst], worst == np.argmin(large["E"]),
             only8.sum(), bool(only8[worst]), WA["f1_e4"][worst] == i111))
    eff, nash = members(PROPS[0][2]), members(PROPS[1][2])
    for run, lab in (("f2_e4", "N = 100"), ("f1_e4", "N = 1000")):
        S = R[run]["S"]
        print("  %s: efficient share > 1/2 at %d games, share on stable strategies > 1/2 at %d" % (lab, (S[:, eff].sum(1) > 0.5).sum(), (S[:, nash].sum(1) > 0.5).sum()))
    print("Which partners win:")
    sw = wedge == "S"
    print("  N = 100, wedge S: median share of 111 %.2f; 111 / (110 + 111) strategies: median %.3f"
          % (np.median(small["S"][sw, i111]), np.median(N[sw, i111] / (N[sw, i110] + N[sw, i111]))))
    beside = pdw & (N[:, i111] == 8) & (N[:, i110] > 0)
    print("  PD/W games where the eight stand beside other partners: %d, with %d to %d others; 111 leads %d of them at N = 100"
          % (beside.sum(), N[beside, i110].min(), N[beside, i110].max(), ((WA["f2_e4"] == i111) & beside).sum()))
    W = wedge == "W"
    has110 = W & (N[:, i110] > 0)
    print("  N = 1000, wedge W: 110 leads %d of the %d games that have 110 strategies (fewest: %d)"
          % (((WA["f1_e4"] == i110) & has110).sum(), has110.sum(), N[has110, i110].min()))
    dep = large["S"][:, i111] < N[:, i111] / 65536.0
    shw = (quad == "SH") & W
    print("  N = 1000: the friendly rivals are depleted (share of the population < share of the strategies) at %d of the %d SHs of W"
          " and %d of the %d PDs of W" % ((dep & shw).sum(), shw.sum(), (dep & pdw).sum(), pdw.sum()))


def main():
    rows, R, WA = table()
    bad = 0
    print("%-8s %5s | %4s %4s %-38s %4s | %4s %4s %-16s %4s" % ("piece", "games", "110", "111", "other", "eff.", "110", "111", "other", "eff."))
    for r in rows:
        pub = PUBLISHED[r[0]]
        mine = (r[1], tuple(r[2:6]), tuple(r[6:10]))
        ok = mine == pub
        bad += not ok
        print("%-8s %5d | %4d %4d %-38s %4d | %4d %4d %-16s %4d   %s" % (tuple(r) + ("= SI Table 6" if ok else "DIFFERS: %r" % (pub,),)))
    names = ["piece", "games"] + ["%s_%s" % (k, run) for run, _ in RUNS for k in ("lead110", "lead111", "other", "eff_below_0.9")]
    cols = {n: [r[j] if not isinstance(r[j], str) else r[j].replace("$", "").replace(", ", "; ") for r in rows] for j, n in enumerate(names)}
    tables.write_table(os.path.join(HERE, "SITable6.csv"), cols, [
        "SI Table 6 -- the two memory-two maps by piece of the plane, eps = 1e-4 (written by SITable6/sitable6.py).",
        "Runs: f2_e4 (N = 100, beta = 3, mu = 1e-4; SI Figure 4d-f) and f1_e4 (N = 1000, beta = 100, mu = 1e-2; main text",
        "Figure 4d-f).  piece: quadrant/wedge (data/games/games.csv; SD: the Snowdrift games of every wedge); games: sampled",
        "games in the piece; lead110, lead111: games whose most abundant atom is 110 / 111; other: the other leading atoms",
        "with their numbers of games, '--' if none; eff_below_0.9: games with realised efficiency below 0.9.",
    ])
    with open(os.path.join(HERE, "SITable6.tex"), "w") as f:
        f.write("% the body of SI Table 6 (between \\midrule and \\bottomrule), written by SITable6/sitable6.py\n")
        f.write("\n".join(tex(rows)) + "\n")
    print()
    text_numbers(R, WA)
    print()
    print("SI Table 6: %d of %d rows (%d entries) agree with the published table" % (len(rows) - bad, len(rows), 9 * len(rows)))
    assert bad == 0, "SI Table 6 does not reproduce"


if __name__ == "__main__":
    main()
