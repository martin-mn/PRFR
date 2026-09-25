#!/bin/bash
# dw4: the WF process at N = 1000, beta = 3, u = 1e-2: weak selection, frequent mutation.
#   bash compile.sh 1e7     -> sf_<L>.x, one binary per run length
# itend is a COMPILE-TIME parameter (`data itv`), so the binary's name says the run length.
# Everything except five parameter lines is DiskM2WF/Cannon/dw2's sf.f, byte for byte.
set -e
case "$1" in
  1e7) IT=10000000 ;;
  *) echo "usage: bash compile.sh {1e7}"; exit 1 ;;
esac
sed "s|data itv  /10000000/|data itv  /$IT/|" sf.f > sf_$1.f
grep -q "data itv  /$IT/" sf_$1.f || { echo "itend patch did not apply"; exit 1; }
module load intel/25.2.1-fasrc01
ifx -O3 -xHost -fp-model precise -o sf_$1.x sf_$1.f payf3.f payf2.f mtb.f mt.f
ls -la sf_$1.x
