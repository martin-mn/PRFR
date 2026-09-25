# lineage — where the memory-two simulator came from

The Wright–Fisher code of this paper is the code of the companion paper on the donation game (reference WFpaper of the
manuscript, arXiv:2608.06147) with the donation game replaced by a list of arbitrary games. This folder records that
step, so that the claim of the kit README of `simulator/kits/dw1` ("the generation loop is untouched") can be checked.

| file | what |
|---|---|
| `sf_wf3.f` | the main program of the companion project's run `wf3` (the donation game on a grid of 99 costs), the author's reference copy (DiskM2WF/Ref/sf_wf3.f); byte for byte as used |
| `mksf_dw1.py` | the generator that turned it into `dw1/sf.f` (DiskM2WF/Opt/mksf.py): twelve named, asserted substitutions and one regex deletion; the game list, the task decode, the seed base and the output headers change, the generation loop does not. Its two paths were made relative: the input is `sf_wf3.f` next to it, the output the path given on the command line |

```bash
python3 mksf_dw1.py /tmp/sf.f            # writes /tmp/sf.f (and, with --chk, /tmp/sfchk.f)
diff /tmp/sf.f ../../../simulator/kits/dw1/sf.f
```

Checked on 2026-09-24: the output is byte-identical to the author's `dw1/sf.f.pre_vor`, the source that ran the first
455 games of the dw1 campaign, and `diff` against the deposited `simulator/kits/dw1/sf.f` shows exactly one change:
the game-list capacity `mgam` raised from 512 to 2048 (with its explanatory comment) when the 512 sunflower games of
this paper were appended to `games.dat`. `mgam` dimensions the game list only; the rebuilt binary was tested
bit-identical on a completed task on the cluster (kit dw1, `ident.slurm`). With `--chk` the generator also writes
`sfchk.f`, the build retuned to wf3's task order and seed base with which dw1 was shown to reproduce wf3 bit for bit;
that output is byte-identical to the author's copy as well.
