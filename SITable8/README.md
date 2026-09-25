# SI Table 8: the sixteen binary memory-one strategies

This folder recomputes SI Table 8 of the paper from first principles and compares it with the table as printed. For
each of the 2^4 = 16 binary memory-one strategies the table gives four things: where the strategy is efficient, where
it is a Nash equilibrium, for which sign of T − S it is competitive (a rival), and its class. Every value is exact and
taken in the limit of rare errors. The same computation checks the statements of SI §10 (*Memory one, for contrast*)
and the memory-one statements of SI §5 that rest on the table.

## Reproducing

```
python3 sitable8.py          # < 1 s; standard library only
python3 sitable8.py --m2     # also tests against all 65536 memory-two co-players: about 30 s, 0.6 GB, needs numpy
python3 sitable8.py --tex ../path/to/ms.tex   # compare with SI Table 8 as typeset in a LaTeX file
```

The script prints the table and compares it with the printed table cell by cell. It then checks each statement and
writes the two CSV files listed below. `output.txt` is the output of `python3 sitable8.py --m2`. The script exits
with status 1 if any cell differs from the printed table or any statement check fails, and 0 otherwise.

## Files

| file | what it is |
|---|---|
| `sitable8.py` | the computation and the comparison |
| `sitable8.csv` | the computed table, 16 rows: `genome, id, name, efficient, nash, rival_for, class` (in the cells, `&` means "and"; `nash` is the set of games at which the strategy is stable, a symmetric Nash equilibrium against a single deviant) |
| `m1_pairs.csv` | the exact ε→0 outcome frequencies `w_CC, w_CD, w_DC, w_DD` of all 256 ordered pairs, as fractions, seen from `sigma`'s side |
| `output.txt` | the printed output of `sitable8.py --m2` |

A strategy is written by its answers after CC, CD, DC and DD (own action first), for example `CDDC` for win-stay,
lose-shift. Its `id` is Σ 2^k over the positions k with answer C. The games are (R, S, T, P) = (1, u, 1+v, 0).

## Method

1. **The pair limits.** For each ordered pair, the stationary distribution of the four-state chain with independent
   errors (rate ε) is a rational function of ε. By the Markov chain tree theorem, each outcome's weight is
   proportional to a diagonal cofactor of I − P(ε). The limit ε → 0 is the ratio of the lowest-order coefficients of
   these cofactors. This is the pair computation of `FinalFigures/m1atoms.py`, the script behind Figures 1b, 2a–g
   and 3a–d, copied unchanged. It runs in Python's `Fraction`, with no threshold.
2. **The three properties.**
   - *Efficient*: self-play is all CC (efficient below the switch line u + v = 1), or w_CC = w_DD = 0 (efficient
     above it).
   - *Rival for T > S*: w_DC ≥ w_CD against every co-player. *Rival for T < S*: w_DC ≤ w_CD against every co-player.
   - *Stable*: the intersection of the 15 closed half-planes π(j, i) ≤ π(i, i), computed as an exact convex polygon.
     The result can be a region, a half-line or a single game.
3. **The co-players.** The sixteen memory-one co-players suffice. The co-player of a memory-one strategy controls a
   decision process on the four outcomes of the last round, and its best reply and best exploiter can be taken
   binary memory-one (the proposition of SI §2, read on four states). `--m2` confirms this directly. It repeats the
   stability and rivalry tests against all 65536 binary memory-two co-players, using the paper's census algorithm
   (state reduction in leading-order arithmetic, SI §6), vectorised in numpy with the census's tolerance of 1e-9.
   For every strategy the stability region and the rival sign come out the same.
4. **The class.** The partner region is the stability region intersected with the efficient side of the switch line. A
   strategy is a friendly rival on the quarter-plane where it is both efficient and a rival.

## Result

**All 80 cells agree with the printed table** (five columns for each of the sixteen strategies). This holds for the
copy of the table in the script and for SI Table 8 read with `--tex` from the LaTeX source of the paper (checked on
2026-09-24).

Three of the stability regions are single games, equilibria with ties:

| strategy | stability region |
|---|---|
| `DDCC` | the single game (u, v) = (0, 0) |
| `CCDD` | the single game (u, v) = (0, 0) |
| `DCDC` | the single game (u, v) = (1/2, −1/2) |

- At (0, 0), R = T = 1 and S = P = 0, so each player's payoff is the rate at which the other player cooperates.
  `CCDD` repeats its own last action and `DDCC` reverses it. Either way, in the limit it cooperates at rate 1/2
  whatever the co-player does. Every co-player therefore earns 1/2, which is what the strategy earns against itself.
- At (1/2, −1/2), R = 1, S = T = 1/2 and P = 0, so each player earns the average of the two cooperation rates.
  `DCDC` cooperates exactly when the co-player defected, so every co-player again earns 1/2.

The exact memory-two census, which the paper's stability regions are taken from, has the same three single-game equilibria
(dimension 0 at the same points; see `provenance/si-misc/`). Single games have measure zero and none of the 512
sampled games is one of them. With the eight strategies that have two-dimensional stability regions and the four with
half-lines (SI §10), tit-for-tat, which is stable at no game, and these three make up the sixteen.

Every checked statement of SI §10, and the memory-one statements of SI §5, holds (`output.txt`). These include:

- the quantised self-play (w_CD is exactly 1/4, or exactly ε(1−ε), at every ε);
- the three efficient strategies, and none above the switch line;
- the closed forms of rivalry, and tit-for-tat as the only fair strategy;
- rivalry = defensibility at memory one;
- friendly rivals 0/2/0/0 on W/S/E/N;
- win-stay, lose-shift as a partner on u ≤ 1, v ≤ 1, u + v < 1, and on the donation game exactly when b ≥ 2c;
- the eight two-dimensional stability regions, the four half-lines and the three single games;
- the eleven lines, 45 faces and twelve cases;
- at most five atoms per game, with 000 and 001 everywhere and 111 exactly on S.

## Inputs and outputs

- Inputs: none. Everything is computed from the definitions.
- Outputs: `sitable8.csv` and `m1_pairs.csv`, written next to the script, and the printed report.
