# Longer punishment, and why it is not rivalry: the full comparison

The paragraph “Longer punishment, and why it is not rivalry” of SI §9 ends: *“… where 22663 is a partner; the
full comparison is in the notes deposited with the code.”* Below is the paragraph in full, with both exploiting
cycles, the second example (32907 near the origin) and the counts of co-players that finish ahead, and then the
numbers recomputed, among them the self-play payoffs of 22663 and 23175 at ε = 10⁻⁴ that SI §9 quotes in “Which
partners win”.

The passages are longer versions of passages condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX; section numbers are those of the SI (“§7” is SI §7). A genome is written
as 16 symbols, position j from the left holding the answer in the state j = 4 (most recent outcome) + (the outcome
before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 from the player's own side; a state written (X, Y) is X in the most
recent round and Y in the round before. `1` or C is cooperation. The game is (R, S, T, P) = (1, u, 1 + v, 0).

## The paragraph in full

**Longer punishment, and why it is not rivalry.** The partners that beat the eight in the Prisoner's Dilemma are not rivals, and the reason is instructive. Rivalry is a worst case over all 65536 co-players: no closed cycle of play may leave the co-player ahead. The eight achieve it by ending every punishment on the co-player's concession, the round in which the co-player cooperates while they still defect, which repays the round in which they were exploited, and by conceding themselves only after an unprovoked defection of their own (§7). The partner 22663, genome `1110000100011010`, differs from the friendly rival 23175, `1110000101011010`, at the single state $(DC,CD)$, position 9: the co-player has defected, been punished and conceded, and where the eight cooperate, 22663 defects once more. Against a co-player that goes on conceding it goes on defecting, and is never behind. But a co-player that answers the second punishment with a defection puts 22663 at the state $(DD,DC)$, two defections of its own followed by the co-player's, which the eight reach only after an unprovoked defection of their own and answer by conceding, at $(DD,DC)$ and again at $(CD,DD)$. A memory of two rounds cannot tell a second round of punishment from an error, and 22663, which has the same answers there, concedes twice. The co-player that defects, concedes once and then defects twice therefore runs 22663 through the cycle $CD$, $DC$, $DD$, $CD$, in which it pays $S$ twice for one $T$, whereas the same co-player runs 23175 through $DD$, $DD$, $DC$, $CD$, one $S$ for one $T$. That co-player earns $(2T+S+P)/4=0.84<R$ at $(u,v)=(-3.21,2.29)$, so 22663 remains a Nash equilibrium: a partner and not a rival. Near the origin the partners that win do the same thing on a different cue. At $(-0.38,0.54)$ the most abundant partner at $N=1000$, 32907, genome `1101000100000001`, answers any defection with two rounds of mutual defection and then cooperates, at $(DD,DD)$, where the eight defect, and again at $(CD,DD)$; *ALLD* supplies that cue for nothing and is met with cooperation two rounds in four, earning $T/2=0.77$ against −0.19 for 32907, still less than $R$. In each case the non-rival returns to cooperation on a cue that the co-player can produce more cheaply than the concession the eight demand: 9253 co-players finish ahead of 32907 and 8759 ahead of 22663, none of them earning $R$, while none finishes ahead of a friendly rival. What such partners gain is absolute payoff: they defect more against strategies that defect, and the mutant cloud consists mostly of such strategies. Rivalry constrains relative payoff in every encounter, and its price in the Prisoner's Dilemma is the round of cooperation that the eight extend to every co-player that has conceded once; in the wedge $S$, where the exploited player earns more than the exploiter, cooperating against a defector costs nothing, and there the friendly rivals, which never defect on a cooperator, are the ones ahead against the cloud (SI §9, “Which partners win”).

## Recomputed (2026-09-24)

`checks/check_longer_punishment.py` (output `checks/check_longer_punishment.txt`; all checks pass). Where T > S a
co-player finishes ahead of σ exactly when w_CD > w_DC in σ's view in the limit ε → 0, so the counts do not depend on
the game; the limit is read at ε = 10⁻⁷.

- 22663 = `1110000100011010` and 23175 = `1110000101011010` differ only at position 9, the state (DC, CD);
  32907 = `1101000100000001`.
- No co-player finishes ahead of the friendly rival 23175; **8759** finish ahead of 22663 and **9253** ahead of 32907.
- At (u, v) = (−3.21, 2.29), 264 co-players ahead of 22663 earn (2T + S + P)/4 = 0.8425 against it (for example 34176,
  `DDDDDDDCCDCDDDDC`); 22663 is a Nash equilibrium there (its best co-player earns its self-play R), and none of the
  8759 co-players ahead of it earns R (the best of them earns 0.9370).
- At (u, v) = (−0.38, 0.54), *ALLD* earns 0.7700 = T/2 against 32907, which earns −0.1900 = S/2; 32907 is a Nash
  equilibrium there, and none of the 9253 co-players ahead of it earns R (the best of them 0.8467). At the sampled
  game nearest to this point, (−0.377, 0.536), 32907 is a partner and the most abundant strategy of the
  large-population run (`data/runs/m2_N1000.csv`, column `top`).
- At ε = 10⁻⁴ and (u, v) = (−3.21, 2.29) the self-play of 22663 is R − 7.59ε and that of the friendly rival 23175 is
  R − 9.50ε: the “R − 7.6ε against R − 9.5ε” of the paragraph “Which partners win” are 22663's and 23175's, in that
  order.
