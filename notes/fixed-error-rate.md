# Why the limit, and not a fixed error rate: the worked examples at ε = 0.01

The paragraph “Why the limit, and not a fixed error rate” of SI §1 ends: *“Worked examples at ε = 0.01 are in the
notes deposited with the code.”* Below are a longer version of that paragraph, which gives the examples, the case
T < S, the examples recomputed, and the argument that below the switch line only *ALLC* is efficient at a fixed ε.

The passages are longer versions of passages condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX; section numbers are those of the SI (“§7” is SI §7). A genome is written
as 16 symbols, position j from the left holding the answer in the state j = 4 (most recent outcome) + (the outcome
before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 from the player's own side; a state written (X, Y) is X in the most
recent round and Y in the round before. `1` or C is cooperation. The game is (R, S, T, P) = (1, u, 1 + v, 0).

## The paragraph in full

**Why the limit, and not a fixed error rate.** The maps of the main text are run at $\epsilon=10^{-4}$, and one may ask why they are organised by classes defined in the limit rather than by the same classes read at that error rate. The reason is a matter of scales. At a fixed $\epsilon$ the payoff matrix is $A(\epsilon)=A_0+\epsilon A_1+\epsilon^2A_2+\dots$, where $A_0$ is the limit matrix. The gaps in $A_0$ are of order one: earning $R$ with a cooperator against earning $S$ or $P$. The gaps in $A_1$ are of order $\epsilon$: the cost of recovering from an error, one exploited round per error of one's own. A payoff difference $\Delta$ decides the fate of a mutant in a population of size $N$ under selection strength $\beta$ only when $N\beta\Delta$ is of order one, so at $\epsilon=10^{-4}$ the small population of SI Figure 4 ($N\beta=300$) resolves $A_0$ alone, the large population of main text Figure 4 ($N\beta=10^{5}$) resolves $A_0$ and part of $A_1$, and no run resolves the tails. The limit classes are the sign pattern of $A_0$, with ties read as ties: they cut the matrix at its order-one gaps, which is where the population's fate is decided, and they are the same for every small $\epsilon$ and piecewise constant over the plane of games, because they are properties of a strategy's rules along the paths that play actually follows, the cooperative path and the recoveries from single errors. The same classes read exactly at a fixed $\epsilon$ cut at threshold zero, so that each membership is decided by whichever order of $\epsilon$ finally breaks a tie, and they degenerate. At $\epsilon=0.01$, for instance, where $T>S$ the only strategy that is never behind *ALLD* is *ALLD* itself, because at every state at which a strategy intends to cooperate it nets $(\epsilon^2-(1-\epsilon)^2)(T-S)<0$ per visit against *ALLD* and every state is visited; tit-for-tat is behind by $0.98\,\epsilon\,(T-S)$ per round and the eight friendly rivals by about $1.9\,\epsilon\,(T-S)$. Below the switch line the only efficient strategy at a fixed $\epsilon$ is *ALLC*, since every intended defection at a visited state adds error-induced losses, and above the switch line no strategy is efficient at $\epsilon=0.01$: at $(u,v)=(-0.5,2)$, for instance, the pair *ALLC*–*ALLD* alone averages more than the best self-play, that of an alternator, so the joint optimum lies off the diagonal, the situation of the one-shot game in §2 returning at a positive error rate. Where $T>S$ there is therefore no friendly rival at any fixed $\epsilon$, since *ALLD* is not efficient, and the strict equilibria, which are a fixed-$\epsilon$ class, carry at most 4% and 19% of the population at $N=100$ and $N=1000$ (§9). Any threshold between $\epsilon$ and one on the payoff differences reproduces the limit classes, since the order-$\epsilon$ gaps lie below it and the order-one gaps above; the limit is the threshold-free name for that window. The ties of the limit are information rather than a defect: the 7639 mutual cooperators tie at $R$, and that tie is the neutral plateau over which drift and numbers act, and over which selection acts only through $A_1$ when $N\beta\epsilon$ is large. Two qualifications. The argument holds while $\epsilon$ is small against the game's own gaps, $\epsilon(T-S)\ll R-P$. And questions that are themselves about the order-$\epsilon$ structure, which partner prevails on a plateau or which equilibria are strict, need the graded quantities at a fixed $\epsilon$, with thresholds in units of $\epsilon$.

## Where T < S

Where T < S a player that cooperates while its co-player defects is ahead, so the degeneration of the fixed-ε classes
described above is one-sided. On the wedge S (T < S, 2R > T + S) *ALLC* is a friendly rival at every ε < ½. It is a
rival: in every round it plays C with probability 1 − ε, whatever has happened, and if the co-player plays D in that
round with probability q, then q ≥ ε and *ALLC*'s payoff minus the co-player's is (S − T)(q − ε) ≥ 0. It is
efficient, since the wedge S lies below the switch line (see the last section of this note). By the theorem it is
then also a Nash equilibrium, a partner, at every fixed ε; the same holds for the discounted game (`discounting.md`,
claim 2).

## The examples, recomputed

`checks/check_fixed_eps.py` recomputes them from the 16-state chain of each pair at ε = 0.01 (output in
`checks/check_fixed_eps.txt`; all checks pass):

- Where T > S a strategy's payoff minus that of *ALLD* is (S − T)(w_CD − w_DC) per round, so its deficit is
  (w_CD − w_DC)/ε in units of ε(T − S). Tit-for-tat: **0.9800**, which is (1 − 2ε): tit-for-tat intends to cooperate
  exactly after an error of *ALLD*, which happens with probability ε, and each such cooperation costs (1 − 2ε)(T − S).
  The eight friendly rivals of the wedge W: **1.922 to 1.940** (“about 1.9”).
- Every one of the other 65535 strategies is strictly behind *ALLD* at ε = 0.01. The smallest deficit is that of
  *Grim* (code 1), 9.9 × 10⁻⁷ in these units: it cooperates only after two rounds of mutual cooperation, which against
  *ALLD* take four errors.
- At (u, v) = (−0.5, 2), above the switch line, the pair *ALLC*–*ALLD* averages **1.23515** per player and round; the
  best self-play of all 65536 strategies is **1.23076**, that of 46299 (`CCDCCDCCDDCDCCDC`), an alternator
  (w_CD + w_DC = 0.962); (S + T)/2 = 1.25. So no strategy is efficient at this game at ε = 0.01: the joint optimum is
  off the diagonal.
- Below the switch line, at the donation game (u, v) = (−1, 1), *ALLC*'s self-play is higher than that of any other of
  the 65536 strategies (the runner-up, 32767, differs from *ALLC* only after two rounds of mutual defection). That
  *ALLC* is the only efficient strategy there also needs the comparison with pairs of different strategies; it follows
  from the argument below.

## Why only ALLC is efficient below the switch line at a fixed ε

(Written out for these notes; it makes the paragraph's reason, “every intended defection at a visited state adds
error-induced losses”, exact.) Given the history, the two moves of a round are independent, each a cooperation with a
probability in [ε, 1 − ε] (for ε < 1/2). If a and b are these probabilities, the pair's average payoff in that round is
f(a, b) = R ab + ½(S + T)[a(1 − b) + (1 − a)b] + P(1 − a)(1 − b), which is bilinear, so on [ε, 1 − ε]² it is largest at
a corner. Below the switch line, R > (S + T)/2 and R > P, so ∂f/∂b at a = 1 − ε,
(1 − ε)(R − ½(S + T)) + ε(½(S + T) − P), is positive, and f(1 − ε, 1 − ε) − f(ε, ε) = (1 − 2ε)(R − P) > 0: the
largest corner is (1 − ε, 1 − ε), both players intending to cooperate, and every other corner is strictly smaller. Hence
no pair of strategies averages more than *ALLC*'s self-play, which is f(1 − ε, 1 − ε) in every round, so *ALLC* is
efficient; and a strategy that intends to defect at some state, which at ε > 0 is visited with positive frequency,
falls strictly short of it. The same argument holds for the discounted payoff (`discounting.md`).
