#!/usr/bin/env python3
"""
Reduce the four main Wright-Fisher runs to the per-game tables of data/runs/ (author's environment only).

    python3 -B reduce_runs.py          ->  ../../data/runs/{m1_N100, m1_N1000, m2_N100, m2_N1000}.csv
                                           ../../data/runs/m1_strategy_atoms.csv, m1_N100_counts.csv, m1_N1000_counts.csv

The four runs are those of main text Figures 4 and 5 and SI Figures 2 to 5, eps = 1e-4 in all four:

    m1_N100    memory one,  N = 100,  beta = 3,   mu = 1e-4   (DiskM1WF run F2, pack mw2_e4.tsv)
    m1_N1000   memory one,  N = 1000, beta = 100, mu = 1e-2   (DiskM1WF run F1, pack mw1_e4.tsv)
    m2_N100    memory two,  N = 100,  beta = 3,   mu = 1e-4   (DiskM2WF run F2, pack dw2_e4.{idx,bin,win})
    m2_N1000   memory two,  N = 1000, beta = 100, mu = 1e-2   (DiskM2WF run F1, pack dw1_e4.{idx,bin,win})

The atom shares S, the atom sizes N and the efficiency E are read through wfdata.load(), the loader the published
figures were drawn with (FinalFigures/wfdata.py: figF4.collect and wfload for memory two, m1load for memory one), so
the tables hold exactly the arrays the published figures were drawn from.  Floats are written with repr() and read
back as the identical doubles.  The other columns are read from the same packs (the per-game lines of the .idx and
.tsv files).  Nothing under AUTHOR_ENV is written.

The full outputs this reads are not deposited: the memory-two packs hold the abundance of each of the 65536
strategies at each game (dw1_e4.bin 253 MB for 967 games, dw2_e4.bin 134 MB for 512), and every Wright-Fisher run is
regenerable bit for bit from the seeds listed in data/runs/runs.csv.  The memory-one packs are small and are
deposited whole (the per-strategy counts tables).
"""
import os
import sys

# ------------------------------------------------------------------------------------------------------------------
AUTHOR_ENV = "/Users/martin/Documents/CL1"      # AUTHOR'S ENVIRONMENT: the private full outputs and the original
#                                                 loaders live under this directory; nothing else in the repository
#                                                 refers to it
# ------------------------------------------------------------------------------------------------------------------
FINAL = os.path.join(AUTHOR_ENV, "PartnersRivals1", "FinalFigures")    # wfdata.py, atomshares.py (the figure loaders)
M1DATA = os.path.join(AUTHOR_ENV, "DiskM1WF", "Data")                  # mw*_e4.tsv, m1_atoms_512.npz, bistable.tsv

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
OUT = os.path.join(REPO, "data", "runs")
sys.path.insert(0, REPO)
sys.path.insert(0, FINAL)

import numpy as np                                                   # noqa: E402

import wfdata                                                        # noqa: E402  (puts DiskM2WF/Opt, DiskM1WF/Opt on the path)
import finalpanels, vor, wfload                                      # noqa: E402  DiskM2WF/Opt
import m1load                                                        # noqa: E402  DiskM1WF/Opt
from common import atoms, games, tables                              # noqa: E402

ORDER, IDX = atoms.ORDER, atoms.IDX
assert wfdata.ORDER == ORDER and wfdata.IDX == IDX

