# SI Figure 8: the cube of population size, selection strength and mutation rate

The memory-two Wright–Fisher process at ε = 10⁻⁴ at the eight corners of {100, 1000} × {3, 100} × {10⁻⁴, 10⁻²} for
(N, β, μ). The figure has 24 disks in three groups of eight: **a–h** the efficiency of the population, **i–p** the
most abundant atom and **q–x** the most enriched atom. Within each group the top row is β = 3 and the bottom row
β = 100. The left pair of columns is N = 100 and the right pair N = 1000, with μ = 10⁻⁴ before 10⁻² in each pair.
The top left disk of each group is SI Figure 4d–f and the bottom right disk is main text Figure 4d–f. The frame,
colours and keys are those of main text Figure 4. The counts are SI Table 7a.

## Command

```
python3 SIFigure8/sifig8.py            # from the repository root; ~6 s
```

It writes `SIFigure8/SIFig8.pdf` and a 72-dpi preview `SIFig8.png`. The PDF deposited here is the published figure,
byte for byte; the preview is not deposited. The script also prints, for each corner, the efficiency range and the
number of games each atom leads, as most abundant and as most enriched.

## Inputs

- `data/robustness/games_<run>.csv` for the eight corners, in the figure's reading order:

  | position | run | β | N | μ |
  |---|---|---:|---:|---|
  | a, i, q | `f2_e4` | 3 | 100 | 10⁻⁴ |
  | b, j, r | `c2_e4` | 3 | 100 | 10⁻² |
  | c, k, s | `c4_e4` | 3 | 1000 | 10⁻⁴ |
  | d, l, t | `dw4_e4` | 3 | 1000 | 10⁻² |
  | e, m, u | `c3_e4` | 100 | 100 | 10⁻⁴ |
  | f, n, v | `c1_e4` | 100 | 100 | 10⁻² |
  | g, o, w | `dw3_e4` | 100 | 1000 | 10⁻⁴ |
  | h, p, x | `f1_e4` | 100 | 1000 | 10⁻² |

- `data/robustness/m2_atom_sizes.csv`, read through `data/robustness/wfruns.py`.
- `common/` and `data/games/` (the cells).

The script is the original `sifig8.py` with the drawing unchanged. Only two things differ: the eight corners are read
from the deposited tables instead of the private packs, and the output path.

## Requirements

Python 3 with numpy and matplotlib. The pixel identity below was obtained with Python 3.10.9, numpy 1.23.5 and
matplotlib 3.7.0 (its bundled DejaVu Sans); other matplotlib versions may differ in antialiasing and text placement.

## Verification (2026-09-24)

The script was run from a fresh copy of `common/`, `data/games/`, `data/robustness/` and this folder, with Python
3.10.9, numpy 1.23.5 and matplotlib 3.7.0. The new PDF and the published `SIFig8.pdf` were rasterised with
`pdftoppm` and compared pixel by pixel.

- The figure is **identical** at 80 dpi and at 150 dpi: max |diff| 0, mean 0, no pixel differs.
- The two PDF files differ only in their `/CreationDate`.
- The preview PNG is byte-identical to the original script's.

## Generations per replicate

The two corners at N = 100 and μ = 10⁻⁴, `f2_e4` (a) and `c3_e4` (e), ran 10⁸ generations per replicate; the other
six corners ran 10⁷. `data/robustness/runs.csv` lists the generations of every run, and
`provenance/robustness/reduce.py` checked them against each pack, whose `total` column is 10 · (generations/2) · N.
