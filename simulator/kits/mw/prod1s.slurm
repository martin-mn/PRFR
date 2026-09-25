#! /bin/bash
# mw / prod1s: the Wright-Fisher process over the 16 BINARY MEMORY-ONE
# strategies at the 512 Voronoi cells of BinM2Ev ca6's Fermat sunflower,
# eps = 1e-4.  The production run behind the memory-one counterpart of Figures 3 and 4.
#
#     N = 1000, m = 1, beta = 100, u = 1e-2, itend = 1e5 (1e3 substitutions), 10 replicates
#
# WHY.  PartnersRivals/FinalFigures draws the seven atoms of (efficient, nash,
# competitive) over this disk for the 65536 binary memory-two strategies:
# Figure 3 / Figure 4 from DiskM2WF's run F1 (N = 1000) and SI Figures 2 / 3
# from its run F2 (N = 100).  This campaign is those four figures' memory-one
# counterpart: the SAME 512 games, the SAME process and the SAME run length,
# with the strategy space cut from 65536 to 16.
#
# THE GAMES ARE dw1's, VERBATIM.  games.dat is rows 456-967 of
# DiskM2WF/Opt/games.dat -- ca6's own sunflower points, a Fermat spiral even on
# the k = 4 disk, snapped to 1/1024 and nudged clear of the exact Nash
# arrangement -- copied rather than regenerated, so the maps overlay cell for
# cell with Figures 3 and 4.
#
#
# WHAT THIS ARRAY IS FOR.  It is not a deliverable: it is the convergence
# control for prod1.  The run length of F1 and F2 is inherited from the
# MEMORY-TWO figures, where the process explores 65536 strategies; with 16 it
# is far longer than the page can resolve.  The full-length probe put the
# between-replicate sd of the dominant strategy's share at 6e-5 (cell 3) and
# 1.0e-4 (cell 1533), and Monte Carlo error goes as 1/sqrt(itend), so cutting
# itend 100x should cost about one decimal place -- ~1e-3 on a share, against
# Figure 3's linear 0..1 colour scale and Figure 4's 5.2 decades of log10.
#
# This array tests that at all 512 cells rather than extrapolating from two.
# Its OWN 10 replicates per cell measure its error where it runs, so a cell
# with a slow metastable mode announces itself as replicate disagreement
# instead of hiding inside an average.  The seed base is independent of
# prod1's (12000000 / 13000000 against 10000000 / 11000000), so the
# comparison measures the error of the estimate and not the correlation of a
# shared sample path.
#
# Output goes to run1s/, never run1/, so the deliverable cannot be
# contaminated by a control.
# Task decode, GAME OUTERMOST, is dw1's unchanged:
#     ie = mod(isl-1,3) + 1        eps = (1e-2, 1e-3, 1e-4)(ie)
#     ig = (isl-1)/3 + 1           the row of games.dat, = ipt + 1
# so eps = 1e-4 is the stride-3 subarray and cell ipt is task 3*ipt + 3:
# ipt 0 -> isl 3, ipt 511 -> isl 1536.  Keeping dw1's decode keeps its verified
# index arithmetic; the eps = 1e-2 and 1e-3 layers can be added later without
# moving a single existing index.
#
# The far games do not overflow: Fermi is cut at |beta*dpi/(2m)| = thr = 25 in
# sf1.f, so a large argument saturates rather than traps, and
# Emax = max(1, (1+u+v)/2) >= 1 > 0 everywhere.
#SBATCH -p shared
#SBATCH -J DiskM1WF.mwprod1s
#SBATCH --comment=DiskM1WF
#SBATCH -t 30
#SBATCH -c 1
#SBATCH --mem=300
#SBATCH -o log/o_r1s_%a.txt
#SBATCH -e log/e_r1s_%a.txt
#SBATCH --array=3-1536:3

module load intel/25.2.1-fasrc01
cd run1s || { echo "run1s/ missing -- use submit.sh, which stages games.dat"; exit 1; }
[ -f games.dat ] || { echo "run1s/games.dat missing -- use submit.sh"; exit 1; }
# Idempotent, and it takes BOTH products to count as done.  sf.f flushes the
# summary file after every replicate but writes the histogram in one burst
# after the last one, so a 10-line summary does NOT imply a finished h-file:
# a task killed in that window would otherwise be skipped for ever and leave a
# permanent hole that verify.sh would report as complete.  (dw1's lesson,
# kept although the histogram here is 16 lines rather than 65536.)
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
../sf1s.x $isl
