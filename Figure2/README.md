# Figure 2: The number of strategies in each atom at every game, for memory one and memory two

This folder reproduces main text Figure 2 from the exact ε → 0 arrangements in `../data/arrangement/`.

## What it shows

Fourteen disks, one per atom. The atoms are written efficient–stable–competitive, in the order 000, 100, 010, 001, 110,
011, 111. Rows **a**–**g** are the 16 binary memory-one strategies, drawn on the 45 faces of their arrangement. Rows
**h**–**n** are the 65536 binary memory-two strategies, on the 22872 faces of theirs, drawn as 27598 polygons. Each
panel counts the strategies in its atom at every game, exactly, in the limit ε → 0.

Each panel has its own colour scale:

- one band per value where the atom takes at most twelve values;
- otherwise, an equal-area magma ramp;
- grey where the atom has no strategy at the game.

The line under each disk gives the number of strategies that belong to the atom somewhere in the plane. The eighth
atom, 101, has no member anywhere.

## Run

```
python3 fig2.py            # the figure, set for the page
python3 fig2.py --wide     # the sheet of release 1.0.0
```

The script writes `Fig2.pdf` (27.79 × 25.70 in, 12.1 MB) and `Fig2.png` (150 dpi) here. The sheet is meant to be
printed 6.89 in (17.5 cm, the full text width) wide, where it is 6.37 in (16.2 cm) tall: height/width
0.9245. With `--wide` it writes `Fig2_wide.pdf` (26.47 × 22.55 in, 12.1 MB) and `Fig2_wide.png` instead: the sheet of
release 1.0.0, whose type printed at that width is 2.4 to 5.8 pt. It prints, per atom, the number of strategies in the
atom somewhere, the per-game range where the atom is present, the number of levels and the share of the disk where it
is empty. It takes about 16 s.

## Type

The page version has the panels, letters, colour scales and data of release 1.0.0, and the same drawing, except that the colour bars
are as tall as the disk (0.85 PW, was 0.80 PW) and their grey triangle is 0.14 of the bar (was 0.06); the disks, lines
and bar widths keep their sizes. Otherwise only the type and the room it takes are changed (`common.counts.page_type`). Printed
6.89 in wide, the sizes are:

| text | printed size |
|---|---|
| panel letters | 8.5 pt, bold |
| heads | 7 pt. The heads of 110, 011 and 111 are set on two lines. A head starts after its letter, not centred over the disk |
| row labels | 7.5 pt |
| u, v | 7 pt. v stands to the right of its axis |
| colour-bar label | 6.5 pt |
| colour-bar ticks, the 0 beside the grey triangle, the line under each disk | 6 pt. The line under each disk is set on two lines |
| labels of the guide circles | 5.5 pt. On the u axis, −1 and −4 stand above it; the other labels stand below it |
| game names on the rim | 5.0 pt; at these gaps the r < LIM assertion allows at most about 5.25 pt |

The band boundaries of every colour scale are those of release 1.0.0. The ramps of **j**, **l** and **m** label
fewer intermediate values, because a 6-pt label takes up more of the bar: **j** labels 2, 200, 1000, 5000, 10000 and
14430 (release 1.0.0 also labelled 100, 500 and 2000); **l** labels 6, 200, 500, 1000 and 7631 (also 100 and 2000);
**m** labels 1, 200, 500 and 987 (also 100).

## Files

| file | role |
|---|---|
| `fig2.py` | the plotting script |
| `Fig2.png` | a 150-dpi preview of the figure (the page version). `Fig2.pdf` is 12.1 MB, so it is not deposited; the script writes it |
| `../data/arrangement/m1_faces_k4.npz`, `m1_faces.csv` | input for **a**–**g**: the memory-one faces, disk areas, atom counts, and the atom of each of the 16 strategies per face |
| `../data/arrangement/m2_faces_k4.npz`, `m2_faces.csv`, `m2_strategies.csv` | input for **h**–**n**: the memory-two faces, their atom counts, and the strategies in each atom somewhere (`open_*`) |
| `../data/arrangement/arrangement.py` | reads those files in the shapes of the original loaders |
| `../common/counts.py` | the count panels, which were `atomcounts.py`: `sheet`, `panel`, `finish` and `page_type` |

The script is the original `FinalFigures/fig2.py`. Its data loading was replaced: the dump
`ca4_arrangement_k4.npz`, `Count6_faces.npz` (`ATOMS`, `ATOM_TOTAL`) and `m1atoms.load()`. The page type was added
on 2026-09-30, and `--wide` keeps the original drawing.

Requirements: Python 3 with numpy and matplotlib.

## Verification (2026-09-24)

The script was run on a fresh copy of `Figure2/`, `common/` and `data/arrangement/`. The software was Python 3.10.9,
numpy 1.23.5 and matplotlib 3.7.0. At the time the script drew only the sheet that `--wide` now draws.

- `Fig2.pdf` is byte-identical to `figures/Fig2.pdf` of the manuscript of that date, apart from its `CreationDate` stamp.
- The two PDFs, rasterised with `pdftoppm` at 80 and at 150 dpi, are pixel-identical: max |diff| 0, mean |diff| 0.
- `Fig2.png` is byte-identical to the original preview.

On 2026-09-30, after the page type was added, the same software gave these results:

- `fig2.py --wide` wrote `Fig2_wide.pdf`, byte-identical, apart from its `CreationDate`, to `figures/Fig2.pdf` of
  the manuscript that release 1.0.0 accompanied (2026-09-25), and `Fig2_wide.png`, byte-identical to the preview of
  release 1.0.0.
- `fig2.py` wrote the page version: `Fig2.pdf`, byte-identical, apart from its `CreationDate`, to `figures/Fig2.pdf`
  of the revised manuscript (2026-09-30), and `Fig2.png`, the deposited preview. The script's own checks pass: no
  text leaves the sheet, and no two heads of a panel overlap. Two further checks also pass: no two texts of different
  panels, bars or row labels overlap, and no letter, head, line under a disk or label of the u axis overlaps a rim
  name. The font sizes in the PDF, multiplied by 6.89 / 27.79, are 6.0, 6.5, 7.0, 7.5 and 8.5 pt. The guide labels
  and the rim names are drawn as outlines, at 5.5 and 5.0 pt.

`reproduce_all.sh` draws the page version only. In a git clone, this compares the `--wide` preview with that of
release 1.0.0:

```
python3 fig2.py --wide && git show v1.0.0:Figure2/Fig2.png | cmp - Fig2_wide.png
```

The receipt gives these memory-two totals: 000 65486, 100 10701, 010 16013, 001 5230, 110 9389, 011 1721 and 111
1677. It also gives the per-game ranges: 100 from 1504 to 7631, 011 from 1 to 987, 111 at 8, 80 or 1519. These are
the numbers of SI §8. At memory one, 15 strategies are in 000 somewhere: all but tit-for-tat, as the SI notes to
Figure 2 say ("Notes to main text Figures 1 to 5").
