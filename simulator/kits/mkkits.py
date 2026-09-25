#!/usr/bin/env python3
"""
mkkits.py -- generate the six Wright-Fisher kits of 2026-09-22: two error-rate series and the
four missing corners of the {N} x {beta} x {mu} cube, all on the 512 sunflower games, from the dw3 kit as the template.

    python3 mkkits.py            -> eh/ el/ c1/ c2/ c3/ c4/   (each a complete kit: source, scripts, README)

Every kit's sf.f is dw3/sf.f with an asserted list of substitutions (each must apply exactly once), so `diff dw3/sf.f
<kit>/sf.f` is the audit.  The parameter lines changed are the header comment, n, iseedb, epsv (eps-series kits only),
uval and bval; itend stays the 1e7 default that compile.sh patches.  ONE functional addition, the same in all six: after
each replicate the 65536 int64 counts of that replicate are written to a stream file r<task> (unit 8, 524288 bytes per
replicate), so that the per-replicate atom shares -- the replicate-level uncertainty -- can be computed
downstream.  Nothing in the generation loop or the random stream is touched, and mkkits.py's test mode proves it:

    python3 mkkits.py test       -> builds dw3's own parameters with and without the addition (gfortran, itend = 1e5),
                                    runs one task of each and compares the summary, winner and histogram files byte for byte.

  kit   N     beta   mu     itend   eps            seeds            arrays
  eh    1000  100    1e-2   1e7     1e-5, 1e-3     20000000 + ...   e5: 1366-2899:3   e3: 1367-2900:3
  el    100   3      1e-4   1e8     1e-5, 1e-3     21000000 + ...   e5, e3 likewise
  c1    100   100    1e-2   1e7     1e-4           22000000 + ...   e4: 1368-2901:3
  c2    100   3      1e-2   1e7     1e-4           23000000 + ...   e4
  c3    100   100    1e-4   1e8     1e-4           24000000 + ...   e4
  c4    1000  3      1e-4   1e7     1e-4           25000000 + ...   e4

The task decode is dw1's: ie = mod(isl-1,3)+1, ig = (isl-1)/3+1; the sunflower is games 456-967 (gid 2000+ipt, ipt =
ig-456).  In the eps-series kits epsv is (1e-5, 1e-3, 1e-4), so ie = 1 is eps = 1e-5 and ie = 2 is eps = 1e-3; the ie = 3
stride is Figure 4's own run (dw1, dw2) and is not submitted.  Seeds iseedb + (isl-1)*10 + irep, bases 20-25 million,
disjoint from dw1 (8e6), dw2 (9e6), dw3 (1e7), dw4 (1.1e7), the memory-one kits (1e7-1.3e7) and PRDiscounting (1.2e7).
"""
import os, re, shutil, subprocess, sys, filecmp

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "dw3")

KITS = [
    # name, N, beta (Fortran literal), u (Fortran literal), run length, seed base, eps-series?, one-line purpose
    ("eh", 1000, "100.d+00", "1.d-02", "1e7", 20000000, True,
     "error-rate series at N = 1000, beta = 100, u = 1e-2 (Figure 4's large population), eps = 1e-5 and 1e-3"),
    ("el", 100, "3.d+00", "1.d-04", "1e8", 21000000, True,
     "error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3"),
    ("c1", 100, "100.d+00", "1.d-02", "1e7", 22000000, False,
     "cube corner N = 100, beta = 100, u = 1e-2 (the small population with the large one's selection and mutation), eps = 1e-4"),
    ("c2", 100, "3.d+00", "1.d-02", "1e7", 23000000, False,
     "cube corner N = 100, beta = 3, u = 1e-2 (the small population with the large one's mutation rate), eps = 1e-4"),
    ("c3", 100, "100.d+00", "1.d-04", "1e8", 24000000, False,
     "cube corner N = 100, beta = 100, u = 1e-4 (the small population with the large one's selection strength), eps = 1e-4"),
    ("c4", 1000, "3.d+00", "1.d-04", "1e7", 25000000, False,
     "cube corner N = 1000, beta = 3, u = 1e-4 (the large population with the small one's selection and mutation), eps = 1e-4"),
    # the seeded re-runs of Figure 4's two runs: dw1's and dw2's parameters AND seed bases, so that
    # a bit-identical regeneration carries the per-replicate r-file that the originals lack, and tests reproducibility
    ("f1", 1000, "100.d+00", "1.d-02", "1e7", 8000000, False,
     "seeded re-run of dw1, Figure 4's large-population run (N = 1000, beta = 100, u = 1e-2, seeds 8000000+), eps = 1e-4"),
    ("f2", 100, "3.d+00", "1.d-04", "1e8", 9000000, False,
     "seeded re-run of dw2, Figure 4's small-population run (N = 100, beta = 3, u = 1e-4, seeds 9000000+), eps = 1e-4"),
]
PROBE_E4 = [1368, 2892, 2895, 2898, 2901, 1902, 2436, 2664]      # dw3's probe cells at ie = 3
WALL = {("1e7", 1000): 240, ("1e8", 100): 240, ("1e7", 100): 60}  # minutes; 65, 67 and ~7 min measured or expected
COPY = ["payf2.f", "payf3.f", "mt.f", "mtb.f", "games.dat"]


