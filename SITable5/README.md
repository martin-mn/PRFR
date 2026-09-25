# SITable5 — where the four atoms that can be empty at memory two have members

This folder reproduces SI Table 5 (SI §8). The switch line, T = S and the two axes cut the plane into ten pieces
(wedge × quadrant). For each piece and each of the atoms 100, 010, 011 and 110, the table says whether the atom has
members among the binary memory-two strategies on all, part or none of the piece.

    python3 sitable5.py          (about 1 s; numpy)

**Input.** The exact ε→0 arrangement in `../data/arrangement/`. That folder belongs to the arrangement deposit, and
this script only reads it. It uses three files:
- `m2_faces.csv`: per face, an interior game (u, v) and the seven atom counts `A_000 … A_111`;
- `m2_faces_k4.npz`: the face polygons;
- `m2_strategies.csv`: the columns `eff_cc`, `eff_alt`, `riv_plus`, `riv_minus` and `open_xyz`.

It also reads `../data/census/census.csv` for the consistency checks. If the arrangement files are renamed, change
the three names at the top of the script.

**Output.** The table printed next to the paper's, and `SITable5.csv`, which adds the number of polygons of the drawing per piece (`m2_faces.csv`; see `../data/arrangement/README.md`). The
exit status is 1 on any mismatch.

**Method.** Each face is assigned to its piece by its interior game. The script first asserts, vertex by vertex, that
no face straddles one of the four lines, or one of the six lines that bound the bays of 110 used below. An entry is
"all" if the atom is non-empty on every face of the piece, "none" if on no face, and "part" otherwise.

The script also checks that the arrangement agrees with the census. On every face the efficient atoms hold 7639 or
3072 strategies, the competitive atoms 2640, and 111 the friendly rivals of the face's wedge; the census columns of
`m2_strategies.csv` equal those of `data/census`.

Then it checks the text of SI §8:
- 000, 001 and 111 have members at every game;
- ten combinations of empty atoms occur, none with 100 and 110 both empty;
- 100 is empty exactly on u ≤ 1, v ≤ 0;
- 011 is empty on S and on the Snowdrift quadrant above the switch line; there are 1519 stable rivals on S, and no
  inefficient equilibrium on the 557 faces of E∩SD;
- the two bays of 110 are exactly the stated polygons, and beyond the three PD lines the only partners are the 8 or
  the 80 friendly rivals;
- 010 has members on the whole Stag Hunt quadrant and on the two triangles of W with u > 0;
- the totals on an open set, 10701, 1721, 9389 and 16013, and the ranges per game.

**Not checked here**, because each needs the set of stable strategies of a face and not only its counts:
- the 843 witnesses of 010 in the Stag Hunt above T = S;
- the 96 and 10 alternator witnesses in the two triangles of W.

**Verification (2026-09-24).** The script was run from a fresh copy against the arrangement as deposited on that
date. All ten rows agree with SI Table 5 of ms.tex, which was parsed directly, and so does every text check.
