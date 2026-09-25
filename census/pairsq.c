// pairsq.c -- the census of pairs.c in EXACT rational arithmetic.
//
// Same algorithm as pairs.c: the eps->0 limit of the stationary distribution of two binary memory-two strategies with
// independent implementation errors, by GTH state reduction in leading-order arithmetic, every quantity held as
// c * eps^e with an integer exponent e and a coefficient c > 0.  pairs.c holds c in double precision and compares with a
// tolerance of 1e-9; here c is an exact positive rational num/den (64-bit numerator and denominator, reduced by their gcd
// after every operation, products formed in 128 bits).  Every transition of the pair chain has leading coefficient 1
// (probability eps^k (1-eps)^(2-k), k = number of flipped actions), and GTH only adds, multiplies and divides positive
// quantities, so every coefficient is a positive rational and nothing is approximated.  An intermediate that does not fit
// in 64 bits after reduction stops the program with a message (it never happened on the full census).
//
// Decisions are exact: rivalry compares w_DC and w_CD as rationals; the Nash and tie-clause test compares payoffs, which
// are rational at a game with rational (u, v), exactly, with no tolerance.
//
// Strategy convention as in pairs.c: state j = 4*recent + before, outcomes CC=0, CD=1, DC=2, DD=3 (own action first);
// bit j of the 16-bit code is 1 for C.  ALLC = 65535, ALLD = 0.
//
// usage (same modes and output columns as pairs.c):
//   pairsq self  stripe nstripes            -> code w_CC w_CD w_DC w_DD            (doubles printed from exact rationals)
//   pairsq rival stripe nstripes sign       -> code first-beater (-1 = rival)      sign +1: T>S reading, -1: T<S
//   pairsq nash  stripe nstripes u v        -> code self maxpay tieviol ntie firstbeat   (u, v integers or p/q)
//   pairsq pair  sigma tau                  -> sigma tau w_CC w_CD w_DC w_DD  plus the exact fractions
//   pairsq cmp   n seed                     -> n random pairs: exact vs double (pairs.c's arithmetic), max deviation
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NS 16
#define EINF 1000000000

typedef unsigned __int128 u128;
typedef struct { uint64_t n, d; } Q;          // positive rational n/d, gcd(n,d) = 1

static uint64_t maxbits_seen = 0;             // largest numerator or denominator met, for the report

static inline uint64_t gcd64(uint64_t a, uint64_t b) {
  if (!a) return b; if (!b) return a;
  int sh = __builtin_ctzll(a | b);
  a >>= __builtin_ctzll(a);
  do { b >>= __builtin_ctzll(b); if (a > b) { uint64_t t = a; a = b; b = t; } b -= a; } while (b);
  return a << sh;
}
static inline u128 gcd128(u128 a, u128 b) {
  while (b) { u128 t = a % b; a = b; b = t; }
  return a;
}
static void overflow(const char *where) {
  fprintf(stderr, "pairsq: 64-bit overflow in %s; the exact census needs wider integers\n", where);
  exit(2);
}
static inline Q mkq(u128 n, u128 d) {         // reduce a 128-bit fraction to a 64-bit one, or stop
  if (n >> 64 || d >> 64) { u128 g = gcd128(n, d); n /= g; d /= g; if (n >> 64 || d >> 64) overflow("reduce"); }
  else { uint64_t g = gcd64((uint64_t)n, (uint64_t)d); n /= g; d /= g; }
  Q q = { (uint64_t)n, (uint64_t)d };
  uint64_t m = q.n | q.d; if (m > maxbits_seen) maxbits_seen = m;
  return q;
}
static inline Q qone(void) { Q q = {1, 1}; return q; }
static inline Q qadd(Q a, Q b) {
  if (a.d == 1 && b.d == 1) { u128 s = (u128)a.n + b.n; if (s >> 64) overflow("add"); Q q = {(uint64_t)s, 1}; return q; }
  return mkq((u128)a.n * b.d + (u128)b.n * a.d, (u128)a.d * b.d);
}
static inline Q qmul(Q a, Q b) {
  if (a.d == 1 && b.d == 1) { u128 p = (u128)a.n * b.n; if (p >> 64) overflow("mul"); Q q = {(uint64_t)p, 1}; return q; }
  return mkq((u128)a.n * b.n, (u128)a.d * b.d);
}
static inline Q qdiv(Q a, Q b) { return mkq((u128)a.n * b.d, (u128)a.d * b.n); }
static inline int qcmp(Q a, Q b) {            // sign of a - b
  u128 l = (u128)a.n * b.d, r = (u128)b.n * a.d; return (l > r) - (l < r);
}
static inline double qdbl(Q a) { return (double)a.n / (double)a.d; }

