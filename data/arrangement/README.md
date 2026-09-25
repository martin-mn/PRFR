# data/arrangement: the exact ε → 0 arrangements behind Figures 1, 2 and 3

Figures 1–3 classify every binary strategy at every game in the limit ε → 0. A strategy is efficient, stable or
competitive (or any combination) at a game, and the combination is its atom. These classifications are constant on
the faces of an arrangement of lines in the plane of games (u, v), with payoffs (R, S, T, P) = (1, u, 1 + v, 0).
This folder holds the two arrangements exactly. The memory-two one has 65536 strategies and uses the stability regions of the
companion work (NEmap). The memory-one one has 16 strategies and is computed here from scratch. The folder also has
the code that checks both arrangements and recovers the paper's counts.

The memory-two arrangement has 22872 faces, on each of which the set of stable strategies is constant (`m2_cells.csv`).
The companion work draws them as 27598 polygons (`m2_faces.csv`, `m2_faces_k4.npz`), and Figures 1c, 2h–n and 3e–h
draw the same polygons. The set of stable strategies of a face is not stored as a list. It follows exactly from
two things that are stored: the exact stability region of every strategy, a polygon, and the side of every line on which each face lies
(see below). The tables call the 22872 faces *cells* and the 27598 polygons *faces*, the names of the companion
drawing.

## Files

| file | rows | bytes | what |
|---|---:|---:|---|
| `m2_strategies.csv` | 65536 | 3234577 | per memory-two strategy: genome, efficiency, rivalry, dimension of its stability region, the atoms it is in somewhere |
| `m2_nash_facets.csv` | 53580 | 918645 | the stability regions of the 23861 strategies whose region has an interior, as polygons, one row per facet |
| `m2_nash_lowdim.csv` | 8649 | 261915 | the stability regions of measure zero: 3774 segments or rays, 4875 single games |
| `m2_lines.csv` | 254 | 4447 | the lines that carry a facet of some polygon |
| `m2_cells.csv` | 22872 | 1659064 | the faces of the arrangement of those lines, each as its sign vector |
| `m2_faces.csv` | 27598 | 2609335 | the polygons drawn in Figures 1c, 2h–n and 3e–h: their cell, an interior game, the counts, the atoms, the case |
| `m2_faces_k4.npz` | 27598 | 2026062 | the same polygons on the disk (K = 4), as float64 vertices |
| `m1_faces.csv` | 45 | 6673 | the memory-one faces: an interior game, the areas, the atoms, the case, and the atom of each of the 16 strategies |
| `m1_faces_k4.npz` | 45 | 148563 | the same faces on the disk |
| `m1_lines.csv` | 11 | 275 | the lines of the memory-one arrangement |
| `cases.csv` | 19 | 1540 | the 19 cases of Figure 1 |
| `arrangement.py` | | 3933 | the loader used by the figure scripts and the checker |
| `check.py` | | 13895 | the checker (below) |
| `m1atoms.py` | | 20702 | the exact memory-one computation. It rebuilds `m1_*` and compares |

Every table starts with `#` comment lines that describe every column, then a header line, then comma-separated values.
Floats are Python `repr`s, which read back as the identical doubles. `common.tables.read_table` reads every table.
Atom columns are named `A_000 … A_111` in the order 000, 100, 010, 001, 110, 011, 111. An atom is written
efficient–stable–competitive. Atom 101 is empty everywhere, so the seven counts add up to the number of strategies.

## Memory two

**Strategies.** `genotype` is the integer code Σ_j c_j 2^j. `genome` is the sixteen answers c_0 … c_15 (1 = C) at
the states j = 4 (most recent outcome) + (the outcome before), with CC = 0, CD = 1, DC = 2, DD = 3. ALLC is 65535,
ALLD is 0. These are the Methods' conventions. The other columns:

- `eff_cc`: the strategy's limiting self-play is permanent mutual cooperation. It is efficient where u + v < 1.
- `eff_alt`: the self-play is perfect alternation. It is efficient where u + v > 1.
- `riv_plus`, `riv_minus`: the strategy is a rival where T > S, respectively T < S. A rival is competitive: no
  memory-two co-player outearns it.

