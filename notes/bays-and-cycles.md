# The atom 110 in its bays: the last forgivers and the cycles that exploit them

SI §8, on the atom `110` (the partners that are not rivals), says of the lines that bound its bays: *“Each of these
lines is the equilibrium condition of the last forgivers to survive it, beyond which a cycle exploiting their
forgiveness pays more than their self-play; each was read off the arrangement and checked by computing the best
co-player of the surviving strategy at ε = 10⁻⁶ on either side of the line, and the strategies and cycles are in the
notes deposited with the code.”* The bays are the regions where the atom is empty, so that the only partners are the
friendly rivals. Below: two passages that name the strategies and cycles, the strategies of every line, and the
check of every line.

The passages are longer versions of passages condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX; section numbers are those of the SI (“§7” is SI §7). A genome is written
as 16 symbols, position j from the left holding the answer in the state j = 4 (most recent outcome) + (the outcome
before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 from the player's own side; a state written (X, Y) is X in the most
recent round and Y in the round before. `1` or C is cooperation. The game is (R, S, T, P) = (1, u, 1 + v, 0).

Percentages “of the disk” are areas of the compactified disk of the main-text figures (**Methods**), not measures
over games.

## The Prisoner's Dilemma bay

In the Prisoner's Dilemma the bay is the set v > 2, u + 2v > 2, 3u + v < −1 (SI §8), that is T > 3R − 2P,
2T + S + P > 4R and 3S + T < 4P. The first, second and third line of the passage are v = 2, u + 2v = 2 and
3u + v = −1.

The first line is the equilibrium condition of mutual cooperators that resume cooperation after two rounds of mutual defection, such as `1001000000000001`, against which *ALLD* earns $T$, $P$, $P$ in a cycle of three rounds; the second is that of the partner `1110000100010010`, which a co-player exploits with a cycle of four rounds paying $T$, $T$, $S$, $P$; the third is that of alternators such as `0100000101100010`, exploited by a cycle of five rounds paying $S$, $P$, $T$, $T$, $P$ against the alternation payoff $(S+T)/2$.

The three strategies of the passage are 32777 (`1001000000000001`, the line v = 2), 18567 (`1110000100010010`,
u + 2v = 2) and 18050 (`0100000101100010`, 3u + v = −1).

## The Harmony bays

In the Harmony quadrant the bay is the part of $E$ with $u+3v<-1$, that is $S+3T<2R+2P$, 3.0% of the disk, where the last forgiving alternators are exploited, two of them by a cycle of five rounds paying $R$, $S$, $S$, $T$, $P$ and the third by play that mixes their alternation with a cycle of three rounds paying $S$, $P$, $R$; and the sliver of $S$ with $u>6$ and $5u+4v>6$, that is $S>6R-5P$ and $5S+4T+P>10R$, 0.3% of the disk, where the last forgiving mutual cooperators are exploited by play that gives the co-player $R$ four times, $S$ once and $P$ five times in ten rounds, and by play that gives it $R$ five times, $S$ five times, $T$ four times and $P$ once in fifteen, each a mixture of shorter cycles.

## The strategies and cycles of every line

The passage on the Harmony bays names the cycles but not the strategies. The strategies of all eight lines are from
the author's record of the check (2026-09-17): the last forgivers, one partner per line (three alternators share the
line u + 3v = −1). The exploitation is given as the exploiting co-player's payoffs round by round: a single cycle, or,
where the co-player's play in the limit ε → 0 divides its time between several cycles of the error-free pair, the
cycles with their weights and the resulting shares of R, S, T and P. On the side of the line where the partner is
stable the exploiting play pays no more than the partner's self-play, on the other side more.

