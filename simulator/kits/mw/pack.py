#!/usr/bin/env python3
"""
Pack one mw run directory into a single text product, on Cannon, with no numpy.

    python3 pack.py run1 packed          -> packed/mw1_e4.tsv  and  packed/mw1_e4.rep.tsv
    python3 pack.py run2 packed          -> packed/mw2_e4.tsv  and  packed/mw2_e4.rep.tsv
    python3 pack.py run1 packed --dev    the same for a SHORT local build: nper and itend are
                                         then taken from each h-file's own header instead of
                                         being required to be the production 10 / 1e7

The histogram of a memory-one cell is 16 numbers, so the whole campaign is a
512-line table and there is no case for dw1's .idx/.bin/.win triple: the
product is plain text, which md5s and diffs and needs no reader.

    mw<W>_e4.tsv      one line per cell:  ipt gid tag u v emax pay ef ntot c0..c15
                      pay / ef are the means over the 10 replicates and
                      c0..c15 the summed second-half occupancy counts, so
                      c_k / ntot is the time-averaged share of strategy k.
    mw<W>_e4.rep.tsv  one line per replicate: ipt irep pay ef ps1..ps4
                      (the spread over replicates, for the stability check)

WHAT IS CHECKED, CELL BY CELL, rather than assumed:
  * the h-file's own '# cell:' line names gid and tag; both must equal
    games.dat row (isl-1)/3+1.  That is a direct test of the task decode --
    the one place where an off-by-one would silently put every number on the
    wrong game.
  * ie must be 3, i.e. eps = 1e-4.
  * the count lines must number '# distinct' and their codes must be 0..15.
  * the counts must sum to the '# total' on that line, and that total must
    equal nper * (itend/2) * N -- the guard against a histogram written in one
    burst and truncated by a kill (dw1's lesson; it renormalises into a
    plausible-looking but wrong abundance vector).
  * the summary file must carry 10 replicate lines, all naming this gid.
"""
import os
import sys


def games(path):
    """row (1-based) -> (gid, cR, cS, cT, u, v, tag)"""
    out = {}
    n = 0
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        f = s.split()
        n += 1
        out[n] = (int(f[0]), float(f[2]), float(f[3]), float(f[4]), float(f[5]), float(f[6]), f[7])
    return out


