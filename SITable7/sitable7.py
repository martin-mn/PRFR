#!/usr/bin/env python3
"""
SI Table 7: robustness of the memory-two maps -- the cube of parameters, the error rate and the mutation kernel -- and
the numbers of the paragraphs "Population size, selection strength and mutation rate", "The error rate" and "The
mutation kernel" of the SI section "The evolutionary maps".

    python3 SITable7/sitable7.py         ->  SITable7/SITable7.csv, SITable7/SITable7.tex (the rows of the tabular),
                                             and the comparison with the published table on the terminal

Rows: a, the eight corners of {N} x {beta} x {mu} at eps = 1e-4 in the reading order of SI Figure 8; b, the two runs of
Figure 4d-f and SI Figure 4d-f at eps = 1e-3 and 1e-5; c, the run of Figure 4d-f under the mixed mutation kernel,
nu = 0, 0.1, 0.5.  Columns:
    agree          games whose most abundant atom is that of the reference map: for a and c main text Figure 4e (f1_e4),
                   for b the same run at eps = 1e-4 (f1_e4 for N = 1000, f2_e4 for N = 100)
    led by 111/110 games whose most abundant atom is 111 / 110
    eff. < 0.9     games with realised efficiency below 0.9 (the pooled efficiency E of games_<run>.csv)
    111 in S       games of the wedge S (126 sampled) that 111 leads
    111 in PD/W    games of the Prisoner's Dilemma part of the wedge W (86 sampled) that 111 leads
    PD/W eff.<0.9  games of PD/W with efficiency below 0.9
The most abundant atom is the one of the figures (common.wfsheet.winners).

Data: data/robustness/games_<run>.csv, replicates_<run>.csv, runs.csv, m2_atom_sizes.csv (data/robustness/wfruns.py)
and data/games/games.csv.  PUBLISHED below is SI Table 7 as typeset in the paper; the script stops if an entry differs.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "data", "robustness"))
from common import games, tables                                    # noqa: E402
from common.atoms import ORDER                                      # noqa: E402
import wfruns                                                       # noqa: E402

I000, I100, I110, I111 = (ORDER.index(a) for a in ("000", "100", "110", "111"))
# (block, run, reference run for "agree")
ROWS = [("a", "f2_e4", "f1_e4"), ("a", "c2_e4", "f1_e4"), ("a", "c4_e4", "f1_e4"), ("a", "dw4_e4", "f1_e4"),
        ("a", "c3_e4", "f1_e4"), ("a", "c1_e4", "f1_e4"), ("a", "dw3_e4", "f1_e4"), ("a", "f1_e4", "f1_e4"),
        ("b", "eh_e3", "f1_e4"), ("b", "eh_e5", "f1_e4"), ("b", "el_e3", "f2_e4"), ("b", "el_e5", "f2_e4"),
        ("c", "lm_g0_e4", "f1_e4"), ("c", "lm_g01_e4", "f1_e4"), ("c", "lm_g05_e4", "f1_e4")]
# SI Table 7 of the paper (ms.tex): (N, beta, mu, eps, nu) and then agree, 111, 110, eff<0.9, 111 in S,
# 111 in PD/W, PD/W eff<0.9
PUBLISHED = [
    ((100, 3, "1e-4", "1e-4", 1.0), (359, 89, 364, 91, 42, 0, 74)),
    ((100, 3, "1e-2", "1e-4", 1.0), (410, 136, 341, 88, 70, 14, 70)),
    ((1000, 3, "1e-4", "1e-4", 1.0), (420, 129, 373, 28, 59, 23, 28)),
    ((1000, 3, "1e-2", "1e-4", 1.0), (485, 199, 300, 12, 126, 22, 3)),
    ((100, 100, "1e-4", "1e-4", 1.0), (409, 103, 373, 66, 64, 0, 62)),
    ((100, 100, "1e-2", "1e-4", 1.0), (467, 152, 351, 76, 93, 17, 57)),
    ((1000, 100, "1e-4", "1e-4", 1.0), (485, 189, 312, 30, 123, 15, 30)),
    ((1000, 100, "1e-2", "1e-4", 1.0), (512, 186, 323, 10, 126, 19, 3)),
    ((1000, 100, "1e-2", "1e-3", 1.0), (494, 184, 315, 43, 126, 15, 23)),
    ((1000, 100, "1e-2", "1e-5", 1.0), (508, 184, 326, 10, 126, 20, 1)),
    ((100, 3, "1e-4", "1e-3", 1.0), (480, 109, 345, 88, 61, 0, 72)),
    ((100, 3, "1e-4", "1e-5", 1.0), (500, 89, 365, 90, 41, 0, 73)),
    ((1000, 100, "1e-2", "1e-4", 0.0), (461, 149, 313, 3, 126, 12, 3)),
    ((1000, 100, "1e-2", "1e-4", 0.1), (469, 157, 313, 7, 126, 15, 5)),
    ((1000, 100, "1e-2", "1e-4", 0.5), (494, 176, 318, 8, 126, 18, 5)),
]
COLS = ["agree", "led111", "led110", "eff_below_0.9", "led111_in_S", "led111_in_PDW", "PDW_eff_below_0.9"]

G = games.games()
QUAD, WEDGE, U, V = G["quadrant"], G["wedge"], G["u"], G["v"]
SW = WEDGE == "S"
PDW = (QUAD == "PD") & (WEDGE == "W")
ABOVE = U + V > 1                                                   # above the switch line (the wedges N and E)
_RUNS = {}


def run(name):
    if name not in _RUNS:
        g = wfruns.load(name)
        g["wa"] = np.where(g["N"] > 0, g["S"], -np.inf).argmax(1)                         # most abundant atom
        g["we"] = np.where(g["N"] > 0, g["S"] / np.maximum(g["N"], 1), -np.inf).argmax(1)  # most enriched atom
        _RUNS[name] = g
    return _RUNS[name]


def row(name, ref):
    g, r = run(name), run(ref)
    wa, E = g["wa"], g["E"]
    return ((wa == r["wa"]).sum(), (wa == I111).sum(), (wa == I110).sum(), (E < 0.9).sum(),
            ((wa == I111) & SW).sum(), ((wa == I111) & PDW).sum(), ((E < 0.9) & PDW).sum())


def tex_power(s):
    return "$10^{%d}$" % int(round(np.log10(float(s))))


def text_numbers():
    f1, f2 = run("f1_e4"), run("f2_e4")
    print("Population size, selection strength and mutation rate:")
    single = [("c3_e4", "beta"), ("c2_e4", "mu"), ("c4_e4", "N")]
    print("  from the small-population run (111 leads %d) each factor alone: %s"
          % ((f2["wa"] == I111).sum(), ", ".join("%s -> %d" % (f, (run(r)["wa"] == I111).sum()) for r, f in single)))
    print("  111 in the wedge S (126): %s" % ", ".join("%s %d" % (r, ((run(r)["wa"] == I111) & SW).sum())
                                                    for r in ("f2_e4", "c3_e4", "c2_e4", "c4_e4", "c1_e4", "dw3_e4", "dw4_e4", "f1_e4")))
    c1 = run("c1_e4")
    print("  N = 100, beta = 100, mu = 1e-2 (c1): 110 leads %d of the 126 games of S (%.2f)" % (((c1["wa"] == I110) & SW).sum(), ((c1["wa"] == I110) & SW).sum() / 126.0))
    print("The error rate:")
    for r, ref in (("eh_e3", "f1_e4"), ("eh_e5", "f1_e4"), ("el_e3", "f2_e4"), ("el_e5", "f2_e4")):
        g = run(r)
        print("  %s: most abundant atom as at eps = 1e-4 at %d games; efficiency < 0.9 at %d (1e-4: %d), mean %.3f (1e-4: %.3f)"
              % (r, (g["wa"] == run(ref)["wa"]).sum(), (g["E"] < 0.9).sum(), (run(ref)["E"] < 0.9).sum(), g["E"].mean(), run(ref)["E"].mean()))
    el3 = run("el_e3")
    print("  N = 100, eps = 1e-3: %d games of S pass from 110 to 111 (and %d from 111 to 110)"
          % (((f2["wa"] == I110) & (el3["wa"] == I111) & SW).sum(), ((f2["wa"] == I111) & (el3["wa"] == I110) & SW).sum()))
    eh3 = run("eh_e3")
    lost = PDW & (f1["wa"] == I111) & (eh3["wa"] != I111)
    print("  N = 1000, eps = 1e-3: of the %d PD/W games 111 leads at 1e-4, it loses %d, to %s"
          % ((PDW & (f1["wa"] == I111)).sum(), lost.sum(), ", ".join(ORDER[i] for i in eh3["wa"][lost])))
    print("The mutation kernel:")
    for r, nu in (("lm_g0_e4", "0"), ("lm_g01_e4", "0.1"), ("lm_g05_e4", "0.5"), ("f1_e4", "1")):
        g = run(r)
        l100, l000 = g["wa"] == I100, g["wa"] == I000
        ER = g["ER"].mean(1)                                        # the replicate-mean efficiency, as a check
        top = g["LEAD"][l100] == I111                               # replicates at 100-led games whose top strategy is a friendly rival
        tsh = g["TOPSHARE"][l100][top]
        allten = (g["R"].argmax(2) == g["wa"][:, None]).all(1).sum()
        print("  nu = %-3s: agree %d; 111 leads %d of S and %d of PD/W; eff < 0.9 at %d (replicate mean: %d), mean %.3f (%.3f);"
              " 100 leads %d (%d above the switch line, %d in PD/W); 000 leads %d (%d SD above the switch line);"
              " 111 most enriched at %d; all ten replicates agree at %d"
              % (nu, (g["wa"] == f1["wa"]).sum(), ((g["wa"] == I111) & SW).sum(), ((g["wa"] == I111) & PDW).sum(),
                 (g["E"] < 0.9).sum(), (ER < 0.9).sum(), g["E"].mean(), ER.mean(), l100.sum(), (l100 & ABOVE).sum(),
                 (l100 & PDW).sum(), l000.sum(), (l000 & ABOVE & (QUAD == "SD")).sum(), (g["we"] == I111).sum(), allten))
        if l100.sum() and nu != "1":
            print("            at the 100-led games the top strategy of a replicate is a friendly rival in %d of the %d replicates;"
                  " its share: median %.4f, quartiles %.4f-%.4f" % (top.sum(), top.size, np.median(tsh), *np.quantile(tsh, [0.25, 0.75])))


def main():
    out, bad = [], 0
    print("%-2s %-10s %5s %4s %5s %5s %4s | %5s %4s %4s %6s %6s %6s %6s" % ("", "run", "N", "beta", "mu", "eps", "nu", *[c[:6] for c in COLS]))
    for k, ((blk, name, ref), (ppar, pval)) in enumerate(zip(ROWS, PUBLISHED)):
        D = run(name)["D"]
        par = (D["N"], D["beta"], D["muplain"], D["epsplain"], D["nu"])
        val = tuple(int(x) for x in row(name, ref))
        ok = par == ppar and val == pval
        bad += not ok
        out.append((blk, name, ref) + par + val)
        print("%-2s %-10s %5d %4d %5s %5s %4g | %5d %4d %4d %6d %6d %6d %6d   %s" % ((blk, name) + par + val + ("= SI Table 7" if ok else "DIFFERS: %r" % (pval,),)))
    names = ["block", "run", "reference", "N", "beta", "mu", "eps", "nu"] + COLS
    tables.write_table(os.path.join(HERE, "SITable7.csv"), {n: [r[j] for r in out] for j, n in enumerate(names)}, [
        "SI Table 7 -- robustness of the memory-two maps (written by SITable7/sitable7.py).  One row per run (data/robustness/runs.csv).",
        "block: a the cube at eps = 1e-4, b the error rate, c the mutation kernel; reference: the run whose most abundant atom",
        "'agree' compares with; N, beta, mu, eps, nu: the parameters; agree: games whose most abundant atom is the reference's;",
        "led111, led110: games whose most abundant atom is 111 / 110; eff_below_0.9: games with realised efficiency below 0.9;",
        "led111_in_S: of the 126 games of the wedge S; led111_in_PDW: of the 86 Prisoner's Dilemmas of the wedge W;",
        "PDW_eff_below_0.9: games of PD/W with efficiency below 0.9.",
    ])
    with open(os.path.join(HERE, "SITable7.tex"), "w") as f:
        f.write("% the body of SI Table 7 (between \\midrule and \\bottomrule), written by SITable7/sitable7.py\n")
        last = None
        for r in out:
            blk = r[0]
            if last is not None and blk != last:
                f.write("\\midrule\n")
            nu = "%g" % r[7]
            f.write("%s & %d & %d & %s & %s & %s & %s\\\\\n" % ("{\\bf %s}" % blk if blk != last else "", r[3], r[4], tex_power(r[5]),
                                                                tex_power(r[6]), nu, " & ".join("%d" % x for x in r[8:])))
            last = blk
    print()
    text_numbers()
    print()
    print("SI Table 7: %d of %d rows (%d entries) agree with the published table" % (len(out) - bad, len(out), 12 * len(out)))
    assert bad == 0, "SI Table 7 does not reproduce"


if __name__ == "__main__":
    main()
