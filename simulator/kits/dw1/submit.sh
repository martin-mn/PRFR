#!/bin/bash
# Submit one dw1 array, doing the three things the global protocol requires in
# a single step: stage the game list, capture the array id with --parsable into
# a JOBID file, and append one line to the cross-project ledger ~/jobs.tsv.
#
#   bash submit.sh probe      6 tasks, the rate probe
#   bash submit.sh disk_e4  166 tasks, the disk block at eps = 1e-4 only
#   bash submit.sh sq       289 tasks, the square at eps = 1e-4
#   bash submit.sh disk     498 tasks, the disk block at ALL THREE eps
#   bash submit.sh vor_probe  5 tasks, the sunflower rate probe
#   bash submit.sh vor_e4   512 tasks, the 512-point sunflower at eps = 1e-4
#
# `disk_e4` + `sq` = 455 tasks = one cell per game at eps = 1e-4.  That is the
# narrowed campaign Martin asked for on 2026-09-03 (u = 1e-2, eps = 1e-4).
# `disk` is the wider original and is NOT part of it; because the task decode
# puts the game outermost, the eps = 1e-2 and 1e-3 layers can be added later
# without moving a single existing index.
#
# games.dat is staged into run/ by write-to-temp-then-rename, never by writing
# the live file in place: `cp -f` truncates its target first, and an array task
# starting in that instant would read a short or empty game list.  `mv` on the
# same filesystem is atomic, so a reader sees either the old file or the new
# one, and the two are identical anyway.  (`ln -sf` is worse still -- it
# unlinks before it links, so the file is briefly absent.)
set -e
case "$1" in
  probe)   SCRIPT=probe.slurm;        TAG=probe;   NT=6;   IDX="37 39 96 138 501 1365";
           NOTE="rate probe, 6 cells: DONwf3_c0.65 e2/e4, DONlam1_c0.65 e4, disk outer ring, both square corners" ;;
  disk_e4) SCRIPT=prod_disk_e4.slurm; TAG=disk_e4; NT=166; IDX="$(seq 3 3 498)";
           NOTE="disk block at eps=1e-4 ONLY (stride-3 subarray 3-498:3): 19 donation (DonationWF scale) + 19 donation (lam=1) + 16x8 disk grid, 10 reps of 1e7 gens" ;;
  sq)      SCRIPT=prod_sq.slurm;      TAG=sq;      NT=289; IDX="$(seq 501 3 1365)";
           NOTE="square 17x17 u,v=-8..8, eps=1e-4 only (stride-3 subarray 501-1365:3), 10 reps of 1e7 gens" ;;
  disk)    SCRIPT=prod_disk.slurm;    TAG=disk;    NT=498; IDX="$(seq 1 498)";
           NOTE="disk block: 19 donation (DonationWF scale) + 19 donation (lam=1) + 16x8 disk grid, 3 eps, 10 reps of 1e7 gens" ;;
  vor_probe) SCRIPT=probe_vor.slurm;    TAG=vor_probe; NT=5; IDX="1368 2892 2895 2898 2901";
           NOTE="sunflower rate probe, 5 cells: the innermost point and the farthest in each quadrant, r = 0.12 to 38.16" ;;
  vor_e4_rest) SCRIPT=prod_vor_e4_rest.slurm; TAG=vor_e4_rest; NT=507; IDX="$(seq 1371 3 2889)";
           NOTE="512-point sunflower MINUS the 5 probe cells (44383754 covers isl 1368,2892,2895,2898,2901 with identical seeds); eps=1e-4, 1371-2889:3" ;;
  vor_e4)  SCRIPT=prod_vor_e4.slurm;  TAG=vor_e4;  NT=512; IDX="$(seq 1368 3 2901)";
           NOTE="512-point Fermat sunflower on the k=4 disk, games COPIED VERBATIM from CL/BinM2Ev kit ca6 (Ref/binm2ev_ca6_points.txt); eps=1e-4 only (stride-3 subarray 1368-2901:3), 10 reps of 1e7 gens" ;;
  *) echo "usage: bash submit.sh {probe|disk_e4|sq|disk|vor_probe|vor_e4|vor_e4_rest}"; exit 1 ;;
esac
# A LIVE PROBE TASK IS A FILE COLLISION, NOT A DUPLICATE.  The 5 vor_probe
# indices are members of the vor_e4 array, and the array's idempotence guard
# skips a task only once it is COMPLETE.  Submitting vor_e4 while the probe is
# still running would start a second process writing run/<isl>, run/h<isl> and
# run/w<isl> for those five cells at the same time as the first -- interleaved
# output, and no error anywhere to say so.  So refuse, and name the fix.
if [ "$1" = "vor_e4" ] && [ -f JOBID_vor_probe ]; then
  live=$(squeue -j "$(cat JOBID_vor_probe)" -h -o '%i' 2>/dev/null | wc -l | tr -d ' ')
  if [ "${live:-0}" -gt 0 ]; then
    echo "REFUSING: $live task(s) of probe $(cat JOBID_vor_probe) are still in the queue."
    echo "  They share run/ with vor_e4 and would be written twice, concurrently."
    echo "  Either wait for the probe, or submit the other 507:"
    echo "      bash submit.sh vor_e4_rest      # --array=1371-2889:3"
    echo "  (the probe's own five ARE the other five -- same isl, same seeds)"
    exit 1
  fi
fi
[ -x sf.x ] || { echo "sf.x not built -- run: bash compile.sh"; exit 1; }
[ -f "$SCRIPT" ] || { echo "$SCRIPT not found"; exit 1; }

# the ledger's task count must be the script's, not a number typed twice
spec=$(awk -F= '/^#SBATCH --array=/{print $2}' "$SCRIPT")
n=$(echo "$IDX" | wc -w)
[ "$n" -eq "$NT" ] || { echo "internal: $TAG index set has $n entries, NT says $NT"; exit 1; }
echo "$SCRIPT: --array=$spec, $NT tasks"

mkdir -p run log
cp -f games.dat run/.games.dat.new && mv -f run/.games.dat.new run/games.dat
echo "$IDX" | tr ' ' '\n' | grep -v '^$' > "IDX_$TAG"

jid=$(sbatch --parsable "$SCRIPT")
echo "$jid" > "JOBID_$TAG"
printf '%s\tDiskM2WF\tdw1_%s\t%s\t%s\t%s\n' \
       "$(date +%F)" "$TAG" "$jid" "$NT" "$NOTE" >> ~/jobs.tsv
echo "submitted $SCRIPT as array $jid ($NT tasks); JOBID_$TAG and IDX_$TAG written, ledger appended"
