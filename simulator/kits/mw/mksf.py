#!/usr/bin/env python3
"""
Build Cannon/mw/sf1.f and Cannon/mw/sf2.f from DiskM2WF's dw1/sf.f (vendored as Ref/sf_dw1.f)
by explicit, asserted string substitutions -- the pattern of DiskM2WF/Opt/mksf.py, which built
dw1/sf.f from DonationWF's wf3/sf.f the same way.

WHAT THIS PRODUCES.  The same Wright-Fisher process as dw1/dw2 -- synchronous Fermi pairwise
comparison, m = 1 random co-player per individual per generation, mutation to a uniformly random
strategy, the second half of the run sampled -- over the 16 BINARY MEMORY-ONE strategies instead
of the 65536 binary memory-two ones.

    sf1.f   N = 1000, beta = 100, u = 1e-2, itend = 1e7, iseedb = 10000000   (the F1 parameters)
    sf2.f   N = 100,  beta = 3,   u = 1e-4, itend = 1e8, iseedb = 11000000   (the F2 parameters)

THE STRATEGY SPACE, AND WHY THE PAYOFFS ARE dw1's OWN NUMBERS.  A memory-one strategy answers the
last round's outcome (own action first: CC, CD, DC, DD); bit k of its index 0..15 is 1 for C, so
ALLC = 15, ALLD = 0, TFT = 5, WSLS = 9, Grim = 1 (FinalFigures/m1atoms.py's convention).  Each one
embeds in memory two as the M2 id 15 * sum_k b_k 16^k -- the memory-two strategy that ignores the
round before last -- so ALLC is 65535, TFT 3855 and WSLS 61455.  The 16 x 16 table of pair payoffs
is built ONCE per task by calling dw1's own payf3 on those embedded ids and forming dw1's own two
lines vl = rr*w0+ss*w1+tt*w2 and vh = rr*w0+tt*w1+ss*w2.  The doubles in the table are therefore
exactly the doubles dw1 would have used for the same pair at the same game, and the generation loop
reads them from the table instead of from the hash cache.  Nothing else in the loop changes: the
PRNG stream is consumed in the same order and the same amounts (the cache never drew randomness),
so this is dw1's process on a smaller strategy set, not a different process.

FinalFigures/m1atoms.py checked the other half of that claim -- that the three properties of each of
the 16 against the other 15 are the same as against all 65536 memory-two co-players, on all 45 faces
of the plane -- so restricting the strategy space does not change what any of the 16 IS.

usage:  python3 mksf.py            (writes ../Cannon/mw/sf1.f and sf2.f, prints the diff summary)
        python3 mksf.py --diff     (also prints the full unified diff of sf1.f against Ref/sf_dw1.f)
"""
import difflib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, os.pardir, "dw1", "sf.f")      # repository layout (author's tree: DiskM1WF/Ref/sf_dw1.f, a sha256-asserted copy)
KIT = HERE                                              # repository layout (author's tree: DiskM1WF/Cannon/mw)
SRC_SHA = "6d9c6f03cf4b0fd4ed8d0694a8bc9365b8e54dedb76ef38081a772614a12e8eb"

# the run parameters that separate the two builds; everything else is shared
RUNS = {
    "sf1.f": dict(n=1000, beta="100.d+00", u="1.d-02", itend="10000000", seed="10000000",
                  tag="F1: N = 1000, beta = 100, u = 1e-2, itend = 1e7  (1e5 substitutions)"),
    "sf2.f": dict(n=100, beta="3.d+00", u="1.d-04", itend="100000000", seed="11000000",
                  tag="F2: N = 100,  beta = 3,   u = 1e-4, itend = 1e8  (1e4 substitutions)"),
    # The convergence controls: the same two runs with itend cut 100x and an
    # INDEPENDENT seed base, so comparing them against the full-length run at
    # the same 512 cells measures the Monte Carlo error of the estimate rather
    # than the correlation of a shared sample path.  The full-length probe put
    # the between-replicate sd of the dominant strategy's share at 6e-5 (cell
    # 3) and 1.0e-4 (cell 1533); error goes as 1/sqrt(itend), so these should
    # land within ~1e-3 of the full run -- below a pixel on either page.
    "sf1s.f": dict(n=1000, beta="100.d+00", u="1.d-02", itend="100000", seed="12000000",
                   tag="F1s: N = 1000, beta = 100, u = 1e-2, itend = 1e5  (F1 with itend cut 100x)"),
    "sf2s.f": dict(n=100, beta="3.d+00", u="1.d-04", itend="1000000", seed="13000000",
                   tag="F2s: N = 100,  beta = 3,   u = 1e-4, itend = 1e6  (F2 with itend cut 100x)"),
}
NEDIT = 26                                  # the number of named edits below


