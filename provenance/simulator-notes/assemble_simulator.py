#!/usr/bin/env python3
"""
assemble_simulator.py -- how ../../simulator/ was assembled from the author's project tree (run once, 2026-09-24).

This script is a record, not a step a reader needs: it reads the private project tree, so it runs only in the
author's environment (the one variable AUTHOR_ENV below).  It copies every file of every cluster kit behind the
paper VERBATIM (byte for byte), except that:

  * the four Fortran files that every kit shares (payf2.f, payf3.f, mt.f, mtb.f) and the two game lists are stored
    once, in simulator/src/ and simulator/games/, after asserting that the copies in all kits are byte-identical;
    simulator/kits/stage.sh puts them back into a kit directory;
  * two generators get their input paths made relative to their own location (one asserted substitution each):
    lm/mklm.py (the absolute path of the f1 kit) and mw/mksf.py (the memory-one generator, which lived in
    DiskM1WF/Opt and read DiskM1WF/Ref/sf_dw1.f, a sha256-asserted copy of dw1/sf.f);
  * two generators are deposited with wording edited for the repository (2026-09-24): mkkits.py, the generator of
    eight kits, in its docstring, two comments and the README text that its readme() writes, and lm/mklm.py in its
    docstring.  This script does not overwrite these two deposited files: it asserts the sha256 of both versions of
    each and that every line in which they differ (for mklm.py, once its input path is made relative as above) is a
    line of the docstring, a comment or a line of readme(), so that the code that writes the kits is the author's.
    Run on a copy of simulator/kits/ after `bash stage.sh dw3`, the deposited mkkits.py rewrites every file of the
    eight kits other than README.md byte for byte, and after `bash stage.sh f1` the deposited mklm.py rewrites
    lm/sf.f and lm/pack.py byte for byte;
  * atoms512.bin (33.5 MB) is stored gzip-compressed (level 9, zero timestamp, so the archive is deterministic).

Not copied: run directories and outputs, log/, JOBID_*/IDX_* records (their numbers are in the kit READMEs),
backups (*.pre_vor), binaries, and each kit's own README.md, which was rewritten for the repository without the
author's cluster paths (the originals are summarised in simulator/kits/<kit>/README.md).

    python3 assemble_simulator.py            # writes into ../../simulator
"""
import gzip, hashlib, os, shutil, sys

# ---- author's environment: the private project tree ------------------------------------------------------------
AUTHOR_ENV = "/Users/martin/Documents/CL1"
# ------------------------------------------------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir, "simulator"))

PR = os.path.join(AUTHOR_ENV, "PartnersRivals", "Cannon")
PR1 = os.path.join(AUTHOR_ENV, "PartnersRivals1", "Cannon")
M2 = os.path.join(AUTHOR_ENV, "DiskM2WF", "Cannon")
M1 = os.path.join(AUTHOR_ENV, "DiskM1WF")

STD = ["sf.f", "compile.sh", "submit.sh", "verify.sh", "pack.py"]
KITS = {
    "dw1": (os.path.join(M2, "dw1"), STD + ["ident.slurm", "probe.slurm", "probe_vor.slurm", "prod_disk.slurm",
                                             "prod_disk_e4.slurm", "prod_sq.slurm", "prod_vor_e4.slurm",
                                             "prod_vor_e4_rest.slurm"]),
    "dw2": (os.path.join(M2, "dw2"), STD + ["probe_1e8.slurm", "probe_1e9.slurm", "prod_1e8.slurm", "prod_1e9.slurm"]),
    "dw3": (os.path.join(PR, "dw3"), STD + ["probe_1e7.slurm", "probe_1e8.slurm", "prod_1e7.slurm", "prod_1e8.slurm"]),
    "dw4": (os.path.join(PR, "dw4"), STD + ["probe_1e7.slurm", "prod_1e7.slurm"]),
    "eh": (os.path.join(PR, "eh"), STD + ["probe_e3.slurm", "probe_e5.slurm", "prod_e3.slurm", "prod_e5.slurm"]),
    "el": (os.path.join(PR, "el"), STD + ["probe_e3.slurm", "probe_e5.slurm", "prod_e3.slurm", "prod_e5.slurm"]),
    "lm": (os.path.join(PR1, "lm"), STD + ["lm.slurm"]),
    "mw": (os.path.join(M1, "Cannon", "mw"), ["sf1.f", "sf2.f", "sf1s.f", "sf2s.f", "compile.sh", "submit.sh",
                                              "verify.sh", "pack.py", "probe1.slurm", "probe2.slurm", "prod1.slurm",
                                              "prod2.slurm", "prod1s.slurm", "prod2s.slurm"]),
}
for k in ("c1", "c2", "c3", "c4", "f1", "f2"):
    KITS[k] = (os.path.join(PR, k), STD + ["probe_e4.slurm", "prod_e4.slurm"])

SHARED = ["payf2.f", "payf3.f", "mt.f", "mtb.f"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)               # keeps the executable bit of the shell scripts
    assert sha(src) == sha(dst)


def patched(src, dst, pairs):
    t = open(src).read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, "%s: anchor occurs %d times: %r" % (src, n, old[:60])
        t = t.replace(old, new)
    open(dst, "w").write(t)
    shutil.copymode(src, dst)


