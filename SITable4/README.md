# SITable4 — the families of friendly rivals

This folder reproduces SI Table 4 (SI §7).
- **a:** the single family of the wedge W, `111*000101*1*010`, 8 strategies.
- **b:** the four families of the wedge N, two of 32 and two of 16 strategies, with their 4×4 tables. The rows are the
  most recent outcome and the columns the outcome before, own action first.
- **E:** the families of the wedge E are the mirror images of those of N.

    python3 sitable4.py          (about 2 s; numpy, scipy >= 1.9)

- **Input:** `../data/census/census.csv`, through the functions of `../families/families.py`, plus
  `../families/covers.csv` for comparison.
- **Output:** the table printed next to the paper's, `SITable4.txt` (the table in text form) and `SITable4.csv`
  (pattern, members and the four rows of each family). The exit status is 1 on any mismatch.

**Method.** The prime patterns and the minimum covers of W and N are recomputed from the census; the cover of E is
recomputed too and checked against the mirror images of N. Each pattern is then checked directly against the set:
- every strategy the pattern names is in the set;
- no fixed position can be made a wildcard;
- the union of the cover is the set.

The script also checks the text of SI §7:
- for W: the eight codes, the wildcards at positions 3, 10 and 12, the four members that defect at (DC,DC), and the
  two fair members that are also in S;
- for N: the pairs differ only at (CC,CD) and (CC,DC), and from each other at three further states; the overlaps of 8,
  with 32+32+16+16−16 = 80; the common positions `****000**1*1*010`; cooperation at 4 to 9 states; the eight members
  shared with E;
- for S: 1519 strategies with 2 common positions; 56 primes with 4 to 9 wildcards; a non-unique cover of 42; the
  largest pattern `111*1***11*1****` with 512 members, among them ALLC and TF2T; WSLS and AON₂ not in S; the
  defensible reading with 1036 strategies, 33 primes and a cover of 24.

**Verification (2026-09-24).** The script was run from a fresh copy. The five patterns, their sizes and their five
4×4 tables agree with SI Table 4 of ms.tex, which was parsed directly. The mirror patterns agree with the four listed
in the text, and every text check agrees.
