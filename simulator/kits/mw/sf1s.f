* M1 strategies; WF pairwise comparison  (synchronous Fermi imitation)
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
*     F1s: N = 1000, beta = 100, u = 1e-2, itend = 1e5  (F1 with itend cut 100x)
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
* Seeds 12000000 + (isl-1)*nper + irep, disjoint from ca2 (43891-45890),
* ca3 (743891-744890), ca4 (2000001-2005700), ca10 (3000001-3008000),
* wf1 (4000001-4000800), wf2 (5000001-5000800), wf3 (6000001-6002970),
* wf4 (7000001-7002970), dw1 (8000000-8029010) and dw2 (9000000-9029010).
*
* usage:  ./sf.x <task index 1..ngam*neps>      (games.dat in the cwd)
* output: unit 3 -> <task>   : nrep lines of gid ie u v Emax pay ef ps(1..4)
*         unit 4 -> w<task>  : header + nwin winner lines per replicate
*         unit 7 -> h<task>  : the cell header, then every strategy with a
*                              non-zero summed count:  code  count
      program sb

      implicit real*8 (a-h,o-z)
      character*12 slurm,wfile,hfile
      character*200 lbuf,lb

      parameter (o0=0.d+00,oh=0.5d+00,o1=1.d+00,o2=2.d+00)
      parameter (n=1000,m=1)
      parameter (rn=dfloat(n),rrn=o1/rn,rrn1=o1/dfloat(n-1))
      parameter (rrm=oh/dfloat(m))
C     mgam is the game-list capacity ONLY -- it dimensions gcr/gcs/gct/gu/gv/
C     ggid/ggic/gtag and appears nowhere in the dynamics, the PRNG stream or
C     the payoff table, so changing it cannot move a number.  games.dat holds
C     the 512 sunflower games; 1024 is headroom.
      parameter (mgam=1024,neps=3,nu=1,nbet=1,nrep=10,nper=10)
      parameter (iseedb=12000000)
      dimension epsv(neps),uval(nu),bval(nbet)
      integer itv(nu)
C     the game list, read from games.dat at start-up
      dimension gcr(mgam),gcs(mgam),gct(mgam),gu(mgam),gv(mgam)
      integer ggid(mgam),ggic(mgam)
      character*24 gtag(mgam)
      parameter (ntpc=nrep/nper)
      parameter (nwin=10)
      parameter (imut=1)
      parameter (nst=16)
C     the 16 binary memory-one strategies, embedded in memory two (see the
C     header): mid(k) = 15 * sum_j bit_j(k) 16^j.  mid is filled at start-up
C     and is the ONLY place the memory-two world is mentioned.
      parameter (nrb=8192)
      parameter (thr=25.d+00)

      dimension f(n),ps(4)
      data epsv /1.d-02,1.d-03,1.d-04/
      data uval /1.d-02/
      data bval /100.d+00/
C     run length per u; raise the 1e-4 entry to keep u*itend fixed
      data itv  /100000/
      integer s(n),sn(n),iwin(nwin),si,sj,mid(0:nst-1)
      integer*8 hist(0:nst-1),nsetl(4),ntot,ndist
      integer*8 htot(0:nst-1),ntotc
      integer*8 hbest
      dimension vlt(0:nst-1,0:nst-1),vht(0:nst-1,0:nst-1)
      dimension rb(nrb)
      character*4 bits

      common /epsval/ pmin,pmax
      common /phist/ hist
      common /thist/ htot

      call get_command_argument(1,slurm)
      slurm=trim(adjustl(slurm))
      read(slurm,*) isl
      wfile='w'//slurm
      hfile='h'//slurm

