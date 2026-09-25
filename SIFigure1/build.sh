#!/bin/sh
# Builds SIFig1.pdf from SIFig1.tex with pdflatex (TeX Live; packages tikz, standalone, times, amsmath, amssymb).
# The auxiliary files go to a temporary directory, so only SIFig1.pdf is written here.
set -e
cd "$(dirname "$0")"
tmp=$(mktemp -d)
pdflatex -interaction=nonstopmode -halt-on-error -output-directory "$tmp" SIFig1.tex > "$tmp/build.out" || { cat "$tmp/build.out"; exit 1; }
cp "$tmp/SIFig1.pdf" SIFig1.pdf
rm -rf "$tmp"
echo "wrote SIFig1.pdf"
