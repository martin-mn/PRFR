# notes/checks — the numbers of the notes, recomputed

Each script recomputes what one note states, prints PASS or FAIL per statement, and exits non-zero if anything fails;
its output, as run on 2026-09-24, is the `.txt` file of the same name. Re-run on 2026-09-25, after the notes were
regenerated with the second property renamed "stable", every script passes; the scripts compute the numbers and
do not read the notes. Python 3 with numpy only
(`check_memory_one_atoms.py` needs the standard library only); each runs in seconds.

| script | note | what it recomputes | result |
|---|---|---|---|
| `check_fixed_eps.py` | `fixed-error-rate.md` | at ε = 0.01: the deficits of tit-for-tat (0.98) and the eight (≈ 1.9) against *ALLD* in units of ε(T − S); every other strategy behind *ALLD*; at (−0.5, 2) the pair *ALLC*–*ALLD* above every self-play; *ALLC*'s self-play the highest at (−1, 1) | all pass |
| `check_discounting.py` | `discounting.md` | the largest relative payoff of any co-player against tit-for-tat, *Grim* and the eight with a cooperative start, by value iteration on the 21 history states: 1 − δ exactly at ε = 0 (δ = 0.9, 0.99, 0.999), positive at ε = 10⁻⁴; *ALLC* never behind on the wedge S | all pass |
| `check_patterns.py` | `families.md` | the members and overlaps of the patterns of W, N and S; against `families/`, the covers of W and N, and the size, fixed positions, prime patterns, cover, multiplicity and members of S and of its defensible reading | all pass |
| `check_bays.py` | `bays-and-cycles.md` | for the eight lines of the bays of `110`, at ε = 10⁻⁶: the partner is stable on one side and exploited on the other, the exploiter's gain in the limit (exact fractions) is a multiple of the line's linear form, and its limiting play against the partner, split into the cycles of the error-free pair with their weights; against `data/arrangement/`, where `110` is empty and the disk shares of the Harmony bays | all pass |
| `check_longer_punishment.py` | `longer-punishment.md` | the genomes; 0, 8759 and 9253 co-players ahead of 23175, 22663 and 32907; the payoffs at (−3.21, 2.29) and (−0.38, 0.54); 32907 the most abundant strategy there at N = 1000 (`data/runs/`); the self-play deficits 7.6ε and 9.5ε | all pass |
| `check_memory_one_atoms.py` | `memory-one-atoms.md` | every sentence of the atom-by-atom reading of main text Figure 2a–g, against the exact atom of each of the 16 strategies on each of the 45 faces of `data/arrangement/m1_faces.csv` | all pass |

`pairchain.py` is the shared module: the 16-state chain of a pair of memory-two strategies with execution errors, in
the convention of the paper and of the simulator (`simulator/src/payf2.f`, `payf3.f`), solved by the
Grassmann–Taksar–Heyman state reduction vectorised over the co-players. It reproduces the simulator's own output: for
strategy 24199 at ε = 10⁻⁴ its self-play frequencies are 0.99882651, 0.00039949, 0.00039949, 0.00037452, as in the
w-file of the smoke run in `simulator/local/`.

The scripts read, and never write, `data/arrangement/`, `data/runs/` and `families/`.

```bash
cd notes/checks
for c in check_*.py; do python3 $c > ${c%.py}.txt; echo "$c: exit $?"; done
```
