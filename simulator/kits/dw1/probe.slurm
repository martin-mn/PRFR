#! /bin/bash
# Rate probe for dw1.  A task is a whole cell -- 10 replicates of 10^7
# generations -- so this measures the real per-task wall time directly.
#
# Six tasks spanning what could set the rate.  What actually sets it is the
# payoff-cache hit rate, which falls as the population gets more diverse, so
# large eps is the slow corner; and, new here, the payoff SCALE, which sets
# how often the Fermi rule saturates and the population collapses onto a few
# strategies.  Measured locally (gfortran, 13 games, 10^6 generations) the
# rate was flat to +-10% across the whole plane, 35-43 s per 10^6; this probe
# is what establishes the true Cannon rate.  Never rescale the local number.
#
#   isl   37 -> DONwf3_c0.65  eps 1e-2   Donation scale, the diverse corner
#   isl   39 -> DONwf3_c0.65  eps 1e-4   the wf3 comparison cell
#   isl   96 -> DONlam1_c0.65 eps 1e-4   the same game at NE's scale
#   isl  138 -> D_a00_r8      eps 1e-4   the disk's outer ring, |u| = 15.5
#   isl  501 -> Q_i00_j00     eps 1e-4   the square corner (-8,-8), Stag Hunt
#   isl 1365 -> Q_i16_j16     eps 1e-4   the square corner (+8,+8), Snowdrift
#
# decode: ie = mod(isl-1,3)+1, ig = (isl-1)/3+1  (game OUTERMOST)
#
# NOTE, as in wf3: this probe uses the PRODUCTION binary and writes into the
# same run/, so its six tasks are real production output on the right seeds
# and prod_*.slurm's line-count guard will skip them once FINISHED.  That
# guard does not protect a task still running -- do not submit production
# until the probe has finished, or submit production with these six indices
# excluded.
#SBATCH -p shared
#SBATCH -J DiskM2WF.dw1probe
#SBATCH --comment=DiskM2WF
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/p_out_%a.txt
#SBATCH -e log/p_err_%a.txt
#SBATCH --array=37,39,96,138,501,1365

module load intel/25.2.1-fasrc01
cd run || { echo "run/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run/games.dat missing -- use submit.sh"; exit 1; }
/usr/bin/time -v ../sf.x $SLURM_ARRAY_TASK_ID
