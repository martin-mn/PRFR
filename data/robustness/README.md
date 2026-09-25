# data/robustness — the memory-two runs of the robustness analyses, reduced

The reduced output of the fifteen memory-two Wright–Fisher runs behind SI Figures 8–12, SI Tables 6 and 7 and the
paragraphs of the SI section "The evolutionary maps" that read them. Among them are the two runs of main text
Figure 4d–f and SI Figure 4d–f, in their regenerations `f1_e4` and `f2_e4`, which carry per-replicate output. For
each run there is one table with one row per game and one with one row per (game, replicate). The folders
`SIFigure8` … `SIFigure12`, `SITable6` and `SITable7` read only these tables, `data/games/` and `common/`.

| file | rows | what |
|---|---|---|
| `runs.csv` | 15 | one row per run: kit, N, β, μ, ε, ν, generations, seed base, slurm offset, Cannon job ID, where the run is used |
| `m2_atom_sizes.csv` | 512 | `N_000 … N_111`: the number of the 65536 strategies in each atom at each game, in the limit ε → 0 (the same for every run) |
| `games_<run>.csv` | 512 each | per game: `isl` (fixes the seeds), `E` realised efficiency, `efsd`, `pay`, `ndist`, `nrep`, and `S_000 … S_111`, the pooled atom shares |
| `replicates_<run>.csv` | 5120 each | per game and replicate: `seed`, `E` and `R_000 … R_111` (that replicate's efficiency and atom shares; not for `dw3_e4`, `dw4_e4`), `top`, `top_atom`, `top_share`, `top_selfpay` (the replicate's most abundant strategy, its atom, its share, its payoff against itself) |
| `wfruns.py` | | the reader: `wfruns.load(run)` returns the arrays the figure scripts use (`S`, `N`, `E`, `R`, `ER`, `LEAD`, …; see its docstring) |

Every table starts with `#` comment lines that describe each of its columns. They are followed by a header line and
comma-separated rows (`common.tables`). All per-game rows are in ipt order 0..511, the games of `data/games/games.csv`.
Floats are written with Python's `repr`, so each one reads back as the same double that was computed.

## The runs

All fifteen runs use the 65536 binary memory-two strategies on the 512 sampled games, with the Wright–Fisher process
with pairwise comparison of the Methods. Each has 10 independent replicates per game, and the second half of each
replicate is sampled. Mutants are drawn uniformly from all 65536 strategies (ν = 1) unless stated.

| run | N | β | μ | ε | ν | generations | seed base | Cannon job | in the paper |
|---|---:|---:|---|---|---:|---|---:|---:|---|
| `f2_e4` | 100 | 3 | 1e-4 | 1e-4 | 1 | 1e8 | 9000000 | 47837725 | SI Fig. 4d–f (the regeneration of dw2), SI Fig. 8 a/i/q, 10 d–f, 11 a–c, SI Tables 6, 7a |
| `c2_e4` | 100 | 3 | 1e-2 | 1e-4 | 1 | 1e7 | 23000000 | 47721339 | SI Fig. 8 b/j/r, SI Table 7a |
| `c4_e4` | 1000 | 3 | 1e-4 | 1e-4 | 1 | 1e7 | 25000000 | 47734216 | SI Fig. 8 c/k/s, SI Table 7a |
| `dw4_e4` | 1000 | 3 | 1e-2 | 1e-4 | 1 | 1e7 | 11000000 | 46108584 | SI Fig. 8 d/l/t, SI Table 7a |
| `c3_e4` | 100 | 100 | 1e-4 | 1e-4 | 1 | 1e8 | 24000000 | 47735495 | SI Fig. 8 e/m/u, SI Table 7a |
| `c1_e4` | 100 | 100 | 1e-2 | 1e-4 | 1 | 1e7 | 22000000 | 47721337 | SI Fig. 8 f/n/v, SI Table 7a |
| `dw3_e4` | 1000 | 100 | 1e-4 | 1e-4 | 1 | 1e7 | 10000000 | 46108583 | SI Fig. 8 g/o/w, SI Table 7a |
| `f1_e4` | 1000 | 100 | 1e-2 | 1e-4 | 1 | 1e7 | 8000000 | 47837723 | main text Fig. 4d–f (the regeneration of dw1), SI Fig. 8 h/p/x, 9 d–f, 11 d–f, 12 j–l, SI Tables 6, 7 |
| `eh_e3` | 1000 | 100 | 1e-2 | 1e-3 | 1 | 1e7 | 20000000 | 47736148 | SI Fig. 9 a–c, SI Table 7b |
| `eh_e5` | 1000 | 100 | 1e-2 | 1e-5 | 1 | 1e7 | 20000000 | 47734175 | SI Fig. 9 g–i, SI Table 7b |
| `el_e3` | 100 | 3 | 1e-4 | 1e-3 | 1 | 1e8 | 21000000 | 47735463 | SI Fig. 10 a–c, SI Table 7b |
| `el_e5` | 100 | 3 | 1e-4 | 1e-5 | 1 | 1e8 | 21000000 | 47734189 | SI Fig. 10 g–i, SI Table 7b |
| `lm_g0_e4` | 1000 | 100 | 1e-2 | 1e-4 | 0 | 1e7 | 30000000 | 48181135 | SI Fig. 12 a–c, SI Table 7c |
| `lm_g01_e4` | 1000 | 100 | 1e-2 | 1e-4 | 0.1 | 1e7 | 31000000 | 48181161 | SI Fig. 12 d–f, SI Table 7c |
| `lm_g05_e4` | 1000 | 100 | 1e-2 | 1e-4 | 0.5 | 1e7 | 32000000 | 48181182 | SI Fig. 12 g–i, SI Table 7c |

