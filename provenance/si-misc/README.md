# provenance/si-misc: where SIFigure1, SITable1 and SITable8 came from

These three folders do not reduce any private output. SI Figure 1 is a TikZ source, and SI Tables 1 and 8 are
computed from the definitions. So nothing in them needs this folder. What is here documents their origin, and runs a
check against the author's private sources.

## Origins

| repository file | taken from (author's tree, 2026-09-24) | change |
|---|---|---|
| `SIFigure1/SIFig1.tex` | `CL1/PartnersRivals1/FinalFigures/SI/SIFig1.tex` (md5 `4c2eccddc4c52ff2c8dd9d89f2b7ea67`, the same as in `PartnersRivals/Figures/` and `PartnersRivals/FinalFigures/SI/`) | two comment lines |
| `SIFigure1/SIFig1.pdf` | `figures/SI/SIFig1.pdf` of the paper's LaTeX source, the published figure (built 2026-09-08) | none |
| `SITable8/sitable8.py` | the pair computation (polynomials in ε, Markov chain tree theorem: `transition`, `det3`, `limit_weights`) of `CL1/PartnersRivals1/FinalFigures/m1atoms.py`, the script behind `Figures/m1_atoms_k4.npz` (Figures 1b, 2a–g, 3a–d), and its per-game test `codes_at` and face points `interior` | the pair computation copied unchanged, except that the cofactors are split out into their own function; `codes_at` and `interior` adapted to exact face vertices; the region algebra, the table, the checks and `--m2` are new |
| `SITable1/sitable1.py` | new; its pair computation is that of `sitable8.py`, extended to probabilistic answers | — |
| the copies of SI Tables 1 and 8 inside the two scripts | `ms.tex`, the paper's LaTeX source | none |

## The check

```
python3 -B check_sources.py <manuscript>    # about 1 s; needs numpy, and what the original m1atoms.py imports
```

It works only in the author's environment. `AUTHOR_ROOT` at the top of the script is the one path to the private
sources, and it reads them without writing anything. `<manuscript>` is the folder of the paper's LaTeX source, with
`ms.tex` and the published figures in `figures/`. `check_sources.txt` is its output from 2026-09-25. **All
checks pass.** They show that:

1. `sitable8.py` gives exactly the 256 pair limits of the original `m1atoms.py`. The stability regions, efficient sets
   and rival sets of SI Table 8 reproduce the atom codes of all sixteen strategies on all 45 faces of
   `m1_atoms_k4.npz`, and its eleven lines.
2. The stability regions of SI Table 8, computed against the 16 memory-one co-players, equal strategy by strategy the
   stability regions in the exact memory-two census of the companion paper, which was computed against all 65536 memory-two
   co-players. That census is `CL/BinM2NE1/Final/Github/exact/ca1_regions.csv`, the source of the paper's stability regions
   (Methods). The self-play weights also agree.

   The census has the same three single-game equilibria as `sitable8.py` and SI Table 8: `DDCC` and `CCDD` at
   (0, 0) and `DCDC` at (1/2, −1/2). There, too, tit-for-tat is stable at no game.
3. The copies of SI Tables 1 and 8 inside `sitable1.py` and `sitable8.py` are the tables as typeset in `ms.tex`.
4. `SIFig1.tex` differs from its source in comment lines only, and `SIFig1.pdf` is the published file.
