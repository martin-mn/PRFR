"""
notes_text.py -- the text of ../../notes/*.md: the Markdown written for the notes, the passages each file uses, and
the edits that bring the references of a passage to the paper's numbering.

FILES: [(file name, title, [part, ...])].  A part is one of
  * Markdown written for the notes (a string);
  * a passage given here in Markdown, Passage(heading, text): heading is the section heading in the note (None for
    none), and [@key] or [@key, @key, ...] in the text is a citation of refs.tex, numbered by mknotes.py in the order
    of first citation in the file;
  * a passage of the author's file of passages, (key, heading, edits): key is a substring of the passage's heading
    in that file (it must match exactly one heading), heading the section heading in the note (None for none), and
    edits a list of (old, new) substitutions made in the converted Markdown of the passage, each of which must occur
    exactly once.  The edits bring references to the paper's numbering.

RENAMES: the renames of the second property, made in every passage of either kind (see below).  The Markdown written
for the notes uses the new name directly.
"""


class Passage:
    """a passage given here in Markdown (see the docstring above)"""

    def __init__(self, heading, text):
        self.heading, self.text = heading, text


CONV = """The passages are longer versions of passages condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX; section numbers are those of the SI (“§7” is SI §7). A genome is written
as 16 symbols, position j from the left holding the answer in the state j = 4 (most recent outcome) + (the outcome
before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 from the player's own side; a state written (X, Y) is X in the most
recent round and Y in the round before. `1` or C is cooperation. The game is (R, S, T, P) = (1, u, 1 + v, 0)."""

DISK = """Percentages “of the disk” are areas of the compactified disk of the main-text figures (**Methods**), not measures
over games."""

# The second of the three properties, which the passages call "Nash", is called "stable" in the paper (the author's
# decision of 2026-09-25): a strategy is stable if it is a symmetric Nash equilibrium against a single deviant.  The
# passages keep the author's words as in his file of passages, and mknotes.py makes these renames in every passage
# of either kind, after its edits: (old, new, n), where old is matched as whole words, never where "Nash
# equilibrium" or "Nash equilibria" follows, and n is the number of times it must apply over the six notes.
# "Nash equilibrium" and "Nash equilibria" are kept, and mknotes.py refuses to write a note in which "Nash" occurs
# in any other way outside its list of references.
RENAMES = [
    ("neither Nash nor", "neither stable nor", 1),         # memory-one-atoms.md: the atom 100
    ("are Nash", "are stable", 2),                         # memory-one-atoms.md: "where all three are", "where they are"
    ("is Nash", "is stable", 1),                           # memory-one-atoms.md: WSLS above the switch line
    ("The Nash strategies", "The stable strategies", 1),   # memory-one-atoms.md: the atom 010
    ("The Nash rivals", "The stable rivals", 1),           # memory-one-atoms.md: the atom 011
]

FILES = []

