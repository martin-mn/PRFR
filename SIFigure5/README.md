# SI Figure 5: Main text Figure 5 for the small population

Reproduces SI Figure 5 from the reduced output of two Wright–Fisher runs.

## What it shows

The share of the population with each property in the runs of SI Figure 4 (N = 100, β = 3, μ = 10⁻⁴,
ε = 10⁻⁴), in the layout and colour scale of main text Figure 5. Row **a**–**c** is memory one and row **d**–**f**
memory two. The columns are efficient (`1**`), stable (`*1*`) and competitive (`**1`). A cell is grey where no strategy
of the space has the property at that game.

## Run

```
python3 sifig5.py
```

It writes `SIFig5.pdf` and `SIFig5.png` (110 dpi) here and prints the per-property summary of each run. It takes
about 3 s.

## Files

| file | role |
|---|---|
| `sifig5.py` | the plotting script, with the same `draw()` as `../Figure5/fig5.py` |
| `SIFig5.pdf` | the published figure (`figures/SI/SIFig5.pdf` of the paper), kept for comparison |
| `SIFig5.png` | a 110-dpi preview the script writes beside the PDF; not deposited (it is byte-identical to the author's) |
| `../data/runs/m1_N100.csv`, `m2_N100.csv` | input: per game `S_*` and `N_*` |
| `../data/runs/wfdata.py` | reads those tables in the shape of the original loader |

The original `fig5.py` drew both Figure 5 and SI Figure 5. This script is its SI half, with only the data loading
changed.

## Verification (2026-09-24)

The script was run on a fresh copy of the folders it needs. Its `SIFig5.pdf` is byte-identical to the published PDF
apart from the `CreationDate` stamp. The two are pixel-identical at 80 and 150 dpi (`pdftoppm`; max |diff| 0), and
`SIFig5.png` is byte-identical to the original preview.

The numbers in the legend reproduce. At memory two the shares on efficient and on stable strategies both exceed one half at 442 games,
and the competitive share exceeds one half at 101. At memory one the shares on efficient, stable and competitive strategies exceed
one half at 186, 314 and 342 games. At 109 games no property holds half the population, 105 of them in the
Snowdrift quadrant. See `../data/runs/check_numbers.py`.
