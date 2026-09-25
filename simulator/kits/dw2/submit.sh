#!/bin/bash
# Submit one dw2 array, doing the three things the global protocol requires in
# a single step: stage the game list, capture the array id with --parsable into
# a JOBID file, and append one line to the cross-project ledger ~/jobs.tsv.
#
#   bash submit.sh probe8     5 tasks, itend = 1e8, the rate + convergence probe
#   bash submit.sh probe9     5 tasks, itend = 1e9, the same five cells
#   bash submit.sh prod8    512 tasks, itend = 1e8
#   bash submit.sh prod9    512 tasks, itend = 1e9
#
# THE TWO RUN LENGTHS ARE SEPARATE CAMPAIGNS IN SEPARATE DIRECTORIES.  itend is
# compiled in, so `run_1e8/` and `run_1e9/` never share a file and neither
# array's idempotence guard can see the other's output.  That is deliberate:
# the point of running both on the probe's five cells is to compare them.
#
# games.dat is staged by write-to-temp-then-rename, never by writing the live
# file in place: `cp -f` truncates its target first, and an array task starting
# in that instant would read a short or empty game list.
set -e
case "$1" in
  probe8) L=1e8; SCRIPT=probe_1e8.slurm; TAG=probe8; NT=5;   IDX="1368 2892 2895 2898 2901";
          NOTE="dw2 rate+convergence probe, N=100 beta=3 u=1e-4 eps=1e-4, itend=1e8 (1e4 substitutions/rep); 5 cells: innermost point and the farthest in each quadrant, r=0.12 to 38.16" ;;
  probe9) L=1e9; SCRIPT=probe_1e9.slurm; TAG=probe9; NT=5;   IDX="1368 2892 2895 2898 2901";
          NOTE="dw2 rate+convergence probe, N=100 beta=3 u=1e-4 eps=1e-4, itend=1e9 (1e5 substitutions/rep, dw1's convention); the SAME 5 cells as probe8, for the convergence comparison" ;;
  prod8)  L=1e8; SCRIPT=prod_1e8.slurm;  TAG=vor8;   NT=512; IDX="$(seq 1368 3 2901)";
          NOTE="dw2 512-point sunflower, N=100 beta=3 u=1e-4 eps=1e-4, itend=1e8, 10 reps (1368-2901:3)" ;;
  prod9)  L=1e9; SCRIPT=prod_1e9.slurm;  TAG=vor9;   NT=512; IDX="$(seq 1368 3 2901)";
          NOTE="dw2 512-point sunflower, N=100 beta=3 u=1e-4 eps=1e-4, itend=1e9, 10 reps (1368-2901:3)" ;;
  *) echo "usage: bash submit.sh {probe8|probe9|prod8|prod9}"; exit 1 ;;
esac

# A LIVE PROBE TASK IS A FILE COLLISION, NOT A DUPLICATE.  The probe indices
# are members of the production array at the SAME run length, sharing
# run_<L>/, and the guard skips a task only once it is COMPLETE.  dw1 learned
# this the hard way; the same refusal is kept here.
case "$1" in
  prod8) P=JOBID_probe8 ;;
  prod9) P=JOBID_probe9 ;;
  *)     P= ;;
esac
if [ -n "$P" ] && [ -f "$P" ]; then
  live=$(squeue -j "$(cat "$P")" -h -o '%i' 2>/dev/null | wc -l | tr -d ' ')
  if [ "${live:-0}" -gt 0 ]; then
    echo "REFUSING: $live task(s) of probe $(cat "$P") are still in the queue."
    echo "  They share run_$L/ with this array and would be written twice, concurrently."
    echo "  Wait for the probe to drain, then resubmit; the guard will skip its five."
    exit 1
  fi
fi

[ -x "sf_$L.x" ] || { echo "sf_$L.x not built -- run: bash compile.sh $L"; exit 1; }
[ -f "$SCRIPT" ] || { echo "$SCRIPT not found"; exit 1; }

# the ledger's task count must be the script's, not a number typed twice
spec=$(awk -F= '/^#SBATCH --array=/{print $2}' "$SCRIPT")
n=$(echo "$IDX" | wc -w)
[ "$n" -eq "$NT" ] || { echo "internal: $TAG index set has $n entries, NT says $NT"; exit 1; }
echo "$SCRIPT: --array=$spec, $NT tasks, binary sf_$L.x"

mkdir -p "run_$L" log
cp -f games.dat "run_$L/.games.dat.new" && mv -f "run_$L/.games.dat.new" "run_$L/games.dat"
echo "$IDX" | tr ' ' '\n' | grep -v '^$' > "IDX_$TAG"

jid=$(sbatch --parsable "$SCRIPT")
echo "$jid" > "JOBID_$TAG"
printf '%s\tDiskM2WF\tdw2_%s\t%s\t%s\t%s\n' \
       "$(date +%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
