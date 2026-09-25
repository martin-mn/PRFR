# provenance/census-figs: how data/arrangement/ was made

`reduce.py` wrote every file in `../../data/arrangement/` from the author's working files. The figure scripts
(`Figure1/`, `Figure2/`, `Figure3/`) and the checker `data/arrangement/check.py` do not need it. It is kept as the
record of where the deposited numbers come from.

```
python3 reduce.py          # about 15 s; only in the author's environment
```

It reads the private files through one variable, `AUTHOR_ENV` (the author's project tree), set at the top of the
script. Nothing else in the repository points outside it. Running it again rewrites `data/arrangement/` byte for
byte. This was checked on 2026-09-24, and again on 2026-09-25, after the header comments it writes were changed to
call the second property "stable".

## The chain

| step | program | output | deposited as |
|---|---|---|---|
| 1 | NEmap's exact census, by the Markov chain tree theorem in integer arithmetic (companion repository [MapBinM2](https://github.com/martin-mn/MapBinM2), `exact/`) | `ca1_regions.csv`: the stability region of each of the 65536 memory-two strategies (polygon facets, tie line, tie point) | `m2_nash_facets.csv`, `m2_nash_lowdim.csv`, `nash_dim` of `m2_strategies.csv` |
| 2 | MapBinM2 `Figure3/computation/arrangement/p3disk.py` | `ca4_arrangement_k4.npz`: the arrangement of the 254 facet lines on the K = 4 disk, as 27598 polygons (22872 faces, 771 of them cut into bands for a field of the companion paper), with `N` and `NEFF` per polygon | `m2_faces_k4.npz` (vertices unchanged), `nash` (the number of stable strategies) and `partners` of `m2_faces.csv` |
| 3 | this paper's pair computation, `PartnersRivals/check/pairs.c` in its first run of 2026-09-03; it is byte-identical to the deposited `census/pairs.c` | `m2_masks.npz`: self-play efficiency (`effCC`, `effALT`) and rivalry (`rivP`, `rivM`) of the 65536, bit-identical to the deposited `data/census/m2_masks.npz` | `eff_cc`, `eff_alt`, `riv_plus`, `riv_minus` of `m2_strategies.csv` |
| 4 | `PartnersRivals/Figures/count6.py` with `DiskM2WF/Opt/exact.py` (the census of step 1, and a rival mask equal to `rivP`) | `Count6_faces.npz`: the eight atom counts on each of the 27598 polygons, evaluated at one interior game of each | `A_*` of `m2_faces.csv`, `open_*` of `m2_strategies.csv` |
| 5 | `FinalFigures/m1atoms.py` (this paper) | `m1_atoms_k4.npz`: the memory-one arrangement | `m1_faces_k4.npz`, `m1_faces.csv`, `m1_lines.csv` |
| 6 | `reduce.py` (here) | numbers the cells and the 19 cases | `m2_cells.csv`, `m2_lines.csv`, `cases.csv`, `case` columns |

## Checks made before anything is written

`reduce.py` asserts these points:

- The efficiency of step 3 equals the self-play distributions of step 1.
- Every one of the 27598 polygons lies strictly on one side of each of the 254 lines. All its vertices were mapped back
  to the plane for this, and the largest excursion across a line is 2.3e-13 relative. The polygons carry 22872
  distinct sign vectors.
- The number of stable strategies, the partner count and the eight atom counts of every polygon follow from the facets of step 1, the
  sign vectors and the masks of step 3. They equal step 2's `N` and `NEFF` and step 4's `ATOMS`, `ATOM_TOTAL` and
  `NE_TOTAL`.

The pipeline of step 4 evaluated floating-point facets at one interior point per face. The route here is combinatorial
and integer, and it agrees on every face. `count6.py` and `exact.py` are therefore not deposited.

Step 5 is reproduced from scratch by `data/arrangement/m1atoms.py`, bit for bit.