// a signed rational for payoffs (numerators may be negative); held as __int128 over a positive 64-bit denominator
typedef struct { __int128 n; uint64_t d; } S;
static S s_of_q(Q a) { S s = {(__int128)a.n, a.d}; return s; }
static S s_scale(S a, __int128 p, uint64_t q) {  // a * p/q
  __int128 n; if (__builtin_mul_overflow(a.n, p, &n)) overflow("scale"); u128 d = (u128)a.d * q;
  __int128 an = n < 0 ? -n : n; u128 g = gcd128((u128)an, d); if (g > 1) { n /= (__int128)g; d /= g; }
  if (d >> 64) overflow("scale"); S s = {n, (uint64_t)d}; return s;
}
static S s_add(S a, S b) {
  __int128 x = 0, y = 0, n = 0; if (__builtin_mul_overflow(a.n, (__int128)b.d, &x) || __builtin_mul_overflow(b.n, (__int128)a.d, &y) ||
      __builtin_add_overflow(x, y, &n)) overflow("sadd");
  u128 d = (u128)a.d * b.d;
  __int128 an = n < 0 ? -n : n; u128 g = gcd128((u128)an, d); if (g > 1) { n /= (__int128)g; d /= g; }
  if (d >> 64) overflow("sadd"); S s = {n, (uint64_t)d}; return s;
}
static int s_cmp(S a, S b) {                  // sign of a - b (products fit: |n| < 2^80 in practice, d < 2^64)
  __int128 l, r; if (__builtin_mul_overflow(a.n, (__int128)b.d, &l) || __builtin_mul_overflow(b.n, (__int128)a.d, &r)) overflow("scmp");
  return (l > r) - (l < r);
}
static double s_dbl(S a) { return (double)a.n / (double)a.d; }

static inline int bitC(unsigned s, int j) { return (s >> j) & 1; }
static inline int swapo(int o) { return ((o & 1) << 1) | (o >> 1); }

static void build(unsigned sig, unsigned tau, Q c[NS][NS], int e[NS][NS]) {
  for (int i = 0; i < NS; i++) for (int j = 0; j < NS; j++) { c[i][j].n = 0; c[i][j].d = 1; e[i][j] = EINF; }
  for (int j = 0; j < NS; j++) {
    int o1 = j >> 2, o0 = j & 3; int jt = 4 * swapo(o1) + swapo(o0);
    int dS = 1 - bitC(sig, j), dT = 1 - bitC(tau, jt);
    for (int fs = 0; fs < 2; fs++) for (int ft = 0; ft < 2; ft++) {
      int onew = 2 * (dS ^ fs) + (dT ^ ft); int nxt = 4 * onew + o1;
      c[j][nxt] = qone(); e[j][nxt] = fs + ft;
    }
  }
}

