#! /bin/bash
# dw4 / prod at itend = 1e7: the WF process with pairwise comparison at
# N = 1000, beta = 3, u = 1e-2: weak selection, frequent mutation, eps = 1e-4, on the 512-point Fermat sunflower of Figures 3 and 4
# of CL1/PartnersRivals (the same games.dat and task decode as DiskM2WF's dw1/dw2).
#
# WHY. Figure 4's mutation rate with Figure 3's selection strength. Mutants are always present (N*u = 10) but beta*mu = 3e-2, so selection should not register the order-mu tax and the partners should again prevail over the friendly rivals, in the Prisoner's Dilemma wedge and in the wedge S.
#
# Task decode (dw1's): ie = mod(isl-1,3)+1 (eps = 1e-4 is ie = 3); ig = (isl-1)/3+1;
# the sunflower is rows 456-967 -> isl 1368-2901 step 3; ipt = (isl-1368)/3.
#SBATCH -p shared
#SBATCH -J PartnersRivals.dw4v7
#SBATCH --comment=PartnersRivals
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_v7_%a.txt
#SBATCH -e log/e_v7_%a.txt
#SBATCH --array=1368-2901:3

module load intel/25.2.1-fasrc01
cd run_1e7 || { echo "run_1e7/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run_1e7/games.dat missing -- use submit.sh"; exit 1; }
# idempotent: a task counts as done only with 10 replicate lines AND a complete histogram
isl=$SLURM_ARRAY_TASK_ID
lines=0
[ -f "$isl" ] && lines=$(wc -l < "$isl")
hdone=0
if [ -f "h$isl" ]; then
  nd=$(awk '/^# distinct/{print $3; exit}' "h$isl")
  nc=$(grep -vc '^#' "h$isl") || nc=0
  [ -n "$nd" ] && [ "$nc" -eq "$nd" ] && hdone=1
fi
if [ "$lines" -ge 10 ] && [ "$hdone" -eq 1 ]; then
  echo "task $isl already complete (10 replicate lines + $nd-state histogram), skipping"
  exit 0
fi
../sf_1e7.x $isl
