# simulator/src — the Fortran shared by every kit

These four files are linked into every binary of every run in `../kits/`. They were byte-identical in all fourteen
kits (checked by sha256 when the repository was assembled), so they are stored once; `../kits/stage.sh` copies them
into a kit directory.

| file | bytes | sha256 | what |
|---|---:|---|---|
| `payf3.f` | 2806 | `9d82c7fe…` | `payf3(isa, isb, w0, w1, w2, w3)`: the stationary distribution of the 16-state Markov chain of a pair of binary memory-two strategies playing with execution errors, by the state-reduction algorithm of Grassmann, Taksar and Heyman (subtraction-free, no pivoting), returned as the outcome frequencies `w0..w3` of CC, CD, DC, DD from the first player's view |
| `payf2.f` | 4160 | `197821fc…` | `payf2ini`, which tabulates the 256 possible 4 × 4 diagonal blocks of the transition matrix for the error rate held in `COMMON /epsval/ pmin, pmax` (`pmin = eps`, `pmax = 1 - eps`); call it once per error rate before `payf3`. (`payf2`, a pivoted-elimination routine with the same interface as `payf3`, is also in the file; no kit calls it.) |
| `mt.f` | 8480 | `5dba5e72…` | the Mersenne twister MT19937, Tsuyoshi Tada's FORTRAN77 translation (2005) of Matsumoto and Nishimura's `mt19937ar`; the kits use `init_genrand(seed)` |
| `mtb.f` | 2034 | `bf4c7b9b…` | `mtfill(rb, nb)`: fills `rb(1:nb)` with exactly the numbers that `nb` successive calls of `genrand_real3()` would return, uniform on (0, 1) with 32-bit resolution, without the per-call overhead |

A pair's payoffs follow from `payf3` as `R w0 + S w1 + T w2 + P w3`, with P = 0 in every game here, which is the line
`vl = rr*w0 + ss*w1 + tt*w2` of every `sf.f`.

The state convention is the paper's: state j = 4 (most recent outcome) + (the outcome before), outcomes CC = 0,
CD = 1, DC = 2, DD = 3 seen from the player's own side, and bit j of a strategy's code is 1 if it cooperates in state
j. The co-player sees CD and DC exchanged, which `payf2ini` handles with the state map `1,3,2,4, 9,11,10,12, 5,7,6,8,
13,15,14,16`.

## Licence of the Mersenne twister

`mt.f` is derived from `mt19937ar`, Copyright (C) 1997–2002 Makoto Matsumoto and Takuji Nishimura, distributed under
a BSD-style licence. The copy that ran in the kits, deposited here unchanged, does not carry that notice in its header;
the notice is reproduced in `LICENSE-MT19937.txt` in this folder and applies to `mt.f` and to `mtb.f`, which is
derived from it. The rest of the repository is under the repository's MIT licence.