C     ---- the game list ----------------------------------------------
C     one game per line:  gid  ic  cR  cS  cT  u  v  tag
C     cR/cS/cT are 17 significant digits and round-trip exactly; the u/v
C     columns are display only, so the dynamics never uses them.
C     ic is metadata (the donation cost index, 0 if not a donation game).
C     NOTE: DiskM2IN's games.dat is NOT interchangeable -- there ic>0 meant
C     'recompute the payoffs internally' and the cR/cS/cT columns of those
C     rows are zero placeholders.  Use Opt/mkgames.py from THIS project.
      open (unit=2,file='games.dat',status='old')
      ngam=0
   11 read (2,'(a)',end=12) lbuf
      lb=adjustl(lbuf)
      if (lb(1:1).eq.'#') goto 11
      if (len_trim(lb).eq.0) goto 11
      ngam=ngam+1
      if (ngam.gt.mgam) stop 'games.dat: too many games, raise mgam'
      read (lb,*) ggid(ngam),ggic(ngam),gcr(ngam),gcs(ngam),
     &            gct(ngam),gu(ngam),gv(ngam),gtag(ngam)
      goto 11
   12 close (2)
      if (ngam.le.0) stop 'games.dat: no games'

      open (unit=3,file=slurm)
      open (unit=4,file=wfile)
      open (unit=7,file=hfile)

C     which (beta, eps, u, c) cell this task carries, and which block of
C     replicates.  ntpc = nrep/nper tasks per cell; with nper = nrep the
C     task IS the cell and the abundance sum below is the cell's total,
C     otherwise the h-files of a cell's ntpc tasks are summed downstream
C     (Figures/wfabund.py does this).  nper = 1 is the right layout when a
C     single replicate is long enough to want its own wall clock.
C
C     task order, fastest first: replicate block, eps, u, beta, GAME.  The
C     game is outermost so that appending games to games.dat appends tasks
C     at the end and never moves an existing game's index.

      iblk =mod(isl-1,ntpc)+1
      ie   =mod((isl-1)/ntpc,neps)+1
      iu   =mod((isl-1)/(ntpc*neps),nu)+1
      ib   =mod((isl-1)/(ntpc*neps*nu),nbet)+1
      ig   =(isl-1)/(ntpc*neps*nu*nbet)+1
      if (ig.gt.ngam) stop 'task index beyond the game list'
      ic=ggic(ig)
      eps=epsv(ie)
      u=uval(iu)
      beta=bval(ib)
      itend=itv(iu)
      init=itend/2
      be=beta*rrm

C     pmin/pmax live in COMMON /epsval/ (shared with payf3), so they are
C     set here rather than declared as parameters
      pmin=eps
      pmax=o1-eps
      call payf2ini

C     THIS game's payoffs, (R,S,T,P) = (cR,cS,cT,0).  rr/ss/tt keep their
C     wf3 names so that the cache-miss line in the generation loop,
C     vl = rr*w0+ss*w1+tt*w2, is untouched -- with a donation row they are
C     (1-c,-c,1) and the arithmetic is bit-identical, not merely equal.

      rr=gcr(ig)
      ss=gcs(ig)
      tt=gct(ig)

C     the attainable optimum in self play: mutual R below the switch line
C     u+v = 1, alternation (S+T)/2 above it.  Efficiency is pay/emax.

      emax=dmax1(rr,oh*(ss+tt))

      write (4,'(a)')
     & '# run: isl ie eps gid u v irun pay ef ndist ntot'
      write (4,'(a)')
     & '# win: isl eps gid irun rank code abund selfpay'//
     & ' selfef cc cd dc dd bits'
      write (7,'(a,i7,a,i6,1x,a,a,e11.3,a,e11.3,a,f9.1)')
     & '# cell: isl ',isl,'  gid ',ggid(ig),trim(gtag(ig)),
     & '  eps ',eps,'  umut ',u,'  beta ',beta
      write (7,'(a,3f24.16,a,2f16.8,a,f24.16)')
     & '# game: cR cS cT ',rr,ss,tt,'   u v ',gu(ig),gv(ig),
     & '   Emax ',emax
      write (7,'(a,i5,a,i12,a,i3)')
     & '# run:  nper ',nper,'  itend ',itend,'  ie ',ie
      write (7,'(a,i4)') '# ic:   ',ic
      write (7,'(a)') '# code  count  (summed over nrep; code 0..15)'
      do is=0,nst-1
         htot(is)=0
      enddo
      ntotc=0

