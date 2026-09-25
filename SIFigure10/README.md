# SI Figure 10: the small-population run of SI Figure 4 at three error rates

The 65536 binary memory-two strategies at N = 100, β = 3, μ = 10⁻⁴, with 10 replicates of 10⁸ generations per game.
There is one row per error rate:

- **a–c**, ε = 10⁻³ (run `el_e3`);
- **d–f**, ε = 10⁻⁴ (run `f2_e4`, SI Figure 4d–f);
- **g–i**, ε = 10⁻⁵ (run `el_e5`).

The columns are those of main text Figure 4: the efficiency, the most abundant atom and the most enriched atom. The
counts are SI Table 7b.

## Command

```
python3 SIFigure10/sifig10.py          # from the repository root; ~3 s
```

It writes `SIFigure10/SIFig10.pdf` and a 110-dpi preview `SIFig10.png`. The PDF deposited here is the published
figure, byte for byte; the preview is not deposited. It also prints:

```
el e3: most abundant atom agrees with eps = 1e-4 at 480 of 512 games; friendly rivals win 109 (1e-4: 89); efficiency below 0.9 at 88 (1e-4: 91); mean efficiency 0.909 (1e-4: 0.913)
el e5: most abundant atom agrees with eps = 1e-4 at 500 of 512 games; friendly rivals win 89 (1e-4: 89); efficiency below 0.9 at 90 (1e-4: 91); mean efficiency 0.913 (1e-4: 0.913)
```

## Inputs

- `data/robustness/games_{el_e3,f2_e4,el_e5}.csv` and `m2_atom_sizes.csv`, read through `data/robustness/wfruns.py`.
- `common/` and `data/games/`.

This is the SI Figure 10 half of the original `FinalFigures/sifig9.py` (see `SIFigure9/`). The drawing is unchanged.
The loading and the output path differ.

## Requirements

Python 3 with numpy and matplotlib. The pixel identity below was obtained with Python 3.10.9, numpy 1.23.5 and
matplotlib 3.7.0 (its bundled DejaVu Sans); other matplotlib versions may differ in antialiasing and text placement.

## Verification (2026-09-24)

The script was run from a fresh copy, with Python 3.10.9, numpy 1.23.5 and matplotlib 3.7.0.

- The figure is **identical** to the published `SIFig10.pdf` at 80 and 150 dpi (`pdftoppm`): max |diff| 0, mean 0.
- The PDFs differ only in their `/CreationDate`.
- The preview PNG is byte-identical to the original's.
