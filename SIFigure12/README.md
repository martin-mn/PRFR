# SI Figure 12: the large-population run of main text Figure 4 under four mutation kernels

The 65536 binary memory-two strategies at N = 1000, β = 100, μ = 10⁻², ε = 10⁻⁴, with 10 replicates of 10⁷
generations per game. A mutating individual adopts, with probability ν, a strategy drawn uniformly from all 65536.
Otherwise it adopts the strategy that differs from its own at one of the sixteen positions, chosen uniformly. There
is one row per kernel:

- **a–c**, ν = 0 (run `lm_g0_e4`);
- **d–f**, ν = 0.1 (`lm_g01_e4`);
- **g–i**, ν = 0.5 (`lm_g05_e4`);
- **j–l**, ν = 1 (`f1_e4`, main text Figure 4d–f).

The columns are those of main text Figure 4. The counts are SI Table 7c.

## Command

```
python3 SIFigure12/sifig12.py          # from the repository root; ~4 s
```

It writes `SIFigure12/SIFig12.pdf` and a 110-dpi preview `SIFig12.png`. The PDF deposited here is the published
figure, byte for byte; the preview is not deposited. It also prints:

```
nu = 0: most abundant atom as at nu = 1 at 461 of 512 games; friendly rivals most abundant at 149 (nu = 1: 186), most enriched at 324 (nu = 1: 261); efficiency below 0.9 at 3 (nu = 1: 10); mean 0.987 (nu = 1: 0.974)
nu = 0.1: most abundant atom as at nu = 1 at 469 of 512 games; friendly rivals most abundant at 157 (nu = 1: 186), most enriched at 331 (nu = 1: 261); efficiency below 0.9 at 7 (nu = 1: 10); mean 0.983 (nu = 1: 0.974)
nu = 0.5: most abundant atom as at nu = 1 at 494 of 512 games; friendly rivals most abundant at 176 (nu = 1: 186), most enriched at 326 (nu = 1: 261); efficiency below 0.9 at 8 (nu = 1: 10); mean 0.977 (nu = 1: 0.974)
```

The remaining numbers of the paragraph "The mutation kernel" come from `SITable7/sitable7.py`: the games 100 and 000
lead, the replicates' top strategies, and the agreement of the replicates.

## Inputs

- `data/robustness/games_{lm_g0_e4,lm_g01_e4,lm_g05_e4,f1_e4}.csv` and `m2_atom_sizes.csv`, read through
  `data/robustness/wfruns.py`.
- `common/` and `data/games/`.

This is the original `FinalFigures/sifiglm.py` with the loading and the output path changed.

## Requirements

Python 3 with numpy and matplotlib. The pixel identity below was obtained with Python 3.10.9, numpy 1.23.5 and
matplotlib 3.7.0 (its bundled DejaVu Sans); other matplotlib versions may differ in antialiasing and text placement.

## Verification (2026-09-24)

The script was run from a fresh copy, with Python 3.10.9, numpy 1.23.5 and matplotlib 3.7.0.

- The figure is **identical** to the published `SIFig12.pdf` at 80 and 150 dpi (`pdftoppm`): max |diff| 0, mean 0.
- The PDFs differ only in their `/CreationDate`.
- The preview PNG is byte-identical to the original's.
