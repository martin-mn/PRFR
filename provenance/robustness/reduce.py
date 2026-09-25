#!/usr/bin/env python3
"""
reduce.py -- turn the packed outputs of the memory-two Wright-Fisher runs of the robustness analyses into the small
tables of data/robustness/ (SI Figures 8-12, SI Tables 6 and 7).

    python3 -B provenance/robustness/reduce.py            (from the repository root; a few seconds, one process)

Reads, for each run of RUNS below, the four files the simulator's pack.py wrote on the cluster (see data/robustness/
README.md for their formats):

    <run>.idx   one line per game: gid isl tag u v cR cS cT Emax pay ef efsd ndist nrep total ps1..ps16
    <run>.bin   512 x 65536 float32: the summed abundance of every strategy over the sampled second half of the ten
                replicates (the 128 MB file that is NOT deposited; regenerable from the seeds)
    <run>.rep   one line per (game, replicate): gid irun ef s000 s100 s010 s001 s110 s011 s111   (absent for dw3, dw4)
    <run>.win   one line per (game, replicate): gid irun rank1 abund selfpay

and atoms512.bin, 512 x 65536 uint8, the eps -> 0 atom code 4*efficient + 2*stable + competitive of every strategy at
every game (written by PartnersRivals/Cannon/mkatoms.py from the exact masks), and writes

    data/robustness/m2_atom_sizes.csv            the number of strategies in each atom at each game (the same for every run)
    data/robustness/games_<run>.csv              per game: the pooled atom shares and the efficiency
    data/robustness/replicates_<run>.csv         per game and replicate: the replicate's efficiency and atom shares (from
                                                 the .rep), its most abundant strategy, that strategy's atom and share
                                                 (from the .win), and the replicate's seed

The pooled share of an atom is computed exactly as the figure scripts' loader wfrep.py computed it: the abundance
vector divided by its sum, then summed over the atom's strategies with np.bincount.  crosscheck.py compares the
tables with the original loaders.

AUTHOR'S ENVIRONMENT: the packed outputs are private (1.5 GB); AUTHOR_ROOT below is the only path into them.
"""
import os
import sys

import numpy as np

# ---------------------------------------------------------------------------------------------- author's environment
AUTHOR_ROOT = "/Users/martin/Documents/CL1"          # author's environment: the private project tree holding the packs
PACKS = {"PartnersRivals": os.path.join(AUTHOR_ROOT, "PartnersRivals", "Data"),
         "lm": os.path.join(AUTHOR_ROOT, "PartnersRivals1", "Cannon", "lm", "packed")}
ATOMS512 = os.path.join(AUTHOR_ROOT, "PartnersRivals", "Cannon", "atoms512.bin")
# ---------------------------------------------------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir)
sys.path.insert(0, ROOT)
from common import games, tables                    # noqa: E402
from common.atoms import IDX, ORDER                 # noqa: E402

OUT = os.path.join(ROOT, "data", "robustness")
NC, NG = 65536, 512

