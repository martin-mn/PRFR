#! /bin/bash
# dw1 / vor_e4_rest: the sunflower MINUS the five cells the probe already has.
#
# Identical to prod_vor_e4.slurm except for the array spec.  The probe's five
# indices are, by luck of how they were chosen (the innermost point and the
# farthest in each quadrant), exactly the FIRST index and the LAST FOUR:
#     1368  and  2892, 2895, 2898, 2901
# so removing them leaves one contiguous stride range, 1371-2889:3 = 507
# tasks, and 507 + 5 = 512.  Seeds are 8000000 + (isl-1)*10 + irep, a
# function of isl alone, so the probe's outputs ARE the production outputs
# for those five cells -- nothing is approximated by leaving them out.
#
# Use this when the probe is still running: submit.sh refuses vor_e4 then,
# because both would write run/<isl> for the same five cells at once.
#
# dw1 / the 512-POINT SUNFLOWER (Voronoi) disk at eps = 1e-4
#
# Martin, 2026-09-04: "for simulating WF on the disk, could you also use the
# Voronoi tesselation of the project CL/BinM2Ev.  512 cells."
#
# THE GAMES ARE ca6's, VERBATIM.  ../../Ref/binm2ev_ca6_points.txt is a copy of
# CL/BinM2Ev/cannon/ca6/points.txt: a Fermat (sunflower) spiral of 512 points
# even on the k = 4 disk, pulled back through the exact radial inverse
# r = k*rho/sqrt(1-rho^2), snapped to 1/1024 (exact as a decimal AND as a
# double) and nudged clear of all 280 lines of the exact Nash arrangement.
# Same strategy space, same (R,S,T,P) = (1,u,1+v,0), same k, so this campaign
# and ca6 are the SAME 512 GAMES in opposite process regimes:
#     ca6       N =  100, mu = 1e-4, eps -> 0 limit payoffs, 20 replicates
#     this      N = 1000, u  = 1e-2, eps = 1e-4,             10 replicates
#
# WHY A SUNFLOWER AND NOT THE 16x8 POLAR GRID.  The polar grid is even in
# (angle, sqrt-radius), not on the disk: 16 fat wedges at the rim, 16 slivers
# at the centre.  The sunflower's Voronoi cells are near-hexagonal and
# near-equal in area, so every game gets its share of the ink.  It also
# reaches FURTHER -- r = 38.2 (rho = 0.9946, 99.0% of the disk by area)
# against the polar grid's r = 15.5 (rho = 0.968).  This block ADDS to the
# 16x8 grid; it does not replace it.
#
# Task decode, game OUTERMOST:  ie = mod(isl-1,3)+1,  ig = (isl-1)/3+1
#   games.dat rows   1- 19  DONwf3_c*   donation ray, DonationWF's scale
#                   20- 38  DONlam1_c*  the same 19 games at NE's scale
#                   39-166  D_a*_r*     the 16 x 8 polar disk grid
#                  167-455  Q_i*_j*     the 17 x 17 square
#                  456-967  V_p*        the 512-point sunflower  <- this block
# Appending left rows 1-455 BYTE-IDENTICAL to the file that ran arrays
# 44155859 and 44155870 (md5 of the first 455 rows checked against Cannon), so
# no existing task index moved.  eps = 1e-4 is ie = 3, i.e. isl = 3*row, so
# row 456 -> isl 1368 and row 967 -> isl 2901.  ipt = (isl - 1368)/3.
#
# 507 tasks.  Rate from probe (see README): the eps=1e-4 rate is flat in the
# game, 64.9-70.9 min per cell across the donation ray, the polar outer ring
# and both square corners, and the sunflower probe extends that to r = 38.
# The far games do NOT overflow: Fermi is cut at |beta*dpi/(2m)| = thr = 25 in
# sf.f, so an argument of ~3800 saturates rather than traps, and
# Emax = max(1, (1+u+v)/2) >= 1 > 0 everywhere.
#SBATCH -p shared
#SBATCH -J DiskM2WF.dw1vor_rest
#SBATCH --comment=DiskM2WF
#SBATCH -t 240
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_vr_%a.txt
#SBATCH -e log/e_vr_%a.txt
#SBATCH --array=1371-2889:3

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