RUNS = [  # name, space, which (the original run names), the space's size
    ("m1_N100", "m1", "F2", 16), ("m1_N1000", "m1", "F1", 16),
    ("m2_N100", "m2", "F2", 65536), ("m2_N1000", "m2", "F1", 65536),
]
# the Cannon campaigns (kits: simulator/kits/dw1, dw2, mw of this repository, in the author's tree DiskM2WF/Cannon/dw1,
# dw2 and DiskM1WF/Cannon/mw; their READMEs and sf.f):
# seed of replicate r = 1..10 of task isl = seed_base + 10 (isl - 1) + r (Mersenne twister, init_genrand)
KIT = {  # name: kit, source, array job id, seed base, task index of game ipt (isl = ISL0 + 3 ipt), figures
    "m1_N100": ("simulator/kits/mw", "sf2.f", 46984101, 11000000, 3, "SIFig2a-h SIFig4a-c SIFig5a-c"),
    "m1_N1000": ("simulator/kits/mw", "sf1.f", 46984100, 10000000, 3, "Fig4a-c Fig5a-c SIFig2i-p"),
    "m2_N100": ("simulator/kits/dw2", "sf.f", 45049704, 9000000, 1368, "SIFig3a-h SIFig4d-f SIFig5d-f"),
    "m2_N1000": ("simulator/kits/dw1", "sf.f", 44394541, 8000000, 1368, "Fig4d-f Fig5d-f SIFig3i-p"),
}
PROPNAME = {"efficient": "P_eff", "stable": "P_nash", "competitive": "P_comp"}

COLDOC = """Columns (one row per game, ipt order 0..511; the games are data/games/games.csv):
  ipt          the game's index (gid = 2000 + ipt in the packs)
  isl          the game's task index in the Cannon array of the run (runs.csv)
  seed1        the seed of its first replicate; replicate r = 1..10 ran on seed1 + r - 1
  u, v         the game, (R, S, T, P) = (1, u, 1 + v, 0), as the pack gives it (equal to games.csv bit for bit)
  emax         Emax = max(R, (S + T)/2), from the pack
  pay          the mean per-round payoff of the population over the sampled halves of the ten replicates
  E            the realised efficiency, the pack's mean of pay/Emax over the replicates: the left column of
               Figure 4 / SI Figure 4 (black where E < 0)
%s  nrep         replicates found (10 at every game)
  S_000..S_111 the share of the population (time x individuals, second half of each replicate, ten replicates
               pooled) held by the strategies of each atom, efficient-stable-competitive, in the eps -> 0
               classification; the seven add to 1 (101 is empty): the atom panels of SI Figures 2 and 3
  N_000..N_111 the number of strategies of the space in each atom at the game (they add to %d)
  P_eff, P_nash, P_comp   the share of the population with each property, the sum of S over its atoms
               (efficient 100+110+111, stable 010+110+011+111, competitive 001+011+111): Figure 5 / SI Figure 5
  abundant     the integer code 4e+2n+c of the most abundant atom (largest S among the atoms with N > 0):
               the middle column of Figure 4 / SI Figure 4 and panels h, p of SI Figures 2 and 3
  enriched     the integer code of the most enriched atom (largest S/N among the atoms with N > 0):
               the right column of Figure 4 / SI Figure 4
  neff         the effective number of strategies, 1/sum_s pi(s)^2, pi the pooled abundance of each strategy
  maxpi        the largest pi(s), the share of the most abundant single strategy
  top          that strategy (%s)%s"""

TOPDOC = {"m1": "memory-one index 0..15: bit j = 1 means C after the outcome j = 0..3 for CC, CD, DC, DD;\n"
                "               ALLD 0, Grim 1, TFT 5, WSLS 9, ALLC 15",
          "m2": "memory-two genome code 0..65535, as in the census; ALLD 0, ALLC 65535"}


def m1_extra(which):
    """per game from the memory-one pack: u, v, emax, pay, ef, ntot and the 16 counts; the split flags"""
    rows, run = m1load.read_pack(which)
    ex = {}
    for ipt, gid, tag, u, v, emax, pay, ef, ntot, cnt in rows:
        p = np.array(cnt, dtype=np.float64) / float(ntot)
        ex[ipt] = dict(gid=gid, tag=tag, u=u, v=v, emax=emax, pay=pay, ef=ef, ntot=ntot, cnt=list(cnt),
                       neff=float(1.0 / np.square(p).sum()), maxpi=float(p.max()), top=int(np.argmax(p)))
    # the games whose ten replicates split between two basins (DiskM1WF/Data/bistable.tsv, measured from the
    # per-replicate abundances of the w-files: some atom's share has a between-replicate s.d. above 0.05)
    split = {}
    for l in open(os.path.join(M1DATA, "bistable.tsv")):
        if l.startswith("#"):
            continue
        f = l.rstrip("\n").split("\t")
        if f[0] == which:
            split[int(f[1])] = (float(f[8]), f[9])
    return ex, split, run


