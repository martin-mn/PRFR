# provenance/four-runs — how data/runs/ was made

This folder holds the reduction of the four main Wright–Fisher runs: memory one and memory two, each at N = 100
(β = 3, μ = 10⁻⁴) and at N = 1000 (β = 100, μ = 10⁻²), all at ε = 10⁻⁴. The full outputs are reduced to the
per-game tables of `../../data/runs/`, and a second, independent reduction checks them.

**These scripts run only in the author's environment.** They read the private full outputs and the original loaders
of the figure scripts. Both are reached through one variable at the top of each script, `AUTHOR_ENV`, set to the
author's project tree, and nothing else in the repository refers to it. They are deposited as the record of how the
tables were made. Nothing in the repository needs them to run: the figure scripts read only `../../data/runs/`.

| script | reads (under `AUTHOR_ENV`) | writes |
|---|---|---|
| `reduce_runs.py` | `PartnersRivals1/FinalFigures/wfdata.py`, the loader of the published figures. That loader reads the memory-two packs `DiskM2WF/Data/dw1_e4`, `dw2_e4` `{.idx,.bin,.win}` through `DiskM2WF/Opt/figF4.collect` and `wfload`, with the exact ε → 0 classification of `DiskM2WF/Opt/exact.py`, and the memory-one packs `DiskM1WF/Data/mw1_e4.tsv`, `mw2_e4.tsv` through `DiskM1WF/Opt/m1load`, with `m1_atoms_512.npz`. The script also reads `DiskM1WF/Data/bistable.tsv`. | `../../data/runs/*.csv` |
| `crosscheck_runs.py` | `DiskM2WF/Data/dw1_e4`, `dw2_e4` `{.idx,.bin}` with its own parser, and `PartnersRivals/Cannon/atoms512.bin` (the atom of every strategy at every game, built separately for the robustness kits `c1`–`c4`, `eh`, `el`, `f1`, `f2` and `lm`; deposited compressed as `simulator/atoms/atoms512.bin.gz`) | nothing; it asserts and prints |

Commands, from this folder:

```
python3 -B reduce_runs.py        # about 20 s; rewrites data/runs/*.csv
python3 -B crosscheck_runs.py    # a few seconds; exit status 0 if every check passes
```

## What reduce_runs.py does

For each run it calls `wfdata.load(space, which)`, the call that drew the published figures. That gives `S`, the
share of the population in each atom (512 × 7, pooled over the ten replicates); `N`, the atom sizes; `E`, the
efficiency; and the games. It adds these columns:

- from the pack's per-game line: `emax`, `pay` and, at memory two, `efsd`, `nrep`, `neff`, `maxpi` and `top`. At
  memory one `neff`, `maxpi` and `top` are computed from the 16 counts.
- the task index `isl` and the first seed `seed1` of each game. These come from the kits' seed rule
  `iseed = iseedb + 10 (isl − 1) + irep`: seed bases 10000000 (memory one, N = 1000, `sf1.f`), 11000000 (memory
  one, N = 100, `sf2.f`), 8000000 (`dw1`) and 9000000 (`dw2`). At memory two `isl` is checked against the packs.
- the property shares and the two winners, computed as `fig5.py` and `fig4.py` compute them.
- at memory one, the basin-split flag of `bistable.tsv`.

It asserts that the games equal `data/games/` bit for bit, that `E` is the pack's `ef` column, and that the written
tables read back to the identical `S`, `N` and `E`. The memory-one packs are small enough to deposit whole, so it
also writes the per-strategy counts and the atoms of the 16 strategies. It checks that these give the memory-one
`S` bit for bit.

## What crosscheck_runs.py checks (2026-09-24)

- **memory two**: the `.idx`/`.bin` packs are parsed afresh and every strategy is classified by `atoms512.bin`, not by
  `exact.py`. `N` is identical at all 512 games of both runs. `S` agrees to max |diff| 1.57 × 10⁻¹³ (N = 100) and
  1.35 × 10⁻¹³ (N = 1000); only the summation order differs. `E`, `pay`, `emax`, `top`, `maxpi`, `isl` and `seed1`
  are identical, and `neff` agrees to 10⁻⁹.
- **memory one**: the atoms of the 16 strategies at the 512 games (`m1_strategy_atoms.csv`) are compared with the
  memory-two classification `atoms512.bin` of the same strategies, embedded as memory-two strategies that ignore
  the round before. None of the 8192 differ.

## Not deposited, and why

The memory-two abundance histograms hold the pooled abundance of each of the 65536 strategies at each game:
`dw1_e4.bin`, 253 MB over the 967 games of that campaign, of which the 512 are a block, and `dw2_e4.bin`, 134 MB.
The per-replicate `.win` files are not deposited either. The repository holds reduced data only. The runs can be
regenerated bit for bit from the kits `simulator/kits/dw1`, `dw2` and `mw` with the seeds of `data/runs/runs.csv`,
and this has been tested: on 2026-09-22 the two memory-two runs were regenerated (Cannon kits `f1`, `f2`, jobs
47837723 and 47837725), and every summary, w- and h-file of all 512 games was byte-identical to the original.
