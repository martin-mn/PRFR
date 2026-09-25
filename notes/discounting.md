# Discounting: the full argument

The paragraph “Discounting” of SI §1 ends: *“The full argument is in the notes deposited with the code.”* This note
gives a longer version of the paragraph, the argument written out in full, and a numerical check of the bound it
rests on.

The passages are longer versions of passages condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX; section numbers are those of the SI (“§7” is SI §7). A genome is written
as 16 symbols, position j from the left holding the answer in the state j = 4 (most recent outcome) + (the outcome
before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 from the player's own side; a state written (X, Y) is X in the most
recent round and Y in the round before. `1` or C is cooperation. The game is (R, S, T, P) = (1, u, 1 + v, 0).

## The paragraph in full

**Discounting.** The same considerations apply when the future is discounted, and one of them becomes a theorem. Let the payoff be $\pi_\delta(\sigma,\tau)=(1-\delta)\sum_{t\ge1}\delta^{t-1}\pi_t$ for a discount factor $\delta<1$, the game started from a given first move. The definitions of §2 apply verbatim to the matrix $\pi_\delta$, and so does the theorem of §2, since its proof uses only the entries of the matrix. But where $T>S$ its hypothesis cannot be met: at any $\delta<1$ and any $0\le\epsilon<\tfrac12$, no strategy is both efficient and a rival. Without errors, two copies of a strategy play symmetrically, so before their first cooperation the history consists of mutual defections only, and *ALLD* produces exactly that history. A strategy whose self-play ever cooperates therefore cooperates, at the same round $t$, against *ALLD*, earning $S$ while *ALLD* earns $T$, and afterwards it can never earn $T$ against *ALLD*; its discounted deficit is at least $(1-\delta)\delta^{t-1}(T-S)>0$, and for an efficient strategy, which cooperates in round one, at least $(1-\delta)(T-S)$. Tit-for-tat, *Grim* and the eight friendly rivals of the wedge $W$, started cooperatively, attain this bound exactly. Where $T<S$ and $2R>T+S$, the wedge $S$, the argument reverses: cooperating against a defector puts a player ahead, and *ALLC* is a friendly rival at every $\delta$ and every $\epsilon<\tfrac12$. Rivalry is thus a limit statement twice over. The first exploitation that *ALLD* inflicts on a cooperator is worth $(1-\delta)(T-S)$ under discounting and $\epsilon(T-S)$ per round at a positive error rate, and the limits $\delta\to1$ and $\epsilon\to0$ are what make it worth nothing; Hilbe, Chatterjee and Nowak make the same observation for reactive strategies [1]. The theorem recovers its content with a slack. Call $\sigma$ unbeatable up to $s$ if $\pi(\sigma,\tau)\ge\pi(\tau,\sigma)-s$ for every $\tau$. An efficient strategy that is unbeatable up to $s$ is a Nash equilibrium up to $s/2$: for every $\tau$,

$$
\pi(\tau,\sigma)=\frac{\pi(\sigma,\tau)+\pi(\tau,\sigma)}{2}+\frac{\pi(\tau,\sigma)-\pi(\sigma,\tau)}{2}\;\le\;E_{\max}+\frac{s}{2}\;=\;\pi(\sigma,\sigma)+\frac{s}{2}.
$$

With $s=(1-\delta)(T-S)$, one exploited round, tit-for-tat and the eight qualify at every $\delta$, and as $\delta\to1$ the slack vanishes and the statement returns to the theorem of §2.

The paragraph gives the error-free step for a deterministic strategy. The argument below also covers errors,
0 < ε < ½ (for ε ≥ ½ an intended cooperation is carried out with probability at most one half, and the error step
fails), and stochastic strategies: if the self-play of a strategy first cooperates in round t with probability
q > 0, its deficit against *ALLD* is at least q(1 − δ)δ^(t−1)(T − S).

## The argument in full

This section writes out the argument of the paragraph in full; the error step, the efficiency of *ALLC* and the
check are added here.

**The discounted game.** With a discount factor δ < 1 the payoff is
$\pi_\delta(\sigma,\tau)=(1-\delta)\sum_{t\ge1}\delta^{t-1}\pi_t$, where $\pi_t$ is σ's expected payoff in
round t, and the game starts from a given first move. The early rounds now carry weight, so a strategy must also say
what it does before it has a history of two rounds: a binary memory-two strategy with a start is a first move, a
second move after each of the four first-round outcomes, and the 16 answers of memory two, 21 binary decisions in
all. The definitions of SI §2 apply verbatim to the matrix $\pi_\delta$ (efficient: $\pi_\delta(\sigma,\sigma)$
equals the joint optimum $E_{\max}$, the largest average payoff of any pair; stable: a symmetric Nash equilibrium; rival:
$\pi_\delta(\sigma,\tau)\ge\pi_\delta(\tau,\sigma)$ for every τ), and so does the theorem (an efficient
rival is a Nash equilibrium), whose proof uses only the entries of the matrix. The best reply to a fixed σ, and the
co-player that gets furthest ahead of it, solve a discounted Markov decision problem on σ's 21 history states, since
both players see the same outcomes; such a problem has an optimal policy that is deterministic and stationary in those
states, so both maxima over *all* co-players are attained by a memory-two strategy with a start and can be computed
exactly.

**1. Where T > S no strategy is both efficient and a rival, at any δ < 1 and any 0 ≤ ε < ½.**

*Without errors.* Two copies of a strategy σ play symmetrically, so before their first cooperation the history consists
of mutual defections only, and *ALLD* produces exactly that history. If the self-play of σ first cooperates in round t,
with probability q > 0, then σ cooperates in round t against *ALLD* too, with the same probability, earning S while
*ALLD* earns T; and afterwards σ can never earn T against *ALLD*, which never cooperates. So
$\pi_\delta(\textit{ALLD},\sigma)-\pi_\delta(\sigma,\textit{ALLD})\ge q(1-\delta)\delta^{t-1}(T-S)>0$ and σ is
not a rival. If the self-play of σ never cooperates, σ earns P < R against itself; since the joint optimum is at least
R (the self-play of *ALLC*), σ is not efficient. An efficient strategy below the switch line cooperates in round one, so
its deficit is at least (1 − δ)(T − S), one exploited round. (Above the switch line no strategy is efficient without
errors at all: symmetric play from a common start never alternates, while a pair of different strategies can.)

*With errors, 0 < ε < ½.* In a round in which σ intends to cooperate against *ALLD*, σ plays C with probability 1 − ε and
*ALLD* plays D with probability 1 − ε, so σ's expected payoff minus *ALLD*'s in that round is
(S − T)[(1 − ε)² − ε²] = −(1 − 2ε)(T − S) < 0. In a round in which σ intends to defect, the outcomes CD and DC both have
probability ε(1 − ε) and the difference is zero. Hence

$$
\pi_\delta(\textit{ALLD},\sigma)-\pi_\delta(\sigma,\textit{ALLD})=(1-2\epsilon)(T-S)\,(1-\delta)\sum_{t\ge1}\delta^{t-1}\Pr[\sigma\text{ intends C in round }t],
$$

and since at ε > 0 every finite history occurs with positive probability, this is positive unless σ never intends to
cooperate. The strategy that never intends to cooperate is not efficient: its self-play per round,
(1 − ε)²P + ε(1 − ε)(S + T) + ε²R, is below that of *ALLC*, (1 − ε)²R + ε(1 − ε)(S + T) + ε²P, by (1 − 2ε)(R − P) > 0,
and the joint optimum is at least the latter. ∎

**2. On the wedge S (T < S, 2R > T + S) *ALLC* is a friendly rival at every δ < 1 and every ε < ½.**

*Rival.* In every round *ALLC* plays C with probability 1 − ε, whatever has happened. If the co-player plays D in that
round with probability q, then q ≥ ε (an intended move is carried out with probability at most 1 − ε), and *ALLC*'s
payoff minus the co-player's is (S − T)[(1 − ε)q − ε(1 − q)] = (S − T)(q − ε) ≥ 0. Summed over the rounds with the
weights (1 − δ)δ^(t−1), $\pi_\delta(\textit{ALLC},\tau)\ge\pi_\delta(\tau,\textit{ALLC})$ for every τ.

*Efficient.* Given the history, the two moves of a round are independent, each a cooperation with a probability in
[ε, 1 − ε]; the pair's average payoff in the round, f(a, b), is bilinear in these probabilities, and since the wedge S
lies below the switch line (R > (S + T)/2) and R > P, its largest value on [ε, 1 − ε]² is f(1 − ε, 1 − ε), the value of
*ALLC* against itself (the argument is in `fixed-error-rate.md`, last section). Every pair's discounted average is a
weighted average of such round values, so none exceeds *ALLC*'s self-play: *ALLC* attains the joint optimum. By the
theorem it is then also a Nash equilibrium, a partner.

**3. The theorem with a slack.** Call σ unbeatable up to s if $\pi(\sigma,\tau)\ge\pi(\tau,\sigma)-s$ for every
τ. An efficient strategy that is unbeatable up to s is a Nash equilibrium up to s/2: for every τ,

$$
\pi(\tau,\sigma)=\frac{\pi(\sigma,\tau)+\pi(\tau,\sigma)}{2}+\frac{\pi(\tau,\sigma)-\pi(\sigma,\tau)}{2}\;\le\;E_{\max}+\frac{s}{2}\;=\;\pi(\sigma,\sigma)+\frac{s}{2},
$$

by the sum bound $\pi(\sigma,\tau)+\pi(\tau,\sigma)\le2E_{\max}$ and efficiency.

**4. Tit-for-tat and the eight qualify with one exploited round.** Take s = (1 − δ)(T − S). Tit-for-tat and the eight
friendly rivals of the wedge W, started cooperatively and without errors, cooperate in every round of self-play, so
they are efficient below the switch line; and no co-player gets further ahead of them than one exploited round, which
*ALLD* takes in round one. So they are unbeatable up to s and Nash equilibria up to s/2 = (1 − δ)(T − S)/2 at every δ,
and as δ → 1 the slack vanishes and the statement returns to the theorem of SI §2. That the bound is attained
exactly, and not only bounded below, is the computation below.

**Two limits.** Rivalry is thus a limit statement twice over: the first exploitation that *ALLD* inflicts on a
cooperator is worth (1 − δ)(T − S) under discounting and ε(T − S) per round at a positive error rate, and it is the
limits δ → 1 and ε → 0 that make it worth nothing. The two limits do not commute. The relevant parameter is ε/(1 − δ),
the expected number of errors within the effective horizon 1/(1 − δ): if ε ≫ 1 − δ the stationary regime of the
undiscounted game dominates, and if ε ≪ 1 − δ errors hardly occur within the horizon and play is essentially
error-free from the start.

## The bound, computed

`checks/check_discounting.py` computes, for a strategy with a start, the largest relative payoff
max over τ of [π_δ(τ, σ) − π_δ(σ, τ)]/(T − S) over **all** co-players, by value iteration on σ's 21 history states
(reward +1 when σ cooperates and τ defects, −1 in the reverse case; the result does not depend on the game as long as
T > S). “Started cooperatively” is taken as: first move C, and after the first round the strategy's own memory-two
answer as if the round before the first had been mutual cooperation. Output in `checks/check_discounting.txt`:

- Without errors, for tit-for-tat, *Grim* and each of the eight (19079, 19087, 20103, 20111, 23175, 23183, 24199,
  24207), at δ = 0.9, 0.99 and 0.999: the maximum is **1 − δ exactly**, and *ALLD* attains it. The bound of claim 1 is
  attained, which is the paragraph's “Tit-for-tat, Grim and the eight friendly rivals of the wedge W, started
  cooperatively, attain this bound exactly”.
- With errors, ε = 10⁻⁴: the maximum stays positive (for tit-for-tat 0.100070, 0.010097, 0.001100 at the three δ), as
  claim 1 requires; *ALLD* comes within 10⁻⁸ of the best co-player.
- On the wedge S, *ALLC* started cooperatively: the maximum is 0 at δ = 0.9, 0.99, 0.999 and ε = 0, 10⁻⁴, 0.1, 0.4, as
  claim 2 requires.

## References

1. Hilbe, C., Chatterjee, K. & Nowak, M. A. Partners and rivals in direct reciprocity. *Nat. Hum. Behav.* **2**, 469–477 (2018).
