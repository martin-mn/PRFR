# kits/lm — the large-population memory-two run under a mixed mutation kernel (SI Figure 12)

SI Figure 12 and SI Table 7c: the run of main text Figure 4d–f (N = 1000, β = 100, μ = 10⁻², ε = 10⁻⁴) with the mutation step changed. A mutating individual adopts, with probability ν, a strategy drawn uniformly from all 65536 (its own included, as in every other run) and otherwise the strategy that differs from its own at one of the 16 positions, chosen uniformly. ν = 0, 0.1, 0.5 are rows a–i; ν = 1, rows j–l, is the run of `../dw1`.

| run | N | β | μ | ε | ν | generations | replicates | tasks (isl) | seed base s0 | display items |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `lm_g0` | 1000 | 100 | 10^-2 | 10^-4 | 0 | 10^7 | 10 | 1368–2901:3 | 30000000 | SI Fig 12a-c (nu=0), SI Table 7c |
| `lm_g01` | 1000 | 100 | 10^-2 | 10^-4 | 0.1 | 10^7 | 10 | 1368–2901:3 | 31000000 | SI Fig 12d-f (nu=0.1), SI Table 7c |
| `lm_g05` | 1000 | 100 | 10^-2 | 10^-4 | 0.5 | 10^7 | 10 | 1368–2901:3 | 32000000 | SI Fig 12g-i (nu=0.5), SI Table 7c |

Seeds: replicate r (1..10) of task isl ran on the Mersenne-twister seed s0 + 10 (isl − 1) + r (`iseed=iseedb+(isl-1)*nper+irep` in the source); every seed is listed in `../../seeds_by_game.csv`.

## Source

`sf.f` is `../f1/sf.f` with the mutation step changed and one parameter added, by the asserted substitutions of `mklm.py` (`diff ../f1/sf.f sf.f` is the audit). In the source ν is called `pglob`, because the name `nu` was already taken (the number of mutation-rate values). One uniform draw decides global or local and a second supplies the genome or the position, so ν = 1 is dw1's process but not dw1's random stream. `pglob` and the seed base are compile-time parameters that `compile.sh` sets (g0: ν = 0, s0 = 30000000; g01: 0.1, 31000000; g05: 0.5, 32000000; g1: ν = 1, 39000000, for local tests only, never submitted). `python3 mklm.py` (after `bash ../stage.sh f1`) regenerates `sf.f` and `pack.py` byte for byte.

## Files

| file | what |
|---|---|
| `compile.sh` | `bash compile.sh g0|g01|g05` builds `sf_<g>.x`; `FC=gfortran ITEND=20000 bash compile.sh g0` for a short local build |
| `lm.slurm` | the array script; `submit.sh` passes the variant as `G` |
| `mklm.py` | builds `sf.f` and `pack.py` from `../f1` (its input path made relative and its docstring reworded for the repository) |
| `pack.py` | packs `run_<g>/` into `lm_<g>_e4.{idx,bin,win,rep}` |
| `sf.f` | the main program as it ran (the source of g0; `compile.sh` sets pglob and iseedb for g01 and g05) |
| `submit.sh` | `bash submit.sh probe|prod g0|g01|g05` |
| `verify.sh` | `bash verify.sh probe|prod g0|g01|g05` |

Not stored here, because every kit shares them: `payf2.f`, `payf3.f` (the stationary distribution of the 16-state pair
chain and the pair payoffs), `mt.f`, `mtb.f` (the Mersenne twister) and `games.dat`. `bash ../stage.sh lm` copies them
from `../../src/` and `../../games/` into this directory, which is then exactly the directory that ran on the cluster.

## How it was run

On the cluster, in this directory:

    bash ../stage.sh lm
    bash compile.sh g0 ; bash compile.sh g01 ; bash compile.sh g05
    bash submit.sh probe g0 ; bash verify.sh probe g0          # 4 cells: isl 1620 2148 2334 2538 (likewise g01, g05)
    bash submit.sh prod g0  ; bash verify.sh prod g0           # 512 tasks, --array=1368-2901:3
    python3 pack.py run_g0 packed                              # -> packed/lm_g0_e4.{idx,bin,win,rep}

Author's cluster settings (Harvard FASRC Cannon), kept as they ran: the Slurm partition (`#SBATCH -p shared`), the compiler module (`module load intel/25.2.1-fasrc01`, `ifx -O3 -xHost -fp-model precise`) and the cross-project job ledger `~/jobs.tsv` that `submit.sh` appends to (`../README.md` shows how to make that append conditional on `PRFR_LEDGER`). Change these for another cluster; nothing else in the kit depends on them. The format of every output file and pack is described in `../../README.md`.

## Record (author's cluster)

2026-09-24: probes g0 48161421, g01 48161433, g05 48161436 (4 cells each); production g0 48181135, g01 48181161, g05 48181182. The author's tree holds no `verify.sh` transcript of the production arrays; the packs hold all 512 games with 10 replicates and the full sample count each (checked by `provenance/simulator-notes/check_seeds_vs_packs.py`).
