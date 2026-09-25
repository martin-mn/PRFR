#!/usr/bin/env python3
"""
Pack an lm run_<g>/ directory (kit lm, from f1's pack.py; packs lm_<g>_<e>.*), ON CANNON (stdlib only: no numpy on the login node's python 3.6), so that the packs
come down instead of the run directory.

    python3 pack.py run_g0 packed [../atoms512.bin]

Per error rate <e> (EPSN below), read by DiskM2WF/Opt/wfload.py exactly like dw1..dw4's packs:
  lm_<g>_<e>.idx   one line per cell, ascending gid:  gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total ps1..ps16
  lm_<g>_<e>.bin   65536 little-endian float32 per cell, same order, normalised to sum 1
  lm_<g>_<e>.win   one line per (cell, replicate): gid irun rank1code abundance selfpay ef
and NEW here, from the r-files (the 65536 int64 counts of each replicate, unit 8 of sf.f):
  lm_<g>_<e>.rep   one line per (cell, replicate): gid irun ef s000 s100 s010 s001 s110 s011 s111
                 the share of that replicate's sampled population in each atom, computed with atoms512.bin (one byte per
                 strategy per sunflower cell, code = 4*efficient + 2*nash + competitive, cells in ipt order; built by
                 mkatoms.py from the exact eps -> 0 masks).  s101 is asserted zero.
A truncated h-file or a short r-file is refused, not renormalised.
"""
import os, sys, glob
from array import array
from itertools import compress

NC = 65536
EPSN = {1: 'e2', 2: 'e3', 3: 'e4'}
NPOP = 1000           # must match `parameter (n=...)` in sf.f
# lm: packs are named lm_<g>_<e>.*, <g> taken from the run directory run_<g>
PFX = "lm"


class Pending(Exception):
    pass


