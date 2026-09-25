# kits/dw1 — the memory-two run at N = 1000, β = 100, μ = 10⁻² (main text Figure 4d–f)

The large-population memory-two run of the paper (called F1 in the author's tree): main text Figures 4d–f and 5d–f, SI Figures 3i–p, 6f, 7f, the corner N = 1000, β = 100, μ = 10⁻² of SI Figure 8, the middle row of SI Figure 9 and the row ν = 1 of SI Figure 12. The kit was built for a larger campaign over 967 games (a donation ray, a polar disk grid and a square of games, rows 1–455 of `games.dat`, none of them used in this paper); the paper uses its **sunflower block**, rows 456–967, the 512 games of `data/games/`, at ε = 10⁻⁴ (task indices 1368–2901 step 3).

| run | N | β | μ | ε | ν | generations | replicates | tasks (isl) | seed base s0 | display items |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `m2_N1000` | 1000 | 100 | 10^-2 | 10^-4 | 1 | 10^7 | 10 | 1368–2901:3 | 8000000 | Fig 4d-f, Fig 5d-f, SI Fig 3i-p, SI Fig 6f, SI Fig 7f, SI Fig 8h/p/x (corner N=1000 beta=100 mu=1e-2), SI Fig 9d-f, SI Fig 12j-l (nu=1), SI Tables 6 and 7 |

Seeds: replicate r (1..10) of task isl ran on the Mersenne-twister seed s0 + 10 (isl − 1) + r (`iseed=iseedb+(isl-1)*nper+irep` in the source); every seed is listed in `../../seeds_by_game.csv`.

## Source

`sf.f` was generated from the Wright–Fisher code of the companion paper (DonationWF `wf3`) by 12 asserted substitutions (the game list replaces the donation game; the generation loop is untouched), and then the game-list capacity `mgam` was raised from 512 to 2048 when the sunflower rows were added. `mgam` dimensions the game list only; the rebuild was tested bit-identical on a completed task (`ident.slurm`, array 44383771). The generator and the wf3 source are in `provenance/simulator-notes/lineage/`, where the regeneration is checked.

## Files

| file | what |
|---|---|
| `compile.sh` | builds `sf.x` (the run length 10⁷ is in the source) |
| `ident.slurm` | the bit-identity test of the rebuilt binary |
| `pack.py` | packs `run/` into `dw1_e{2,3,4}.{idx,bin,win}`; it assumes the production length (5·10⁹ samples per replicate) |
| `probe.slurm` | the rate probe of the earlier blocks (not used in this paper) |
| `probe_vor.slurm` | the 5-cell rate probe of the sunflower block (isl 1368, 2892, 2895, 2898, 2901) |
| `prod_disk.slurm` | the earlier disk block at three error rates (not submitted) |
| `prod_disk_e4.slurm` | the earlier disk block at ε = 10⁻⁴ (not used in this paper) |
| `prod_sq.slurm` | the earlier square block (not used in this paper) |
| `prod_vor_e4.slurm` | **the production array of the paper**: the 512 sunflower games at ε = 10⁻⁴, `--array=1368-2901:3` |
| `prod_vor_e4_rest.slurm` | the same minus the five probe cells (prepared, not needed) |
| `sf.f` | the main program exactly as it ran (the Wright–Fisher generation loop, the payoff cache, the output) |
| `submit.sh` | stages `games.dat` into the run directory, submits one array with `sbatch --parsable`, records its id |
| `verify.sh` | completion per task from `sacct`, and per cell from the output files |

Not stored here, because every kit shares them: `payf2.f`, `payf3.f` (the stationary distribution of the 16-state pair
chain and the pair payoffs), `mt.f`, `mtb.f` (the Mersenne twister) and `games.dat`. `bash ../stage.sh dw1` copies them
from `../../src/` and `../../games/` into this directory, which is then exactly the directory that ran on the cluster.

## How it was run

On the cluster, in this directory:

    bash ../stage.sh dw1
    bash compile.sh                      # -> sf.x
    bash submit.sh vor_probe             # 5 tasks; then bash verify.sh vor_probe and read the rate
    bash submit.sh vor_e4                # 512 tasks, --array=1368-2901:3 (the probe cells are skipped when complete)
    bash verify.sh vor_e4
    python3 pack.py run packed           # -> packed/dw1_e4.{idx,bin,win}  (the sunflower games are gid 2000-2511)

Author's cluster settings (Harvard FASRC Cannon), kept as they ran: the Slurm partition (`#SBATCH -p shared`), the compiler module (`module load intel/25.2.1-fasrc01`, `ifx -O3 -xHost -fp-model precise`) and the cross-project job ledger `~/jobs.tsv` that `submit.sh` appends to (`../README.md` shows how to make that append conditional on `PRFR_LEDGER`). Change these for another cluster; nothing else in the kit depends on them. The format of every output file and pack is described in `../../README.md`.

## Record (author's cluster)

2026-09-04: probe `vor_probe` 44383754 (5 cells, 63.6–80.0 min per cell), bit-identity test `ident` 44383771 (identical), production `vor_e4` 44394541: 512 of 512 COMPLETED, 557.8 core-hours. Regenerated bit for bit on 2026-09-22 by kit `f1` (same code and seeds plus the per-replicate count file): every summary, w- and h-file of the 512 games identical.