// GTH in leading-order arithmetic, exactly as pairs.c but with rational coefficients.
// Output: w[k] exact rational (zero = {0,1}) for the limiting stationary distribution.
static void gth(Q c[NS][NS], int e[NS][NS], Q w[NS]) {
  for (int k = NS - 1; k >= 1; k--) {
    int es = EINF; Q cs = {0, 1};
    for (int j = 0; j < k; j++) { int ej = e[k][j]; if (ej < es) { es = ej; cs = c[k][j]; } else if (ej == es && es < EINF) { cs = qadd(cs, c[k][j]); } }
    for (int i = 0; i < k; i++) { if (e[i][k] < EINF) { c[i][k] = qdiv(c[i][k], cs); e[i][k] -= es; } }
    for (int i = 0; i < k; i++) { if (e[i][k] >= EINF) continue; int eik = e[i][k]; Q cik = c[i][k];
      for (int j = 0; j < k; j++) { if (e[k][j] >= EINF) continue; int en = eik + e[k][j]; Q cn = qmul(cik, c[k][j]);
        if (en < e[i][j]) { e[i][j] = en; c[i][j] = cn; } else if (en == e[i][j]) { c[i][j] = qadd(c[i][j], cn); } } }
  }
  Q pc[NS]; int pe[NS]; pc[0] = qone(); pe[0] = 0;
  for (int k = 1; k < NS; k++) { int ek = EINF; Q ck = {0, 1};
    for (int i = 0; i < k; i++) { if (e[i][k] >= EINF || pe[i] >= EINF) continue; int en = pe[i] + e[i][k]; Q cn = qmul(pc[i], c[i][k]);
      if (en < ek) { ek = en; ck = cn; } else if (en == ek) { ck = qadd(ck, cn); } }
    pc[k] = ck; pe[k] = ek; }
  int emin = EINF; Q ct = {0, 1};
  for (int k = 0; k < NS; k++) { if (pe[k] < emin) { emin = pe[k]; ct = pc[k]; } else if (pe[k] == emin) { ct = qadd(ct, pc[k]); } }
  for (int k = 0; k < NS; k++) { if (pe[k] == emin) w[k] = qdiv(pc[k], ct); else { w[k].n = 0; w[k].d = 1; } }
}

// limiting outcome frequencies from sigma's side: W[0]=CC, W[1]=CD, W[2]=DC, W[3]=DD, exact
static void freqs(unsigned sig, unsigned tau, Q W[4]) {
  Q c[NS][NS]; int e[NS][NS]; Q w[NS];
  build(sig, tau, c, e); gth(c, e, w);
  for (int o = 0; o < 4; o++) { W[o].n = 0; W[o].d = 1; }
  for (int j = 0; j < NS; j++) if (w[j].n) W[j >> 2] = (W[j >> 2].n ? qadd(W[j >> 2], w[j]) : w[j]);
}