# ----------------------------------------------------------------------------------------------------------------------
FILES.append(("fixed-error-rate.md", "Why the limit, and not a fixed error rate: the worked examples at ε = 0.01", [
    """The paragraph “Why the limit, and not a fixed error rate” of SI §1 ends: *“Worked examples at ε = 0.01 are in the
notes deposited with the code.”* Below are a longer version of that paragraph, which gives the examples, the case
T < S, the examples recomputed, and the argument that below the switch line only *ALLC* is efficient at a fixed ε.""",
    CONV,
    Passage("The paragraph in full", r"""**Why the limit, and not a fixed error rate.** The maps of the main text are run at $\epsilon=10^{-4}$, and one may ask why they are organised by classes defined in the limit rather than by the same classes read at that error rate. The reason is a matter of scales. At a fixed $\epsilon$ the payoff matrix is $A(\epsilon)=A_0+\epsilon A_1+\epsilon^2A_2+\dots$, where $A_0$ is the limit matrix. The gaps in $A_0$ are of order one: earning $R$ with a cooperator against earning $S$ or $P$. The gaps in $A_1$ are of order $\epsilon$: the cost of recovering from an error, one exploited round per error of one's own. A payoff difference $\Delta$ decides the fate of a mutant in a population of size $N$ under selection strength $\beta$ only when $N\beta\Delta$ is of order one, so at $\epsilon=10^{-4}$ the small population of SI Figure 4 ($N\beta=300$) resolves $A_0$ alone, the large population of main text Figure 4 ($N\beta=10^{5}$) resolves $A_0$ and part of $A_1$, and no run resolves the tails. The limit classes are the sign pattern of $A_0$, with ties read as ties: they cut the matrix at its order-one gaps, which is where the population's fate is decided, and they are the same for every small $\epsilon$ and piecewise constant over the plane of games, because they are properties of a strategy's rules along the paths that play actually follows, the cooperative path and the recoveries from single errors. The same classes read exactly at a fixed $\epsilon$ cut at threshold zero, so that each membership is decided by whichever order of $\epsilon$ finally breaks a tie, and they degenerate. At $\epsilon=0.01$, for instance, where $T>S$ the only strategy that is never behind *ALLD* is *ALLD* itself, because at every state at which a strategy intends to cooperate it nets $(\epsilon^2-(1-\epsilon)^2)(T-S)<0$ per visit against *ALLD* and every state is visited; tit-for-tat is behind by $0.98\,\epsilon\,(T-S)$ per round and the eight friendly rivals by about $1.9\,\epsilon\,(T-S)$. Below the switch line the only efficient strategy at a fixed $\epsilon$ is *ALLC*, since every intended defection at a visited state adds error-induced losses, and above the switch line no strategy is efficient at $\epsilon=0.01$: at $(u,v)=(-0.5,2)$, for instance, the pair *ALLC*–*ALLD* alone averages more than the best self-play, that of an alternator, so the joint optimum lies off the diagonal, the situation of the one-shot game in §2 returning at a positive error rate. Where $T>S$ there is therefore no friendly rival at any fixed $\epsilon$, since *ALLD* is not efficient, and the strict equilibria, which are a fixed-$\epsilon$ class, carry at most 4% and 19% of the population at $N=100$ and $N=1000$ (§9). Any threshold between $\epsilon$ and one on the payoff differences reproduces the limit classes, since the order-$\epsilon$ gaps lie below it and the order-one gaps above; the limit is the threshold-free name for that window. The ties of the limit are information rather than a defect: the 7639 mutual cooperators tie at $R$, and that tie is the neutral plateau over which drift and numbers act, and over which selection acts only through $A_1$ when $N\beta\epsilon$ is large. Two qualifications. The argument holds while $\epsilon$ is small against the game's own gaps, $\epsilon(T-S)\ll R-P$. And questions that are themselves about the order-$\epsilon$ structure, which partner prevails on a plateau or which equilibria are strict, need the graded quantities at a fixed $\epsilon$, with thresholds in units of $\epsilon$."""),
    """## Where T < S

Where T < S a player that cooperates while its co-player defects is ahead, so the degeneration of the fixed-ε classes
described above is one-sided. On the wedge S (T < S, 2R > T + S) *ALLC* is a friendly rival at every ε < ½. It is a
rival: in every round it plays C with probability 1 − ε, whatever has happened, and if the co-player plays D in that
round with probability q, then q ≥ ε and *ALLC*'s payoff minus the co-player's is (S − T)(q − ε) ≥ 0. It is
efficient, since the wedge S lies below the switch line (see the last section of this note). By the theorem it is
then also a Nash equilibrium, a partner, at every fixed ε; the same holds for the discounted game (`discounting.md`,
claim 2).""",
    """## The examples, recomputed

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
falls strictly short of it. The same argument holds for the discounted payoff (`discounting.md`).""",
]))