def subst(text, pairs, where):
    for old, new in pairs:
        c = text.count(old)
        assert c == 1, "%s: anchor occurs %d times: %r" % (where, c, old[:70])
        text = text.replace(old, new)
    return text


def fortran_u(lit):
    return {"1.d-02": "1e-2", "1.d-04": "1e-4"}[lit]


def fortran_b(lit):
    return {"100.d+00": "100", "3.d+00": "3"}[lit]


def make_sf(name, n, beta, u, seed, eps_series, addition=True, itv=None):
    t = open(os.path.join(TPL, "sf.f")).read()
    pairs = [
        ("*     dw3: N = 1000, m = 1, beta = 100, u = 1e-4, itend = 1e7 (default; compile.sh sets it)",
         "*     %s: N = %d, m = 1, beta = %s, u = %s, itend = 1e7 (default; compile.sh sets it)"
         % (name, n, fortran_b(beta), fortran_u(u))),
        ("      parameter (n=1000,m=1)", "      parameter (n=%d,m=1)" % n),
        ("      parameter (iseedb=10000000)", "      parameter (iseedb=%d)" % seed),
        ("      data uval /1.d-04/", "      data uval /%s/" % u),
        ("      data bval /100.d+00/", "      data bval /%s/" % beta),
    ]
    if eps_series:
        pairs += [
            ("*     eps = 1e-2, 1e-3, 1e-4                 (3)", "*     eps = 1e-5, 1e-3, 1e-4                 (3)"),
            ("      data epsv /1.d-02,1.d-03,1.d-04/", "      data epsv /1.d-05,1.d-03,1.d-04/"),
        ]
    if addition:
        pairs += [
            ("*         unit 7 -> h<task>  : the cell header, then every strategy with a\n"
             "*                              non-zero summed count:  code  count\n",
             "*         unit 7 -> h<task>  : the cell header, then every strategy with a\n"
             "*                              non-zero summed count:  code  count\n"
             "*         unit 8 -> r<task>  : after every replicate its 65536 int64 counts,\n"
             "*                              unformatted stream, 524288 bytes per replicate\n"),
            ("      character*12 slurm,wfile,hfile\n", "      character*12 slurm,wfile,hfile,rfile\n"),
            ("      hfile='h'//slurm\n", "      hfile='h'//slurm\n      rfile='r'//slurm\n"),
            ("      open (unit=7,file=hfile)\n",
             "      open (unit=7,file=hfile)\n"
             "      open (unit=8,file=rfile,access='stream',form='unformatted',\n"
             "     &      status='replace')\n"),
            ("      call flush(3)\n", "      call flush(3)\n      write (8) hist\n      call flush(8)\n"),
            ("      call flush(7)\n\n      stop\n", "      call flush(7)\n      close (8)\n\n      stop\n"),
        ]
    if itv is not None:
        pairs.append(("      data itv  /10000000/", "      data itv  /%d/" % itv))
    return subst(t, pairs, name + "/sf.f")


def arrays(eps_series):
    """[(tag, ie, offset)] -- the arrays a kit submits"""
    return [("e5", 1, -2), ("e3", 2, -1)] if eps_series else [("e4", 3, 0)]


