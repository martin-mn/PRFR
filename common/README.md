# common — shared code of the figure folders

The pieces that several display items share, taken from the original figure scripts
(`FinalFigures/atomshares.py`, `atomcounts.py`, `eulerlib.py`, `fig4.py`, `m1atoms.py`, `wfdata.py`, `wfrep.py`,
`PartnersRivals/Figures/disklib.py`, `DiskM2WF/Opt/vor.py`, `disk.py`). The code is moved unchanged. Only the data
loading was replaced, and the output path became an argument. The package covers:

- the 512 sampled games, their Voronoi cells and their ids;
- the disk map, and the drawing of the special lines and of the rim names;
- the atom order, names and colours;
- the frame of a disk panel, the count scale and panel, and the Figure 4 sheet;
- the pre-save text checks and a CSV table format.

Requirements: Python 3, numpy and matplotlib. scipy is needed only by `games.compute_cells`. The published figures
were rendered with Python 3.10.9, numpy 1.23.5, matplotlib 3.7.0 and scipy 1.10.0, using matplotlib's bundled
DejaVu Sans. With these versions the figures redrawn through this package are pixel-identical to the published PDFs
(see Verification). Other matplotlib versions may differ in antialiasing and text placement.

## Importing

From a folder next to `common/` (e.g. `Figure4/fig4.py`):

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from common import games, disk, atoms, style, geometry, tables    # side-effect free
from common import furniture, counts, wfsheet, checks             # drawing modules, see the warning below
```

**Side effects.** Importing `common.furniture` does two things, exactly as the original `atomshares.py` and
`atomcounts.py` did when imported: it calls `matplotlib.use("Agg")`, and it sets
`matplotlib.rcParams.update(furniture.RC)`, where
`RC = {"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 15, "axes.linewidth": 1.2}`. `common.counts` and
`common.wfsheet` import `furniture`, so they have the same effect. Import it before you create a figure.

Figure 1 never imported these modules; it sets its own rcParams (`pdf.fonttype 42`, `ps.fonttype 42`,
`font.family sans-serif`). A Figure 1 script should therefore import only the side-effect-free modules: `games`,
`disk`, `atoms`, `style`, `geometry` and `tables`. Importing `common` itself, which runs `__init__`, imports only
those modules.

`common/__init__.py` re-exports these names: `atoms disk games geometry style tables IDX NAME ORDER PROPS K phi to_disk
cell_areas cells cells_keep index_of uv xy polyarea unpack_faces GREY TINT WINCOL`.

## Conventions used everywhere

- **Game.** A game is (R, S, T, P) = (1, u, 1 + v, 0).
- **Game order.** Every per-game array has shape (512, ...) and is in **ipt order** 0..511. The packed runs of the
  simulator name a game by `gid = 2000 + ipt`, or by the tag `V_pNNN_QQW` with NNN = ipt.
- **Atom code.** An atom is written as the string efficient-stable-competitive and stored as the integer
  `4*efficient + 2*stable + competitive`.
- **ORDER.** `ORDER = ["000","100","010","001","110","011","111"]` is the order of the atoms in every figure and in
  every (n, 7) array. `IDX = [0, 4, 2, 1, 6, 3, 7]` gives their integer codes, so `A8[:, IDX]` turns an (n, 8) array
  indexed by code into ORDER. Code 5 (`101`) is empty at every game.
- **Units.** Disk coordinates are data units on the unit disk. Layout constants are in inches, font sizes in
  points.

---

## common.games — the 512 games and their cells (data in `../data/games/`)

| name | signature | returns |
|---|---|---|
| `NGAME, GID0, IG0` | constants | `512`, `2000`, `456`: `gid = GID0 + ipt`; `ig = IG0 + ipt` is the 1-based row in the 967-row `games.dat` of the memory-two kits |
| `DATA, GAMES_CSV, CELLS_CSV` | constants | absolute paths of `data/games/`, `games.csv`, `cells.csv` |
| `games()` | `()` | dict of (512,) arrays, cached: `ipt, gid, ig, u1024, v1024` int64; `u, v, emax, x, y, cell_area` float64; `tag, quadrant, wedge` str |
| `uv()` | `()` | (512, 2) float64 `(u, v)`. Bit-identical to the `UV` of `wfdata.load`, `wfrep.load` and `sifig8.load_idx` |
| `xy()` | `()` | (512, 2) float64: the disk points, `to_disk(u, v)` (= `vor.xy()`) |
| `emax()` | `()` | (512,) float64 `max(1, (1 + u + v)/2)`, exact |
| `tags()` | `()` | (512,) str `V_pNNN_QQW` |
| `index_of(tag)` | `(str)` | `int` ipt for a tag `V_p...`, else `None` (= `vor.index_of`) |
| `ipt_of_gid(gid)` | `(int)` | `gid - 2000`; raises `ValueError` outside 2000..2511 |
| `cells()` | `()` | list of 512 float64 arrays of shape (n_i, 2), n_i = 5..8, in ipt order: the Voronoi cells on the unit disk. Bit-identical to `vor.cells()`. The vertices are in cyclic order; the orientation varies |
| `cells_keep()` | `()` | `(pol, keep)`, a drop-in for `wfdata.cells()`: `pol` is the list of cells with at least 3 vertices, `keep` their ipt list. All 512 cells qualify, so `keep == list(range(512))` |
| `cell_areas()` | `()` | (512,) float64: `polyarea` of each cell (disk units²; the total is 3.13972) |
| `clip_disk(poly, nseg=64)` | `((n,2) array, int)` | the polygon clipped to the unit circle (= `vor.clip_disk`) |
| `compute_cells(p=None)` | `((512,2) array or None)` | recomputes the cells from the disk points (default `xy()`) with `scipy.spatial.Voronoi` (= `vor.cells`) |
| `selftest()` | `()` | prints and asserts. Also run as `python3 -m common` from the repository root |

The columns of `games.csv` are described in its own header and in `data/games/README.md`. Their meanings:

- `quadrant`: `PD` (u < 0 < v), `SD` (u, v > 0), `SH` (u, v < 0), `HA` (v < 0 < u).
- `wedge`: `W` (u+v < 1, u−v < 1), `S` (u+v < 1, u−v > 1), `N` (u+v > 1, u−v < 1), `E` (u+v > 1, u−v > 1).

## common.disk — the map, the special lines, the rim names

K = 4. The map is (u, v) → (u, v)/sqrt(K² + u² + v²) onto the open unit disk. Two implementations are kept, because
the originals used both and they can differ in the last bit of a double:

- `to_disk` gives the sunflower points and hence the cells.
- `phi` gives every line and every face drawn on the disk.

| name | signature | returns / does |
|---|---|---|
| `K, RB` | constants | `4.0`; `2000.0` (lines are cut at \|t\| = RB) |
| `to_disk(u, v, k=K)` | arrays of any shape | `(x, y)` float arrays (DiskM2WF `disk.to_disk`) |
| `from_disk(x, y, k=K)` | arrays | `(u, v)`, the inverse |
| `phi(p, k=K)` | `p` of shape (n, 2) or (2,) | (n, 2) disk points (disklib `phi`) |
| `plane(q, k=K)` | (n, 2) disk points | (n, 2) games, the inverse of `phi`; 1 − r² is clamped at 1e-12 (fig1 `plane`) |
| `arc(A, B, f=phi, tol=1e-5)` | two plane points | list of disk points along the image of segment A–B, within `tol` of the true conic, B excluded (disklib `arc`) |
| `conic(a, b, c, f=phi, rb=RB, arms=(-1, 1), npt=20000)` | a line a·u + b·v = c | list with one (npt, 2) disk polyline per arm (disklib `conic`). `arms=(1,)` gives a half-line |
| `SWITCH, TEQS, DONATION` | `(1,1,1)`, `(1,-1,1)`, `(1,1,0)` | (a, b, c) of the switch line u + v = 1, of T = S (u − v = 1), and of the donation line u + v = 0 (drawn only as the half-line u < 0 < v) |
| `CONICS` | list | `[(polyline (20000, 2), colour, dash)]`, five entries: switch line `"crimson"` `(0,(7,4))`, two arms; T = S `"white"` `(0,(7,4))`, two arms; donation `"#12d7e8"` `(0,(8,3,1.5,3))`, one arm. Identical to `atomshares.CONICS` and `atomcounts.CONICS` |
| `draw_conics(ax, halo=True, lw=1.5, zorder=7)` | axes | draws `CONICS`. `halo=True` adds a 2.7-pt `"0.35"` stroke under the white T = S line, as on the sunflower maps. `halo=False` draws it without, as on the count maps of Figures 2 and 3 |
| `euler_lines()` | `()` | `(sw, ts)`, each (40001, 2): the switch line and T = S, sampled at t ∈ linspace(−2000, 2000, 40001), as Figure 1 b, c draws them (eulerlib `draw_map`) |
| `draw_euler_lines(ax)` | axes | Figure 1's lines: switch line `"crimson"` lw 1.1; T = S `"0.10"` lw 0.9, `ls=(0,(3,2))`; zorder 8 |
| `NAMES` | tuple | `((45,"Snowdrift"), (135,"Prisoner's Dilemma"), (225,"Stag Hunt"), (315,"Harmony"))`: angles in degrees |
| `NM_FS, NM_TRK, NM_GAP` | constants | `42.0` pt (the base size, scaled by each sheet), `0.09` em of tracking, `0.028` radii of gap |
| `advances(s, fp, fontsize, tracking)` | str, FontProperties, pt, em | list of per-character pen advances in pt, kerned (disklib) |
| `arc_text(ax, s, theta_c, r_in, fontsize, dpu, gap, tracking, color="0.10", zorder=12)` | `theta_c` in degrees, `dpu` in data units per pt | sets `s` on an arc outside `r_in` as PathPatches. Returns `(theta_lo, theta_hi, r_outer)` in degrees and data units (disklib `arc_text`). Typical call: `arc_text(ax, name, angle, 1.0, furniture.NM_FS, furniture.DPU, disk.NM_GAP, disk.NM_TRK)` |

## common.atoms — atom codes, properties, regions

| name | value / signature | notes |
|---|---|---|
| `ORDER` | `["000","100","010","001","110","011","111"]` | |
| `IDX` | `[0, 4, 2, 1, 6, 3, 7]` | the integer code of each atom in `ORDER` |
| `CODE` | `np.array(["000","001",...,"111"])` | integer code → string (eulerlib `CODE`) |
| `NAME` | dict | `000` "none of the three", `100` "efficient only", `010` "stable only", `001` "competitive only", `110` "efficient and stable only", `011` "stable and competitive only", `111` "efficient, stable and competitive" (the heads of the atom panels) |
| `EMPTY` | `5` | the code of 101 |
| `PROPS` | list | `[("efficient","1**",["100","110","111"]), ("stable","*1*",["010","110","011","111"]), ("competitive","**1",["001","011","111"])]` (fig5 `PROPS`) |
| `PARTNERS` | tuple | `("efficient and stable: partners", "11*", ["110","111"])` |
| `code(e, n, c)` | bool arrays or scalars | int64 `4e + 2n + c` |
| `to_order(A8)` | (..., 8) array | (..., 7) array in ORDER; asserts that column 101 is zero |
| `members(atoms)` | list of atom strings | their ORDER indices, e.g. `members(PROPS[0][2]) == [1, 4, 6]` |
| `pieces(uv)` | (n, 2) array | `(quadrant, wedge)` str arrays (= `m1atoms.pieces`, with its tie-breaking: u = 0 or v = 0 goes to HA) |
| `emax(u, v)` | arrays | `max(1, (1 + u + v)/2)` |

Figure 3's `SETS` used integer codes, e.g. efficient = `[4, 6, 7]`. The same sets are
`[IDX[i] for i in members(PROPS[0][2])]`.

## common.style — colours

| name | value |
|---|---|
| `WINCOL` | `{"000":"0.36", "100":"#8fb8e8", "010":"#dba622", "001":"#f0a48c", "110":"#2f5fb3", "011":"#c43d3b", "111":"#7a4fa8"}`: the atom colours of every "most abundant / most enriched atom" map and its swatch legend |
| `TINT` | `{"000":"white", "100":"#d2dff5", "001":"#f8d7d3", "010":"#e6e6e6", "110":"#b9c8ea", "011":"#ebbcbc", "111":"#cbbbe6"}`: Figure 1's atom tints. Figure 1's key uses `"white"` for 000 |
| `COL_E, COL_C, COL_N` | `"#1f4e9c"`, `"#b3232b"`, `"0.10"`: Figure 1's efficient circle, competitive circle and the dashed curve of the stable strategies |
| `GREY` | `"0.84"`: a cell or face where the atom or property has no strategy at the game |
| `SHARE_NORM, EFF_NORM` | `Normalize(0, 1)` |
| `SHARE_CMAP()` | a fresh copy of viridis (the share maps) |
| `EFF_CMAP()` | a copy of viridis with under-colour `"black"` (efficiency < 0), the same as `wfsheet.ECMAP` |

The count maps use magma (`counts.atom_scale`). Figure 1's nineteen case colours are used only by Figure 1 and are
not included here.

## common.geometry — polygons and packed faces

| name | signature | returns |
|---|---|---|
| `polyarea(p)` | (n, 2) array | float `0.5*abs(x·roll(y,−1) − y·roll(x,−1))`, bit-for-bit the formula of `eulerlib.polyarea` and figstrict's cell areas |
| `unpack_faces(verts, offsets)` | (V, 2), (F+1,) | list of F polygons `verts[offsets[i]:offsets[i+1]]`: the format of `ca4_arrangement_k4.npz` and `m1_atoms_k4.npz` |
| `pack_faces(faces)` | list | `(verts (V,2), offsets (F+1,) int64)` |

## common.tables — deposited CSV tables

Every table has `#` comment lines, then a header line of column names, then comma-separated rows. Floats are
written with `repr()`, which round-trips exactly.

| name | signature | returns / does |
|---|---|---|
| `write_table(path, columns, comments=())` | `columns`: ordered dict name → sequence (all one length); `comments`: list of lines or one string | writes the table. ints as ints, bools as 1/0, floats by `repr`, strings as they are (no commas, quotes or newlines) |
| `read_table(path)` | | dict name → (n,) numpy array. A column is int64 if every entry parses as an int, else float64 if every entry parses as a float (`nan`/`inf` allowed), else str |
| `comments(path)` | | the header comment lines, without `# ` |
| `atom_columns(prefix, A)` | `A` of shape (n, 7) in ORDER | `{"<prefix>_000": A[:,0], ..., "<prefix>_111": A[:,6]}` |
| `atom_array(table, prefix)` | a `read_table` dict | the (n, 7) array in ORDER |

Suggested column names for per-game run tables, so that every folder reads the same run the same way: `ipt`; the
atom shares `S_000 … S_111`; the strategies per atom `N_000 … N_111`; the efficiency `E`.

## common.furniture — the frame of a disk panel (imports Agg and sets RC)

These are the layout constants of `atomshares.py`, in inches unless stated otherwise:

| constant | value |
|---|---|
| `PW` | 4.3 (panel width) |
| `LIM` | 1.175 (data units) |
| `EXTT, EXTB` | 0.22, 0.34 (data units above and below the disk) |
| `PH` | `PW*(2*LIM+EXTT+EXTB)/(2*LIM)` = 5.3247 |
| `COLGAP, ROWGAP` | 0.55, 0.25 |
| `ML, MR, MB, MT` | 0.30, 0.20, 0.25, 0.25 |
| `NCOL, NROW` | 4, 2 |
| `FIG_W, FIG_H` | 19.35, 11.399 (atomshares' eight-panel sheet) |
| `DPU` | `(2*LIM/PW)/72` = 0.00759 data units per pt |
| `SC` | `PW/13.46` |
| `NM_FS` | `42*SC*1.25` = 16.77 pt (rim names) |
| `FS` | `max(9, 13*SC*1.9)*1.45` = 13.05 pt (base font) |
| `GUIDE` | `(1, 2, 4, 10)` |
| `th` | `linspace(0, 2π, 4001)` |
| `PEL, HALO` | path effects |
| `GUIDE_C, GUIDE_LW, GUIDE_A` | `"white"`, 0.6, 0.28 |
| `CBH` | 0.22, the horizontal colour bar height |
| `SW` | `CBH*2*LIM/PW` = 0.1202, the swatch side in data units |
| `LFS` | `FS*0.82` = 10.70 pt |
| `LW` | the width of a bold "000" at `LFS` in data units (0.1618) |
| `PITCH, X0, YL` | 0.3370, −1.1620, −1.2851: the swatch row under a disk, in data units |

| function | signature | does |
|---|---|---|
| `furniture(ax, letter, title, halo=True)` | axes, str, str | draws everything on a disk panel except the cells. That is the two diameters, `CONICS` (with the T = S halo if `halo`), the guide circles at \|u\|, \|v\| = 1, 2, 4, 10 with their ticks and labels, `$u$` and `$v$`, the bold panel `letter` at the top left, the head `title` at the top centre (`""` for none), and the four game names on the rim. It sets xlim (−LIM, LIM), ylim (−(LIM+EXTB), LIM+EXTT), equal aspect and axis off. Draw the cells first, as a `PolyCollection` at zorder 1 with `linewidths=0.3`, edgecolors = facecolors and antialiased; the furniture draws at zorder 5–12. `halo=False` reproduces the count maps (atomcounts), `halo=True` the sunflower maps (atomshares) |
| `disk_legend(ax)` | axes | the seven `WINCOL` swatches with bold codes in one row centred under the disk, at y = `YL`, as under panel h of SI Figures 2 and 3. Returns the 7 code `Text`s |
| `disk_legend_check(ax, legend, renderer)` | | asserts that no code runs into the next swatch. Call it after `fig.canvas.draw()` |

A sunflower map is drawn like this:

```python
pol, keep = games.cells_keep()
fc = [GREY if gap[i] else cmap(norm(val[i])) for i in keep]
ax.add_collection(PolyCollection(pol, facecolors=fc, edgecolors=fc, linewidths=0.3, antialiased=True, zorder=1))
furniture.furniture(ax, "a", "head")
```

## common.counts — count panels (atomcounts.py; imports furniture)

| name | signature | returns / does |
|---|---|---|
| `atom_scale(vals, weights)` | (n,) values, (n,) areas | `(cmap, norm, ticks, labels, discrete)`. If the positive values take a single level: one magma band (0.75). If they take at most 12 levels: `discrete_bands(..., by="rank")`, labelled at every level. Otherwise: `equalised` (an area-weighted equal-area magma ramp of up to 256 bands, which prints `bar atom: ...`). `cmap.set_under(GREY)`, so zero is grey |
| `discrete_bands(vals, weights, cmap="magma", vmin=None, vmax=None, minshare=0.010, group=str, by="value", share=True)` | | `(ListedColormap, BoundaryNorm, ticks, ticklabels, receipt)` (disklib, verbatim) |
| `equalised(vals, weights, cmap="magma", name="")` | | `(ListedColormap, BoundaryNorm, ticks)` |
| `ladder(lo, hi)`, `thin(ticks, norm, nbands, mingap=0.052)`, `grp(x)`, `NB=256` | | helpers of the scale |
| constants | | `PW, LIM, EXTT, EXTB, PH` as in furniture; `CBW` 0.22, `CBGAP` 0.26, `CBLAB` 1.30 (the vertical bar); `COLW = PW+CBGAP+CBW+CBLAB` = 6.08; `COLGAP` 0.30, `ROWGAP` 0.25; `ML, MR, MB, MT` 0.30, 0.20, 0.25, 0.25; `NCOL, NROW` 4, 2; `FIG_W, FIG_H`; `DPU, SC, NM_FS, FS` as in furniture; **`CBH = 0.8*PW` = 3.44, the vertical bar height (not furniture.CBH)**; `ATOM_ORDER = ORDER`; `ATOM_NAME = NAME` |
| `cellxy(row, col)` | | lower-left corner (inches) of a cell of the default 2×4 sheet |
| `sheet(nrow, ncol=4, labw=0.0)` | | `(fig, W, H, xy)`. `xy(row, col)` gives the lower-left corner in inches of a disk; `labw` is a left column for row labels (Figures 2 and 3 use 0.75) |
| `panel(fig, W, H, x, y, FACES, DA, vals, letter, head, sub, barlabel="Number of strategies")` | `FACES`: list of disk polygons; `DA`: (nf,) areas; `vals`: (nf,) counts | one count disk at (x, y) inches, grey where `vals == 0`, `furniture(halo=False)`, the `sub` line under the disk, and the vertical colour bar to its right. Returns `dict(min, max, levels, zshare)` |
| `rowlabel(fig, W, H, x, y, text)` | | a rotated label 0.45 in to the left of the disk at (x, y) |
| `finish(fig, W, H, out)` | `out` a `.pdf` path | text checks (as `check_sheet(xticks=False)`), then saves `out` and `out` with `.png` at 150 dpi, closes the figure and prints the size |

SI Figures 6 and 7 (figstrict) used `atom_scale` and the constants `CBW, CBGAP, CBLAB, CBH` from here.

## common.wfsheet — the Figure 4 sheet (fig4.py; imports furniture)

| name | signature | returns / does |
|---|---|---|
| `ECMAP, ENORM` | | viridis with `"black"` under-colour; `Normalize(0, 1)` |
| `COLS` | | `["efficiency", "most abundant atom", "most enriched atom"]` |
| `LABEL, ROWS` | | the row labels of the four main runs, e.g. `LABEL[("m2","F1")] == "Memory-2, $N = 1000$"`. `ROWS = [("m1","F2"), ("m1","F1"), ("m2","F2"), ("m2","F1")]` (F1: N = 1000, β = 100, μ = 1e-2; F2: N = 100, β = 3, μ = 1e-4; ε = 1e-4; the other names of these runs are listed in `data/runs/README.md`) |
| `winners(S, N, E, D, name)` | `S` (512,7) shares in ORDER; `N` (512,7) strategies per atom; `E` (512,); `D` dict with `N, beta, muplain` | `(wa, we)`, (512,) int ORDER indices of the most abundant atom (argmax of S where N > 0) and of the most enriched atom (argmax of S/N where N > 0). Prints a three-line receipt |
| layout | | `PW, LIM, EXTT` as in furniture; `EXTB = 0.08`; `PH = PW*(2*LIM+EXTT+EXTB)/(2*LIM)` = 4.8489; `ML, MR, MT, MB = 0.95, 0.15, 0.15, 0.20`; `COLGAP, ROWGAP = 0.45, 0.15`; `LEG = 0.80`. These are also the layout of fig5.py, figstrict.py and sifig11.py |
| `draw(rows, out, png_dpi=110)` | `rows = [(label, E, wa, we)]` top to bottom; `out` a `.pdf` path | Figure 4's sheet: three disks per row, letters a, b, c, ... row by row, column heads on the first row only, the efficiency bar under column 1 and the atom legend under columns 2–3. Checks the texts, then writes `out` and `out` with `.png` at `png_dpi`. This is `fig4.draw(rows, stem)` with the stem replaced by the full path |
| `efficiency_bar(fig, FIG_W, FIG_H, x, yleg, label)` | inches | the horizontal efficiency bar, (x + 0.18 PW) to (x + 0.82 PW), centred at height `yleg`, with `label` above it. Returns the colorbar. Used by `draw` and by SI Figure 8 |
| `sheet_legend(fig, FIG_W, FIG_H, xc, yleg, title)` | inches | a full-sheet axes in inches with the seven swatches centred at `xc` and `title` above them. Returns the axes. Used by `draw` and by SI Figure 8 |

Figure 4 and SI Figure 4 (`fig4.py`) and SI Figures 9, 10 and 12 (`sifig9.py`, `sifiglm.py`) call
`draw(rows, out)` after `winners`. SI Figure 8 uses `winners`, `ECMAP`, `ENORM`, `EXTB`, `efficiency_bar` and
`sheet_legend`. SI Figure 11 uses `EXTB`.

## common.checks

| name | signature | does |
|---|---|---|
| `check_sheet(fig, W, H, xticks=True, yticks=True, heads=True)` | W, H in inches | calls `fig.canvas.draw()`, then asserts that every figure text, every non-empty visible axes text and the chosen tick labels of axes with the axis on lie inside the sheet. With `heads`, it also asserts that no two `va="bottom"`, `ha in ("center","left")` texts of one axes overlap. Returns the renderer. The originals: atomshares.py and figstrict.py used the defaults; atomcounts `finish` used `xticks=False`; fig4.py and fig5.py used `yticks=False, heads=False` |

## Mapping from the original modules

| original | here |
|---|---|
| `vor.points()`, `vor.xy()`, `vor.cells()`, `vor.index_of` | `games.games()["ipt"/"u"/"v"]`, `games.xy()`, `games.cells()`, `games.index_of` |
| `wfdata.cells()` | `games.cells_keep()` |
| `disk.to_disk`, `disklib.phi(p, 4)`, `disklib.arc`, `disklib.conic` | `disk.to_disk`, `disk.phi(p)`, `disk.arc`, `disk.conic` |
| `disklib.NAMES, NM_FS, NM_TRK, NM_GAP, advances, arc_text` | `disk.*` |
| `disklib.discrete_bands` | `counts.discrete_bands` |
| `atomshares.ORDER, NAME, WINCOL, GREY, CONICS` | `atoms.ORDER`, `atoms.NAME`, `style.WINCOL`, `style.GREY`, `disk.CONICS` |
| `atomshares.furniture` and layout constants | `furniture.furniture`, `furniture.*` |
| panel h legend of `atomshares.draw` / `draw_runs` | `furniture.disk_legend`, `furniture.disk_legend_check` |
| `atomcounts.*` (atom_scale, sheet, panel, rowlabel, finish, constants) | `counts.*` (the unused `atomcounts.draw` is dropped) |
| `eulerlib.ORDER, CODE, TINT, COL_E, COL_C, COL_N, polyarea` | `atoms.ORDER`, `atoms.CODE`, `style.TINT`, `style.COL_*`, `geometry.polyarea` |
| the two lines in `eulerlib.draw_map` | `disk.draw_euler_lines(ax)` (or `disk.euler_lines()`) |
| `m1atoms.pieces`, `m1atoms.ORDER/NAME` | `atoms.pieces`, `atoms.ORDER/NAME` |
| `fig1.plane` | `disk.plane` |
| `fig4.draw(rows, stem)`, `winners`, `ECMAP`, `ENORM`, layout | `wfsheet.draw(rows, out_pdf_path)`, `wfsheet.winners`, `wfsheet.ECMAP`, ... |
| `wfdata.ORDER, IDX, LABEL, ROWS`, `wfrep.ORDER, IDX` | `atoms.ORDER`, `atoms.IDX`, `wfsheet.LABEL`, `wfsheet.ROWS` |
| `fig5.PROPS` | `atoms.PROPS` |

Not included, because each is used by only one display item or one pair of display items drawn by the same script:

- `atomshares.draw_runs` (SI Figures 2 and 3);
- `fig5.draw` (Figure 5 and SI Figure 5);
- `figstrict.draw` (SI Figures 6 and 7);
- `eulerlib.euler` and `draw_map` (Figure 1);
- Figure 1's case palette.

The data loaders `wfdata`, `wfrep`, `m1load`, `figF4.collect` and `strictne` read the private full outputs and are
likewise not included.

## Verification (2026-09-24)

1. `games.uv()`, `xy()` and `cells()` are bit-identical to DiskM2WF `vor.points()`, `vor.xy()` and `vor.cells()`.
   `cells_keep()` is bit-identical to `wfdata.cells()`. The (u, v) of the four main runs (`wfdata.load`) and of all 17
   packed `.idx` files equal `games.uv()` exactly. Recomputing the cells with scipy 1.10.0 (`compute_cells`) is
   bit-identical.
2. The following are identical to the originals: `disk.CONICS` (vs `atomshares.CONICS`, `atomcounts.CONICS`),
   `disk.euler_lines` (vs eulerlib), the glyph paths and return values of `disk.arc_text`, every layout constant of
   `furniture` and `counts`, `WINCOL`, `TINT`, `GREY`, `ORDER`, `NAME`, and `counts.atom_scale` on three test fields.
3. Whole figures were redrawn from a fresh copy of `common/` and `data/games/`, rasterised with `pdftoppm` next to the
   published PDFs and compared pixelwise:
   - Figure 4 and SI Figure 4 were drawn by `wfsheet.draw` from the runs' arrays.
   - Figure 3 was drawn by `counts.sheet/panel/rowlabel/finish` from the arrangement npz files.
   - SI Figures 2 and 3 were drawn by `furniture.furniture`, `disk_legend` and `check_sheet`.

   All five are **identical**: max |diff| 0 at 80 dpi (Figure 4 also at 150 dpi).
