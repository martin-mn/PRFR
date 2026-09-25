#!/bin/bash
# smoke.sh -- build one kit's simulator locally with gfortran, run ONE game for a few generations, check the output
# files, pack them, and compare them with the reference run made on the author's machine.
#
#   bash smoke.sh                   kit f1, 20000 generations, task 1902 (the game gid 2178, (u,v) = (-2.014, 2.093))
#   bash smoke.sh <kit> [itend] [task]
#       <kit>   f1 f2 c1 c2 c3 c4 eh el dw1 dw2 dw3 dw4 lm   (memory two, 65536 strategies)
#               mw1 mw2                                      (memory one: kits/mw/sf1.f and sf2.f)
#       itend   the number of generations per replicate (the second half is sampled); the runs of the paper used
#               1e7 or 1e8.  The default 20000 takes about ten seconds at N = 1000.
#       task    the task index isl: memory two 1368 + 3*ipt (eps = 1e-4; eh/el: 1366 + 3*ipt for eps = 1e-5,
#               1367 + 3*ipt for eps = 1e-3); memory one 3 + 3*ipt.  The default is the game ipt = 178.
#   FC=... FFLAGS=... override the compiler (default gfortran -O2).  The cluster builds used
#   ifx -O3 -xHost -fp-model precise (see each kit's compile.sh).
#
# Everything is written to ./work/<kit>_<itend>_<task>/ next to this script.  The run itself is the kit's own
# source with ONE line changed, the run length `data itv /.../` (as each kit's compile.sh does); nothing else.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SIM=$(dirname "$HERE")
KIT=${1:-f1}; IT=${2:-20000}; FC=${FC:-gfortran}; FFLAGS=${FFLAGS:--O2}
case "$KIT" in
  mw1|mw2) SRCF="$SIM/kits/mw/sf${KIT#mw}.f"; GAMES="$SIM/games/games_m1.dat"; TASK=${3:-537}; M=1 ;;
  f1|f2|c1|c2|c3|c4|eh|el|dw1|dw2|dw3|dw4|lm) SRCF="$SIM/kits/$KIT/sf.f"; GAMES="$SIM/games/games.dat"; TASK=${3:-1902}; M=2 ;;
  *) echo "unknown kit '$KIT'"; exit 1 ;;
esac
W="$HERE/work/${KIT}_${IT}_${TASK}"
rm -rf "$W"; mkdir -p "$W/run"
cd "$W"
# the run length is the one line that changes, exactly as compile.sh does it
n=$(grep -c "^      data itv  /[0-9]*/" "$SRCF")
[ "$n" -eq 1 ] || { echo "expected one 'data itv' line in $SRCF, found $n"; exit 1; }
sed "s|^      data itv  /[0-9]*/|      data itv  /$IT/|" "$SRCF" > sf.f
cp "$SIM"/src/payf2.f "$SIM"/src/payf3.f "$SIM"/src/mt.f "$SIM"/src/mtb.f .
$FC $FFLAGS -o sf.x sf.f payf3.f payf2.f mtb.f mt.f
NPOP=$(sed -n 's/^      parameter (n=\([0-9]*\),m=1)/\1/p' sf.f)
echo "== $KIT: $(basename "$SRCF") with itend = $IT, N = $NPOP, task $TASK, built with $FC $FFLAGS"
cp "$GAMES" run/games.dat
t0=$(date +%s)
(cd run && ../sf.x "$TASK")
t1=$(date +%s)
echo "   ran in $((t1 - t0)) s"

# ---- checks -----------------------------------------------------------------------------------------------------
fail=0
nl=$(grep -c . "run/$TASK")
[ "$nl" -eq 10 ] && echo "   summary $TASK: 10 replicate lines" || { echo "!! summary has $nl lines"; fail=1; }
nd=$(awk '/^# distinct/{print $3; exit}' "run/h$TASK"); tot=$(awk '/^# distinct/{print $5; exit}' "run/h$TASK")
nc=$(grep -vc '^#' "run/h$TASK")
want=$((10 * (IT / 2) * NPOP))
[ "$nc" -eq "$nd" ] && [ "$tot" -eq "$want" ] && echo "   h$TASK: $nd strategies, $tot counts = 10 x itend/2 x N" \
  || { echo "!! h-file: $nc lines for $nd distinct, total $tot, expected $want"; fail=1; }
nw=$(grep -c '^# *[0-9]' "run/w$TASK")
[ "$nw" -eq 10 ] && echo "   w$TASK: 10 replicate blocks of the 10 most abundant strategies" || { echo "!! w-file has $nw blocks"; fail=1; }
if grep -q "rfile='r'" sf.f; then
  rs=$(wc -c < "run/r$TASK" | tr -d ' ')
  [ "$rs" -eq 5242880 ] && echo "   r$TASK: 10 x 65536 int64 per-replicate counts" || { echo "!! r-file has $rs bytes"; fail=1; }
fi
[ $fail -eq 0 ] || exit 1

# ---- pack, with the kit's own pack.py ---------------------------------------------------------------------------
PK="$SIM/kits/${KIT%[12]}/pack.py"; [ "$M" = 2 ] && PK="$SIM/kits/$KIT/pack.py"
echo "   pack.py:"
if [ "$M" = 1 ]; then
  # mw's pack.py expects all 512 cells; with one cell it packs that one and lists the other 511 as missing
  mv run "run${KIT#mw}"
  python3 -B "$PK" "run${KIT#mw}" packed --dev | grep -v ": missing product" | sed 's/^/     /' || true
  echo "     (the other 511 cells were not run, so pack.py reports them missing: expected in a smoke test)"
elif grep -q "rfile='r'" sf.f; then
  gunzip -c "$SIM/atoms/atoms512.bin.gz" > atoms512.bin
  RD=run; [ "$KIT" = lm ] && { mv run run_g0; RD=run_g0; }     # lm's pack.py names its packs after run_<g>
  python3 -B "$PK" "$RD" packed atoms512.bin | sed 's/^/     /'
else
  python3 -B "$PK" run packed | sed 's/^/     /' || true
  [ "$KIT" = dw1 ] && echo "     (dw1's pack.py assumes the production length, 5e9 samples a replicate, so it flags a short run: expected)"
fi
echo "   packs: $(ls packed | tr '\n' ' ')"

# ---- compare with the reference run --------------------------------------------------------------------------------
REF="$HERE/reference/${KIT}_${IT}_${TASK}.sha256"
RUNDIR=$(ls -d run* | head -1)
if [ -f "$REF" ]; then
  if (cd "$W/$RUNDIR" && shasum -a 256 -c "$REF" > ../check.txt 2>&1); then
    echo "== identical to the reference run ($(head -1 "$HERE/reference/README.md" | sed 's/^# //'))"
  else
    cat check.txt
    echo "== DIFFERENT from the reference run. That is expected with another compiler, other flags or another"
    echo "   CPU: one differently rounded payoff changes one comparison and with it the whole random trajectory."
  fi
else
  echo "== no reference for this (kit, itend, task); outputs in $W"
fi
