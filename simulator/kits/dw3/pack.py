#!/usr/bin/env python3
"""
Pack a dw3 run_<L>/ directory, ON CANNON, so that ~200 MB comes down instead of
~1.3 GB of h-files.

    python3 pack.py run packed        # -> packed/dw3_e{2,3,4}.{idx,bin}

*** NUMPY-FREE, deliberately. ***  There is no numpy on any Cannon python
module -- `python/3.10.13-fasrc01` and `intelpython/3.9.16-fasrc01` both lack
it -- which is why DonationWF's `sumcells.py` is pure stdlib too.  Checked,
not assumed.  Standard library only, so `python3 pack.py` works with whatever
python is on PATH.

Output per error rate, and the pair is read by ../../Opt/wfload.py:

  dw3_<e>.idx   text, one line per cell, in ascending gid:
                  gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total
                  ps1 .. ps16
                (u and v are games.dat's display columns, passed straight
                 through; the analysis side recomputes NE's exact coordinates
                 as u = cS/cR, v = cT/cR - 1 and CHECKS them against these --
                 see Opt/wfload.ne_uv.  cR = 1-c on the donation rows, so
                 u = cS is wrong there.)
  dw3_<e>.bin   65536 little-endian float32 per cell, cells in the same order
                as the .idx, each normalised to sum 1
  dw3_<e>.win   text, one line per (cell, replicate):
                  gid irun rank1code abundance selfpay ef
                This is the WF uncertainty instrument.  The .bin histogram is
                summed over the cell's 10 INDEPENDENT replicates, so its
                argmax can be a strategy that led in only a few of them; the
                per-replicate rank-1 is what says whether the cell has one
                answer or several.  See Opt/maps.audit.

A cell whose <isl> file holds fewer replicate lines than expected is packed
anyway, with `nrep` saying so, rather than dropped silently.

A TRUNCATED h-file, on the other hand, is refused.  sf.f writes the whole
65536-line histogram in one burst after the last replicate (sf.f:475-483)
whereas the summary file is flushed after every replicate (sf.f:424), so a
task killed in that window leaves a complete summary and a partial histogram --
and the resubmission guard, if it looked only at the summary, would skip it for
ever.  The check costs nothing and is exact: `# distinct ndist total ntotc` is
written BEFORE the counts, so it survives truncation, and both

    len(counts) == ndist        sum(counts) == total

hold for a complete h-file whatever the replicate count (ntotc is accumulated
per replicate at sf.f:421).  Without them a short histogram is renormalised by
its own partial sum into a plausible-looking but wrong abundance vector, and
nothing downstream can tell.
"""
import os, sys, glob
from array import array

NC = 65536
EPSN = {1: "e2", 2: "e3", 3: "e4"}


class Pending(Exception):
    """A task that has not written its histogram yet -- expected mid-run, and
       not the same thing as a cell that is broken."""


# The sampled draws per replicate are (itend/2) * N.  dw1 hardcoded 5e9
# (5e6 sampled generations x 1000 individuals).  For dw2 that is 5e7 x 100 --
# the SAME number, by coincidence, which is exactly why it must not stay
# hardcoded: the next run length or population size would pass a check that
# had stopped meaning anything.  itend is read from each h-file's own header;
# N is a compile-time parameter of sf.f and is not written there, so it is
# declared once, here, and must match `parameter (n=...)` in sf.f.
NPOP = 1000


