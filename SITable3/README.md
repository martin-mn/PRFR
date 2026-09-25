# SITable3 — the counts at one game

This folder reproduces SI Table 3 (SI §6). It gives the number of binary memory-two strategies with each property at
the donation game with b = 1 and c = 2/3, the point (u,v) = (−2,2), (R,S,T,P) = (1,−2,3,0), in the limit ε→0.

    python3 sitable3.py          (about 1 s; numpy)

- **Input:** `../data/census/census.csv` (the exact run) and `census_double.csv` (the double-precision run).
- **Output:** the table printed with both runs next to the paper's, and `SITable3.csv`. The exit status is 1 on any
  mismatch.

**Method.** The game lies below the switch line, so the efficient strategies are the mutual cooperators (`eff_cc`).
It has T > S, so the competitive strategies are the rivals for T>S (`riv_p`). Stability and the tie clause come from the
census's `nash` pass at this game, against all 65536 memory-two co-players (`nash`, which holds stability, and
`tie_ok`).

The rows are:
- competitive, 2640;
- efficient, 7639;
- stable, 672;
- partners, 187;
- friendly rivals, 8;
- efficient, stable and competitive, 8;
- stable and competitive, 493;
- partners satisfying the tie clause, 8.

The script also checks the sentences around the table. Adding stability to "efficient and competitive" changes nothing.
Dropping efficiency admits 485 more strategies, ALLD among them. The 8 partners that satisfy the tie clause are the
eight friendly rivals of W.

**Verification (2026-09-24).** The script was run from a fresh copy. Every row agrees with ms.tex, which was parsed
directly, in both runs, with identical sets strategy by strategy.