# The runs: pack folder, then the row of runs.csv (kit, N, beta, mu, eps, nu, generations per replicate, seed base,
# slurm offset ie, the Slurm array job ID of the production array on Cannon, per-replicate output, where it is used).
# The parameters are those of the kits' sf.f (PartnersRivals/Cannon/README.md, PartnersRivals1/Cannon/lm/README.md);
# N and the generations are checked against the 'total' column of every .idx (= 10 * generations/2 * N).
RUNS = {
    "f1_e4": ("PartnersRivals", "f1", 1000, 100, "1e-2", "1e-4", 1, "1e7", 8000000, 3, 47837723, 1,
              "main text Figure 4d-f; SI Figures 8 h/p/x and 9 d-f and 11 d-f and 12 j-l; SI Tables 6 and 7: "
              "DiskM2WF run dw1 (job 44394541) regenerated with its own seeds - byte-identical to dw1 at all 512 games - "
              "plus the per-replicate output"),
    "f2_e4": ("PartnersRivals", "f2", 100, 3, "1e-4", "1e-4", 1, "1e8", 9000000, 3, 47837725, 1,
              "SI Figure 4d-f; SI Figures 8 a/i/q and 10 d-f and 11 a-c; SI Tables 6 and 7: "
              "DiskM2WF run dw2 (job 45049704) regenerated with its own seeds - byte-identical to dw2 - "
              "plus the per-replicate output"),
    "c2_e4": ("PartnersRivals", "c2", 100, 3, "1e-2", "1e-4", 1, "1e7", 23000000, 3, 47721339, 1, "SI Figure 8 b/j/r; SI Table 7a row 2"),
    "c4_e4": ("PartnersRivals", "c4", 1000, 3, "1e-4", "1e-4", 1, "1e7", 25000000, 3, 47734216, 1, "SI Figure 8 c/k/s; SI Table 7a row 3"),
    "dw4_e4": ("PartnersRivals", "dw4", 1000, 3, "1e-2", "1e-4", 1, "1e7", 11000000, 3, 46108584, 0, "SI Figure 8 d/l/t; SI Table 7a row 4"),
    "c3_e4": ("PartnersRivals", "c3", 100, 100, "1e-4", "1e-4", 1, "1e8", 24000000, 3, 47735495, 1, "SI Figure 8 e/m/u; SI Table 7a row 5"),
    "c1_e4": ("PartnersRivals", "c1", 100, 100, "1e-2", "1e-4", 1, "1e7", 22000000, 3, 47721337, 1, "SI Figure 8 f/n/v; SI Table 7a row 6"),
    "dw3_e4": ("PartnersRivals", "dw3", 1000, 100, "1e-4", "1e-4", 1, "1e7", 10000000, 3, 46108583, 0, "SI Figure 8 g/o/w; SI Table 7a row 7"),
    "eh_e3": ("PartnersRivals", "eh", 1000, 100, "1e-2", "1e-3", 1, "1e7", 20000000, 2, 47736148, 1, "SI Figure 9 a-c; SI Table 7b row 1"),
    "eh_e5": ("PartnersRivals", "eh", 1000, 100, "1e-2", "1e-5", 1, "1e7", 20000000, 1, 47734175, 1, "SI Figure 9 g-i; SI Table 7b row 2"),
    "el_e3": ("PartnersRivals", "el", 100, 3, "1e-4", "1e-3", 1, "1e8", 21000000, 2, 47735463, 1, "SI Figure 10 a-c; SI Table 7b row 3"),
    "el_e5": ("PartnersRivals", "el", 100, 3, "1e-4", "1e-5", 1, "1e8", 21000000, 1, 47734189, 1, "SI Figure 10 g-i; SI Table 7b row 4"),
    "lm_g0_e4": ("lm", "lm/g0", 1000, 100, "1e-2", "1e-4", 0, "1e7", 30000000, 3, 48181135, 1, "SI Figure 12 a-c; SI Table 7c row 1"),
    "lm_g01_e4": ("lm", "lm/g01", 1000, 100, "1e-2", "1e-4", 0.1, "1e7", 31000000, 3, 48181161, 1, "SI Figure 12 d-f; SI Table 7c row 2"),
    "lm_g05_e4": ("lm", "lm/g05", 1000, 100, "1e-2", "1e-4", 0.5, "1e7", 32000000, 3, 48181182, 1, "SI Figure 12 g-i; SI Table 7c row 3"),
}
RUNCOLS = ["kit", "N", "beta", "mu", "eps", "nu", "generations", "seed_base", "ie", "jobid", "per_replicate", "role"]
NPER = 10                                           # replicates per game; seed = seed_base + (isl - 1)*NPER + irep


