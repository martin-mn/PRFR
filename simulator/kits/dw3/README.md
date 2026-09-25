# kits/dw3 — cube corner N = 1000, β = 100, μ = 10⁻⁴ (SI Figure 8)

One corner of the cube {100, 1000} × {3, 100} × {10⁻⁴, 10⁻²} of SI Figure 8 and SI Table 7a: the large population and the strong selection of main text Figure 4 with the rare mutation of the small-population run. Run length 10⁷ generations, as at every corner with N = 1000 (10⁸ generations were run at N = 100 with μ = 10⁻⁴ only).

| run | N | β | μ | ε | ν | generations | replicates | tasks (isl) | seed base s0 | display items |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `dw3` | 1000 | 100 | 10^-4 | 10^-4 | 1 | 10^7 | 10 | 1368–2901:3 | 10000000 | SI Fig 8g/o/w (corner N=1000 beta=100 mu=1e-4), SI Table 7a |

Seeds: replicate r (1..10) of task isl ran on the Mersenne-twister seed s0 + 10 (isl − 1) + r (`iseed=iseedb+(isl-1)*nper+irep` in the source); every seed is listed in `../../seeds_by_game.csv`.

## Source

`sf.f` is `../dw2/sf.f` with the header comment and four parameter lines changed (`n=1000`, `iseedb=10000000`, `bval=100.d+00`, `itv=10000000`; `uval=1.d-04` is dw2's); `diff ../dw2/sf.f sf.f` is the audit. It is also the template from which `../mkkits.py` generates the kits c1–c4, eh, el, f1 and f2.

## Files

| file | what |
|---|---|
| `compile.sh` | `bash compile.sh 1e7` builds `sf_1e7.x` (`1e8` also possible) |
| `pack.py` | packs a finished run directory into the per-run files `<run>_<e>.{idx,bin,win[,rep]}` (standard library only) |
| `probe_1e7.slurm` | 8-cell probe |
| `probe_1e8.slurm` | 8-cell probe at 10⁸ generations (a convergence check, not in the paper) |
| `prod_1e7.slurm` | **the production array of the paper**, `--array=1368-2901:3` |
| `prod_1e8.slurm` | 10⁸ variant (not run) |
| `sf.f` | the main program exactly as it ran (the Wright–Fisher generation loop, the payoff cache, the output) |
| `submit.sh` | stages `games.dat` into the run directory, submits one array with `sbatch --parsable`, records its id |
| `verify.sh` | completion per task from `sacct`, and per cell from the output files |

Not stored here, because every kit shares them: `payf2.f`, `payf3.f` (the stationary distribution of the 16-state pair
chain and the pair payoffs), `mt.f`, `mtb.f` (the Mersenne twister) and `games.dat`. `bash ../stage.sh dw3` copies them
from `../../src/` and `../../games/` into this directory, which is then exactly the directory that ran on the cluster.

## How it was run

On the cluster, in this directory:

    bash ../stage.sh dw3
    bash compile.sh 1e7
    bash submit.sh probe7 ; bash verify.sh probe7
    bash submit.sh prod7                 # 512 tasks (tag vor7)
    bash verify.sh vor7
    python3 pack.py run_1e7 packed       # -> packed/dw3_e4.{idx,bin,win}

Author's cluster settings (Harvard FASRC Cannon), kept as they ran: the Slurm partition (`#SBATCH -p shared`), the compiler module (`module load intel/25.2.1-fasrc01`, `ifx -O3 -xHost -fp-model precise`) and the cross-project job ledger `~/jobs.tsv` that `submit.sh` appends to (`../README.md` shows how to make that append conditional on `PRFR_LEDGER`). Change these for another cluster; nothing else in the kit depends on them. The format of every output file and pack is described in `../../README.md`.

## Record (author's cluster)

2026-09-11/12: probe 46096617 (8 cells, 57–78 min), production `vor7` 46108583: 512 of 512 COMPLETED, 483 core-hours, mean 57 min per task. A 10⁸-generation probe of 8 cells, 46108668, completed 2026-09-13; it is not used in the paper (at those cells the dominant class was unchanged).
