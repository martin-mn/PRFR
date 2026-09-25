# simulator/games — the game lists the simulator reads

The simulator reads its games from a file `games.dat` in the working directory. These are the two files the runs of the
paper read; `../kits/stage.sh` copies the right one into a kit directory under that name.

| file | rows | sha256 | read by |
|---|---:|---|---|
| `games.dat` | 967 | `72a01386…` | every memory-two kit (dw1–dw4, c1–c4, eh, el, f1, f2, lm), byte-identical in all of them |
| `games_m1.dat` | 512 | `1e9916c8…` | the memory-one kit mw (as its `games.dat`) |

One game per line after the `#` header lines: `gid ic cR cS cT u v tag`. The payoffs are (R, S, T, P) = (cR, cS, cT, 0),
written with 17 significant digits so that they read back as the same doubles; `u` and `v` are for display only (the
dynamics never read them); `ic` is metadata (0 on the rows used here).

**The 512 games of the paper are rows 456–967 of `games.dat`** (gid 2000–2511, tag `V_pNNN_QQW` with NNN = ipt) and all
512 rows of `games_m1.dat`, in the same order. On these rows cR = 1, so u = cS and v = cT − 1 exactly, and every u and v
is a multiple of 2⁻¹⁰. They are the games of `data/games/games.csv` (ipt = gid − 2000), bit for bit (checked there).
Rows 1–455 of `games.dat` (a donation ray in two payoff scales, a 16 × 8 polar grid and a 17 × 17 square) belong to an
earlier campaign of the dw1 kit and are not used in this paper; they stay in the file because the task index of a
memory-two kit is tied to the row: game row ig at error-rate slot ie is task isl = 3 (ig − 1) + ie, so the 512 games
at ε = 10⁻⁴ (ie = 3) are tasks 1368, 1371, …, 2901. In the memory-one kit the row of game ipt is ipt + 1, so its
tasks are 3, 6, …, 1536.
