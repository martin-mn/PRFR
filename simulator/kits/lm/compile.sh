#!/bin/bash
# lm: bash compile.sh {g0|g01|g05|g1} -> sf_<g>.x, with pglob and the seed base compiled in (itend = 1e7, as in f1).
#   g0: pglob = 0 (all mutations local), seeds 30000000+;  g01: pglob = 0.1, 31000000+;  g05: pglob = 0.5, 32000000+;
#   g1: pglob = 1 (all global: f1's process, not f1's stream), 39000000+ -- for local tests only, never submitted.
# On Cannon: ifx as in f1.  Locally: FC=gfortran bash compile.sh g0
set -e
case "$1" in
  g0)  PG=0.d+00; SB=30000000 ;;
  g01) PG=1.d-01; SB=31000000 ;;
  g05) PG=5.d-01; SB=32000000 ;;
  g1)  PG=1.d+00; SB=39000000 ;;
  *) echo "usage: bash compile.sh {g0|g01|g05|g1}"; exit 1 ;;
esac
FC=${FC:-ifx}
IT=${ITEND:-10000000}
# a shortened binary must never reach the cluster: ITEND is for local test builds only
if [ "$FC" = ifx ] && [ "$IT" != 10000000 ]; then echo "ITEND=$IT refused for an ifx (Cannon) build"; exit 1; fi
sed -e "s|      parameter (pglob=0.d+00)|      parameter (pglob=$PG)|" \
    -e "s|      parameter (iseedb=30000000)|      parameter (iseedb=$SB)|" \
    -e "s|data itv  /10000000/|data itv  /$IT/|" sf.f > sf_$1.f
grep -q "parameter (pglob=$PG)" sf_$1.f && grep -q "parameter (iseedb=$SB)" sf_$1.f && grep -q "data itv  /$IT/" sf_$1.f \
  || { echo "parameter patch did not apply"; exit 1; }
if [ "$FC" = ifx ]; then
  module load intel/25.2.1-fasrc01
  ifx -O3 -xHost -fp-model precise -o sf_$1.x sf_$1.f payf3.f payf2.f mtb.f mt.f
else
  $FC -O2 -o sf_$1.x sf_$1.f payf3.f payf2.f mtb.f mt.f
fi
ls -la sf_$1.x
