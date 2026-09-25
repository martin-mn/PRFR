#!/bin/bash
# Build the exact (pairsq) and the double-precision (pairs) census programs on Cannon.
set -e
module load gcc 2>/dev/null || true
gcc -O3 -march=native -o pairsq pairsq.c
gcc -O3 -march=native -o pairs pairs.c
./pairsq cmp 100000 7
./pairsq pair 19079 65535
