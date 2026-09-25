# provenance/strict — how data/strict was made

This folder records how the tables of `../../data/strict` were made from outputs that are not deposited. Those tables
are the data of SI Figures 6 and 7 and of the Methods paragraph "Strict equilibria". The scripts here run only in the
author's environment. To check the tables without it, use `../../data/strict/check_strict.py` and
`recompute_sets.py`: they need nothing but the repository.

| file | what |
|---|---|
| `reduce_strict.py` | reads the private full outputs and writes the five tables of `data/strict` |
| `bruteforce/` | the double-precision brute-force scan and its quadruple-precision re-adjudication (Fortran), as run for the comparison the Methods describe |

## reduce_strict.py

```
python3 -B reduce_strict.py [outdir]        # default ../../data/strict; about 20 s, 1.6 GB of memory
```

The one path to the private tree is the variable `AUTHOR_ENV` at the top (the author's environment); everything
under it is only read. `-B` (and `sys.dont_write_bytecode` in the script) keeps Python from writing bytecode into the
private folders it imports from. The script uses these unchanged original modules:

| module | gives |
|---|---|
| `PartnersRivals/FinalFigures/strictne.py` | the data module of the original `figstrict.py`: `m1()` (the memory-one sets, exact), `m1_efficient()`, `m1_shares()`, `m2()` and `m2eff()` (the per-game memory-two numbers the figures were drawn from, cached in `PartnersRivals/Figures/strictne_m2.npz` and `strictne_m2eff.npz`), `_walk()` (the abundance vector π of every game of a memory-two run) |
| `DiskM2WF/Opt/ne16.py` | `verdicts(u, v)`: the weak and the strict set among the 65536 at a game at ε = 1/10000 |
| `DiskM2WF/Opt/exact.py` | `load()`, `masks()`: the ε → 0 census, whose self-play weights give the mutual cooperators (7639) and the alternators (3072), hence the efficient set of a game |
| `DiskM1WF/Opt/m1load.py`, `m1disk.py` | the memory-one run packs (the counts of the 16 strategies per game) and the exact ε → 0 classification of the 16 |

### Inputs (private)

- **The memory-two runs.** Their abundance vectors are DiskM2WF `Data/dw2_e4.{idx,bin}` (run F2: N = 100, β = 3,
  μ = 10⁻⁴; Cannon array 45049704) and `Data/dw1_e4.{idx,bin}` (run F1: N = 1000, β = 100, μ = 10⁻²; array 44394541),
  both at ε = 10⁻⁴. These are the runs of SI Figure 4 and main Figure 4. The .bin files hold 65536 numbers per game.
- **The memory-one runs.** DiskM1WF `Data/mw2_e4.tsv` (N = 100) and `mw1_e4.tsv` (N = 1000): per game, the count of
  each of the 16 strategies over the sampled individual-generations. They are deposited whole as
  `data/runs/m1_N100_counts.csv` and `m1_N1000_counts.csv`, and the counts of `data/strict/m1_sets.csv` equal them.
- **The one-flip half-planes.** DiskM2WF `Data/ne16_e4/` holds, for each of the 65536 residents, the sixteen one-flip
  gains at ε = 1/10000 as primitive integer triples (a, b, c), with gain ∝ a + b u + c v. They were built by
  `exact/exactcoef.py` (`exact16`) of github.com/martin-mn/MapBinM2 (`python3 ne16.py build`). `ne16.verdicts` decides
  each sign in double precision only where an error bound certifies it, and otherwise in exact integers. On these 512
  games every sign was certified: 0 were referred, and the smallest relative margin was 5.3 × 10⁻⁹.
- **The limit census.** DiskM2WF `Data/exactlayer.npz`, built from MapBinM2's `exact/ca1_regions.csv`.
- **The brute-force scan.** DiskM2IN `Data/ne/n100b3sun/ne_<gid>.bin`, 512 files of 65536 doubles, 256 MB. Each holds
  the margin π(s, s) − max over the 65535 others t of π(t, s), computed in double precision by `bruteforce/nescan.f90`
  (Cannon array 45022524, 8 tasks of 64 games). The games it read are `DiskM2IN/Cannon/dk1/games_sun.dat`, whose
  cS = u and cT = 1 + v the script checks against `data/games` bit for bit.
- **The re-adjudication.** `Data/ne/n100b3sun/QUADFIX.dat` from `bruteforce/neq.f90`. The 2014 scan verdicts with
  |margin| ≤ 10⁻¹⁴, of both signs, were recomputed in quadruple precision. 160 flipped, all from "not strict" to
  "strict", and none the other way.

### What it writes, and what it checks

- `m1_games.csv`, `m1_sets.csv`:
  - from `strictne.m1(compare_m2=True)`; the script asserts that weak = strict at every game, and that strictness among
    the 16 equals strictness against all 65536 memory-two deviations (`ne16` at the embedded codes);
  - the shares are those of `strictne.m1_shares`, and the script asserts that they are exactly the counts over `ntot`.
- `m2_games.csv`:
  - the per-game numbers exactly as the figures used them (`strictne.m2()`, `m2eff()`);
  - plus `n_strict_float64`, the brute-force count (m > 0).
- `m2_sets.csv`:
  - one row per (game, resident) of `ne16.verdicts`, with the flags from `exact.masks` and the census, and π from
    `strictne._walk`;
  - the script asserts that the rows reproduce every per-game count, and that `pi[strict].sum()` reproduces every
    per-game share of the caches to the last bit. The receipt shows max |diff| = 0 for all four share columns.
- `m2_float64_check.csv`:
  - every (game, resident) where the brute force (m > 0) and the exact set disagree;
  - the script asserts that this set is exactly the 160 lines of `QUADFIX.dat`, that there is no pair the other way
    round, and that each double margin equals the QUADFIX value to the 13 digits printed there.

The receipt of the run of 2026-09-24:

```
memory two: 0 signs referred to exact integers by ne16 (0 = every verdict certified by the float screen)
memory two: per-game shares recomputed from pi vs the figure's caches, max |diff|: all F1 0, all F2 0, eff F1 0, eff F2 0
wrote .../data/strict: m1_games.csv, m1_sets.csv (1263 rows), m2_games.csv, m2_sets.csv (65547 rows), m2_float64_check.csv (160 rows)
```

## bruteforce/

This is the program behind the Methods sentence "... and by a brute-force comparison of every resident against all
65535 alternatives in double precision". It was part of the companion project DiskM2IN and was run on the Cannon
cluster. The files are copied unchanged.

| file | what |
|---|---|
| `nescan.f90` | for every game and every resident s, the margin π(s, s) − max over t ≠ s of π(t, s) over all 65535 t, in double precision. `./nescan.x <games.dat> <first> <last> <keps> <simdir> <outdir>` (rows of games.dat, keps = 4 for ε = 10⁻⁴). It writes `ne_<gid>.bin` (the 65536 margins) and `ne_<gid>.dat` (a summary; simdir supplies that project's own abundance vector, used only for the summary's mass column) |
| `payf2.f`, `payf3.f` | the pair chain of two memory-two strategies at ε, its stationary outcome frequencies by state reduction (GTH), in double precision; `payf2ini` sets up the tables |
| `neq.f90` | the re-adjudication: the same margin over all 65535 alternatives, for a list of (gid, s), with `payf2.f` and `payf3.f` compiled unchanged under `-freal-8-real-16`, which makes every double a real(16) |
| `neprod.slurm` | the production array (8 tasks × 64 games, one 112-core node each) |

`neq.x` was built and run as

```
gfortran -O2 -fopenmp -fwrapv -freal-8-real-16 -J$BD -I$BD -o neq.x neq.f90 payf3.f payf2.f
OMP_NUM_THREADS=12 ./neq.x games_sun.dat <candfile> 4 <out>     # candfile: "gid s margin_double" per line, by gid
```

It took 1960 core-seconds for the 2014 candidates. The build line of `nescan.x` was not recorded. The kit compiled its
other programs, which use the same `payf3.f` and `payf2.f`, with
`ifx -O3 -xHost -fp-model precise -qopenmp -auto` (module `intel/25.2.1-fasrc01` on Cannon). `-auto` matters there, because
`payf3` is called inside an OpenMP region. `nescan.f90` estimates its own cost at about 431 core-hours for the 512
games.

Why the double scan and the exact test differ at 160 pairs: the margin is a difference of two payoffs of order one,
while the true margins of these residents are of order ε⁴ ≈ 10⁻¹⁶. One unit in the last place of a payoff near 1 is
2.2 × 10⁻¹⁶. The sixteen one-flip half-planes avoid the subtraction. So does the bias formulation of
`data/strict/recompute_sets.py`.