def slurm(name, purpose, tag, kind, L, n, idx_spec, wall):
    guard = r"""module load intel/25.2.1-fasrc01
cd run_%(L)s || { echo "run_%(L)s/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run_%(L)s/games.dat missing -- use submit.sh"; exit 1; }
# idempotent: a task counts as done only with 10 replicate lines, a complete histogram AND a full r-file
isl=$SLURM_ARRAY_TASK_ID
lines=0
[ -f "$isl" ] && lines=$(wc -l < "$isl")
hdone=0
if [ -f "h$isl" ]; then
  nd=$(awk '/^# distinct/{print $3; exit}' "h$isl")
  nc=$(grep -vc '^#' "h$isl") || nc=0
  [ -n "$nd" ] && [ "$nc" -eq "$nd" ] && hdone=1
fi
rdone=0
[ -f "r$isl" ] && [ "$(stat -c %%s "r$isl")" -eq 5242880 ] && rdone=1
if [ "$lines" -ge 10 ] && [ "$hdone" -eq 1 ] && [ "$rdone" -eq 1 ]; then
  echo "task $isl already complete (10 replicate lines, $nd-state histogram, 10 replicate count blocks), skipping"
  exit 0
fi
../sf_%(L)s.x $isl
""" % {"L": L}
    return """#! /bin/bash
# %(name)s / %(kind)s %(tag)s at itend = %(L)s: the WF process with pairwise comparison, %(purpose)s,
# on the 512-point Fermat sunflower of Figures 4 and 5 of CL1/PartnersRivals (dw1/dw2's games.dat and task decode).
# Task decode: ie = mod(isl-1,3)+1; ig = (isl-1)/3+1; the sunflower is games 456-967 (gid 2000+ipt, ipt = ig-456).
# This array is the ie = %(ie)d stride, tag %(tag)s.
#SBATCH -p shared
#SBATCH -J PartnersRivals.%(name)s%(short)s
#SBATCH --comment=PartnersRivals
#SBATCH -t %(wall)d
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_%(kind)s%(tag)s_%%a.txt
#SBATCH -e log/e_%(kind)s%(tag)s_%%a.txt
#SBATCH --array=%(spec)s

""" % {"name": name, "kind": kind, "tag": tag, "L": L, "purpose": purpose, "ie": {"e5": 1, "e3": 2, "e4": 3}[tag],
       "short": ("p" if kind == "probe" else "v") + tag[1], "wall": wall, "spec": idx_spec} + guard


def submit_sh(name, purpose, L, eps_series):
    cases = []
    for tag, ie, off in arrays(eps_series):
        probe = " ".join(str(i + off) for i in PROBE_E4)
        cases.append('  probe_%s) SCRIPT=probe_%s.slurm; TAG=probe_%s; NT=8; IDX="%s";\n'
                     '      NOTE="%s probe, %s, itend=%s, ie=%d (%s); 8 cells: innermost, farthest per quadrant, 3 PD/W cells near the donation ray at r=3,6,9" ;;'
                     % (tag, tag, tag, probe, name, purpose, L, ie, tag))
        cases.append('  prod_%s)  SCRIPT=prod_%s.slurm;  TAG=prod_%s;  NT=512; IDX="$(seq %d 3 %d)";\n'
                     '      NOTE="%s 512-point sunflower, %s, itend=%s, ie=%d (%s), 10 reps (%d-%d:3)" ;;'
                     % (tag, tag, tag, 1368 + off, 2901 + off, name, purpose, L, ie, tag, 1368 + off, 2901 + off))
    usage = "|".join("probe_%s|prod_%s" % (t, t) for t, _, _ in arrays(eps_series))
    return """#!/bin/bash
# Submit one %(name)s array: stage the game list, capture the array id with --parsable into JOBID_<tag>, and append one
# line to the cross-project ledger ~/jobs.tsv.   bash submit.sh {%(usage)s}
# %(purpose)s.  The run length is compiled in (compile.sh %(L)s -> sf_%(L)s.x); the run directory is run_%(L)s/.
set -e
L=%(L)s
case "$1" in
%(cases)s
  *) echo "usage: bash submit.sh {%(usage)s}"; exit 1 ;;
esac
# a live probe task is a file collision with the production array of the same stride
case "$1" in
  prod_*) P=JOBID_probe_${1#prod_} ;;
  *) P= ;;
esac
if [ -n "$P" ] && [ -f "$P" ]; then
  live=$(squeue -j "$(cat "$P")" -h -o '%%i' 2>/dev/null | wc -l | tr -d ' ')
  if [ "${live:-0}" -gt 0 ]; then
    echo "REFUSING: $live task(s) of probe $(cat "$P") are still in the queue; they share run_$L/."; exit 1
  fi
fi
[ -x "sf_$L.x" ] || { echo "sf_$L.x not built -- run: bash compile.sh $L"; exit 1; }
[ -f "$SCRIPT" ] || { echo "$SCRIPT not found"; exit 1; }
spec=$(awk -F= '/^#SBATCH --array=/{print $2}' "$SCRIPT")
n=$(echo "$IDX" | wc -w)
[ "$n" -eq "$NT" ] || { echo "internal: $TAG index set has $n entries, NT says $NT"; exit 1; }
echo "$SCRIPT: --array=$spec, $NT tasks, binary sf_$L.x"
mkdir -p "run_$L" log
cp -f games.dat "run_$L/.games.dat.new" && mv -f "run_$L/.games.dat.new" "run_$L/games.dat"
echo "$IDX" | tr ' ' '\\n' | grep -v '^$' > "IDX_$TAG"
jid=$(sbatch --parsable "$SCRIPT")
echo "$jid" > "JOBID_$TAG"
printf '%%s\\tPartnersRivals\\t%(name)s_%%s\\t%%s\\t%%s\\t%%s\\n' "$(date +%%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
""" % {"name": name, "usage": usage, "purpose": purpose, "L": L, "cases": "\n".join(cases)}


