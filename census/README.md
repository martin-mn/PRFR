# census — the exact ε→0 classification of the 65536 binary memory-two strategies

This folder holds the census of SI §6 ("The binary memory-two strategies"). It classifies every binary memory-two
strategy in the limit of rare errors, ε→0: its self-play, which decides whether it is efficient; whether it is a rival
for T>S and for T<S; and whether it is stable, and satisfies the tie clause, at the donation game (u,v) = (−2,2). The
folder has two C programs that compute the same census, one in double precision and one in exact rational arithmetic,
the program that compares them (`compare.py`), a Floyd–Warshall test of defensibility, and the Cannon kit of the exact
run. Its reduced output, one row per strategy, is in `../data/census/`. `check.py` recomputes every count of the
census from that output.

Games are (R, S, T, P) = (1, u, 1+v, 0). A strategy's code has bit j = 1 when it cooperates at state
j = 4·(most recent outcome) + (the outcome before), with the outcomes CC=0, CD=1, DC=2, DD=3 written own action first.
So ALLC = 65535, ALLD = 0, TFT = 3855 and WSLS = 61455. The genome of the paper is `format(code, '016b')[::-1]`.

## Files

| file | what |
|---|---|
| `pairs.c` | the census program. It runs GTH state reduction of the 16-state pair chain in leading-order arithmetic: every quantity is held as c·ε^m, with an exact integer exponent m and a coefficient c in double precision. Decisions are compared with a tolerance of 1e-9 |
| `pairsq.c` | the same algorithm with every coefficient an exact positive rational: a 64-bit numerator and denominator, reduced after every operation, with products formed in 128 bits. The program stops on overflow, which never happened. It has no tolerance anywhere |
| `compare.py` | compares the raw outputs of the two programs decision by decision, then recomputes the paper's counts from the exact outputs: `python3 compare.py <outdir> 512` |
| `Makefile` | `make` builds `pairs` and `pairsq`. `make selftest` compares 10⁵ random pairs exact against double and prints one pair |
| `defensible.py` | Murase and Baek's defensibility of all 65536 strategies, by Floyd–Warshall on the 16-node graph of each strategy, for T>S and for T<S (about 1 s) |
| `reduce.py` | turns the raw outputs of the four passes into the tables of `../data/census/`: `python3 reduce.py <outdir>` |
| `check.py` | recomputes the census counts of SI §6 and the Methods from `../data/census/` and compares them with the paper. It also compares the stable strategies at (−2,2) with the exact arrangement of the companion work in `../data/arrangement/`, strategy by strategy (exit status 1 on a mismatch) |
| `censuslib.py` | the loader of `../data/census/census.csv` that the other folders use, and the conventions: masks, wedges, genomes, mirror images, named strategies |
| `cannon/` | the Cannon kit of the exact run: `compile.sh`, `task.sh`, `probe.slurm`, `full.slurm`, its `README.md` and `RESULT.md` |

`pairs.c`, `pairsq.c`, `compare.py` and the kit files are byte-identical to the files that produced the paper's
numbers.

## The four passes

Each program runs the same four passes over the 65536 candidates σ, striped as `<prog> <pass> <stripe> <nstripes> ...`.
Stripe s handles the strategies s, s + nstripes, and so on.

| pass | command | work | output line |
|---|---|---|---|
| self-play | `self s n` | one chain per strategy, 65536 chains | `σ w_CC w_CD w_DC w_DD`: the limiting self-play frequencies. Efficient below the switch line if w_CC = 1 (7639 mutual cooperators); above it if w = (0, ½, ½, 0) (3072 alternators); on the line if w_DD = 0 (14757) |
| rivalry, T>S | `rival s n 1` | for each σ, the co-players τ = 0, 1, … in turn, stopping at the first τ with w_CD > w_DC. That is 206,891,410 chains, 173,015,040 of them for the 2640 rivals, which run through all 65536 | `σ τ_first`, with −1 for none: σ is a rival for T>S |
| rivalry, T<S | `rival s n -1` | the same with w_DC > w_CD: 228,253,906 chains | `σ τ_first`, −1 for a rival for T<S (the 2640 mirror images) |
| stability and tie clause at (−2,2) | `nash s n -2 2` | for each σ, the co-players in turn, stopping once one earns more than E_max = 1 against σ | `σ π(σ,σ) max π(τ,σ) tieviol ntie τ_first`: stable if τ_first = −1 (672). For a stable σ, ntie counts the co-players that tie, and tieviol = 1 if one of them makes σ earn less than π(σ,σ). The tie clause holds for 8 of the 187 partners |

`pairs pair σ τ` (and `pairsq pair σ τ`, which also prints the exact fractions) gives the limit of one pair.
`pairsq cmp n seed` compares the two arithmetics on n random pairs.