C     the game's payoffs are set above, before the headers that name them

C     the 16 x 16 payoff table, built once per task with dw1's own payf3 on
C     the embedded ids and dw1's own two payoff lines.  vlt(i,j) is i's
C     per-round payoff against j and vht(i,j) is j's against i, so the pair
C     (i,j) needs one call and the generation loop needs no min/max swap.
C     With 16 strategies the table is 136 distinct calls against dw1's hash
C     cache of 2^20 slots; the loop reads it in place of the cache and draws
C     the same random numbers in the same order.

      do k=0,nst-1
         mid(k)=0
         do j=0,3
            if (btest(k,j)) mid(k)=mid(k)+15*(16**j)
         enddo
      enddo
      do ia=0,nst-1
         do ib=ia,nst-1
            call payf3(mid(ia),mid(ib),w0,w1,w2,w3)
            vl=rr*w0+ss*w1+tt*w2
            vh=rr*w0+tt*w1+ss*w2
            vlt(ia,ib)=vl
            vht(ia,ib)=vh
            vlt(ib,ia)=vh
            vht(ib,ia)=vl
         enddo
      enddo

C     ================= replicate loop =================

      do irep=1,nper

      irun=(iblk-1)*nper+irep
      iseed=iseedb+(isl-1)*nper+irep
      call init_genrand(iseed)
      irb=nrb

      do is=0,nst-1
         hist(is)=0
      enddo
      z=o0
      ef=o0

C     initial population: 4 fair coins per player -- the memory-one analogue
C     of dw1's 16, i.e. uniform on the 16 strategies

      do i=1,n
         is=0
         do k=1,4
            if (irb.ge.nrb) then
               call mtfill(rb,nrb)
               irb=0
            endif
            irb=irb+1
            if (rb(irb).ge.oh) is=ibset(is,k-1)
         enddo
         s(i)=is
      enddo

C     dynamics

      do it=1,itend

C        fitnesses: play against m random others

         do i=1,n
            f(i)=o0
         enddo

         do i=1,n
            si=s(i)
            do l=1,m
   43          if (irb.ge.nrb) then
                  call mtfill(rb,nrb)
                  irb=0
               endif
               irb=irb+1
               j=1+int(rb(irb)*rn)
               if (j.eq.i) goto 43
               sj=s(j)

               f(i)=f(i)+vlt(si,sj)
               f(j)=f(j)+vht(si,sj)
            enddo
         enddo

C        sample the second half

         if (it.gt.init) then
            z=z+o1
            efg=o0
            do i=1,n
               efg=efg+f(i)
               is=s(i)
               hist(is)=hist(is)+1
            enddo
            ef=ef+efg
         endif

C        update: mutation or pairwise comparison

         do i=1,n

            if (irb.ge.nrb) then
               call mtfill(rb,nrb)
               irb=0
            endif
            irb=irb+1

            if (rb(irb).lt.u) then

               if (imut.eq.1) then
C                 one integer draw supplies all 4 loci
                  if (irb.ge.nrb) then
                     call mtfill(rb,nrb)
                     irb=0
                  endif
                  irb=irb+1
                  sn(i)=int(rb(irb)*16.d+00)
               else
C                 legacy: 4 separate uniforms
                  is=0
                  do k=1,4
                     if (irb.ge.nrb) then
                        call mtfill(rb,nrb)
                        irb=0
                     endif
                     irb=irb+1
                     if (rb(irb).ge.oh) is=ibset(is,k-1)
                  enddo
                  sn(i)=is
               endif

            else

               if (irb.ge.nrb) then
                  call mtfill(rb,nrb)
                  irb=0
               endif
               irb=irb+1
               j=1+int(rb(irb)*rn)