# ----------------------------------------------------------------------------------------------------------------------
FILES.append(("discounting.md", "Discounting: the full argument", [
    """The paragraph “Discounting” of SI §1 ends: *“The full argument is in the notes deposited with the code.”* This note
gives a longer version of the paragraph, the argument written out in full, and a numerical check of the bound it
rests on.""",
    CONV,
    Passage("The paragraph in full", r"""**Discounting.** The same considerations apply when the future is discounted, and one of them becomes a theorem. Let the payoff be $\pi_\delta(\sigma,\tau)=(1-\delta)\sum_{t\ge1}\delta^{t-1}\pi_t$ for a discount factor $\delta<1$, the game started from a given first move. The definitions of §2 apply verbatim to the matrix $\pi_\delta$, and so does the theorem of §2, since its proof uses only the entries of the matrix. But where $T>S$ its hypothesis cannot be met: at any $\delta<1$ and any $0\le\epsilon<\tfrac12$, no strategy is both efficient and a rival. Without errors, two copies of a strategy play symmetrically, so before their first cooperation the history consists of mutual defections only, and *ALLD* produces exactly that history. A strategy whose self-play ever cooperates therefore cooperates, at the same round $t$, against *ALLD*, earning $S$ while *ALLD* earns $T$, and afterwards it can never earn $T$ against *ALLD*; its discounted deficit is at least $(1-\delta)\delta^{t-1}(T-S)>0$, and for an efficient strategy, which cooperates in round one, at least $(1-\delta)(T-S)$. Tit-for-tat, *Grim* and the eight friendly rivals of the wedge $W$, started cooperatively, attain this bound exactly. Where $T<S$ and $2R>T+S$, the wedge $S$, the argument reverses: cooperating against a defector puts a player ahead, and *ALLC* is a friendly rival at every $\delta$ and every $\epsilon<\tfrac12$. Rivalry is thus a limit statement twice over. The first exploitation that *ALLD* inflicts on a cooperator is worth $(1-\delta)(T-S)$ under discounting and $\epsilon(T-S)$ per round at a positive error rate, and the limits $\delta\to1$ and $\epsilon\to0$ are what make it worth nothing; Hilbe, Chatterjee and Nowak make the same observation for reactive strategies [@HilbeChatterjeeNowak2018]. The theorem recovers its content with a slack. Call $\sigma$ unbeatable up to $s$ if $\pi(\sigma,\tau)\ge\pi(\tau,\sigma)-s$ for every $\tau$. An efficient strategy that is unbeatable up to $s$ is a Nash equilibrium up to $s/2$: for every $\tau$,

$$
\pi(\tau,\sigma)=\frac{\pi(\sigma,\tau)+\pi(\tau,\sigma)}{2}+\frac{\pi(\tau,\sigma)-\pi(\sigma,\tau)}{2}\;\le\;E_{\max}+\frac{s}{2}\;=\;\pi(\sigma,\sigma)+\frac{s}{2}.
$$

With $s=(1-\delta)(T-S)$, one exploited round, tit-for-tat and the eight qualify at every $\delta$, and as $\delta\to1$ the slack vanishes and the statement returns to the theorem of §2."""),
    """The paragraph gives the error-free step for a deterministic strategy. The argument below also covers errors,
0 < ε < ½ (for ε ≥ ½ an intended cooperation is carried out with probability at most one half, and the error step
fails), and stochastic strategies: if the self-play of a strategy first cooperates in round t with probability
q > 0, its deficit against *ALLD* is at least q(1 − δ)δ^(t−1)(T − S).

## The argument in full

This section writes out the argument of the paragraph in full; the error step, the efficiency of *ALLC* and the
check are added here.

**The discounted game.** With a discount factor δ < 1 the payoff is
$\\pi_\\delta(\\sigma,\\tau)=(1-\\delta)\\sum_{t\\ge1}\\delta^{t-1}\\pi_t$, where $\\pi_t$ is σ's expected payoff in
round t, and the game starts from a given first move. The early rounds now carry weight, so a strategy must also say
what it does before it has a history of two rounds: a binary memory-two strategy with a start is a first move, a
second move after each of the four first-round outcomes, and the 16 answers of memory two, 21 binary decisions in
all. The definitions of SI §2 apply verbatim to the matrix $\\pi_\\delta$ (efficient: $\\pi_\\delta(\\sigma,\\sigma)$
equals the joint optimum $E_{\\max}$, the largest average payoff of any pair; stable: a symmetric Nash equilibrium; rival:
$\\pi_\\delta(\\sigma,\\tau)\\ge\\pi_\\delta(\\tau,\\sigma)$ for every τ), and so does the theorem (an efficient
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
$\\pi_\\delta(\\textit{ALLD},\\sigma)-\\pi_\\delta(\\sigma,\\textit{ALLD})\\ge q(1-\\delta)\\delta^{t-1}(T-S)>0$ and σ is
not a rival. If the self-play of σ never cooperates, σ earns P < R against itself; since the joint optimum is at least
R (the self-play of *ALLC*), σ is not efficient. An efficient strategy below the switch line cooperates in round one, so
its deficit is at least (1 − δ)(T − S), one exploited round. (Above the switch line no strategy is efficient without
errors at all: symmetric play from a common start never alternates, while a pair of different strategies can.)

*With errors, 0 < ε < ½.* In a round in which σ intends to cooperate against *ALLD*, σ plays C with probability 1 − ε and
*ALLD* plays D with probability 1 − ε, so σ's expected payoff minus *ALLD*'s in that round is
(S − T)[(1 − ε)² − ε²] = −(1 − 2ε)(T − S) < 0. In a round in which σ intends to defect, the outcomes CD and DC both have
probability ε(1 − ε) and the difference is zero. Hence

$$
\\pi_\\delta(\\textit{ALLD},\\sigma)-\\pi_\\delta(\\sigma,\\textit{ALLD})=(1-2\\epsilon)(T-S)\\,(1-\\delta)\\sum_{t\\ge1}\\delta^{t-1}\\Pr[\\sigma\\text{ intends C in round }t],
$$

and since at ε > 0 every finite history occurs with positive probability, this is positive unless σ never intends to
cooperate. The strategy that never intends to cooperate is not efficient: its self-play per round,
(1 − ε)²P + ε(1 − ε)(S + T) + ε²R, is below that of *ALLC*, (1 − ε)²R + ε(1 − ε)(S + T) + ε²P, by (1 − 2ε)(R − P) > 0,
and the joint optimum is at least the latter. ∎

**2. On the wedge S (T < S, 2R > T + S) *ALLC* is a friendly rival at every δ < 1 and every ε < ½.**

*Rival.* In every round *ALLC* plays C with probability 1 − ε, whatever has happened. If the co-player plays D in that
round with probability q, then q ≥ ε (an intended move is carried out with probability at most 1 − ε), and *ALLC*'s
payoff minus the co-player's is (S − T)[(1 − ε)q − ε(1 − q)] = (S − T)(q − ε) ≥ 0. Summed over the rounds with the
weights (1 − δ)δ^(t−1), $\\pi_\\delta(\\textit{ALLC},\\tau)\\ge\\pi_\\delta(\\tau,\\textit{ALLC})$ for every τ.

*Efficient.* Given the history, the two moves of a round are independent, each a cooperation with a probability in
[ε, 1 − ε]; the pair's average payoff in the round, f(a, b), is bilinear in these probabilities, and since the wedge S
lies below the switch line (R > (S + T)/2) and R > P, its largest value on [ε, 1 − ε]² is f(1 − ε, 1 − ε), the value of
*ALLC* against itself (the argument is in `fixed-error-rate.md`, last section). Every pair's discounted average is a
weighted average of such round values, so none exceeds *ALLC*'s self-play: *ALLC* attains the joint optimum. By the
theorem it is then also a Nash equilibrium, a partner.

**3. The theorem with a slack.** Call σ unbeatable up to s if $\\pi(\\sigma,\\tau)\\ge\\pi(\\tau,\\sigma)-s$ for every
τ. An efficient strategy that is unbeatable up to s is a Nash equilibrium up to s/2: for every τ,

$$
\\pi(\\tau,\\sigma)=\\frac{\\pi(\\sigma,\\tau)+\\pi(\\tau,\\sigma)}{2}+\\frac{\\pi(\\tau,\\sigma)-\\pi(\\sigma,\\tau)}{2}\\;\\le\\;E_{\\max}+\\frac{s}{2}\\;=\\;\\pi(\\sigma,\\sigma)+\\frac{s}{2},
$$

by the sum bound $\\pi(\\sigma,\\tau)+\\pi(\\tau,\\sigma)\\le2E_{\\max}$ and efficiency.

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
  claim 2 requires.""",
]))