def verify_sh(name, L, eps_series):
    usage = "|".join("probe_%s|prod_%s" % (t, t) for t, _, _ in arrays(eps_series))
    return """#!/bin/bash
# Completion of a %(name)s array, established per task from sacct -- never from squeue -u, whose output spans every
# project submitting under this user.    bash verify.sh {%(usage)s}
# A cell counts as complete only with all 10 replicate lines, a histogram of ndist lines AND an r-file of exactly
# 10 x 524288 bytes (the per-replicate counts, written after each replicate).
set -e
RUN=run_%(L)s
J="JOBID_$1"; [ -f "$J" ] || { echo "$J not found -- this kit has no record of that array"; exit 1; }
jid=$(cat "$J")
echo "array $jid"
echo "--- tasks that are not COMPLETED (empty is clean) ---"
sacct -j "$jid" --format=JobID,State,ExitCode,Elapsed -X --noheader | awk '$2 != "COMPLETED"'
echo "--- core-hours, and per-task wall time ---"
sacct -j "$jid" --format=Elapsed,AllocCPUS -X --noheader | awk \\
 '{split($1,a,"[:-]"); if (length(a)==4) s=((a[1]*24+a[2])*60+a[3])*60+a[4]; else s=(a[1]*60+a[2])*60+a[3];
   t+=s*$2; n++; if (s>mx) mx=s; if (mn=="" || s<mn) mn=s}
  END{if(n) printf "%%.1f core-h over %%d tasks; wall %%.1f-%%.1f min, mean %%.1f\\n", t/3600, n, mn/60, mx/60, t/60/n;
      else print "no accounting rows yet"}'
echo "--- cells of THIS array, complete = 10 replicate lines + full histogram + full r-file ---"
I="IDX_$1"
[ -f "$I" ] || { echo "$I not found"; exit 1; }
ndone=0; nshort=0; nnoh=0; nnor=0; nmiss=0; miss=""
while read -r isl; do
  [ -n "$isl" ] || continue
  if [ ! -f "$RUN/$isl" ]; then nmiss=$((nmiss+1)); miss="$miss $isl"; continue; fi
  Lr=$(wc -l < "$RUN/$isl")
  nd=""; nc=0
  if [ -f "$RUN/h$isl" ]; then
    nd=$(awk '/^# distinct/{print $3; exit}' "$RUN/h$isl")
    nc=$(grep -vc '^#' "$RUN/h$isl") || nc=0
  fi
  rs=0; [ -f "$RUN/r$isl" ] && rs=$(stat -c %%s "$RUN/r$isl")
  if [ "$Lr" -ge 10 ] && [ -n "$nd" ] && [ "$nc" -eq "$nd" ] && [ "$rs" -eq 5242880 ]; then
    ndone=$((ndone+1))
  elif [ "$Lr" -lt 10 ]; then
    nshort=$((nshort+1)); miss="$miss $isl(${Lr}rep)"
  elif [ -z "$nd" ] || [ "$nc" -ne "$nd" ]; then
    nnoh=$((nnoh+1)); miss="$miss $isl(hist $nc/${nd:-0})"
  else
    nnor=$((nnor+1)); miss="$miss $isl(rfile ${rs}B)"
  fi
done < "$I"
echo "$ndone complete of $(wc -l < "$I") in this array"
[ "$nmiss" -gt 0 ] && echo "  $nmiss not started"
[ "$nshort" -gt 0 ] && echo "  $nshort short on replicates"
[ "$nnoh" -gt 0 ] && echo "  $nnoh have 10 replicates but no complete histogram -- RESUBMIT THESE"
[ "$nnor" -gt 0 ] && echo "  $nnor have histogram but a short r-file -- RESUBMIT THESE"
[ -n "$miss" ] && echo " incomplete:$miss"
exit 0
""" % {"name": name, "usage": usage, "L": L}