def sub(s, old, new, tag):
    n = s.count(old)
    assert n == 1, "edit %r matched %d times, expected 1" % (tag, n)
    return s.replace(old, new)


def build(which):
    R = RUNS[which]
    s = open(SRC).read()
    done = []

    # ------------------------------------------------------------------ 1  the header block
    old_head = s[:s.index("      program sb")]
    HEAD = """* M1 strategies; WF pairwise comparison  (synchronous Fermi imitation)
*
* mw = DiskM2WF's dw1 with the STRATEGY SPACE CUT DOWN from the 65536 binary
* memory-two strategies to the 16 binary memory-one ones, so that the figures
* of PartnersRivals/FinalFigures (Figures 3 and 4, SI Figures 2 and 3) can be
* drawn for memory one.  Built from Ref/sf_dw1.f by ../Opt/mksf.py as an
* asserted list of substitutions, so `diff` is the audit.
*
* A memory-one strategy answers the LAST ROUND'S OUTCOME, own action first:
* CC, CD, DC, DD.  Bit k of its index 0..15 is 1 for C, so
*     ALLD = 0 = DDDD   Grim = 1 = CDDD   TFT = 5 = CDCD
*     WSLS = 9 = CDDC   ALLC = 15 = CCCC
* which is FinalFigures/m1atoms.py's convention.  Each embeds in memory two as
*     mid(k) = 15 * sum_j b_j 16^j          (ALLC 65535, TFT 3855, WSLS 61455)
* -- the memory-two strategy that ignores the round before last.
*
* THE PAYOFFS ARE dw1's OWN NUMBERS.  The 16 x 16 table vlt/vht is built once
* per task by calling dw1's payf3 on the embedded ids and forming dw1's own
* two lines,
*     vl = rr*w0 + ss*w1 + tt*w2        vh = rr*w0 + tt*w1 + ss*w2
* so every double in it is the double dw1 would have used for that pair at
* that game.  The generation loop reads the table instead of the hash cache;
* it draws the same random numbers in the same order and the same amounts,
* because the cache never drew any.  This is dw1's process on a smaller
* strategy set, not a different process.
*
* FinalFigures/m1atoms.py checked that each of the 16 has the same three
* properties (efficient, nash, competitive) against the other 15 as against
* all 65536 memory-two co-players, on all 45 faces of the plane, so cutting
* the space down does not change what any of the 16 is.
*
* A game is entered as (cR, cS, cT) with P = 0; NE's representative of a
* symmetric 2x2 game with R > P is (1, u, 1+v, 0).  games.dat holds the 512
* Voronoi cells of BinM2Ev ca6's Fermat sunflower on the k = 4 disk, copied
* verbatim from DiskM2WF/Opt/games.dat rows 456-967, so this campaign and
* dw1's / dw2's sunflower blocks are THE SAME 512 GAMES.
*
* Efficiency is normalised by the attainable optimum, which above the switch
* line u+v = 1 is ALTERNATION, not mutual cooperation:
*     Emax = max( R, (S+T)/2 ) = max( cR, (cS+cT)/2 )
* Both the raw mean per-round payoff and pay/Emax are written out.
*
* Grid:
*     %(tag)s
*     eps = 1e-4                             (the ie = 3 slot of dw1's epsv)
*     games = whatever games.dat holds       (512: the sunflower)
*     nrep = nper = 10, so ONE TASK = ONE (game, eps) CELL and its h-file IS
*     the cell's summed abundance histogram -- nothing to sum downstream.
*
* Task decode, GAME OUTERMOST, is dw1's unchanged:
*     ie = mod(isl-1,3) + 1        eps = (1e-2, 1e-3, 1e-4)(ie)
*     ig = (isl-1)/3 + 1           the row of games.dat
* so game ig at eps = 1e-4 is task 3*(ig-1)+3 and the campaign is the
* stride-3 subarray 3-1536:3.  Keeping dw1's decode keeps its verified index
* arithmetic, its pack.py and its verify.sh.
*
* Seeds %(seed)s + (isl-1)*nper + irep, disjoint from ca2 (43891-45890),
* ca3 (743891-744890), ca4 (2000001-2005700), ca10 (3000001-3008000),
* wf1 (4000001-4000800), wf2 (5000001-5000800), wf3 (6000001-6002970),
* wf4 (7000001-7002970), dw1 (8000000-8029010) and dw2 (9000000-9029010).
*
* usage:  ./sf.x <task index 1..ngam*neps>      (games.dat in the cwd)
* output: unit 3 -> <task>   : nrep lines of gid ie u v Emax pay ef ps(1..4)
*         unit 4 -> w<task>  : header + nwin winner lines per replicate
*         unit 7 -> h<task>  : the cell header, then every strategy with a
*                              non-zero summed count:  code  count
""" % R
    s = sub(s, old_head, HEAD, "header block")
    done.append("header block")

    # ------------------------------------------------------------------ 2  population size
    s = sub(s, "      parameter (n=1000,m=1)\n",
            "      parameter (n=%d,m=1)\n" % R["n"], "n")
    done.append("n")

    # ------------------------------------------------------------------ 3  the parameter card
    s = sub(s,
            "      parameter (mgam=2048,neps=3,nu=1,nbet=1,nrep=10,nper=10)\n"
            "      parameter (iseedb=8000000)\n",
            "      parameter (mgam=1024,neps=3,nu=1,nbet=1,nrep=10,nper=10)\n"
            "      parameter (iseedb=%s)\n" % R["seed"], "parameter card")
    done.append("parameter card")

    # ------------------------------------------------------------------ 4  the mgam comment
    s = sub(s,
            "C     mgam is the game-list capacity ONLY -- it dimensions gcr/gcs/gct/gu/gv/\n"
            "C     ggid/ggic/gtag and appears nowhere in the dynamics, the PRNG stream or\n"
            "C     the payoff cache, so raising it cannot move a number.  Raised from 512\n"
            "C     to 2048 on 2026-09-04 when the 512-point sunflower took games.dat from\n"
            "C     455 rows to 967; 2048 costs 147 kB against the 300 MB requested.  The\n"
            "C     claim that the rebuild is bit-identical is not asserted, it is TESTED:\n"
            "C     see README section 'the sunflower block', which reruns a completed task\n"
            "C     with the new binary and diffs the h-file.\n",
            "C     mgam is the game-list capacity ONLY -- it dimensions gcr/gcs/gct/gu/gv/\n"
            "C     ggid/ggic/gtag and appears nowhere in the dynamics, the PRNG stream or\n"
            "C     the payoff table, so changing it cannot move a number.  games.dat holds\n"
            "C     the 512 sunflower games; 1024 is headroom.\n", "mgam comment")
    done.append("mgam comment")

    # ------------------------------------------------------------------ 5  the run values
    s = sub(s, "      data uval /1.d-02/\n", "      data uval /%s/\n" % R["u"], "uval")
    s = sub(s, "      data bval /100.d+00/\n", "      data bval /%s/\n" % R["beta"], "bval")
    s = sub(s, "      data itv  /10000000/\n", "      data itv  /%s/\n" % R["itend"], "itv")
    done += ["uval", "bval", "itv"]

    # ------------------------------------------------------------------ 6  the state count
    s = sub(s, "      parameter (nst=65536)\n",
            "      parameter (nst=16)\n"
            "C     the 16 binary memory-one strategies, embedded in memory two (see the\n"
            "C     header): mid(k) = 15 * sum_j bit_j(k) 16^j.  mid is filled at start-up\n"
            "C     and is the ONLY place the memory-two world is mentioned.\n", "nst")
    done.append("nst")

    # ------------------------------------------------------------------ 7  drop the hash cache, add the table
    s = sub(s,
            "      parameter (lcb=20,ncb=2**lcb)\n"
            "      parameter (nrb=8192)\n",
            "      parameter (nrb=8192)\n", "cache size")
    s = sub(s, "      dimension f(n),ps(16)\n", "      dimension f(n),ps(4)\n", "ps")
    s = sub(s,
            "      integer s(n),sn(n),nset(16),iwin(nwin),si,sj\n"
            "      integer*8 hist(0:nst-1),nsetl(16),ntot,nhit,nmis,ndist,mcb\n",
            "      integer s(n),sn(n),iwin(nwin),si,sj,mid(0:nst-1)\n"
            "      integer*8 hist(0:nst-1),nsetl(4),ntot,ndist\n", "declarations")
    s = sub(s,
            "      integer*8 ckey(0:ncb-1),key,ih\n"
            "      dimension cvl(0:ncb-1),cvh(0:ncb-1)\n"
            "      dimension rb(nrb)\n"
            "      character*16 bits\n",
            "      dimension vlt(0:nst-1,0:nst-1),vht(0:nst-1,0:nst-1)\n"
            "      dimension rb(nrb)\n"
            "      character*4 bits\n", "table declarations")
    s = sub(s,
            "      common /epsval/ pmin,pmax\n"
            "      common /pcache/ ckey,cvl,cvh\n"
            "      common /phist/ hist\n",
            "      common /epsval/ pmin,pmax\n"
            "      common /phist/ hist\n", "pcache common")
    done += ["cache size", "ps", "declarations", "table declarations", "pcache common"]

    # ------------------------------------------------------------------ 8  the 16 x 16 payoff table
    s = sub(s,
            "C     the payoff cache is cleared once per task, not once per replicate\n"
            "\n"
            "      mcb=int(ncb,8)-1\n"
            "      do islot=0,ncb-1\n"
            "         ckey(islot)=-1\n"
            "      enddo\n"
            "      nhit=0\n"
            "      nmis=0\n",
            "C     the 16 x 16 payoff table, built once per task with dw1's own payf3 on\n"
            "C     the embedded ids and dw1's own two payoff lines.  vlt(i,j) is i's\n"
            "C     per-round payoff against j and vht(i,j) is j's against i, so the pair\n"
            "C     (i,j) needs one call and the generation loop needs no min/max swap.\n"
            "C     With 16 strategies the table is 136 distinct calls against dw1's hash\n"
            "C     cache of 2^20 slots; the loop reads it in place of the cache and draws\n"
            "C     the same random numbers in the same order.\n"
            "\n"
            "      do k=0,nst-1\n"
            "         mid(k)=0\n"
            "         do j=0,3\n"
            "            if (btest(k,j)) mid(k)=mid(k)+15*(16**j)\n"
            "         enddo\n"
            "      enddo\n"
            "      do ia=0,nst-1\n"
            "         do ib=ia,nst-1\n"
            "            call payf3(mid(ia),mid(ib),w0,w1,w2,w3)\n"
            "            vl=rr*w0+ss*w1+tt*w2\n"
            "            vh=rr*w0+tt*w1+ss*w2\n"
            "            vlt(ia,ib)=vl\n"
            "            vht(ia,ib)=vh\n"
            "            vlt(ib,ia)=vh\n"
            "            vht(ib,ia)=vl\n"
            "         enddo\n"
            "      enddo\n", "payoff table")
    done.append("payoff table")

    # ------------------------------------------------------------------ 9  the initial population
    s = sub(s,
            "C     initial population: 16 fair coins per player, as in s.f\n"
            "\n"
            "      do i=1,n\n"
            "         is=0\n"
            "         do k=1,16\n",
            "C     initial population: 4 fair coins per player -- the memory-one analogue\n"
            "C     of dw1's 16, i.e. uniform on the 16 strategies\n"
            "\n"
            "      do i=1,n\n"
            "         is=0\n"
            "         do k=1,4\n", "initial population")
    done.append("initial population")

    # ------------------------------------------------------------------ 10  the pair payoff in the loop
    s = sub(s,
            "               sj=s(j)\n"
            "\n"
            "               if (si.le.sj) then\n"
            "                  ia=si\n"
            "                  ib=sj\n"
            "                  isw=0\n"
            "               else\n"
            "                  ia=sj\n"
            "                  ib=si\n"
            "                  isw=1\n"
            "               endif\n"
            "               key=int(ia,8)*65536+int(ib,8)\n"
            "               ih=ieor(key,ishft(key,-17))\n"
            "               ih=ih*1000003\n"
            "               ih=ieor(ih,ishft(ih,-11))\n"
            "               islot=int(iand(ih,mcb))\n"
            "               if (ckey(islot).eq.key) then\n"
            "                  vl=cvl(islot)\n"
            "                  vh=cvh(islot)\n"
            "                  nhit=nhit+1\n"
            "               else\n"
            "                  call payf3(ia,ib,w0,w1,w2,w3)\n"
            "                  vl=rr*w0+ss*w1+tt*w2\n"
            "                  vh=rr*w0+tt*w1+ss*w2\n"
            "                  ckey(islot)=key\n"
            "                  cvl(islot)=vl\n"
            "                  cvh(islot)=vh\n"
            "                  nmis=nmis+1\n"
            "               endif\n"
            "               if (isw.eq.0) then\n"
            "                  f(i)=f(i)+vl\n"
            "                  f(j)=f(j)+vh\n"
            "               else\n"
            "                  f(i)=f(i)+vh\n"
            "                  f(j)=f(j)+vl\n"
            "               endif\n",
            "               sj=s(j)\n"
            "\n"
            "               f(i)=f(i)+vlt(si,sj)\n"
            "               f(j)=f(j)+vht(si,sj)\n", "pair payoff")
    done.append("pair payoff")

    # ------------------------------------------------------------------ 11  mutation: 16 states, not 65536
    s = sub(s,
            "               if (imut.eq.1) then\n"
            "C                 one integer draw supplies all 16 loci\n"
            "                  if (irb.ge.nrb) then\n"
            "                     call mtfill(rb,nrb)\n"
            "                     irb=0\n"
            "                  endif\n"
            "                  irb=irb+1\n"
            "                  sn(i)=int(rb(irb)*65536.d+00)\n"
            "               else\n"
            "C                 legacy: 16 separate uniforms\n"
            "                  is=0\n"
            "                  do k=1,16\n",
            "               if (imut.eq.1) then\n"
            "C                 one integer draw supplies all 4 loci\n"
            "                  if (irb.ge.nrb) then\n"
            "                     call mtfill(rb,nrb)\n"
            "                     irb=0\n"
            "                  endif\n"
            "                  irb=irb+1\n"
            "                  sn(i)=int(rb(irb)*16.d+00)\n"
            "               else\n"
            "C                 legacy: 4 separate uniforms\n"
            "                  is=0\n"
            "                  do k=1,4\n", "mutation")
    done.append("mutation")

    # ------------------------------------------------------------------ 12  the per-locus cooperation record
    s = sub(s,
            "      ntot=0\n"
            "      ndist=0\n"
            "      do k=1,16\n"
            "         nsetl(k)=0\n"
            "      enddo\n",
            "      ntot=0\n"
            "      ndist=0\n"
            "      do k=1,4\n"
            "         nsetl(k)=0\n"
            "      enddo\n", "nsetl clear")
    s = sub(s,
            "            do k=1,16\n"
            "               if (btest(is,k-1)) nsetl(k)=nsetl(k)+hist(is)\n"
            "            enddo\n",
            "            do k=1,4\n"
            "               if (btest(is,k-1)) nsetl(k)=nsetl(k)+hist(is)\n"
            "            enddo\n", "nsetl accumulate")
    s = sub(s,
            "      do k=1,16\n"
            "         ps(k)=(pmax*dble(nsetl(k))\n"
            "     &         +pmin*dble(ntot-nsetl(k)))*rrn/z\n"
            "      enddo\n",
            "      do k=1,4\n"
            "         ps(k)=(pmax*dble(nsetl(k))\n"
            "     &         +pmin*dble(ntot-nsetl(k)))*rrn/z\n"
            "      enddo\n", "ps compute")
    s = sub(s,
            "      write (3,'(2i8,2f14.6,19f16.10)') ggid(ig),ie,gu(ig),gv(ig),\n"
            "     &      emax,pay,ef,(ps(k),k=1,16)\n",
            "      write (3,'(2i8,2f14.6,7f16.10)') ggid(ig),ie,gu(ig),gv(ig),\n"
            "     &      emax,pay,ef,(ps(k),k=1,4)\n", "unit 3 write")
    done += ["nsetl clear", "nsetl accumulate", "ps compute", "unit 3 write"]

    # ------------------------------------------------------------------ 13  the w-file: no cache counters
    s = sub(s,
            "      write (4,'(a)')\n"
            "     & '# run: isl ie eps gid u v irun pay ef ndist ntot nhit nmis'\n",
            "      write (4,'(a)')\n"
            "     & '# run: isl ie eps gid u v irun pay ef ndist ntot'\n", "w header 1")
    s = sub(s,
            "      write (4,'(a,2i7,e11.3,i7,2f10.4,i7,2f12.7,i9,3i16)') '# ',\n"
            "     &      isl,ie,eps,ggid(ig),gu(ig),gv(ig),irun,pay,ef,\n"
            "     &      ndist,ntot,nhit,nmis\n",
            "      write (4,'(a,2i7,e11.3,i7,2f10.4,i7,2f12.7,i9,i16)') '# ',\n"
            "     &      isl,ie,eps,ggid(ig),gu(ig),gv(ig),irun,pay,ef,\n"
            "     &      ndist,ntot\n", "w run line")
    done += ["w header 1", "w run line"]

    # ------------------------------------------------------------------ 14  the winner lines: 4 loci, 4 bits
    s = sub(s,
            "         call payf3(is,is,w0,w1,w2,w3)\n"
            "         spay=rr*w0+ss*w1+tt*w2\n"
            "         do k=1,16\n",
            "         call payf3(mid(is),mid(is),w0,w1,w2,w3)\n"
            "         spay=rr*w0+ss*w1+tt*w2\n"
            "         do k=1,4\n", "winner selfpay")
    s = sub(s,
            "         write (4,'(i8,e11.3,i7,2i6,i7,f12.8,2f12.7,4f11.8,1x,a16)')\n",
            "         write (4,'(i8,e11.3,i7,2i6,i7,f12.8,2f12.7,4f11.8,1x,a4)')\n",
            "winner write")
    done += ["winner selfpay", "winner write"]

    # ------------------------------------------------------------------ 15  the h-file header line
    s = sub(s,
            "      write (7,'(a)') '# code  count  (summed over nrep)'\n",
            "      write (7,'(a)') '# code  count  (summed over nrep; code 0..15)'\n",
            "h header")
    done.append("h header")

    assert len(done) == NEDIT, "%d edits applied, expected %d" % (len(done), NEDIT)
    # the hash cache and the 16-bit genome are gone from the CODE (the header comment still
    # explains both, and names the embedded ids 65535 / 3855 / 61455)
    code = "".join(l for l in s.splitlines(keepends=True) if l[:1] not in ("C", "*", "c", "!"))
    for bad in ("ckey", "cvl(", "cvh(", "nhit", "nmis", "mcb", "65536", "nset(16)", "character*16",
                "lcb", "ncb", "pcache"):
        assert bad not in code, "the built source still mentions %r" % bad
    return s, done


def main():
    import hashlib
    sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    assert sha == SRC_SHA, "Ref/sf_dw1.f is not the vendored dw1/sf.f (sha %s)" % sha
    src = open(SRC).read().splitlines(keepends=True)
    for name in sorted(RUNS):
        s, done = build(name)
        p = os.path.join(KIT, name)
        open(p, "w").write(s)
        d = list(difflib.unified_diff(src, s.splitlines(keepends=True),
                                      "Ref/sf_dw1.f", "Cannon/mw/" + name, n=0))
        nplus = sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
        nminus = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
        print("%s: %d edits, %d lines (-%d +%d against dw1)" % (name, len(done), s.count("\n"), nminus, nplus))
        if "--diff" in sys.argv:
            sys.stdout.writelines(d)
    # the two builds differ in exactly the five run-parameter lines and the header's Grid/seed block
    a, b = build("sf1.f")[0].splitlines(), build("sf2.f")[0].splitlines()
    dd = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(a) == len(b), "the two builds differ in line count"
    print("sf1.f vs sf2.f: %d lines differ" % len(dd))
    for x, y in dd:
        print("   -%s\n   +%s" % (x, y))


if __name__ == "__main__":
    main()