def m2_extra(which):
    """per game from the memory-two .idx: u, v, emax, pay, ef, efsd, nrep, neff, maxpi, top"""
    G = wfload.load_run(finalpanels.idxpath(which), ie=3)
    ex = {}
    for g in G.values():
        ipt = vor.index_of(g["tag"])
        if ipt is None:
            continue
        ex[int(ipt)] = dict(gid=g["gid"], isl=g["isl"], tag=g["tag"], u=g["u"], v=g["v"], emax=g["emax"], pay=g["pay"],
                            ef=g["eff"], efsd=g["efsd"], nrep=g["nrep"], neff=g["neff"], maxpi=g["maxpi"],
                            top=int(g["top"][0]))
    return ex


def reduce_run(name, space, which, nstrat):
    S, N, E, UV, D = wfdata.load(space, which)
    gm = games.games()
    assert (UV == games.uv()).all(), name
    if space == "m1":
        ex, split, runline = m1_extra(which)
    else:
        ex, split, runline = m2_extra(which), None, None
    assert sorted(ex) == list(range(512)), name
    for i in range(512):
        e = ex[i]
        assert e["gid"] == gm["gid"][i] and e["tag"] == gm["tag"][i], (name, i)
        assert (e["u"], e["v"]) == (UV[i, 0], UV[i, 1]), (name, i)
        assert float(e["ef"]) == E[i], (name, i)
    PS = {PROPNAME[nm]: S[:, atoms.members(a)].sum(1) for nm, _, a in atoms.PROPS}   # as fig5.shares sums them
    share = np.where(N > 0, S, -np.inf)
    enr = np.where(N > 0, S / np.maximum(N, 1), -np.inf)                          # as fig4.winners
    wa, we = share.argmax(1), enr.argmax(1)

    kit, sf, jobid, seed0, isl0, figs = KIT[name]
    isl = isl0 + 3 * np.arange(512)
    if space == "m2":
        assert [int(ex[i]["isl"]) for i in range(512)] == isl.tolist(), name
    cols = {"ipt": np.arange(512), "isl": isl, "seed1": seed0 + 10 * (isl - 1) + 1, "u": UV[:, 0], "v": UV[:, 1],
            "emax": [float(ex[i]["emax"]) for i in range(512)], "pay": [float(ex[i]["pay"]) for i in range(512)],
            "E": E}
    if space == "m2":
        cols["efsd"] = [float(ex[i]["efsd"]) for i in range(512)]
        cols["nrep"] = [int(ex[i]["nrep"]) for i in range(512)]
    else:
        cols["nrep"] = [10] * 512                                     # the pack's run line: 10 replicates per game
        assert ", 10 replicates" in runline, runline
    cols.update(tables.atom_columns("S", S))
    cols.update(tables.atom_columns("N", N.astype(np.int64)))
    cols.update(PS)
    cols["abundant"] = [IDX[k] for k in wa]
    cols["enriched"] = [IDX[k] for k in we]
    cols["neff"] = [float(ex[i]["neff"]) for i in range(512)]
    cols["maxpi"] = [float(ex[i]["maxpi"]) for i in range(512)]
    cols["top"] = [int(ex[i]["top"]) for i in range(512)]
    if space == "m1":
        cols["split"] = [int(i in split) for i in range(512)]
        cols["split_sd"] = [split[i][0] if i in split else 0.0 for i in range(512)]

    src = ("DiskM1WF/Data/%s (the Cannon kit mw, %s); atoms: DiskM1WF/Data/m1_atoms_512.npz (the exact eps -> 0 "
           "classification of the 16 strategies at the 512 games)" % (m1load.DATASETS[which]["pack"],
                                                                       "sf1.f / prod1" if which == "F1" else "sf2.f / prod2")
           if space == "m1" else
           "DiskM2WF/Data/%s{.idx,.bin,.win} (the Cannon kit %s, job %s); atoms: the exact eps -> 0 classification "
           "(DiskM2WF/Opt/exact.py: BinM2NE1's census for stability, the ca17 rival mask, self-play efficiency)"
           % (finalpanels.DATASETS[which]["idx"][:-4], finalpanels.DATASETS[which]["kit"], finalpanels.DATASETS[which]["jobid"]))
    head = ["The Wright-Fisher run %s: memory %s (%d strategies), N = %d, beta = %d, mu = %s, eps = 1e-4, uniform mutants,"
            % (name, "one" if space == "m1" else "two", nstrat, D["N"], D["beta"], D["muplain"]),
            "10 replicates per game of %s generations, the second half of each sampled; the run the paper draws in %s."
            % (D["itplain"], "Figures 4 and 5 (rows %s) and SI Figure %s" % (
                "a-c" if space == "m1" else "d-f", "2 i-p" if space == "m1" else "3 i-p") if D["N"] == 1000 else
               "SI Figures 4 and 5 (rows %s) and SI Figure %s" % ("a-c" if space == "m1" else "d-f",
                                                                  "2 a-h" if space == "m1" else "3 a-h")),
            "Source (not deposited): " + src + ".",
            "Written by provenance/four-runs/reduce_runs.py through the loader of the published figures (wfdata.load).",
            ""]
    efsd = "  efsd         the s.d. of pay/Emax over the ten replicates\n" if space == "m2" else ""
    split_doc = ("\n  split        1 where the ten replicates split between two basins (some atom's share has a"
                 "\n               between-replicate s.d. above 0.05, measured from the per-replicate abundances), else 0"
                 "\n  split_sd     that largest between-replicate s.d. (0 where split = 0)") if space == "m1" else ""
    doc = (COLDOC % (efsd, nstrat, TOPDOC[space], split_doc)).split("\n")
    path = os.path.join(OUT, name + ".csv")
    tables.write_table(path, cols, head + doc)
    print("%-9s wrote %s (%d bytes)" % (name, os.path.relpath(path, REPO), os.path.getsize(path)))

    # read back: the arrays of the figures come back bit for bit
    T = tables.read_table(path)
    assert (tables.atom_array(T, "S") == S).all() and (tables.atom_array(T, "N") == N).all() and (T["E"] == E).all()
    return ex if space == "m1" else None