def compile_sh(name, purpose):
    return """#!/bin/bash
# %(name)s: %(purpose)s.
#   bash compile.sh 1e7 | bash compile.sh 1e8     -> sf_<L>.x, one binary per run length
# itend is a COMPILE-TIME parameter (`data itv`), so the binary's name says the run length.
# sf.f is dw3's with the parameter lines of mkkits.py changed and the per-replicate r-file added; `diff ../dw3/sf.f sf.f`.
set -e
case "$1" in
  1e7) IT=10000000 ;;
  1e8) IT=100000000 ;;
  *) echo "usage: bash compile.sh {1e7|1e8}"; exit 1 ;;
esac
sed "s|data itv  /10000000/|data itv  /$IT/|" sf.f > sf_$1.f
grep -q "data itv  /$IT/" sf_$1.f || { echo "itend patch did not apply"; exit 1; }
module load intel/25.2.1-fasrc01
ifx -O3 -xHost -fp-model precise -o sf_$1.x sf_$1.f payf3.f payf2.f mtb.f mt.f
ls -la sf_$1.x
""" % {"name": name, "purpose": purpose}


PACK = r'''#!/usr/bin/env python3
"""
Pack a %(name)s run_<L>/ directory, ON CANNON (stdlib only: no numpy on the login node's python 3.6), so that the packs
come down instead of the run directory.

    python3 pack.py run_%(L)s packed [../atoms512.bin]

Per error rate <e> (EPSN below), read by DiskM2WF/Opt/wfload.py exactly like dw1..dw4's packs:
  %(name)s_<e>.idx   one line per cell, ascending gid:  gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total ps1..ps16
  %(name)s_<e>.bin   65536 little-endian float32 per cell, same order, normalised to sum 1
  %(name)s_<e>.win   one line per (cell, replicate): gid irun rank1code abundance selfpay ef
and NEW here, from the r-files (the 65536 int64 counts of each replicate, unit 8 of sf.f):
  %(name)s_<e>.rep   one line per (cell, replicate): gid irun ef s000 s100 s010 s001 s110 s011 s111
                 the share of that replicate's sampled population in each atom, computed with atoms512.bin (one byte per
                 strategy per sunflower cell, code = 4*efficient + 2*nash + competitive, cells in ipt order; built by
                 mkatoms.py from the exact eps -> 0 masks).  s101 is asserted zero.
A truncated h-file or a short r-file is refused, not renormalised.
"""
import os, sys, glob
from array import array
from itertools import compress

NC = 65536
EPSN = %(epsn)s
NPOP = %(npop)d           # must match `parameter (n=...)` in sf.f


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
        raise ValueError("TRUNCATED histogram: %%d lines sum %%d, header says %%d %%d" %% (len(cnt), tot, meta["ndist"], meta["total"]))
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
        raise ValueError("r-file has %%d bytes, expected %%d for %%d replicates" %% (size, nrep * 8 * NC, nrep))
    with open(path, "rb") as f:
        a.fromfile(f, nrep * NC)
    if sys.byteorder != "little":
        a.byteswap()
    out = []
    for r in range(nrep):
        h = a[r * NC:(r + 1) * NC]
        if sum(h) != perrep(itend):
            raise ValueError("replicate %%d counts sum to %%d, expected %%d" %% (r + 1, sum(h), perrep(itend)))
        out.append(h)
    return out


def atom_shares(h, sel, tot):
    return [sum(compress(h, sel[a])) / float(tot) for a in range(8)]


def main(rundir, out, atoms):
    os.makedirs(out, exist_ok=True)
    A = open(atoms, "rb").read()
    if len(A) != 512 * NC:
        raise ValueError("%%s has %%d bytes, expected 512 x 65536" %% (atoms, len(A)))
    hs = sorted(glob.glob(os.path.join(rundir, "h[0-9]*")), key=lambda p: int(os.path.basename(p)[1:]))
    print("%%d h-files in %%s" %% (len(hs), rundir))
    by = {}; dropped = []; pending = []; nowin = []; mismatch = []
    for hp in hs:
        isl = int(os.path.basename(hp)[1:])
        sp = os.path.join(rundir, str(isl)); rp = os.path.join(rundir, "r%%d" %% isl)
        if not os.path.exists(sp):
            print("  task %%d: h-file but no summary, DROPPED" %% isl); dropped.append(isl); continue
        try:
            meta, p = read_h(hp)
            ie, nrep, pay, ef, sd, ps, efs = read_summary(sp)
            if meta["total"] != nrep * perrep(meta["itend"]):
                mismatch.append(isl)
            reps = read_r(rp, nrep, meta["itend"])
        except Pending:
            pending.append(isl); continue
        except Exception as e:
            print("  task %%d: %%s -- DROPPED" %% (isl, e)); dropped.append(isl); continue
        ipt = int(meta["tag"].split("_")[1][1:])
        if meta["gid"] != 2000 + ipt:
            raise ValueError("isl %%d: gid %%d is not 2000 + ipt %%d" %% (isl, meta["gid"], ipt))
        ac = A[ipt * NC:(ipt + 1) * NC]
        sel = [[x == a for x in ac] for a in range(8)]
        shares = [atom_shares(h, sel, perrep(meta["itend"])) for h in reps]
        for s in shares:
            if s[5] != 0.0:
                raise ValueError("isl %%d: atom 101 has mass %%g" %% (isl, s[5]))
        wp = os.path.join(rundir, "w%%d" %% isl)
        win = read_win(wp) if os.path.exists(wp) else []
        if not win:
            nowin.append(isl)
        by.setdefault(ie, []).append((meta["gid"], meta, p, isl, nrep, pay, ef, sd, ps, win, efs, shares))
    for ie in sorted(by):
        R = sorted(by[ie], key=lambda r: r[0]); nm = EPSN.get(ie, "ie%%d" %% ie)
        fb = open(os.path.join(out, "%(name)s_%%s.bin" %% nm), "wb")
        fi = open(os.path.join(out, "%(name)s_%%s.idx" %% nm), "w")
        fw = open(os.path.join(out, "%(name)s_%%s.win" %% nm), "w")
        fr = open(os.path.join(out, "%(name)s_%%s.rep" %% nm), "w")
        fw.write("# gid irun rank1 abund selfpay\n")
        fi.write("# gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total ps1..ps16\n")
        fr.write("# gid irun ef s000 s100 s010 s001 s110 s011 s111   (atom shares of the replicate, exact eps->0 atoms)\n")
        short = []
        for gid, meta, p, isl, nrep, pay, ef, sd, ps, win, efs, shares in R:
            for irun, code, ab, spay in win:
                fw.write("%%6d %%4d %%6d %%12.8f %%14.7f\n" %% (gid, irun, code, ab, spay))
            for r in range(nrep):
                s = shares[r]
                fr.write("%%6d %%4d %%12.8f %%s\n" %% (gid, r + 1, efs[r], " ".join("%%12.8f" %% s[a] for a in (0, 4, 2, 1, 6, 3, 7))))
            p.tofile(fb)
            fi.write("%%6d %%6d %%-24s %%20.12e %%20.12e %%20.12e %%20.12e %%20.12e %%20.12e %%18.10e %%18.10e %%14.6e %%7d %%4d %%16d %%s\n"
                     %% (gid, isl, meta["tag"], meta["u"], meta["v"], meta["cR"], meta["cS"], meta["cT"], meta["emax"],
                        pay, ef, sd, meta.get("ndist", -1), nrep, meta.get("total", -1), " ".join("%%14.10f" %% x for x in ps)))
            if nrep < 10:
                short.append(isl)
        fb.close(); fi.close(); fw.close(); fr.close()
        print("  ie=%%d -> %(name)s_%%s.{idx,bin,win,rep}  %%4d cells%%s" %% (ie, nm, len(R), "   SHORT: %%s" %% short if short else ""))
    bad = 0
    if pending:
        print("   (%%d task(s) have not written a histogram yet: %%s%%s)" %% (len(pending), pending[:12], " ..." if len(pending) > 12 else ""))
    if dropped:
        print("!! %%d cell(s) DROPPED: %%s" %% (len(dropped), dropped)); bad += 1
    if mismatch:
        print("!! %%d cell(s) whose summary and histogram disagree: %%s" %% (len(mismatch), mismatch)); bad += 1
    if nowin:
        print("!! %%d cell(s) with no rank-1 lines: %%s" %% (len(nowin), nowin)); bad += 1
    if not bad:
        print("clean: every h-file packed, every histogram whole, every r-file whole, every cell has its rank-1 lines")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "run_%(L)s",
                  sys.argv[2] if len(sys.argv) > 2 else "packed",
                  sys.argv[3] if len(sys.argv) > 3 else os.path.join("..", "atoms512.bin")))
'''


