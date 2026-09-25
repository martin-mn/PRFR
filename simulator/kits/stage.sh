#!/bin/bash
# stage.sh -- make a kit directory complete, i.e. exactly as it ran on the cluster.
#
# The four Fortran files that every kit shares (payf2.f payf3.f mt.f mtb.f) and the game list are stored once in
# the repository, in ../src/ and ../games/, instead of fourteen identical times.  This script copies them into the
# kit directories, so that each kit's own compile.sh, submit.sh and pack.py find them where they expect them, and
# unpacks ../atoms/atoms512.bin.gz to ./atoms512.bin, the default path of every pack.py that writes a .rep file
# (a kit's pack.py reads ../atoms512.bin).
#
#   bash stage.sh c1 f2 mw        stage these kits
#   bash stage.sh all             stage every kit
#   bash stage.sh --clean all     remove the staged copies again (only the files this script puts there)
#
# The memory-one kit mw gets ../games/games_m1.dat (512 rows) as its games.dat; every memory-two kit gets
# ../games/games.dat (967 rows, the sunflower is rows 456-967).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SIM=$(dirname "$HERE")
KITS="c1 c2 c3 c4 dw1 dw2 dw3 dw4 eh el f1 f2 lm mw"
SHARED="payf2.f payf3.f mt.f mtb.f"
clean=0
if [ "$1" = "--clean" ]; then clean=1; shift; fi
[ $# -gt 0 ] || { echo "usage: bash stage.sh [--clean] {all | kit ...}   kits: $KITS"; exit 1; }
[ "$1" = "all" ] && set -- $KITS
for k in "$@"; do
  case " $KITS " in *" $k "*) ;; *) echo "unknown kit '$k' (kits: $KITS)"; exit 1 ;; esac
  d="$HERE/$k"
  if [ $clean -eq 1 ]; then
    for f in $SHARED games.dat; do rm -f "$d/$f"; done
    echo "$k: staged files removed"
    continue
  fi
  for f in $SHARED; do cp "$SIM/src/$f" "$d/$f"; done
  if [ "$k" = mw ]; then g="$SIM/games/games_m1.dat"; else g="$SIM/games/games.dat"; fi
  cp "$g" "$d/games.dat"
  echo "$k: staged $SHARED games.dat ($(basename "$g"))"
done
if [ $clean -eq 1 ]; then
  [ "$*" = "$KITS" ] && rm -f "$HERE/atoms512.bin" && echo "atoms512.bin removed"
  exit 0
fi
if [ ! -f "$HERE/atoms512.bin" ]; then
  gunzip -c "$SIM/atoms/atoms512.bin.gz" > "$HERE/atoms512.bin"
  echo "atoms512.bin unpacked ($(wc -c < "$HERE/atoms512.bin" | tr -d ' ') bytes)"
fi
