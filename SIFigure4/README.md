# SI Figure 4: Main text Figure 4 for the small population

Reproduces SI Figure 4 from the reduced output of two Wright–Fisher runs.

## What it shows

The layout of main text Figure 4, for the runs at N = 100, β = 3, μ = 10⁻⁴, ε = 10⁻⁴, uniform mutants and 10
replicates of 10⁸ generations per game, with the second half of each replicate sampled. Row **a**–**c** is memory one
(16 strategies) and row **d**–**f** memory two (65536 strategies). The left column is the realised efficiency (black
where the mean payoff is negative), the middle column the most abundant atom and the right column the most enriched
atom.

## Run

```
python3 sifig4.py
```

It writes `SIFig4.pdf` and `SIFig4.png` (110 dpi) here and prints the receipt of each run. It takes about 3 s.

## Files

| file | role |
|---|---|
| `sifig4.py` | the plotting script |
| `SIFig4.pdf` | the published figure (`figures/SI/SIFig4.pdf` of the paper), kept for comparison |
| `SIFig4.png` | a 110-dpi preview the script writes beside the PDF; not deposited (it is byte-identical to the author's) |
| `../data/runs/m1_N100.csv`, `m2_N100.csv` | input: per game `E`, `S_*` and `N_*` |
| `../data/runs/wfdata.py` | reads those tables in the shape of the original loader |
| `../common/wfsheet.py` | the sheet and the choice of the two winners, shared with Figure 4 |

The original `fig4.py` drew both Figure 4 and SI Figure 4. This script is its SI half. The only change is the data
loading.

## Verification (2026-09-24)

The script was run on a fresh copy of the folders it needs. Its `SIFig4.pdf` is byte-identical to the published PDF
apart from the `CreationDate` stamp. The two are pixel-identical at 80 and 150 dpi (`pdftoppm`; max |diff| 0), and
`SIFig4.png` is byte-identical to the original preview.

The legend says that at memory two the most enriched atom is 111 in 379 games and 110 in 120; the receipt gives
the same counts. The receipt also agrees with SI Table 6: the efficiency is below 0.9 at 91 games at memory two.
See `../data/runs/README.md`.