def readme(name, n, beta, u, L, seed, eps_series, purpose):
    arr = arrays(eps_series)
    lines = ["# `Cannon/%s` — %s" % (name, purpose), "",
             "Made 2026-09-22: %s." % ("an error-rate series" if eps_series
                                        else "the seeded re-run of one of Figure 4's runs with the per-replicate r-file" if name.startswith("f")
                                        else "one of the four missing corners of the {N} x {beta} x {mu} cube"),
             "",
             "Generated by `../mkkits.py` from `../dw3` (which is DiskM2WF's dw1/dw2 with parameter lines changed): `diff ../dw3/sf.f sf.f`",
             "shows the parameter lines (`n=%d`, `iseedb=%d`, `uval=%s`, `bval=%s`%s) and the one functional addition of these kits,"
             % (n, seed, u, beta, ", `epsv=1e-5,1e-3,1e-4`" if eps_series else ""),
             "the per-replicate count file `r<task>` (unit 8: after every replicate the 65536 int64 counts, 524288 bytes each), which",
             "`pack.py` turns into per-replicate atom shares (`.rep`) with `../atoms512.bin`.  `python3 ../mkkits.py test` proves the addition",
             ("leaves the summary, winner and histogram files byte-identical.  Seeds `%d + (isl-1)*10 + irep`, THE SAME as the original run's,"
              " so the summary, winner and histogram files must come out identical to the originals in ~/CL1/DiskM2WF/%s/run_%s/ (cmp them)." % (seed, "dw1" if name == "f1" else "dw2", L))
             if name.startswith("f") else
             "leaves the summary, winner and histogram files byte-identical.  Seeds `%d + (isl-1)*10 + irep`, disjoint from every earlier campaign." % seed,
             "", "## Arrays", ""]
    for tag, ie, off in arr:
        lines.append("    %s: ie = %d, --array=%d-%d:3 (512 tasks); probe cells %s" % (tag, ie, 1368 + off, 2901 + off, " ".join(str(i + off) for i in PROBE_E4)))
    lines += ["", "Task decode (dw1's): ie = mod(isl-1,3)+1, ig = (isl-1)/3+1; the sunflower is games 456-967, gid 2000+ipt, ipt = ig-456.", "",
              "## Protocol (on Cannon, in ~/CL1/PartnersRivals/%s; ../atoms512.bin uploaded once)" % name, "",
              "    bash compile.sh %s" % L]
    for tag, ie, off in arr:
        lines += ["    bash submit.sh probe_%s     # 8 cells; then bash verify.sh probe_%s and READ the rate before" % (tag, tag),
                  "    bash submit.sh prod_%s      # 512 tasks" % tag]
    lines += ["    python3 pack.py run_%s packed   # -> packed/%s_<e>.{idx,bin,win,rep}; copy to CL1/PartnersRivals/Data/" % (L, name),
              "", "Cost: %s." % {("1e7", 1000): "about 65 min per task as in dw1/dw3, ~560 core-h per 512-task array",
                                 ("1e8", 100): "about 67 min per task as in dw2, ~570 core-h per array",
                                 ("1e7", 100): "about 7 min per task (N x itend is a tenth of dw1's), ~60 core-h per array"}[(L, n)],
              "Completion is established per task from `sacct` (verify.sh), never from an empty `squeue`.", ""]
    return "\n".join(lines)


