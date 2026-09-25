#!/bin/bash
# Completion of a dw4 array, established per task from sacct.  Never from
# squeue -u: that output spans every project submitting under this user.
#   bash verify.sh {probe7|probe8|vor7|vor8}
#
# The run directory is per RUN LENGTH -- run_1e8/ or run_1e9/ -- because
# itend is a compile-time parameter and the two are different campaigns.
# The tag decides which: *8 -> run_1e8, *9 -> run_1e9.
#
# Two things this reports that the first version did not:
#
#  * the cell loop is restricted to THIS array's own index set (IDX_<tag>,
#    written by submit.sh), not to every numeric file in run/.  Three arrays
#    share run/, so a whole-directory count answers no question anyone asked --
#    a completely failed disk_e4 could still show a large count if sq had
#    finished.
#  * a cell counts as complete only if it has all 10 replicate lines AND a
#    histogram of ndist lines.  sf.f flushes the summary after every replicate
#    but writes the 65536-line h-file in one burst at the end, so those are
#    genuinely different facts, and the h-file is the deliverable.
set -e
case "$1" in
  *7) RUN=run_1e7 ;;
  *8) RUN=run_1e8 ;;
  *) echo "usage: bash verify.sh {probe7|probe8|vor7|vor8}"; exit 1 ;;
esac
J="JOBID_$1"; [ -f "$J" ] || { echo "$J not found -- this kit has no record of that array"; exit 1; }
jid=$(cat "$J")
echo "array $jid"
echo "--- tasks that are not COMPLETED (empty is clean) ---"
sacct -j "$jid" --format=JobID,State,ExitCode,Elapsed -X --noheader | awk '$2 != "COMPLETED"'
echo "--- core-hours, and per-task wall time ---"
sacct -j "$jid" --format=Elapsed,AllocCPUS -X --noheader | awk \
 '{split($1,a,"[:-]"); if (length(a)==4) s=((a[1]*24+a[2])*60+a[3])*60+a[4]; else s=(a[1]*60+a[2])*60+a[3];
   t+=s*$2; n++; if (s>mx) mx=s; if (mn=="" || s<mn) mn=s}
  END{if(n) printf "%.1f core-h over %d tasks; wall %.1f-%.1f min, mean %.1f\n", t/3600, n, mn/60, mx/60, t/60/n;
      else print "no accounting rows yet"}'
echo "--- cells of THIS array, complete = 10 replicate lines + full histogram ---"
I="IDX_$1"
if [ ! -f "$I" ]; then
  echo "$I not found -- submitted by an older submit.sh; cannot scope the count to this array"
  exit 0
fi
ndone=0; nshort=0; nnoh=0; nmiss=0; miss=""
while read -r isl; do
  [ -n "$isl" ] || continue
  if [ ! -f "$RUN/$isl" ]; then nmiss=$((nmiss+1)); miss="$miss $isl"; continue; fi
  L=$(wc -l < "$RUN/$isl")
  nd=""; nc=0
  if [ -f "$RUN/h$isl" ]; then
    nd=$(awk '/^# distinct/{print $3; exit}' "$RUN/h$isl")
    nc=$(grep -vc '^#' "$RUN/h$isl") || nc=0
  fi
  if [ "$L" -ge 10 ] && [ -n "$nd" ] && [ "$nc" -eq "$nd" ]; then
    ndone=$((ndone+1))
  elif [ "$L" -lt 10 ]; then
    nshort=$((nshort+1)); miss="$miss $isl(${L}rep)"
  else
    nnoh=$((nnoh+1)); miss="$miss $isl(hist $nc/${nd:-0})"
  fi
done < "$I"
echo "$ndone complete of $(wc -l < "$I") in this array"
[ "$nmiss" -gt 0 ] && echo "  $nmiss not started"
[ "$nshort" -gt 0 ] && echo "  $nshort short on replicates"
[ "$nnoh" -gt 0 ] && echo "  $nnoh have 10 replicates but no complete histogram -- RESUBMIT THESE"
[ -n "$miss" ] && echo " incomplete:$miss"
exit 0