RUNS_COMMENTS = [
    "runs.csv -- the fifteen memory-two Wright-Fisher runs whose reduced output is in this folder, one row per run",
    "(written by provenance/robustness/reduce.py).  Every run: the 65536 binary memory-two strategies on the 512 sampled",
    "games (data/games), the Wright-Fisher process with pairwise comparison of the Methods, 10 independent replicates per",
    "game, the second half of each replicate sampled.",
    "Columns:",
    "  run            the name of the packed output and of the tables games_<run>.csv and replicates_<run>.csv",
    "  kit            the simulator kit that produced it (the Cannon kits of the project)",
    "  N              population size",
    "  beta           selection strength of the pairwise comparison",
    "  mu             mutation rate per individual and generation",
    "  eps            error rate: the probability that an intended move is flipped",
    "  nu             mutation kernel: the probability that a mutant is drawn uniformly from all 65536 strategies (its own",
    "                 included); otherwise one of the 16 positions of its own strategy is flipped. nu = 1: the uniform kernel",
    "  generations    generations per replicate (the second half is sampled)",
    "  seed_base      the seed of replicate rep of task isl is seed_base + (isl - 1)*10 + rep (column seed of replicates_<run>.csv)",
    "  ie             offset of the slurm array: isl = 3*(ig - 1) + ie with ig = 456 + ipt (column isl of games_<run>.csv)",
    "  jobid          the Slurm array job ID of the production array on the Harvard Cannon cluster",
    "  per_replicate  1 if the run wrote per-replicate atom shares (a .rep file; the kits of 2026-09-22 and later), else 0",
    "  role           where the run appears in the paper (a/b/c: the same disk in the three groups of SI Figure 8)",
]


def rows(path):
    return [l.split() for l in open(path) if l.strip() and not l.startswith("#")]


