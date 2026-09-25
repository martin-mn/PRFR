#!/usr/bin/env python3
"""Build kit lm (local mutation) from ../f1, the seeded kit of Figure 4's large-population memory-two run
(N = 1000, beta = 100, mu = 1e-2, eps = 1e-4).  The author's design:

    with probability mu an individual mutates; the mutation is GLOBAL with probability nu (a strategy drawn uniformly from all
    65536, its own included, exactly as in f1) and LOCAL with probability 1 - nu (one of the 16 bits of its own strategy,
    chosen uniformly, is flipped).  Runs: nu = 0, 0.1, 0.5 (nu = 1 is f1 itself).

In sf.f nu is called pglob, because f1 already uses the name nu for the number of mutation-rate values.  Every change to f1's
sf.f is an asserted substitution below, so `diff <f1>/sf.f sf.f` is the audit.  Run once, locally:  python3 mklm.py
"""
import pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
F1 = HERE.parent / "f1"          # repository layout: simulator/kits/f1 (author's tree: PartnersRivals/Cannon/f1)

src = (F1 / "sf.f").read_text()


def sub(old, new):
    global src
    n = src.count(old)
    assert n == 1, (n, old[:70])
    src = src.replace(old, new)


# 1. header: what this kit is
sub("* M2 strategies; WF pairwise comparison  (synchronous Fermi imitation)\n",
    "* M2 strategies; WF pairwise comparison  (synchronous Fermi imitation)\n"
    "*\n"
    "* KIT lm (CL1/PartnersRivals1, 2026-09-24): f1 with a MIXED MUTATION KERNEL.\n"
    "* With probability u an individual mutates; the mutant is GLOBAL with\n"
    "* probability pglob (a strategy drawn uniformly from all 65536, its own\n"
    "* included, as in f1) and LOCAL with probability 1-pglob (one of the 16\n"
    "* bits of its own strategy, chosen uniformly, is flipped).  pglob and the\n"
    "* seed base are compile-time parameters set by compile.sh:\n"
    "*     g0: pglob = 0    seeds 30000000+    g01: pglob = 0.1  seeds 31000000+\n"
    "*     g05: pglob = 0.5 seeds 32000000+    g1: pglob = 1, seeds 39000000+,\n"
    "*     local tests only, never submitted\n"
    "* Everything else is f1's: N = 1000, beta = 100, u = 1e-2, eps = 1e-4 stride\n"
    "* (ie = 3), itend = 1e7, 10 replicates per task, the 512-point sunflower,\n"
    "* output formats unchanged.  The global/local decision costs one extra\n"
    "* uniform per mutation, so pglob = 1 is f1's process but not f1's stream.\n"
    "* `diff <f1>/sf.f sf.f` is the audit; mklm.py makes it.\n")
# 1b. inherited f1 comments that would now be wrong
sub("* The generation loop is byte-identical to wf3/sf.f and hence to Cannon/ca10\n",
    "* The generation loop (except lm's mutation step, see the header) is\n"
    "* byte-identical to wf3/sf.f and hence to Cannon/ca10\n")
sub("* Seeds 8000000 + (isl-1)*nper + irep, disjoint from ca2 (43891-45890),\n",
    "* Seeds iseedb + (isl-1)*nper + irep, iseedb = 30/31/32/39 million for\n"
    "* g0/g01/g05/g1 (lm header); f1 used 8000000.  Earlier bases: ca2 (43891-45890),\n")
# 2. the two compile-time parameters (compile.sh substitutes these exact lines)
sub("      parameter (iseedb=8000000)\n",
    "      parameter (iseedb=30000000)\n"
    "C     lm: probability that a mutation is global (compile.sh sets it)\n"
    "      parameter (pglob=0.d+00)\n")