MKKITS = ("3f81510cca8de585a805fb03e989eec68af82b220135ec469d61b6ad51a6fa96",       # the author's file
          "9106e358b24702d4bd714f585b2c621bdcd2909d4ecaee7f29bae7fa2c00f887")       # the deposited file
MKLM = ("f15f9fecd87588c1f0ebde0f99d2edeefa7670eb1c302a70c5bae9bd747d79ef",         # the author's file
        "1a8bd2ddefb8ca0c8ced199ce8f683b9b0631a91a1cd93c39d896d8c51559f9e")         # the deposited file


def wording(lines):
    """indices of the lines of a generator that are its docstring, a comment, or part of its function readme()"""
    out, i = set(), 0
    if lines[0].startswith("#!"):
        out.add(0); i = 1
    if lines[i].startswith('"""'):
        j = i + 1
        while not lines[j].startswith('"""'):
            j += 1
        out |= set(range(i, j + 1))
    inside = False
    for k, ln in enumerate(lines):
        if ln.startswith("def "):
            inside = ln.startswith("def readme(")
        if inside or ln.lstrip().startswith("#"):
            out.add(k)
    return out


def check_wording(name, src, dep, shas, pairs=()):
    """the deposited generator dep differs from the author's src in wording lines only, once the asserted
    substitutions pairs (old, new) are made in the author's file"""
    import difflib
    assert (sha(src), sha(dep)) == shas, "%s: not the two versions this record describes" % name
    t = open(src).read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, "%s: anchor occurs %d times: %r" % (name, n, old[:60])
        t = t.replace(old, new)
    a, b = t.split("\n"), open(dep).read().split("\n")
    wa, wb = wording(a), wording(b)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            assert set(range(i1, i2)) <= wa and set(range(j1, j2)) <= wb, "%s: a code line differs" % name
    print("%s: the deposited file differs from the author's in wording lines only%s"
          % (name, " (after %d asserted substitution%s)" % (len(pairs), "s" * (len(pairs) > 1)) if pairs else ""))


def main():
    # 1. the shared sources and game lists: identical in every kit, stored once
    for f in SHARED:
        h = {sha(os.path.join(d, f)) for d, _ in KITS.values()}
        assert len(h) == 1, "%s differs between kits" % f
        copy(os.path.join(KITS["f1"][0], f), os.path.join(SIM, "src", f))
    h2 = {sha(os.path.join(d, "games.dat")) for k, (d, _) in KITS.items() if k != "mw"}
    assert len(h2) == 1, "games.dat differs between the memory-two kits"
    copy(os.path.join(KITS["f1"][0], "games.dat"), os.path.join(SIM, "games", "games.dat"))
    copy(os.path.join(KITS["mw"][0], "games.dat"), os.path.join(SIM, "games", "games_m1.dat"))

    # 2. every kit's own files, verbatim
    for k, (d, files) in sorted(KITS.items()):
        for f in files:
            copy(os.path.join(d, f), os.path.join(SIM, "kits", k, f))
        print("%-4s %2d files from %s" % (k, len(files), os.path.relpath(d, AUTHOR_ENV)))

    # 3. the generators
    check_wording("mkkits.py", os.path.join(PR, "mkkits.py"), os.path.join(SIM, "kits", "mkkits.py"),
                  MKKITS)                                                                  # already relative (HERE/dw3)
    check_wording("lm/mklm.py", os.path.join(PR1, "lm", "mklm.py"), os.path.join(SIM, "kits", "lm", "mklm.py"), MKLM,
                  [('F1 = pathlib.Path("%s")' % os.path.join(AUTHOR_ENV, "PartnersRivals", "Cannon", "f1"),
                    'F1 = HERE.parent / "f1"          # repository layout: simulator/kits/f1 (author\'s tree: PartnersRivals/Cannon/f1)')])
    patched(os.path.join(M1, "Opt", "mksf.py"), os.path.join(SIM, "kits", "mw", "mksf.py"),
            [('SRC = os.path.join(HERE, os.pardir, "Ref", "sf_dw1.f")',
              'SRC = os.path.join(HERE, os.pardir, "dw1", "sf.f")      # repository layout (author\'s tree: DiskM1WF/Ref/sf_dw1.f, a sha256-asserted copy)'),
             ('KIT = os.path.join(HERE, os.pardir, "Cannon", "mw")',
              'KIT = HERE                                              # repository layout (author\'s tree: DiskM1WF/Cannon/mw)')])

    # 4. the atom of every strategy at every game, for pack.py's per-replicate shares
    src = os.path.join(PR, "atoms512.bin")
    raw = open(src, "rb").read()
    assert len(raw) == 512 * 65536
    assert hashlib.sha256(raw).hexdigest().startswith("dccd19ca")
    dst = os.path.join(SIM, "atoms", "atoms512.bin.gz")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as fo:
        with gzip.GzipFile(filename="atoms512.bin", mode="wb", compresslevel=9, fileobj=fo, mtime=0) as g:
            g.write(raw)
    assert gzip.open(dst).read() == raw
    print("atoms512.bin.gz: %d bytes (from %d)" % (os.path.getsize(dst), len(raw)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
