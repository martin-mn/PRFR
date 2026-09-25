# simulator — the Wright–Fisher simulator of the paper, and the seeds of every run

The evolutionary maps of the paper (main text Figures 4 and 5, SI Figures 2–12, SI Tables 6 and 7) come from one
Fortran 77 program, run on a cluster as Slurm arrays with one task per game. This folder holds that program in every
version that produced a map (the *kits*, byte-identical to what ran), the parameters and random seeds of every run, a
local smoke test, and the atom table the packing step needs. The process is the one of the Methods, "The
Wright–Fisher process with pairwise comparison"; below, each of its statements is matched to the code.

The reduced output of the runs is not here: the per-game and per-replicate tables of the four main runs are in
`../data/runs/`, those of the fifteen memory-two robustness runs in `../data/robustness/`. The full per-strategy
abundance histograms (`.bin`, 128 MB per run) are not deposited; every run can be regenerated from the kits and the
seeds, and two of them were: the runs of main text Figure 4d–f and SI Figure 4d–f were re-run from their seeds (kits
`f1`, `f2`) and every output file came out byte-identical. `CHECKSUMS.sha256` gives the sha256 of every packed file
(`.idx`, `.bin`, `.win`, `.rep`) of the 17 memory-two runs the paper uses, so that a regenerated run can be checked
against the original bit for bit (below, "The packs").

## Layout

| path | what |
|---|---|
| `SEEDS.csv` | one row per run: kit, source, N, β, μ, ε, ν, generations, replicates, task indices, seed base, the smallest and largest seed, the display items it feeds |
| `CHECKSUMS.sha256` | the sha256 of every packed file of the 17 memory-two runs, one line `<sha256>  <run>/<file>` per file (written by `provenance/simulator-notes/mkchecksums.py`) |
| `seeds_by_game.csv` | the seed of the first replicate of every game in every run (512 rows) |
| `mkseeds.py` | writes both tables from the kit files (`python3 mkseeds.py --check` verifies them) |
| `kits/` | the fourteen kits, the generators `kits/mkkits.py`, `kits/lm/mklm.py`, `kits/mw/mksf.py`, and `kits/stage.sh` |
| `src/` | the four Fortran files every kit links: the pair-chain payoffs (`payf2.f`, `payf3.f`) and the Mersenne twister (`mt.f`, `mtb.f`), with the twister's licence |
| `games/` | the two game lists the kits read (`games.dat`, 967 rows, the 512 games of the paper are rows 456–967; `games_m1.dat`, the same 512 for the memory-one kit) |
| `atoms/` | `atoms512.bin.gz`, the ε → 0 atom of each of the 65536 strategies at each game, read by `pack.py` for the per-replicate atom shares |
| `local/` | `smoke.sh`, a one-game local run with checks, and reference outputs |

## The runs

| run | kit | strategies | N | β | μ | ε | generations | display items |
|---|---|---|---:|---:|---:|---:|---:|---|
| `m1_N1000` | mw (`sf1.f`) | 16 memory-one | 1000 | 100 | 10⁻² | 10⁻⁴ | 10⁷ | main Fig. 4a–c, 5a–c; SI Fig. 2i–p, 6c, 7c |
| `m1_N100` | mw (`sf2.f`) | 16 memory-one | 100 | 3 | 10⁻⁴ | 10⁻⁴ | 10⁸ | SI Fig. 2a–h, 4a–c, 5a–c, 6b, 7b |
| `m2_N1000` | dw1 | 65536 memory-two | 1000 | 100 | 10⁻² | 10⁻⁴ | 10⁷ | main Fig. 4d–f, 5d–f; SI Fig. 3i–p, 6f, 7f, 8h/p/x, 9d–f, 12j–l |
| `m2_N100` | dw2 | 65536 memory-two | 100 | 3 | 10⁻⁴ | 10⁻⁴ | 10⁸ | SI Fig. 3a–h, 4d–f, 5d–f, 6e, 7e, 8a/i/q, 10d–f |
| `f1`, `f2` | f1, f2 | memory-two | as m2_N1000, m2_N100 | | | | | SI Fig. 11 (per-replicate shares; same seeds, identical outputs) |
| `dw3`, `dw4`, `c1`–`c4` | same names | memory-two | the six other corners of {100, 1000} × {3, 100} × {10⁻⁴, 10⁻²} | | | 10⁻⁴ | 10⁷, c3: 10⁸ | SI Fig. 8, SI Table 7a |
| `eh_e3`, `eh_e5` | eh | memory-two | 1000 | 100 | 10⁻² | 10⁻³, 10⁻⁵ | 10⁷ | SI Fig. 9a–c, g–i; SI Table 7b |
| `el_e3`, `el_e5` | el | memory-two | 100 | 3 | 10⁻⁴ | 10⁻³, 10⁻⁵ | 10⁸ | SI Fig. 10a–c, g–i; SI Table 7b |
| `lm_g0`, `lm_g01`, `lm_g05` | lm | memory-two, ν = 0, 0.1, 0.5 | 1000 | 100 | 10⁻² | 10⁻⁴ | 10⁷ | SI Fig. 12a–i; SI Table 7c |

