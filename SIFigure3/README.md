# SI Figure 3: The share of the population in each atom, for the 65536 binary memory-two strategies

Reproduces SI Figure 3 from the reduced output of the two memory-two Wright–Fisher runs.

## What it shows

SI Figure 2 for memory two. These are the runs of SI Figure 4d–f and main text Figure 4d–f, both at ε = 10⁻⁴ with
uniform mutants and 10 replicates per game:

- **a**–**h**: N = 100, β = 3, μ = 10⁻⁴, with 10⁸ generations per replicate;
- **i**–**p**: N = 1000, β = 100, μ = 10⁻², with 10⁷ generations per replicate.

Panels **a**–**g** and **i**–**o** show the share of the population held by each atom, linear from 0 to 100 %, and
grey where the atom has no strategy at that game. Panels **h** and **p** show the most abundant atom.

## Run

```
python3 sifig3.py
```

It writes `SIFig3.pdf` and `SIFig3.png` (150 dpi) here and prints the same per-atom summary as SI Figure 2. It
takes about 5 s.

## Files

| file | role |
|---|---|
| `sifig3.py` | the plotting script, containing `draw_runs()`, the original `atomshares.draw_runs` |
| `SIFig3.pdf` | the published figure (`figures/SI/SIFig3.pdf` of the paper), kept for comparison |
| `SIFig3.png` | a 150-dpi preview the script writes beside the PDF; not deposited (it is byte-identical to the author's) |
| `../data/runs/m2_N100.csv`, `m2_N1000.csv` | input: per game `S_*` and `N_*` |
| `../data/runs/wfdata.py` | reads those tables in the shape of the original loader |
| `../common/furniture.py`, `style.py`, `atoms.py` | the frame, the colours, the atom order and names |

In the author's project the shares came from the 65536 per-strategy abundances of each game. Those are the packed
`.bin` files of 134 MB and 253 MB, and they are not deposited. The atom shares reduced from them are deposited in
full precision, and the figure is drawn from those. `../provenance/four-runs/` holds the reduction, and a second,
independent reduction that it was checked against.

## Verification (2026-09-24)

The script was run on a fresh copy of the folders it needs. Its `SIFig3.pdf` is byte-identical to the published PDF
apart from the `CreationDate` stamp. The two are pixel-identical at 80 and 150 dpi (`pdftoppm`; max |diff| 0), and
`SIFig3.png` is byte-identical to the original preview.

The counts of the most abundant atom are those of SI Table 6. At N = 100: 110 at 364 games, 111 at 89, 000 at 24,
100 at 15, 011 at 15, 010 at 3 and 001 at 2. At N = 1000: 110 at 323, 111 at 186, 100 at 2 and 011 at 1. The median
share of the most abundant atom is 0.77 with 30 games decided by less than 0.05 at N = 100, and 0.92 with 1 game at
N = 1000, as in the Methods.
