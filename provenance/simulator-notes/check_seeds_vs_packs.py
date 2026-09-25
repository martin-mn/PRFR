#!/usr/bin/env python3
"""
check_seeds_vs_packs.py -- check ../../simulator/SEEDS.csv against the packed outputs of the runs themselves.

The packs are the private full outputs (author's environment, AUTHOR_ENV below); this script only reads them.  For
every run of SEEDS.csv it checks, game by game, what the pack records about the task that produced the game:

  * memory two (.idx, one line per game): the task index isl is the one SEEDS.csv derives for that game
    (isl_first + 3*ipt), the game id is 2000 + ipt, the number of replicates is SEEDS.csv's, and the total number
    of sampled individual-generations is replicates * (generations/2) * N;
  * memory one (.tsv): the header names N, beta, mu, itend and the replicate count, and every game's total is
    replicates * (generations/2) * N.

Since the seed of a replicate is s0 + 10 (isl - 1) + r, a matching isl means the pack came from the task whose
seeds SEEDS.csv lists.  (The seed base s0 itself is not written into any output file; it is read from the source.)

    python3 check_seeds_vs_packs.py
"""
import csv, os, sys

# ---- author's environment: where the private packs are ---------------------------------------------------------
AUTHOR_ENV = "/Users/martin/Documents/CL1"
# ------------------------------------------------------------------------------------------------------------------
PACK = {
    "m2_N1000": "DiskM2WF/Data/dw1_e4.idx", "m2_N100": "DiskM2WF/Data/dw2_e4.idx",
    "f1": "PartnersRivals/Data/f1_e4.idx", "f2": "PartnersRivals/Data/f2_e4.idx",
    "dw3": "PartnersRivals/Data/dw3_e4.idx", "dw4": "PartnersRivals/Data/dw4_e4.idx",
    "c1": "PartnersRivals/Data/c1_e4.idx", "c2": "PartnersRivals/Data/c2_e4.idx",
    "c3": "PartnersRivals/Data/c3_e4.idx", "c4": "PartnersRivals/Data/c4_e4.idx",
    "eh_e3": "PartnersRivals/Data/eh_e3.idx", "eh_e5": "PartnersRivals/Data/eh_e5.idx",
    "el_e3": "PartnersRivals/Data/el_e3.idx", "el_e5": "PartnersRivals/Data/el_e5.idx",
    "lm_g0": "PartnersRivals1/Cannon/lm/packed/lm_g0_e4.idx", "lm_g01": "PartnersRivals1/Cannon/lm/packed/lm_g01_e4.idx",
    "lm_g05": "PartnersRivals1/Cannon/lm/packed/lm_g05_e4.idx",
    "m1_N1000": "DiskM1WF/Data/mw1_e4.tsv", "m1_N100": "DiskM1WF/Data/mw2_e4.tsv",
    "m1_N1000_ctrl": "DiskM1WF/Data/mw1s_e4.tsv", "m1_N100_ctrl": "DiskM1WF/Data/mw2s_e4.tsv",
}
HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, os.pardir, os.pardir, "simulator", "SEEDS.csv")


def main():
    rows = list(csv.DictReader(l for l in open(SEEDS) if not l.startswith("#")))
    bad = 0
    for r in rows:
        run = r["run"]; p = os.path.join(AUTHOR_ENV, PACK[run])
        N, G, R = int(r["N"]), int(r["generations"]), int(r["replicates"])
        want_tot = R * (G // 2) * N
        if p.endswith(".idx"):
            got = {}
            for l in open(p):
                if l.startswith("#"):
                    continue
                f = l.split()
                gid = int(f[0])
                if 2000 <= gid <= 2511:
                    got[gid - 2000] = (int(f[1]), f[2], int(f[13]), int(f[14]))
            ok = len(got) == 512
            for ipt in range(512):
                isl, tag, nrep, tot = got.get(ipt, (None, "", None, None))
                ok &= isl == int(r["isl_first"]) + 3 * ipt and tag.startswith("V_p%03d" % ipt) \
                    and nrep == R and tot == want_tot
            what = "512 games: isl, tag, nrep = %d and total = %d each" % (R, want_tot)
        else:
            head = open(p).readline() + open(p).readlines()[1]
            ok = ("N = %d," % N) in head and ("itend = %d," % G) in head and ("%d replicates" % R) in head \
                and ("beta = %g," % float(r["beta"])) in head
            tots = [int(l.split("\t")[8]) for l in open(p) if not l.startswith("#")]
            ok &= len(tots) == 512 and all(t == want_tot for t in tots)
            what = "header N, beta, itend, replicates; 512 games with total = %d" % want_tot
        print("%-14s %-48s %s  (%s)" % (run, PACK[run], "OK  " if ok else "FAIL", what))
        bad += not ok
    print("%d of %d runs consistent with SEEDS.csv" % (len(rows) - bad, len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