Every run: the 512 games of `../data/games/`, 10 independent replicates per game, the second half of each replicate
sampled, every individual in every generation. `SEEDS.csv` has the exact values, read from the kit files, and also
lists the two memory-one convergence controls (`*_ctrl`), which are not used in the paper.

**Run lengths.** 10⁸ generations at N = 100 with μ = 10⁻⁴ (`m2_N100`, `c3`, `el` and the memory-one `m1_N100`) and
10⁷ otherwise, so that N × generations is 10¹⁰ in every run except `c1` and `c2` (10⁹): the packs record
5 × 10¹⁰ sampled individual-generations per game, 10 × (generations/2) × N, and 5 × 10⁹ for `c1` and `c2`.

## The process, statement by statement

`kits/f1/sf.f` is the reference version; the others differ in parameter lines (and lm in the mutation step, mw in the
strategy space). One task is one game: `./sf_1e7.x <isl>` reads `games.dat` from the working directory, decodes the
game row ig = (isl − 1)/3 + 1 and the error-rate slot ie = mod(isl − 1, 3) + 1, and runs all 10 replicates.

- **Population and initial state.** N individuals, each a strategy code 0..65535; replicate r starts from N codes drawn
  independently and uniformly (16 fair coins each), after `call init_genrand(iseed)` with
  `iseed = iseedb + (isl-1)*nper + irep` (nper = 10).
- **Interaction.** Every generation each individual picks one co-player uniformly among the others (`m = 1`,
  `if (j.eq.i) goto 43`), and both add their per-round payoff of the ε-perturbed pair chain to their fitness `f`, so
  that an individual plays two games on average.
- **Payoffs.** The payoff of a pair is computed from the stationary distribution of the 16-state chain at the run's ε
  (`payf3`, see `src/`) when the pair first meets, and kept in a hash cache of 2²⁰ slots keyed by the pair
  (`ckey`, `cvl`, `cvh`), emptied once per task, i.e. per game. A cache hit returns the same doubles that the computation
  would, so the cache saves time and changes no value. (Memory one: a 16 × 16 table filled once per game.)
- **Update, synchronous.** For each individual, one uniform number decides mutation (probability μ, `uval`): the new
  strategy is `int(rb*65536)`, uniform over the whole space, its own included. Otherwise a role model j is drawn
  uniformly from the whole population, itself included, and its strategy is adopted with probability
  1/(1 + exp(−β(f_j − f_i)/2)) (`be = beta*rrm`, rrm = 1/(2m)). All individuals update from the old population
  (`sn`), then `s = sn`. The logistic is evaluated as 0 or 1 when |β(f_j − f_i)/2| ≥ 25; since `genrand_real3` returns
  numbers in [2⁻³³, 1 − 2⁻³³] and 1/(1 + e²⁵) ≈ 1.4 × 10⁻¹¹ < 2⁻³³, this cutoff changes no decision.
- **Sampling.** In the second half of the run (`it > itend/2`) the strategy of every individual is counted in every
  generation (`hist`), and the population's summed fitness is accumulated for the mean payoff.
- **Mixed kernel (kit lm).** A mutating individual draws one more uniform number: with probability ν (`pglob`) it takes a
  uniform strategy as above, otherwise it flips one of its own 16 positions, chosen uniformly.

## Running one game locally

```bash
cd local && bash smoke.sh           # about 10 s: kit f1, one game, 20000 generations, with checks and the pack
```