These four columns are computed in this paper, by the census program `census/pairs.c`; they are the masks
`effCC`, `effALT`, `rivP` and `rivM` of `data/census/m2_masks.npz`. `eff_cc` and `eff_alt` also agree with the
self-play distributions of NEmap's exact census.

**Stability regions.** For each strategy, NEmap found the set of games at which it is a Nash equilibrium in the limit
ε → 0, its stability region. The files and columns named `nash` (`m2_nash_facets.csv`, `m2_nash_lowdim.csv`,
`nash_dim` and `nash_nfacets` of `m2_strategies.csv`, `nash` of `m2_faces.csv`) hold this property, stability: a
symmetric Nash equilibrium against a single deviant.
It is tested against all 65535 other memory-two strategies, with ties admitted. The census is exact: it uses the Markov
chain tree theorem in integer arithmetic (MapBinM2, `exact/ca1_regions.csv`). The set is a convex polygon given by
integer inequalities a + b u + c v ≤ 0 (`m2_nash_facets.csv`). A set of measure zero is a segment or ray of one line, or
a single game (`m2_nash_lowdim.csv`). A set can also be empty. `nash_dim` in `m2_strategies.csv` is 2, 1, 0 or −1
accordingly, for 23861, 3774, 4875 and 33026 strategies.

**Lines and cells.** The facets lie on 254 distinct lines, A u + B v = C (`m2_lines.csv`, in lowest terms).
The lines include the switch line u + v = 1 and the line T = S, u − v = 1. They cut the whole plane into exactly 22872
open cells. All 18359 intersection points lie within |u|, |v| ≤ 171. A cell is recorded as its sign vector (`sides`
in `m2_cells.csv`): bit j is 1 if A_j u + B_j v > C_j on the cell. Each facet row carries its `line` and the `bit` on
whose side it holds strictly. So, exactly and without any arithmetic on coordinates:

```
g is stable on cell k   <=>   nash_dim[g] == 2  and  (int(sides[k], 16) >> line) & 1 == bit  for every facet row of g
```

The atom of g on the cell is 4e + 2n + c. Here n is the stability bit above. e is `eff_cc` below the switch line and
`eff_alt` above it. c is `riv_plus` where u − v < 1 and `riv_minus` where u − v > 1. The two sides come from the cell's
bits of the lines `switch` and `TeqS`. The 22872 cells carry 4286 distinct sets of stable strategies.

**Polygons.** The companion work's drawing of this arrangement has 27598 polygons: `ca4_arrangement_k4.npz`, which is
MapBinM2 `Figure3/ca4_arrangement_k4.npz`. There are more polygons than the 22872 cells because MapBinM2's
`p3disk.py` cut 771 of the cells into bands for a mean-efficiency field that the companion paper draws. Every count
here is constant on a cell, so a band carries its cell's numbers. Figures 1c, 2 and 3 draw these 27598 polygons. They are the faces of
`m2_faces.csv`, whose `cell` column names the cell of each. `m2_faces_k4.npz` holds them on the disk
(u, v) → (u, v)/sqrt(16 + u² + v²), in the format of `common.geometry`: `verts` (252238 × 2), `offsets` (27599), `K`.
Face i is `verts[offsets[i]:offsets[i + 1]]`. `u`, `v` in `m2_faces.csv` is a game strictly inside the face.
It is the one at which the atoms were first evaluated (`count6.py`, with DiskM2WF `exact.masks`).

**Cases.** A case is the set of atoms that are non-empty at a game. `cases.csv` lists the 19 cases of both
memories with their numbers in Figure 1. The `case` columns of the face tables give each face's case.

## Memory one

The 16 binary memory-one strategies are written by their answers after CC, CD, DC, DD, own action first. So ALLC is
CCCC, ALLD DDDD, TFT CDCD, WSLS CDDC and Grim CDDD. `m1atoms.py` computes every pair's limiting distribution in
rational arithmetic, by the Markov chain tree theorem. From these it finds the lines across which some strategy's
atom changes. There are 11: u = −1, −½, 0, ½, 1; v = −1, −½, 0, 1; the switch line; and T = S (`m1_lines.csv`).
They cut the plane into exactly 45 faces. The script classifies each face at two interior rational games, which must
agree. It maps the faces onto the disk with the adaptive conic subdivision of `common.disk.arc`. `m1_faces.csv` gives,
per face, the atom code (0–7) of each of the 16 strategies (columns `code_XXXX`) and their tallies `A_*`.

