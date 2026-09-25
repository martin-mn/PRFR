# data/strict — strict Nash equilibria at ε = 10⁻⁴ and the population on them

This folder holds the data of SI Figures 6 and 7 and of the Methods paragraph "Strict equilibria". For each of the 512
sampled games (`../games`) and both strategy spaces it gives:

- which strategies are strict Nash equilibria at the error rate of the runs, ε = 10⁻⁴;
- which of them are efficient in the limit ε → 0;
- how much of the population sits on them in the two Wright–Fisher runs.

| file | rows | what |
|---|---:|---|
| `m1_games.csv` | 512 | memory one, one row per game: the number of strict (and of weak) equilibria among the 16 strategies, the sets as 16-bit masks, the strategies efficient and those stable in the limit ε → 0 as masks (`eff_mask`; `nash_limit_mask`, which holds stability), the shares of the population |
| `m1_sets.csv` | 1263 | memory one, one row per (game, strict equilibrium): the strategy, whether it is efficient, and its count of individual-generations in each run |
| `m2_games.csv` | 512 | memory two, one row per game: the number of strict (and weak) equilibria among the 65536 strategies, of efficient ones, of efficient strategies, the count found by the double-precision brute force, the shares |
| `m2_sets.csv` | 65547 | memory two, one row per (game, strict equilibrium): the strategy, whether it is efficient, a mutual cooperator or an alternator, whether the double-precision scan also found it, and its abundance in each run |
| `m2_float64_check.csv` | 160 | memory two, the (game, strategy) pairs at which the double-precision brute force and the exact one-flip test disagree, with both margins |
| `check_strict.py` | | reads the tables, checks their consistency, and prints every number the paper quotes about them (2 s) |
| `recompute_sets.py` | | recomputes the strict sets of both memories from the games alone, independently, and compares them with the tables (20 s) |

Every table starts with `#` comment lines that describe each column, followed by a header line and comma-separated
values. Floats are written with Python's `repr`, which reads back as the identical double. `common.tables.read_table`
reads them.

## Conventions

- **Games.** `ipt` 0..511, (R, S, T, P) = (1, u, 1 + v, 0), as in `../games/games.csv`. Every table repeats `u` and
  `v`, and the checks assert that they are equal to the game table.
- **Runs.** `F2` is the run at N = 100, β = 3, μ = 10⁻⁴ and `F1` the run at N = 1000, β = 100, μ = 10⁻², both at
  ε = 10⁻⁴ (the runs of the paper's SI Figure 4 and main Figure 4). These are the names of the original figure
  loader, `../runs/wfdata.py`. The same runs are `m1_N100`, `m1_N1000`, `m2_N100` and `m2_N1000` in `../runs/`, the
  memory-two ones `dw2` and `dw1` in the simulator (regenerated as `f2` and `f1`, `f2_e4` and `f1_e4` in
  `../robustness/`); the table "The same runs appear under different names" in the section on the simulator of the
  top-level `README.md` lists every name. `share_F2` is panel b or e of SI Figures 6 and 7, and `share_F1` is panel c
  or f.
- **Memory-one strategy** `s` = 0..15: bit j is 1 if the strategy cooperates after outcome j = CC, CD, DC, DD, with
  its own action first. So ALLD is 0, Grim (CDDD) 1, TFT (CDCD) 5, WSLS (CDDC) 9 and ALLC 15. `strategy` spells the four
  answers.
- **Memory-two strategy** `s` = 0..65535: bit k is 1 if the strategy intends C in state k = 4 × (the most recent
  outcome) + (the outcome before), outcomes numbered as above. This is the code of the companion repository
  github.com/martin-mn/MapBinM2. ALLD is 0 and ALLC 65535, and the memory-one strategy with answers b_j is
  15 × Σ_j b_j 16^j.
- **Strict** at ε = 10⁻⁴ means π(s, s) > π(t, s) for every other strategy t of the space: the 15 others at memory one,
  the 65535 others at memory two. **Weak** means ≥. At memory two, at ε > 0, the sixteen one-flip deviations decide
  both tests against all 65535. Weak and strict equilibria coincide at all 512 games for both memories, so
  `n_weak = n_strict` everywhere.
- **Efficient** is the paper's limit notion ε → 0. Below the switch line u + v < 1 it means a mutual cooperator (7639
  memory-two strategies; CCCC, CDDC and CCCD at memory one); above it, an alternator (3072 at memory two, none at
  memory one). No game lies on the switch line.
- **Shares.** At memory one the share is the count on the strategies divided by `ntot`, and at memory two the sum of
  the abundances `pi`. The per-game shares are exactly the sums of the per-strategy rows. For memory one the sum of
  `c` over a game's rows divided by `ntot` gives the share bit for bit. For memory two `numpy.sum` of `pi` over a game's
  rows, in file order, gives it bit for bit. `check_strict.py` asserts both.

## The numbers they give

`python3 check_strict.py` recomputes these from the tables and asserts each one:

