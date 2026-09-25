# SI Figure 7 — efficient strict Nash equilibria at the error rate of the runs

This folder redraws SI Figure 7. It is SI Figure 6 restricted to the strict equilibria that are efficient in the limit
ε → 0: mutual cooperators below the switch line u + v = 1, alternators above it. No alternator is strict at any of the
512 games, so every game above the switch line is grey. Memory one is in row 1 (panels a–c), memory two in row 2 (d–f).

| column | panels | what |
|---|---|---|
| 1 | a, d | the number of efficient strict Nash equilibria at ε = 10⁻⁴: 0–2 at memory one (ALLC and WSLS), 0–128 at memory two; one count scale per panel, grey where there is none |
| 2 | b, e | the share of the population on them in the run at N = 100, β = 3, μ = 10⁻⁴ |
| 3 | c, f | the same in the run at N = 1000, β = 100, μ = 10⁻² |

Columns 2 and 3 are linear from 0 to 100 %, grey where the game has no efficient strict equilibrium.

## Reproduce

```
cd SIFigure7
python3 sifig7.py            # writes SIFig7.pdf here (about 3 s); --png also writes SIFig7.png at 110 dpi
```

Requirements: Python 3 with numpy and matplotlib. The published page was rendered with Python 3.10.9, numpy 1.23.5
and matplotlib 3.7.0, using matplotlib's bundled DejaVu Sans. With these versions the script reproduces the published
PDF byte for byte, apart from the creation date matplotlib embeds.

## Files

| file | what |
|---|---|
| `sifig7.py` | the entry point: `figstrict.draw(efficient=True, ...)` |
| `figstrict.py` | the sheet, identical to `../SIFigure6/figstrict.py` |
| `SIFig7.pdf` | the published figure, for comparison |

Inputs: the columns `n_eff_strict`, `share_eff_F2` and `share_eff_F1` of `../data/strict/m1_games.csv` and
`../data/strict/m2_games.csv` (`F2`: N = 100, `F1`: N = 1000), and `../data/games/` through `../common`. See
`../data/strict/README.md`, and `../SIFigure6/README.md` for how the script relates to the author's original.

Output: `SIFig7.pdf` (16.68 × 11.00 in).

## Verification (2026-09-24)

This was done as for SI Figure 6, in a fresh copy of the folders, against the published `figures/SI/SIFig7.pdf`:

| resolution | max \|diff\| | mean \|diff\| | differing pixels |
|---|---|---|---|
| 80 dpi | 0 | 0 | 0 |
| 150 dpi | 0 | 0 | 0 |

The two PDFs are byte-identical apart from `/CreationDate`: both are 323027 bytes.
