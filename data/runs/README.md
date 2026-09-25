# data/runs — the four main Wright–Fisher runs, reduced to per-game tables

These are the four runs behind main text Figures 4 and 5 and SI Figures 2 to 5. Each is reduced to one row per
sampled game, and the tables hold everything those figures draw. All four runs use ε = 10⁻⁴, the 512 games of
`../games/`, uniform mutants over the whole strategy space (the current strategy included), and 10 independent
replicates per game, with the second half of each replicate sampled.

| run (table) | space | N | β | μ | generations | drawn in |
|---|---|---:|---:|---:|---:|---|
| `m1_N100.csv` | 16 binary memory-one strategies | 100 | 3 | 10⁻⁴ | 10⁸ | SI Fig. 2a–h, SI Fig. 4a–c, SI Fig. 5a–c |
| `m1_N1000.csv` | 16 binary memory-one strategies | 1000 | 100 | 10⁻² | 10⁷ | Fig. 4a–c, Fig. 5a–c, SI Fig. 2i–p |
| `m2_N100.csv` | 65536 binary memory-two strategies | 100 | 3 | 10⁻⁴ | 10⁸ | SI Fig. 3a–h, SI Fig. 4d–f, SI Fig. 5d–f |
| `m2_N1000.csv` | 65536 binary memory-two strategies | 1000 | 100 | 10⁻² | 10⁷ | Fig. 4d–f, Fig. 5d–f, SI Fig. 3i–p |

## Files

| file | rows | bytes | what |
|---|---:|---:|---|
| `runs.csv` | 4 | 2264 | the run index: parameters, the kit in `../../simulator/kits/`, the Slurm job id, the seed base, the task index |
| `m1_N100.csv`, `m1_N1000.csv` | 512 | 125286, 125862 | per game: efficiency, the seven atom shares and sizes, the property shares, the winners, and the basin-split flag |
| `m2_N100.csv`, `m2_N1000.csv` | 512 | 180985, 181799 | per game: the same (without the split flag, with the s.d. of the efficiency over the replicates) |
| `m1_N100_counts.csv`, `m1_N1000_counts.csv` | 512 | 79403, 88993 | the memory-one runs whole: per game the count of each of the 16 strategies |
| `m1_strategy_atoms.csv` | 512 | 18857 | the atom of each of the 16 memory-one strategies at each game |
| `wfdata.py` | | | the loader the figure scripts import (`load(space, which)`, `table(name)`, `run(name)`, `cells()`) |
| `check_numbers.py` | | | recomputes from these tables the numbers the paper quotes and compares them with the text |

Every table starts with `#` lines that describe each column, then a header line, then comma-separated values
(`common/tables.py`). Floats are written with Python's `repr`, so they read back as the identical doubles. The rows
are in ipt order 0..511, the order of `../games/games.csv`.

### Columns of the per-game tables

| column | meaning |
|---|---|
| `ipt` | the game (`../games/games.csv`) |
| `isl`, `seed1` | the task index of the game in the run's Cannon array, and the seed of its first replicate. Replicate r = 1..10 ran on `seed1 + r − 1` (Mersenne twister), so `seed1 = seed_base + 10 (isl − 1) + 1`. |
| `u`, `v` | the game, (R, S, T, P) = (1, u, 1 + v, 0), bit-identical to `games.csv` |
| `emax`, `pay`, `E` | E_max = max(R, (S + T)/2); the mean per-round payoff of the population over the sampled halves; the realised efficiency, the mean of pay/E_max over the replicates (left column of Figure 4) |
| `efsd` (memory two) | the s.d. of pay/E_max over the ten replicates |
| `nrep` | replicates (10 at every game) |
| `S_000` … `S_111` | the share of the population, over individuals × sampled generations with the ten replicates pooled, held by the strategies of each atom (efficient–stable–competitive, the ε → 0 classification). The seven add to 1, since 101 is empty. |
| `N_000` … `N_111` | the number of strategies of the space in each atom at the game (adding to 16 or 65536) |
| `P_eff`, `P_nash`, `P_comp` | the share of the population with each property, the sum of `S` over its atoms (Figure 5); `P_nash` holds stability, a symmetric Nash equilibrium against a single deviant |
| `abundant`, `enriched` | the integer code 4e + 2n + c of the most abundant atom (the largest `S` among atoms with `N` > 0) and of the most enriched atom (the largest `S/N`) (middle and right columns of Figure 4) |
| `neff`, `maxpi`, `top` | the effective number of strategies 1/Σπ(s)², the largest single-strategy abundance, and that strategy. At memory one `top` is the memory-one index (bit j = C after outcome j = CC, CD, DC, DD; ALLD 0, Grim 1, TFT 5, CCCD 7, WSLS 9, ALLC 15); at memory two it is the genome code (ALLD 0, ALLC 65535). |
| `split`, `split_sd` (memory one) | 1 where the ten replicates split between two basins, meaning some atom's share has a between-replicate s.d. above 0.05, measured from the per-replicate abundances; that s.d. |

The ORDER of the atoms, the codes and the regions of the plane are those of `../../common/atoms.py`.

## Reading them

The figure scripts use the loader:

```python
sys.path.insert(0, os.path.join(HERE, os.pardir, "data", "runs"))
import wfdata
S, N, E, UV, D = wfdata.load("m2", "F1")     # memory two, N = 1000: (512,7), (512,7), (512,), (512,2), dict
```

`"F1"` (N = 1000) and `"F2"` (N = 100) are the original names of the runs, kept so that the scripts read as the
originals did. Any other code can use `common.tables.read_table("m2_N1000.csv")` and
`common.tables.atom_array(T, "S")`.

The same runs have other names elsewhere in the repository:

| table here | loader (`wfdata.load`), `../strict/` | simulator kit | `../robustness/` |
|---|---|---|---|
| `m1_N1000` | `("m1", "F1")` | `mw` (`sf1.f`) | — |
| `m1_N100` | `("m1", "F2")` | `mw` (`sf2.f`) | — |
| `m2_N1000` | `("m2", "F1")` | `dw1`, regenerated bit for bit as `f1` | `f1_e4` |
| `m2_N100` | `("m2", "F2")` | `dw2`, regenerated bit for bit as `f2` | `f2_e4` |

The table "The same runs appear under different names" in the section on the simulator of the top-level `README.md`
is the same list.

## Where the numbers come from

`../../provenance/four-runs/reduce_runs.py` wrote these tables in the author's environment. It reads the runs through
the loader of the published figures (`FinalFigures/wfdata.py`), so `S`, `N` and `E` are exactly the arrays the
published figures were drawn from. The memory-two atoms come from the exact ε → 0 layer (`DiskM2WF/Opt/exact.py`).
The memory-one atoms come from the exact ε → 0 limit of the four-state pair chains, in rational arithmetic
(`DiskM1WF/Opt/m1disk.py`), checked there against the 45-face arrangement of the memory-one plane.
`../../provenance/four-runs/crosscheck_runs.py` reduced the memory-two packs a second time, with its own parser and an independently built atom table (`atoms512.bin`). `N`,
`E`, `pay`, `emax`, `top` and `maxpi` are identical; `S` agrees to 1.6 × 10⁻¹³, the difference being the summation
order. The memory-one atoms also agree with the memory-two classification of the sixteen strategies embedded as
memory-two strategies, at all 8192 strategy–game pairs.

**Not deposited.** The per-strategy abundance histograms of the memory-two runs are not in the repository:
`dw1_e4.bin`, 253 MB for the 967 games of that campaign, and `dw2_e4.bin`, 134 MB. The same holds for the
per-replicate w-files. Every run can be regenerated bit for bit from its seeds with the kits in
`../../simulator/kits/` (`dw1`, `dw2`, `mw`; `runs.csv` gives the kit, source, job id and seed base). The two
memory-two runs were in fact regenerated on 2026-09-22 (kits `f1` and `f2`), and every summary, w- and h-file was
byte-identical to the original. For memory one the histogram is only 16 numbers per game, so the runs are
deposited whole in `m1_*_counts.csv`. With `m1_strategy_atoms.csv` they give the memory-one `S`, `N`, `top` and
`maxpi` bit for bit.

## The numbers of the text

```
python3 check_numbers.py
```

The script first checks the tables for consistency: the shares add to 1, the sizes add to the size of the space,
and `P_*`, `abundant` and `enriched` equal their recomputation. It then recomputes 146 numbers that the Abstract,
Results, Conclusion, Methods, the SI sections "The evolutionary maps" and "Memory one, for contrast", SI Table 6,
rows 1 and 8 of SI Table 7a, and the legends of Figures 4 and 5 and SI Figures 2 to 5 quote from these four runs.
Each is printed next to the value in the text, and the exit status is the number that differ. On 2026-09-25 all 146
agree. Among them:

- at memory two, N = 1000: 110 is the most abundant atom at 323 games and 111 at 186; 111 is the most enriched atom at
  261 and 110 at 249; the efficiency is below 0.9 at 10 games;
- at memory one, N = 1000: the efficiency is below 0.9 at 324 games;
- at memory two, N = 1000: the shares on efficient and on stable strategies exceed one half together at 509 games, with means 0.95 and
  0.94, and the competitive share has mean 0.37;
- at memory one: the atom 110 is the most abundant at 60 games at N = 1000 and 63 at N = 100. At these games it holds
  win-stay, lose-shift and, where v < 0, also ALLC and CCCD, which are partners there but not competitive. The single
  most abundant strategy is WSLS at 35 of the 60 and 39 of the 63 games, and ALLC or CCCD at most of the others
  (ALLC 17 and CCCD 8 at N = 1000; ALLC 10, CCCD 11 and Grim 3 at N = 100);
- all of SI Table 6.

A number that the text gives rounded is compared at the precision of the text. For example, at memory two the share
of the strategy space in 000 is 0.837 on average over the games, and from 0.64 to 0.91 per game (checked as 0.8), and
the mean efficiency at N = 100 on the Prisoner's Dilemmas below the switch line is 0.595 (checked as 0.6).

Two statistics of the SI section "Replicates" are recomputed here: the median margin of the two largest atom shares
(0.58 and 0.87), and the s.d. of the efficiency over the replicates, which exceeds 0.1 only at 14 and 3 Stag Hunts
(the column `efsd`). The per-replicate counts of that section need the per-replicate output of the regenerations,
which belongs to SI Figure 11.
