# Memory one: the atoms strategy by strategy

SI §10, “The sixteen strategies”, ends: *“SI Table 8 thus gives the atom of every strategy at every game off the
two lines; the reading of main text Figure 2a–g atom by atom is in the notes deposited with the code.”* That reading
is below, followed by its check against the exact memory-one arrangement.

The passage is a longer version of a passage condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX. A memory-one strategy is written by its answers after the outcomes CC,
CD, DC, DD of the last round, own move first: *ALLD* = DDDD, *Grim* = CDDD, tit-for-tat = CDCD, *WSLS* (win-stay,
lose-shift) = CDDC, *ALLC* = CCCC. The game is (R, S, T, P) = (1, u, 1 + v, 0), so that T > R is v > 0, S > R is
u > 1, T > S is u < 1 + v, 2S < R + P is u < ½, T < 2R − P is v < 1, the switch line S + T = 2R is u + v = 1, and the
unit square is 0 ≤ u, v ≤ 1. The reading is that of the 45 open faces of the memory-one arrangement, off the three
half-lines, on each of which one further strategy is stable with ties (SI §10).

Percentages “of the disk” are areas of the compactified disk of the main-text figures (**Methods**), not measures
over games.

## The atoms strategy by strategy (main text Figure 2a–g)

**The atoms strategy by strategy.** The counts of main text Figure 2a–g are constant on the 45 faces of the memory-one arrangement and small enough to be named. Between six and twelve of the sixteen strategies have none of the three properties (main text Figure 2a); tit-for-tat is the only one that never belongs to this atom, because it is competitive at every game. The efficient strategies that are neither stable nor competitive, `100`, are the mutual cooperators *ALLC* and $CCCD$, the strategy that cooperates unless both players defected, wherever $T>R$ below the switch line, where an unconditional defector exploits them, joined by *WSLS* where $T>2R-P$, and *WSLS* alone in the Harmony games with $S>R$; the atom is empty above the switch line, where no memory-one strategy is efficient, and where $T\le R$ and $S\le R$, where all three are stable (Figure 2b). The stable strategies that are neither efficient nor competitive, `010`, are up to five of the sixteen in the Stag Hunt, *ALLD*, *Grim*, $DCCD$, $DDDC$ and $DCCC$ on parts of it and *ALLD* among them wherever $T<S$; $DDDC$ also in the Harmony games with $2S<R+P$; and *WSLS* alone on the part of the unit square above the switch line, where it is stable but cannot alternate (Figure 2c). The atom is empty on 71% of the disk. Between two and four strategies are competitive only, `001`, tit-for-tat always among them (Figure 2d). The partners that are not competitive, `110`, are all three mutual cooperators where $T\le R$, $S\le R$ and $T>S$, and *WSLS* alone in the Prisoner's Dilemma with $T<2R-P$, in the Snowdrift games of the unit square below the switch line, and on the wedge $S$ with $S<R$ (Figure 2e). The stable rivals that are not efficient, `011`, are *ALLD* and *Grim* in the Prisoner's Dilemma and in the Stag Hunt with $T>S$, *Grim* only where $2S+R\le3P$, and *ALLC* and $CCCD$ in the Harmony games above the switch line, where they are stable and, since $T<S$, competitive, but where nothing that fails to alternate is efficient (Figure 2f). The friendly rivals, `111`, are *ALLC* and $CCCD$ on the wedge $S$ and nobody elsewhere (Figure 2g).

## Checked (2026-09-24)

`checks/check_memory_one_atoms.py` (output `checks/check_memory_one_atoms.txt`; all checks pass) tests every sentence
of the passage against `data/arrangement/m1_faces.csv`, the exact atom of each of the 16 strategies on each of the 45
faces (computed in rational arithmetic by `data/arrangement/m1atoms.py`). Each sentence that names the members of an
atom is read as a rule giving, for a game (u, v), the set of strategies in that atom, and the rule must give exactly
the strategies of the table on every face; the counts, the ranges and the share of the disk on which `010` is empty
are recomputed from the same table.
