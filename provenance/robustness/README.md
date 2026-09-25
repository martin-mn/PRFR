# provenance/robustness — how data/robustness was made

Two scripts. They are kept for the record: both read the private full outputs of the simulator, which are not
deposited (1.9 GB of per-strategy abundance vectors). A reader who has regenerated the runs from the seeds can run
them after pointing `AUTHOR_ROOT` at the regenerated packs. Neither is needed to redraw a figure or to recompute a
table.

| script | reads | writes | time |
|---|---|---|---|
| `reduce.py` | the packs `<run>.{idx,bin,rep,win}` of the fifteen runs, and `atoms512.bin` | every table in `data/robustness/`: `runs.csv`, `m2_atom_sizes.csv`, `games_<run>.csv`, `replicates_<run>.csv` | ≈ 5 s |
| `crosscheck.py` | the tables in `data/robustness/`, and the same runs through the loaders of the original figure scripts | a report on the terminal; it stops at the first difference that would change a figure or a table | ≈ 30 s |

```
python3 -B provenance/robustness/reduce.py          # from the repository root
python3 -B provenance/robustness/crosscheck.py
```

**Author's environment.** Each script has a single path into the private tree, the variable `AUTHOR_ROOT` at its top,
set to the author's project tree. All other paths are relative to that variable or to the repository.

- `reduce.py` reads from `PartnersRivals/Data/` (the packs of the kits `f1`, `f2`, `c1`–`c4`, `dw3`, `dw4`, `eh`
  and `el`), from `PartnersRivals1/Cannon/lm/packed/` (the kit `lm`), and from `PartnersRivals/Cannon/atoms512.bin`.
  Its only other import is `common/`.
- `crosscheck.py` also reads the packs of Figure 4's original runs in `DiskM2WF/Data/` (`dw1_e4.*`, `dw2_e4.*`), and
  imports the original figure scripts' loaders from `PartnersRivals1/FinalFigures/`
  (`wfdata.py`, `wfrep.py`, `sifig8.py`) and, through them, `DiskM2WF/Opt/` (`exact.py`, `wfload.py`,
  `figF4.py`, `vor.py`). It imports them with bytecode writing turned off, so it writes nothing there.

Requirements: Python 3 with numpy; `crosscheck.py` also needs matplotlib and scipy, which the original loaders import.

## What reduce.py does

For each run:

1. **Checks the pack against the repository.** Each game of the `.idx` must be the game of `data/games/games.csv` bit
   for bit (`cS = u`, `cT = 1 + v`, same tag and gid, the same Emax). There must be ten replicates per game. The
   `total` column must equal `10 · (generations/2) · N` with the N and generations of `runs.csv`. The task indices
   must follow `isl = 3(ig − 1) + ie`. The number of distinct strategies must be the number of non-zero entries of the
   abundance vector.
2. **Computes the pooled atom shares.** It divides the float32 abundance vector (`.bin`) of each game by its sum and
   sums it over the atoms of `atoms512.bin` with `np.bincount`, exactly as the original loader `wfrep.py` did.
   It asserts that the atom 101 is empty.
3. **Reads the per-replicate output.** From the `.rep` it takes each replicate's efficiency and atom shares, and
   asserts that the ten average to the pooled shares within 2e-6 (the check of `wfrep.py`). From the `.win` it takes
   each replicate's most abundant strategy, its share and its payoff against itself, and looks up that strategy's
   atom in `atoms512.bin`. It also records each replicate's seed, `seed_base + (isl − 1)·10 + rep`.
4. **Writes the two tables of the run**, and then `runs.csv` and `m2_atom_sizes.csv`. The parameters in `runs.csv`
   (N, β, μ, ε, ν, generations, seed base, slurm offset, job ID) are those of the kits' `sf.f`, their READMEs and
   `JOBID` files. They are written out from the `RUNS` table at the top of `reduce.py`.

## What crosscheck.py found (2026-09-24)

```
atoms512.bin == exact.masks at all 512 x 65536 (strategy, game) pairs
f1_e4 == dw1_e4 (its 512 sampled games): .idx rows, .win rows (5120) and .bin rows byte-identical
f2_e4 == dw2_e4 (its 512 sampled games): .idx rows, .win rows (5120) and .bin rows byte-identical
f1_e4  vs wfdata.load('m2', 'F1')   games, N, E identical; S max|diff| 1.3e-13; most abundant and most enriched atom identical
f2_e4  vs wfdata.load('m2', 'F2')   games, N, E identical; S max|diff| 1.6e-13; ...
dw4_e4 vs sifig8.load_idx(dw4)      games, N, E identical; S max|diff| 1.1e-13; ...
dw3_e4 vs sifig8.load_idx(dw3)      games, N, E identical; S max|diff| 2.7e-13; ...
c1..c4, eh_e3, eh_e5, el_e3, el_e5, lm_g0/g01/g05  vs wfrep.load:  bit-identical
every run with a .rep vs wfrep.load: R, ER, LEAD identical
all checks passed
```

The shares of `f1_e4`, `f2_e4`, `dw3_e4` and `dw4_e4` differ from the originals in the last bits because the originals
summed over each atom with a mask of the exact classification, not with `np.bincount`. No figure and no table changes:
SI Figures 8–12 redraw identical to the published PDFs, and SI Tables 6 and 7 reproduce in every entry.

The second and third lines are the comparison of the packs of `f1_e4` and `f2_e4` with those of Figure 4's original
runs: the regenerations are the published runs, bit for bit, with the per-replicate output added.
