# simulator/kits — the cluster kits exactly as they ran

One directory per kit. A kit is the Fortran main program of a run, the script that compiles it, the Slurm array
scripts, `submit.sh` (submits an array and records its id), `verify.sh` (completion per task from `sacct`) and
`pack.py` (packs a finished run directory; Python 3, standard library only). Every file is byte-identical to the file
that ran on the cluster, except the READMEs, which were written for the repository, two generator scripts whose
input paths were made relative (`lm/mklm.py`, `mw/mksf.py`; one line each, and the docstring of `lm/mklm.py` reworded
for the repository), and the generator `mkkits.py`, whose docstring, two comments and the text of the README it writes
were reworded for the repository (every other file it writes is unchanged; see below). Each kit's README gives its
parameters, seeds, files, protocol and the record of its arrays.

| kit | runs (see `../SEEDS.csv`) | display items | source |
|---|---|---|---|
| `dw1` | `m2_N1000`: memory two, N = 1000, β = 100, μ = 10⁻², 10⁷ generations | main text Fig. 4d–f, 5d–f; SI Fig. 3i–p, 6f, 7f, 8, 9d–f, 12j–l | from the companion paper's `wf3` (`provenance/simulator-notes/lineage/`) |
| `dw2` | `m2_N100`: memory two, N = 100, β = 3, μ = 10⁻⁴, 10⁸ generations | SI Fig. 3a–h, 4d–f, 5d–f, 6e, 7e, 8, 10d–f | `dw1/sf.f`, five parameter lines |
| `f1`, `f2` | the regenerations of dw1 and dw2 with per-replicate output, same seeds | SI Fig. 11 | `dw3/sf.f` via `mkkits.py` |
| `dw3`, `dw4` | cube corners (1000, 100, 10⁻⁴) and (1000, 3, 10⁻²) | SI Fig. 8, SI Table 7a | `dw2/sf.f`, parameter lines |
| `c1`–`c4` | the other four cube corners | SI Fig. 8, SI Table 7a | `dw3/sf.f` via `mkkits.py` |
| `eh`, `el` | the two main memory-two runs at ε = 10⁻³ and 10⁻⁵ | SI Fig. 9, 10, SI Table 7b | `dw3/sf.f` via `mkkits.py` |
| `lm` | the large-population run with the mixed mutation kernel, ν = 0, 0.1, 0.5 | SI Fig. 12, SI Table 7c | `f1/sf.f` via `lm/mklm.py` |
| `mw` | the two memory-one runs (and two convergence controls not in the paper) | main text Fig. 4a–c, 5a–c; SI Fig. 2, 4a–c, 5a–c, 6b–c, 7b–c | `dw1/sf.f` via `mw/mksf.py` |

## Staging

The four Fortran files every kit links (`payf2.f`, `payf3.f`, `mt.f`, `mtb.f`) and the game list are stored once, in
`../src/` and `../games/`. Before a kit is compiled or a generator is run:

```bash
bash stage.sh c1              # or: bash stage.sh all
bash stage.sh --clean all     # removes the staged copies again
```

`stage.sh` also unpacks `../atoms/atoms512.bin.gz` to `./atoms512.bin`, where the kits' `pack.py` look for it. A staged
kit directory is file for file the directory that ran (checked for all 188 files, 2026-09-24).

## The generators, and what they prove

- `mkkits.py` (in this folder) writes the kits `eh el c1 c2 c3 c4 f1 f2` from `dw3/` by asserted substitutions, each
  of which must apply exactly once: `python3 mkkits.py [kit ...]` (after `bash stage.sh dw3`). Run on a copy of this
  folder on 2026-09-24, it reproduced every `sf.f`, Slurm script, `compile.sh`, `submit.sh`, `verify.sh` and `pack.py`
  of those eight kits byte for byte (it also rewrites their README.md, with the author's paths). The deposited
  `mkkits.py` differs from the author's only in wording lines (its docstring, two comments and the function `readme()`,
  as `provenance/simulator-notes/assemble_simulator.py` asserts); re-run on a staged copy on 2026-09-24, it reproduced
  every file of the eight kits other than README.md byte for byte.
  `python3 mkkits.py test` builds dw3's parameters with gfortran at 10⁵ generations with and without the
  per-replicate count file, runs task 1902 with both and compares the outputs: summary, w- and h-file IDENTICAL, and
  the ten replicate blocks of the r-file sum exactly to the h-file (re-run 2026-09-24, 32 s).
- `lm/mklm.py` writes `lm/sf.f` and `lm/pack.py` from `f1/` (after `bash stage.sh f1`); reproduced byte for byte. Apart
  from its input path it differs from the author's only in its docstring (asserted by the same script).
- `mw/mksf.py` writes the four memory-one sources from `dw1/sf.f` (sha256 asserted); reproduced byte for byte.
- `dw1/sf.f` itself was generated from the companion paper's Wright–Fisher code; that generator and its input are in
  `provenance/simulator-notes/lineage/`, with the check.

## Author's cluster settings

The scripts are kept as they ran on Harvard's FASRC Cannon cluster. Cluster-specific are: the partition
(`#SBATCH -p shared`), the compiler module (`module load intel/25.2.1-fasrc01`; the compile line
`ifx -O3 -xHost -fp-model precise`), the job names and comments (`#SBATCH -J`, `--comment`), and the line of every
`submit.sh` that appends the submission to the author's cross-project ledger `~/jobs.tsv`. Adapt these for another
cluster; the simulation does not depend on them. No account name or path of the author's cluster is used by any
script; comments in the sources mention the author's project folders (DiskM2WF, DonationWF, PartnersRivals, ...) by
name.

**The job ledger.** As deposited, every `submit.sh` ends by appending one line (date, project, kit and tag, array id,
number of tasks, a note) to `~/jobs.tsv`, the author's record of submissions; the scripts are left as they ran. To make
that append conditional on the environment variable `PRFR_LEDGER`, run once, in this folder,

```bash
sed -i.orig 's|>> ~/jobs.tsv$|>> "${PRFR_LEDGER:-/dev/null}"|' */submit.sh
```

which changes that one line in each of the fourteen scripts (the originals are kept as `submit.sh.orig`). The line is
then written only if `PRFR_LEDGER` is set, to the file it names; `PRFR_LEDGER=~/jobs.tsv` restores what ran, and with
the variable unset nothing is written outside the kit (the script's closing message still says "ledger appended").
Nothing else in the scripts reads or needs the ledger. Tested 2026-09-24 on a copy of this folder: the substitution
applies once in each of the fourteen scripts, `bash -n` accepts them, and a submission with `sbatch` and `squeue`
replaced by stubs wrote no ledger line with `PRFR_LEDGER` unset and one line to the named file with it set.
