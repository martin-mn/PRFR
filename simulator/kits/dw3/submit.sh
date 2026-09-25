#!/bin/bash
# Submit one dw3 array: stage the game list, capture the array id with --parsable into
# JOBID_<tag>, and append one line to the cross-project ledger ~/jobs.tsv.
#   bash submit.sh probe7|probe8   8 tasks: the rate + convergence probe
#   bash submit.sh prod7|prod8    512 tasks: the sunflower
# Run lengths are separate campaigns in separate directories run_<L>/ (itend is compiled in).
set -e
case "$1" in
  probe7) L=1e7; SCRIPT=probe_1e7.slurm; TAG=probe7; NT=8; IDX="1368 2892 2895 2898 2901 1902 2436 2664";
          NOTE="dw3 probe, N = 1000, beta = 100, u = 1e-4: strong selection, rare mutation, eps=1e-4, itend=1e7; 8 cells: innermost, farthest per quadrant, 3 PD/W cells near the donation ray at r=3,6,10" ;;
  prod7)  L=1e7; SCRIPT=prod_1e7.slurm;  TAG=vor7;   NT=512; IDX="$(seq 1368 3 2901)";
          NOTE="dw3 512-point sunflower, N = 1000, beta = 100, u = 1e-4: strong selection, rare mutation, eps=1e-4, itend=1e7, 10 reps (1368-2901:3)" ;;
  probe8) L=1e8; SCRIPT=probe_1e8.slurm; TAG=probe8; NT=8; IDX="1368 2892 2895 2898 2901 1902 2436 2664";
          NOTE="dw3 probe, N = 1000, beta = 100, u = 1e-4: strong selection, rare mutation, eps=1e-4, itend=1e8; 8 cells: innermost, farthest per quadrant, 3 PD/W cells near the donation ray at r=3,6,10" ;;
  prod8)  L=1e8; SCRIPT=prod_1e8.slurm;  TAG=vor8;   NT=512; IDX="$(seq 1368 3 2901)";
          NOTE="dw3 512-point sunflower, N = 1000, beta = 100, u = 1e-4: strong selection, rare mutation, eps=1e-4, itend=1e8, 10 reps (1368-2901:3)" ;;
  *) echo "usage: bash submit.sh {probe7|probe8|prod7|prod8}"; exit 1 ;;
esac
# a live probe task is a file collision with the production array of the same run length
case "$1" in
  prod7) P=JOBID_probe7 ;;
  prod8) P=JOBID_probe8 ;;
  *) P= ;;
esac
if [ -n "$P" ] && [ -f "$P" ]; then
  live=$(squeue -j "$(cat "$P")" -h -o '%i' 2>/dev/null | wc -l | tr -d ' ')
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
echo "$IDX" | tr ' ' '\n' | grep -v '^$' > "IDX_$TAG"
jid=$(sbatch --parsable "$SCRIPT")
echo "$jid" > "JOBID_$TAG"
printf '%s\tPartnersRivals\tdw3_%s\t%s\t%s\t%s\n' "$(date +%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