def write_m1_strategies(ex1000, ex100):
    """the memory-one packs whole: the counts of each of the 16 strategies at each game, and their atoms"""
    z = np.load(os.path.join(M1DATA, "m1_atoms_512.npz"))
    codes, tags, uv = z["codes"].astype(np.int64), z["tags"], z["uv"]
    assert (uv == games.uv()).all() and (tags == games.tags()).all()
    cols = {"ipt": np.arange(512)}
    cols.update({"a%d" % k: codes[:, k] for k in range(16)})
    tables.write_table(os.path.join(OUT, "m1_strategy_atoms.csv"), cols, [
        "The atom of each of the 16 binary memory-one strategies at each of the 512 games, in the exact eps -> 0",
        "classification (DiskM1WF/Data/m1_atoms_512.npz): the integer code 4*efficient + 2*stable + competitive.",
        "Strategy k: bit j of k is 1 if the strategy cooperates after the outcome j = 0..3 for CC, CD, DC, DD",
        "(ALLD 0, Grim 1, TFT 5, CCCD 7 (C except after DD), WSLS 9, ALLC 15).",
        "", "Columns: ipt (the game, data/games/games.csv), a0..a15 (the atom code of strategy k)"])
    for name, which, ex in (("m1_N1000_counts", "F1", ex1000), ("m1_N100_counts", "F2", ex100)):
        D = m1load.DATASETS[which]
        cols = {"ipt": np.arange(512), "ntot": [int(ex[i]["ntot"]) for i in range(512)]}
        cols.update({"c%d" % k: [int(ex[i]["cnt"][k]) for i in range(512)] for k in range(16)})
        tables.write_table(os.path.join(OUT, name + ".csv"), cols, [
            "The memory-one Wright-Fisher run %s whole: N = %d, beta = %d, mu = %s, eps = 1e-4, 10 replicates of %s"
            % (name[:-7], D["N"], D["beta"], D["muplain"], D["itplain"]),
            "generations per game; per game the number of individual-generations, over the sampled second halves of the ten",
            "replicates, in which each of the 16 strategies was held (DiskM1WF/Data/%s, the Cannon kit mw)." % D["pack"],
            "c_k / ntot is the pooled abundance pi(k); with m1_strategy_atoms.csv it gives the atom and property shares, the",
            "most abundant and most enriched atom, neff, maxpi and top of %s.csv, bit for bit." % name[:-7],
            "", "Columns: ipt (the game), ntot (the total, 10 x N x generations/2), c0..c15 (the count of strategy k; k as in",
            "m1_strategy_atoms.csv)"])
        print("%-16s wrote data/runs/%s.csv" % (name, name))
    # the atom shares recomputed from the counts and the atoms equal those of the loader
    for name, ex in (("m1_N1000", ex1000), ("m1_N100", ex100)):
        T = tables.read_table(os.path.join(OUT, name + ".csv"))
        S8 = np.zeros((512, 8))
        for i in range(512):
            for k in range(16):
                S8[i, codes[i, k]] += ex[i]["cnt"][k]
            S8[i] /= float(ex[i]["ntot"])
        assert (S8[:, IDX] == tables.atom_array(T, "S")).all(), name