See `local/README.md`. A full run is 512 tasks of about an hour each (10 replicates of N × generations = 10¹⁰
individual-updates), 450–615 core-hours per run on the author's cluster (60 for c1 and c2): a cluster job, not a local
one.

## Running a campaign on a cluster

```bash
cd kits
bash stage.sh c1                    # the shared sources, games.dat and atoms512.bin into place
cd c1
bash compile.sh 1e7                 # ifx -O3 -xHost -fp-model precise; for gfortran edit the compile line
bash submit.sh probe_e4             # 8 cells; read the rate with
bash verify.sh probe_e4             #   (per task from sacct, per cell from the files)
bash submit.sh prod_e4              # the 512 games; probe cells already complete are skipped
bash verify.sh prod_e4
python3 pack.py run_1e7 packed      # -> packed/c1_e4.{idx,bin,win,rep}
```

Each kit's README has its own commands and the record of its arrays. The scripts carry the author's cluster settings
(partition, compiler module, a job ledger); `kits/README.md` lists them, and gives the one-line change that makes the
ledger line of every `submit.sh` conditional on the environment variable `PRFR_LEDGER`.

## What a task writes

For task `isl`, in the run directory (memory-two kits; the memory-one kit writes the same with 4 in place of 16):

| file | unit | contents |
|---|---|---|
| `<isl>` | 3 | the summary: one line per replicate, `gid ie u v Emax pay ef ps1..ps16`. `pay` is the mean per-round payoff of an individual over the sampled half, `ef = pay/Emax` with E_max = max(R, (S+T)/2), and `ps(k)` the mean probability, errors included, that a sampled individual cooperates in state k − 1 |
| `w<isl>` | 4 | per replicate a line `# isl ie eps gid u v irun pay ef ndist ntot nhit nmis` (ndist distinct strategies, ntot samples, cache hits and misses), then the 10 most abundant strategies: `isl eps gid irun rank code abund selfpay selfef cc cd dc dd bits` (self-play payoff, its efficiency, the self-play outcome frequencies and the 16-letter genome, position j = the answer in state j) |
| `h<isl>` | 7 | the header (`# cell:` isl, gid, tag, eps, umut = μ, beta; `# game:` cR cS cT, u v, Emax; `# run:` nper, itend, ie), then after the last replicate `# distinct <ndist> total <ntot>` and one line `code count` for every strategy with a non-zero count, summed over the 10 replicates. count/total is the strategy's abundance π |
| `r<isl>` | 8 | (kits of 2026-09-22 on: c1–c4, eh, el, f1, f2, lm) after every replicate its 65536 counts as little-endian int64, unformatted stream: 10 × 524288 bytes |

## The packs

`pack.py` of a kit turns a run directory into one file set per error rate, named `<kit>_<e>` (`e4` for ε = 10⁻⁴):
`.idx`, one line per game in gid order (`gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total ps1..ps16`, `efsd`
the s.d. of `ef` over the replicates); `.bin`, 65536 little-endian float32 per game, the abundance π normalised to sum
1 (512 × 256 kB = 128 MB); `.win`, one line per (game, replicate) with the most abundant strategy
(`gid irun rank1 abund selfpay`); and, from the r-file, `.rep`, one line per (game, replicate) with that replicate's
efficiency and its seven atom shares `s000 s100 s010 s001 s110 s011 s111`, computed with `kits/atoms512.bin`, which
`kits/stage.sh` unpacks from `atoms/atoms512.bin.gz` (the share of atom 101 is asserted to be zero). The packers
refuse a truncated histogram or a short r-file rather than renormalise it. The memory-one packer writes
`mw<W>_e4.tsv` (per game the 16 counts) and `mw<W>_e4.rep.tsv`. The deposited tables in `../data/runs/` and
`../data/robustness/` are reductions of these packs.

`CHECKSUMS.sha256` lists the sha256 of the packs of the 17 memory-two runs, in the format of `sha256sum` with the run
of `SEEDS.csv` as the directory of each file (`m2_N1000/dw1_e4.bin`, `f1/f1_e4.rep`, …). To check a regenerated run,
put its pack in a directory named after the run and, from the directory that holds it,

```bash
grep -v '^#' CHECKSUMS.sha256 | grep ' c1/' | sha256sum -c          # or: shasum -a 256 -c
```

