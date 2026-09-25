# SI Table 6: the two memory-two maps by piece of the plane

The 512 sampled games of the two memory-two runs at ε = 10⁻⁴:

- N = 100, β = 3, μ = 10⁻⁴ (run `f2_e4`, SI Figure 4d–f);
- N = 1000, β = 100, μ = 10⁻² (run `f1_e4`, main text Figure 4d–f).

The games are grouped by quadrant (PD, SH, HA, SD) and by wedge (W, S, N, E; SI Table 2). The Snowdrift games form
one row. For each piece and each run the table gives four numbers:

- the number of games whose most abundant atom is 110;
- the number whose most abundant atom is 111;
- any other leading atom, named, with its number of games;
- the number of games with realised efficiency below 0.9.

## Command

```
python3 SITable6/sitable6.py           # from the repository root; ~1 s
```

The script writes two files:

- `SITable6.csv`, the table (commented header, one row per piece);
- `SITable6.tex`, the rows of the tabular as typeset in the SI.

On the terminal it prints each row next to the published one and stops if any entry differs. It then prints the
numbers of the SI paragraph "The maps by region" and three of "Which partners win", which read the same two runs.

## Inputs

- `data/robustness/games_{f2_e4,f1_e4}.csv` and `m2_atom_sizes.csv`, through `data/robustness/wfruns.py`.
- `data/games/games.csv`: the quadrant and wedge of each game.

The most abundant atom is the one of the figures: the largest pooled share among the atoms that have strategies at
the game (`common.wfsheet.winners`).

## Requirements

Python 3 with numpy.

## Verification (2026-09-24)

All 9 rows (81 entries) agree with SI Table 6 of the paper. The text numbers printed also agree with the SI:

- At N = 1000, 111 leads all 126 games of the wedge S, 14 Prisoner's Dilemmas and 27 Harmony games above the
  switch line.
- The eight friendly rivals of SI Table 4a are the only partners at 20 PD/W games. 111 leads 19 of them at
  N = 1000, at radii 2.4 to 16.2. The twentieth is the worst game, (u, v) = (−26.99, 14.68), at radius 30.7. Its
  efficiency is −0.021 at N = 100 and 0.19 at N = 1000, the lowest of both maps.
- The two 100 games at N = 1000 lie along T = S: (1.95, 0.95) and (4.34, 3.35).
- The mean efficiency over the 86 PD/W games is 0.595 at N = 100 and 0.961 at N = 1000.
- The efficient share exceeds 1/2 at 458 and 511 games, and the share on stable strategies at 468 and 510.
- At N = 100 the median share of 111 in the wedge S is 0.36, and 111 makes up 0.199 of the partners there.
- The eight stand beside 28 to 2732 other partners at 66 PD/W games, and lead none of them at N = 100.
- At N = 1000, 110 leads all 159 games of the wedge W that have 110 strategies; the fewest there is 28.
- At N = 1000 the eight are depleted at all 84 Stag Hunts of W and at 32 of the 86 PD/W games.
