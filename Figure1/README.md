# Figure 1: The three properties, their atoms, and which atoms are empty at each game, for memory one and memory two

This folder reproduces main text Figure 1 from the exact ε → 0 arrangements in `../data/arrangement/`.

## What it shows

- **a** is the Euler diagram of the three properties in the general case. The efficient strategies are the blue
  circle, the competitive strategies the red circle and the stable strategies the dashed curve. All seven atoms appear,
  and the lens of the two circles lies inside the dashed curve, so atom 101 is empty.
- **b** is the disk of games for the 16 binary memory-one strategies. Every face of the arrangement is coloured by its
  case, the set of atoms that have members there.
- **c** is the same for the 65536 binary memory-two strategies.
- The key below the disks has one row per case. A present atom is a cell in the tint of panel a, carrying its code. An
  empty atom is a white cell with ∅.

The cases are numbered once for both disks: by the number of empty atoms, then by area. There are 19 in all, twelve at
memory one and ten at memory two, and three of them (7, 11 and 13) occur at both. `../data/arrangement/cases.csv`
lists them.

## Run

```
python3 fig1.py
```

The script writes `Fig1.pdf` and a 220-dpi preview `Fig1.png` here. It prints the 19 cases with their empty atoms
and their shares of the two disks, and takes about 9 s. The preview is not deposited.

## Files

| file | role |
|---|---|
| `fig1.py` | the plotting script |
| `eulerlib.py` | the Euler-diagram and disk-map drawing of Figure 1, with `euler()` and `draw_map()` |
| `Fig1.pdf` | the published figure (`figures/Fig1.pdf` of the paper), byte for byte |
| `../data/arrangement/m2_faces_k4.npz`, `m2_faces.csv` | input for **c**: the 22872 faces of the memory-two arrangement, drawn as 27598 polygons, and their seven atom counts |
| `../data/arrangement/m1_faces_k4.npz`, `m1_faces.csv` | input for **b**: the 45 memory-one faces, their interior games and atom counts |
| `../data/arrangement/arrangement.py` | reads those files in the shapes of the original loaders |
| `../common/disk.py` | the disk map, the rim names (`arc_text`) and `common.atoms.pieces` |

The script is the original `FinalFigures/fig1.py`. Only its data loading was replaced: the dump
`ca4_arrangement_k4.npz` and `Count6_faces.npz` for memory two, and `m1atoms.load()` for memory one. `eulerlib.py` is
the original too, with only its import of `disklib` replaced by `common.disk`.

Figure 1 does not import `common.furniture`, `counts` or `wfsheet`, because those modules set rcParams. It sets its
own rcParams, as the original did.

Requirements: Python 3 with numpy, matplotlib, scipy (`ndimage`, used to place the case numbers) and Pillow.

## Verification (2026-09-24)

The script was run on a fresh copy of `Figure1/`, `common/` and `data/arrangement/`. The software was Python 3.10.9,
numpy 1.23.5, matplotlib 3.7.0, scipy 1.10.0 and Pillow 9.4.0.

- `Fig1.pdf` is byte-identical to the published `figures/Fig1.pdf`, apart from its `CreationDate` stamp.
- The two PDFs were rasterised with `pdftoppm` at 80 and at 150 dpi. They are pixel-identical: max |diff| 0,
  mean |diff| 0.
- The preview `Fig1.png` it writes is byte-identical to the author's.

The printed case table matches the Methods and SI §8 ("Ten Euler diagrams"): ten cases at memory two (1–7, 9, 11, 13), twelve at memory one,
and 7, 11 and 13 shared.
