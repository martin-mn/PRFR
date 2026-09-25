#!/usr/bin/env python3
"""make_census_data.py -- how data/census/ was made from the author's full census outputs, and the checks run on them.

    python3 make_census_data.py          (about 15 s; runs only in the author's environment)

It reads the private raw outputs of the exact census run (not deposited: 8192 files, 32 MB, which census/cannon/ and
the two programs regenerate) and writes the deposited tables of data/census/ with census/reduce.py; then

  1. runs census/compare.py on the raw outputs (exact against double, and the paper's counts), which must end in
     "ALL AGREE";
  2. compares the six masks of the new data/census/m2_masks.npz with those of the first, independent computation of
     2026-09-03 (the file the figure scripts read before), bit for bit;
  3. compares families/families.txt, as families/families.py writes it from data/census/, with the original.

Everything outside this repository is reached through AUTHOR_ENV and nothing there is written.
"""
import os
import subprocess
import sys

import numpy as np

# ---------------------------------------------------------------- the author's environment (the only private path)
AUTHOR_ENV = "/Users/martin/Documents/CL1"
RAW = os.path.join(AUTHOR_ENV, "PartnersRivals1", "Cannon", "xq", "full_out", "out")     # Cannon job 48068392
MASKS_FIRST = os.path.join(AUTHOR_ENV, "PartnersRivals", "Figures", "m2_masks.npz")        # pairs.c, 2026-09-03
FAMILIES_FIRST = os.path.join(AUTHOR_ENV, "PartnersRivals", "check", "families.txt")
# --------------------------------------------------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
DATA = os.path.join(ROOT, "data", "census")
PY = [sys.executable, "-B"]


def run(args, cwd):
    print("$ (cd %s && %s)" % (os.path.relpath(cwd, ROOT), " ".join(os.path.basename(a) if i == 0 else a
                                                                     for i, a in enumerate(args))))
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr)
        raise SystemExit("failed")
    return r.stdout


ok = True
out = run(PY + [os.path.join(ROOT, "census", "reduce.py"), RAW, DATA], os.path.join(ROOT, "census"))
print(out)
out = run(PY + [os.path.join(ROOT, "census", "compare.py"), RAW, "512"], os.path.join(ROOT, "census"))
print(out)
ok &= out.strip().endswith("ALL AGREE")

a, b = np.load(os.path.join(DATA, "m2_masks.npz")), np.load(MASKS_FIRST)
for k in ("effCC", "effALT", "rivP", "rivM", "defP", "defM"):
    same = a[k].dtype == b[k].dtype and a[k].shape == b[k].shape and bool((a[k] == b[k]).all())
    ok &= same
    print("m2_masks %-6s  new (exact census + Floyd-Warshall) == first computation (2026-09-03): %s" % (k, same))

run(PY + [os.path.join(ROOT, "families", "families.py")], os.path.join(ROOT, "families"))
same = open(os.path.join(ROOT, "families", "families.txt")).read() == open(FAMILIES_FIRST).read()
ok &= same
print("families.txt written from data/census == the original families.txt: %s" % same)
print("\nALL AGREE" if ok else "\nDISAGREEMENT FOUND")
sys.exit(0 if ok else 1)
