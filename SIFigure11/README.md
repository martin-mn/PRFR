# SI Figure 11: how certain the two memory-two maps are, game by game

The 512 games in the frame of main text Figure 4, for the memory-two runs at N = 100, β = 3, μ = 10⁻⁴ (**a–c**; run
`f2_e4`, SI Figure 4d–f) and at N = 1000, β = 100, μ = 10⁻² (**d–f**; run `f1_e4`, main text Figure 4d–f).

- **a, d**: the margin of the most abundant atom, the largest atom share of the pooled population minus the second
  largest.
- **b, e**: the standard deviation of the realised efficiency over the ten replicates, saturated at 0.2.
- **c, f**: how many of the ten replicates have, as their own most abundant atom, the atom of the pooled map. This is
  read from the exact per-replicate atom shares of the bit-for-bit regenerations `f1_e4` and `f2_e4`.

## Command

```
python3 SIFigure11/sifig11.py          # from the repository root; ~3 s
```

It writes `SIFigure11/SIFig11.pdf` and a 110-dpi preview `SIFig11.png`. The PDF deposited here is the published
figure, byte for byte; the preview is not deposited. It then prints the numbers of
the SI paragraph "Replicates", first for the two runs drawn:

```
f2_e4 (N = 100): margin median 0.58, ...; efficiency s.d. ... above 0.1 at 14; ...; exact agreement all ten at 412, five or fewer at 11; single-replicate maps: 111 leads 90-101 games (pooled 89), ...
f1_e4 (N = 1000): margin median 0.87, ...; efficiency s.d. ... above 0.1 at 3; ...; exact agreement all ten at 487, five or fewer at 0; single-replicate maps: 111 leads 185-190 games (pooled 186), ...
```

It then prints the same line for each of the eleven further runs with per-replicate output. These are `c1`–`c4`,
`eh_e3`, `eh_e5`, `el_e3`, `el_e5` and the three `lm` runs; `dw3` and `dw4` have none. Among them `c4_e4`
(N = 1000, β = 3, μ = 10⁻⁴) is the exception the text names: all ten replicates agree at only 248 games. The other
ten agree at 392 to 483 games. Naming runs on the command line restricts this report to them.

## Inputs

- `data/robustness/games_{f2_e4,f1_e4}.csv`: the pooled shares and the efficiency.
- `data/robustness/replicates_<run>.csv`: each replicate's efficiency and atom shares, and its most abundant strategy
  and that strategy's atom (the "rank-1 proxy" the script also reports).
- `common/` and `data/games/`.

The standard deviation in b and e is computed from the ten replicate efficiencies with ddof = 1. It equals the
`efsd` the simulator wrote, to the 8 decimals of the replicate files.

The script is the original `FinalFigures/sifig11.py`, with the drawing unchanged. The original took the pooled
shares from the packs of the original runs `dw2` and `dw1` and the replicates from their regenerations `f2`, `f1`.
Here both come from the regenerations, whose packs are byte-identical to the originals (`data/robustness/README.md`,
which also lists the names these two runs have in the other folders: `dw1` = `f1` = `f1_e4` = `m2_N1000` = `F1`, and
`dw2` = `f2` = `f2_e4` = `m2_N100` = `F2`).

## Requirements

Python 3 with numpy and matplotlib. The pixel identity below was obtained with Python 3.10.9, numpy 1.23.5 and
matplotlib 3.7.0 (its bundled DejaVu Sans); other matplotlib versions may differ in antialiasing and text placement.

## Verification (2026-09-24)

The script was run from a fresh copy, with Python 3.10.9, numpy 1.23.5 and matplotlib 3.7.0.

- The figure is **identical** to the published `SIFig11.pdf` at 80 and 150 dpi (`pdftoppm`): max |diff| 0, mean 0.
- The PDFs differ only in their `/CreationDate`.
- The preview PNG is byte-identical to the original's.
- Every number printed for the text equals the one in the SI: 0.58 and 0.87; 412 and 487; 11 and 0; 90–101 and
  185–190; 14 and 3 Stag Hunts; 248 for `c4_e4`.
