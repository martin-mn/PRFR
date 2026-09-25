#!/usr/bin/env bash
# reproduce_all.sh -- redraws every figure and recomputes every table of
#   "Partners, rivals, and friendly rivals in the evolution of direct reciprocity" (Martin A. Nowak)
# from the data deposited in this repository, and runs every checker, one script at a time, under nice.
#
#   bash reproduce_all.sh                    everything: figures, tables and checks (about 4 minutes on a laptop)
#   bash reproduce_all.sh figures            main text Figures 1-5 and SI Figures 1-12
#   bash reproduce_all.sh tables             SI Tables 1-8 and the family descriptions
#   bash reproduce_all.sh checks             the checkers in data/, census/, notes/checks/ and simulator/
#   bash reproduce_all.sh Figure4 SITable6   single folders (any folder named in the list of steps below)
#   bash reproduce_all.sh list               the steps, without running them
#
#   PYTHON=/path/to/python3 bash reproduce_all.sh ...   another interpreter (default: python3 on the PATH)
#
# Each step runs in its own folder, as that folder's README says, under "nice -n 10" and with "python3 -B"
# (no __pycache__). Its output goes to reproduce_log/<step>.out and .err. After each step the script prints
# the files the step wrote and, for every deposited output that the step rewrites, whether the new file is
# identical to the deposited one. A PDF written by matplotlib differs from the deposited one only in its
# creation date.
#
# The script stops at the first step that fails: a step fails if it exits with a non-zero status, if it prints
# FAIL, FAILED, DIFFERS or DIFFERENT, or if its last line reports a non-zero number of differences. A step that
# needs a program that is not installed (pdflatex, a C compiler, gfortran) is skipped with a note.
#
# Exit status: 0 if every step passed and every rewritten deposited file is identical to the deposited one;
# 1 if a step failed (the script stops there); 2 if every step passed but a rewritten file is not identical
# (with matplotlib versions other than those of requirements.txt, a figure may differ in antialiasing).
#
# The steps rewrite the deposited figures and tables in place. With the versions in requirements.txt they
# come out identical, the PDFs apart from their creation date. In a git clone, "git checkout -- ." restores
# the deposited files.

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
LOG="$ROOT/reproduce_log"
SNAP="$(mktemp -d "${TMPDIR:-/tmp}/reproduce_all.XXXXXX")"
trap 'rm -rf "$SNAP"' EXIT

command -v "$PY" >/dev/null 2>&1 || { echo "no Python interpreter '$PY'"; exit 1; }
"$PY" -c "import numpy, matplotlib" >/dev/null 2>&1 || { echo "$PY cannot import numpy and matplotlib; see requirements.txt"; exit 1; }

