#!/usr/bin/env python3
"""compare.py -- the exact census (pairsq) against the double-precision one (pairs) and against the paper's counts.

    python3 compare.py <outdir> [nstripes]      (default nstripes 512)

For every pass and every strategy the decisions of the two programs are compared: the self-play support (which decides
efficiency), the first co-player that outperforms the strategy (rivalry, both signs of T-S; -1 = none, i.e. a rival), and
at (u,v) = (-2,2) the stability decision, the number of tying co-players and the tie-clause verdict.  Then the census counts are
recomputed from the exact outputs alone and printed next to the numbers quoted in the paper.
"""
import glob
import os
import sys

out = sys.argv[1]
nstr = int(sys.argv[2]) if len(sys.argv) > 2 else 512


def read(prog, mode):
    rows = {}
    files = sorted(glob.glob(os.path.join(out, "%s_%s_*.txt" % (prog, mode))))
    for f in files:
        for line in open(f):
            p = line.split()
            if p:
                rows[int(p[0])] = p[1:]
    return rows, len(files)


ok = True
res = {}
for mode in ("self", "rivP", "rivM", "nash"):
    q, nq = read("pairsq", mode)
    d, nd = read("pairs", mode)
    res[mode] = q
    missing = 65536 - len(q)
    diff = 0
    for s, a in q.items():
        b = d.get(s)
        if b is None:
            continue
        if mode == "self":
            wq = [float(x) for x in a]; wd = [float(x) for x in b]
            if any((x > 0) != (y > 0) for x, y in zip(wq, wd)) or max(abs(x - y) for x, y in zip(wq, wd)) > 1e-12:
                diff += 1
        elif mode in ("rivP", "rivM"):
            if a[0] != b[0]:
                diff += 1
        else:  # nash: self maxpay tieviol ntie firstbeat
            if a[2:] != b[2:] or abs(float(a[0]) - float(b[0])) > 1e-12:
                diff += 1
    print("%-5s exact rows %5d (files %3d), double rows %5d (files %3d), strategies missing %5d, decisions differing %d"
          % (mode, len(q), nq, len(d), nd, missing, diff))
    ok &= diff == 0

if all(len(res[m]) == 65536 for m in res):
    W = {s: [float(x) for x in a] for s, a in res["self"].items()}
    below = {s for s, w in W.items() if w[0] == 1.0}                               # permanent mutual cooperation
    above = {s for s, w in W.items() if w[0] == 0 and w[3] == 0 and w[1] == 0.5}   # perfect alternation
    line = {s for s, w in W.items() if w[3] == 0}                                  # no mutual defection
    rP = {s for s, a in res["rivP"].items() if a[0] == "-1"}
    rM = {s for s, a in res["rivM"].items() if a[0] == "-1"}
    rev = lambda s: int(format(s, "016b")[::-1], 2)
    mirror = lambda s: 65535 - rev(s)
    nash = {s for s, a in res["nash"].items() if a[4] == "-1"}
    tieok = {s for s, a in res["nash"].items() if a[2] == "0"}
    rows = [
        ("efficient below the switch line", len(below), 7639),
        ("efficient above (alternators)", len(above), 3072),
        ("efficient on the switch line", len(line), 14757),
        ("rivals for T>S", len(rP), 2640),
        ("rivals for T<S", len(rM), 2640),
        ("rivals for T<S = mirror(rivals for T>S)", int({mirror(s) for s in rP} == rM), 1),
        ("rivals either way", len(rP | rM), 5230),
        ("rivals both ways (fair)", len(rP & rM), 50),
        ("friendly rivals W (below, T>S)", len(below & rP), 8),
        ("friendly rivals S (below, T<S)", len(below & rM), 1519),
        ("friendly rivals E (above, T<S)", len(above & rM), 80),
        ("friendly rivals N (above, T>S)", len(above & rP), 80),
        ("friendly rivals somewhere", len((below & (rP | rM)) | (above & (rP | rM))), 1677),
        ("stable at (-2,2)", len(nash), 672),
        ("partners at (-2,2)", len(nash & below), 187),
        ("stable and rival (T>S) at (-2,2)", len(nash & rP), 493),
        ("efficient, stable and rival at (-2,2)", len(nash & rP & below), 8),
        ("partners satisfying the tie clause", len(nash & below & tieok), 8),
    ]
    print("\n%-44s %8s %8s" % ("census from the exact outputs", "exact", "paper"))
    for lab, a, b in rows:
        flag = "" if a == b else "   <-- differs"
        ok &= a == b
        print("%-44s %8d %8d%s" % (lab, a, b, flag))
    print("\nthe eight of W:", sorted(below & rP))
print("\nALL AGREE" if ok else "\nDISAGREEMENT FOUND")
