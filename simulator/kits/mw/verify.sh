#!/bin/bash
# Completion of an mw array, established PER TASK from sacct.  Never from
# squeue -u: that output spans every project submitting under this user, and an
# empty squeue means "not running", nothing more.
#   bash verify.sh {probe1|prod1|probe2|prod2}
#
# The cell loop is restricted to THIS array's own index set (IDX_<tag>, written
# by submit.sh), and a cell counts as complete only with all 10 replicate lines
# AND a histogram of ndist lines -- sf.f flushes the summary after every
# replicate but writes the histogram in one burst at the end, so those are
# different facts and the h-file is the deliverable.
set -e
J="JOBID_$1"; [ -f "$J" ] || { echo "$J not found -- this kit has no record of that array"; exit 1; }
jid=$(cat "$J")
# the s cases FIRST: "prod1s" also matches *1s, and would fall through to the
# error if the bare patterns were tested first
case "$1" in *1s) W=1s ;; *2s) W=2s ;; *1) W=1 ;; *2) W=2 ;;
             *) echo "cannot tell which run $1 is"; exit 1 ;; esac
echo "array $jid   (run$W/)"
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
[ -f "$I" ] || { echo "$I not found -- cannot scope the count to this array"; exit 0; }
ndone=0; nshort=0; nnoh=0; nmiss=0; miss=""
while read -r isl; do
  [ -n "$isl" ] || continue
  if [ ! -f "run$W/$isl" ]; then nmiss=$((nmiss+1)); miss="$miss $isl"; continue; fi
  L=$(wc -l < "run$W/$isl")
  nd=""; nc=0
  if [ -f "run$W/h$isl" ]; then
    nd=$(awk '/^# distinct/{print $3; exit}' "run$W/h$isl")
    nc=$(grep -vc '^#' "run$W/h$isl") || nc=0
  fi
  if [ "$L" -ge 10 ] && [ -n "$nd" ] && [ "$nc" -eq "$nd" ]; then ndone=$((ndone+1))
  elif [ "$L" -lt 10 ]; then nshort=$((nshort+1)); miss="$miss $isl(${L}rep)"
  else nnoh=$((nnoh+1)); miss="$miss $isl(hist $nc/${nd:-0})"; fi
done < "$I"
echo "$ndone complete of $(wc -l < "$I") in this array"
[ "$nmiss" -gt 0 ] && echo "  $nmiss not started"
[ "$nshort" -gt 0 ] && echo "  $nshort short on replicates"
[ "$nnoh" -gt 0 ] && echo "  $nnoh have 10 replicates but no complete histogram -- RESUBMIT THESE"
[ -n "$miss" ] && echo " incomplete:$miss"
exit 0
