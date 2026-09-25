#!/usr/bin/env python3
"""reduce.py -- the raw outputs of the four census passes -> the per-strategy tables of data/census/.

    python3 reduce.py <outdir> [<datadir>]        default <datadir>: ../data/census next to this folder

<outdir> holds the outputs of both programs for the four passes, as written by run_local.sh or by the Cannon kit
(cannon/task.sh): <prog>_<pass>_<stripe>.txt and .err with prog in {pairsq (exact), pairs (double)} and pass in
{self, rivP, rivM, nash}.  Any number of stripes is accepted; every strategy must occur exactly once per pass.

Writes to <datadir>:
    census.csv          one row per strategy, from the EXACT program pairsq, plus defensibility (defensible.py)
    census_double.csv   the same columns from the double-precision program pairs (without defensibility)
    passes.csv          one row per program, pass and stripe: what the program reported on stderr
    m2_masks.npz        the six boolean masks effCC, effALT, rivP, rivM, defP, defM (the file the figure scripts read)

The column definitions are written into the header of each table and into data/census/README.md.
"""
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))
sys.path.insert(0, HERE)
from common.tables import write_table          # noqa: E402
import defensible                               # noqa: E402

NC = 65536
PASSES = ("self", "rivP", "rivM", "nash")
NCOL = {"self": 4, "rivP": 1, "rivM": 1, "nash": 5}
PROGS = {"pairsq": "exact rational arithmetic (pairsq.c)", "pairs": "double precision, tolerance 1e-9 (pairs.c)"}

ERR = {  # the one line each pass may print on stderr, and what it carries
    ("pairsq", "rivP"): r"stripe (\d+): exact; smallest nonzero \|wDC-wCD\| = (\S+), chains=(\d+), largest integer met=(\d+)$",
    ("pairs", "rivP"): r"stripe (\d+): gapmin\(nonzero \|wDC-wCD\|\)=(\S+), chains=(\d+)$",
    ("pairsq", "nash"): r"stripe (\d+): nash exact, largest integer met=(\d+)$",
}
ERR[("pairsq", "rivM")] = ERR[("pairsq", "rivP")]
ERR[("pairs", "rivM")] = ERR[("pairs", "rivP")]


def read_pass(outdir, prog, mode):
    """{code: [fields...]} for one program and pass, and the parsed stderr lines"""
    rows, logs = {}, []
    files = sorted(glob.glob(os.path.join(outdir, "%s_%s_*.txt" % (prog, mode))))
    if not files:
        raise SystemExit("no %s_%s_*.txt in %s" % (prog, mode, outdir))
    for f in files:
        stripe = int(re.search(r"_(\d+)\.txt$", f).group(1))
        for line in open(f):
            p = line.split()
            if not p:
                continue
            assert len(p) == 1 + NCOL[mode], (f, line)
            s = int(p[0])
            assert s not in rows, "strategy %d twice in %s %s" % (s, prog, mode)
            rows[s] = p[1:]
        err = f[:-4] + ".err"
        text = open(err).read().strip() if os.path.exists(err) else ""
        pat = ERR.get((prog, mode))
        rec = {"stripe": stripe, "chains": -1, "gap_min": float("nan"), "max_int": -1}
        if pat is None:
            assert text == "", "unexpected stderr in %s: %r" % (err, text[:200])
        else:
            m = re.match(pat, text)
            assert m and int(m.group(1)) == stripe, "unexpected stderr in %s: %r" % (err, text[:200])
            g = m.groups()
            if mode == "nash":
                rec["max_int"] = int(g[1])
            else:
                rec["gap_min"], rec["chains"] = float(g[1]), int(g[2])
                if prog == "pairsq":
                    rec["max_int"] = int(g[3])
        logs.append(rec)
    assert sorted(rows) == list(range(NC)), "%s %s: %d of %d strategies" % (prog, mode, len(rows), NC)
    return rows, logs


