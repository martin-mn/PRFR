#! /bin/bash
# dw1 / disk_e4: the disk block at eps = 1e-4 ONLY -- the stride-3 subarray
#
# Martin narrowed the study on 2026-09-03 to u = 1e-2 (this kit) and
# eps = 1e-4, so the disk block is one task per game, not three.
#
# One task = one (game, eps) cell = 10 replicates of 10^7 generations,
# second half sampled, so its h-file IS the cell's summed 65536-state
# abundance histogram and nothing needs summing downstream.
#
# Task decode, game OUTERMOST:  ie = mod(isl-1,3)+1,  ig = (isl-1)/3+1
#   games.dat rows   1- 19  DONwf3_c*   donation ray, DonationWF's scale
#                   20- 38  DONlam1_c*  the same 19 games at NE's scale
#                   39-166  D_a*_r*     the 16 x 8 disk grid
#                  167-455  Q_i*_j*     the 17 x 17 square
# eps = 1e-4 is ie = 3, i.e. isl = 3*ig exactly, so rows 1..166 are
# isl = 3, 6, ..., 498.  Endpoints checked against the Fortran decode and
# against the probe's own h-file headers: isl 3 -> row 1 DONwf3_c0.05,
# isl 498 -> row 166 D_a15_r8_HA, isl 501 -> row 167 Q_i00_j00 (the square,
# which is prod_sq.slurm's business, not this one's).
#
# 166 tasks.  Measured rate from probe 44143919: 64.9-70.9 min per eps=1e-4
# cell, peak RSS 29.5 MB.
#SBATCH -p shared
#SBATCH -J DiskM2WF.dw1disk_e4
#SBATCH --comment=DiskM2WF
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_de4_%a.txt
#SBATCH -e log/e_de4_%a.txt
#SBATCH --array=3-498:3

module load intel/25.2.1-fasrc01
cd run || { echo "run/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run/games.dat missing -- use submit.sh"; exit 1; }
# idempotent, and it takes BOTH products to count as done.  sf.f flushes the
# summary file after every replicate but writes the 65536-line histogram in
# one burst after the last one, so a 10-line summary does NOT imply a finished
# h-file: a task killed in that window would otherwise be skipped for ever and
# leave a permanent hole that verify.sh would report as complete.
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
../sf.x $isl
