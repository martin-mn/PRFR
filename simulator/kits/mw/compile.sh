#!/bin/bash
# mw: the WF process over the 16 binary memory-one strategies at the 512
# sunflower games.  Same compiler and flags as DiskM2WF/Cannon/dw1, so the two
# campaigns are the same build of the same generation loop.
#   sf1.x   N = 1000, beta = 100, u = 1e-2, itend = 1e7   (the F1 parameters)
#   sf2.x   N = 100,  beta = 3,   u = 1e-4, itend = 1e8   (the F2 parameters)
#   sf1s.x  the same as sf1.x with itend cut 100x and an independent seed base
#   sf2s.x  the same as sf2.x with itend cut 100x and an independent seed base
# The sources are NOT edited by hand: ../../Opt/mksf.py builds all four from
# Ref/sf_dw1.f by an asserted list of 26 substitutions; sf1.f / sf2.f differ in
# exactly five parameter lines and sf<W>s.f from sf<W>.f in exactly two.
#
#   bash compile.sh                  build all four
#   bash compile.sh sf1s sf2s        build only these
#
# BUILD ONLY WHAT YOU NEED WHILE AN ARRAY IS RUNNING.  Relinking sf1.x under a
# live prod1 is a needless risk: ifx writes the output in place, and a task
# exec'ing it in that instant gets a truncated image.
set -e
module load intel/25.2.1-fasrc01
T="$*"
[ -n "$T" ] || T="sf1 sf2 sf1s sf2s"
for t in $T; do
  [ -f "$t.f" ] || { echo "$t.f not found"; exit 1; }
  ifx -O3 -xHost -fp-model precise -o "$t.x" "$t.f" payf3.f payf2.f mtb.f mt.f
  ls -la "$t.x"
done
# the lines that separate the builds, for the record
echo "--- sf1.f vs sf2.f (the F1/F2 parameters) ---"
diff sf1.f sf2.f | grep -E '^[<>]' | grep -v '^[<>] \*' || true
echo "--- sf1.f vs sf1s.f (the convergence control) ---"
diff sf1.f sf1s.f | grep -E '^[<>]' | grep -v '^[<>] \*' || true
