# SI Figure 2: The share of the population in each atom, for the 16 binary memory-one strategies

Reproduces SI Figure 2 from the reduced output of the two memory-one Wright–Fisher runs.

## What it shows

Two runs over the 16 binary memory-one strategies, both at ε = 10⁻⁴ with uniform mutants and 10 replicates per game:

- **a**–**h**: N = 100, β = 3, μ = 10⁻⁴, with 10⁸ generations per replicate;
- **i**–**p**: N = 1000, β = 100, μ = 10⁻², with 10⁷ generations per replicate.

Panels **a**–**g** and **i**–**o** each show one atom (000, 100, 010, 001, 110, 011, 111). The colour is the share
of the population held by the atom's strategies, linear from 0 to 100 %, and grey where the atom has no strategy at
that game. Panels **h** and **p** colour each game by its most abundant atom, with the key below the last one.

## Run

```
python3 sifig2.py
```

It writes `SIFig2.pdf` and `SIFig2.png` (150 dpi) here. For each run it prints, per atom, the mean, the median, the
minimum and the maximum share, the number of empty games and the number of games the atom leads. It also prints the
median share of the most abundant atom and the number of games decided by less than 0.05. It takes about 5 s.

## Files

| file | role |
|---|---|
| `sifig2.py` | the plotting script, containing `draw_runs()`, the original `atomshares.draw_runs` |
| `SIFig2.pdf` | the published figure (`figures/SI/SIFig2.pdf` of the paper), kept for comparison |
| `SIFig2.png` | a 150-dpi preview the script writes beside the PDF; not deposited (it is byte-identical to the author's) |
| `../data/runs/m1_N100.csv`, `m1_N1000.csv` | input: per game the atom shares `S_*` and the atom sizes `N_*` |
| `../data/runs/wfdata.py` | reads those tables in the shape of the original loader |
| `../common/furniture.py`, `style.py`, `atoms.py` | the frame, the colours, the atom order and names |

`draw_runs()` served both SI Figures 2 and 3 in the original `atomshares.py`. It is carried here and in
`../SIFigure3/sifig3.py` unchanged, apart from where it takes its constants from and the output path.

Some games show as speckle: their ten replicates fixed in different basins, so the plotted share is the fraction of
the replicates in each basin (Methods) and falls between the values of the neighbouring games. The deposited tables
flag these games in the columns `split` and `split_sd` of `m1_N100.csv` and `m1_N1000.csv`: 59 games in the small run
and 11 in the large one, as in the Methods. The flags come from the per-replicate abundances, which are not deposited.

## Verification (2026-09-24)

The script was run on a fresh copy of the folders it needs. Its `SIFig2.pdf` is byte-identical to the published PDF
apart from the `CreationDate` stamp. The two are pixel-identical at 80 and 150 dpi (`pdftoppm`; max |diff| 0), and
`SIFig2.png` is byte-identical to the original preview.

The counts of the most abundant atom are those of the SI section "Memory one, for contrast":

- N = 100: 011 at 141 games, 111 at 126, 000 at 120, 110 at 63, 001 at 62.
- N = 1000: 000 at 154, 111 at 126, 001 at 90, 011 at 82, 110 at 60.

The median share of the most abundant atom is 1.00 (19 games decided by less than 0.05) and 0.96 (18 games), as in
the Methods.