# ----------------------------------------------------------------------------------------------------------------------
FILES.append(("families.md", "The families of friendly rivals: W by rows, N state by state, the largest pattern of S", [
    """SI §7 says: *“The notes deposited with the code read the family of W by rows, the eight positions shared by the
80 of N state by state, and the largest pattern of S.”* The three readings are below, each followed by a longer
version of the corresponding paragraph of SI §7, with the literature and the counts that the SI states more briefly.
The family descriptions themselves (the prime patterns and the minimal covers, among them the cover of 42 patterns of
S that the Methods and SI §7 say is “included in the computed output”) are in the folder `families/` of the
repository.""",
    CONV,
    """A pattern is 16 symbols `1`, `0` or `*`, a wildcard standing for either answer. The eight friendly rivals of W are
the pattern `111*000101*1*010`, integer codes 19079, 19087, 20103, 20111, 23175, 23183, 24199, 24207.""",
    ("the wedge W: the rules of the eight, read by rows", "W: the rules of the eight, read by rows", []),
    Passage("W: the paragraph in full", r"""**The wedge $W$: one family.** The eight friendly rivals of the Prisoner's Dilemma wedge are a single family with three wildcards, `111*000101*1*010` (SI Table 4a), with integer codes 19079, 19087, 20103, 20111, 23175, 23183, 24199 and 24207. In brief, the family cooperates after mutual cooperation, punishes exploitation, answers an unprovoked defection of its own with a second one, the anti-tit-for-tat move of *TFT-ATFT* [@YiBaekChoi2017], then accepts the punishment, and defects after prolonged mutual defection, which is what makes *ALLD* unprofitable and the strategy a rival; the rules read by rows, with the reason for each, are given above. The three wildcards sit at the states $(CC,DD)$, $(DC,DC)$ and $(DD,CC)$, positions 3, 10 and 12. The first and the last are reached in self-play only at second order in the error rate and cost nothing in the limit. The second decides distinguishability: the four members that defect at $(DC,DC)$, 19079, 19087, 23175 and 23183, keep exploiting an unconditional cooperator and are the four strategies that Yi, Baek and Choi single out by adding distinguishability to efficiency and defensibility [@YiBaekChoi2017], *TFT-ATFT* and its three variants, while the four that cooperate there return to mutual cooperation against *ALLC* and earn only $R$ against it; Murase and Baek count all eight as *TFT-ATFT* and its variants [@MuraseBaek2020]. Two members, 20111 and 24207, which cooperate at $(DC,DC)$, are fair and belong to $S$ as well. The second defection at $(DC,CC)$ is not contrition in the classical sense. Contrite tit-for-tat [@Sugden1986, @BoerlijstNowakSigmund1997JTB, @WuAxelrod1995] apologises at once for an unprovoked defection of its own and keeps track of the players' standing, which no bounded history of round outcomes records [@MuraseBaek2020automata]; and contrition alone does not ensure cooperation [@Hilbe2009]. This family does the reverse: it defects once more and only then accepts the co-player's punishment."""),
    ("the wedge N: the eight positions shared by all 80, state by state",
     "N: the eight positions shared by all 80, state by state", []),
    Passage("N: the paragraph in full", r"""**The wedge $N$: four families in two pairs.** The 80 alternating friendly rivals of the Snowdrift wedge are covered by exactly four prime patterns, two with five wildcards and two with four, and the description is unique (SI Table 4b): `*10*0000*1*1*010` and `*01*0000*1*1*010` with 32 members each, `*10*000*11*10010` and `*01*000*11*10010` with 16 each. The four overlap: the families of 32 and 16 on the left of the table share 8 strategies, as do the two on the right, so $32+32+16+16-16=80$. All 80 agree at eight positions, `****000**1*1*010`, which encode the alternation itself, its restart in the right phase after a double error, and defection after $(DD,DD)$, which keeps *ALLD* out. The two families of a pair differ only in how the two players break the symmetry again after a round of mutual cooperation that followed an asymmetric round, which they can do in either order; the pairs differ at three further states. The rules state by state are given above. The 80 cooperate at between 4 and 9 of their 16 states; none is a strategy with a name. Eight of them, the fair alternators, are friendly rivals in $E$ as well."""),
    """## S: the largest pattern, state by state

The reading of the largest pattern of S, `111*1***11*1****` (512 strategies), is part of the paragraph below:
“cooperate after mutual cooperation, cooperate after being exploited if the round before was mutual cooperation,
cooperate after exploiting the co-player unless the round before was DC, and do anything else at the remaining
states, in particular anything after mutual defection.”""",
    ("'The wedge S: no compact description'", "S: the paragraph in full", []),
    """## Checked

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
are the prime patterns and minimal covers of the families is the census's result (`families/`).""",
]))

