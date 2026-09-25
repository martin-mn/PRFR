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
python3 fig2.py
```

The script writes `Fig2.pdf` (26.47 × 22.55 in, 12.1 MB) and `Fig2.png` (150 dpi) here. It prints, per atom, the
number of strategies in the atom somewhere, the per-game range where the atom is present, the number of levels and
the share of the disk where it is empty. It takes about 16 s.

## Files

| file | role |
|---|---|
| `fig2.py` | the plotting script |
| `Fig2.png` | a 150-dpi preview of the published figure. `Fig2.pdf` is 12.1 MB, so it is not deposited; the script writes it |
| `../data/arrangement/m1_faces_k4.npz`, `m1_faces.csv` | input for **a**–**g**: the memory-one faces, disk areas, atom counts, and the atom of each of the 16 strategies per face |
| `../data/arrangement/m2_faces_k4.npz`, `m2_faces.csv`, `m2_strategies.csv` | input for **h**–**n**: the memory-two faces, their atom counts, and the strategies in each atom somewhere (`open_*`) |
| `../data/arrangement/arrangement.py` | reads those files in the shapes of the original loaders |
| `../common/counts.py` | the count panels, which were `atomcounts.py`: `sheet`, `panel` and `finish` |

The script is the original `FinalFigures/fig2.py`. Only its data loading was replaced: the dump
`ca4_arrangement_k4.npz`, `Count6_faces.npz` (`ATOMS`, `ATOM_TOTAL`) and `m1atoms.load()`.

Requirements: Python 3 with numpy and matplotlib.

## Verification (2026-09-24)

The script was run on a fresh copy of `Figure2/`, `common/` and `data/arrangement/`. The software was Python 3.10.9,
numpy 1.23.5 and matplotlib 3.7.0.

- `Fig2.pdf` is byte-identical to the published `figures/Fig2.pdf`, apart from its `CreationDate` stamp.
- The two PDFs, rasterised with `pdftoppm` at 80 and at 150 dpi, are pixel-identical: max |diff| 0, mean |diff| 0.
- `Fig2.png` is byte-identical to the original preview.

The receipt gives these memory-two totals: 000 65486, 100 10701, 010 16013, 001 5230, 110 9389, 011 1721 and 111
1677. It also gives the per-game ranges: 100 from 1504 to 7631, 011 from 1 to 987, 111 at 8, 80 or 1519. These are
the numbers of SI §8. At memory one, 15 strategies are in 000 somewhere: all but tit-for-tat, as the legend says.