**Seeds.** Replicate `rep` (1..10) of the game run as slurm task `isl` used the seed `seed_base + (isl − 1)·10 + rep`.
Here `isl = 3(ig − 1) + ie`, with `ig = 456 + ipt` and `ie` given in `runs.csv`. The `seed` column of every
`replicates_<run>.csv` holds this value. `eh` and `el` share a seed base between their two error rates, but their
arrays use different offsets `ie`. All 76,800 replicates in this folder have distinct seeds.

**Figure 4's own runs.** `f1_e4` and `f2_e4` are the runs `dw1` (job 44394541) and `dw2` (job 45049704) of main text
Figure 4d–f and SI Figure 4d–f, rerun on 2026-09-22 with their original seeds and one addition: a stream of
per-replicate counts. Their `.idx`, `.win` and `.bin` are byte-identical to `dw1`'s (its 512 sampled games) and to
`dw2`'s. They add the `.rep`, the per-replicate atom shares that SI Figure 11 c, f and the replicate counts of the SI
are made from. The same two runs are deposited in `data/runs/` (`m2_N1000.csv`, `m2_N100.csv`, reduced there
through the loader of the published figures). The pooled shares of the two folders differ by at most 1.6e-13, because
the atom sums are taken in a different order. The efficiencies, atom sizes, `isl` and seeds are identical, and so
are the most abundant and most enriched atoms at every game.

**Names of these two runs.** Each has one name per folder:

| run | simulator kit | `data/runs/` | here | `data/runs/wfdata.py`, `data/strict/` |
|---|---|---|---|---|
| memory two, N = 1000, β = 100, μ = 10⁻² | `dw1`, regenerated as `f1` | `m2_N1000` | `f1_e4` | `F1` |
| memory two, N = 100, β = 3, μ = 10⁻⁴ | `dw2`, regenerated as `f2` | `m2_N100` | `f2_e4` | `F2` |

The table "The same runs appear under different names" in the section on the simulator of the top-level `README.md`
also covers the two memory-one runs.

**Runs without per-replicate output.** `dw3_e4` and `dw4_e4` (2026-09-11) predate the per-replicate stream. Their
`replicates_*.csv` therefore hold only the columns taken from the `.win`: the most abundant strategy of each
replicate, its atom and its share.

## Columns, briefly

- `S_abc`: the share of the population in atom `abc` (efficient-stable-competitive, the ε → 0 classification of the
  paper), pooled over the ten replicates and the sampled second halves. It is the per-strategy abundance vector,
  normalised and summed over the atom's strategies. The atom 101 is empty at every game and has no column.
- `E`: the realised efficiency, the population's mean per-round payoff divided by `Emax = max(1, (1 + u + v)/2)`
  (the `ef` of the packs). `efsd`: the standard deviation of that ratio over the ten replicates (ddof = 1), as the
  simulator wrote it.
- `R_abc`, `E` in the replicate tables: the same quantities for a single replicate, to the 8 decimals of the
  simulator's `.rep`. The ten replicates of a game average to the pooled `S_abc` within 8e-9, and to the pooled `E`
  within 4e-9.
- `top`: the replicate's single most abundant strategy, by its integer code 0..65535 of the Methods (the genome read
  as a binary number, ALLD = 0, ALLC = 65535). `top_atom`: that strategy's atom at the game, as the code
  4·efficient + 2·stable + competitive. For example, 7 is 111 (a friendly rival) and 4 is 100.

## What is not deposited, and why

The reduction discards three things:

- **The per-strategy abundance vectors** (`<run>.bin`). Each is 512 × 65536 float32 = 128 MB, and the fifteen come
  to 1.9 GB. Every number in the paper uses them only through the atom sums above; the most abundant single strategy
  of each replicate is kept.
- **The mean genome of each game** (the `ps1..ps16` columns of the `.idx`: the population's mean probability of
  cooperating at each of the sixteen positions). No figure or table uses them.
- **The raw per-cell outputs on the cluster.** The simulator's kits reproduce all of these bit for bit from the seeds
  above. `f1` and `f2` did exactly that for Figure 4's two runs: they reproduced every one of 1,536 output files of
  each.

The table of the atom of every strategy at every game that the reduction used, `atoms512.bin` (512 × 65536 bytes,
33.5 MB), is deposited compressed to 0.6 MB as `simulator/atoms/atoms512.bin.gz`, because the kits' packers read it.
Its atom sizes are `m2_atom_sizes.csv`. `provenance/robustness/crosscheck.py` confirmed that it equals the exact
masks of the census for all 512 × 65536 (game, strategy) pairs.

## Provenance and checks

Everything in this folder except `wfruns.py` and this README was written by `provenance/robustness/reduce.py` from the
packed files on the author's machine. `provenance/robustness/crosscheck.py` compared the tables with what the loaders
of the original figure scripts return (`wfdata.load`, `sifig8.load_idx` and `wfrep.load`). For all fifteen runs the
games, atom sizes, efficiencies, replicate shares, replicate efficiencies and replicate leaders are identical. The
pooled shares are bit-identical to `wfrep.load`, and differ from `wfdata.load` and `load_idx` by at most 2.7e-13.
The most abundant and most enriched atom are identical at every game of every run. With these tables, SI Figures
8–12 redraw pixel for pixel, and SI Tables 6 and 7 reproduce in every entry (see the figure and table folders).

Size: 9.8 MB in 34 files; the largest is 0.62 MB.