def perrep(itend):
    return (itend // 2) * NPOP


def read_h(path):
    meta = {}; code = []; cnt = []
    with open(path) as f:
        for ln in f:
            if ln[0] == "#":
                t = ln.split()
                if ln.startswith("# cell:"):
                    meta["isl"] = int(t[3]); meta["gid"] = int(t[5]); meta["tag"] = t[6]
                elif ln.startswith("# game:"):
                    meta["cR"], meta["cS"], meta["cT"] = map(float, t[5:8])
                    meta["u"], meta["v"] = float(t[10]), float(t[11]); meta["emax"] = float(t[-1])
                elif ln.startswith("# run:"):
                    meta["nper"] = int(t[3]); meta["itend"] = int(t[5])
                elif ln.startswith("# distinct"):
                    meta["ndist"] = int(t[2]); meta["total"] = int(t[4])
                continue
            a, b = ln.split(); code.append(int(a)); cnt.append(int(b))
    if "ndist" not in meta:
        raise Pending("no histogram yet")
    if not meta.get("emax", 0.0) > 0.0:
        raise ValueError("Emax header missing")
    tot = sum(cnt)
    if len(cnt) != meta["ndist"] or tot != meta["total"]:
        raise ValueError("TRUNCATED histogram: %d lines sum %d, header says %d %d" % (len(cnt), tot, meta["ndist"], meta["total"]))
    p = array("f", bytes(4 * NC)); ftot = float(tot)
    for c, k in zip(code, cnt):
        p[c] = k / ftot
    return meta, p


def read_win(path):
    out = []
    for ln in open(path):
        if ln[0] == "#":
            continue
        f = ln.split()
        if int(f[4]) != 1:
            continue
        out.append((int(f[3]), int(f[5]), float(f[6]), float(f[7])))
    return out


def read_summary(path):
    rows = [[float(x) for x in l.split()] for l in open(path) if l.strip()]
    if not rows:
        raise ValueError("empty summary")
    n = len(rows); ie = int(rows[0][1])
    pay = sum(r[5] for r in rows) / n
    efs = [r[6] for r in rows]; ef = sum(efs) / n
    sd = (sum((e - ef) ** 2 for e in efs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    ps = [sum(r[7 + k] for r in rows) / n for k in range(16)]
    return ie, n, pay, ef, sd, ps, efs


def read_r(path, nrep, itend):
    """the nrep replicate count blocks; returns a list of array('q')"""
    a = array("q"); assert a.itemsize == 8
    size = os.path.getsize(path)
    if size != nrep * 8 * NC:
        raise ValueError("r-file has %d bytes, expected %d for %d replicates" % (size, nrep * 8 * NC, nrep))
    with open(path, "rb") as f:
        a.fromfile(f, nrep * NC)
    if sys.byteorder != "little":
        a.byteswap()
    out = []
    for r in range(nrep):
        h = a[r * NC:(r + 1) * NC]
        if sum(h) != perrep(itend):
            raise ValueError("replicate %d counts sum to %d, expected %d" % (r + 1, sum(h), perrep(itend)))
        out.append(h)
    return out


def atom_shares(h, sel, tot):
    return [sum(compress(h, sel[a])) / float(tot) for a in range(8)]


def main(rundir, out, atoms):
    global PFX
    import re
    b = os.path.basename(os.path.abspath(rundir))
    mg = re.fullmatch(r"run_(g0|g01|g05|g1)", b)
    if not mg:
        print("!! run directory must be run_<g>, g in g0 g01 g05 g1: %s" % b); return 1
    PFX = "lm_" + mg.group(1)
    os.makedirs(out, exist_ok=True)
    A = open(atoms, "rb").read()
    if len(A) != 512 * NC:
        raise ValueError("%s has %d bytes, expected 512 x 65536" % (atoms, len(A)))
    hs = sorted(glob.glob(os.path.join(rundir, "h[0-9]*")), key=lambda p: int(os.path.basename(p)[1:]))
    print("%d h-files in %s" % (len(hs), rundir))
    if not hs:
        print("!! no h-files in %s" % rundir); return 1
    by = {}; dropped = []; pending = []; nowin = []; mismatch = []
    for hp in hs:
        isl = int(os.path.basename(hp)[1:])
        sp = os.path.join(rundir, str(isl)); rp = os.path.join(rundir, "r%d" % isl)
        if not os.path.exists(sp):
            print("  task %d: h-file but no summary, DROPPED" % isl); dropped.append(isl); continue
        try:
            meta, p = read_h(hp)
            ie, nrep, pay, ef, sd, ps, efs = read_summary(sp)
            if meta["total"] != nrep * perrep(meta["itend"]):
                mismatch.append(isl)
            reps = read_r(rp, nrep, meta["itend"])
        except Pending:
            pending.append(isl); continue
        except Exception as e:
            print("  task %d: %s -- DROPPED" % (isl, e)); dropped.append(isl); continue
        ipt = int(meta["tag"].split("_")[1][1:])
        if meta["gid"] != 2000 + ipt:
            raise ValueError("isl %d: gid %d is not 2000 + ipt %d" % (isl, meta["gid"], ipt))
        ac = A[ipt * NC:(ipt + 1) * NC]
        sel = [[x == a for x in ac] for a in range(8)]
        shares = [atom_shares(h, sel, perrep(meta["itend"])) for h in reps]
        for s in shares:
            if s[5] != 0.0:
                raise ValueError("isl %d: atom 101 has mass %g" % (isl, s[5]))
        wp = os.path.join(rundir, "w%d" % isl)
        win = read_win(wp) if os.path.exists(wp) else []
        if not win:
            nowin.append(isl)
        by.setdefault(ie, []).append((meta["gid"], meta, p, isl, nrep, pay, ef, sd, ps, win, efs, shares))
    for ie in sorted(by):
        R = sorted(by[ie], key=lambda r: r[0]); nm = EPSN.get(ie, "ie%d" % ie)
        fb = open(os.path.join(out, PFX + "_%s.bin" % nm), "wb")
        fi = open(os.path.join(out, PFX + "_%s.idx" % nm), "w")
        fw = open(os.path.join(out, PFX + "_%s.win" % nm), "w")
        fr = open(os.path.join(out, PFX + "_%s.rep" % nm), "w")
        fw.write("# gid irun rank1 abund selfpay\n")
        fi.write("# gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total ps1..ps16\n")
        fr.write("# gid irun ef s000 s100 s010 s001 s110 s011 s111   (atom shares of the replicate, exact eps->0 atoms)\n")
        short = []
        for gid, meta, p, isl, nrep, pay, ef, sd, ps, win, efs, shares in R:
            for irun, code, ab, spay in win:
                fw.write("%6d %4d %6d %12.8f %14.7f\n" % (gid, irun, code, ab, spay))
            for r in range(nrep):
                s = shares[r]
                fr.write("%6d %4d %12.8f %s\n" % (gid, r + 1, efs[r], " ".join("%12.8f" % s[a] for a in (0, 4, 2, 1, 6, 3, 7))))
            p.tofile(fb)
            fi.write("%6d %6d %-24s %20.12e %20.12e %20.12e %20.12e %20.12e %20.12e %18.10e %18.10e %14.6e %7d %4d %16d %s\n"
                     % (gid, isl, meta["tag"], meta["u"], meta["v"], meta["cR"], meta["cS"], meta["cT"], meta["emax"],
                        pay, ef, sd, meta.get("ndist", -1), nrep, meta.get("total", -1), " ".join("%14.10f" % x for x in ps)))
            if nrep < 10:
                short.append(isl)
        fb.close(); fi.close(); fw.close(); fr.close()
        print("  ie=%d -> %s_%s.{idx,bin,win,rep}  %4d cells%s" % (ie, PFX, nm, len(R), "   SHORT: %s" % short if short else ""))
    bad = 0
    if pending:
        print("   (%d task(s) have not written a histogram yet: %s%s)" % (len(pending), pending[:12], " ..." if len(pending) > 12 else ""))
    if dropped:
        print("!! %d cell(s) DROPPED: %s" % (len(dropped), dropped)); bad += 1
    if mismatch:
        print("!! %d cell(s) whose summary and histogram disagree: %s" % (len(mismatch), mismatch)); bad += 1
    if nowin:
        print("!! %d cell(s) with no rank-1 lines: %s" % (len(nowin), nowin)); bad += 1
    if not bad:
        print("clean: every h-file packed, every histogram whole, every r-file whole, every cell has its rank-1 lines")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "run_g0",
                  sys.argv[2] if len(sys.argv) > 2 else "packed",
                  sys.argv[3] if len(sys.argv) > 3 else os.path.join("..", "atoms512.bin")))
