#! /bin/bash
# dw1 / ident: IS THE REBUILT BINARY BIT-IDENTICAL TO THE ONE THAT RAN THE
#              455-CELL CAMPAIGN?
#
# The sunflower block took games.dat from 455 rows to 967, past sf.f's
# mgam = 512, so sf.f had to be recompiled with mgam = 2048.  mgam dimensions
# the game-list arrays only and appears nowhere in the dynamics, the PRNG
# stream or the payoff cache -- but "appears nowhere" is an argument, and the
# 512 new cells are going to be plotted on the same figures as the 455 old
# ones, so it is tested instead.
#
# Task 3 (row 1, DONwf3_c0.05) is rerun with the NEW binary in run_ident/, a
# directory of its own so the campaign's own h3 is never at risk, and the two
# h-files are compared byte for byte.  The h-file carries no timestamp -- its
# header is (isl, gid, tag, eps, umut, beta, payoffs, Emax, nper, itend, ie,
# ic) -- so `cmp` is exactly the right test, and it covers all 10 replicates,
# all 65536 states and the 5e10 samples behind them.
#
#   sbatch ident.slurm ; then:  cmp run_ident/h3 run/h3 && echo BIT-IDENTICAL
#
#SBATCH -p shared
#SBATCH -J DiskM2WF.dw1ident
#SBATCH --comment=DiskM2WF
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_ident.txt
#SBATCH -e log/e_ident.txt

module load intel/25.2.1-fasrc01
set -e
mkdir -p run_ident
cp -f games.dat run_ident/.games.dat.new && mv -f run_ident/.games.dat.new run_ident/games.dat
cd run_ident
rm -f 3 w3 h3
../sf.x 3
cd ..
if cmp -s run_ident/h3 run/h3; then
  echo "BIT-IDENTICAL: run_ident/h3 == run/h3, mgam 512 -> 2048 moved nothing"
else
  echo "*** DIFFERS *** the rebuild is NOT bit-identical; do not mix the blocks"
  cmp run_ident/h3 run/h3 || true
fi