WANT=" $* "
LIST=0
case "$WANT" in *" list "*) LIST=1 ;; esac
SEL=${WANT// list / }
[ -z "${SEL// /}" ] && SEL="  "              # nothing named: every step
if [ "$LIST" = 1 ]; then printf '%-8s %-18s %-22s %s\n' stage folder "log name" command; else mkdir -p "$LOG"; fi
NSTEP=0; NFILE=0; NSKIP=0; NOTES=""
T_START=$(date +%s)

same() {  # same NEW OLD: how NEW compares with the deposited file OLD (exit status 0 if identical)
  "$PY" - "$1" "$2" <<'EOF'
import re, sys
a, b = (open(p, "rb").read() for p in sys.argv[1:3])
dates = lambda s: re.sub(rb"/(CreationDate|ModDate) ?\(D:[^)]*\)", b"", s)
ids = lambda s: re.sub(rb"/ID ?\[ ?<[0-9A-Fa-f]*> ?<[0-9A-Fa-f]*> ?\]", b"", dates(s))
if a == b:
    print("identical to the deposited file")
elif dates(a) == dates(b):
    print("identical to the deposited file apart from its creation date")
elif ids(a) == ids(b):
    print("identical to the deposited file apart from its dates and its /ID")
else:
    print("DIFFERS from the deposited file")
    sys.exit(1)
EOF
}

# The kit generators of simulator/kits, run on a temporary copy that holds only what they read (the template kits
# dw3 and dw1, the generators and the shared sources), and their output compared file by file with the deposited
# kits. Runs in simulator/. mkkits.py writes eh el c1 c2 c3 c4 f1 f2 (their README.md files were written for the
# repository and are not compared), lm/mklm.py writes lm/sf.f and lm/pack.py, mw/mksf.py the four memory-one sources.
GENERATED_KITS="eh el c1 c2 c3 c4 f1 f2"
STAGED=" payf2.f payf3.f mt.f mtb.f games.dat "
regenerate_kits() {
  local t="$SNAP/kits_copy" k f b n=0 bad=0
  rm -rf "$t"; mkdir -p "$t/kits/lm" "$t/kits/mw" "$t/kits/dw1" "$t/kits/dw3" || return 1
  cp -R src games atoms "$t/" && cp kits/mkkits.py kits/stage.sh "$t/kits/" && cp kits/lm/mklm.py "$t/kits/lm/" \
    && cp kits/mw/mksf.py "$t/kits/mw/" || return 1
  for k in dw1 dw3; do
    for f in kits/$k/*; do
      b=${f##*/}
      [ -f "$f" ] && case "$STAGED" in *" $b "*) ;; *) cp "$f" "$t/kits/$k/" ;; esac
    done
  done
  (cd "$t/kits" && nice -n 10 bash stage.sh dw3 && nice -n 10 "$PY" -B mkkits.py \
     && nice -n 10 "$PY" -B lm/mklm.py && nice -n 10 "$PY" -B mw/mksf.py) || { echo "a generator failed"; return 1; }
  for k in $GENERATED_KITS; do
    for f in "$t/kits/$k"/*; do                       # every file the generator wrote, against the deposited one
      b=${f##*/}
      [ -f "$f" ] || continue
      case "$STAGED README.md " in *" $b "*) continue ;; esac
      if cmp -s "$f" "kits/$k/$b"; then n=$((n + 1)); else echo "DIFFERS: kits/$k/$b"; bad=$((bad + 1)); fi
    done
    for f in kits/$k/*; do                             # and every deposited file of the kit was written
      b=${f##*/}
      [ -f "$f" ] || continue
      case "$STAGED README.md submit.sh.orig " in *" $b "*) continue ;; esac
      case "$b" in sf_*.f|*.x|JOBID_*|IDX_*) continue ;; esac
      [ -f "$t/kits/$k/$b" ] || { echo "not written by mkkits.py: kits/$k/$b"; bad=$((bad + 1)); }
    done
  done
  for f in lm/sf.f lm/pack.py mw/sf1.f mw/sf2.f mw/sf1s.f mw/sf2s.f; do
    if [ -f "$t/kits/$f" ] && cmp -s "$t/kits/$f" "kits/$f"; then n=$((n + 1)); else echo "DIFFERS: kits/$f"; bad=$((bad + 1)); fi
  done
  rm -rf "$t"
  if [ "$bad" -ne 0 ]; then echo "$bad file(s) of the kits not reproduced"; return 1; fi
  echo "the generators rewrote $n files of the kits, all identical to the deposited ones"
}

