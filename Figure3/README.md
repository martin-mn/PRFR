# Figure 3: The number of strategies with each property at every game, for memory one and memory two

This folder reproduces main text Figure 3 from the exact ε → 0 arrangements in `../data/arrangement/`.

## What it shows

Eight disks. Row **a**–**d** is the 16 binary memory-one strategies and row **e**–**h** the 65536 binary memory-two
strategies. Each panel counts the strategies in one set at every game, in the limit ε → 0. A set is a sum of atoms of
Figure 2:

- **a**, **e**: efficient, 1\*\* (100 + 110 + 111). The count is constant on each side of the switch line: at memory
  two, 7639 mutual cooperators below it and 3072 alternators above it; at memory one, 3 below and none above.
- **b**, **f**: stable, \*1\* (010 + 110 + 011 + 111). At memory two there are 299 to 22069 at a game, and 23861 strategies
  are stable somewhere.
- **c**, **g**: competitive, \*\*1 (001 + 011 + 111). The count is constant off the line T = S: 2640 at memory two, 4 at
  memory one.
- **d**, **h**: the partners, 11\* (110 + 111). At memory two there are 8 to 7639 at a game, and 9431 strategies are
  partners somewhere.

The colour rules are those of Figure 2. Grey means the set is empty at the game. The line under each disk gives the
number of strategies that belong to the set somewhere.

## Run

```
python3 fig3.py
```

The script writes `Fig3.pdf` (26.47 × 11.40 in, 6.9 MB) and `Fig3.png` (150 dpi) here, and prints a receipt per
panel. It takes about 10 s.

## Files

| file | role |
|---|---|
| `fig3.py` | the plotting script |
| `Fig3.png` | a 150-dpi preview of the published figure. `Fig3.pdf` is 6.9 MB, so it is not deposited; the script writes it |
| `../data/arrangement/m1_faces_k4.npz`, `m1_faces.csv` | input for **a**–**d** |
| `../data/arrangement/m2_faces_k4.npz`, `m2_faces.csv` | input for **e**–**h**: the memory-two faces and their atom counts |
| `../data/arrangement/m2_strategies.csv` | the efficiency and rivalry masks (`eff_cc`, `eff_alt`, `riv_plus`, `riv_minus`) and the strategies stable somewhere, which give the totals under the disks |
| `../data/arrangement/arrangement.py` | reads those files in the shapes of the original loaders |
| `../common/counts.py` | the count panels, which were `atomcounts.py`: `sheet`, `panel`, `rowlabel` and `finish` |

The script is the original `FinalFigures/fig3.py`. Only its data loading was replaced: the dump
`ca4_arrangement_k4.npz`, `Count6_faces.npz`, `m2_masks.npz` and `m1atoms.load()`. The original typed the total 9431
(partners on an open set) as a constant. The script keeps the constant and asserts that the deposited data give the
same number.

Requirements: Python 3 with numpy and matplotlib.

## Verification (2026-09-24)

The script was run on a fresh copy of `Figure3/`, `common/` and `data/arrangement/`. The software was Python 3.10.9,
numpy 1.23.5 and matplotlib 3.7.0.

- `Fig3.pdf` is byte-identical to the published `figures/Fig3.pdf`, apart from its `CreationDate` stamp.
- The two PDFs, rasterised with `pdftoppm` at 80 and at 150 dpi, are pixel-identical: max |diff| 0, mean |diff| 0.
- `Fig3.png` is byte-identical to the original preview.

The totals under the memory-two disks are 10711, 23861, 5230 and 9431. The per-game ranges are 3072 to 7639
(efficient), 299 to 22069 (stable), 2640 (competitive) and 8 to 7639 (partners). These are the counts of the Methods and
SI §6. `../data/arrangement/check.py` derives them independently, from the polygons of the stability regions.
