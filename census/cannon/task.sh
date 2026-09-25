#!/bin/bash
# One census pass in both arithmetics, striped over NSTR stripes run NPAR at a time.
#   usage: task.sh <tag> <nstripes> <npar> [stripe list]     tag in: all | probe
# Writes out/<prog>_<mode>_<stripe>.txt (+ .err) for prog in pairsq (exact), pairs (double);
# modes: self, rivP (T>S), rivM (T<S), nash at (u,v) = (-2,2).
set -e
tag=$1; NSTR=$2; NPAR=$3; shift 3
mkdir -p out
if [ $# -gt 0 ]; then STRIPES="$@"; else STRIPES=$(seq 0 $((NSTR-1))); fi
jobs=()
for s in $STRIPES; do
  for prog in pairsq pairs; do
    jobs+=("./$prog self $s $NSTR > out/${prog}_self_$s.txt 2> out/${prog}_self_$s.err")
    jobs+=("./$prog rival $s $NSTR 1 > out/${prog}_rivP_$s.txt 2> out/${prog}_rivP_$s.err")
    jobs+=("./$prog rival $s $NSTR -1 > out/${prog}_rivM_$s.txt 2> out/${prog}_rivM_$s.err")
    jobs+=("./$prog nash $s $NSTR -2 2 > out/${prog}_nash_$s.txt 2> out/${prog}_nash_$s.err")
  done
done
start=$(date +%s)
printf '%s\n' "${jobs[@]}" | xargs -P $NPAR -I{} bash -c '{}'
end=$(date +%s)
echo "$tag: ${#jobs[@]} passes over $(echo $STRIPES | wc -w) stripes of $NSTR, npar $NPAR, wall $((end-start)) s" | tee out/TIMING_$tag
