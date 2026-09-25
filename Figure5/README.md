# Figure 5: The share of the population with each property, in the two runs of Figure 4

Reproduces main text Figure 5 from the reduced output of two Wright–Fisher runs.

## What it shows

The two runs of Figure 4 (N = 1000, β = 100, μ = 10⁻², ε = 10⁻⁴): memory one in row **a**–**c** and memory two in
row **d**–**f**. Each column is one property, and each panel shows the share of the population held by the
strategies with that property, which is the sum of the shares of its atoms:

- **a**, **d**: efficient, `1**` = 100 + 110 + 111;
- **b**, **e**: stable, `*1*` = 010 + 110 + 011 + 111;
- **c**, **f**: competitive, `**1` = 001 + 011 + 111.

The scale is linear from 0 to 100 %. A cell is grey where no strategy of the space has the property at that game.
At memory one that is every game above the switch line for efficiency, and the Snowdrift games outside the unit
square for stability.

## Run

```
python3 fig5.py
```

It writes `Fig5.pdf` and `Fig5.png` (110 dpi) here. For each run it prints, per property, the mean, the median,
the minimum and the maximum share, the number of games above one half, and the number of games at which no
strategy has the property. It takes about 3 s.

## Files

| file | role |
|---|---|
| `fig5.py` | the plotting script: the original `fig5.py` with its data loading replaced |
| `Fig5.pdf` | the published figure (`figures/Fig5.pdf` of the paper), kept for comparison |
| `Fig5.png` | a 110-dpi preview the script writes beside the PDF; not deposited (it is byte-identical to the author's) |
| `../data/runs/m1_N1000.csv`, `m2_N1000.csv` | input: per game the atom shares `S_*` and the atom sizes `N_*` |
| `../data/runs/wfdata.py` | reads those tables in the shape of the original loader |
| `../common/furniture.py` | the frame of a disk panel, with the layout constants shared with Figure 4 |

The script sums the property shares from `S`, exactly as the original did. The tables also store them, as `P_eff`,
`P_nash` and `P_comp` (`P_nash` holds the share on stable strategies), and they are equal bit for bit (`../data/runs/check_numbers.py`). The original `fig5.py` also
drew SI Figure 5, which is `../SIFigure5/sifig5.py` and uses the same `draw()`.

## Verification (2026-09-24)

The script was run on a fresh copy of the folders it needs. Its `Fig5.pdf` is byte-identical to the published PDF
apart from the `CreationDate` stamp. The two are pixel-identical at 80 and 150 dpi (`pdftoppm`; max |diff| 0), and
`Fig5.png` is byte-identical to the original preview.

The printed numbers are those of the Results paragraph "Which properties the population has". At memory two the
mean efficient share is 0.954, the mean share on stable strategies 0.943 and the mean competitive share 0.368, and the competitive
share exceeds one half at 186 games. At memory one the efficient share exceeds one half at 186 games, the share on stable strategies
at 268 and the competitive share at 315. The joint counts, 509 games for memory two and 137 for memory one, are
recomputed in `../data/runs/check_numbers.py`.