# ----------------------------------------------------------------------------------------------------------------------
FILES.append(("bays-and-cycles.md", "The atom 110 in its bays: the last forgivers and the cycles that exploit them", [
    """SI §8, on the atom `110` (the partners that are not rivals), says of the lines that bound its bays: *“Each of these
lines is the equilibrium condition of the last forgivers to survive it, beyond which a cycle exploiting their
forgiveness pays more than their self-play; each was read off the arrangement and checked by computing the best
co-player of the surviving strategy at ε = 10⁻⁶ on either side of the line, and the strategies and cycles are in the
notes deposited with the code.”* The bays are the regions where the atom is empty, so that the only partners are the
friendly rivals. Below: two passages that name the strategies and cycles, the strategies of every line, and the
check of every line.""",
    CONV,
    DISK,
    """## The Prisoner's Dilemma bay

In the Prisoner's Dilemma the bay is the set v > 2, u + 2v > 2, 3u + v < −1 (SI §8), that is T > 3R − 2P,
2T + S + P > 4R and 3S + T < 4P. The first, second and third line of the passage are v = 2, u + 2v = 2 and
3u + v = −1.""",
    Passage(None, r"""The first line is the equilibrium condition of mutual cooperators that resume cooperation after two rounds of mutual defection, such as `1001000000000001`, against which *ALLD* earns $T$, $P$, $P$ in a cycle of three rounds; the second is that of the partner `1110000100010010`, which a co-player exploits with a cycle of four rounds paying $T$, $T$, $S$, $P$; the third is that of alternators such as `0100000101100010`, exploited by a cycle of five rounds paying $S$, $P$, $T$, $T$, $P$ against the alternation payoff $(S+T)/2$."""),
    """The three strategies of the passage are 32777 (`1001000000000001`, the line v = 2), 18567 (`1110000100010010`,
u + 2v = 2) and 18050 (`0100000101100010`, 3u + v = −1).""",
    Passage("The Harmony bays", r"""In the Harmony quadrant the bay is the part of $E$ with $u+3v<-1$, that is $S+3T<2R+2P$, 3.0% of the disk, where the last forgiving alternators are exploited, two of them by a cycle of five rounds paying $R$, $S$, $S$, $T$, $P$ and the third by play that mixes their alternation with a cycle of three rounds paying $S$, $P$, $R$; and the sliver of $S$ with $u>6$ and $5u+4v>6$, that is $S>6R-5P$ and $5S+4T+P>10R$, 0.3% of the disk, where the last forgiving mutual cooperators are exploited by play that gives the co-player $R$ four times, $S$ once and $P$ five times in ten rounds, and by play that gives it $R$ five times, $S$ five times, $T$ four times and $P$ once in fifteen, each a mixture of shorter cycles."""),
    """## The strategies and cycles of every line

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
  partner's self-play, which equals $E_{\\max}$ (the partner is efficient), so that the partner is stable there; on
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
  three bays (5470 of the 27598 polygons of `m2_faces.csv`), and the two Harmony bays cover 3.02% and 0.29% of the area of the disk.""",
]))

