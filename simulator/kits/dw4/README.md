# kits/dw4 — cube corner N = 1000, β = 3, μ = 10⁻² (SI Figure 8)

One corner of the cube of SI Figure 8 and SI Table 7a: the large population and the frequent mutation of main text Figure 4 with the weak selection of the small-population run.

| run | N | β | μ | ε | ν | generations | replicates | tasks (isl) | seed base s0 | display items |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `dw4` | 1000 | 3 | 10^-2 | 10^-4 | 1 | 10^7 | 10 | 1368–2901:3 | 11000000 | SI Fig 8d/l/t (corner N=1000 beta=3 mu=1e-2), SI Table 7a |

Seeds: replicate r (1..10) of task isl ran on the Mersenne-twister seed s0 + 10 (isl − 1) + r (`iseed=iseedb+(isl-1)*nper+irep` in the source); every seed is listed in `../../seeds_by_game.csv`.

## Source

`sf.f` is `../dw3/sf.f` with the seed base and two parameter lines changed (`iseedb=11000000`, `uval=1.d-02`, `bval=3.d+00`).

## Files

| file | what |
|---|---|
| `compile.sh` | `bash compile.sh 1e7` builds `sf_1e7.x` |
| `pack.py` | packs a finished run directory into the per-run files `<run>_<e>.{idx,bin,win[,rep]}` (standard library only) |
| `probe_1e7.slurm` | 8-cell probe |
| `prod_1e7.slurm` | **the production array of the paper**, `--array=1368-2901:3` |
| `sf.f` | the main program exactly as it ran (the Wright–Fisher generation loop, the payoff cache, the output) |
| `submit.sh` | stages `games.dat` into the run directory, submits one array with `sbatch --parsable`, records its id |
| `verify.sh` | completion per task from `sacct`, and per cell from the output files |

Not stored here, because every kit shares them: `payf2.f`, `payf3.f` (the stationary distribution of the 16-state pair
chain and the pair payoffs), `mt.f`, `mtb.f` (the Mersenne twister) and `games.dat`. `bash ../stage.sh dw4` copies them
from `../../src/` and `../../games/` into this directory, which is then exactly the directory that ran on the cluster.

## How it was run

On the cluster, in this directory:

    bash ../stage.sh dw4
    bash compile.sh 1e7
    bash submit.sh probe7 ; bash verify.sh probe7
    bash submit.sh prod7 ; bash verify.sh vor7
    python3 pack.py run_1e7 packed       # -> packed/dw4_e4.{idx,bin,win}

Author's cluster settings (Harvard FASRC Cannon), kept as they ran: the Slurm partition (`#SBATCH -p shared`), the compiler module (`module load intel/25.2.1-fasrc01`, `ifx -O3 -xHost -fp-model precise`) and the cross-project job ledger `~/jobs.tsv` that `submit.sh` appends to (`../README.md` shows how to make that append conditional on `PRFR_LEDGER`). Change these for another cluster; nothing else in the kit depends on them. The format of every output file and pack is described in `../../README.md`.

## Record (author's cluster)

2026-09-11/12: probe 46096640 (8 cells), production `vor7` 46108584: 512 of 512 COMPLETED, 613 core-hours, mean 72 min per task.
