#! /bin/bash
# el / probe e3 at itend = 1e8: the WF process with pairwise comparison, error-rate series at N = 100, beta = 3, u = 1e-4 (Figure 4's small population), eps = 1e-5 and 1e-3,
# on the 512-point Fermat sunflower of Figures 4 and 5 of CL1/PartnersRivals (dw1/dw2's games.dat and task decode).
# Task decode: ie = mod(isl-1,3)+1; ig = (isl-1)/3+1; the sunflower is games 456-967 (gid 2000+ipt, ipt = ig-456).
# This array is the ie = 2 stride, tag e3.
#SBATCH -p shared
#SBATCH -J PartnersRivals.elp3
#SBATCH --comment=PartnersRivals
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_probee3_%a.txt
#SBATCH -e log/e_probee3_%a.txt
#SBATCH --array=1367,2891,2894,2897,2900,1901,2435,2663

module load intel/25.2.1-fasrc01
cd run_1e8 || { echo "run_1e8/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run_1e8/games.dat missing -- use submit.sh"; exit 1; }
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
../sf_1e8.x $isl
