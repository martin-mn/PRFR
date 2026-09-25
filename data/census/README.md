# data/census — the census of the 65536 binary memory-two strategies, one row per strategy

This folder holds the reduced output of the exact ε→0 census of SI §6. It was computed by `../../census/pairsq.c`
(exact rational arithmetic) and `../../census/pairs.c` (double precision) in Cannon job 48068392 on 2026-09-23, and
reduced by `../../census/reduce.py`. Defensibility comes from `../../census/defensible.py`. Every file below is written
by `reduce.py` and can be regenerated bit for bit from the programs (see `../../census/README.md`). The raw pass
outputs, 8192 files and 32 MB, are not deposited.

| file | bytes | what |
|---|---:|---|
| `census.csv` | 6175141 | the exact run: 65536 rows, with self-play, rivalry for T>S and T<S, defensibility, and stability and the tie clause at (u,v) = (−2,2) |
| `census_double.csv` | 6219918 | the double-precision run: the same columns without defensibility, so that the two runs can be compared strategy by strategy |
| `passes.csv` | 126067 | 4096 rows, one per program, pass and stripe of 512: what the programs printed on stderr (chains solved, the smallest nonzero \|w_DC − w_CD\|, the largest integer met) |
| `m2_masks.npz` | 5556 | the six boolean masks `effCC`, `effALT`, `rivP`, `rivM`, `defP`, `defM` of `census.csv`, under the names and in the format of the file the figure scripts read. They are bit-identical to the masks of the first computation, 2026-09-03 |

Each CSV starts with `#` comment lines that describe every column, then one header line; it is read by
`common.tables.read_table`, or by `census/censuslib.load()`, which also returns the boolean masks.

## Columns of census.csv (and census_double.csv)

A strategy's `code` has bit j = 1 when it cooperates at state j = 4·(most recent outcome) + (the outcome before),
with the outcomes CC=0, CD=1, DC=2, DD=3 written own action first. ALLC = 65535 and ALLD = 0. The paper's genome is
`format(code, '016b')[::-1]`.

| column | meaning |
|---|---|
| `code` | the strategy, 0..65535 |
| `w_CC, w_CD, w_DC, w_DD` | limiting self-play frequencies of the four outcomes. In the exact run these are exact rationals printed as the nearest double |
| `eff_cc` | w_CC = 1: a mutual cooperator, efficient below the switch line u+v = 1 (7639) |
| `eff_alt` | w = (0, ½, ½, 0): an alternator, efficient above the switch line (3072) |
| `eff_line` | w_DD = 0: efficient on the switch line (14757) |
| `beat_p` | the lowest co-player τ with w_CD > w_DC (σ outperformed when T>S), or −1 for none |
| `riv_p` | `beat_p` = −1: a rival wherever T>S, u − v < 1 (2640) |
| `beat_m`, `riv_m` | the same for T<S, with w_DC > w_CD (2640, the mirror images) |
| `def_p`, `def_m` | defensible for T>S and for T<S: no negative cycle in the strategy's graph (2144 each), `census.csv` only |
| `ne_self` | π(σ,σ) at (u,v) = (−2,2), (R,S,T,P) = (1,−2,3,0) |
| `ne_maxpay` | the largest π(τ,σ) met. The scan over τ stops once this exceeds E_max = 1, so for a stable σ it is the maximum over all 65536 co-players |
| `ne_beat` | the lowest τ with π(τ,σ) > π(σ,σ), or −1 for none |
| `nash` | stability: `ne_beat` = −1, a symmetric Nash equilibrium at (−2,2) against every memory-two co-player (672) |
| `ne_ntie` | the co-players met with π(τ,σ) = π(σ,σ); this counts all of them when `nash` = 1 |
| `ne_tieviol` | 1 if one of those co-players has π(σ,τ) < π(σ,σ), so that the tie clause fails |
| `tie_ok` | `nash` = 1 and `ne_tieviol` = 0 (8 among the 187 partners, the eight friendly rivals of W) |

The 0/1 columns are the decisions exactly as `compare.py` reads them from the raw outputs. For a strategy that is not
stable, `ne_ntie` and `ne_tieviol` cover only the co-players scanned before the scan stopped.

## Checks

`python3 ../../census/check.py` compares the two runs decision by decision (0 differences in every pass). It also
compares `m2_masks.npz` with `census.csv`, recomputes every census count of SI §6 against the paper, and compares the
672 stable strategies at (−2,2) with the exact stability regions of `../arrangement/`, strategy by strategy (the same 672); the
output ends in `ALL AGREE`. The folders `families/`, `SITable2/`, `SITable3/` and `SITable4/` read `census.csv`; `SITable5/` uses it
for a consistency check of the arrangement.
