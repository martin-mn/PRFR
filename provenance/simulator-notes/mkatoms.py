#!/usr/bin/env python3
"""
mkatoms.py -- how simulator/atoms/atoms512.bin.gz was made: the exact eps -> 0 atom of every one of the 65536 binary
memory-two strategies at each of the 512 games, one byte per strategy (code = 4*efficient + 2*stable + competitive,
0..7; 5 never occurs), games in ipt order 0..511, 512 x 65536 bytes.  The kits' pack.py reads it to turn each
replicate's 65536 counts into the replicate's seven atom shares (the .rep files).

This is the author's PartnersRivals/Cannon/mkatoms.py with its inputs made explicit; the code that computes the
codes is unchanged.  It needs the exact eps -> 0 layer of the companion work (the stability regions, the self-play
weights and the rival mask), which the private module DiskM2WF/Opt/exact.py loads; hence the one author's-environment
variable below.  The games are read from the repository's simulator/games/games.dat (rows 456-967; cR = 1 there, so
u = cS and v = cT - 1 exactly).

    python3 mkatoms.py [out]      # default out: ./atoms512.bin ; prints the sha256 (dccd19ca... for the deposited file)
"""
import hashlib, os, sys
import numpy as np

# ---- author's environment: the module that loads the exact eps -> 0 layer -------------------------------------
AUTHOR_OPT = "/Users/martin/Documents/CL1/DiskM2WF/Opt"
# ------------------------------------------------------------------------------------------------------------------
sys.path.insert(0, AUTHOR_OPT)
import exact  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES = os.path.join(HERE, os.pardir, os.pardir, "simulator", "games", "games.dat")
out_path = sys.argv[1] if len(sys.argv) > 1 else "atoms512.bin"

rows = [l.split() for l in open(GAMES) if l.strip() and not l.lstrip().startswith("#")]
V = [r for r in rows if r[7].startswith("V_p")]
assert len(V) == 512
d = exact.load()
out = np.zeros((512, 65536), dtype=np.uint8)
cnt = np.zeros((512, 8), dtype=np.int64)
for r in V:
    ipt = int(r[7].split("_")[1][1:]); assert int(r[0]) == 2000 + ipt
    cR, cS, cT = float(r[2]), float(r[3]), float(r[4]); assert cR == 1.0
    u, v = cS, cT - 1.0
    assert abs(u - float(r[5])) < 1e-9 and abs(v - float(r[6])) < 1e-9, (ipt, u, v, r[5], r[6])
    eff, riv, ne = exact.masks(d, u, v)
    code = 4 * eff.astype(np.uint8) + 2 * ne.astype(np.uint8) + riv.astype(np.uint8)
    out[ipt] = code
    cnt[ipt] = np.bincount(code, minlength=8)
assert not cnt[:, 5].any(), "atom 101 occupied somewhere"
assert (cnt.sum(1) == 65536).all()
print("111 counts over the cells:", sorted(set(cnt[:, 7].tolist())))
out.tofile(out_path)
print("%s: %d bytes, sha256 %s" % (out_path, os.path.getsize(out_path),
                                   hashlib.sha256(open(out_path, "rb").read()).hexdigest()))
