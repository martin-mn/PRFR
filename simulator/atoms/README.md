# simulator/atoms — the atom of every memory-two strategy at every game

`atoms512.bin.gz` (608,874 bytes) unpacks to `atoms512.bin`, 33,554,432 bytes, sha256
`dccd19ca4d886b142a3fdf11eb3ed945986ad29624cd60b4a0b36a3c891b3fe6`:

- 512 blocks of 65536 bytes, one block per game in ipt order 0..511 (gid 2000 + ipt);
- byte s of block ipt is the atom of the memory-two strategy with code s (0..65535) at that game, in the limit ε → 0,
  written as the integer `4·efficient + 2·stable + competitive` (0..7). The code 5, the atom `101`, never occurs.

It is the input with which each kit's `pack.py` turns the 65536 counts of every replicate (the r-file) into that
replicate's seven atom shares, the `.rep` file. `bash ../kits/stage.sh <kit>` unpacks it to `../kits/atoms512.bin`, the
path the kits' `pack.py` read by default (`../atoms512.bin` from a kit directory). To read it in Python:

```python
import gzip, numpy as np
A = np.frombuffer(gzip.open("atoms512.bin.gz").read(), dtype=np.uint8).reshape(512, 65536)
```

How it was made: from the exact ε → 0 layer (efficiency from each strategy's self-play, rivalry from the rival masks
for T > S and T < S, stability from the exact arrangement of the companion work) by
`provenance/simulator-notes/mkatoms.py`, which needs the author's environment. Re-run on 2026-09-24, it reproduced
the file bit for bit (same sha256). The per-game atom sizes that the figures use are deposited as tables in `data/`.
