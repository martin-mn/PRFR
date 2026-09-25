# SI Figure 1: feasible payoffs and the two half-planes behind the theorem

A standalone TikZ picture with three panels, each in the plane of pairs (own payoff, co-player's payoff):

- **a**, below the switch line, at (R, S, T, P) = (3, 0, 5, 1): the feasible quadrilateral, the line
  x + y = 2E_max and the rival's half-plane.
- **b**, above the switch line, at (3, 1, 6, 0): the feasible set is a triangle and E_max = (T + S)/2.
- **c**, the one-shot game A = (1 3; 2 0) of SI §2.

The argument the figure illustrates is in SI §1 (*Repeated play with rare errors*) and SI §2 (*Definitions and
the theorem*); the legend is with the SI figure legends. The figure contains no computed data. Every coordinate is
written in `SIFig1.tex`.

## Reproducing

```
sh build.sh          # or: pdflatex SIFig1.tex
```

This needs pdflatex with the packages `standalone`, `tikz` (libraries `arrows.meta` and `calc`), `times`, `amsmath`
and `amssymb`. The published PDF was made with pdfTeX 1.40.26 (TeX Live 2024). `build.sh` compiles in a temporary
directory and writes only `SIFig1.pdf` here.

## Files

| file | what it is |
|---|---|
| `SIFig1.tex` | the source, `FinalFigures/SI/SIFig1.tex` of the paper. Only two comment lines were changed (the header, and a stale "3x3" in the panel-c comment); the drawing code is untouched |
| `build.sh` | the build |
| `SIFig1.pdf` | the published figure, byte for byte (md5 `864973f6e680bb58e24167d871d11d61`, 77823 bytes, 429.5 × 168.8 pt) |

## Verification (2026-09-24)

`SIFig1.tex` was rebuilt from a fresh copy with `build.sh`. The rebuilt PDF's page content and font streams are
byte-identical to the published PDF's. The files differ only in the PDF info dictionary: the creation and
modification dates, and hence the `/ID` and the cross-reference offsets. Rasterised with `pdftoppm` at 80 and 300
dpi, the two are **identical**: max |diff| = 0, mean |diff| = 0.
