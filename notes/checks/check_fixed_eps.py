#!/usr/bin/env python3
"""
check_fixed_eps.py -- the worked examples at eps = 0.01 of ../fixed-error-rate.md, recomputed.

  1. Against ALLD, where T > S, a strategy's payoff minus ALLD's is (S - T)(w_CD - w_DC) per round, so its deficit in
     units of eps (T - S) is (w_CD - w_DC)/eps.  The notes: tit-for-tat 0.98, the eight friendly rivals of W "about
     1.9", and every strategy other than ALLD strictly behind ALLD.
  2. At (u, v) = (-0.5, 2), above the switch line: the pair ALLC-ALLD averages more than the best self-play of any of
     the 65536 strategies, which is an alternator's.
  3. (Partial check of "below the switch line the only efficient strategy at a fixed eps is ALLC".)  At the donation
     game (u, v) = (-1, 1), no other strategy's self-play reaches ALLC's.  The full statement also needs the maximum over
     all 65536^2 pairs, which is not computed here.

    python3 check_fixed_eps.py          (about 5 s)
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairchain as pc

EPS = 0.01
ok = True


def report(cond, text):
    global ok
    ok &= bool(cond)
    print("%s  %s" % ("PASS" if cond else "FAIL", text))


W = pc.stationary(pc.ALLD, np.arange(pc.NC), EPS)          # ALLD's view against everyone
behind = (W[:, 2] - W[:, 1]) / EPS                         # the co-player's (w_CD - w_DC) is ALLD's (w_DC - w_CD)
print("deficit against ALLD at eps = 0.01, in units of eps (T - S):")
print("   TFT %.4f" % behind[pc.TFT])
for s in pc.EIGHT:
    print("   %5d %s %.4f" % (s, pc.genome(s), behind[s]))
report(abs(behind[pc.TFT] - 0.98) < 5e-3, "tit-for-tat is behind ALLD by 0.98 eps (T - S) per round (computed %.4f)" % behind[pc.TFT])
e8 = behind[pc.EIGHT]
report(np.all(np.abs(e8 - 1.9) < 0.1), "the eight are behind by about 1.9 eps (T - S) (computed %.3f to %.3f)" % (e8.min(), e8.max()))
others = np.delete(behind, pc.ALLD)
report(others.min() > 0, "every strategy other than ALLD is strictly behind ALLD (smallest deficit %.3g eps(T-S), at %d)"
       % (others.min(), np.delete(np.arange(pc.NC), pc.ALLD)[others.argmin()]))

u, v = -0.5, 2.0
R, S, T, P = pc.game(u, v)
wp = pc.stationary(pc.ALLC, [pc.ALLD], EPS)[0]
pair = 0.5 * sum(pc.pays(wp[None], u, v)).item()
Wself = pc.selfplay_all(EPS)
sp = Wself @ pc.game(u, v)
best = int(sp.argmax())
print("at (u, v) = (-0.5, 2), eps = 0.01: ALLC-ALLD average %.5f; best self-play %.5f by %d %s (w_CD + w_DC = %.3f); "
      "(S + T)/2 = %.3f" % (pair, sp[best], best, pc.genome(best), Wself[best, 1] + Wself[best, 2], (S + T) / 2))
report(pair > sp.max(), "the pair ALLC-ALLD averages more than every self-play")
report(Wself[best, 1] + Wself[best, 2] > 0.9, "the best self-play is an alternator's")

u, v = -1.0, 1.0
sp = Wself @ pc.game(u, v)
order = np.argsort(-sp)
print("at (u, v) = (-1, 1), eps = 0.01: best self-plays %s" % ", ".join("%d %.6f" % (i, sp[i]) for i in order[:3]))
report(order[0] == pc.ALLC and sp[order[1]] < sp[pc.ALLC], "ALLC has the highest self-play of the 65536 (partial check)")
print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