def main(run, outdir):
    W = os.path.basename(run.rstrip("/"))
    assert W.startswith("run"), "the run directory must be named run<label>, not %r" % run
    W = W[3:]
    # N, itend, beta, u -- ALL FOUR, because a run's identity is all four and a
    # header built from a `W == "1"` ternary labelled run1s as beta = 3, u = 1e-4
    PAR = {"1": (1000, 10 ** 7, 100.0, 1e-2), "2": (100, 10 ** 8, 3.0, 1e-4),     # deliverables
           "1s": (1000, 10 ** 5, 100.0, 1e-2), "2s": (100, 10 ** 6, 3.0, 1e-4)}   # controls
    assert W in PAR, "no parameters known for run%s (have %s)" % (W, ", ".join(sorted(PAR)))
    N, ITEND, BETA, UMUT = PAR[W]
    NPER = 10
    dev = "--dev" in sys.argv          # a short local build: take itend/nper from each h-file
    G = games(os.path.join(run, "games.dat"))
    assert len(G) == 512, "games.dat in %s has %d rows, expected 512" % (run, len(G))

    cells, reps, bad = [], [], []
    seenrun = (NPER, ITEND)
    for ipt in range(512):
        isl = 3 * (ipt + 1)
        row = ipt + 1
        gid, cR, cS, cT, u, v, tag = G[row]
        hp, sp = os.path.join(run, "h%d" % isl), os.path.join(run, "%d" % isl)
        if not (os.path.exists(hp) and os.path.exists(sp)):
            bad.append("%d: missing product" % isl)
            continue
        cnt, tot_hdr, ndist, seen = [0] * 16, None, None, []
        ghdr, nper, itend, expect = None, NPER, ITEND, None
        for line in open(hp):
            if line.startswith("# cell:"):
                f = line.split()
                # '# cell: isl <isl>  gid <gid> <tag>  eps <e>  umut <u>  beta <b>'
                ghdr = (int(f[5]), f[6], float(f[8]), float(f[10]), float(f[12]))
            elif line.startswith("# run:"):
                f = line.split()
                assert int(f[-1]) == 3, "%s: ie is %s, not 3 (eps = 1e-4)" % (hp, f[-1])
                nper, itend = int(f[3]), int(f[5])
                if not dev:
                    assert (nper, itend) == (NPER, ITEND), \
                        "%s: nper %d itend %d, this run is %d / %d" % (hp, nper, itend, NPER, ITEND)
                expect = nper * (itend // 2) * N
            elif line.startswith("# distinct"):
                f = line.split()
                ndist, tot_hdr = int(f[2]), int(f[4])
            elif not line.startswith("#"):
                f = line.split()
                k, c = int(f[0]), int(f[1])
                assert 0 <= k < 16, "%s: code %d out of range" % (hp, k)
                cnt[k] += c
                seen.append(k)
        if ghdr is not None:
            # the h-file carries the parameters it ran with; they must be this
            # run's, so a mislabelled pack is impossible rather than unlikely
            if abs(ghdr[3] - UMUT) > 1e-12 * max(1.0, UMUT) or abs(ghdr[4] - BETA) > 1e-9:
                bad.append("%d: ran with u = %g, beta = %g; run%s is u = %g, beta = %g"
                           % (isl, ghdr[3], ghdr[4], W, UMUT, BETA))
        if ghdr is None or ndist is None:
            bad.append("%d: h-file has no header" % isl)
            continue
        if len(seen) != ndist:
            bad.append("%d: %d count lines, header says %d -- TRUNCATED" % (isl, len(seen), ndist))
            continue
        if sum(cnt) != tot_hdr:
            bad.append("%d: counts sum to %d, header total %d" % (isl, sum(cnt), tot_hdr))
            continue
        if tot_hdr != expect:
            bad.append("%d: total %d, expected nper*(itend/2)*N = %d" % (isl, tot_hdr, expect))
            continue
        assert ghdr[0] == gid and ghdr[1] == tag, \
            "%s: h-file says gid %d %s, games.dat row %d says gid %d %s -- TASK DECODE" \
            % (hp, ghdr[0], ghdr[1], row, gid, tag)
        assert abs(ghdr[2] - 1e-4) < 1e-12, "%s: eps %g" % (hp, ghdr[2])
        rl = [l.split() for l in open(sp) if l.strip()]
        if len(rl) != nper:
            bad.append("%d: %d replicate lines, expected %d" % (isl, len(rl), nper))
            continue
        for irep, f in enumerate(rl, 1):
            assert int(f[0]) == gid, "%s: replicate %d names gid %s" % (sp, irep, f[0])
            reps.append((ipt, irep, float(f[5]), float(f[6])) + tuple(float(x) for x in f[7:11]))
        emax = max(cR, 0.5 * (cS + cT))
        pay = sum(float(f[5]) for f in rl) / nper
        ef = sum(float(f[6]) for f in rl) / nper
        cells.append((ipt, gid, tag, u, v, emax, pay, ef, tot_hdr, cnt))
        seenrun = (nper, itend)

    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "mw%s_e4.tsv" % W)
    with open(p, "w") as fh:
        fh.write("# DiskM1WF mw%s: the WF process over the 16 binary memory-one strategies,\n" % W)
        fh.write("# N = %d, beta = %s, u = %s, eps = 1e-4, itend = %d, %d replicates,\n"
                 % (N, ("%g" % BETA), ("%.0e" % UMUT).replace("e-0", "e-"),
                    seenrun[1], seenrun[0]))
        fh.write("# at the 512 Voronoi cells of BinM2Ev ca6's sunflower on the k = 4 disk.\n")
        fh.write("# c_k / ntot is the time-averaged share of strategy k (bit j = 1 means C\n")
        fh.write("# after outcome j, j = 0..3 for CC, CD, DC, DD; ALLD 0, Grim 1, TFT 5, WSLS 9, ALLC 15).\n")
        fh.write("# ipt\tgid\ttag\tu\tv\temax\tpay\tef\tntot\t" + "\t".join("c%d" % k for k in range(16)) + "\n")
        for ipt, gid, tag, u, v, emax, pay, ef, tot, cnt in cells:
            fh.write("%d\t%d\t%s\t%.12g\t%.12g\t%.12g\t%.10g\t%.10g\t%d\t%s\n"
                     % (ipt, gid, tag, u, v, emax, pay, ef, tot, "\t".join(str(c) for c in cnt)))
    q = os.path.join(outdir, "mw%s_e4.rep.tsv" % W)
    with open(q, "w") as fh:
        fh.write("# ipt\tirep\tpay\tef\tps1\tps2\tps3\tps4    (one line per replicate)\n")
        for r in reps:
            fh.write("%d\t%d\t%.10g\t%.10g\t%.8g\t%.8g\t%.8g\t%.8g\n" % r)
    print("%s: %d cells of 512, %d replicate lines" % (p, len(cells), len(reps)))
    if bad:
        print("INCOMPLETE OR INCONSISTENT (%d):" % len(bad))
        for b in bad[:40]:
            print("   ", b)
        sys.exit(1)
    print("all 512 cells complete and consistent")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0] if a else "run1", a[1] if len(a) > 1 else "packed")
