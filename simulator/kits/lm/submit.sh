#!/bin/bash
# Submit one lm array: stage the game list in run_<g>/, capture the array id with --parsable into JOBID_<tag>_<g>, write
# IDX_<tag>_<g>, and append one line to the cross-project ledger ~/jobs.tsv.     bash submit.sh {probe|prod} {g0|g01|g05}
set -e
TAG=$1; G=$2
case "$G" in g0|g01|g05) ;; *) echo "usage: bash submit.sh {probe|prod} {g0|g01|g05}"; exit 1 ;; esac
case "$G" in g0) NUV=0 ;; g01) NUV=0.1 ;; g05) NUV=0.5 ;; esac
case "$TAG" in
  probe) SPEC="1620,2148,2334,2538"; IDX="1620 2148 2334 2538"; NT=4
         NOTE="lm probe, local mutation nu=$NUV (N=1000 beta=100 mu=1e-2 eps=1e-4, itend 1e7, 10 reps); 4 cells: PD/W 110-led, SH/S, deep PD/W only-the-eight, PD above switch" ;;
  prod)  SPEC="1368-2901:3"; IDX="$(seq 1368 3 2901)"; NT=512
         NOTE="lm 512-point sunflower, local mutation nu=$NUV (N=1000 beta=100 mu=1e-2 eps=1e-4, itend 1e7, 10 reps)" ;;
  *) echo "usage: bash submit.sh {probe|prod} {g0|g01|g05}"; exit 1 ;;
esac
# any live array of this g (probe or prod) writes into the same run_<g>/: refuse, and refuse if the check itself fails
for P in "JOBID_probe_$G" "JOBID_prod_$G"; do
  [ -f "$P" ] || continue
  st=$(sacct -j "$(cat "$P")" -X -n -o State) || { echo "sacct failed for $(cat "$P") -- not submitting"; exit 1; }
  if echo "$st" | grep -Eq 'PENDING|RUNNING|REQUEUED|SUSPENDED|RESIZING|CONFIGURING'; then
    echo "REFUSING: array $(cat "$P") ($P) still has live tasks; it shares run_$G/."; exit 1
  fi
done
[ -x "sf_$G.x" ] || { echo "sf_$G.x not built -- run: bash compile.sh $G"; exit 1; }
grep -q "data itv  /10000000/" "sf_$G.f" || { echo "sf_$G.x was not built for itend 1e7 -- rebuild: bash compile.sh $G"; exit 1; }
n=$(echo "$IDX" | wc -w)
[ "$n" -eq "$NT" ] || { echo "internal: $TAG index set has $n entries, NT says $NT"; exit 1; }
mkdir -p "run_$G" log
cp -f games.dat "run_$G/.games.dat.new" && mv -f "run_$G/.games.dat.new" "run_$G/games.dat"
echo "$IDX" | tr ' ' '\n' | grep -v '^$' > "IDX_${TAG}_$G"
[ -f "JOBID_${TAG}_$G" ] && cat "JOBID_${TAG}_$G" >> "JOBID_${TAG}_$G.history"
jid=$(sbatch --parsable --array="$SPEC" --export=ALL,G="$G" \
      -o "log/o_${TAG}_${G}_%A_%a.txt" -e "log/e_${TAG}_${G}_%A_%a.txt" lm.slurm)
echo "$jid" > "JOBID_${TAG}_$G"
printf '%s\tPartnersRivals1\tlm_%s_%s\t%s\t%s\t%s\n' "$(date +%F)" "$TAG" "$G" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted lm.slurm G=$G as array $jid ($NT tasks, --array=$SPEC); JOBID_${TAG}_$G and IDX_${TAG}_$G written, ledger appended"