// ---- the double-precision arithmetic of pairs.c, kept verbatim for the cmp mode ----
static void build_d(unsigned sig, unsigned tau, double c[NS][NS], int e[NS][NS]) {
  for (int i = 0; i < NS; i++) for (int j = 0; j < NS; j++) { c[i][j] = 0; e[i][j] = EINF; }
  for (int j = 0; j < NS; j++) {
    int o1 = j >> 2, o0 = j & 3; int jt = 4 * swapo(o1) + swapo(o0);
    int dS = 1 - bitC(sig, j), dT = 1 - bitC(tau, jt);
    for (int fs = 0; fs < 2; fs++) for (int ft = 0; ft < 2; ft++) {
      int onew = 2 * (dS ^ fs) + (dT ^ ft); int nxt = 4 * onew + o1;
      c[j][nxt] = 1.0; e[j][nxt] = fs + ft;
    }
  }
}
static void gth_d(double c[NS][NS], int e[NS][NS], double w[NS]) {
  for (int k = NS - 1; k >= 1; k--) {
    int es = EINF; double cs = 0;
    for (int j = 0; j < k; j++) { int ej = e[k][j]; if (ej < es) { es = ej; cs = c[k][j]; } else if (ej == es && es < EINF) { cs += c[k][j]; } }
    for (int i = 0; i < k; i++) { if (e[i][k] < EINF) { c[i][k] /= cs; e[i][k] -= es; } }
    for (int i = 0; i < k; i++) { if (e[i][k] >= EINF) continue; int eik = e[i][k]; double cik = c[i][k];
      for (int j = 0; j < k; j++) { if (e[k][j] >= EINF) continue; int en = eik + e[k][j]; double cn = cik * c[k][j];
        if (en < e[i][j]) { e[i][j] = en; c[i][j] = cn; } else if (en == e[i][j]) { c[i][j] += cn; } } }
  }
  double pc[NS]; int pe[NS]; pc[0] = 1; pe[0] = 0;
  for (int k = 1; k < NS; k++) { int ek = EINF; double ck = 0;
    for (int i = 0; i < k; i++) { if (e[i][k] >= EINF || pe[i] >= EINF) continue; int en = pe[i] + e[i][k]; double cn = pc[i] * c[i][k];
      if (en < ek) { ek = en; ck = cn; } else if (en == ek) { ck += cn; } }
    pc[k] = ck; pe[k] = ek; }
  int emin = EINF; double ct = 0;
  for (int k = 0; k < NS; k++) { if (pe[k] < emin) { emin = pe[k]; ct = pc[k]; } else if (pe[k] == emin) { ct += pc[k]; } }
  for (int k = 0; k < NS; k++) w[k] = (pe[k] == emin) ? pc[k] / ct : 0.0;
}
static void freqs_d(unsigned sig, unsigned tau, double W[4]) {
  double c[NS][NS]; int e[NS][NS]; double w[NS];
  build_d(sig, tau, c, e); gth_d(c, e, w);
  W[0] = W[1] = W[2] = W[3] = 0; for (int j = 0; j < NS; j++) W[j >> 2] += w[j];
}

