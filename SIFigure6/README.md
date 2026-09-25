# SI Figure 6 — strict Nash equilibria at the error rate of the runs

This folder redraws SI Figure 6: the strict Nash equilibria at ε = 10⁻⁴ and the share of the population on them, at the
512 sampled games. Memory one is in row 1 (panels a–c), memory two in row 2 (d–f).

| column | panels | what |
|---|---|---|
| 1 | a, d | the number of strict Nash equilibria at ε = 10⁻⁴: 0–7 among the 16 memory-one strategies, 0–645 among the 65536 memory-two strategies. Each panel has its own count scale in Figure 2's style (bands for a few values, an equal-area ramp otherwise); grey where there is none |
| 2 | b, e | the share of the population on them in the run at N = 100, β = 3, μ = 10⁻⁴ |
| 3 | c, f | the same in the run at N = 1000, β = 100, μ = 10⁻² |

Columns 2 and 3 are linear from 0 to 100 % (the colour bar under column 2), grey where the game has no strict
equilibrium.

## Reproduce

```
cd SIFigure6
python3 sifig6.py            # writes SIFig6.pdf here (about 3 s); --png also writes SIFig6.png at 110 dpi
```

Requirements: Python 3 with numpy and matplotlib. The published page was rendered with Python 3.10.9, numpy 1.23.5
and matplotlib 3.7.0, using matplotlib's bundled DejaVu Sans. With these versions the script reproduces the published
PDF byte for byte, apart from the creation date matplotlib embeds (see Verification).

The script prints one receipt line per row, for example:
`Memory-2, 65536 strategies: strict Nash equilibria per game 0..645, median 15, none at 111 games (21.7% of the cell
area); share on them N = 100: max 0.040 ...; N = 1000: max 0.193 ...`.

## Files

| file | what |
|---|---|
| `sifig6.py` | the entry point: `figstrict.draw(efficient=False, ...)` |
| `figstrict.py` | the sheet, shared with SI Figure 7 (an identical copy is in `../SIFigure7`) |
| `SIFig6.pdf` | the published figure, for comparison |

Inputs:

- `../data/strict/m1_games.csv` (columns `n_strict`, `share_F2`, `share_F1`) and `../data/strict/m2_games.csv` (the same
  columns): one row per game. `F2` is the run at N = 100, `F1` the run at N = 1000: the memory-two runs `dw2` and
  `dw1` of the simulator (`m2_N100` and `m2_N1000` in `../data/runs/`) and the memory-one runs `m1_N100` and
  `m1_N1000`. The table "The same runs appear under different names" in the section on the simulator of
  `../README.md` gives every name of each run. See `../data/strict/README.md`.
- `../data/games/` through `../common` (the games and their Voronoi cells), and `common.furniture` and `common.counts`
  for the frame of the disk and the count scale.

Output: `SIFig6.pdf` (16.68 × 11.00 in).

The script is the author's `figstrict.py` with the drawing code unchanged. The original read the same numbers through
`strictne.py` from the private run outputs; here `data()` reads them from the two tables. The per-strategy sets behind
the counts, and how the tables were made, are in `../data/strict` and `../provenance/strict`.

## Verification (2026-09-24)

`SIFigure6/`, `SIFigure7/`, `common/`, `data/games/` and `data/strict/` were copied to a fresh directory and the script
was run there. The new PDF and the published one (`figures/SI/SIFig6.pdf` of the paper) were rasterised with
`pdftoppm -png` and compared pixel by pixel:

| resolution | max \|diff\| | mean \|diff\| | differing pixels |
|---|---|---|---|
| 80 dpi | 0 | 0 | 0 |
| 150 dpi | 0 | 0 | 0 |

The two PDFs are also byte-identical once the `/CreationDate` entry is removed: both are 329562 bytes.