def reduce_run(run, A):
    where = RUNS[run][0]
    meta = dict(zip(RUNCOLS, RUNS[run][1:]))
    seedb, has_rep = meta["seed_base"], bool(meta["per_replicate"])
    base = os.path.join(PACKS[where], run)
    G = games.games()
    R = rows(base + ".idx")
    assert len(R) == NG, (run, len(R))
    blob = np.fromfile(base + ".bin", dtype="<f4")
    assert blob.size == NG * NC, (run, blob.size)
    blob = blob.reshape(NG, NC)
    col = {k: np.zeros(NG, dtype=np.int64) for k in ("isl", "ndist", "nrep", "total")}
    col.update({k: np.full(NG, np.nan) for k in ("pay", "E", "efsd")})
    S = np.full((NG, 7), np.nan)
    seen = np.zeros(NG, bool)
    for k, r in enumerate(R):
        gid, isl, tag = int(r[0]), int(r[1]), r[2]
        ipt = games.ipt_of_gid(gid)
        assert tag == G["tag"][ipt] and int(tag.split("_")[1][1:]) == ipt, (run, gid, tag)
        cR, cS, cT = map(float, r[5:8])
        assert cR == 1.0 and cS == G["u"][ipt] and cT - 1.0 == G["v"][ipt], (run, gid)   # the game, bit for bit
        assert abs(float(r[8]) - G["emax"][ipt]) < 1e-9, (run, gid, r[8])
        col["isl"][ipt], col["pay"][ipt], col["E"][ipt], col["efsd"][ipt] = isl, float(r[9]), float(r[10]), float(r[11])
        col["ndist"][ipt], col["nrep"][ipt], col["total"][ipt] = int(r[12]), int(r[13]), int(r[14])
        p = blob[k].astype(np.float64)
        p = p / p.sum()
        full = np.bincount(A[ipt], weights=p, minlength=8)          # wfrep.load, verbatim
        assert full[5] == 0.0, (run, gid, "101 is not empty")
        S[ipt] = full[IDX]
        assert int((blob[k] > 0).sum()) == col["ndist"][ipt], (run, gid, "ndist")
        seen[ipt] = True
    assert seen.all() and (col["nrep"] == NPER).all() and np.allclose(S.sum(1), 1.0)
    assert (col["total"] == NPER * int(float(meta["generations"])) // 2 * meta["N"]).all(), (run, "N or generations")
    assert (col["isl"] == 1365 + 3 * np.arange(NG) + (col["isl"][0] - 1365)).all(), (run, "isl is not 3(ig-1) + ie")
    ie = int(col["isl"][0] - 1365)
    assert ie == meta["ie"], (run, "ie")

    # per replicate
    TOP = np.full((NG, NPER), -1, dtype=np.int64); TSH = np.full((NG, NPER), np.nan); TSP = np.full((NG, NPER), np.nan)
    for r in rows(base + ".win"):
        ipt, irun = games.ipt_of_gid(int(r[0])), int(r[1]) - 1
        assert TOP[ipt, irun] == -1, (run, r)
        TOP[ipt, irun], TSH[ipt, irun], TSP[ipt, irun] = int(r[2]), float(r[3]), float(r[4])
    assert (TOP >= 0).all(), (run, "a replicate is missing from the .win")
    TAT = np.take_along_axis(A, TOP, axis=1)                        # the atom code of each replicate's rank-1 strategy
    ER = np.full((NG, NPER), np.nan); RS = np.full((NG, NPER, 7), np.nan)
    if has_rep:
        for r in rows(base + ".rep"):
            ipt, irun = games.ipt_of_gid(int(r[0])), int(r[1]) - 1
            assert np.isnan(ER[ipt, irun]), (run, r)
            ER[ipt, irun] = float(r[2]); RS[ipt, irun] = [float(x) for x in r[3:10]]
        assert not np.isnan(ER).any() and not np.isnan(RS).any(), (run, "a replicate is missing from the .rep")
        dev = np.abs(RS.mean(1) - S).max()
        assert dev < 2e-6, (run, "replicate shares do not average to the pooled shares", dev)   # wfrep.load's check
    else:
        dev = np.nan

    # ------------------------------------------------------------------------------------------------ write
    gcols = {"ipt": np.arange(NG), "isl": col["isl"], "E": col["E"], "efsd": col["efsd"], "pay": col["pay"],
             "ndist": col["ndist"], "nrep": col["nrep"]}
    gcols.update(tables.atom_columns("S", S))
    tables.write_table(os.path.join(OUT, "games_%s.csv" % run), gcols, [
        "games_%s.csv -- memory-two Wright-Fisher run %s (parameters: runs.csv), one row per sampled game, ipt order 0..511." % (run, run),
        "Reduced by provenance/robustness/reduce.py from the packed files %s.{idx,bin} and atoms512.bin." % run,
        "Columns:",
        "  ipt      the game (data/games/games.csv; gid = 2000 + ipt)",
        "  isl      the task index of the game in the kit's slurm array (isl = 3*(ig - 1) + ie with ie = %d); it fixes the seeds" % ie,
        "  E        realised efficiency: mean per-round payoff of the population over the sampled second half of the",
        "           ten replicates, divided by Emax = max(1, (1 + u + v)/2)  (the 'ef' column of the .idx)",
        "  efsd     standard deviation over the ten replicates of each replicate's pay/Emax, as the simulator wrote it (the .idx)",
        "  pay      mean per-round payoff of the population, the numerator of E",
        "  ndist    number of distinct strategies with a non-zero count in the summed abundance",
        "  nrep     replicates found (10 at every game)",
        "  S_abc    pooled share of the population in the atom abc (efficient-stable-competitive, eps -> 0 atoms):",
        "           the abundance summed over the ten replicates and the sampled half, normalised, summed over the atom",
        "           (the atom 101 is empty at every game and has no column)",
    ])
    rcols = {"ipt": np.repeat(np.arange(NG), NPER), "rep": np.tile(np.arange(1, NPER + 1), NG),
             "seed": (seedb + (np.repeat(col["isl"], NPER) - 1) * NPER + np.tile(np.arange(1, NPER + 1), NG))}
    comments = [
        "replicates_%s.csv -- memory-two Wright-Fisher run %s (parameters: runs.csv), one row per (game, replicate)," % (run, run),
        "5120 rows, ipt order 0..511, replicates 1..10 within a game.",
        "Reduced by provenance/robustness/reduce.py from the packed files %s.{idx,win%s} and atoms512.bin." % (run, ",rep" if has_rep else ""),
        "Columns:",
        "  ipt      the game (data/games/games.csv)",
        "  rep      the replicate, 1..10",
        "  seed     the replicate's seed: seed_base + (isl - 1)*10 + rep, seed_base = %d (runs.csv), isl from games_%s.csv" % (seedb, run),
    ]
    if has_rep:
        rcols["E"] = ER.ravel()
        rcols.update(tables.atom_columns("R", RS.reshape(NG * NPER, 7)))
        comments += [
            "  E        the replicate's realised efficiency over its sampled second half (the .rep, 8 decimals)",
            "  R_abc    the share of the replicate's sampled population in the atom abc (the .rep, 8 decimals); the ten",
            "           replicates of a game average to the pooled S_abc of games_%s.csv within %.1e" % (run, dev),
        ]
    rcols.update({"top": TOP.ravel(), "top_atom": TAT.ravel(), "top_share": TSH.ravel(), "top_selfpay": TSP.ravel()})
    comments += [
        "  top          the replicate's most abundant strategy over its sampled half (the .win 'rank1'): its integer code",
        "               0..65535 of the Methods (the genome read as a binary number; ALLD = 0, ALLC = 65535)",
        "  top_atom     its atom at this game as the integer code 4*efficient + 2*stable + competitive (0..7; 101 = 5 never",
        "               occurs); e.g. 7 = 111 (a friendly rival), 6 = 110, 4 = 100",
        "  top_share    its share of the replicate's sampled population (the .win 'abund')",
        "  top_selfpay  its per-round payoff against itself at this game (the .win 'selfpay')",
    ]
    tables.write_table(os.path.join(OUT, "replicates_%s.csv" % run), rcols, comments)
    return S, col["E"], ie


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.fromfile(ATOMS512, dtype=np.uint8)
    assert A.size == NG * NC, ATOMS512
    A = A.reshape(NG, NC)
    N8 = np.stack([np.bincount(A[i], minlength=8) for i in range(NG)])
    assert not N8[:, 5].any() and (N8.sum(1) == NC).all()
    tables.write_table(os.path.join(OUT, "m2_atom_sizes.csv"),
                       dict([("ipt", np.arange(NG))] + list(tables.atom_columns("N", N8[:, IDX]).items())), [
        "m2_atom_sizes.csv -- the number of the 65536 binary memory-two strategies in each atom at each sampled game,",
        "in the limit eps -> 0 (the classification of the paper; the same for every run of this folder).",
        "Reduced by provenance/robustness/reduce.py from atoms512.bin (one atom code per strategy per game).",
        "Columns: ipt (the game, data/games/games.csv); N_abc the size of the atom abc (efficient-stable-competitive);",
        "each row sums to 65536; the atom 101 is empty at every game and has no column.",
    ])
    rc = {"run": list(RUNS)}
    rc.update({c: [RUNS[r][1 + j] for r in RUNS] for j, c in enumerate(RUNCOLS)})
    tables.write_table(os.path.join(OUT, "runs.csv"), rc, RUNS_COMMENTS)
    for run in (sys.argv[1:] or list(RUNS)):
        S, E, ie = reduce_run(run, A)
        print("%-10s ie %d  E %.4f .. %.4f  most abundant atom 111 at %3d games, 110 at %3d" %
              (run, ie, E.min(), E.max(), (S.argmax(1) == 6).sum(), (S.argmax(1) == 4).sum()))
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
