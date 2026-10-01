# Changelog

## 1.1.0 (2026-10-01)

Release 1.1.0 accompanies the revised manuscript of 2026-09-30. Its data are those of release 1.0.0. Three things
changed: Figures 2 and 3 are set for the printed page, the pointers to the paper follow the revised manuscript, and
`data/runs/check_numbers.py` checks only numbers that the revised manuscript quotes at the place it names.

### Figures 2 and 3 set for the page

- `fig2.py` and `fig3.py` set their sheets for a page 6.89 in (17.5 cm) wide. Printed at that width, the type set in a
  font is at least 6 pt, the guide labels are 5.5 pt and the rim names 5.0 pt. In release 1.0.0 the type printed at
  that width ran from 2.4 to 5.8 pt.
- The panels, letters, data and band boundaries of every colour scale are those of release 1.0.0. The colour bars are
  as tall as the disk (0.85 PW, was 0.80 PW), and their grey triangle is 0.14 of the bar (was 0.06). The ramps of
  Figure 2 **j**, **l** and **m** and of Figure 3 **f** and **h** label fewer intermediate values. The long heads and
  the line under each disk are set on two lines. `Figure2/README.md` and `Figure3/README.md` give every size.
- `fig2.py --wide` and `fig3.py --wide` draw the sheets of release 1.0.0, byte for byte apart from the creation date
  of the PDF.
- The deposited previews `Figure2/Fig2.png` and `Figure3/Fig3.png` are those of the page version.
- The code: `common/counts.py` gained `page_type`, `WIDE`, the `ty` arguments and two more text checks in `finish`;
  `common/furniture.py` gained `TYPE` and `ty`. Without `ty`, every figure is drawn as in release 1.0.0. `.gitignore`
  lists the files that `--wide` writes. The docstrings of `fig2.py` and `fig3.py` no longer say that only the data
  loading changed, those of `common/counts.py` and `common/README.md` record the page type added on 2026-09-30, and
  all four call the sheets drawn without `ty` "as in release 1.0.0".
- The verification notes in `README.md`, `Figure2/README.md` and `Figure3/README.md` say which manuscript each PDF
  matches: the `--wide` sheets those of the manuscript that release 1.0.0 accompanied, the page version Figures 2 and
  3 of the revised manuscript. The two folder READMEs give a command that compares the `--wide` previews with those
  of release 1.0.0 in a git clone, since `reproduce_all.sh` draws only the page version. The table of display items
  in `README.md` lists `--wide`.

### The pointers to the paper

The revised manuscript changed where some things are:

- The Methods open the Supplementary Information. The main text calls them "SI Methods" and keeps a short summary.
- Detail from the legends of main text Figures 1 to 5 moved to the SI paragraph "Notes to main text Figures 1 to 5".
- Some numbers moved from the Results to the SI Methods and to SI §9 ("The evolutionary maps") and §10 ("Memory one,
  for contrast"), and the memory-one count 324 (games with efficiency below 0.9 at N = 1000) is no longer quoted.

The READMEs, and the docstrings, comments and printed headings of the check scripts, now point to the SI Methods
where they pointed to "the Methods", and to the SI notes where they pointed to a legend. These files changed for it:

- `README.md`, `reproduce_all.sh` (the label of one step);
- `Figure1/README.md`, `Figure2/README.md`, `Figure3/README.md`, `Figure4/README.md`, `Figure5/README.md`,
  `SIFigure2/README.md`, `SIFigure3/README.md`;
- `census/README.md`, `census/check.py`; `families/README.md`; `notes/README.md`; `simulator/README.md`,
  `simulator/mkseeds.py`;
- `data/arrangement/README.md` and `check.py`, `data/robustness/README.md`, `data/runs/README.md`,
  `data/strict/README.md` and `check_strict.py`.

The data-file headers, the notes and the provenance record keep the wording of release 1.0.0, so that every data
file stays byte-identical and every provenance script still writes exactly the deposited headers. In them "the
Methods" is the Methods section of the paper, which in the revised manuscript opens the Supplementary Information.
The section "Conventions" of `README.md` says so.

`data/strict/recompute_sets.py` named the companion code repository as a paper cited in the Methods. It now names the
companion paper, bioRxiv 2026.09.05.749606, and gives the code repository separately.

### `data/runs/check_numbers.py`: 134 checks (was 146)

- **Dropped, 12 checks.** The five labelled "Abstract" and the five labelled "Conclusion" repeated checks of the
  Results: the Abstract quotes none of these numbers, and the Conclusion states them in words, if at all. The check of
  the memory-one count 324 is dropped because the number is no longer quoted. Its complement, 188 games with
  efficiency above 0.9, is quoted in the SI Methods and still checked. The check of the ranking of the memory-one atoms
  by the games they lead is dropped because its sentence left the Results. SI §10 gives the same ranking as ordered
  counts, and they are still checked.
- **Relabelled, 38 checks**, with the numbers and the code unchanged. The 24 checks labelled "Methods" are now "SI
  Methods". Ten memory-one checks moved from "Results" to "SI m1" (SI §10) and one to "SI Methods". Two memory-two
  checks moved from "Results" to "SI evol." (SI §9). The check that at memory one no strategy is stable exactly at the
  Snowdrift games outside the unit square moved from "Fig. 5" to "SI notes".
- The docstring lists the new places. The final line keeps its form: "134 numbers checked: 134 agree with the text,
  0 differ".
- `README.md` and `data/runs/README.md` give the new count and the new list of places.

### Version metadata

- `CITATION.cff`: version 1.1.0, released 2026-10-01. Its `doi` is the concept DOI 10.5281/zenodo.22964492, which
  resolves to the latest release. The DOI of release 1.1.0 is added once Zenodo has minted it, as it was for release
  1.0.0. `identifiers` keeps the DOI of release 1.0.0 and the concept DOI.
- `.zenodo.json`: version 1.1.0.
- `README.md`: the archive line and "How to cite".
- This file is new.

### Unchanged

- Every data file under `data/`, `census/`, `families/` and `simulator/` (the CSV tables with their headers, the
  `.npz` files, the game lists, `atoms512.bin.gz`, the seed tables and `CHECKSUMS.sha256`).
- The six notes (`notes/*.md` other than `notes/README.md`), their checks and logs (`notes/checks/`), `provenance/`,
  the simulator kits (`simulator/kits/`, `simulator/src/`, `simulator/games/`, `simulator/atoms/`) and `LICENSE`.
- Every figure and table other than Figures 2 and 3. `reproduce_all.sh` (43 steps) rewrites them identical to the
  deposited files, the PDFs apart from their creation date (SI Figure 1 apart from its dates and its /ID).

## 1.0.0 (2026-09-25)

The first release: the code and data for the manuscript of 2026-09-25. Tag `v1.0.0`, commit `f3747b5`. Archived on
Zenodo as doi:10.5281/zenodo.22964493 (all versions: doi:10.5281/zenodo.22964492). The commit after it, `68b68a3`,
added that DOI to `CITATION.cff` and `README.md`.
