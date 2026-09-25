# provenance/simulator-notes — how `simulator/` and `notes/` were made

The scripts here read the author's private project tree and are kept as the record of how the deposited files were
made; they are not needed to use the repository. Each points at the private sources through one variable at its top,
marked "author's environment" (`AUTHOR_ENV`, or for `mknotes.py` `PASSAGES`, read from the environment variable
`PRFR_PASSAGES`). Everything else they read or write is inside the repository.

| file | what | run on 2026-09-24 |
|---|---|---|
| `assemble_simulator.py` | copies every file of the fourteen cluster kits verbatim into `simulator/kits/`, after asserting that the four shared Fortran files and the game list are byte-identical in all kits, stores those once in `simulator/src/` and `simulator/games/`, makes the input paths of two generators relative, checks that the deposited `mkkits.py` and `lm/mklm.py` differ from the author's in wording lines only (for `lm/mklm.py` once its input path is made relative), and writes `simulator/atoms/atoms512.bin.gz` | yes; a staged copy of `simulator/kits/` was then compared with the author's kit directories: 188 files, none different; re-run into a scratch folder after the wording checks were added: both pass, and all 126 files it writes are identical to the deposited ones |
| `check_seeds_vs_packs.py` | checks `simulator/SEEDS.csv` against the packed outputs of all 21 runs (task index of every game, replicates, total sample count) | yes: 21 of 21 consistent (`check_seeds_vs_packs.log`) |
| `mkchecksums.py` | writes `simulator/CHECKSUMS.sha256`, the sha256 of every packed file of the 17 memory-two runs, and compares the 512 games of the regenerations `f1` and `f2` with the original packs game by game | yes: 64 files; `f1` and `f2` identical to the originals (`mkchecksums.log`) |
| `mkatoms.py` | makes `atoms512.bin`, the ε → 0 atom of every strategy at every game, from the exact layer (the author's module DiskM2WF/Opt/exact.py) | yes: sha256 `dccd19ca…`, identical to the deposited file |
| `lineage/` | the companion paper's Wright–Fisher source and the generator that made the memory-two simulator from it | yes: reproduces the author's source byte for byte (`lineage/README.md`) |
| `mknotes.py` | writes the six `notes/*.md` from `notes_text.py` and the author's LaTeX of the passages, with the reference list and the label numbers of the manuscript; renames the second property from "Nash" to "stable" in every passage (`RENAMES` of `notes_text.py`) and refuses to write a note in which "Nash" occurs other than in "Nash equilibrium" or "Nash equilibria" outside its references | yes: 6 files, 11 passages (4 converted from the author's LaTeX, 7 given in `notes_text.py`), 1 edit; re-run on 2026-09-25 with the renames: 1 edit and 6 renames, and the notes differ from those of 2026-09-24 only in the name of the property |
| `latex2md.py` | the LaTeX-to-Markdown converter `mknotes.py` uses; it refuses unknown LaTeX | |
| `notes_text.py` | the text written for the notes, the passages each note uses (some of them in Markdown), the edits that bring the references of the others to the paper's numbering, and the renames of the second property (`RENAMES`) | |

The private sources: the kit directories `CL1/PartnersRivals/Cannon/{c1..c4, dw3, dw4, eh, el, f1, f2}` and the
generator `CL1/PartnersRivals/Cannon/mkkits.py`, `CL1/PartnersRivals1/Cannon/lm`, `CL1/DiskM2WF/Cannon/{dw1, dw2}`,
`CL1/DiskM1WF/Cannon/mw` and `CL1/DiskM1WF/Opt/mksf.py`; the packs in `CL1/PartnersRivals/Data`, `CL1/DiskM2WF/Data`,
`CL1/DiskM1WF/Data` and `CL1/PartnersRivals1/Cannon/lm/packed`; for the notes, the author's file of passages with the
manuscript's `refs.tex` and `ms.aux` next to it, and the working notes `CL1/PartnersRivals/Discounting/notes/definitions.md`
(read, not copied) for the discounting note; for the strategies of the Harmony bays, the record in
`CL1/PartnersRivals/Figures/README.md` (2026-09-17).