## Checks

```
python3 check.py        # about 8 s
python3 m1atoms.py m2   # about 7 s
```

**`check.py`** reads only this folder. For memory two it:

- rebuilds the set of stable strategies, the partner set and the seven atom counts of every face, in integer arithmetic, from
  the lines, the cell signs, the facets and the four masks, and compares them with `m2_faces.csv`;
- checks that the 254 lines give exactly 22872 cells, and that the 27598 polygons are bands of them;
- checks that every drawn vertex, mapped back to the plane, lies on its cell's side of all 254 lines, up to a relative
  2.3e-13, and that every recorded interior game does;
- prints and asserts the numbers of the Methods and SI §6 (Nash equilibria and partners). 23861 strategies are stable on an open set of games and 9431
  are partners there. Between 299 and 22069 strategies are stable at a game in the interior of a face, and between 8 and
  7639 are partners;
- checks two regions. There are 7639 partners, and atom 100 is empty, exactly on the cells with u < 1, v < 0. Where
  there are only 8 partners, they are the 8 friendly rivals of W, in the Prisoner's Dilemma;
- prints the atom totals of SI §8 (000 65486, 100 10701, 010 16013, 001 5230, 110 9389, 011 1721, 111 1677) and their
  per-game ranges;
- checks that the Snowdrift part of wedge E has 557 faces and no inefficient stable strategy on any of them (SI §8);
- checks the ten memory-two cases.

For memory one it checks:

- the tallies of the 16 codes, and the twelve cases, of which 7, 11 and 13 are shared with memory two;
- the 45 faces of the 11 lines, and the numbering of the 19 cases;
- that the 3 mutual cooperators are all partners exactly where u < 1, v < 0 (legend of Figure 3);
- that every strategy but tit-for-tat is in 000 somewhere (legend of Figure 2);
- that 8 strategies are stable on an open set, 0 to 8 at a game, and that in the Snowdrift quadrant the only one is
  WSLS, on the unit square (SI §10).

In all, the checker makes 32 checks.

**`m1atoms.py`** rebuilds the memory-one arrangement from nothing and checks that it equals the deposited `m1_*` files
bit for bit: vertices, codes, interior games, areas and lines. With `m2`, it also decides the three properties of the
16 against all 65536 memory-two co-players. For that it uses this folder's memory-two layer, evaluated exactly at each
face's rational interior game. The results agree with the memory-one classification on all 45 faces.

Both were run on 2026-09-24 and pass.

**`../../census/check.py`** also reads this folder. It evaluates the exact stability region of every memory-two strategy at
the one game the census tests, (u, v) = (−2, 2), and finds the census's 672 stable strategies there, strategy by
strategy. It also checks that `eff_cc`, `eff_alt`, `riv_plus` and `riv_minus` equal the census columns.

## Loading

`arrangement.py` returns the arrays in the shapes the original figure scripts used. It depends on numpy and
`common.tables` only.

```python
import os, sys
sys.path.insert(0, "<repository root>/data/arrangement")
import arrangement
D2 = arrangement.m2()      # faces (list of 27598 disk polygons), atoms (27598, 8) by code, atom_total, ne_total, cell, uvc, ...
D1 = arrangement.m1()      # faces, diskarea, uvc, codes (45, 16), atoms (45, 8), lines, ...
S2 = arrangement.m2_strategies()
```

## Provenance

`../../provenance/census-figs/reduce.py` wrote every file here from the author's working files. The sources:

- the companion arrangement `ca4_arrangement_k4.npz`;
- the per-face atom counts `Count6_faces.npz` of `PartnersRivals/Figures/count6.py`;
- `m2_masks.npz`;
- NEmap's `ca1_regions.csv`;
- the memory-one cache `m1_atoms_k4.npz` of `FinalFigures/m1atoms.py`.

Before writing, the script recomputed every per-face number from the combinatorial description above. It asserted
that each equals the companion dump's `N` and `NEFF` and Count6's `ATOMS`. Running the script again gives the same
files byte for byte.