- **Memory two.**
  - Strict equilibria per game: 0–645, median 15; 65547 (game, strategy) pairs in all.
  - The 111 games with none are all in the Snowdrift quadrant, which has 127 games.
  - The 16 Snowdrift games with strict equilibria all lie within |(u, v)| < 1.96 and have 4–16 each, 127 in all. 112
    of these are mutual cooperators. The other 15 lie at four games near the origin below the switch line (ipt 2, 7,
    10, 15). They are neither mutual cooperators nor alternators: in the limit their self-play is mutual cooperation
    half or two thirds of the time and mutual defection otherwise.
  - No strict equilibrium is an alternator.
  - The share of the population on strict equilibria is at most 0.0400 at N = 100 and 0.1933 at N = 1000, with
    medians 0.0011 and 0.0034.
  - Efficient strict equilibria: 0–128 per game, none above the switch line. In the Prisoner's Dilemma they occur only
    at v < 2, that is T < 3R − 2P.
- **Memory one.**
  - Strict equilibria per game: 0–7. There are seven strategies: ALLD exactly where u < 0 (257 games), ALLC exactly
    where v < 0 (256), WSLS exactly where u < 1 and v < 1 (199), and Grim, DDDC, DCCC and DCCD at 224, 143, 113 and 71
    games.
  - Seven at once at 71 Stag Hunt games. None at the 119 Snowdrift games outside the unit square.
  - CCCD is stable in the limit exactly where v ≤ 0, and a strict equilibrium nowhere.
  - The share on strict equilibria exceeds one half at 258 and 246 games (N = 100 and N = 1000).
  - The share on the efficient ones exceeds one half at 117 and 163 games. These are ALLC where v < 0 below the switch
    line (214 games) and WSLS where it is strict below the switch line (196).
- **The double-precision brute force** (`m2_float64_check.csv`).
  - It compares every resident against all 65535 alternatives and agrees with the exact test at all but 160 of the
    512 × 65536 pairs, in 102 games. At all 160 the exact test finds a strict equilibrium and the brute force does not.
  - The 160 are ALLC (101 pairs) and three other mutual cooperators, 63359 (50), 63903 (8) and 61449 (1). They occur
    in Stag Hunt (107) and Harmony (53) games.
  - Their true margins, in quadruple precision, are 1.5 × 10⁻¹⁸ to 2.9 × 10⁻¹⁶. The double subtraction gave 0,
    −1.1 × 10⁻¹⁶ or −2.2 × 10⁻¹⁶.
  - They hold at most 0.0013 (N = 100) and 0.022 (N = 1000) of the population at a game, with medians over the 102
    games of 4 × 10⁻⁵ and 7 × 10⁻⁶.
  - The largest shares are the same with either set. The median share at N = 1000 over the 512 games would be 0.00037
    with the double-precision sets instead of 0.0034.

## Recomputing the sets

`python3 recompute_sets.py` needs only `../games/games.csv`. For memory one it solves all 16 × 16 pair chains at
ε = 1/10000 in exact rational arithmetic and decides strictness among the 16. It then embeds the 16 in memory two and
tests them against all 65536 memory-two strategies, again exactly.

For memory two it decides the sign of each of the 16 × 65536 one-flip gains at each game from the bias of the
resident's self-play chain, in double precision. This avoids the subtraction of two payoffs of order one that limits a
direct comparison. Any sign it cannot certify is referred to exact rational arithmetic (the docstring explains how).
On these 512 games none had to be referred: the smallest relative size of a sign-deciding quantity is 5.3 × 10⁻⁹. 32
further verdicts, among them the pairs of `m2_float64_check.csv`, are decided exactly as a check. The script also
prints the self-play, near the limit, of the 16 strict equilibria of the Snowdrift games: 10 cooperate throughout, 4
are half CC and half DD, and 2 are two thirds CC and one third DD.

The result agrees with `m1_sets.csv`, `m1_games.csv` and `m2_sets.csv` at every one of the 512 × 16 and 512 × 65536
(game, strategy) pairs. The shares cannot be recomputed from the repository: they need the full abundance vectors of
the runs (65536 numbers per game), which are not deposited. They can be regenerated bit for bit from the seeds with
the kits in `../../simulator/kits/` (see `../runs/README.md`).

## Provenance

`../../provenance/strict/reduce_strict.py` made the tables from the author's private full outputs. It copied the
per-game numbers from the objects the original figure scripts used, so SI Figures 6 and 7 come out identical. It
derived the per-strategy rows afresh from the exact one-flip test, the exact limit census and the full abundance
vectors, and checked them against those numbers: counts exactly, shares to the last bit.

The memory-two strict sets were decided on the exact integer half-planes of the sixteen one-flip deviations, built by
`exact/exactcoef.py` of github.com/martin-mn/MapBinM2. Efficiency comes from the same repository's exact limit census.
The memory-one sets were decided in rational arithmetic. The runs' per-strategy counts at memory one also appear, for
all 16 strategies, in `../runs/m1_N100_counts.csv` and `m1_N1000_counts.csv`.

Size of this folder: 4.3 MB, of which `m2_sets.csv` is 4.1 MB.
