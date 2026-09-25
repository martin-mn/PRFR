#!/bin/bash
# Submit one mw array, doing the three things the global protocol requires in a
# single step: stage the game list, capture the array id with --parsable into a
# JOBID file, and append one line to the cross-project ledger ~/jobs.tsv.
#
#   bash submit.sh probe1     5 tasks, the F1 rate probe   (N = 1000, beta = 100, u = 1e-2)
#   bash submit.sh prod1    512 tasks, the F1 production   (--array=3-1536:3)
#   bash submit.sh probe2     5 tasks, the F2 rate probe   (N = 100,  beta = 3,   u = 1e-4)
#   bash submit.sh prod2    512 tasks, the F2 production   (--array=3-1536:3)
#   bash submit.sh prod1s   512 tasks, the F1 convergence control: itend cut 100x
#   bash submit.sh prod2s   512 tasks, the F2 convergence control: itend cut 100x
#
# W is the run label, and it is used for BOTH the output directory (run$W/) and
# the binary (sf$W.x), so the controls' W = "1s" needs no other change here.
#
# The two runs have their own binary (sf1.x / sf2.x) and their own output
# directory (run1/ / run2/), so they cannot overwrite each other's cells; the
# probe and the production of ONE run do share a directory, on purpose, so the
# probe's five cells are real production output.
#
# games.dat is staged by write-to-temp-then-rename, never by writing the live
# file in place: `cp -f` truncates its target first, and an array task starting
# in that instant would read a short or empty game list.  `mv` on the same
# filesystem is atomic.  (`ln -sf` is worse: it unlinks before it links.)
set -e
case "$1" in
  probe1) SCRIPT=probe1.slurm; W=1; NT=5;   IDX="3 1527 1530 1533 1536";
          NOTE="M1 WF rate probe, F1 params (N=1000 beta=100 u=1e-2 itend=1e7), 5 cells: the innermost and the four farthest, r = 0.12 to 38.16" ;;
  prod1)  SCRIPT=prod1.slurm;  W=1; NT=512; IDX="$(seq 3 3 1536)";
          NOTE="M1 WF, F1 params (N=1000 beta=100 u=1e-2 itend=1e7, eps=1e-4), 512-point sunflower, 10 reps -- the memory-one Figures 3 and 4" ;;
  probe2) SCRIPT=probe2.slurm; W=2; NT=5;   IDX="3 1527 1530 1533 1536";
          NOTE="M1 WF rate probe, F2 params (N=100 beta=3 u=1e-4 itend=1e8), 5 cells: the innermost and the four farthest, r = 0.12 to 38.16" ;;
  prod2)  SCRIPT=prod2.slurm;  W=2; NT=512; IDX="$(seq 3 3 1536)";
          NOTE="M1 WF, F2 params (N=100 beta=3 u=1e-4 itend=1e8, eps=1e-4), 512-point sunflower, 10 reps -- the memory-one SI Figures 2 and 3" ;;
  prod1s) SCRIPT=prod1s.slurm; W=1s; NT=512; IDX="$(seq 3 3 1536)";
          NOTE="M1 WF CONVERGENCE CONTROL for prod1: F1 with itend cut 100x to 1e5 and an independent seed base, 512 cells, 10 reps -- not a deliverable" ;;
  prod2s) SCRIPT=prod2s.slurm; W=2s; NT=512; IDX="$(seq 3 3 1536)";
          NOTE="M1 WF CONVERGENCE CONTROL for prod2: F2 with itend cut 100x to 1e6 and an independent seed base, 512 cells, 10 reps -- not a deliverable" ;;
  *) echo "usage: bash submit.sh {probe1|prod1|probe2|prod2|prod1s|prod2s}"; exit 1 ;;
esac
TAG="$1"
# A LIVE PROBE TASK IS A FILE COLLISION, NOT A DUPLICATE.  The five probe
# indices are members of the production array, and the array's idempotence
# guard skips a task only once it is COMPLETE.  Submitting production while the
# probe still runs would start a second process writing run<W>/<isl>,
# run<W>/h<isl> and run<W>/w<isl> for those five cells at the same time as the
# first -- interleaved output, and no error anywhere to say so.
if [ "${1#prod}" != "$1" ] && [ -f "JOBID_probe$W" ]; then
  live=$(squeue -j "$(cat JOBID_probe$W)" -h -o '%i' 2>/dev/null | wc -l | tr -d ' ')
  if [ "${live:-0}" -gt 0 ]; then
    echo "REFUSING: $live task(s) of probe $(cat JOBID_probe$W) are still in the queue."
    echo "  They share run$W/ with $TAG and would be written twice, concurrently."
    echo "  Wait for the probe (that is the point of a probe: read the rate first)."
    exit 1
  fi
fi
[ -x "sf$W.x" ] || { echo "sf$W.x not built -- run: bash compile.sh"; exit 1; }
[ -f "$SCRIPT" ] || { echo "$SCRIPT not found"; exit 1; }

# the ledger's task count must be the script's own, not a number typed twice
spec=$(awk -F= '/^#SBATCH --array=/{print $2}' "$SCRIPT")
n=$(echo "$IDX" | wc -w)
[ "$n" -eq "$NT" ] || { echo "internal: $TAG index set has $n entries, NT says $NT"; exit 1; }
nspec=$(python3 - "$spec" <<'PY'
import sys
s = sys.argv[1]
t = 0
for part in s.split(','):
    if '-' in part:
        rng, _, st = part.partition(':')
        a, b = rng.split('-')
        st = int(st or 1)
        t += len(range(int(a), int(b) + 1, st))
    else:
        t += 1
print(t)
PY
)
[ "$nspec" -eq "$NT" ] || { echo "internal: --array=$spec is $nspec tasks, NT says $NT"; exit 1; }
echo "$SCRIPT: --array=$spec, $NT tasks, run$W/, sf$W.x"

mkdir -p "run$W" log
cp -f games.dat "run$W/.games.dat.new" && mv -f "run$W/.games.dat.new" "run$W/games.dat"
echo "$IDX" | tr ' ' '\n' | grep -v '^$' > "IDX_$TAG"

jid=$(sbatch --parsable "$SCRIPT")
echo "$jid" > "JOBID_$TAG"
printf '%s\tDiskM1WF\tmw_%s\t%s\t%s\t%s\n' \
       "$(date +%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
