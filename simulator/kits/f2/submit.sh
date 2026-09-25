#!/bin/bash
# Submit one f2 array: stage the game list, capture the array id with --parsable into JOBID_<tag>, and append one
# line to the cross-project ledger ~/jobs.tsv.   bash submit.sh {probe_e4|prod_e4}
# seeded re-run of dw2, Figure 4's small-population run (N = 100, beta = 3, u = 1e-4, seeds 9000000+), eps = 1e-4.  The run length is compiled in (compile.sh 1e8 -> sf_1e8.x); the run directory is run_1e8/.
set -e
L=1e8
case "$1" in
  probe_e4) SCRIPT=probe_e4.slurm; TAG=probe_e4; NT=8; IDX="1368 2892 2895 2898 2901 1902 2436 2664";
      NOTE="f2 probe, seeded re-run of dw2, Figure 4's small-population run (N = 100, beta = 3, u = 1e-4, seeds 9000000+), eps = 1e-4, itend=1e8, ie=3 (e4); 8 cells: innermost, farthest per quadrant, 3 PD/W cells near the donation ray at r=3,6,9" ;;
  prod_e4)  SCRIPT=prod_e4.slurm;  TAG=prod_e4;  NT=512; IDX="$(seq 1368 3 2901)";
      NOTE="f2 512-point sunflower, seeded re-run of dw2, Figure 4's small-population run (N = 100, beta = 3, u = 1e-4, seeds 9000000+), eps = 1e-4, itend=1e8, ie=3 (e4), 10 reps (1368-2901:3)" ;;
  *) echo "usage: bash submit.sh {probe_e4|prod_e4}"; exit 1 ;;
esac
# a live probe task is a file collision with the production array of the same stride
case "$1" in
  prod_*) P=JOBID_probe_${1#prod_} ;;
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
printf '%s\tPartnersRivals\tf2_%s\t%s\t%s\t%s\n' "$(date +%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
