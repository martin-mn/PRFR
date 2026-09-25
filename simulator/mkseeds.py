#!/usr/bin/env python3
"""
mkseeds.py -- write SEEDS.csv and seeds_by_game.csv from the kit files themselves.

Every number in the two tables is read from the Fortran source and the Slurm/compile scripts in kits/ (the files
that ran on the cluster), not typed in: the population size, the seed base, the replicate count, the error rate of
the array's stride, the mutation rate, the selection strength, the run length, the global-mutation fraction and the
array of task indices.  Only the list of runs and the display items each one feeds are given here by hand (RUNS).

    python3 mkseeds.py            # rewrites SEEDS.csv and seeds_by_game.csv next to this script, prints a summary
    python3 mkseeds.py --check    # rewrites nothing; fails if the two files differ from what the kits say

The seed rule (Methods of the paper; every kit's sf.f, `iseed=iseedb+(isl-1)*nper+irep`):

    seed of replicate r (r = 1..10) of task k  =  s0 + 10 (k - 1) + r

where k = isl is the Slurm array task index of the game's cell, NOT the game's number 0..511, and s0 = iseedb is
the run's seed base.  The memory-two kits read the 967-row games.dat and decode ig = (isl-1)/3 + 1 (the row) and
ie = mod(isl-1, 3) + 1 (the error rate); the 512 games of the paper are rows 456..967, so game ipt has
isl = 1365 + 3*ipt + ie.  The memory-one kit reads a 512-row games.dat, so there isl = 3*ipt + ie.  Every run of
the paper uses one error-rate stride only (ie = 3, eps = 1e-4, except the error-rate series eh and el).
Standard library only.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KITS = os.path.join(HERE, "kits")
NGAME = 512

# (run id, kit, source, production Slurm script, ie, lm variant or None, memory, the display items it feeds, note)
RUNS = [
    ("m1_N1000", "mw", "sf1.f", "prod1.slurm", 3, None, 1,
     "Fig 4a-c; Fig 5a-c; SI Fig 2i-p; SI Fig 6c; SI Fig 7c", "memory one: large population"),
    ("m1_N100", "mw", "sf2.f", "prod2.slurm", 3, None, 1,
     "SI Fig 2a-h; SI Fig 4a-c; SI Fig 5a-c; SI Fig 6b; SI Fig 7b", "memory one: small population"),
    ("m2_N1000", "dw1", "sf.f", "prod_vor_e4.slurm", 3, None, 2,
     "Fig 4d-f; Fig 5d-f; SI Fig 3i-p; SI Fig 6f; SI Fig 7f; SI Fig 8h/p/x (corner N=1000 beta=100 mu=1e-2); "
     "SI Fig 9d-f; SI Fig 12j-l (nu=1); SI Tables 6 and 7", "memory two: large population (F1)"),
    ("m2_N100", "dw2", "sf.f", "prod_1e8.slurm", 3, None, 2,
     "SI Fig 3a-h; SI Fig 4d-f; SI Fig 5d-f; SI Fig 6e; SI Fig 7e; SI Fig 8a/i/q (corner N=100 beta=3 mu=1e-4); "
     "SI Fig 10d-f; SI Tables 6 and 7", "memory two: small population (F2)"),
    ("f1", "f1", "sf.f", "prod_e4.slurm", 3, None, 2, "SI Fig 11d-f (per-replicate atom shares)",
     "bit-for-bit regeneration of m2_N1000 with the per-replicate count file (same seeds)"),
    ("f2", "f2", "sf.f", "prod_e4.slurm", 3, None, 2, "SI Fig 11a-c (per-replicate atom shares)",
     "bit-for-bit regeneration of m2_N100 with the per-replicate count file (same seeds)"),
    ("dw3", "dw3", "sf.f", "prod_1e7.slurm", 3, None, 2, "SI Fig 8g/o/w (corner N=1000 beta=100 mu=1e-4); SI Table 7a",
     "cube corner"),
    ("dw4", "dw4", "sf.f", "prod_1e7.slurm", 3, None, 2, "SI Fig 8d/l/t (corner N=1000 beta=3 mu=1e-2); SI Table 7a",
     "cube corner"),
    ("c1", "c1", "sf.f", "prod_e4.slurm", 3, None, 2, "SI Fig 8f/n/v (corner N=100 beta=100 mu=1e-2); SI Table 7a",
     "cube corner"),
    ("c2", "c2", "sf.f", "prod_e4.slurm", 3, None, 2, "SI Fig 8b/j/r (corner N=100 beta=3 mu=1e-2); SI Table 7a",
     "cube corner"),
    ("c3", "c3", "sf.f", "prod_e4.slurm", 3, None, 2, "SI Fig 8e/m/u (corner N=100 beta=100 mu=1e-4); SI Table 7a",
     "cube corner"),
    ("c4", "c4", "sf.f", "prod_e4.slurm", 3, None, 2, "SI Fig 8c/k/s (corner N=1000 beta=3 mu=1e-4); SI Table 7a",
     "cube corner"),
    ("eh_e3", "eh", "sf.f", "prod_e3.slurm", 2, None, 2, "SI Fig 9a-c; SI Table 7b", "error-rate series: large population"),
    ("eh_e5", "eh", "sf.f", "prod_e5.slurm", 1, None, 2, "SI Fig 9g-i; SI Table 7b", "error-rate series: large population"),
    ("el_e3", "el", "sf.f", "prod_e3.slurm", 2, None, 2, "SI Fig 10a-c; SI Table 7b", "error-rate series: small population"),
    ("el_e5", "el", "sf.f", "prod_e5.slurm", 1, None, 2, "SI Fig 10g-i; SI Table 7b", "error-rate series: small population"),
    ("lm_g0", "lm", "sf.f", "lm.slurm", 3, "g0", 2, "SI Fig 12a-c (nu=0); SI Table 7c", "mixed mutation kernel"),
    ("lm_g01", "lm", "sf.f", "lm.slurm", 3, "g01", 2, "SI Fig 12d-f (nu=0.1); SI Table 7c", "mixed mutation kernel"),
    ("lm_g05", "lm", "sf.f", "lm.slurm", 3, "g05", 2, "SI Fig 12g-i (nu=0.5); SI Table 7c", "mixed mutation kernel"),
    ("m1_N1000_ctrl", "mw", "sf1s.f", "prod1s.slurm", 3, None, 1, "none",
     "convergence control of m1_N1000 (run length divided by 100); not in the paper"),
    ("m1_N100_ctrl", "mw", "sf2s.f", "prod2s.slurm", 3, None, 1, "none",
     "convergence control of m1_N100 (run length divided by 100); not in the paper"),
]


def fnum(s):
    """a Fortran real literal (1.d-02, 100.d+00) as a float"""
    return float(s.lower().replace("d", "e"))


def one(pattern, text, what):
    m = re.findall(pattern, text, re.M)
    assert len(m) == 1, "%s: %d matches for %r" % (what, len(m), pattern)
    return m[0]


def kit_params(kit, src, slurm, ie, variant):
    d = os.path.join(KITS, kit)
    f = open(os.path.join(d, src)).read()
    p = {}
    p["N"] = int(one(r"^      parameter \(n=(\d+),m=1\)", f, src))
    nrep, nper = one(r"^      parameter \(mgam=\d+,neps=3,nu=1,nbet=1,nrep=(\d+),nper=(\d+)\)", f, src)
    p["replicates"] = int(nrep); nper = int(nper)
    assert nper == p["replicates"], "one task = one cell needs nper = nrep"
    p["seed_base"] = int(one(r"^      parameter \(iseedb=(\d+)\)", f, src))
    eps = one(r"^      data epsv /([^/]+)/", f, src).split(",")
    p["eps"] = fnum(eps[ie - 1])
    p["mu"] = fnum(one(r"^      data uval /([^/]+)/", f, src))
    p["beta"] = fnum(one(r"^      data bval /([^/]+)/", f, src))
    itv = int(one(r"^      data itv  /(\d+)/", f, src))
    assert "iseed=iseedb+(isl-1)*nper+irep" in f.replace(" ", ""), "seed rule not found in " + src
    s = open(os.path.join(d, slurm)).read()
    # which binary the production array ran, hence the run length
    exe = one(r"^(?:\.\./|\"\.\./)(sf[^ \"]*\.x)", s, slurm)
    comp = open(os.path.join(d, "compile.sh")).read()
    if exe in ("sf.x", "sf1.x", "sf2.x", "sf1s.x", "sf2s.x"):
        p["generations"] = itv                          # the run length compiled from the source as it stands
    elif exe.startswith("sf_$G"):                       # lm: pglob, seed base and itend set by compile.sh
        pg, sb = re.search(r"^  %s\)\s+PG=([^;]+); SB=(\d+) ;;" % variant, comp, re.M).groups()
        p["nu"] = fnum(pg); p["seed_base"] = int(sb)
        p["generations"] = int(one(r"^IT=\$\{ITEND:-(\d+)\}", comp, "lm compile.sh"))
    else:                                               # sf_1e7.x / sf_1e8.x: compile.sh patches `data itv`
        L = one(r"^(?:\.\./)sf_(1e\d)\.x", s, slurm)
        p["generations"] = int(one(r"^  %s\) IT=(\d+) *;;" % L, comp, kit + "/compile.sh"))
    p.setdefault("nu", 1.0)
    if kit != "lm":
        assert "pglob" not in f
    spec = re.search(r"^#SBATCH --array=(\S+)", s, re.M)
    spec = spec.group(1) if spec else one(r'^  prod\)\s+SPEC="([^"]+)"', open(os.path.join(d, "submit.sh")).read(), "lm submit.sh")
    a, step = spec.split(":"); lo, hi = map(int, a.split("-"))
    p["isl_first"], p["isl_last"], p["isl_step"] = lo, hi, int(step)
    return p


def isl_of(ipt, memory, ie):
    return (3 * ipt + ie) if memory == 1 else (1365 + 3 * ipt + ie)


def build():
    rows, per_game = [], {}
    for rid, kit, src, slurm, ie, variant, memory, items, note in RUNS:
        p = kit_params(kit, src, slurm, ie, variant)
        isl = [isl_of(i, memory, ie) for i in range(NGAME)]
        assert (isl[0], isl[-1], 3) == (p["isl_first"], p["isl_last"], p["isl_step"]), \
            "%s: the array %d-%d:%d is not the 512 games at ie = %d" % (rid, p["isl_first"], p["isl_last"], p["isl_step"], ie)
        s0, R = p["seed_base"], p["replicates"]
        seeds = [s0 + 10 * (k - 1) + 1 for k in isl]
        per_game[rid] = seeds
        rows.append(dict(run=rid, memory=memory, kit=kit, source="kits/%s/%s" % (kit, src), slurm=slurm, ie=ie,
                         N=p["N"], beta=p["beta"], mu=p["mu"], eps=p["eps"], nu=p["nu"], generations=p["generations"],
                         replicates=R, sampled_generations=p["generations"] // 2,
                         isl_first=p["isl_first"], isl_last=p["isl_last"], isl_step=3, seed_base=s0,
                         seed_min=seeds[0], seed_max=seeds[-1] + R - 1, display_items=items, note=note))
    return rows, per_game


def fmt(v):
    if isinstance(v, float):
        return repr(v)
    s = str(v)
    assert "," not in s and '"' not in s, s
    return s


COLS = ["run", "memory", "kit", "source", "slurm", "ie", "N", "beta", "mu", "eps", "nu", "generations", "replicates",
        "sampled_generations", "isl_first", "isl_last", "isl_step", "seed_base", "seed_min", "seed_max",
        "display_items", "note"]
HEAD1 = """# The Wright-Fisher runs of the paper: parameters and random seeds, one row per run, read from the kit files by
# mkseeds.py (do not edit by hand).  Seed of replicate r (1..replicates) of task isl: seed_base + 10*(isl - 1) + r.
# Columns:
#   run                  run id used in this repository
#   memory               1: the 16 binary memory-one strategies; 2: the 65536 binary memory-two strategies
#   kit, source, slurm   the kit directory under kits/, its Fortran main program, the production Slurm script
#   ie                   the error-rate slot of the task decode (ie = mod(isl-1,3)+1): eps = epsv(ie) of the source
#   N, beta, mu, eps     population size, selection strength, mutation probability, execution-error rate
#   nu                   the probability that a mutation is global (uniform over the whole space); otherwise one of
#                        the 16 positions of the strategy is flipped (kit lm only; nu = 1 everywhere else)
#   generations          generations per replicate (itend); the second half is sampled: sampled_generations
#   replicates           independent replicates per game (one task = one game = all replicates)
#   isl_first..isl_last  the Slurm task indices of the 512 games, step isl_step, in game order ipt = 0..511
#   seed_base            s0 (parameter iseedb of the source, or of compile.sh for kit lm)
#   seed_min, seed_max   the smallest and the largest seed the run used
#   display_items        the figures and tables of the paper that the run feeds
#   note                 what the run is
"""
HEAD2 = """# The random seed of replicate 1 of every game in every run; replicate r used that seed + (r - 1).  Written by
# mkseeds.py from the kit files (see SEEDS.csv for the parameters of each run).  Rows: the 512 games in ipt order.
# Columns:
#   ipt              game index 0..511 (data/games/games.csv)
#   gid              the game id in games.dat and in every packed run: 2000 + ipt
#   isl_m2_e4        task index of the game in the memory-two kits at eps = 1e-4 (ie = 3): 1368 + 3*ipt
#   isl_m2_e3        ... at ie = 2 (eps = 1e-3 in eh/el): 1367 + 3*ipt
#   isl_m2_e5        ... at ie = 1 (eps = 1e-5 in eh/el): 1366 + 3*ipt
#   isl_m1           task index of the game in the memory-one kit mw (ie = 3): 3 + 3*ipt
#   <run>            first seed of the game in that run (one column per row of SEEDS.csv)
"""


def write(rows, per_game):
    a = HEAD1 + ",".join(COLS) + "\n" + "".join(",".join(fmt(r[c]) for c in COLS) + "\n" for r in rows)
    cols = ["ipt", "gid", "isl_m2_e4", "isl_m2_e3", "isl_m2_e5", "isl_m1"] + [r["run"] for r in rows]
    lines = [HEAD2, ",".join(cols) + "\n"]
    for i in range(NGAME):
        v = [i, 2000 + i, 1368 + 3 * i, 1367 + 3 * i, 1366 + 3 * i, 3 + 3 * i] + [per_game[r["run"]][i] for r in rows]
        lines.append(",".join(str(x) for x in v) + "\n")
    return a, "".join(lines)


def main():
    rows, per_game = build()
    a, b = write(rows, per_game)
    pa, pb = os.path.join(HERE, "SEEDS.csv"), os.path.join(HERE, "seeds_by_game.csv")
    if "--check" in sys.argv:
        ok = open(pa).read() == a and open(pb).read() == b
        print("SEEDS.csv and seeds_by_game.csv %s the kit files" % ("agree with" if ok else "DIFFER FROM"))
        return 0 if ok else 1
    open(pa, "w").write(a); open(pb, "w").write(b)
    print("%-14s %-4s %5s %6s %7s %7s %4s %10s %3s %10s   %s" % ("run", "kit", "N", "beta", "mu", "eps", "nu",
                                                                  "gens", "rep", "seed_base", "seeds"))
    for r in rows:
        print("%-14s %-4s %5d %6g %7g %7g %4g %10d %3d %10d   %d..%d" % (r["run"], r["kit"], r["N"], r["beta"], r["mu"],
              r["eps"], r["nu"], r["generations"], r["replicates"], r["seed_base"], r["seed_min"], r["seed_max"]))
    # seed ranges that coincide between runs
    rng = [(r["run"], r["seed_min"], r["seed_max"]) for r in rows]
    for i in range(len(rng)):
        for j in range(i + 1, len(rng)):
            x, y = rng[i], rng[j]
            if x[1] <= y[2] and y[1] <= x[2]:
                sx = set(s + k for s in per_game[x[0]] for k in range(10))
                sy = set(s + k for s in per_game[y[0]] for k in range(10))
                print("shared seeds: %-14s %-14s %5d of %d" % (x[0], y[0], len(sx & sy), len(sx)))
    print("wrote %s and %s" % (os.path.basename(pa), os.path.basename(pb)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