def build(names=None):
    for name, n, beta, u, L, seed, eps_series, purpose in KITS:
        if names and name not in names:
            continue
        d = os.path.join(HERE, name)
        os.makedirs(os.path.join(d, "log"), exist_ok=True)
        for f in COPY:
            shutil.copyfile(os.path.join(TPL, f), os.path.join(d, f))
        open(os.path.join(d, "sf.f"), "w").write(make_sf(name, n, beta, u, seed, eps_series))
        for tag, ie, off in arrays(eps_series):
            wall = WALL[(L, n)]
            probe = ",".join(str(i + off) for i in PROBE_E4)
            open(os.path.join(d, "probe_%s.slurm" % tag), "w").write(slurm(name, purpose, tag, "probe", L, n, probe, wall))
            open(os.path.join(d, "prod_%s.slurm" % tag), "w").write(slurm(name, purpose, tag, "prod", L, n, "%d-%d:3" % (1368 + off, 2901 + off), wall))
        open(os.path.join(d, "submit.sh"), "w").write(submit_sh(name, purpose, L, eps_series)); os.chmod(os.path.join(d, "submit.sh"), 0o755)
        open(os.path.join(d, "verify.sh"), "w").write(verify_sh(name, L, eps_series)); os.chmod(os.path.join(d, "verify.sh"), 0o755)
        open(os.path.join(d, "compile.sh"), "w").write(compile_sh(name, purpose)); os.chmod(os.path.join(d, "compile.sh"), 0o755)
        epsn = "{1: 'e5', 2: 'e3', 3: 'e4'}" if eps_series else "{1: 'e2', 2: 'e3', 3: 'e4'}"
        open(os.path.join(d, "pack.py"), "w").write(PACK % {"name": name, "L": L, "epsn": epsn, "npop": n})
        open(os.path.join(d, "README.md"), "w").write(readme(name, n, beta, u, L, seed, eps_series, purpose))
        diff = subprocess.run(["diff", os.path.join(TPL, "sf.f"), os.path.join(d, "sf.f")], capture_output=True, text=True).stdout
        nchanged = sum(1 for l in diff.splitlines() if l[:1] in "<>")
        print("%s: written; sf.f differs from dw3's in %d lines" % (name, nchanged))