def columns(res):
    """the per-strategy columns of one program's four passes"""
    W = np.array([[float(x) for x in res["self"][s]] for s in range(NC)])
    bp = np.array([int(res["rivP"][s][0]) for s in range(NC)])
    bm = np.array([int(res["rivM"][s][0]) for s in range(NC)])
    ne = res["nash"]
    self_ = np.array([float(ne[s][0]) for s in range(NC)])
    maxpay = np.array([float(ne[s][1]) for s in range(NC)])
    tieviol = np.array([int(ne[s][2]) for s in range(NC)])
    ntie = np.array([int(ne[s][3]) for s in range(NC)])
    nbeat = np.array([int(ne[s][4]) for s in range(NC)])
    # the decisions, exactly as compare.py reads them
    eff_cc = W[:, 0] == 1.0
    eff_alt = (W[:, 0] == 0) & (W[:, 3] == 0) & (W[:, 1] == 0.5)
    eff_line = W[:, 3] == 0
    nash = nbeat == -1
    return {
        "code": np.arange(NC),
        "w_CC": W[:, 0], "w_CD": W[:, 1], "w_DC": W[:, 2], "w_DD": W[:, 3],
        "eff_cc": eff_cc, "eff_alt": eff_alt, "eff_line": eff_line,
        "beat_p": bp, "riv_p": bp == -1, "beat_m": bm, "riv_m": bm == -1,
        "ne_self": self_, "ne_maxpay": maxpay, "ne_beat": nbeat, "nash": nash,
        "ne_ntie": ntie, "ne_tieviol": tieviol, "tie_ok": nash & (tieviol == 0),
    }


