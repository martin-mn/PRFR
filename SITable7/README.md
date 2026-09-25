# SI Table 7: robustness of the memory-two maps

The table has three blocks, all of memory-two Wright–Fisher runs over the 512 sampled games with ten replicates each:

- **a**, the eight corners of {100, 1000} × {3, 100} × {10⁻⁴, 10⁻²} for (N, β, μ) at ε = 10⁻⁴, in the reading
  order of SI Figure 8;
- **b**, the runs of main text Figure 4d–f and SI Figure 4d–f at ε = 10⁻³ and 10⁻⁵;
- **c**, the run of main text Figure 4d–f under the mixed mutation kernel, ν = 0, 0.1 and 0.5.

The columns are these:

- agree: games whose most abundant atom is the reference map's (main text Figure 4e for a and c, the same run at
  ε = 10⁻⁴ for b);
- led by 111, led by 110;
- eff. < 0.9;
- 111 in S and 111 in PD/W: the games 111 leads in the wedge S (126 games) and in the Prisoner's Dilemmas of the
  wedge W (86 games);
- PD/W eff. < 0.9.

## Command

```
python3 SITable7/sitable7.py           # from the repository root; ~2 s
```

The script writes two files:

- `SITable7.csv`, one row per run, with its parameters and the seven columns;
- `SITable7.tex`, the rows of the tabular as typeset in the SI.

It prints each row next to the published one and stops if any entry differs. It then prints the numbers of three
SI paragraphs: "Population size, selection strength and mutation rate", "The error rate" and "The mutation kernel".

## Inputs

- `data/robustness/games_<run>.csv` of the fifteen runs, with `replicates_<run>.csv` for the kernel paragraph,
  `runs.csv` (the parameters) and `m2_atom_sizes.csv`, all through `data/robustness/wfruns.py`.
- `data/games/games.csv`: the wedge and quadrant of each game.

The table uses the pooled efficiency `E` of each run. The replicate-mean efficiency, which the analysis of the
kernel runs used, gives the same counts; the script prints both.

## Requirements

Python 3 with numpy.

## Verification (2026-09-24)

All 15 rows (180 entries: five parameters and seven counts each) agree with SI Table 7 of the paper. The text
numbers printed also agree with the SI:

- Population size, selection strength and mutation rate:
  - from the small-population run each factor alone moves the friendly rivals from 89 to 103 (β), 136 (μ) or
    129 (N) games;
  - N together with strong selection or high mutation gives them 123 to 126 of the 126 games of S (dw3 123,
    dw4 126, f1 126);
  - at N = 100, β = 100, μ = 10⁻², 110 leads 33 of those 126 games, a quarter.
- The error rate:
  - the most abundant atom is that of ε = 10⁻⁴ at 494 and 508 games at N = 1000, and at 480 and 500 at N = 100;
  - at N = 100 and ε = 10⁻³, 19 games of S pass from 110 to 111 and none pass back;
  - at N = 1000 and ε = 10⁻³ the efficiency is below 0.9 at 43 games against 10, with mean 0.957 against 0.974;
  - there the eight lose 4 of their 19 PD/W games, to 001 once and 011 three times.
- The mutation kernel (ν = 0, 0.1, 0.5 against ν = 1):
  - the most abundant atom is that of Figure 4e at 461, 469 and 494 games;
  - 111 leads 12, 15 and 18 PD/W games against 19;
  - the efficiency is below 0.9 at 3, 7 and 8 games, with mean 0.987, 0.983 and 0.977;
  - 100 leads 44, 33 and 11 games, of which 30, 25 and 8 lie above the switch line and the rest in PD/W;
  - 000 leads 6, 9 and 6 Snowdrift games above the switch line;
  - at the 100-led games the top strategy of a replicate is a friendly rival in 289 of 440, 273 of 330 and 90 of
    110 replicates, with median share 0.020, 0.014 and 0.025 (the SI's "about 0.02");
  - 111 is the most enriched atom at 324, 331 and 326 games against 261;
  - all ten replicates agree with the pooled map at 474, 473 and 481 games against 487.
