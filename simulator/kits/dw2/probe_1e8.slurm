#! /bin/bash
# dw2 / vor_1e8: the 512-POINT SUNFLOWER at N = 100, beta = 3, u = 1e-4,
# eps = 1e-4, itend = 1e8 (1e4 substitutions per replicate).
#
# Martin, 2026-09-07: "for F2 in FiguresFinal produce the same as for F1 but
# use N=100, beta=3, and u=10^(-4)."
#
# WHY THIS IS THE INTERESTING RUN.  N*u = 0.01, so a mutant arrives once every
# 100 generations against a fixation-or-loss time of order N = 100 generations:
# the population is monomorphic almost all the time and the process is a
# sequential-fixation walk.  That is the Imhof-Nowak regime CL1/DiskM2IN solves
# exactly at the SAME N and beta.  So this campaign is not just a second
# parameter point -- it is an independent simulation of the process that
# project computes, on the same 512 games, by a different code.  Where the two
# agree, both are validated; where they part, the gap is u = 1e-4 against
# u -> 0 and nothing else.
#
# THE GAMES ARE dw1's games.dat, UNCHANGED, so the task decode is unchanged:
#   ie = mod(isl-1,3)+1,  ig = (isl-1)/3+1;  eps = 1e-4 is ie = 3
#   rows 456-967 are the sunflower -> isl 1368-2901 step 3;  ipt = (isl-1368)/3
# Rows 1-455 (donation ray, polar grid, square) are present in the file and
# are NOT part of this campaign.
#
# THE BINARY IS PER RUN LENGTH.  itend is a compile-time parameter, so this
# script runs sf_1e8.x and no other; bash compile.sh 1e8 builds it.
#
# RATE.  Measured locally (gfortran -O2, 1 replicate, 1e6 generations, cell
# V_p000, eps = 1e-4): 2.99 s at N = 100 against 26.48 s at N = 1000, so the
# cost is linear in N x itend with a small fixed overhead.  Scaled to 10
# replicates of 1e8 that is 49.8 min (1e8) or 8.3 h (1e9) per cell LOCALLY.
# The Cannon rate is NOT this number -- this family has run 1.0x to 1.6x the
# local rate -- and is measured by the probe before the full array is sized.
#SBATCH -p shared
#SBATCH -J DiskM2WF.dw2vor_1e8
#SBATCH --comment=DiskM2WF
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_p1e8_%a.txt
#SBATCH -e log/e_p1e8_%a.txt
#SBATCH --array=1368,2892,2895,2898,2901

module load intel/25.2.1-fasrc01
cd run_1e8 || { echo "run_1e8/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run_1e8/games.dat missing -- use submit.sh"; exit 1; }
# idempotent, and it takes BOTH products to count as done -- dw1's guard
# verbatim.  sf.f flushes the summary after every replicate but writes the
# 65536-line histogram in one burst after the last, so a 10-line summary does
# NOT imply a finished h-file.
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
