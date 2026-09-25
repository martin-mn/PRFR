#!/bin/bash
# Submit one el array: stage the game list, capture the array id with --parsable into JOBID_<tag>, and append one
# line to the cross-project ledger ~/jobs.tsv.   bash submit.sh {probe_e5|prod_e5|probe_e3|prod_e3}
# error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3.  The run length is compiled in (compile.sh 1e8 -> sf_1e8.x); the run directory is run_1e8/.
set -e
L=1e8
case "$1" in
  probe_e5) SCRIPT=probe_e5.slurm; TAG=probe_e5; NT=8; IDX="1366 2890 2893 2896 2899 1900 2434 2662";
      NOTE="el probe, error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3, itend=1e8, ie=1 (e5); 8 cells: innermost, farthest per quadrant, 3 PD/W cells near the donation ray at r=3,6,9" ;;
  prod_e5)  SCRIPT=prod_e5.slurm;  TAG=prod_e5;  NT=512; IDX="$(seq 1366 3 2899)";
      NOTE="el 512-point sunflower, error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3, itend=1e8, ie=1 (e5), 10 reps (1366-2899:3)" ;;
  probe_e3) SCRIPT=probe_e3.slurm; TAG=probe_e3; NT=8; IDX="1367 2891 2894 2897 2900 1901 2435 2663";
      NOTE="el probe, error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3, itend=1e8, ie=2 (e3); 8 cells: innermost, farthest per quadrant, 3 PD/W cells near the donation ray at r=3,6,9" ;;
  prod_e3)  SCRIPT=prod_e3.slurm;  TAG=prod_e3;  NT=512; IDX="$(seq 1367 3 2900)";
      NOTE="el 512-point sunflower, error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3, itend=1e8, ie=2 (e3), 10 reps (1367-2900:3)" ;;
  *) echo "usage: bash submit.sh {probe_e5|prod_e5|probe_e3|prod_e3}"; exit 1 ;;
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
printf '%s\tPartnersRivals\tel_%s\t%s\t%s\t%s\n' "$(date +%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