The pack of `m2_N1000` (kit dw1) holds 967 games, the 512 of the paper and the 455 of rows 1–455 of `games.dat`,
which the kit also ran and the paper does not use; the regeneration `f1` packs the 512. Game by game, the `.idx`
line, the `.bin` block and the ten `.win` lines of every one of the 512 games are identical in `f1` and in the
original, and the `.idx`, `.bin` and `.win` of `f2` are identical as files to those of `m2_N100` (kit dw2), as
`CHECKSUMS.sha256` shows.

## Seeds

Each replicate runs on its own Mersenne-twister seed,

    seed = s0 + 10 (isl − 1) + r,        r = 1..10,

where isl is the Slurm task index of the game (not the game number) and s0 the run's seed base (`iseedb`). For the
memory-two kits isl = 1365 + 3·ipt + ie, i.e. 1368 + 3·ipt at ε = 10⁻⁴, 1367 + 3·ipt and 1366 + 3·ipt for the
ε = 10⁻³ and 10⁻⁵ strides of eh and el; for the memory-one kit isl = 3 + 3·ipt. `SEEDS.csv` gives s0 for every run and
`seeds_by_game.csv` the first seed of every game.

The seed bases are 8, 9, 10, 11, 20–25 and 30–32 million (and 12, 13 million for the memory-one controls). Two pairs of
runs share seeds on purpose: `f1` and `f2` are `m2_N1000` and `m2_N100` regenerated with their own seeds. Two pairs
share some seed values by accident: the memory-one runs used the bases 10 and 11 million, the same as `dw3` and `dw4`,
and since the task ranges overlap (isl 1368–1536), 57 games × 10 replicates of each memory-one run start from a seed
that a memory-two cube corner also used, for a different game (memory-one ipt 455–511, memory-two ipt 0–56). The runs
simulate different strategy spaces and are never compared game by game, so this has no statistical consequence; but
the remark in the kits' comments that these bases are disjoint from every earlier campaign is not literally true.
Within every other pair of runs the seeds are distinct (`python3 mkseeds.py` prints the overlaps).

## Checks made for the repository (2026-09-24)

- Every file of every kit, staged, is byte-identical to the file in the author's kit directory (188 files; the
  shared Fortran files and `games.dat` were identical in all kits before they were stored once). The generators
  `lm/mklm.py` and `mw/mksf.py` differ from the author's in one input path each, `lm/mklm.py` also in the wording of
  its docstring, and `mkkits.py` in the wording of its docstring, two comments and the README text it writes
  (`kits/README.md`).
- `mkkits.py`, `lm/mklm.py` and `mw/mksf.py`, run on a copy of `kits/`, regenerate the files they write byte for byte
  (for `mkkits.py`, every file of its eight kits other than README.md);
  `mkkits.py test` (gfortran, 10⁵ generations) finds the per-replicate file addition output-neutral: IDENTICAL.
- `SEEDS.csv` agrees with every pack: for all 21 runs, the task index of each of the 512 games, the number of replicates
  and the total sample count N × (generations/2) × 10 recorded in the packs are the ones SEEDS.csv implies
  (`provenance/simulator-notes/check_seeds_vs_packs.py`, log next to it). The seeds also agree with the `seed1` and
  `seed` columns of the tables in `../data/runs/` and `../data/robustness/`.
- `atoms/atoms512.bin.gz` unpacks to the file the packs were made with (sha256 `dccd19ca…`), and regenerating it from
  the exact ε → 0 layer reproduces it bit for bit.
- `CHECKSUMS.sha256` was written from the packs the paper used (64 files, 2.4 GB), and the 512 games of the
  regenerations `f1` and `f2` were compared with the originals game by game: identical
  (`provenance/simulator-notes/mkchecksums.py`, log next to it).
- `local/smoke.sh` runs for f1, f2, dw1, lm, mw1 and mw2 with complete outputs; dw1 and f1 give identical summary, w- and
  h-files, as they must.

## Requirements

A Fortran 77 compiler (the runs: Intel `ifx` from the module `intel/25.2.1-fasrc01`, with `-O3 -xHost -fp-model precise`; the smoke test: gfortran
14.1 with `-O2`), bash, and Python 3 with the standard library only (the packers were written for the cluster's
python, which has no numpy). Slurm for the cluster scripts.