def test():
    """dw3's own parameters, with and without the addition, at itend = 1e5: the three original output files must agree byte for byte."""
    import tempfile
    work = tempfile.mkdtemp(prefix="mkkits_test_", dir=HERE)
    bins = {}
    for label, addition in (("orig", False), ("new", True)):
        src = make_sf("dw3", 1000, "100.d+00", "1.d-04", 10000000, False, addition=addition, itv=100000)
        src = src.replace("*     dw3: N = 1000, m = 1, beta = 100, u = 1e-4, itend = 1e7 (default; compile.sh sets it)",
                          "*     dw3: N = 1000, m = 1, beta = 100, u = 1e-4, itend = 1e7 (default; compile.sh sets it)")
        d = os.path.join(work, label); os.makedirs(d)
        open(os.path.join(d, "sf.f"), "w").write(src)
        for f in COPY:
            shutil.copyfile(os.path.join(TPL, f), os.path.join(d, f))
        subprocess.check_call(["gfortran", "-O2", "-o", "sf.x", "sf.f", "payf3.f", "payf2.f", "mtb.f", "mt.f"], cwd=d)
        bins[label] = d
    procs = [subprocess.Popen(["./sf.x", "1902"], cwd=bins[l]) for l in ("orig", "new")]
    for p in procs:
        assert p.wait() == 0
    for f in ("1902", "w1902", "h1902"):
        same = filecmp.cmp(os.path.join(bins["orig"], f), os.path.join(bins["new"], f), shallow=False)
        print("%-6s %s" % (f, "IDENTICAL" if same else "DIFFERENT"))
        assert same
    r = os.path.join(bins["new"], "r1902"); size = os.path.getsize(r)
    print("r1902: %d bytes (%d replicates of 524288)" % (size, size // 524288))
    assert size == 10 * 524288
    # the ten replicate blocks must sum to the h-file
    a = array_q(r); h = {}
    for ln in open(os.path.join(bins["new"], "h1902")):
        if ln[0] != "#":
            c, k = ln.split(); h[int(c)] = int(k)
    tot = [0] * 65536
    for rep in range(10):
        for i in range(65536):
            tot[i] += a[rep * 65536 + i]
    assert {i: t for i, t in enumerate(tot) if t} == h, "replicate blocks do not sum to the histogram"
    print("the ten replicate blocks sum exactly to h1902: %d distinct strategies, %d counts" % (len(h), sum(h.values())))
    assert not os.path.exists(os.path.join(bins["orig"], "r1902"))
    print("test passed; work dir %s" % work)


def array_q(path):
    from array import array
    a = array("q"); a.fromfile(open(path, "rb"), os.path.getsize(path) // 8); return a


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        build(sys.argv[1:] or None)          # python3 mkkits.py [kit ...]   (no names: every kit)
