# Figure 4: What evolution selects, for memory one and memory two, in a large population

Reproduces main text Figure 4 from the reduced output of two Wright–Fisher runs.

## What it shows

Six disks on the 512 sampled games, one Voronoi cell per game. Row **a**–**c** is memory one (the 16 binary
memory-one strategies) and row **d**–**f** memory two (the 65536 binary memory-two strategies). Both runs have
N = 1000, β = 100, μ = 10⁻², ε = 10⁻⁴, uniform mutants and 10 replicates of 10⁷ generations per game, with the
second half of each replicate sampled.

- **a**, **d**: the realised efficiency, the mean per-round payoff divided by E_max = max(R, (S + T)/2). The scale is
  viridis from 0 to 1, black where the mean payoff is negative.
- **b**, **e**: the most abundant atom, the atom with the largest share of the population.
- **c**, **f**: the most enriched atom, the atom with the largest ratio of its share of the population to its share of
  the strategy space.

The atoms are written efficient–stable–competitive, in the ε → 0 classification.

## Run

```
python3 fig4.py
```

It writes `Fig4.pdf` and `Fig4.png` (110 dpi) here, and prints a receipt for each run. The receipt gives the
efficiency range, the number of games with efficiency below 0.9 and the game counts of the two winners. The script
takes about 3 s.

## Files

| file | role |
|---|---|
| `fig4.py` | the plotting script |
| `Fig4.pdf` | the published figure (`figures/Fig4.pdf` of the paper), kept for comparison |
| `Fig4.png` | a 110-dpi preview the script writes beside the PDF; not deposited (it is byte-identical to the author's) |
| `../data/runs/m1_N1000.csv`, `m2_N1000.csv` | input: per game, the efficiency `E`, the atom shares `S_*` and the atom sizes `N_*` |
| `../data/runs/wfdata.py` | reads those tables in the shape of the original loader |
| `../data/games/` | the 512 games and their cells, through `common.games` |
| `../common/wfsheet.py` | the sheet, `draw()`, and the choice of the two winners, `winners()` |

The script is the original `fig4.py` with its data loading replaced. It computes the most abundant and the most
enriched atom from `S` and `N` in `common.wfsheet.winners`, as the original did. The tables also store the two
winners, in the columns `abundant` and `enriched`, and `../data/runs/check_numbers.py` confirms that they agree. The
original script also drew SI Figure 4, which is now in `../SIFigure4/`.

## Verification (2026-09-24)

The script was run on a fresh copy of `Figure4/`, `common/`, `data/games/` and `data/runs/`. It produced a `Fig4.pdf`
that is byte-identical to the published PDF apart from its `CreationDate` stamp. The two PDFs, rasterised with
`pdftoppm` at 80 and 150 dpi, are pixel-identical: max |diff| 0, mean |diff| 0. `Fig4.png` is byte-identical to the
original preview. The software was Python 3.10.9, numpy 1.23.5 and matplotlib 3.7.0.

The counts in the receipt are those of the text. At memory two, 110 is the most abundant atom at 323 games and 111
at 186, 111 is the most enriched atom at 261 and 110 at 249, and the efficiency is below 0.9 at 10 games. At memory
one the efficiency is below 0.9 at 324 games and negative at 77. See `../data/runs/README.md`.