# step STAGE DIR NAME LABEL NEED COMMAND [DEPOSITED ...]
#   STAGE      figures, tables or checks
#   DIR        the folder the command runs in, relative to the repository root
#   NAME       the name of the step's log files, reproduce_log/NAME.out and .err
#   NEED       a program the step needs on the PATH, or -
#   COMMAND    one string, run under nice in DIR (or the name of a function of this script, which nices its own commands)
#   DEPOSITED  deposited files (relative to DIR) that the step rewrites and that are compared with their
#              deposited version; =log:FILE compares what the step prints with the deposited FILE
step() {
  local stage=$1 dir=$2 name=$3 label=$4 need=$5 cmd=$6; shift 6
  if [ "$SEL" != "  " ]; then
    case "$SEL" in *" $stage "*|*" $dir "*|*" ${dir%%/*} "*|*" $name "*) ;; *) return 0 ;; esac
  fi
  NSTEP=$((NSTEP + 1))
  local pp=$P
  local shown=${cmd//"$pp"/python3 -B}
  local run="nice -n 10 $cmd"
  if declare -F "$cmd" >/dev/null; then run=$cmd; shown="$cmd (a function of reproduce_all.sh)"; fi
  if [ "$LIST" = 1 ]; then
    printf '%-8s %-18s %-22s %s\n' "$stage" "$dir" "$name" "$shown"
    return 0
  fi
  printf '\n[%2d] %s   (%s: %s)\n' "$NSTEP" "$label" "$dir" "$shown"
  if [ "$need" != "-" ] && ! command -v "$need" >/dev/null 2>&1; then
    echo "     SKIPPED: $need is not installed"
    NSKIP=$((NSKIP + 1)); NOTES="$NOTES
  skipped: $label ($need is not installed)"
    return 0
  fi
  local f g snap="$SNAP/$name"
  mkdir -p "$snap"
  for f in "$@"; do
    g=${f#=log:}
    [ -f "$ROOT/$dir/$g" ] && cp -p "$ROOT/$dir/$g" "$snap/$(printf '%s' "$g" | tr '/' '_')"
  done
  : > "$snap/.stamp"
  sleep 1                              # every file the step writes is then strictly newer than the stamp
  local t0 st dt
  t0=$(date +%s)
  (cd "$ROOT/$dir" && eval "$run") > "$LOG/$name.out" 2> "$LOG/$name.err"
  st=$?
  dt=$(( $(date +%s) - t0 ))
  local last why=""
  last=$(grep -v '^[[:space:]]*$' "$LOG/$name.out" | tail -n 1)
  local rootpat="$ROOT/"
  last=${last//"$rootpat"/}
  last=$(printf '%s' "$last" | cut -c1-120)
  if [ $st -ne 0 ]; then
    why="it exited with status $st"
  elif grep -Eq '(^|[^A-Za-z])(FAIL|FAILED|DIFFERS|DIFFERENT)([^A-Za-z]|$)' "$LOG/$name.out"; then
    why="it printed: $(grep -E -m 1 '(^|[^A-Za-z])(FAIL|FAILED|DIFFERS|DIFFERENT)([^A-Za-z]|$)' "$LOG/$name.out" | cut -c1-120)"
  elif printf '%s' "$last" | grep -Eq '(^|[^0-9.])[1-9][0-9]*( [a-z()]+)? differ|not all'; then
    why="its last line reports differences"
  fi
  if [ -n "$why" ]; then
    echo "     FAILED after $dt s: $why. The end of its output:"
    tail -n 15 "$LOG/$name.out" | sed 's/^/       /'
    tail -n 15 "$LOG/$name.err" | sed 's/^/       /'
    echo
    echo "Stopped. The full output is in reproduce_log/$name.out and reproduce_log/$name.err."
    exit 1
  fi
  if [ -z "$last" ]; then echo "     ok in $dt s."; else echo "     ok in $dt s. Last line printed: $last"; fi
  local wrote nw
  wrote=$(cd "$ROOT" && find . -type f -newer "$snap/.stamp" ! -path "./reproduce_log/*" ! -name .DS_Store \
          | sed 's|^\./||' | sort)
  nw=$(printf '%s' "$wrote" | grep -c . || true)
  printf '%s\n' "$wrote" | head -n 6 | while read -r f; do
    [ -n "$f" ] && printf '     wrote %s (%s bytes)\n' "$f" "$(wc -c < "$ROOT/$f" | tr -d ' ')"
  done
  [ "$nw" -gt 6 ] && echo "     ... and $((nw - 6)) more files, $(printf '%s\n' "$wrote" | tail -n +7 | cut -d/ -f1-3 | sort -u | tr '\n' ' ')"
  local new old res
  for f in "$@"; do
    g=${f#=log:}
    old="$snap/$(printf '%s' "$g" | tr '/' '_')"
    if [ "$f" != "$g" ]; then new="$LOG/$name.out"; g="the printed output against $g"; else new="$ROOT/$dir/$g"; fi
    if [ ! -f "$old" ]; then echo "     $g: no deposited copy to compare with"; continue; fi
    if [ ! -f "$new" ]; then
      echo "     $g: NOT WRITTEN"; NFILE=$((NFILE + 1)); NOTES="$NOTES
  not written: $dir/$g"; continue
    fi
    if res=$(same "$new" "$old"); then
      echo "     $g: $res"
    else
      echo "     $g: $res"; NFILE=$((NFILE + 1)); NOTES="$NOTES
  not identical to the deposited file: $dir/$g"
    fi
  done
}

P="\"$PY\" -B"
if [ "$LIST" = 0 ]; then
  echo "Reproducing the display items of the paper in $ROOT"
  echo "with Python $("$PY" -c 'import sys, numpy, matplotlib; print(sys.version.split()[0] + ", numpy " + numpy.__version__ + ", matplotlib " + matplotlib.__version__)')"
  "$PY" -c 'import matplotlib, sys; sys.exit(matplotlib.__version__ != "3.7.0")' || \
    echo "(The deposited figures were rendered with matplotlib 3.7.0; with another version a figure may differ in antialiasing.)"
fi

# ------------------------------------------------------------------------------------------------- figures
# The figure scripts also write PNG previews; only those of Figures 2 and 3 are deposited (their PDFs are over 5 MB).
step figures .          common     "the 512 games and their cells: self-test"  -  "$P -m common"
step figures Figure1    Figure1    "Figure 1"      -         "$P fig1.py"     Fig1.pdf
step figures Figure2    Figure2    "Figure 2"      -         "$P fig2.py"     Fig2.png
step figures Figure3    Figure3    "Figure 3"      -         "$P fig3.py"     Fig3.png
step figures Figure4    Figure4    "Figure 4"      -         "$P fig4.py"     Fig4.pdf
step figures Figure5    Figure5    "Figure 5"      -         "$P fig5.py"     Fig5.pdf
step figures SIFigure1  SIFigure1  "SI Figure 1"   pdflatex  "sh build.sh"    SIFig1.pdf
step figures SIFigure2  SIFigure2  "SI Figure 2"   -         "$P sifig2.py"   SIFig2.pdf
step figures SIFigure3  SIFigure3  "SI Figure 3"   -         "$P sifig3.py"   SIFig3.pdf
step figures SIFigure4  SIFigure4  "SI Figure 4"   -         "$P sifig4.py"   SIFig4.pdf
step figures SIFigure5  SIFigure5  "SI Figure 5"   -         "$P sifig5.py"   SIFig5.pdf
step figures SIFigure6  SIFigure6  "SI Figure 6"   -         "$P sifig6.py"   SIFig6.pdf
step figures SIFigure7  SIFigure7  "SI Figure 7"   -         "$P sifig7.py"   SIFig7.pdf
step figures SIFigure8  SIFigure8  "SI Figure 8"   -         "$P sifig8.py"   SIFig8.pdf
step figures SIFigure9  SIFigure9  "SI Figure 9"   -         "$P sifig9.py"   SIFig9.pdf
step figures SIFigure10 SIFigure10 "SI Figure 10"  -         "$P sifig10.py"  SIFig10.pdf
step figures SIFigure11 SIFigure11 "SI Figure 11"  -         "$P sifig11.py"  SIFig11.pdf
step figures SIFigure12 SIFigure12 "SI Figure 12"  -         "$P sifig12.py"  SIFig12.pdf

# -------------------------------------------------------------------------------------------------- tables
# Each table script compares its table with the printed one entry by entry and exits non-zero on a mismatch.
step tables SITable1  SITable1  "SI Table 1"  -  "$P sitable1.py"  =log:output.txt
step tables families  families  "the family descriptions (SI section 7)"  -  "$P families.py"  families.txt covers.csv
step tables SITable2  SITable2  "SI Table 2"  -  "$P sitable2.py"  SITable2.csv
step tables SITable3  SITable3  "SI Table 3"  -  "$P sitable3.py"  SITable3.csv
step tables SITable4  SITable4  "SI Table 4"  -  "$P sitable4.py"  SITable4.csv SITable4.txt
step tables SITable5  SITable5  "SI Table 5"  -  "$P sitable5.py"  SITable5.csv
step tables SITable6  SITable6  "SI Table 6"  -  "$P sitable6.py"  SITable6.csv SITable6.tex
step tables SITable7  SITable7  "SI Table 7"  -  "$P sitable7.py"  SITable7.csv SITable7.tex
step tables SITable8  SITable8  "SI Table 8, with the check against all 65536 memory-two co-players"  -  "$P sitable8.py --m2"  sitable8.csv m1_pairs.csv =log:output.txt

# -------------------------------------------------------------------------------------------------- checks
step checks data/arrangement arrangement_check    "the exact arrangement: the counts of the Methods and SI sections 6 and 8"  -  "$P check.py"
step checks data/arrangement arrangement_m1atoms  "the memory-one arrangement rebuilt from nothing"  -  "$P m1atoms.py m2"
step checks data/runs        runs_check_numbers   "the four main runs: the numbers of the text"   -  "$P check_numbers.py"
step checks data/strict      strict_check         "strict equilibria: the numbers of the text"    -  "$P check_strict.py"
step checks data/strict      strict_recompute     "strict equilibria: the sets recomputed from the games"  -  "$P recompute_sets.py"
step checks census           census_check         "the census: the counts of SI section 6, and the stable strategies at (-2,2) against data/arrangement"  -  "$P check.py"
step checks census           census_build         "the census programs: build and self-test"      cc  "make selftest"
step checks notes/checks     notes_fixed_eps      "notes: the fixed error rate"   -  "$P check_fixed_eps.py"          =log:check_fixed_eps.txt
step checks notes/checks     notes_discounting    "notes: discounting"            -  "$P check_discounting.py"        =log:check_discounting.txt
step checks notes/checks     notes_patterns       "notes: the families"           -  "$P check_patterns.py"           =log:check_patterns.txt
step checks notes/checks     notes_bays           "notes: the bays and cycles"    -  "$P check_bays.py"               =log:check_bays.txt
step checks notes/checks     notes_punishment     "notes: longer punishment"      -  "$P check_longer_punishment.py"  =log:check_longer_punishment.txt
step checks notes/checks     notes_memory_one     "notes: the memory-one atoms"   -  "$P check_memory_one_atoms.py"   =log:check_memory_one_atoms.txt
step checks simulator        simulator_seeds      "the simulator: the seed tables against the kit files"  -  "$P mkseeds.py --check"
step checks simulator        simulator_kits       "the simulator: the kit generators, rerun on a temporary copy"  -  regenerate_kits
step checks simulator/local  simulator_smoke      "the simulator: one game, built and run locally"  gfortran  "bash smoke.sh"

if [ "$NSTEP" = 0 ]; then echo "No step matches '$*'. The steps: bash reproduce_all.sh list"; exit 1; fi
[ "$LIST" = 1 ] && exit 0
echo
echo "Done: $NSTEP steps in $(( $(date +%s) - T_START )) s, every step passed ($NSKIP skipped);"
echo "$NFILE rewritten file(s) not identical to the deposited ones."
[ -n "$NOTES" ] && printf '%s\n' "$NOTES"
echo "The output of every step is in reproduce_log/."
[ "$NFILE" -eq 0 ] || exit 2
exit 0
