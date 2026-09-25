#!/bin/bash
# Completion of a c2 array, established per task from sacct -- never from squeue -u, whose output spans every
# project submitting under this user.    bash verify.sh {probe_e4|prod_e4}
# A cell counts as complete only with all 10 replicate lines, a histogram of ndist lines AND an r-file of exactly
# 10 x 524288 bytes (the per-replicate counts, written after each replicate).
set -e
RUN=run_1e7
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
echo "--- cells of THIS array, complete = 10 replicate lines + full histogram + full r-file ---"
I="IDX_$1"
[ -f "$I" ] || { echo "$I not found"; exit 1; }
ndone=0; nshort=0; nnoh=0; nnor=0; nmiss=0; miss=""
while read -r isl; do
  [ -n "$isl" ] || continue
  if [ ! -f "$RUN/$isl" ]; then nmiss=$((nmiss+1)); miss="$miss $isl"; continue; fi
  Lr=$(wc -l < "$RUN/$isl")
  nd=""; nc=0
  if [ -f "$RUN/h$isl" ]; then
    nd=$(awk '/^# distinct/{print $3; exit}' "$RUN/h$isl")
    nc=$(grep -vc '^#' "$RUN/h$isl") || nc=0
  fi
  rs=0; [ -f "$RUN/r$isl" ] && rs=$(stat -c %s "$RUN/r$isl")
  if [ "$Lr" -ge 10 ] && [ -n "$nd" ] && [ "$nc" -eq "$nd" ] && [ "$rs" -eq 5242880 ]; then
    ndone=$((ndone+1))
  elif [ "$Lr" -lt 10 ]; then
    nshort=$((nshort+1)); miss="$miss $isl(${Lr}rep)"
  elif [ -z "$nd" ] || [ "$nc" -ne "$nd" ]; then
    nnoh=$((nnoh+1)); miss="$miss $isl(hist $nc/${nd:-0})"
  else
    nnor=$((nnor+1)); miss="$miss $isl(rfile ${rs}B)"
  fi
done < "$I"
echo "$ndone complete of $(wc -l < "$I") in this array"
[ "$nmiss" -gt 0 ] && echo "  $nmiss not started"
[ "$nshort" -gt 0 ] && echo "  $nshort short on replicates"
[ "$nnoh" -gt 0 ] && echo "  $nnoh have 10 replicates but no complete histogram -- RESUBMIT THESE"
[ "$nnor" -gt 0 ] && echo "  $nnor have histogram but a short r-file -- RESUBMIT THESE"
[ -n "$miss" ] && echo " incomplete:$miss"
exit 0
