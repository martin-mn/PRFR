# SI Figure 9: the large-population run of main text Figure 4 at three error rates

The 65536 binary memory-two strategies at N = 1000, β = 100, μ = 10⁻², with 10 replicates of 10⁷ generations per
game. There is one row per error rate:

- **a–c**, ε = 10⁻³ (run `eh_e3`);
- **d–f**, ε = 10⁻⁴ (run `f1_e4`, main text Figure 4d–f);
- **g–i**, ε = 10⁻⁵ (run `eh_e5`).

The columns are those of main text Figure 4: the efficiency, the most abundant atom and the most enriched atom. The
atoms are the ε → 0 classification in every row. The counts are SI Table 7b.

## Command

```
python3 SIFigure9/sifig9.py            # from the repository root; ~3 s
```

It writes `SIFigure9/SIFig9.pdf` and a 110-dpi preview `SIFig9.png`. The PDF deposited here is the published
figure, byte for byte; the preview is not deposited. It also prints the lines the text
of the SI quotes:

```
eh e3: most abundant atom agrees with eps = 1e-4 at 494 of 512 games; friendly rivals win 184 (1e-4: 186); efficiency below 0.9 at 43 (1e-4: 10); mean efficiency 0.957 (1e-4: 0.974)
eh e5: most abundant atom agrees with eps = 1e-4 at 508 of 512 games; friendly rivals win 184 (1e-4: 186); efficiency below 0.9 at 10 (1e-4: 10); mean efficiency 0.976 (1e-4: 0.974)
```

## Inputs

- `data/robustness/games_{eh_e3,f1_e4,eh_e5}.csv` and `m2_atom_sizes.csv`, read through `data/robustness/wfruns.py`.
- `common/` (`wfsheet.draw`, the sheet of main text Figure 4) and `data/games/`.

The original `FinalFigures/sifig9.py` drew SI Figures 9 and 10 in one script. This is its SI Figure 9 half; the
other half is `SIFigure10/sifig10.py`. The drawing is unchanged. The loading and the output path differ.

## Requirements

Python 3 with numpy and matplotlib. The pixel identity below was obtained with Python 3.10.9, numpy 1.23.5 and
matplotlib 3.7.0 (its bundled DejaVu Sans); other matplotlib versions may differ in antialiasing and text placement.

## Verification (2026-09-24)

The script was run from a fresh copy of `common/`, `data/games/`, `data/robustness/` and this folder, with Python
3.10.9, numpy 1.23.5 and matplotlib 3.7.0. The new PDF and the published `SIFig9.pdf` were rasterised with `pdftoppm`.

- The figure is **identical** at 80 and 150 dpi: max |diff| 0, mean 0.
- The PDFs differ only in their `/CreationDate`.
- The preview PNG is byte-identical to the original's.