**How long they take.**
- On Cannon (job 48068392, `test` partition), all 4096 passes (512 stripes × 4 passes × 2 programs) took 164 s of
  wall time on 48 cores. The probe of 4 stripes (32 passes) took 22 s on 16 cores. The first, double-precision
  computation of 2026-09-03 (`pairs.c` alone) took at most 70 s per pass on 12 local cores.
- Measured here on an Apple M-series Mac (one core, `nice`): the self-play pass of all 65536 strategies takes 0.3 s
  exact and 0.1 s double. The same 4-stripe probe, all passes and both programs, took 28 s of wall time with 4
  processes, so the whole census needs about 128 × 28 s ≈ 1 h on 4 cores, or about 20 min on 12.
- The rivalry passes dominate the cost. An exact stripe of 512 of the stability pass (`nash`) takes 2.6–19 s on one core.

## Commands

Build and self-test (a few seconds):

    make && make selftest

The self-test ends with `19079 65535 0.5 0 0.5 0   exact 1/2 0/1 1/2 0/1`.

Run the whole census locally into `out/`, 512 stripes, 4 at a time (about an hour; `task.sh` runs both programs):

    bash cannon/task.sh local 512 4

Run a probe of four stripes instead (about 30 s):

    bash cannon/task.sh probe 512 4 0 7 100 255

Compare the two programs and write the tables:

    python3 compare.py out 512            # ends in ALL AGREE
    python3 reduce.py out                 # writes ../data/census/{census,census_double,passes}.csv and m2_masks.npz
    python3 check.py                      # the census counts from ../data/census, against the paper; ends in ALL AGREE

On Cannon, copy `pairs.c`, `pairsq.c` and `compare.py` into `cannon/`, then run
`bash compile.sh; jid=$(sbatch --parsable probe.slurm)`, and after that `full.slurm` (see `cannon/README.md`).

`check.py` and `defensible.py` need only Python 3 and numpy. `check.py` reads `../data/census/` and
`../data/arrangement/`. The deposited tables were written with Python 3.10.9 and
numpy 1.23.5. The programs need a C compiler with `unsigned __int128` (gcc or clang); remove `-march=native` from the
`Makefile` if your compiler rejects it.

## Inputs and outputs

- Input: none. The census is computed from the definitions.
- Output of the programs: `out/<prog>_<pass>_<stripe>.txt` and `.err`, 32 MB for 512 stripes. These raw outputs are
  not deposited.
- Output of `reduce.py`: `../data/census/`, described in its README. Nothing else in this folder is written.

## Verification (2026-09-24)

- **Programs.** `make` and `make selftest` were run from a fresh copy (clang 15, arm64); the self-test gave 10⁵
  pairs with max |exact − double| = 3.3e-16 and 0 support mismatches. The local self-play pass of all 65536
  strategies reproduced the deposited self-play columns of both tables exactly. The local 4-stripe probe (stripes 0,
  7, 100 and 255; all four passes; both programs) is **byte-identical**, stdout and stderr, to the corresponding 32
  outputs of the Cannon run, which was compiled with gcc on Cannon (x86-64).
- **The two runs.** `compare.py` on the full raw outputs finds 0 differing decisions in every pass. `check.py` does
  the same on the deposited tables.
- **Defensibility.** `defensible.py` gives 2144 strategies for each sign, the second set the mirror image of the first.
- **Masks.** The six masks of `../data/census/m2_masks.npz`, from the exact census and `defensible.py`, are
  bit-identical to those of the first, independent computation of 2026-09-03, the file the figure scripts read.
- **Counts.** `check.py` reproduces every count listed in its output: 7639, 3072 and 14757 efficient; 2640, 2640,
  5230 and 50 rivals (the 50 split 2, 8 and 40, TFT among them); 2144 defensible and the 496 rivals with a negative
  cycle; the friendly rivals by wedge, 8/1519/80/80 (limit) and 8/1036/80/80 (defensible); 483; 1677; 116 and 2067 on
  the switch line; SI Table 3; 485; the chain counts; the smallest exact gap 2.93e-3; the largest integer 831097.
- **Stability regions.** At (u,v) = (−2,2) the exact stability regions of `../data/arrangement/` (polygons, segments,
  rays and single games, closed, ties admitted) give 672 stable strategies, 656 of them through a two-dimensional
  region and 16 through a segment or ray. They are, strategy by strategy, the 672 of the `nash` column of
  `census.csv`, which holds stability: the symmetric difference is empty. The efficiency and rivalry columns of `../data/arrangement/m2_strategies.csv` equal those of
  `census.csv`.