def perrep(itend):
    """sampled (individual x generation) draws in one replicate"""
    return (itend // 2) * NPOP


def read_h(path):
    meta = {}
    code = []
    cnt = []
    with open(path) as f:
        for ln in f:
            if ln[0] == "#":
                t = ln.split()
                if ln.startswith("# cell:"):
                    meta["isl"] = int(t[3]); meta["gid"] = int(t[5])
                    meta["tag"] = t[6]
                elif ln.startswith("# game:"):
                    meta["cR"], meta["cS"], meta["cT"] = map(float, t[5:8])
                    meta["u"], meta["v"] = float(t[10]), float(t[11])
                    meta["emax"] = float(t[-1])
                elif ln.startswith("# run:"):
                    # '# run:  nper 10  itend 100000000  ie 3'
                    meta["nper"] = int(t[3]); meta["itend"] = int(t[5])
                elif ln.startswith("# distinct"):
                    meta["ndist"] = int(t[2]); meta["total"] = int(t[4])
                continue
            a, b = ln.split()
            code.append(int(a)); cnt.append(int(b))
    if "ndist" not in meta:
        # sf.f writes the h-file's headers when the task STARTS and the
        # `# distinct` line plus the counts only after the last replicate, so
        # this is the normal look of a task that is still running.  Distinguish
        # it from corruption: only a file that got as far as `# distinct` and
        # then stopped is a truncation.
        raise Pending("no histogram yet -- task still running, or it died "
                      "before writing one")
    if not meta.get("emax", 0.0) > 0.0:
        raise ValueError("'# game:' header has Emax = %r -- this h-file "
                         "predates the header fix, rerun it"
                         % meta.get("emax"))
    tot = sum(cnt)
    if len(cnt) != meta["ndist"] or tot != meta["total"]:
        raise ValueError("TRUNCATED histogram: %d count lines and sum %d, "
                         "but the header says ndist %d total %d"
                         % (len(cnt), tot, meta["ndist"], meta["total"]))
    if tot <= 0:
        raise ValueError("empty histogram")
    p = array("f", bytes(4 * NC))
    ftot = float(tot)
    for c, k in zip(code, cnt):
        p[c] = k / ftot
    return meta, p


def read_win(path):
    """the w-file: the rank-1 line of each replicate.
       columns: isl eps gid irun rank code abund selfpay selfef w0..w3 bits"""
    out = []
    for ln in open(path):
        if ln[0] == "#":
            continue
        f = ln.split()
        if int(f[4]) != 1:          # rank
            continue
        out.append((int(f[3]), int(f[5]), float(f[6]), float(f[7])))
    return out


def read_summary(path):
    rows = [[float(x) for x in l.split()] for l in open(path) if l.strip()]
    if not rows:
        raise ValueError("empty summary")
    n = len(rows)
    ie = int(rows[0][1])
    pay = sum(r[5] for r in rows) / n
    efs = [r[6] for r in rows]
    ef = sum(efs) / n
    if n > 1:
        sd = (sum((e - ef) ** 2 for e in efs) / (n - 1)) ** 0.5
    else:
        sd = 0.0
    ps = [sum(r[7 + k] for r in rows) / n for k in range(16)]
    return ie, n, pay, ef, sd, ps


def main(rundir, out):
    os.makedirs(out, exist_ok=True)
    hs = sorted(glob.glob(os.path.join(rundir, "h[0-9]*")),
                key=lambda p: int(os.path.basename(p)[1:]))
    print("%d h-files in %s" % (len(hs), rundir))
    by = {}
    dropped = []
    pending = []
    nowin = []
    mismatch = []
    for hp in hs:
        isl = int(os.path.basename(hp)[1:])
        sp = os.path.join(rundir, str(isl))
        if not os.path.exists(sp):
            print("  task %d: h-file but no summary, DROPPED" % isl)
            dropped.append(isl); continue
        try:
            meta, p = read_h(hp)
            ie, nrep, pay, ef, sd, ps = read_summary(sp)
        except Pending:
            pending.append(isl); continue
        except Exception as e:
            print("  task %d: %s -- DROPPED" % (isl, e))
            dropped.append(isl); continue
        # the two files must agree about how many replicates ran
        if meta.get("itend") is None:
            raise ValueError("isl %s: h-file header has no itend" % isl)
        if meta["total"] != nrep * perrep(meta["itend"]):
            print("  task %d: summary has %d replicates (%d expected counts) "
                  "but the histogram totals %d"
                  % (isl, nrep, nrep * perrep(meta["itend"]), meta["total"]))
            mismatch.append(isl)
        wp = os.path.join(rundir, "w%d" % isl)
        win = read_win(wp) if os.path.exists(wp) else []
        if not win:
            nowin.append(isl)
        by.setdefault(ie, []).append((meta["gid"], meta, p, isl, nrep,
                                      pay, ef, sd, ps, win))

    for ie in sorted(by):
        R = sorted(by[ie], key=lambda r: r[0])
        nm = EPSN.get(ie, "ie%d" % ie)
        fb = open(os.path.join(out, "dw3_%s.bin" % nm), "wb")
        fi = open(os.path.join(out, "dw3_%s.idx" % nm), "w")
        fw = open(os.path.join(out, "dw3_%s.win" % nm), "w")
        fw.write("# gid irun rank1 abund selfpay\n")
        fi.write("# gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep "
                 "total ps1..ps16\n")
        short = []
        for gid, meta, p, isl, nrep, pay, ef, sd, ps, win in R:
            for irun, code, ab, sp in win:
                fw.write("%6d %4d %6d %12.8f %14.7f\n"
                         % (gid, irun, code, ab, sp))
            p.tofile(fb)
            fi.write("%6d %6d %-24s %20.12e %20.12e %20.12e %20.12e %20.12e "
                     "%20.12e %18.10e %18.10e %14.6e %7d %4d %16d %s\n"
                     % (gid, isl, meta["tag"], meta["u"], meta["v"],
                        meta["cR"], meta["cS"], meta["cT"], meta["emax"],
                        pay, ef, sd, meta.get("ndist", -1), nrep,
                        meta.get("total", -1),
                        " ".join("%14.10f" % x for x in ps)))
            if nrep < 10:
                short.append(isl)
        fb.close(); fi.close(); fw.close()
        print("  ie=%d -> dw3_%s.{idx,bin,win}  %4d cells%s"
              % (ie, nm, len(R), "   SHORT: %s" % short if short else ""))

    # loud, because a dropped cell is otherwise one line among several hundred
    bad = 0
    if pending:
        print("   (%d task(s) have not written a histogram yet -- still "
              "running: %s%s)"
              % (len(pending), pending[:12],
                 " ..." if len(pending) > 12 else ""))
    if dropped:
        print("!! %d cell(s) DROPPED and absent from the products: %s"
              % (len(dropped), dropped)); bad += 1
    if mismatch:
        print("!! %d cell(s) whose summary and histogram disagree: %s"
              % (len(mismatch), mismatch)); bad += 1
    if nowin:
        print("!! %d cell(s) with no rank-1 lines, so no leader audit: %s"
              % (len(nowin), nowin)); bad += 1
    if not bad:
        print("clean: every h-file packed, every histogram whole, "
              "every cell has its per-replicate rank-1 lines")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "run",
                  sys.argv[2] if len(sys.argv) > 2 else "packed"))
