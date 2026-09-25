# Result, 2026-09-23 21:21 EDT: the exact census agrees with the double-precision census on every decision

Job 48068392 (test partition, 48 cores; 48068170 was cancelled while pending on Resources and resubmitted smaller):
COMPLETED 0:0, 164 s wall, 4096 passes (512 stripes x {self, rivP, rivM, nash(-2,2)} x {exact, double}); `sacct` clean,
every .err file free of errors, no overflow anywhere. Probe 48068015 (4 stripes, 16 cores): COMPLETED, 22 s.
Outputs: full_out/out (fetched as out_full.tgz); comparison: `python3 compare.py full_out/out 512`.

* decisions differing between exact and double: 0 in every pass (self-play support and weights to 1e-12; first
  outperforming co-player for T>S and T<S; stability decision, number of tying co-players, tie-clause verdict at (-2,2)).
* census from the exact outputs alone: 7639 / 3072 / 14757 efficient (below / above / on the switch line); 2640 rivals for
  T>S and 2640 for T<S, the second the mirror image of the first; 5230 either way; 50 both ways; friendly rivals
  8 / 1519 / 80 / 80 on W / S / E / N, 1677 somewhere; at (-2,2): 672 stable, 187 partners, 493 stable rivals, 8 efficient stable
  rivals, 8 partners satisfying the tie clause -- every count as in the paper.
* largest numerator or denominator met in the exact run: 831097 (64-bit fractions have ample room).
* chains per rivalry pass: 206,891,410 (T>S) and 228,253,906 (T<S), of which 2640 x 65536 = 173,015,040 are the rivals'.
* smallest nonzero |w_DC - w_CD| met (exact, over every chain computed, rivals and non-rivals up to their first beater):
  2.93e-3; the double run met a spurious nonzero 1.4e-17 where the exact value is 0 (absorbed by the 1e-9 tolerance).
