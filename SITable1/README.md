# SI Table 1: classical strategies of the repeated Prisoner's Dilemma and their properties

SI Table 1 is a conceptual table. It lists ten classical strategies as witnesses: examples showing that no
implication among efficient, stable and competitive holds other than the theorem. The paper does not compute these
entries; it argues them in its text. This folder therefore has two parts:

- **Where each entry is argued in the paper** (the table below).
- **A check of every row.** `sitable1.py` checks each row exactly, at four donation games, in the limit of rare
  errors (and without errors for the one row that says so). It then compares the results with the printed table.

## Reproducing

```
python3 sitable1.py                          # about 3 s; standard library only
python3 sitable1.py --tex ../path/to/ms.tex  # compare with SI Table 1 as typeset in a LaTeX file
```

`output.txt` is its output. The script exits with a non-zero status if any case differs from the printed table.

**Result: all 53 cases agree with the printed table.**

## What is checked

**Games.** The donation games (R, S, T, P) = (b − c, −c, b, 0), with c = 1 and b = 3/2, 2, 3 and 5. At these games
E_max = R.

**Strategies.** All ten strategies are memory one, written by their probabilities of cooperating after CC, CD, DC
and DD. Where a row names a family, the check uses representatives, and prints their parameters:

- *Generous tit-for-tat*, (1, q, 1, q), at q = q\*/100, q\*/2 and 99q\*/100, with q\* = 1 − c/b.
- *Generous zero-determinant (ZD) strategies*, with π_X − R = χ(π_Y − R), at χ = 2 and 3.
- *Extortionate ZD strategies*, with π_X − P = χ(π_Y − P), at χ = 2 and 3.
- *The equaliser*, which fixes the co-player's payoff at π0 = (b − c)/2.

For each ZD strategy the script first confirms that its defining relation holds in the limit against all 16
co-players.

**Win-stay, lose-shift** is checked at b = 3, 5 and 21/10 for the row b > 2c, and at b = 3/2 and 19/10 for b < 2c.

**Boundaries.**

- Generous tit-for-tat is stable, with a tie, at q = q\*, and is not stable just above it. So the threshold q\* of the
  caption is 1 − c/b at the donation game.
- At q = 0 (tit-for-tat) it is not efficient.
- Win-stay, lose-shift at b = 2c is stable with a tie: ALLD earns (T + P)/2 = R against it.

**Method.** For each pair, the stationary distribution of the four-state chain with errors (rate ε) is computed
exactly by the Markov chain tree theorem, and the limit ε → 0 is taken from the lowest-order coefficients. This is
the pair computation of `../SITable8/sitable8.py`, extended to probabilistic answers.

The co-players are the sixteen binary memory-one strategies. Against a memory-one strategy, stochastic or not, the
co-player controls a decision process on the four outcomes of the last round. Its best reply and its best exploiter
over all strategies are therefore deterministic and stationary: binary memory one (the proposition of SI §2, read on
four states). The row "tit-for-tat, no errors, cooperative start" is checked at ε = 0: tit-for-tat opens with C, and
it plays the 16 co-players with either first move, 32 in all.

## Where each entry is argued

Section numbers and headings are those of the paper's SI as of 2026-09-24:

- §1 The setting
- §2 Definitions and the theorem
- §3 What does not follow, and the tie clause
- §10 Memory one, for contrast

"Main text" is the Results paragraph beginning "That no other implication among the three properties holds", unless
another paragraph is named.

| row | efficient | stable | competitive | class |
|---|---|---|---|---|
| ALLD | not efficient in any game with R > P: §2, *Efficient strategies* | stable at the donation game (stable on u ≤ 0, SI Table 8; donation games have u < 0) | a rival where T > S, since it defects after CD and DD: §10, *Rivalry in closed form*; main text, paragraph *Repeated games* | rival: main text ("A competitive and stable strategy need not be efficient: ALLD"); §3, last sentence |
| ALLC | self-play is all CC, which is efficient below the switch line: §2, *Efficient strategies* | not stable: ALLD earns T > R against it (SI Table 8: ALLC is stable only on v ≤ 0, and donation games have v > 0) | no; submissive where T > S: §2, *Friendly rivals* | submissive: §2, *Friendly rivals* |
| tit-for-tat, no errors, cooperative start | two tit-for-tat players that start with C cooperate for ever: §1, *Repeated play with rare errors* | follows from the theorem (§2), because it is efficient and a rival; §1, *Discounting*, uses the same case, with a slack, at every δ < 1 | fair, so never outperformed: §2, *Rivals* | friendly rival. Not argued in a sentence of its own. It follows from the three cells to the left and the theorem, and the Introduction names TFT-ATFT as the first friendly rival *with* errors |
| tit-for-tat, rare errors | earns (R+S+T+P)/4 in self-play: §3; it does not repair an error: §2, *Efficient strategies* | ALLC earns R against it: §3; main text ("unconditional cooperators earn more against them") | fair: §2, *Rivals*; §10 (the only fair strategy) | rival, "this rival is invaded": §3 |
| win-stay, lose-shift, b > 2c | it repairs errors: §2, *Efficient strategies* | stable when T + P < 2R, i.e. b > 2c: caption of SI Table 1; §10 ("exactly when b ≥ 2c, with a tie at b = 2c") | ALLD outperforms it: §3; main text; §10 (a rival in neither direction) | partner: main text; §10 (partner on u ≤ 1, v ≤ 1, u + v < 1) |
| win-stay, lose-shift, b < 2c | as above | not stable when b < 2c: caption; §10 | as above | efficient only |
| generous tit-for-tat, 0 < q < q\* | it repairs errors: §2, *Efficient strategies* | partner for 0 < q < q\*, the threshold of Hilbe, Chatterjee and Nowak (2018): caption | not competitive: main text, paragraph *Repeated games*, which lists ALLC, generous tit-for-tat and WSLS as not competitive | partner, "stable because they punish enough": main text |
| generous zero-determinant | efficient | stable | not competitive | partner: main text ("GTFT and the generous zero-determinant strategies are partners of the same kind", citing Stewart & Plotkin 2013) |
| extortionate zero-determinant | not efficient | ALLC earns more against it than it earns against itself, and can invade: main text | never outperformed: main text; main text, paragraph *Repeated games* ("the extortionate strategies are competitive") | rival: main text |
| equaliser zero-determinant | not efficient (its self-play payoff π0 is below R) | stable with ties, since every co-player earns π0: §3 | outperformed by ALLD: §3 | stable only: §3, the witnesses of atom 010 |

For the generous ZD row the paper states only the class (in the main text), not each property separately. The
check confirms all three properties for the representatives listed above.

## Files

| file | what it is |
|---|---|
| `sitable1.py` | the checks and the comparison |
| `output.txt` | the printed output of `sitable1.py` |

- Inputs: none.
- Outputs: the printed report only.
