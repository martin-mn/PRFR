#!/usr/bin/env python3
"""
Build Cannon/dw1/sf.f from DonationWF's wf3/sf.f (vendored as Ref/sf_wf3.f)
by explicit, asserted string substitutions.

The point of doing it this way rather than by hand: every edit is named, each
must apply exactly once, and `diff Ref/sf_wf3.f Cannon/dw1/sf.f` is then a
short reviewable list.  In particular the GENERATION LOOP is not in the edit
list at all, so it is byte-identical to wf3's -- which is byte-identical to
ca10's, the code behind the published Fig 1.

usage:  python3 mksf.py            (writes ../Cannon/dw1/sf.f)
        python3 mksf.py --chk      (also writes sfchk.f, the retuned build
                                    for the bit-for-bit acceptance test)
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "sf_wf3.f")          # repository copy (author's tree: DiskM2WF/Ref/sf_wf3.f)
# repository: the output goes to the path given on the command line, default ./sf.f (author's tree: Cannon/dw1/sf.f)
DST  = os.path.abspath(([a for a in sys.argv[1:] if not a.startswith("--")] or ["sf.f"])[0])

def sub(s, old, new, tag):
    n = s.count(old)
    assert n == 1, "edit %r matched %d times, expected 1" % (tag, n)
    return s.replace(old, new)

s = open(SRC).read()

# ---------------------------------------------------------------- 1 header
HEAD = """* M2 strategies; WF pairwise comparison  (synchronous Fermi imitation)
*
* dw1 = DonationWF's wf3, with the DONATION GAME REPLACED BY A LIST OF
* ARBITRARY GAMES read from games.dat, so the WF process can be run at every
* point of NE.pdf's plane -- the 16x8 disk grid and the 17x17 square that
* CL1/DiskM2IN solved in the Imhof-Nowak limit.
*
* A game is entered as (cR, cS, cT) with P = 0.  NE's representative of a
* symmetric 2x2 game with R > P is (1, u, 1+v, 0); DonationWF's donation
* scale is (1-c, -c, 1, 0).  BOTH are in games.dat, because beta multiplies
* a RAW payoff difference here, so the two scales are the same games at
* different selection strengths (beta_don = beta_NE/(1-c) on the ray).
*
* The generation loop is byte-identical to wf3/sf.f and hence to Cannon/ca10
* /sf.f, the code behind Fig 1 of the paper.  It is built by Opt/mksf.py as
* an asserted list of substitutions on wf3/sf.f, so `diff` is the audit.
* The one line that carries the game into the dynamics,
*     vl = rr*w0 + ss*w1 + tt*w2
* is UNCHANGED: only the values of rr, ss, tt now come from games.dat
* instead of from (1-c, -c, 1).  With a donation row they are (1-c, -c, 1),
* so the arithmetic is bit-identical, not merely equal.
*
* Efficiency is normalised by the attainable optimum, which above the switch
* line u+v = 1 is ALTERNATION, not mutual cooperation:
*     Emax = max( R, (S+T)/2 ) = max( cR, (cS+cT)/2 )
* Both the raw mean per-round payoff and pay/Emax are written out, so the
* normalisation can be changed downstream without rerunning.
*
* Grid:
*     N = 1000, m = 1, beta = 100, u = 1e-2, itend = 1e7  (1e5 substitutions)
*     eps = 1e-2, 1e-3, 1e-4                 (3)
*     games = whatever games.dat holds       (455: 19+19 donation, 128 disk,
*                                             289 square)
*     nrep = nper = 10, so ONE TASK = ONE (game, eps) CELL and its h-file IS
*     the cell's summed abundance histogram -- nothing to sum downstream.
*
* Task order, GAME OUTERMOST, fastest first: replicate block, eps, u, beta,
* game.  Game is outermost so that APPENDING games to games.dat appends
* tasks at the end and never moves an existing game's indices -- the ca7/ca8
* lesson, applied to the axis that will actually grow here.  With
* ntpc = 1 and neps = 3 the three tasks of game ig are 3*(ig-1)+1..3, and
* eps = 1e-4 alone is the stride-3 subarray 3*(ig-1)+3.
*
* Seeds 8000000 + (isl-1)*nper + irep, disjoint from ca2 (43891-45890),
* ca3 (743891-744890), ca4 (2000001-2005700), ca10 (3000001-3008000),
* wf1 (4000001-4000800), wf2 (5000001-5000800), wf3 (6000001-6002970) and
* wf4 (7000001-7002970).
*
* usage:  ./sf.x <task index 1..ngam*neps>      (games.dat in the cwd)
* output: unit 3 -> <task>   : nrep lines of gid ie u v Emax pay ef ps(1..16)
*         unit 4 -> w<task>  : header + nwin winner lines per replicate
*         unit 7 -> h<task>  : the cell header, then every strategy with a
*                              non-zero summed count:  code  count
"""
old_head = s[:s.index("\n      program sb")]
s = s.replace(old_head, HEAD.rstrip("\n"), 1)

# ------------------------------------------------------- 2 declarations
s = sub(s,
  "      character*12 slurm,wfile,hfile\n",
  "      character*12 slurm,wfile,hfile\n"
  "      character*200 lbuf,lb\n", "buffers")

s = sub(s,
  "      parameter (nc=99,neps=3,nu=1,nbet=1,nrep=10,nper=10)\n"
  "      dimension cval(nc),epsv(neps),uval(nu),bval(nbet)\n"
  "      integer itv(nu)\n",
  "      parameter (mgam=512,neps=3,nu=1,nbet=1,nrep=10,nper=10)\n"
  "      parameter (iseedb=8000000)\n"
  "      dimension epsv(neps),uval(nu),bval(nbet)\n"
  "      integer itv(nu)\n"
  "C     the game list, read from games.dat at start-up\n"
  "      dimension gcr(mgam),gcs(mgam),gct(mgam),gu(mgam),gv(mgam)\n"
  "      integer ggid(mgam),ggic(mgam)\n"
  "      character*24 gtag(mgam)\n", "parameter card")

# drop the 99-cost table
m = re.search(r"      data cval /.*?0\.99d0/\n", s, re.S)
assert m, "cval table not found"
s = s[:m.start()] + s[m.end():]

# ------------------------------------------------------- 3 read games.dat
s = sub(s,
  "      open (unit=3,file=slurm)\n",
  "C     ---- the game list ----------------------------------------------\n"
  "C     one game per line:  gid  ic  cR  cS  cT  u  v  tag\n"
  "C     cR/cS/cT are 17 significant digits and round-trip exactly; the u/v\n"
  "C     columns are display only, so the dynamics never uses them.\n"
  "C     ic is metadata (the donation cost index, 0 if not a donation game).\n"
  "C     NOTE: DiskM2IN's games.dat is NOT interchangeable -- there ic>0 meant\n"
  "C     'recompute the payoffs internally' and the cR/cS/cT columns of those\n"
  "C     rows are zero placeholders.  Use Opt/mkgames.py from THIS project.\n"
  "      open (unit=2,file='games.dat',status='old')\n"
  "      ngam=0\n"
  "   11 read (2,'(a)',end=12) lbuf\n"
  "      lb=adjustl(lbuf)\n"
  "      if (lb(1:1).eq.'#') goto 11\n"
  "      if (len_trim(lb).eq.0) goto 11\n"
  "      ngam=ngam+1\n"
  "      if (ngam.gt.mgam) stop 'games.dat: too many games, raise mgam'\n"
  "      read (lb,*) ggid(ngam),ggic(ngam),gcr(ngam),gcs(ngam),\n"
  "     &            gct(ngam),gu(ngam),gv(ngam),gtag(ngam)\n"
  "      goto 11\n"
  "   12 close (2)\n"
  "      if (ngam.le.0) stop 'games.dat: no games'\n"
  "\n"
  "      open (unit=3,file=slurm)\n", "games reader")

# ------------------------------------------------------- 4 the task decode
s = sub(s,
  "C     task order, fastest first: replicate block, c, u, eps, beta.  beta is\n"
  "C     outermost so a second intensity appends tasks without moving the\n"
  "C     first block's indices.\n"
  "\n"
  "      iblk =mod(isl-1,ntpc)+1\n"
  "      ic   =mod((isl-1)/ntpc,nc)+1\n"
  "      iu   =mod((isl-1)/(ntpc*nc),nu)+1\n"
  "      ie   =mod((isl-1)/(ntpc*nc*nu),neps)+1\n"
  "      ib   =(isl-1)/(ntpc*nc*nu*neps)+1\n"
  "      c=cval(ic)\n",
  "C     task order, fastest first: replicate block, eps, u, beta, GAME.  The\n"
  "C     game is outermost so that appending games to games.dat appends tasks\n"
  "C     at the end and never moves an existing game's index.\n"
  "\n"
  "      iblk =mod(isl-1,ntpc)+1\n"
  "      ie   =mod((isl-1)/ntpc,neps)+1\n"
  "      iu   =mod((isl-1)/(ntpc*neps),nu)+1\n"
  "      ib   =mod((isl-1)/(ntpc*neps*nu),nbet)+1\n"
  "      ig   =(isl-1)/(ntpc*neps*nu*nbet)+1\n"
  "      if (ig.gt.ngam) stop 'task index beyond the game list'\n"
  "      ic=ggic(ig)\n", "decode")

# ------------------------------------------------------- 5 the game payoffs
# wf3 set the payoffs AFTER writing the file headers.  The headers here name
# the game, so the assignment moves up (see edit 6) and this block goes.
s = sub(s,
  "C     donation game payoffs\n"
  "\n"
  "      rr=o1-c\n"
  "      ss=-c\n"
  "      tt=o1\n",
  "C     the game's payoffs are set above, before the headers that name them\n",
  "payoffs")

# ------------------------------------------------------- 6 headers
s = sub(s,
  "      write (4,'(a)')\n"
  "     & '# run: isl ie eps ic c irun ef ndist ntot nhit nmis'\n"
  "      write (4,'(a)')\n"
  "     & '# win: isl eps c irun rank code abund selfpay cc cd dc dd bits'\n"
  "      write (7,'(a,i6,a,e11.3,a,e11.3,a,f8.4,a,f9.1,a,i5,a,i12)')\n"
  "     & '# cell: isl ',isl,'  eps ',eps,'  u ',u,'  c ',c,\n"
  "     & '  beta ',beta,'  nper ',nper,'  itend ',itend\n"
  "      write (7,'(a)') '# code  count  (summed over nrep)'\n",
  "C     THIS game's payoffs, (R,S,T,P) = (cR,cS,cT,0).  rr/ss/tt keep their\n"
  "C     wf3 names so that the cache-miss line in the generation loop,\n"
  "C     vl = rr*w0+ss*w1+tt*w2, is untouched -- with a donation row they are\n"
  "C     (1-c,-c,1) and the arithmetic is bit-identical, not merely equal.\n"
  "\n"
  "      rr=gcr(ig)\n"
  "      ss=gcs(ig)\n"
  "      tt=gct(ig)\n"
  "\n"
  "C     the attainable optimum in self play: mutual R below the switch line\n"
  "C     u+v = 1, alternation (S+T)/2 above it.  Efficiency is pay/emax.\n"
  "\n"
  "      emax=dmax1(rr,oh*(ss+tt))\n"
  "\n"
  "      write (4,'(a)')\n"
  "     & '# run: isl ie eps gid u v irun pay ef ndist ntot nhit nmis'\n"
  "      write (4,'(a)')\n"
  "     & '# win: isl eps gid irun rank code abund selfpay'//\n"
  "     & ' selfef cc cd dc dd bits'\n"
  "      write (7,'(a,i7,a,i6,1x,a,a,e11.3,a,e11.3,a,f9.1)')\n"
  "     & '# cell: isl ',isl,'  gid ',ggid(ig),trim(gtag(ig)),\n"
  "     & '  eps ',eps,'  umut ',u,'  beta ',beta\n"
  "      write (7,'(a,3f24.16,a,2f16.8,a,f24.16)')\n"
  "     & '# game: cR cS cT ',rr,ss,tt,'   u v ',gu(ig),gv(ig),\n"
  "     & '   Emax ',emax\n"
  "      write (7,'(a,i5,a,i12,a,i3)')\n"
  "     & '# run:  nper ',nper,'  itend ',itend,'  ie ',ie\n"
  "      write (7,'(a,i4)') '# ic:   ',ic\n"
  "      write (7,'(a)') '# code  count  (summed over nrep)'\n", "headers")

# ------------------------------------------------------- 7 the seed base
s = sub(s, "      iseed=6000000+(isl-1)*nper+irep\n",
           "      iseed=iseedb+(isl-1)*nper+irep\n", "seed base")

# ------------------------------------------------------- 8 the normaliser
s = sub(s,
  "      ef=ef*rrn*rrm/(z*(o1-c))\n",
  "C     pay = mean per-round payoff of a player, ef = pay/emax.  wf3 divided\n"
  "C     by (1-c), which IS emax on the donation ray below the switch line.\n"
  "      pay=ef*rrn*rrm/z\n"
  "      ef=pay/emax\n", "normaliser")

# ------------------------------------------------------- 9 the records
s = sub(s,
  "      write (3,'(18f16.10)') c,ef,(ps(k),k=1,16)\n",
  "      write (3,'(2i8,2f14.6,19f16.10)') ggid(ig),ie,gu(ig),gv(ig),\n"
  "     &      emax,pay,ef,(ps(k),k=1,16)\n", "unit 3 record")

s = sub(s,
  "      write (4,'(a,2i7,e11.3,i5,f8.4,i7,f12.7,i9,3i16)') '# ',\n"
  "     &      isl,ie,eps,ic,c,irun,ef,ndist,ntot,nhit,nmis\n",
  "      write (4,'(a,2i7,e11.3,i7,2f10.4,i7,2f12.7,i9,3i16)') '# ',\n"
  "     &      isl,ie,eps,ggid(ig),gu(ig),gv(ig),irun,pay,ef,\n"
  "     &      ndist,ntot,nhit,nmis\n", "unit 4 run record")

s = sub(s,
  "         write (4,'(i8,e11.3,f8.4,2i6,i7,f12.8,f12.7,4f11.8,1x,a16)')\n"
  "     &         isl,eps,c,irun,iw,is,ab,spay,w0,w1,w2,w3,bits\n",
  "         write (4,'(i8,e11.3,i7,2i6,i7,f12.8,2f12.7,4f11.8,1x,a16)')\n"
  "     &         isl,eps,ggid(ig),irun,iw,is,ab,spay,spay/emax,\n"
  "     &         w0,w1,w2,w3,bits\n", "unit 4 winner record")

open(DST, "w").write(s)
print("wrote", os.path.relpath(DST, HERE))

# --------------------------------------------------------------- the check
if "--chk" in sys.argv:
    CHK = os.path.join(os.path.dirname(DST), "sfchk.f")
    t = s
    # wf3's decode order (c inner, eps outer) and wf3's seed base, so that a
    # games.dat holding wf3's 99 costs in wf3's order makes task isl carry
    # exactly wf3's (c, eps, seed) triple.
    t = sub(t,
      "      iblk =mod(isl-1,ntpc)+1\n"
      "      ie   =mod((isl-1)/ntpc,neps)+1\n"
      "      iu   =mod((isl-1)/(ntpc*neps),nu)+1\n"
      "      ib   =mod((isl-1)/(ntpc*neps*nu),nbet)+1\n"
      "      ig   =(isl-1)/(ntpc*neps*nu*nbet)+1\n",
      "      iblk =mod(isl-1,ntpc)+1\n"
      "      ig   =mod((isl-1)/ntpc,ngam)+1\n"
      "      iu   =mod((isl-1)/(ntpc*ngam),nu)+1\n"
      "      ie   =mod((isl-1)/(ntpc*ngam*nu),neps)+1\n"
      "      ib   =(isl-1)/(ntpc*ngam*nu*neps)+1\n", "chk decode")
    t = sub(t, "      parameter (iseedb=8000000)\n",
               "      parameter (iseedb=6000000)\n", "chk seed base")
    open(CHK, "w").write(t)
    print("wrote", os.path.relpath(CHK, HERE),
          "(wf3's decode order and seed base)")
