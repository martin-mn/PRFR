#!/usr/bin/env python3
"""
mkchecksums.py -- write ../../simulator/CHECKSUMS.sha256, the sha256 of every packed file of the memory-two runs of
the paper: for each of the 17 runs its .idx, .bin, .win and (for the kits that write the per-replicate file) .rep.

The packs are the private full outputs of the runs (author's environment, the one variable AUTHOR_ENV below; this
script only reads them).  The per-strategy abundance histograms (.bin, 65536 float32 per game) are not deposited, but
every run can be regenerated from its kit and seeds (../../simulator/), and these checksums let anyone who does so
check the regenerated pack bit for bit against the one the paper used.  pack.py writes the four files from a run
directory; the run name is the one of ../../simulator/SEEDS.csv, the pack name the one pack.py gives it.

Format: that of sha256sum, one line "<sha256>  <run>/<pack file>" per file, with the run as the directory of the file;
lines starting with # are comments.  To check a regenerated pack, put its files in a directory named after the run:

    grep -v '^#' CHECKSUMS.sha256 | grep ' f1/' | sha256sum -c        (shasum -a 256 -c on macOS)

Two further checks are printed (log: mkchecksums.log): the 512 games of the regenerations f1 and f2 against the
original packs of dw1 and dw2, game by game (the .idx line, the 256 kB block of the .bin and the ten .win lines of
every game identical), since dw1's pack also holds the 455 games of the companion work and so differs as a file.

    python3 mkchecksums.py            (about 10 s; reads 2.4 GB)
"""
import hashlib, os, sys

# ---- author's environment: where the private packs are ---------------------------------------------------------
AUTHOR_ENV = "/Users/martin/Documents/CL1"
# ------------------------------------------------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir, "simulator", "CHECKSUMS.sha256"))

PR, PR1, M2 = "PartnersRivals/Data", "PartnersRivals1/Cannon/lm/packed", "DiskM2WF/Data"
# run (SEEDS.csv), kit, the pack's directory and name, whether the kit writes the per-replicate file (.rep)
RUNS = [
    ("m2_N1000", "dw1", M2, "dw1_e4", False), ("m2_N100", "dw2", M2, "dw2_e4", False),
    ("f1", "f1", PR, "f1_e4", True), ("f2", "f2", PR, "f2_e4", True),
    ("dw3", "dw3", PR, "dw3_e4", False), ("dw4", "dw4", PR, "dw4_e4", False),
    ("c1", "c1", PR, "c1_e4", True), ("c2", "c2", PR, "c2_e4", True), ("c3", "c3", PR, "c3_e4", True),
    ("c4", "c4", PR, "c4_e4", True),
    ("eh_e3", "eh", PR, "eh_e3", True), ("eh_e5", "eh", PR, "eh_e5", True),
    ("el_e3", "el", PR, "el_e3", True), ("el_e5", "el", PR, "el_e5", True),
    ("lm_g0", "lm", PR1, "lm_g0_e4", True), ("lm_g01", "lm", PR1, "lm_g01_e4", True),
    ("lm_g05", "lm", PR1, "lm_g05_e4", True),
]
GAME = 65536 * 4                                   # bytes per game in a .bin


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def games(stem):
    """gid -> (the .idx line, the .bin block, the .win lines) of every game of a pack"""
    idx = [l for l in open(stem + ".idx") if not l.startswith("#")]
    win = {}
    for l in open(stem + ".win"):
        if not l.startswith("#"):
            win.setdefault(int(l.split()[0]), []).append(l)
    out = {}
    with open(stem + ".bin", "rb") as f:
        assert os.path.getsize(stem + ".bin") == len(idx) * GAME
        for l in idx:
            g = int(l.split()[0])
            out[g] = (l, f.read(GAME), win.get(g))
    return out


def main():
    lines = ["# sha256 of the packed output of the 17 memory-two Wright-Fisher runs of the paper (the per-strategy",
             "# abundance histograms .bin are not deposited; see simulator/README.md).  Format of sha256sum: one line",
             "# '<sha256>  <run>/<pack file>' per file, the run as in SEEDS.csv, the pack file as its kit's pack.py names it.",
             "# Check a regenerated pack in a directory named after its run:",
             "#     grep -v '^#' CHECKSUMS.sha256 | grep ' f1/' | sha256sum -c",
             "# Written by provenance/simulator-notes/mkchecksums.py from the packs the paper used.",
             "# run: kit, number of games in the pack, bytes of its four (or three) files"]
    body, tot, nfile = [], 0, 0
    for run, kit, d, stem, rep in RUNS:
        exts = ["idx", "bin", "win"] + (["rep"] if rep else [])
        p = os.path.join(AUTHOR_ENV, d, stem)
        assert os.path.exists(p + ".rep") == rep, "%s: .rep %s" % (run, "missing" if rep else "unexpected")
        ng = os.path.getsize(p + ".bin") // GAME
        size = sum(os.path.getsize(p + "." + e) for e in exts)
        lines.append("#   %-8s kit %-4s %4d games %11d bytes" % (run, kit, ng, size))
        for e in exts:
            body.append("%s  %s/%s.%s" % (sha(p + "." + e), run, stem, e))
            nfile += 1
        tot += size
    text = "\n".join(lines + body) + "\n"
    open(OUT, "w").write(text)
    print("wrote %s: %d files of %d runs, %.2f GB hashed" % (os.path.relpath(OUT, HERE), nfile, len(RUNS), tot / 1e9))

    ok = True
    for orig, new in (("dw1_e4", "f1_e4"), ("dw2_e4", "f2_e4")):
        A, B = games(os.path.join(AUTHOR_ENV, M2, orig)), games(os.path.join(AUTHOR_ENV, PR, new))
        same = all(g in A and A[g] == B[g] for g in B)
        ok &= same and len(B) == 512
        print("%s: its %d games against the same games of %s (%d games): .idx line, .bin block and .win lines %s"
              % (new, len(B), orig, len(A), "IDENTICAL for every game" if same else "DIFFER"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