# 3. the mutation step
sub("""               if (imut.eq.1) then
C                 one integer draw supplies all 16 loci
                  if (irb.ge.nrb) then
                     call mtfill(rb,nrb)
                     irb=0
                  endif
                  irb=irb+1
                  sn(i)=int(rb(irb)*65536.d+00)
               else
""", """               if (imut.eq.1) then
C                 lm: one uniform decides global or local; a second one
C                 supplies either all 16 loci (global, as in f1) or the
C                 locus to flip (local).  rb lies in (0,1), so pglob = 0
C                 is always local and pglob = 1 always global.
                  if (irb.ge.nrb) then
                     call mtfill(rb,nrb)
                     irb=0
                  endif
                  irb=irb+1
                  rkind=rb(irb)
                  if (irb.ge.nrb) then
                     call mtfill(rb,nrb)
                     irb=0
                  endif
                  irb=irb+1
                  if (rkind.lt.pglob) then
                     sn(i)=int(rb(irb)*65536.d+00)
                  else
                     kflip=int(rb(irb)*16.d+00)
                     sn(i)=ieor(s(i),ishft(1,kflip))
                  endif
               else
""")
(HERE / "sf.f").write_text(src)
for f in ("payf3.f", "payf2.f", "mtb.f", "mt.f", "games.dat"):
    shutil.copy(F1 / f, HERE / f)

pack = (F1 / "pack.py").read_text()
assert pack.count('"f1_%s') == 4 and pack.count("f1_%s.{idx") == 1
pack = pack.replace('"f1_%s', 'PFX + "_%s').replace("-> f1_%s.{idx,bin,win,rep}", "-> %s_%s.{idx,bin,win,rep}")
pack = pack.replace('print("  ie=%d -> %s_%s.{idx,bin,win,rep}  %4d cells%s" % (ie, nm,',
                    'print("  ie=%d -> %s_%s.{idx,bin,win,rep}  %4d cells%s" % (ie, PFX, nm,')
assert 'PFX, nm,' in pack
pack = pack.replace("NPOP = 1000           # must match `parameter (n=...)` in sf.f\n",
                    "NPOP = 1000           # must match `parameter (n=...)` in sf.f\n"
                    "# lm: packs are named lm_<g>_<e>.*, <g> taken from the run directory run_<g>\n"
                    "PFX = \"lm\"\n")
pack = pack.replace("def main(rundir, out, atoms):\n",
                    "def main(rundir, out, atoms):\n"
                    "    global PFX\n"
                    "    import re\n"
                    "    b = os.path.basename(os.path.abspath(rundir))\n"
                    "    mg = re.fullmatch(r\"run_(g0|g01|g05|g1)\", b)\n"
                    "    if not mg:\n"
                    "        print(\"!! run directory must be run_<g>, g in g0 g01 g05 g1: %s\" % b); return 1\n"
                    "    PFX = \"lm_\" + mg.group(1)\n")
assert pack.count("global PFX") == 1
pack = pack.replace("Pack a f1 run_<L>/ directory", "Pack an lm run_<g>/ directory (kit lm, from f1's pack.py; packs lm_<g>_<e>.*)")
pack = pack.replace('sys.argv[1] if len(sys.argv) > 1 else "run_1e7"', 'sys.argv[1] if len(sys.argv) > 1 else "run_g0"')
assert pack.count("python3 pack.py run_1e7 packed") == 1
pack = pack.replace("python3 pack.py run_1e7 packed", "python3 pack.py run_g0 packed")
pack = pack.replace("  f1_<e>.", "  lm_<g>_<e>.")
assert "f1_<e>" not in pack
old_h = '    print("%d h-files in %s" % (len(hs), rundir))\n'
assert pack.count(old_h) == 1
pack = pack.replace(old_h, old_h + '    if not hs:\n        print("!! no h-files in %s" % rundir); return 1\n')
(HERE / "pack.py").write_text(pack)
print("wrote sf.f, pack.py and copied payf3.f payf2.f mtb.f mt.f games.dat into", HERE)
