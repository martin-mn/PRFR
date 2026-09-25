#! /bin/bash
# dw3 / probe at itend = 1e8: the WF process with pairwise comparison at
# N = 1000, beta = 100, u = 1e-4: strong selection, rare mutation, eps = 1e-4, on the 512-point Fermat sunflower of Figures 3 and 4
# of CL1/PartnersRivals (the same games.dat and task decode as DiskM2WF's dw1/dw2).
#
# WHY. Figure 4's selection strength with Figure 3's mutation rate. The argument of the paper says the order-mu tax on strategies that can be outperformed is what hands games to the friendly rivals, so with mu = 1e-4 (beta*mu = 1e-2) the Prisoner's Dilemma wedge should return to the partners, and the wedge S should be shared by partners and friendly rivals in proportion to their numbers, as in Figure 3.
#
# Task decode (dw1's): ie = mod(isl-1,3)+1 (eps = 1e-4 is ie = 3); ig = (isl-1)/3+1;
# the sunflower is rows 456-967 -> isl 1368-2901 step 3; ipt = (isl-1368)/3.
#SBATCH -p shared
#SBATCH -J PartnersRivals.dw3p8
#SBATCH --comment=PartnersRivals
#SBATCH -t 1200
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_p8_%a.txt
#SBATCH -e log/e_p8_%a.txt
#SBATCH --array=1368,2892,2895,2898,2901,1902,2436,2664

module load intel/25.2.1-fasrc01
cd run_1e8 || { echo "run_1e8/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run_1e8/games.dat missing -- use submit.sh"; exit 1; }
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
../sf_1e8.x $isl
