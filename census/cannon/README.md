> **In this repository.** The scripts are the kit as it ran on Cannon, unchanged. They expect `pairs.c`, `pairsq.c` and
> `compare.py` next to it, so copy them from `..` first: `cp ../pairs.c ../pairsq.c ../compare.py .`. The Slurm
> scripts use the `test` partition and label jobs `PartnersRivals1.xq`; adapt both to your cluster. The raw outputs
> that `RESULT.md` refers to (`full_out/out`, `out_full.tgz`) are not deposited. Their reduced form is
> `../../data/census/`, written by `../reduce.py`. `task.sh` also runs on a workstation, from `..`:
> `bash cannon/task.sh local 512 4`.

# xq -- the memory-two census in exact rational arithmetic

The census of the paper held its GTH leading-order coefficients in double precision and compared them with a tolerance
of 1e-9; this kit repeats it in exact arithmetic. `pairsq.c` is `pairs.c` (the census program of the paper, copied
here unchanged) with every coefficient held as an exact positive rational (64-bit numerator and denominator, reduced after
every operation, products in 128 bits; overflow stops the program). Every decision is exact: rivalry compares w_DC with
w_CD as rationals, the stability and tie-clause test at (u,v) = (-2,2) compares rational payoffs with no tolerance.

Passes (both programs, same stripes): self (efficiency), rival for T>S (rivP) and T<S (rivM), nash (stability) at (-2,2).
Comparison: `compare.py` (local) checks the exact outputs against the double ones and against the paper's counts.

    bash compile.sh                        # on Cannon, login node: builds, runs a 1e5-pair self-check
    jid=$(sbatch --parsable probe.slurm)   # 4 stripes of 512, 16 cores -> rate
    jid=$(sbatch --parsable full.slurm)    # all 512 stripes, 112 cores

Local timing (M-series, one core): exact 2.4e5 chains/s, double 1.1e6 chains/s; one nash (stability) stripe of 512 takes 2.6-19 s exact.