static void parse_rat(const char *s, __int128 *p, uint64_t *q) {  // "a" or "a/b", a may be negative
  long a = 0, b = 1; const char *sl = strchr(s, '/');
  a = atol(s); if (sl) b = atol(sl + 1);
  if (b <= 0) { fprintf(stderr, "bad rational %s\n", s); exit(1); }
  *p = a; *q = (uint64_t)b;
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: pairsq self|rival|nash stripe nstripes [sign|u v] | pair s t | cmp n seed\n"); return 1; }
  const char *mode = argv[1];
  if (!strcmp(mode, "pair")) {
    unsigned s = (unsigned)atol(argv[2]), t = (unsigned)atol(argv[3]); Q W[4]; freqs(s, t, W);
    printf("%u %u %.17g %.17g %.17g %.17g   exact %llu/%llu %llu/%llu %llu/%llu %llu/%llu\n", s, t,
           qdbl(W[0]), qdbl(W[1]), qdbl(W[2]), qdbl(W[3]),
           (unsigned long long)W[0].n, (unsigned long long)W[0].d, (unsigned long long)W[1].n, (unsigned long long)W[1].d,
           (unsigned long long)W[2].n, (unsigned long long)W[2].d, (unsigned long long)W[3].n, (unsigned long long)W[3].d);
    return 0;
  }
  if (!strcmp(mode, "cmp")) {
    long n = atol(argv[2]); srand((unsigned)atol(argv[3])); double dmax = 0; long nsupp = 0;
    for (long i = 0; i < n; i++) {
      unsigned s = ((unsigned)rand() ^ ((unsigned)rand() << 8)) & 65535u, t = ((unsigned)rand() ^ ((unsigned)rand() << 8)) & 65535u;
      Q W[4]; double Wd[4]; freqs(s, t, W); freqs_d(s, t, Wd);
      for (int o = 0; o < 4; o++) { double x = qdbl(W[o]) - Wd[o]; if (x < 0) x = -x; if (x > dmax) dmax = x;
        if ((W[o].n == 0) != (Wd[o] == 0)) nsupp++; }
    }
    printf("cmp: %ld pairs, max |exact - double| = %.3e, support mismatches = %ld, largest integer met = %llu\n",
           n, dmax, nsupp, (unsigned long long)maxbits_seen);
    return 0;
  }
  if (argc < 4) { fprintf(stderr, "need stripe nstripes\n"); return 1; }
  int stripe = atoi(argv[2]), nstr = atoi(argv[3]);
  if (!strcmp(mode, "self")) {
    for (unsigned s = stripe; s < 65536; s += nstr) { Q W[4]; freqs(s, s, W);
      printf("%u %.17g %.17g %.17g %.17g\n", s, qdbl(W[0]), qdbl(W[1]), qdbl(W[2]), qdbl(W[3])); }
  } else if (!strcmp(mode, "rival")) {
    int sign = atoi(argv[4]);   // +1: T>S reading (need w_DC >= w_CD against all tau); -1: T<S reading (w_CD >= w_DC)
    long ntau_total = 0; double gapmin = 1e9;
    for (unsigned s = stripe; s < 65536; s += nstr) {
      long beater = -1;
      for (long t0 = 0; t0 < 65536; t0++) { unsigned t = (unsigned)t0; Q W[4]; freqs(s, t, W); ntau_total++;
        int c = qcmp(W[2], W[1]); int d = sign * c;       // d >= 0: sigma not outperformed by t
        if (c) { double g = qdbl(W[2]) - qdbl(W[1]); if (g < 0) g = -g; if (g < gapmin) gapmin = g; }
        if (d < 0) { beater = t; break; } }
      printf("%u %ld\n", s, beater);
    }
    fprintf(stderr, "stripe %d: exact; smallest nonzero |wDC-wCD| = %.6e, chains=%ld, largest integer met=%llu\n",
            stripe, gapmin, ntau_total, (unsigned long long)maxbits_seen);
  } else if (!strcmp(mode, "nash")) {
    __int128 up, vp; uint64_t uq, vq; parse_rat(argv[4], &up, &uq); parse_rat(argv[5], &vp, &vq);
    // payoffs in the normalisation (R,S,T,P) = (1, u, 1+v, 0), outcomes seen from sigma's side
    S one = {1, 1}; S ut = {up, uq}; S tv = s_add(one, (S){vp, vq});
    S emax = one; { S alt = s_scale(s_add(ut, tv), 1, 2); if (s_cmp(alt, emax) > 0) emax = alt; }  // max{R,(S+T)/2}
    for (unsigned s = stripe; s < 65536; s += nstr) {
      Q Ws[4]; freqs(s, s, Ws);
      S self = s_add(s_add(s_of_q(Ws[0]), s_scale(s_of_q(Ws[1]), up, uq)), s_scale(s_of_q(Ws[2]), tv.n, tv.d));
      S maxpay = {-1000000000, 1}; int tieviol = 0; long ntie = 0; long firstbeat = -1;
      for (long t0 = 0; t0 < 65536; t0++) { unsigned t = (unsigned)t0; Q W[4]; freqs(s, t, W);
        S ptau = s_add(s_add(s_of_q(W[0]), s_scale(s_of_q(W[1]), tv.n, tv.d)), s_scale(s_of_q(W[2]), up, uq));
        S psig = s_add(s_add(s_of_q(W[0]), s_scale(s_of_q(W[1]), up, uq)), s_scale(s_of_q(W[2]), tv.n, tv.d));
        if (s_cmp(ptau, maxpay) > 0) maxpay = ptau;
        int ct = s_cmp(ptau, self);
        if (ct == 0) { ntie++; if (s_cmp(psig, self) < 0) tieviol = 1; }
        if (ct > 0 && firstbeat < 0) firstbeat = t;
        if (s_cmp(maxpay, emax) > 0) break; }
      printf("%u %.17g %.17g %d %ld %ld\n", s, s_dbl(self), s_dbl(maxpay), tieviol, ntie, firstbeat);
    }
    fprintf(stderr, "stripe %d: nash exact, largest integer met=%llu\n", stripe, (unsigned long long)maxbits_seen);
  }
  return 0;
}
