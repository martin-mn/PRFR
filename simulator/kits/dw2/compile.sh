#!/bin/bash
# dw2: the WF process at N = 100, beta = 3, u = 1e-4 -- the near-rare-mutation
# regime, and the direct counterpart of CL1/DiskM2IN's N = 100, beta = 3 run.
#
#   bash compile.sh 1e8      -> sf_1e8.x   (1e4 substitutions per replicate)
#   bash compile.sh 1e9      -> sf_1e9.x   (1e5, the project's dw1 convention)
#
# itend is a COMPILE-TIME parameter (`data itv`), so there is one binary per
# run length and the binary's name says which.  Everything else -- the
# generation loop, the PRNG, the payoff cache, the task decode -- is dw1's,
# byte for byte; `diff ../dw1/sf.f sf.f` is five lines, all of them parameters.
set -e
case "$1" in
  1e8) IT=100000000  ;;
  1e9) IT=1000000000 ;;
  *) echo "usage: bash compile.sh {1e8|1e9}"; exit 1 ;;
esac
sed "s|data itv  /100000000/|data itv  /$IT/|" sf.f > sf_$1.f
grep -q "data itv  /$IT/" sf_$1.f || { echo "itend patch did not apply"; exit 1; }
module load intel/25.2.1-fasrc01
ifx -O3 -xHost -fp-model precise -o sf_$1.x sf_$1.f payf3.f payf2.f mtb.f mt.f
ls -la sf_$1.x
