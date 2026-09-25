# simulator/local — a smoke test on one's own machine

`smoke.sh` builds one kit's simulator with gfortran, runs **one game** for a few generations, checks that every output
file is complete, packs it with the kit's own `pack.py`, and compares the output with the reference run in
`reference/`. It needs bash, a Fortran compiler and Python 3 (standard library only).

```bash
bash smoke.sh                 # kit f1 (the regeneration of main text Figure 4d-f's run), 20000 generations, game ipt = 178
bash smoke.sh mw1             # the memory-one run of main text Figure 4a-c, same game (task 537)
bash smoke.sh lm 20000 1902   # any kit, run length, task index
FC=ifx FFLAGS="-O3 -xHost -fp-model precise" bash smoke.sh f1     # the cluster's compiler and flags
```

The run is the kit's own source with one line changed, the run length `data itv /.../`, exactly as each kit's
`compile.sh` sets it (the runs of the paper used 10⁷ or 10⁸ generations). The default game, task 1902 of the
memory-two kits (gid 2178, (u, v) = (−2.014, 2.093), a Prisoner's Dilemma below the switch line), is one of the probe
cells of the cluster runs. Everything is written to `work/<kit>_<itend>_<task>/`: the binary, the run directory with
the four output files (see `../README.md`) and the packs.

What it prints, for the default (about 10 s on an Apple M2 Pro):

```
== f1: sf.f with itend = 20000, N = 1000, task 1902, built with gfortran -O2
   ran in 7 s
   summary 1902: 10 replicate lines
   h1902: 65536 strategies, 100000000 counts = 10 x itend/2 x N
   w1902: 10 replicate blocks of the 10 most abundant strategies
   r1902: 10 x 65536 int64 per-replicate counts
   pack.py:
     1 h-files in run
       ie=3 -> f1_e4.{idx,bin,win,rep}     1 cells
     clean: every h-file packed, every histogram whole, every r-file whole, every cell has its rank-1 lines
   packs: f1_e4.bin f1_e4.idx f1_e4.rep f1_e4.win
== identical to the reference run (...)
```

Even at this length the game is held by one of the eight friendly rivals of the wedge W: in replicate 1 the most
abundant strategy is 24199 (`CCCDDDDCDCCCCDCD`), with 90% of the sampled population (`work/.../run/w1902`).

## The reference runs

`reference/<kit>_<itend>_<task>.sha256` holds the sha256 of the summary, w-, h- and (where the kit writes one) r-file of
a run made on the author's machine; `reference/f1_20000_1902.summary` is the summary file of the default run, for
reading. `smoke.sh` compares against the reference when one exists for the (kit, itend, task) it ran. Bit identity is
expected only with the same compiler, flags and CPU family: the simulation is deterministic given its seeds, but a pair
payoff that is rounded differently in its last bit can change one imitation decision and with it the whole random
trajectory. The references are:

| file | kit | notes |
|---|---|---|
| `f1_20000_1902.sha256` | f1 | the default |
| `dw1_20000_1902.sha256` | dw1 | summary, w- and h-file identical to f1's: f1 is dw1 plus the per-replicate file, with the same seeds |
| `f2_20000_1902.sha256` | f2 | |
| `lm_20000_1902.sha256` | lm | ν = 0, the source as deposited (compile.sh's g0) |
| `mw1_20000_537.sha256`, `mw2_20000_537.sha256` | mw | memory one, the same game |

They were made with GNU Fortran 14.1.0, `-O2`, on macOS 26.6 (arm64, Apple M2 Pro), 2026-09-24.