def header(prog, with_def):
    h = [
        "The census of the 65536 binary memory-two strategies in the limit eps -> 0, one row per strategy,",
        "from the program %s: the four passes self, rivP, rivM and nash at (u,v) = (-2,2)." % PROGS[prog],
        "Produced by census/reduce.py from the raw pass outputs; see data/census/README.md and census/README.md.",
        "Strategy code: bit j is 1 when the strategy cooperates at state j = 4*(most recent outcome) + (the outcome",
        "before), outcomes CC=0 CD=1 DC=2 DD=3 written own action first; ALLC = 65535, ALLD = 0. The genome of the",
        "paper is format(code, '016b')[::-1] (position j from the left = state j, 1 = C).",
        "columns:",
        "code        the strategy",
        "w_CC..w_DD  its limiting self-play frequencies of the four outcomes (%s)"
        % ("exact rationals, printed as the nearest double" if prog == "pairsq" else "double precision"),
        "eff_cc      1 if w_CC == 1: a mutual cooperator, efficient below the switch line u+v=1",
        "eff_alt     1 if w = (0, 1/2, 1/2, 0): an alternator, efficient above the switch line",
        "eff_line    1 if w_DD == 0: efficient on the switch line",
        "beat_p      rivalry for T>S: the lowest code tau with w_CD > w_DC (sigma outperformed), -1 if none",
        "riv_p       1 if beat_p == -1: a rival (competitive) wherever T > S, i.e. u - v < 1",
        "beat_m      rivalry for T<S: the lowest code tau with w_DC > w_CD, -1 if none",
        "riv_m       1 if beat_m == -1: a rival wherever T < S, i.e. u - v > 1",
    ]
    if with_def:
        h += ["def_p       1 if defensible for T>S (Murase-Baek: no negative cycle, Floyd-Warshall, census/defensible.py)",
              "def_m       1 if defensible for T<S"]
    h += [
        "at the donation game (u,v) = (-2,2), (R,S,T,P) = (1,-2,3,0), in the limit:",
        "ne_self     pi(sigma,sigma), sigma's self-play payoff",
        "ne_maxpay   the largest pi(tau,sigma) met; the scan over tau = 0..65535 stops once it exceeds Emax = 1,",
        "            so it is the maximum over all 65536 co-players whenever the scan ran to the end",
        "ne_beat     the lowest tau with pi(tau,sigma) > pi(sigma,sigma), -1 if none",
        "nash        1 if ne_beat == -1: stable, a Nash equilibrium at (-2,2) against all 65536 memory-two co-players",
        "ne_ntie     the number of tau met with pi(tau,sigma) = pi(sigma,sigma) (all of them when nash = 1)",
        "ne_tieviol  1 if one of these tau has pi(sigma,tau) < pi(sigma,sigma): the tie clause fails",
        "tie_ok      1 if nash = 1 and ne_tieviol = 0: stable with the tie clause (Akin) satisfied",
    ]
    return h


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    outdir = sys.argv[1]
    datadir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, os.pardir, "data", "census")
    os.makedirs(datadir, exist_ok=True)
    tabs, logs = {}, []
    for prog in PROGS:
        res = {}
        for mode in PASSES:
            res[mode], lg = read_pass(outdir, prog, mode)
            logs += [dict(program=prog, pass_=mode, **r) for r in lg]
        tabs[prog] = columns(res)
        print("%-6s read: %s" % (prog, ", ".join("%s %d stripes" % (m, sum(1 for l in logs if l["program"] == prog
                                                                          and l["pass_"] == m)) for m in PASSES)))
    dp, dm = defensible.defensible(1), defensible.defensible(-1)
    ex = dict(tabs["pairsq"])
    ex = {k: ex[k] for k in ("code", "w_CC", "w_CD", "w_DC", "w_DD", "eff_cc", "eff_alt", "eff_line",
                             "beat_p", "riv_p", "beat_m", "riv_m")}
    ex["def_p"], ex["def_m"] = dp, dm
    for k in ("ne_self", "ne_maxpay", "ne_beat", "nash", "ne_ntie", "ne_tieviol", "tie_ok"):
        ex[k] = tabs["pairsq"][k]
    write_table(os.path.join(datadir, "census.csv"), ex, header("pairsq", True))
    write_table(os.path.join(datadir, "census_double.csv"), tabs["pairs"], header("pairs", False))
    logs.sort(key=lambda r: (list(PROGS).index(r["program"]), PASSES.index(r["pass_"]), r["stripe"]))
    write_table(os.path.join(datadir, "passes.csv"), {
        "program": [r["program"] for r in logs], "pass": [r["pass_"] for r in logs],
        "stripe": [r["stripe"] for r in logs], "chains": [r["chains"] for r in logs],
        "gap_min": [r["gap_min"] for r in logs], "max_int": [r["max_int"] for r in logs]}, [
        "What the census programs reported on stderr, one row per program, pass and stripe (census/reduce.py).",
        "program   pairsq (exact rationals) or pairs (double precision)",
        "pass      self, rivP (T>S), rivM (T<S), nash (at (u,v) = (-2,2))",
        "stripe    the stripe: strategies stripe, stripe + nstripes, ... (nstripes = the number of rows per pass)",
        "chains    rivalry passes: the number of pair chains solved (a candidate's scan stops at its first beater); -1 = not reported",
        "gap_min   rivalry passes: the smallest nonzero |w_DC - w_CD| met in the stripe; nan = not reported",
        "max_int   pairsq only: the largest numerator or denominator met in the stripe; -1 = not reported",
        "The self pass and the double-precision nash pass print nothing on stderr."])
    note = ("bool masks over the 65536 binary M2 strategies, bit j = 1 means C at state j = 4*recent + before. "
            "effCC/effALT: exact eps->0 self-play all-CC / perfect alternation; rivP/rivM: never outperformed by any "
            "M2 co-player in the eps->0 limit for T>S / T<S; defP/defM: Murase-Baek defensibility (no negative cycle). "
            "Written by census/reduce.py from the exact census (pairsq.c) and census/defensible.py.")
    np.savez_compressed(os.path.join(datadir, "m2_masks.npz"), effCC=ex["eff_cc"], effALT=ex["eff_alt"],
                        defP=dp, defM=dm, rivP=ex["riv_p"], rivM=ex["riv_m"], note=np.array(note))
    for f in ("census.csv", "census_double.csv", "passes.csv", "m2_masks.npz"):
        print("wrote %-18s %9d bytes" % (f, os.path.getsize(os.path.join(datadir, f))))


if __name__ == "__main__":
    main()
