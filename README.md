# Code and data for: Partners, rivals, and friendly rivals in the evolution of direct reciprocity

Code and data to reproduce every figure and table in the paper and its
Supplementary Information.

Martin A. Nowak, Department of Mathematics and Department of Organismic and
Evolutionary Biology, Harvard University.

Archived on Zenodo: release 1.0.0, [doi:10.5281/zenodo.22964493](https://doi.org/10.5281/zenodo.22964493)
(all versions: [doi:10.5281/zenodo.22964492](https://doi.org/10.5281/zenodo.22964492)). MIT licence.

## What is computed

A strategy of a repeated game is *efficient* if a population using it earns the
largest average payoff any pair of players can attain, *stable* if it is a
symmetric Nash equilibrium against a single deviant, that is, if no rare mutant
does better than the residents do among themselves, and *competitive* (a
*rival*) if no co-player earns more than it does. Stability in this sense is
the first of Maynard Smith's two conditions for an evolutionarily stable
strategy, and the only one asked for. Partners are efficient and stable, and
friendly rivals are efficient and competitive. The paper shows that an
efficient competitive strategy is always stable. It then classifies all 16 binary memory-one strategies
and all 2<sup>16</sup> = 65536 binary memory-two strategies at every symmetric
two-player game, in the limit of rare errors ε → 0. Each strategy falls
into one of the *atoms* `000` … `111`, written efficient–stable–competitive, and
`101` is empty by the theorem. The classification is exact. It uses a census of
the 65536 strategies in exact rational arithmetic, with a second run in double
precision, and the exact arrangement of the plane of games into faces on which
the set of stable strategies is constant. Finally, the paper follows the evolution of both strategy
spaces at 512 sampled games with a Wright–Fisher process with pairwise
comparison, in 17 parameter settings, each run on a cluster with ten replicates
per game. This repository holds the census programs, the simulator with the
seed of every replicate, the reduced output of the census and of the
simulations, one folder per display item with the script that redraws or
recomputes it from the deposited data, and the notes to which the Supplementary
Information refers.

## Layout

One folder per display item, named as the paper names it, plus the code and the
data they share:

```
Figure1 … Figure5          the five main-text figures
SIFigure1 … SIFigure12     the twelve Supplementary Information figures
SITable1 … SITable8        the eight Supplementary Information tables
common/                    shared drawing code: the 512 games and their cells, the disk map, atoms, colours, sheets
data/                      the deposited (reduced) data that the display folders read
census/                    the exact eps -> 0 pair computation of the 65536 strategies, with its check program
families/                  the family descriptions of the friendly rivals
simulator/                 the Wright–Fisher simulator as it ran on the cluster, and the seeds of every run
notes/                     the notes deposited with the code, to which the SI refers
provenance/                how data/ was reduced from the full outputs (runs only in the author's environment)
reproduce_all.sh           runs every figure and table script in turn, then the checkers
```

A display folder holds:

- the script that makes the item;
- the published figure: the PDF if it is under 5 MB, otherwise a 150-dpi PNG
  preview;
- a `README.md` that says what the item shows, which command makes it, what it
  reads and writes, and how it was checked against the published figure.

The scripts read their inputs from `data/`, `common/` and their own folder. SI
Tables 2–5 also read `census/censuslib.py`, and SI Table 4 also reads
`families/`. Each script finds these files from its own location, so it runs
from its folder or from the repository root alike. Only the scripts in
`provenance/` read anything outside the repository.

## Display items

The command is run inside the item's folder. The input is under `data/` unless
another folder is named. The times are for one core of an Apple M2 Pro.

| display item | folder | command | input | time |
|---|---|---|---|---:|
| **Figure 1**: the three properties, their atoms, and which atoms are empty at each game | `Figure1` | `python3 fig1.py` | `arrangement/` (memory one and memory two) | 9 s |
| **Figure 2**: the number of strategies in each atom at every game | `Figure2` | `python3 fig2.py` | `arrangement/` | 16 s |
| **Figure 3**: the number of strategies with each property at every game | `Figure3` | `python3 fig3.py` | `arrangement/` | 9 s |
| **Figure 4**: what evolution selects, in a large population | `Figure4` | `python3 fig4.py` | `runs/m1_N1000.csv`, `m2_N1000.csv` | 3 s |
| **Figure 5**: the share of the population with each property | `Figure5` | `python3 fig5.py` | `runs/m1_N1000.csv`, `m2_N1000.csv` | 2 s |
| **SI Figure 1**: feasible payoffs and the two half-planes behind the theorem | `SIFigure1` | `sh build.sh` (pdflatex) | none (TikZ source) | 1 s |
| **SI Figure 2**: the share of each atom, memory one, both runs | `SIFigure2` | `python3 sifig2.py` | `runs/m1_N100.csv`, `m1_N1000.csv` | 5 s |
| **SI Figure 3**: the share of each atom, memory two, both runs | `SIFigure3` | `python3 sifig3.py` | `runs/m2_N100.csv`, `m2_N1000.csv` | 5 s |
| **SI Figure 4**: main text Figure 4 for the small population | `SIFigure4` | `python3 sifig4.py` | `runs/m1_N100.csv`, `m2_N100.csv` | 2 s |
| **SI Figure 5**: main text Figure 5 for the small population | `SIFigure5` | `python3 sifig5.py` | `runs/m1_N100.csv`, `m2_N100.csv` | 3 s |
| **SI Figure 6**: strict Nash equilibria at ε = 10⁻⁴ and the share of the population on them | `SIFigure6` | `python3 sifig6.py` | `strict/m1_games.csv`, `m2_games.csv` | 2 s |
| **SI Figure 7**: the same for the efficient strict Nash equilibria | `SIFigure7` | `python3 sifig7.py` | `strict/m1_games.csv`, `m2_games.csv` | 3 s |
| **SI Figure 8**: the cube of population size, selection strength and mutation rate | `SIFigure8` | `python3 sifig8.py` | `robustness/` (the eight corners) | 6 s |
| **SI Figure 9**: the large-population run at three error rates | `SIFigure9` | `python3 sifig9.py` | `robustness/` (`eh_e3`, `f1_e4`, `eh_e5`) | 3 s |
| **SI Figure 10**: the small-population run at three error rates | `SIFigure10` | `python3 sifig10.py` | `robustness/` (`el_e3`, `f2_e4`, `el_e5`) | 3 s |
| **SI Figure 11**: how certain the two memory-two maps are, game by game | `SIFigure11` | `python3 sifig11.py` | `robustness/` (pooled and per-replicate tables) | 3 s |
| **SI Figure 12**: the large-population run under four mutation kernels | `SIFigure12` | `python3 sifig12.py` | `robustness/` (`lm_g0_e4`, `lm_g01_e4`, `lm_g05_e4`, `f1_e4`) | 4 s |
| **SI Table 1**: classical strategies of the repeated Prisoner's Dilemma | `SITable1` | `python3 sitable1.py` | none (exact, from the definitions) | 3 s |
| **SI Table 2**: the four quarter-planes | `SITable2` | `python3 sitable2.py` | `census/census.csv` | 1 s |
| **SI Table 3**: the counts at one game | `SITable3` | `python3 sitable3.py` | `census/census.csv`, `census_double.csv` | 1 s |
| **SI Table 4**: the families of friendly rivals | `SITable4` | `python3 sitable4.py` | `census/census.csv`, `families/` | 1 s |
| **SI Table 5**: where the four atoms that can be empty at memory two have members | `SITable5` | `python3 sitable5.py` | `arrangement/`, `census/` | 1 s |
| **SI Table 6**: the two memory-two maps by piece of the plane | `SITable6` | `python3 sitable6.py` | `robustness/` (`f2_e4`, `f1_e4`), `games/` | 1 s |
| **SI Table 7**: robustness of the memory-two maps | `SITable7` | `python3 sitable7.py` | `robustness/` (all fifteen runs), `games/` | 1 s |
| **SI Table 8**: the sixteen binary memory-one strategies | `SITable8` | `python3 sitable8.py` (`--m2`: against all 65536 memory-two co-players) | none (exact, from the definitions) | < 1 s (26 s) |

Every figure script was run from a fresh copy of the repository on 2026-09-24,
with the versions in `requirements.txt`, and reproduced the published figure:

- **Figures 1–5 and SI Figures 2–12.** Rasterised next to the published PDF,
  each is pixel-identical at 80 and 150 dpi. Each PDF is byte-identical to the
  published one apart from the creation date that matplotlib writes into it.
  For Figures 2 and 3 the PDF is 12.1 and 6.9 MB, so a 150-dpi PNG preview is
  deposited instead, and the script writes the PDF. The scripts of the other
  figures also write a PNG preview, which is not deposited.
- **SI Figure 1.** Rebuilt with pdflatex, it is pixel-identical to the published
  PDF, and the two files differ only in their dates and their `/ID`.

Each table script prints its table next to the published one, compares them
entry by entry and exits with an error on any mismatch. Every entry agrees: SI
Table 1, 53 cases; SI Tables 2–5, every row; SI Table 6, 81 entries; SI Table 7,
180 entries; SI Table 8, 80 cells.

Some figures were drawn by one script in the author's project. Each folder here
stands alone:

- **Figure 4 and SI Figure 4** were drawn by one original script, `fig4.py`.
  Both now use the sheet in `common/wfsheet.py`.
- **Figure 5 and SI Figure 5** were drawn by one original script, `fig5.py`. The
  two folders hold its `draw()` twice.
- **SI Figures 2 and 3** each carry a copy of the original
  `atomshares.draw_runs`.
- **SI Figures 6 and 7** carry identical copies of `figstrict.py`.
- **SI Figures 9 and 10** were drawn by one original script, `sifig9.py`, which
  is split here into two.
- **SI Figure 12** is the original `sifiglm.py`.

## The census and the family descriptions (`census/`, `families/`)

`census/` holds the exact ε → 0 pair computation of SI §6 and its check
program. Two C programs classify all 65536 binary memory-two strategies:

- `pairs.c` runs Grassmann–Taksar–Heyman state reduction of the 16-state pair
  chain in leading-order arithmetic, with the coefficients in double precision
  and a tolerance of 10⁻⁹.
- `pairsq.c` runs the same algorithm with every coefficient an exact rational,
  and no tolerance anywhere.

Each program makes four passes: self-play (efficiency), rivalry for T > S and
for T < S, and stability with the tie clause at (u, v) = (−2, 2). `compare.py`
compares the two programs decision by decision, and `defensible.py` tests Murase
and Baek's defensibility by Floyd–Warshall. The exact run was Cannon job
48068392 (4096 passes, 164 s on 48 cores). Its output is reduced to
`data/census/`, and the two arithmetics agree on every decision.

```
cd census
make && make selftest        # builds pairs and pairsq, compares 1e5 random pairs exact against double (seconds)
python3 check.py             # every census count of SI §6 and the Methods, from data/census, and the 672 stable
                             # strategies at (-2, 2) from the stability regions of data/arrangement (2 s); ends in ALL AGREE
bash cannon/task.sh local 512 4    # the whole census, both programs (about 1 hour on 4 cores)
python3 compare.py out 512 && python3 reduce.py out    # compares the two runs, and rewrites data/census
```

`families/` describes each set of friendly rivals as a minimum cover by prime
wildcard patterns (Quine–McCluskey merging, then an exact set cover by integer
linear programming). `python3 families.py` (2 s) writes two files:

- `families.txt`, the full description of each set;
- `covers.csv`, the covers in machine-readable form.

The cover of the wedge S is not unique: 42 patterns, of which the paper says
"one of the minimal covers is included in the computed output". Which cover the
solver returns depends on the solver. With scipy 1.10.0 it is the deposited
one, byte for byte.

The stability regions of memory two, the set of games at which each strategy is
stable, come from the exact census of the companion paper
(Nowak, *An exhaustive map of binary memory-two direct reciprocity over
symmetric two-player games*, bioRxiv 2026.09.05.749606,
[doi:10.64898/2026.09.05.749606](https://doi.org/10.64898/2026.09.05.749606);
code at [github.com/martin-mn/MapBinM2](https://github.com/martin-mn/MapBinM2)).
They are deposited here in `data/arrangement/`, below.

## The simulator and the seeds (`simulator/`)

The evolutionary maps come from one Fortran 77 program, run as Slurm arrays with
one task per game. The maps are Figures 4 and 5, SI Figures 2–12 and SI Tables
6 and 7. `simulator/kits/` holds the program in every version that produced a
map: fourteen kits, byte-identical to what ran on Harvard's Cannon cluster
apart from their READMEs, one input path in each of two generator scripts, and
the wording of the generators `mkkits.py` and `lm/mklm.py`
(`simulator/kits/README.md`). The shared Fortran files (the pair-chain payoffs
and the Mersenne twister) are in `src/` and the game lists in `games/`. Other
files:

- `simulator/SEEDS.csv`: one row per run, 21 rows. They are the 19 runs of the
  paper, two of which are the bit-for-bit regenerations, and two memory-one
  convergence controls that the paper does not use. Each row gives the kit, N,
  β, μ, ε, mutation kernel ν, generations, replicates, task indices and seed
  base s₀.
- `simulator/seeds_by_game.csv`: the first seed of every game in every run.
- `simulator/CHECKSUMS.sha256`: the sha256 of every packed output file
  (`.idx`, `.bin`, `.win`, `.rep`) of the 17 memory-two runs, 64 files, against
  which a regenerated run is checked bit for bit (`simulator/README.md`, "The
  packs").

Replicate r = 1 … 10 of the game run as Slurm task `isl` uses the seed

    seed = s0 + 10 (isl − 1) + r

The two memory-two runs of Figure 4 and SI Figure 4 were regenerated from these
seeds (kits `f1`, `f2`), and every output file was byte-identical to the
original.

```
cd simulator/local && bash smoke.sh    # builds kit f1 with gfortran, runs one game for 20000 generations,
                                       # packs it and compares it with a reference run (about 10 s)
cd simulator && python3 mkseeds.py --check     # SEEDS.csv and seeds_by_game.csv against the kit files
```

A full run is 512 tasks of about an hour each: a cluster job.
`simulator/README.md` matches every statement of the Methods about the process
to the code. It also explains how to stage, compile, submit, verify and pack a
kit. The kits' scripts carry the author's cluster settings, which
`simulator/kits/README.md` lists.

The same runs appear under different names in different folders:

| run | kit | name in `data/runs/` | name in `data/robustness/` | name in `data/runs/wfdata.py` and `data/strict/` |
|---|---|---|---|---|
| memory one, N = 1000, β = 100, μ = 10⁻² | `mw` (`sf1.f`) | `m1_N1000` | — | `F1` |
| memory one, N = 100, β = 3, μ = 10⁻⁴ | `mw` (`sf2.f`) | `m1_N100` | — | `F2` |
| memory two, N = 1000, β = 100, μ = 10⁻² | `dw1`; regenerated as `f1` | `m2_N1000` | `f1_e4` | `F1` |
| memory two, N = 100, β = 3, μ = 10⁻⁴ | `dw2`; regenerated as `f2` | `m2_N100` | `f2_e4` | `F2` |

All four runs use ε = 10⁻⁴. The regenerations are byte-identical to the originals
and add per-replicate output. `data/runs/` reduced the originals through the
loader of the published figures. `data/robustness/` reduced the regenerations,
and its pooled shares differ from those of `data/runs/` by at most 1.6 × 10⁻¹³
(summation order). The fifteen robustness runs are listed in
`data/robustness/runs.csv`.

## The deposited data (`data/`)

Only reduced data are deposited: per-game, per-face, per-strategy and
per-replicate tables. Every table is a CSV file. It starts with `#` comment
lines that say what each column is, then a header line, then comma-separated
values. Floats are written with Python's `repr`, so they read back as the
identical double. `common.tables.read_table` reads every table. Polygons are in
`.npz` files. No file is larger than 6.2 MB, and `data/` holds 38.7 MB in all.

| folder | size | what it holds | read by |
|---|---:|---|---|
| `data/games/` | 0.2 MB | the 512 sampled games (u, v), exact multiples of 2⁻¹⁰, with their ids, regions and disk points, and their Voronoi cells on the disk | every map through `common.games` |
| `data/arrangement/` | 10.9 MB | the exact ε → 0 arrangements, in two parts listed below this table | Figures 1–3, SI Table 5 |
| `data/census/` | 12.5 MB | the census, one row per strategy, in exact and in double precision: self-play, rivalry, defensibility, stability and tie clause at (−2, 2), and the pass receipts. Also the six masks as `m2_masks.npz` | SI Tables 2–5, `families/` |
| `data/runs/` | 0.8 MB | the four main Wright–Fisher runs, one row per game: efficiency, the seven atom shares and sizes, the property shares, the winners, and the task index and first seed. The two memory-one runs are also deposited whole (the count of each of the 16 strategies per game) | Figures 4, 5, SI Figures 2–5 |
| `data/robustness/` | 9.8 MB | the fifteen memory-two runs of the robustness analyses, in two tables per run. The first has one row per game, with the pooled atom shares and the efficiency. The second has one row per replicate, with its seed, its most abundant strategy and, for all runs but `dw3_e4` and `dw4_e4`, its efficiency and atom shares. Also the atom sizes at each game | SI Figures 8–12, SI Tables 6, 7 |
| `data/strict/` | 4.3 MB | the strict Nash equilibria at ε = 10⁻⁴, at each game and for both memories: counts, sets and the share of the population on them. Also the 160 (game, strategy) pairs where the double-precision brute force and the exact test disagree | SI Figures 6, 7 |

The two parts of `data/arrangement/` are these:

- **Memory two.** The 254 lines; the 22872 faces of their arrangement, on each
  of which the set of stable strategies is constant, as sign vectors; the exact
  stability region of every strategy, a polygon; and the 27598 polygons as which Figures 1c, 2h–n
  and 3e–h draw the 22872 faces (the companion drawing cuts 771 of them into
  bands), with their atom counts and cases. The tables call the faces *cells*
  and the polygons *faces*, the names of the companion drawing.
- **Memory one.** 11 lines and 45 faces.

Checkers recompute the numbers the paper quotes from the deposited tables.
`data/census/` is checked by `census/check.py`, which also derives the stable
strategies at (−2, 2) from the stability regions of `data/arrangement/` and compares
them with the census. `data/robustness/` is checked by the table scripts of SI
Tables 6 and 7. The other folders carry their own checkers:

```
cd data/arrangement && python3 check.py        # the Methods counts 23861, 9431, 299-22069, 8-7639; SI §6 and §8 (8 s)
cd data/arrangement && python3 m1atoms.py m2   # rebuilds the memory-one arrangement exactly and compares (7 s)
cd data/runs        && python3 check_numbers.py   # 146 numbers of the text from the four main runs (< 1 s)
cd data/strict      && python3 check_strict.py    # the strict-equilibrium numbers of the Methods and SI (1 s)
cd data/strict      && python3 recompute_sets.py  # the strict sets recomputed from the games alone (17 s)
```

**Not deposited.** These files are not deposited:

- **The per-strategy abundance histograms of the memory-two runs** (`.bin`, 65536
  float32 per game; 134 MB for a run of 512 games; 2.4 GB for the 17 packed
  memory-two runs). Every number of the paper uses them only through the atom
  sums deposited in `data/runs/` and `data/robustness/`. They are regenerated
  bit for bit from the seeds with the kits in `simulator/`, and
  `simulator/CHECKSUMS.sha256` gives the sha256 of every packed file of the 17
  runs, against which a regeneration is checked. For the two runs of Figure 4
  and SI Figure 4 this was done, and every output file came out
  byte-identical.
- **The raw per-task outputs of the cluster runs** (the summary, w-, h- and
  r-files of every task). For the fifteen runs of `data/robustness/`, its
  replicate tables keep the most abundant strategy of every replicate, and,
  for all but `dw3_e4` and `dw4_e4`, the replicate's efficiency and atom
  shares.
- **The mean genome of each game** (`ps1..ps16`), which no figure or table
  uses.
- **The raw census outputs** (8192 files, 32 MB). Their content is in
  `data/census/`, and `census/` regenerates them.

The memory-one histograms are only 16 numbers per game, so they are deposited
whole. The table of ε → 0 atoms of every strategy at every game, `atoms512.bin`
(33.5 MB), is deposited compressed to 0.6 MB in `simulator/atoms/`, because the
kits' packers need it.

## The notes (`notes/`)

The SI refers in six places to "the notes deposited with the code", and the Code
availability statement promises "the notes on individual strategies and cycles
referred to in the Supplementary Information". `notes/` holds them, one file for
each of the six places: longer versions of passages condensed in the SI, with
the arguments written out and the numbers recomputed. Each file opens with the
sentence of the paper that points to it.

| place in the paper | file |
|---|---|
| SI §1, *Why the limit, and not a fixed error rate*: worked examples at ε = 0.01 | `notes/fixed-error-rate.md` |
| SI §1, *Discounting*: the full argument | `notes/discounting.md` |
| SI §7, the families of W, N and S read state by state | `notes/families.md` |
| SI §8, the atom `110`: the strategies and cycles of the bays | `notes/bays-and-cycles.md` |
| SI §9, *Longer punishment*: the full comparison of 22663 and 23175 | `notes/longer-punishment.md` |
| SI §10, the reading of main text Figure 2a–g atom by atom | `notes/memory-one-atoms.md` |

`notes/checks/` holds one script per note that recomputes its numbers and
statements, from first principles and from the deposited data (`data/arrangement/`,
`data/runs/`, `families/`). Each script prints PASS or FAIL per statement and
exits with an error if anything fails. Its output is the `.txt` file of the same
name, and every statement of the six notes passes:

```
cd notes/checks && for c in check_*.py; do python3 $c; done
```

## Provenance (`provenance/`)

Each subfolder records how one part of `data/` (or `simulator/`, `notes/`) was
made from the author's full outputs, and the cross-checks that were run on it:

| subfolder | made | cross-check |
|---|---|---|
| `census-figs/` | `data/arrangement/` | recomputes every per-face count combinatorially and asserts it equals the companion dump and the original per-face counts |
| `census-code/` | `data/census/`, `families/families.txt` | `compare.py` on the 8192 raw outputs; the masks bit-identical to the first computation of 2026-09-03 |
| `four-runs/` | `data/runs/` | an independent second reduction of the memory-two packs with its own parser |
| `robustness/` | `data/robustness/` | compares the tables with the loaders of the original figure scripts, for all fifteen runs |
| `strict/` | `data/strict/` | asserts the 160 (game, strategy) pairs on which the double-precision brute force and the exact test disagree against their quadruple-precision recomputation; holds the Fortran brute-force scan |
| `simulator-notes/` | `simulator/` (with `CHECKSUMS.sha256`, from the packs), `notes/` | the seed tables against the packs of all 21 runs; the regenerations `f1`, `f2` against the originals, game by game; the lineage of the memory-two simulator |
| `si-misc/` | nothing | where `SIFigure1`, `SITable1` and `SITable8` came from; a check against the author's sources |

These scripts run only in the author's environment. Each reaches the private
files through one variable at its top, marked "author's environment"
(`AUTHOR_ENV`, `AUTHOR_ROOT` or `AUTHOR_OPT`; for `simulator-notes/mknotes.py`,
the environment variable `PRFR_PASSAGES`). They are deposited as the record of
how the data were made, and nothing else in the repository needs them.

## Requirements

Python 3 with numpy, matplotlib, scipy and Pillow:

```
pip install -r requirements.txt
```

`requirements.txt` pins the versions with which the figures were verified:
Python 3.10.9, numpy 1.23.5, matplotlib 3.7.0 (with its bundled DejaVu Sans),
scipy 1.10.0 and Pillow 9.4.0. The tables and numbers do not depend on these
versions. A different matplotlib may shift antialiasing or text placement by a
pixel. scipy is needed for three things, and needs version 1.9 or later for
`milp`:

- `scipy.ndimage` (Figure 1);
- `scipy.optimize.milp` (`families/`, `SITable4/`);
- `scipy.spatial.Voronoi` (`common.games.compute_cells`).

Pillow is needed for Figure 1. `SITable1` and `SITable8` use only the standard
library, and `sitable8.py --m2` needs numpy.

Other tools, each needed by one part:

- **pdflatex** for SI Figure 1, with the packages `standalone`, `tikz`, `times`,
  `amsmath` and `amssymb`. The published figure was made with TeX Live 2024.
- **A C compiler** with `unsigned __int128` (gcc or clang) for `census/`.
- **A Fortran 77 compiler** for `simulator/`. The runs used Intel `ifx`
  (`-O3 -xHost -fp-model precise`), and the smoke test uses gfortran 14.
- **bash**, and **Slurm** for the cluster kits. The packers use only the Python
  standard library.

## Reproducing everything

```
bash reproduce_all.sh                    # figures, tables and checks: about 4 minutes
bash reproduce_all.sh figures            # or: tables, checks, or folder names such as Figure4 SITable6
bash reproduce_all.sh list               # the steps, without running them
```

`reproduce_all.sh` runs every figure and table script in turn, one at a time,
under `nice -n 10` and with `python3 -B`. Then it runs the checkers:

- `data/arrangement/check.py` and `m1atoms.py`, `data/runs/check_numbers.py`,
  `data/strict/check_strict.py` and `recompute_sets.py`;
- `census/check.py`, and the census self-test (`make selftest`) when a C
  compiler is installed;
- the six scripts of `notes/checks/`, each output compared with its `.txt`;
- `python3 -m common`, the self-test of the games and cells;
- `simulator/mkseeds.py --check`; the generators of the kits
  (`simulator/kits/mkkits.py`, `lm/mklm.py`, `mw/mksf.py`), rerun on a
  temporary copy and compared file by file with the deposited kits; and the
  simulator smoke test when gfortran is installed.

After each step it prints the files the step wrote. For each deposited output
the step rewrote, it says whether the new file is identical to the deposited
one. It stops at the first step that fails: a non-zero exit status, a printed
FAIL, or a reported difference. The full output of every step goes to
`reproduce_log/`. Its exit status is 0 when every step passed and every
rewritten file is identical to the deposited one.

The steps rewrite the deposited figures and tables in place. With the pinned
versions they come out identical, the PDFs apart from their creation date.
`git checkout -- .` restores the deposited files.

The script does not rerun the expensive computations:

- the full census (about an hour on four cores; the cluster kit is
  `census/cannon/`);
- the Wright–Fisher runs (hundreds of core-hours each; `simulator/kits/`);
- the reductions in `provenance/`.

## Conventions

Every game is brought by a positive affine change of scale to

```
R = 1        S = u        T = 1 + v        P = 0
```

so mutual cooperation earns 1, mutual defection 0, and the plane of `(u, v)` is
the whole space of symmetric two-player games in which mutual cooperation beats
mutual defection. The quadrants are the Prisoner's Dilemma `u < 0 < v`,
Snowdrift `u, v > 0`, Stag Hunt `u, v < 0` and Harmony `v < 0 < u`. The switch
line `u + v = 1`, where the best joint outcome changes from mutual cooperation
to alternation, and the line `T = S` (`u − v = 1`) cut the plane into the four
wedges W, S, N and E of SI Table 2. Every map draws the plane compactified onto
the unit disk by `(u, v) -> (u, v) / sqrt(16 + u² + v²)`.

A memory-two strategy is a genome of sixteen answers, position
`j = 4·(most recent outcome) + (the outcome before)` with `CC = 0, CD = 1,
DC = 2, DD = 3` seen from the player's own side. Its integer code is `Σ c_j 2^j`
with `c_j = 1` for cooperation, so ALLC is 65535, ALLD 0 and tit-for-tat 3855.
A memory-one strategy is written by its answers after CC, CD, DC and DD, for
example `CDDC` for win-stay, lose-shift. The atoms are written
efficient–stable–competitive. The integer code of an atom is
`4·efficient + 2·stable + competitive`, and figures and tables list the atoms in
the order `000, 100, 010, 001, 110, 011, 111`. Per-game arrays are in the order
`ipt = 0 … 511` of `data/games/games.csv`. Files and columns named for the
second property keep the name `nash` (for example `nash` in
`data/census/census.csv`, `P_nash` in `data/runs/`, `m2_nash_facets.csv` and
`nash_dim` in `data/arrangement/`): they hold stability, a symmetric Nash
equilibrium against a single deviant. `common/README.md` has the rest.

## License

Code and data are released under the MIT License (`LICENSE`).

The one exception is the Mersenne-twister code. `simulator/src/mt.f`, and the
bulk generator in `simulator/src/mtb.f` derived from it, are Tsuyoshi Tada's
FORTRAN 77 translation of `mt19937ar` by Makoto Matsumoto and Takuji Nishimura,
Copyright (C) 1997–2002 Makoto Matsumoto and Takuji Nishimura. They are
distributed under its own BSD-style licence, which is reproduced in
`simulator/src/LICENSE-MT19937.txt`.
The polygons of the memory-two stability regions and the drawing of the arrangement in
`data/arrangement/` are re-encoded from the companion repository
[MapBinM2](https://github.com/martin-mn/MapBinM2), which is released by the
same author under the MIT License.

## How to cite

Please cite the paper, and this repository if you use its code or data:

> Nowak, M. A. Partners, rivals, and friendly rivals in the evolution of direct
> reciprocity (2026).

> Nowak, M. A. Code and data for: Partners, rivals, and friendly rivals in the
> evolution of direct reciprocity. Version 1.0.0 (2026).
> https://github.com/martin-mn/PRFR

**To be added on publication:** the journal and DOI of the paper, and the DOI
of the archived release of this repository.

```bibtex
@misc{Nowak2026PRFRcode,
  author    = {Nowak, Martin A.},
  title     = {Code and data for: Partners, rivals, and friendly rivals in the evolution of direct reciprocity},
  year      = {2026},
  version   = {1.0.0},
  url       = {https://github.com/martin-mn/PRFR}
}
```

`CITATION.cff` and `.zenodo.json` carry the same metadata.