C              logistic imitation probability, xf = be*df with
C              be = beta/2m and df a sum over 2m games, so the intensity
C              acting on a per-round payoff difference is beta.
C              |xf|>thr is decided
C              without dexp: genrand_real3 lies in
C              [2**-33, 1-2**-33], so for thr=25 the comparison
C              ran<prob has the same outcome as with prob=1 or 0.

               xf=be*(f(j)-f(i))
               if (xf.ge.thr) then
                  prob=o1
               else if (xf.le.-thr) then
                  prob=o0
               else if (xf.ge.o0) then
                  prob=o1/(o1+dexp(-xf))
               else
                  ex=dexp(xf)
                  prob=ex/(o1+ex)
               endif

               if (irb.ge.nrb) then
                  call mtfill(rb,nrb)
                  irb=0
               endif
               irb=irb+1
               if (rb(irb).lt.prob) then
                  sn(i)=s(j)
               else
                  sn(i)=s(i)
               endif

            endif

         enddo

         do i=1,n
            s(i)=sn(i)
         enddo

      enddo

C     ---- output ------------------------------------------------------

C     pay = mean per-round payoff of a player, ef = pay/emax.  wf3 divided
C     by (1-c), which IS emax on the donation ray below the switch line.
      pay=ef*rrn*rrm/z
      ef=pay/emax

      ntot=0
      ndist=0
      do k=1,4
         nsetl(k)=0
      enddo
      do is=0,nst-1
         if (hist(is).ne.0) then
            ndist=ndist+1
            ntot=ntot+hist(is)
            htot(is)=htot(is)+hist(is)
            do k=1,4
               if (btest(is,k-1)) nsetl(k)=nsetl(k)+hist(is)
            enddo
         endif
      enddo
      do k=1,4
         ps(k)=(pmax*dble(nsetl(k))
     &         +pmin*dble(ntot-nsetl(k)))*rrn/z
      enddo

      ntotc=ntotc+ntot
      write (3,'(2i8,2f14.6,7f16.10)') ggid(ig),ie,gu(ig),gv(ig),
     &      emax,pay,ef,(ps(k),k=1,4)
      call flush(3)

C     the nwin most abundant strategies of the second half

      do iw=1,nwin
         iwin(iw)=-1
         hbest=-1
         do is=0,nst-1
            if (hist(is).gt.hbest) then
               idup=0
               do jw=1,iw-1
                  if (iwin(jw).eq.is) idup=1
               enddo
               if (idup.eq.0) then
                  hbest=hist(is)
                  iwin(iw)=is
               endif
            endif
         enddo
      enddo

      write (4,'(a,2i7,e11.3,i7,2f10.4,i7,2f12.7,i9,i16)') '# ',
     &      isl,ie,eps,ggid(ig),gu(ig),gv(ig),irun,pay,ef,
     &      ndist,ntot
      do iw=1,nwin
         is=iwin(iw)
         ab=dble(hist(is))/dble(ntot)
         call payf3(mid(is),mid(is),w0,w1,w2,w3)
         spay=rr*w0+ss*w1+tt*w2
         do k=1,4
            if (btest(is,k-1)) then
               bits(k:k)='C'
            else
               bits(k:k)='D'
            endif
         enddo
         write (4,'(i8,e11.3,i7,2i6,i7,f12.8,2f12.7,4f11.8,1x,a4)')
     &         isl,eps,ggid(ig),irun,iw,is,ab,spay,spay/emax,
     &         w0,w1,w2,w3,bits
      enddo
      call flush(4)

      enddo

C     ================= end replicate loop =============

C     the summed abundance of every strategy over this task's nper
C     replicates.  ntotc = nper*(itend/2)*n is the grand total, so
C     count/ntotc is the mean frequency of that strategy in the sampled
C     half of a run.  Sum the h-files of a cell's ntpc tasks for the cell.

      ndist=0
      do is=0,nst-1
         if (htot(is).ne.0) ndist=ndist+1
      enddo
      write (7,'(a,i8,a,i16)') '# distinct ',ndist,'   total ',ntotc
      do is=0,nst-1
         if (htot(is).ne.0) write (7,'(i7,1x,i16)') is,htot(is)
      enddo
      call flush(7)

      stop
      end