def write_index():
    """runs.csv: one row per run, its parameters and where it came from"""
    cols = {k: [] for k in ("name", "space", "nstrat", "N", "beta", "mu", "eps", "generations", "replicates",
                            "kit", "source", "jobid", "seed_base", "isl0", "figures")}
    for name, space, which, nstrat in RUNS:
        D = (m1load.DATASETS if space == "m1" else finalpanels.DATASETS)[which]
        kit, sf, jobid, seed0, isl0, figs = KIT[name]
        for k, v in (("name", name), ("space", space), ("nstrat", nstrat), ("N", D["N"]), ("beta", D["beta"]),
                     ("mu", float(D["muplain"])), ("eps", 1e-4), ("generations", int(float(D["itplain"]))),
                     ("replicates", D["nrep"]), ("kit", kit), ("source", sf), ("jobid", jobid), ("seed_base", seed0),
                     ("isl0", isl0), ("figures", figs)):
            cols[k].append(v)
    tables.write_table(os.path.join(OUT, "runs.csv"), cols, [
        "The four main Wright-Fisher runs (Methods, 'The Wright-Fisher process with pairwise comparison'): one row per run.",
        "Every run: the 512 games of data/games, uniform mutants over the whole space (the current strategy included),",
        "eps = 1e-4, 10 independent replicates per game from independent uniform initial populations, the second half",
        "of each replicate sampled (every individual in every generation).",
        "",
        "Columns:",
        "  name         the run; its per-game table is <name>.csv",
        "  space        m1: the 16 binary memory-one strategies (run as memory-two strategies that ignore the round",
        "               before); m2: the 65536 binary memory-two strategies",
        "  nstrat       the size of the space",
        "  N, beta, mu, eps   population size, selection intensity, mutation rate, error rate",
        "  generations  generations per replicate",
        "  replicates   replicates per game",
        "  kit, source  the Cannon kit in this repository (simulator/kits/) and the Fortran source of the run",
        "  jobid        the Slurm array job id of the production array on Harvard's Cannon cluster",
        "  seed_base    s0: replicate r = 1..10 of task isl ran on the seed s0 + 10 (isl - 1) + r",
        "  isl0         the task index of game ipt is isl = isl0 + 3 ipt (column isl of the per-game tables)",
        "  figures      the display items drawn from the run",
        "The two memory-two runs were regenerated bit for bit from these seeds on 2026-09-22 (kits f1, f2, jobs",
        "47837723 and 47837725): every summary, w- and h-file of the 512 games was byte-identical to the original.",
        "m2_N1000: five of its games (the probe cells, ipt 0 and 508-511) ran, on the same seeds, in the probe array",
        "44383754, and the production array skipped them."])
    print("runs      wrote data/runs/runs.csv")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write_index()
    got = {}
    for name, space, which, nstrat in RUNS:
        got[name] = reduce_run(name, space, which, nstrat)
    write_m1_strategies(got["m1_N1000"], got["m1_N100"])
