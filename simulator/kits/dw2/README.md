# kits/dw2 — the memory-two run at N = 100, β = 3, μ = 10⁻⁴ (SI Figure 4d–f)

The small-population memory-two run of the paper (F2 in the author's tree): SI Figures 3a–h, 4d–f, 5d–f, 6e, 7e, the corner N = 100, β = 3, μ = 10⁻⁴ of SI Figure 8 and the middle row of SI Figure 10.

| run | N | β | μ | ε | ν | generations | replicates | tasks (isl) | seed base s0 | display items |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `m2_N100` | 100 | 3 | 10^-4 | 10^-4 | 1 | 10^8 | 10 | 1368–2901:3 | 9000000 | SI Fig 3a-h, SI Fig 4d-f, SI Fig 5d-f, SI Fig 6e, SI Fig 7e, SI Fig 8a/i/q (corner N=100 beta=3 mu=1e-4), SI Fig 10d-f, SI Tables 6 and 7 |

Seeds: replicate r (1..10) of task isl ran on the Mersenne-twister seed s0 + 10 (isl − 1) + r (`iseed=iseedb+(isl-1)*nper+irep` in the source); every seed is listed in `../../seeds_by_game.csv`.

## Source

`sf.f` is `../dw1/sf.f` with five parameter lines changed and nothing else (`diff ../dw1/sf.f sf.f`): `n=100`, `iseedb=9000000`, `uval=1.d-04`, `bval=3.d+00`, `itv=100000000`. (Its header comment still carries dw1's grid line.)

## Files

| file | what |
|---|---|
| `compile.sh` | `bash compile.sh 1e8` builds `sf_1e8.x` (10⁸ generations; a 10⁹ variant was prepared, not run) |
| `pack.py` | packs a finished run directory into the per-run files `<run>_<e>.{idx,bin,win[,rep]}` (standard library only) |
| `probe_1e8.slurm` | 5-cell probe at 10⁸ generations |
| `probe_1e9.slurm` | 5-cell probe at 10⁹ (not run) |
| `prod_1e8.slurm` | **the production array of the paper**, `--array=1368-2901:3` |
| `prod_1e9.slurm` | 10⁹ variant (not run) |
| `sf.f` | the main program exactly as it ran (the Wright–Fisher generation loop, the payoff cache, the output) |
| `submit.sh` | stages `games.dat` into the run directory, submits one array with `sbatch --parsable`, records its id |
| `verify.sh` | completion per task from `sacct`, and per cell from the output files |

Not stored here, because every kit shares them: `payf2.f`, `payf3.f` (the stationary distribution of the 16-state pair
chain and the pair payoffs), `mt.f`, `mtb.f` (the Mersenne twister) and `games.dat`. `bash ../stage.sh dw2` copies them
from `../../src/` and `../../games/` into this directory, which is then exactly the directory that ran on the cluster.

## How it was run

On the cluster, in this directory:

    bash ../stage.sh dw2
    bash compile.sh 1e8                  # -> sf_1e8.x
    bash submit.sh prod8                 # 512 tasks (tag vor8)
    bash verify.sh vor8
    python3 pack.py run_1e8 packed       # -> packed/dw2_e4.{idx,bin,win}

Author's cluster settings (Harvard FASRC Cannon), kept as they ran: the Slurm partition (`#SBATCH -p shared`), the compiler module (`module load intel/25.2.1-fasrc01`, `ifx -O3 -xHost -fp-model precise`) and the cross-project job ledger `~/jobs.tsv` that `submit.sh` appends to (`../README.md` shows how to make that append conditional on `PRFR_LEDGER`). Change these for another cluster; nothing else in the kit depends on them. The format of every output file and pack is described in `../../README.md`.

## Record (author's cluster)

2026-09-07: production `vor8` 45049704: 512 of 512 COMPLETED, 572.1 core-hours, 57.5–77.3 min per task. Regenerated bit for bit on 2026-09-22 by kit `f2`: every output file of the 512 games identical.