| line (side where the partner is stable) | in payoffs | last forgiver | genome | exploiting play (the co-player's payoffs) | against |
|---|---|---:|---|---|---|
| v ≤ 2 | T ≤ 3R − 2P | 32777 | `CDDCDDDDDDDDDDDC` | T, P, P (*ALLD*) | R |
| u + 2v ≤ 2 | 2T + S + P ≤ 4R | 18567 | `CCCDDDDCDDDCDDCD` | T, T, S, P | R |
| 3u + v ≥ −1 | 3S + T ≥ 4P | 18050 | `DCDDDDDCDCCDDDCD` | S, P, T, T, P | (S + T)/2 |
| u + 3v ≥ −1 | S + 3T ≥ 2R + 2P | 11781, 15877 | `CDCDDDDDDCCCDCDD`, `CDCDDDDDDCCCCCDD` | R, S, S, T, P | (S + T)/2 |
| u + 3v ≥ −1 | S + 3T ≥ 2R + 2P | 24069 | `CDCDDDDDDCCCCDCD` | 5/8 of the time the alternation S, T, 3/8 the cycle S, P, R: R, S, T, P in the shares 1/8, 7/16, 5/16, 1/8 | (S + T)/2 |
| u ≤ 6 | S ≤ 6R − 5P | 46919 | `CCCDDDCDCCCDCCDC` | 4/5 of the time the cycle R, P, 1/5 the cycle S, P: R, S, T, P in the shares 2/5, 1/10, 0, 1/2 (R four times, S once, P five times in 10 rounds) | R |
| 5u + 4v ≤ 6 | 5S + 4T + P ≤ 10R | 4599 | `CCCDCCCCCDDDCDDD` | 8/15 of the time the cycle T, R, 2/15 the cycle R, P, 1/3 the round S repeated: R, S, T, P in the shares 1/3, 1/3, 4/15, 1/15 (R five times, S five times, T four times, P once in 15 rounds) | R |

Each line is where the exploiting play's average equals the partner's self-play: for 32777, T/3 = R; for 18567,
(2T + S + P)/4 = R; for 18050, (S + 2T + 2P)/5 = (S + T)/2; for 11781 and 15877, (R + 2S + T + P)/5 = (S + T)/2; for
24069, (2R + 7S + 5T + 2P)/16 = (S + T)/2; for 46919, (4R + S + 5P)/10 = R; for 4599, (5R + 5S + 4T + P)/15 = R.

## Checked (2026-09-24)

`checks/check_bays.py` (output `checks/check_bays.txt`) takes, for each strategy and its line, one game 0.02 from the
line on either side, and computes at ε = 10⁻⁶ the strategy's self-play and the payoff of its best co-player among all
65536 memory-two strategies (no co-player of any memory does better, SI §2). For the exploiting co-player it also
computes the limiting outcome frequencies as exact fractions, and from them its gain over the partner's self-play as a
linear function of (u, v); and it splits the limiting play into the cycles of the error-free pair and their weights.
Results:

- **All eight lines are confirmed.** On the side given in the table the best co-player earns no more than the
  partner's self-play, which equals $E_{\max}$ (the partner is efficient), so that the partner is stable there; on
  the other side it earns more, and its gain in the limit is a
  positive multiple of the line's own linear form, so the line is exactly where the partner stops being an
  equilibrium.
- **The exploiting play is the one in the table for all eight.** For 32777, 18567, 18050, 11781 and 15877 the best
  co-player's limiting play is a single cycle, the one of the table (up to where it is entered). For the other three
  it divides its time between cycles of the error-free pair. Every co-player that gets the same limiting shares as the
  best one (between 192 and 1920 of them, depending on the partner) plays the same cycles with the same weights.
  Against 24069 the best co-player, 65292 (`DDCCDDDDCCCCCCCC`), spends 5/8 of the time in the alternation and 3/8 in
  a cycle of three rounds that pays it S, P, R, so that it earns R, S, T and P in the shares 1/8, 7/16, 5/16 and 1/8;
  its gain over the self-play (S + T)/2 is (−1 − u − 3v)/16, against (−1 − u − 3v)/10 for the cycle R, S, S, T, P
  against 11781 and 15877: the same line. Against 46919 the best
  co-player, 61552 (`DDDDCCCDDDDDCCCC`), spends 4/5 of the time in the cycle R, P and 1/5 in the cycle S, P; against
  4599 the best co-player, 65520 (`DDDDCCCCCCCCCCCC`), spends 8/15 in the cycle T, R, 2/15 in the cycle R, P and 1/3
  in the round S repeated. Their shares are those of the passage's ten and fifteen rounds.
- **The bays in the arrangement.** In `data/arrangement` the atom `110` is empty on exactly the polygons of the
  three bays (5470 of the 27598 polygons of `m2_faces.csv`), and the two Harmony bays cover 3.02% and 0.29% of the area of the disk.
