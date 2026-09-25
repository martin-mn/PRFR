# The families of friendly rivals: W by rows, N state by state, the largest pattern of S

SI §7 says: *“The notes deposited with the code read the family of W by rows, the eight positions shared by the
80 of N state by state, and the largest pattern of S.”* The three readings are below, each followed by a longer
version of the corresponding paragraph of SI §7, with the literature and the counts that the SI states more briefly.
The family descriptions themselves (the prime patterns and the minimal covers, among them the cover of 42 patterns of
S that the Methods and SI §7 say is “included in the computed output”) are in the folder `families/` of the
repository.

The passages are longer versions of passages condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX; section numbers are those of the SI (“§7” is SI §7). A genome is written
as 16 symbols, position j from the left holding the answer in the state j = 4 (most recent outcome) + (the outcome
before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 from the player's own side; a state written (X, Y) is X in the most
recent round and Y in the round before. `1` or C is cooperation. The game is (R, S, T, P) = (1, u, 1 + v, 0).

A pattern is 16 symbols `1`, `0` or `*`, a wildcard standing for either answer. The eight friendly rivals of W are
the pattern `111*000101*1*010`, integer codes 19079, 19087, 20103, 20111, 23175, 23183, 24199, 24207.

## W: the rules of the eight, read by rows

Read by rows: after a round of mutual cooperation, cooperate, whatever preceded it. After being exploited, defect, unless the round before was mutual defection, in which case cooperate to restart. After exploiting the co-player, cooperate again, unless the round before was mutual cooperation, in which case defect once more: an unprovoked defection of one's own is followed by a second, which is the anti-tit-for-tat move of *TFT-ATFT* [1], and the co-player's punishment is then accepted, since after mutual defection preceded by one's own exploitation of the co-player the answer is to cooperate. After mutual defection preceded by the co-player's exploitation, and after two rounds of mutual defection, defect, which is what makes *ALLD* unprofitable and the strategy a rival.

## W: the paragraph in full

**The wedge $W$: one family.** The eight friendly rivals of the Prisoner's Dilemma wedge are a single family with three wildcards, `111*000101*1*010` (SI Table 4a), with integer codes 19079, 19087, 20103, 20111, 23175, 23183, 24199 and 24207. In brief, the family cooperates after mutual cooperation, punishes exploitation, answers an unprovoked defection of its own with a second one, the anti-tit-for-tat move of *TFT-ATFT* [1], then accepts the punishment, and defects after prolonged mutual defection, which is what makes *ALLD* unprofitable and the strategy a rival; the rules read by rows, with the reason for each, are given above. The three wildcards sit at the states $(CC,DD)$, $(DC,DC)$ and $(DD,CC)$, positions 3, 10 and 12. The first and the last are reached in self-play only at second order in the error rate and cost nothing in the limit. The second decides distinguishability: the four members that defect at $(DC,DC)$, 19079, 19087, 23175 and 23183, keep exploiting an unconditional cooperator and are the four strategies that Yi, Baek and Choi single out by adding distinguishability to efficiency and defensibility [1], *TFT-ATFT* and its three variants, while the four that cooperate there return to mutual cooperation against *ALLC* and earn only $R$ against it; Murase and Baek count all eight as *TFT-ATFT* and its variants [2]. Two members, 20111 and 24207, which cooperate at $(DC,DC)$, are fair and belong to $S$ as well. The second defection at $(DC,CC)$ is not contrition in the classical sense. Contrite tit-for-tat [3, 4, 5] apologises at once for an unprovoked defection of its own and keeps track of the players' standing, which no bounded history of round outcomes records [6]; and contrition alone does not ensure cooperation [7]. This family does the reverse: it defects once more and only then accepts the co-player's punishment.

## N: the eight positions shared by all 80, state by state

All 80 agree at eight positions, `****000**1*1*010`: at $(CD,DC)$ they defect and at $(DC,CD)$ they cooperate, which is the alternation itself, each player answering the co-player's last move with the opposite of its own; after $(DD,DD)$ they defect, so that *ALLD* cannot exploit them; after $(DD,DC)$ they cooperate and after $(DD,CD)$ they defect, which restarts the alternation in the right phase after a double error; after $(DC,DD)$ they cooperate; and after $(CD,CC)$ and $(CD,CD)$, exploited after mutual cooperation or exploited twice, they defect. The two families of a pair differ only at the states $(CC,CD)$ and $(CC,DC)$, where one cooperates and the other defects: after a round of mutual cooperation that followed an asymmetric round the two players have to break the symmetry again, and they can do it in either order. Between the pairs the difference is the treatment of the states $(CD,DD)$, $(DC,CC)$ and $(DD,CC)$.

## N: the paragraph in full

**The wedge $N$: four families in two pairs.** The 80 alternating friendly rivals of the Snowdrift wedge are covered by exactly four prime patterns, two with five wildcards and two with four, and the description is unique (SI Table 4b): `*10*0000*1*1*010` and `*01*0000*1*1*010` with 32 members each, `*10*000*11*10010` and `*01*000*11*10010` with 16 each. The four overlap: the families of 32 and 16 on the left of the table share 8 strategies, as do the two on the right, so $32+32+16+16-16=80$. All 80 agree at eight positions, `****000**1*1*010`, which encode the alternation itself, its restart in the right phase after a double error, and defection after $(DD,DD)$, which keeps *ALLD* out. The two families of a pair differ only in how the two players break the symmetry again after a round of mutual cooperation that followed an asymmetric round, which they can do in either order; the pairs differ at three further states. The rules state by state are given above. The 80 cooperate at between 4 and 9 of their 16 states; none is a strategy with a name. Eight of them, the fair alternators, are friendly rivals in $E$ as well.

## S: the largest pattern, state by state

The reading of the largest pattern of S, `111*1***11*1****` (512 strategies), is part of the paragraph below:
“cooperate after mutual cooperation, cooperate after being exploited if the round before was mutual cooperation,
cooperate after exploiting the co-player unless the round before was DC, and do anything else at the remaining
states, in particular anything after mutual defection.”

## S: the paragraph in full

**The wedge $S$: no compact description.** The 1519 mutual cooperators that are rivals for $T<S$ have almost nothing in common: only two positions are fixed across the whole set, cooperation at $(CC,CC)$ and at $(CC,DC)$. The set has 56 prime patterns, with 4 to 9 wildcards each, and a family description needs 42 of them; it is not unique. One minimal description is included in the computed output; its 42 patterns name 4368 strategies with multiplicity, so the families overlap heavily. The largest single pattern, `111*1***11*1****`, names 512 strategies: cooperate after mutual cooperation, cooperate after being exploited if the round before was mutual cooperation, cooperate after exploiting the co-player unless the round before was $DC$, and do anything else at the remaining states, in particular anything after mutual defection. The set contains *ALLC* and tit-for-two-tats, and the two fair strategies 20111 and 24207, but not *WSLS* or *AON*$_2$, which go on defecting against a co-player that keeps cooperating after they have once defected on it, and for $T<S$ that is to be outperformed. The reason the class is so large and so loose is the one given in §2: when $T<S$ the unilateral cooperator earns more, so never defecting against a cooperator suffices for rivalry, and any error-correcting cooperator that does so qualifies. Restricting to the defensible reading leaves 1036 strategies, 33 prime patterns and a family description of 24.

## Checked

`checks/check_patterns.py` (output `checks/check_patterns.txt`) checks the arithmetic of the patterns quoted here: the
pattern of W names exactly the eight codes, its wildcards are at positions 3, 10 and 12, and the four members that
defect at (DC, DC) are 19079, 19087, 23175 and 23183; the four patterns of N name 32, 32, 16 and 16 strategies, the
pairs with the same first symbols share 8 each and no other pair overlaps, so the union is 80; all 80 match
`****000**1*1*010` and cooperate at between 4 and 9 of their 16 states; and `111*1***11*1****` names 512 strategies.
Against the census output in `families/` it checks the counts of the paragraphs: the cover of N is unique and has
four patterns, that of W one; S has 1519 members, only the positions (CC, CC) and (CC, DC) fixed, 56 prime patterns
with 4 to 9 wildcards, a minimal cover of 42 that is not unique and names 4368 strategies with multiplicity, among
them `111*1***11*1****`; the union of that cover contains *ALLC*, tit-for-two-tats, 20111 and 24207 but not *WSLS* or
*AON*$_2$; and the defensible reading of S has 1036 strategies, 33 prime patterns and a cover of 24. That the patterns
are the prime patterns and minimal covers of the families is the census's result (`families/`).

## References

1. Yi, S. D., Baek, S. K. & Choi, J.-K. Combination with anti-tit-for-tat remedies problems of tit-for-tat. *J. Theor. Biol.* **412**, 1–7 (2017).
2. Murase, Y. & Baek, S. K. Five rules for friendly rivalry in direct reciprocity. *Sci. Rep.* **10**, 16904 (2020).
3. Sugden, R. *The Economics of Rights, Co-operation and Welfare* (Blackwell, Oxford, 1986).
4. Boerlijst, M. C., Nowak, M. A. & Sigmund, K. The logic of contrition. *J. Theor. Biol.* **185**, 281–293 (1997).
5. Wu, J. & Axelrod, R. How to cope with noise in the iterated prisoner's dilemma. *J. Conflict Resolut.* **39**, 183–189 (1995).
6. Murase, Y. & Baek, S. K. Automata representation of successful strategies for social dilemmas. *Sci. Rep.* **10**, 13370 (2020).
7. Hilbe, C. Contrition does not ensure cooperation in the iterated prisoner's dilemma. *Int. J. Bifurcat. Chaos* **19**, 3877–3885 (2009).
