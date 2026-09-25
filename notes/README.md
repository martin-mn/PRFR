# notes — the notes deposited with the code

The Supplementary Information refers in six places to "the notes deposited with the code", and the Code availability
statement promises "the notes on individual strategies and cycles referred to in the Supplementary Information". This
folder holds them, one file for each of the six places. Each file opens with the sentence of the paper that points to
it and gives longer versions of passages condensed in the SI, in the author's words (converted from LaTeX to
Markdown, with the mathematics in LaTeX), the arguments written out, and the numbers recomputed (`checks/`).

## Where each reference of the paper leads

| place in the paper | the sentence | file |
|---|---|---|
| SI §1, "Why the limit, and not a fixed error rate" | "Worked examples at ε = 0.01 are in the notes deposited with the code." | [`fixed-error-rate.md`](fixed-error-rate.md) |
| SI §1, "Discounting" | "The full argument is in the notes deposited with the code." | [`discounting.md`](discounting.md) |
| SI §7, "The families of friendly rivals" | "The notes deposited with the code read the family of W by rows, the eight positions shared by the 80 of N state by state, and the largest pattern of S." | [`families.md`](families.md) |
| SI §8, the atom `110` | "… and the strategies and cycles are in the notes deposited with the code." | [`bays-and-cycles.md`](bays-and-cycles.md) |
| SI §9, "Longer punishment, and why it is not rivalry" | "… where 22663 is a partner; the full comparison is in the notes deposited with the code." | [`longer-punishment.md`](longer-punishment.md) |
| SI §10, "The sixteen strategies" | "… the reading of main text Figure 2a–g atom by atom is in the notes deposited with the code." | [`memory-one-atoms.md`](memory-one-atoms.md) |
| Main text, Code availability | "… and the notes on individual strategies and cycles referred to in the Supplementary Information." | the six files above; the individual strategies and cycles are in `bays-and-cycles.md`, `longer-punishment.md`, `families.md` and `memory-one-atoms.md` |

The other items that the paper says are deposited with the code are not notes and live in other folders of the
repository:

| place in the paper | the item | folder |
|---|---|---|
| Methods, "Nash equilibria, partners and atoms"; SI §6, "What is computed here" | the exact arrangement, the faces with their sets of stable strategies | `data/arrangement/` |
| Methods, "Family descriptions"; SI §7, the wedge S | "one of the minimal covers is included in the computed output" | `families/` (`covers.csv`) |
| SI §6, "How the census was computed" | "Both programs and their README are part of the deposited code" | `census/` |
| Methods, "The Wright–Fisher process …" | the seed base "listed with the code" of every run, and the seed bases of the further runs | `simulator/SEEDS.csv`, `simulator/seeds_by_game.csv` |
| Code availability | "the evolutionary simulator with the seeds of every run" | `simulator/` |

## The files

| file | contents |
|---|---|
| `fixed-error-rate.md` | SI §1: the paragraph in full, the case T < S, the examples at ε = 0.01 recomputed, and why only *ALLC* is efficient below the switch line at a fixed ε |
| `discounting.md` | SI §1: the paragraph in full and the full argument (no efficient rival where T > S at any δ < 1 and 0 ≤ ε < ½; *ALLC* a friendly rival on the wedge S; the theorem with a slack), with the bound computed |
| `families.md` | SI §7: the family of W by rows, the eight positions of N state by state, the largest pattern of S, and the three paragraphs in full |
| `bays-and-cycles.md` | SI §8: the last forgivers of the atom `110` and the play that exploits them, with the strategies of every line, checked |
| `longer-punishment.md` | SI §9: 22663 against 23175, and 32907 near the origin, in full, recomputed |
| `memory-one-atoms.md` | SI §10: the reading of main text Figure 2a–g atom by atom, checked against the exact memory-one arrangement |
| `checks/` | the scripts that recompute the numbers and statements of the six files, and their output (see `checks/README.md`) |

## Conventions

A strategy of memory two is a genome of 16 symbols, position j from the left holding its answer in the state
j = 4 (most recent outcome) + (the outcome before), outcomes CC = 0, CD = 1, DC = 2, DD = 3 seen from the player's own
side, and its integer code is Σ c_j 2^j with c_j = 1 for cooperation (*ALLC* = 65535, *ALLD* = 0, tit-for-tat = 3855).
A state written (X, Y) is X in the most recent round and Y in the round before. A memory-one strategy is written by its
answers after CC, CD, DC, DD. The atoms are written efficient–stable–competitive, `110` being the partners that are not
rivals and `111` the friendly rivals. The game is (R, S, T, P) = (1, u, 1 + v, 0). Section, equation, figure and table
numbers are those of the paper. Percentages "of the disk" are areas of the compactified disk of the main-text figures,
not measures over games.

## How the files were made

`provenance/simulator-notes/mknotes.py` wrote the six `.md` files (not this README and not `checks/`) from
`provenance/simulator-notes/notes_text.py` and the author's LaTeX of the passages, with the manuscript's reference
list and its label numbers; the converter (`latex2md.py` there) refuses any LaTeX it does not know, so nothing is
dropped silently. `notes_text.py` holds the text written for the notes, some of the passages in Markdown, and, for
the passages converted from LaTeX, the edits that bring their references to the paper's numbering, each asserted to
apply exactly once. The passages call the second property "Nash", as the author's file of passages does; the paper
calls it "stable" (a symmetric Nash equilibrium against a single deviant), and `mknotes.py` renames it in every
passage by the list `RENAMES` of `notes_text.py`, each rename asserted to apply the number of times given there. It
writes no note in which "Nash" occurs other than in "Nash equilibrium" or "Nash equilibria", outside the list of
references.