# ----------------------------------------------------------------------------------------------------------------------
FILES.append(("longer-punishment.md", "Longer punishment, and why it is not rivalry: the full comparison", [
    """The paragraph “Longer punishment, and why it is not rivalry” of SI §9 ends: *“… where 22663 is a partner; the
full comparison is in the notes deposited with the code.”* Below is the paragraph in full, with both exploiting
cycles, the second example (32907 near the origin) and the counts of co-players that finish ahead, and then the
numbers recomputed, among them the self-play payoffs of 22663 and 23175 at ε = 10⁻⁴ that SI §9 quotes in “Which
partners win”.""",
    CONV,
    ("'Longer punishment, and why it is not rivalry'", "The paragraph in full", [
        ("are the ones ahead against the cloud (above).", "are the ones ahead against the cloud (SI §9, “Which partners win”)."),
    ]),
    """## Recomputed (2026-09-24)

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
  order.""",
]))

# ----------------------------------------------------------------------------------------------------------------------
FILES.append(("memory-one-atoms.md", "Memory one: the atoms strategy by strategy", [
    """SI §10, “The sixteen strategies”, ends: *“SI Table 8 thus gives the atom of every strategy at every game off the
two lines; the reading of main text Figure 2a–g atom by atom is in the notes deposited with the code.”* That reading
is below, followed by its check against the exact memory-one arrangement.""",
    """The passage is a longer version of a passage condensed in the SI, in the author's words, converted from LaTeX to
Markdown with the mathematics left in LaTeX. A memory-one strategy is written by its answers after the outcomes CC,
CD, DC, DD of the last round, own move first: *ALLD* = DDDD, *Grim* = CDDD, tit-for-tat = CDCD, *WSLS* (win-stay,
lose-shift) = CDDC, *ALLC* = CCCC. The game is (R, S, T, P) = (1, u, 1 + v, 0), so that T > R is v > 0, S > R is
u > 1, T > S is u < 1 + v, 2S < R + P is u < ½, T < 2R − P is v < 1, the switch line S + T = 2R is u + v = 1, and the
unit square is 0 ≤ u, v ≤ 1. The reading is that of the 45 open faces of the memory-one arrangement, off the three
half-lines, on each of which one further strategy is stable with ties (SI §10).""",
    DISK,
    Passage("The atoms strategy by strategy (main text Figure 2a–g)", r"""**The atoms strategy by strategy.** The counts of main text Figure 2a–g are constant on the 45 faces of the memory-one arrangement and small enough to be named. Between six and twelve of the sixteen strategies have none of the three properties (main text Figure 2a); tit-for-tat is the only one that never belongs to this atom, because it is competitive at every game. The efficient strategies that are neither Nash nor competitive, `100`, are the mutual cooperators *ALLC* and $CCCD$, the strategy that cooperates unless both players defected, wherever $T>R$ below the switch line, where an unconditional defector exploits them, joined by *WSLS* where $T>2R-P$, and *WSLS* alone in the Harmony games with $S>R$; the atom is empty above the switch line, where no memory-one strategy is efficient, and where $T\le R$ and $S\le R$, where all three are Nash (Figure 2b). The Nash strategies that are neither efficient nor competitive, `010`, are up to five of the sixteen in the Stag Hunt, *ALLD*, *Grim*, $DCCD$, $DDDC$ and $DCCC$ on parts of it and *ALLD* among them wherever $T<S$; $DDDC$ also in the Harmony games with $2S<R+P$; and *WSLS* alone on the part of the unit square above the switch line, where it is Nash but cannot alternate (Figure 2c). The atom is empty on 71% of the disk. Between two and four strategies are competitive only, `001`, tit-for-tat always among them (Figure 2d). The partners that are not competitive, `110`, are all three mutual cooperators where $T\le R$, $S\le R$ and $T>S$, and *WSLS* alone in the Prisoner's Dilemma with $T<2R-P$, in the Snowdrift games of the unit square below the switch line, and on the wedge $S$ with $S<R$ (Figure 2e). The Nash rivals that are not efficient, `011`, are *ALLD* and *Grim* in the Prisoner's Dilemma and in the Stag Hunt with $T>S$, *Grim* only where $2S+R\le3P$, and *ALLC* and $CCCD$ in the Harmony games above the switch line, where they are Nash and, since $T<S$, competitive, but where nothing that fails to alternate is efficient (Figure 2f). The friendly rivals, `111`, are *ALLC* and $CCCD$ on the wedge $S$ and nobody elsewhere (Figure 2g)."""),
    """## Checked (2026-09-24)

`checks/check_memory_one_atoms.py` (output `checks/check_memory_one_atoms.txt`; all checks pass) tests every sentence
of the passage against `data/arrangement/m1_faces.csv`, the exact atom of each of the 16 strategies on each of the 45
faces (computed in rational arithmetic by `data/arrangement/m1atoms.py`). Each sentence that names the members of an
atom is read as a rule giving, for a game (u, v), the set of strategies in that atom, and the rule must give exactly
the strategies of the table on every face; the counts, the ranges and the share of the disk on which `010` is empty
are recomputed from the same table.""",
]))
