# SITable2 — the four quarter-planes

This folder reproduces SI Table 2 (SI §5). For each open wedge cut by the switch line u+v = 1 and the line
u−v = 1 (T = S), it gives the side of each line, the direction in which the wedge opens, what efficiency means there,
which sign of T − S rivalry refers to, and the number of friendly rivals among the 65536 binary memory-two strategies,
under the limit reading and under defensibility.

    python3 sitable2.py          (under 1 s; numpy)

- **Input:** `../data/census/census.csv`, read through `../census/censuslib.py`.
- **Output:** the table printed next to the paper's, and `SITable2.csv`. The exit status is 1 on any mismatch.

**Method.** The first six columns are derived at a test game far along each wedge's opening direction:
- the opening direction is the one axis direction whose ray stays in the wedge;
- efficiency comes from E_max = max(1, (1+u+v)/2), which is mutual cooperation R below the switch line and
  alternation (T+S)/2 above it;
- rivalry comes from the sign of T − S = 1 + v − u.

The two counts are `eff & riv` (limit) and `eff & def` (defensible), where the efficient set is `eff_cc` or `eff_alt`
and the rivalry set is `riv_p` or `riv_m`, taken from the wedge.

The script also checks the counts of the paragraph "The two lines" that precedes the table. There are 14757 efficient
strategies on the switch line, with 116 friendly rivals on its T>S part and 2067 on its T<S part. On T = S the
friendly rivals are the 7639 and 3072 efficient strategies.

**Verification (2026-09-24).** The script was run from a fresh copy. All four rows agree with ms.tex, which was parsed
directly (W 8/8, S 1519/1036, E 80/80, N 80/80), and so do the five counts of the two lines.
