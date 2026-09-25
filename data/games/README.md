# data/games — the 512 sampled games and their cells on the disk

The Wright–Fisher maps of the paper (Figures 4 and 5, SI Figures 2–4 and 6–12) are drawn on 512 games, the points of
a Fermat (sunflower) spiral on the disk of games, one game per Voronoi cell. This folder holds the games and the
cells; `common/games.py` reads them (see `common/README.md`).

| file | rows | what |
|---|---|---|
| `games.csv` | 512 | one row per game, in ipt order 0..511: ids, the game (u, v) exactly, Emax, region, disk point, cell area |
| `cells.csv` | 3101 | the vertices of the 512 Voronoi cells on the unit disk (5 to 8 per cell) |

Both files start with `#` comment lines that describe every column, followed by a header line and comma-separated
values. Floats are written with Python's `repr`, which reads back as the identical double.

## The games

Payoffs (R, S, T, P) = (1, u, 1 + v, 0). The disk point of a game is (u, v)/sqrt(16 + u² + v²); the spiral is
ρ_i = ρ_max sqrt((i − 1/2)/512), θ_i = 2π i/φ² on the disk (i = ipt + 1, φ the golden ratio, ρ_max ≈ 0.995). Every
point was then snapped to the 1/1024 grid in the plane and moved off every line of the exact arrangement of the stability regions, so no
game lies on a tie. Every u and v is therefore an exact
multiple of 2⁻¹⁰ (the columns `u1024`, `v1024` give 1024u and 1024v as integers), exact both as a decimal and as a double.
|(u, v)| runs from 0.124 to 38.16, and the cells cover the whole disk. By quadrant the games are split PD 129, SD 127,
SH 128, HA 128; by wedge W 179, S 126, N 121, E 86.

Identifiers: `ipt` (0..511) is the index of the point on the spiral and the order of every per-game array in this
repository. `gid = 2000 + ipt` is the game id in the simulator's `games.dat` and in every packed run (`.idx`, `.win`,
`.rep`). `ig = 456 + ipt` is the game's 1-based row in the 967-row `games.dat` of the memory-two kits, whose task index
is `isl = 3(ig − 1) + ie`. `tag = V_pNNN_QQW` combines ipt, the quadrant (PD, SD, SH, HA) and the wedge
(W, S, N, E); the regions are defined in `common/atoms.py`.

Provenance: the points are BinM2Ev kit ca6's `points.txt` (columns ipt, u, v), which DiskM2WF copied verbatim as
`Ref/binm2ev_ca6_points.txt`. These two runs use the same games as the companion project's ca6 run, so their maps can
be overlaid cell for cell.

## The cells

A cell is the Voronoi region of its game's disk point. The diagram is built from the 512 points, their 512 inversions
in the unit circle (which bound the outer cells) and 32 far points on the circle of radius 3. Each region is then
clipped to the unit circle with Sutherland–Hodgman against a circumscribed 64-gon, and the cut vertices are pushed
back onto the circle. This is the algorithm of DiskM2WF `Opt/vor.py`, `cells()`, reproduced in
`common.games.compute_cells`. Each cell's vertices are listed in cyclic order, but the orientation is not the same for
all cells. The cells tile the disk except for the thin slivers the 64-gon leaves at the rim: their total area is
3.13972, 99.940% of π.

## Checks (run 2026-09-24)

- `ipt`, `u` and `v` are bit-identical to DiskM2WF `vor.points()`. `x` and `y` are bit-identical to `vor.xy()`.
  `cells.csv` is bit-identical to `vor.cells()`, and to `wfdata.cells()` of the figure scripts, for all 3101
  vertices.
- `gid`, `tag`, `cS = u` and `cT = 1 + v` agree bit for bit with rows 456–967 of the `games.dat` read by every
  memory-two kit (dw1, dw2, dw3, dw4, eh, el, c1–c4, f1, f2, lm, all byte-identical), with the 512-row `games.dat` of
  the memory-one kit (mw), and with the sunflower rows of all 17 packed runs (`dw1_e4` … `lm_g05_e4.idx`). They also
  agree with the (u, v) that the four main runs' loaders return (`wfdata.load`, memory one and memory two, N = 100 and
  1000).
- `python3 -m common` (run from the repository root) re-reads both files, checks that the tags, quadrants,
  wedges, Emax and areas are consistent, and recomputes the cells from the points with scipy. With scipy 1.10.0 the
  recomputed cells are bit-identical to `cells.csv`; another Qhull may order or round the vertices differently.
