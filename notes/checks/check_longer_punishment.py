#!/usr/bin/env python3
"""
check_longer_punishment.py -- the numbers of ../longer-punishment.md, recomputed.

Where T > S a co-player tau finishes ahead of sigma exactly when, in sigma's view, w_CD > w_DC in the limit
eps -> 0; the count of such co-players does not depend on the game.  Here the limit is read at eps = 1e-7 with the
threshold 1e-4 on w_CD - w_DC (the limit differences are rationals with small denominators, the eps terms are of order
1e-7).  Checked:

  1. the genomes of 22663 and 23175 and that they differ at position 9 only;
  2. 23175 (a friendly rival of W) has no co-player ahead of it; 22663 has 8759; 32907 has 9253;
  3. at (u, v) = (-3.21, 2.29) the co-player of 22663 that "defects, concedes once and then defects twice" earns
     (2T + S + P)/4 = 0.84 < R, and 22663 is a Nash equilibrium there (no co-player earns more than its self-play R);
  4. at (u, v) = (-0.38, 0.54) ALLD earns T/2 = 0.77 against 32907, which earns S/2 = -0.19, and 32907 is stable there;
  5. no co-player that finishes ahead of 22663 or 32907 earns R against it, and at the sampled game nearest to
     (-0.38, 0.54) 32907 is the most abundant strategy of the large-population run (../../data/runs/m2_N1000.csv)
     and a partner;
  6. the self-play deficits at eps = 1e-4 behind "R - 7.6 eps against R - 9.5 eps" (SI section 9, 'Which partners win').

    python3 check_longer_punishment.py      (about 5 s)
"""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairchain as pc

EPS, THR = 1e-7, 1e-4
ok = True


def report(cond, text):
    global ok
    ok &= bool(cond)
    print("%s  %s" % ("PASS" if cond else "FAIL", text))


g1, g2 = pc.genome(22663).replace("C", "1").replace("D", "0"), pc.genome(23175).replace("C", "1").replace("D", "0")
report(g1 == "1110000100011010" and g2 == "1110000101011010", "22663 = %s, 23175 = %s" % (g1, g2))
report([j for j in range(16) if g1[j] != g2[j]] == [9], "they differ only at position 9, the state (DC, CD)")
g3 = pc.genome(32907).replace("C", "1").replace("D", "0")
report(g3 == "1101000100000001", "32907 = %s" % g3)

W = {s: pc.stationary(s, np.arange(pc.NC), EPS) for s in (22663, 23175, 32907)}
ahead = {s: np.nonzero(W[s][:, 1] - W[s][:, 2] > THR)[0] for s in W}
for s, want in ((23175, 0), (22663, 8759), (32907, 9253)):
    report(len(ahead[s]) == want, "%d co-players finish ahead of %d (the notes: %d)" % (len(ahead[s]), s, want))

u, v = -3.21, 2.29
R, S, T, P = pc.game(u, v)
own, co = pc.pays(W[22663], u, v)
self_ = (pc.stationary(22663, [22663], EPS)[0] @ pc.game(u, v)).item()
cyc = (2 * T + S + P) / 4
hit = [t for t in ahead[22663] if abs(co[t] - cyc) < 1e-4]
report(len(hit) > 0, "at (-3.21, 2.29): %d co-players ahead of 22663 earn (2T + S + P)/4 = %.4f, e.g. %d %s"
       % (len(hit), cyc, hit[0] if hit else -1, pc.genome(hit[0]) if hit else ""))
report(co.max() <= self_ + 1e-4 and abs(self_ - R) < 1e-4,
       "22663 is stable there: best co-player %.6f, self-play %.6f = R" % (co.max(), self_))
report(co[ahead[22663]].max() < R - 1e-3, "no co-player ahead of 22663 earns R (the best of them %.4f)" % co[ahead[22663]].max())

u, v = -0.38, 0.54
R, S, T, P = pc.game(u, v)
own, co = pc.pays(W[32907], u, v)
self_ = (pc.stationary(32907, [32907], EPS)[0] @ pc.game(u, v)).item()
report(abs(co[pc.ALLD] - T / 2) < 1e-4 and abs(own[pc.ALLD] - S / 2) < 1e-4,
       "at (-0.38, 0.54): ALLD earns %.4f = T/2 against 32907, which earns %.4f = S/2" % (co[pc.ALLD], own[pc.ALLD]))
report(co.max() <= self_ + 1e-4, "32907 is stable there: best co-player %.6f, self-play %.6f" % (co.max(), self_))
report(co[ahead[32907]].max() < R - 1e-3, "no co-player ahead of 32907 earns R (the best of them %.4f)" % co[ahead[32907]].max())
# "the most abundant partner at N = 1000": the sampled game of the large-population run nearest to (-0.38, 0.54)
RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "data", "runs", "m2_N1000.csv")
rows = list(csv.DictReader(l for l in open(RUN) if not l.startswith("#")))
g = min(rows, key=lambda r: (float(r["u"]) - u) ** 2 + (float(r["v"]) - v) ** 2)
ug, vg = float(g["u"]), float(g["v"])
own, co = pc.pays(W[32907], ug, vg)
self_ = (pc.stationary(32907, [32907], EPS)[0] @ pc.game(ug, vg)).item()
report(int(g["top"]) == 32907 and (round(ug, 2), round(vg, 2)) == (u, v) and co.max() <= self_ + 1e-4
       and abs(self_ - 1.0) < 1e-4,
       "at the sampled game (%.3f, %.3f) the most abundant strategy of the N = 1000 run is %s (data/runs/m2_N1000.csv), "
       "a partner there (stable, self-play R)" % (ug, vg, g["top"]))

u, v = -3.21, 2.29
for s in (22663, 23175):
    d = (1.0 - pc.stationary(s, [s], 1e-4)[0] @ pc.game(u, v)) / 1e-4
    print("      self-play of %d at eps = 1e-4, (u, v) = (-3.21, 2.29): R - %.2f eps" % (s, d))
d1 = (1.0 - pc.stationary(22663, [22663], 1e-4)[0] @ pc.game(u, v)) / 1e-4
d2 = (1.0 - pc.stationary(23175, [23175], 1e-4)[0] @ pc.game(u, v)) / 1e-4
report(abs(d1 - 7.6) < 0.05 and abs(d2 - 9.5) < 0.05, "R - 7.6 eps is 22663's self-play and R - 9.5 eps the friendly rival 23175's")
print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
