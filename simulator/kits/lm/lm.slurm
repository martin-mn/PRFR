#! /bin/bash
# lm: one cell (a sunflower game at eps = 1e-4, 10 replicates of 1e7 generations) of the local-mutation runs,
# N = 1000, beta = 100, mu = 1e-2, global fraction pglob = G (g0 | g01 | g05), set by submit.sh via --export.
# Task decode (f1's): ie = mod(isl-1,3)+1, ig = (isl-1)/3+1; sunflower games 456-967, ipt = ig-456; this is the ie = 3 stride.
#SBATCH -p shared
#SBATCH -J PartnersRivals1.lm
#SBATCH --comment=PartnersRivals1
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300

module load intel/25.2.1-fasrc01
[ -n "$G" ] || { echo "G not set -- use submit.sh"; exit 1; }
cd "run_$G" || { echo "run_$G/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run_$G/games.dat missing -- use submit.sh"; exit 1; }
# idempotent: a task counts as done only with 10 replicate lines, a complete histogram AND a full r-file
isl=$SLURM_ARRAY_TASK_ID
lines=0
[ -f "$isl" ] && lines=$(wc -l < "$isl")
hdone=0
if [ -f "h$isl" ]; then
  nd=$(awk '/^# distinct/{print $3; exit}' "h$isl")
  nc=$(grep -vc '^#' "h$isl") || nc=0
  [ -n "$nd" ] && [ "$nc" -eq "$nd" ] && hdone=1
fi
rdone=0
[ -f "r$isl" ] && [ "$(stat -c %s "r$isl")" -eq 5242880 ] && rdone=1
if [ "$lines" -ge 10 ] && [ "$hdone" -eq 1 ] && [ "$rdone" -eq 1 ]; then
  echo "task $isl already complete (10 replicate lines, $nd-state histogram, 10 replicate count blocks), skipping"
  exit 0
fi
"../sf_$G.x" $isl
