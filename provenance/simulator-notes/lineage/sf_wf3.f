* M2 strategies; WF pairwise comparison  (synchronous Fermi imitation)
*
* wf3 = the FINE COST GRID, so the WF process can be drawn on the same
* 99-cost grid as the paper's ca8 and SI Fig 8: c = 0.01 .. 0.99 in steps of
* 0.01, three error rates, at beta = 100 and u = 1e-2 only.
*
* A separate kit rather than a widened wf1/wf2, so that their task indices
* keep the meaning their data was written with -- the ca7/ca8 lesson.
* `diff wf3/sf.f wf2/sf.f` touches only the header, the PARAMETER card, the
* four tables and the seed base.  The generation loop is untouched and still
* reproduces ca10 bit-for-bit.
*
* wf1 = ca10's process, with u and beta lifted out of the PARAMETER card
* into tables so they can be swept, and with the FULL 65536-state abundance
* histogram written out, summed over the replicates of a cell.
*
* The dynamics are byte-identical to Cannon/ca10/sf.f.  `diff` against it
* touches only: the header, the parameter card, the tables, the task decode,
* the seed base, and the new htot output.  The generation loop is untouched.
*
* Grid (Martin, Aug 29):
*     N = 1000, m = 1, beta = 100, u = 1e-2
*     eps = 1e-2, 1e-3, 1e-4                 (3)
*     c   = 0.01 ... 0.99 step 0.01          (99)
*     nrep = 10 replicates of itend = 1e7 generations, second half sampled
*     u*itend = 1e5 substitutions a run, as in ca4/ca10
*
* nper = nrep = 10: ONE TASK = ONE CELL, so ntask = neps*nc = 297 and each
* task's h-file IS the cell's summed abundance -- no downstream summing.
* At ~75 min a task that is a small thing to lose.  nper = 1 would give 2970
* tasks and 4.6 GB of h-files instead of 297 and 0.5 GB, for the same CPU.
*
* Task order, beta OUTERMOST so a second intensity appends tasks without
* moving the first block's indices (the ca7/ca8 lesson):
*     ic = mod(isl-1,nc)+1              c = 0.01*ic
*     ie = mod((isl-1)/nc,neps)+1       1-99 eps=1e-2, 100-198 1e-3,
*                                       199-297 1e-4
*     iu = 1, ib = 1  (single u, single beta)
*
* itend is still a table indexed by iu, with one entry here.  A run makes
* ~ u*itend substitutions, so 1e7 at u = 1e-2 gives the 1e5 that ca4 and
* ca10 used.
*
* Seeds 6000001 .. 6002970, disjoint from ca2 (43891-45890), ca3 (743891-
* 744890), ca4 (2000001-2005700), ca10 (3000001-3008000), wf1 (4000001-
* 4000800) and wf2 (5000001-5000800).
*
* usage:  ./sf.x <task index 1..297>
* output: unit 3 -> <task>   : nrep lines of  c, ef, ps(1..16)
*         unit 4 -> w<task>  : header + nwin winner lines per replicate
*         unit 7 -> h<task>  : the cell line, then every strategy with a
*                              non-zero summed count:  code  count
*
      program sb

      implicit real*8 (a-h,o-z)
      character*12 slurm,wfile,hfile

      parameter (o0=0.d+00,oh=0.5d+00,o1=1.d+00,o2=2.d+00)
      parameter (n=1000,m=1)
      parameter (rn=dfloat(n),rrn=o1/rn,rrn1=o1/dfloat(n-1))
      parameter (rrm=oh/dfloat(m))
      parameter (nc=99,neps=3,nu=1,nbet=1,nrep=10,nper=10)
      dimension cval(nc),epsv(neps),uval(nu),bval(nbet)
      integer itv(nu)
      parameter (ntpc=nrep/nper)
      parameter (nwin=10)
      parameter (imut=1)
      parameter (nst=65536)
      parameter (lcb=20,ncb=2**lcb)
      parameter (nrb=8192)
      parameter (thr=25.d+00)

      dimension f(n),ps(16)
      data cval /0.01d0,0.02d0,0.03d0,0.04d0,0.05d0,0.06d0,0.07d0,
     &           0.08d0,0.09d0,0.10d0,0.11d0,0.12d0,0.13d0,0.14d0,
     &           0.15d0,0.16d0,0.17d0,0.18d0,0.19d0,0.20d0,0.21d0,
     &           0.22d0,0.23d0,0.24d0,0.25d0,0.26d0,0.27d0,0.28d0,
     &           0.29d0,0.30d0,0.31d0,0.32d0,0.33d0,0.34d0,0.35d0,
     &           0.36d0,0.37d0,0.38d0,0.39d0,0.40d0,0.41d0,0.42d0,
     &           0.43d0,0.44d0,0.45d0,0.46d0,0.47d0,0.48d0,0.49d0,
     &           0.50d0,0.51d0,0.52d0,0.53d0,0.54d0,0.55d0,0.56d0,
     &           0.57d0,0.58d0,0.59d0,0.60d0,0.61d0,0.62d0,0.63d0,
     &           0.64d0,0.65d0,0.66d0,0.67d0,0.68d0,0.69d0,0.70d0,
     &           0.71d0,0.72d0,0.73d0,0.74d0,0.75d0,0.76d0,0.77d0,
     &           0.78d0,0.79d0,0.80d0,0.81d0,0.82d0,0.83d0,0.84d0,
     &           0.85d0,0.86d0,0.87d0,0.88d0,0.89d0,0.90d0,0.91d0,
     &           0.92d0,0.93d0,0.94d0,0.95d0,0.96d0,0.97d0,0.98d0,
     &           0.99d0/
      data epsv /1.d-02,1.d-03,1.d-04/
      data uval /1.d-02/
      data bval /100.d+00/
C     run length per u; raise the 1e-4 entry to keep u*itend fixed
      data itv  /10000000/
      integer s(n),sn(n),nset(16),iwin(nwin),si,sj
      integer*8 hist(0:nst-1),nsetl(16),ntot,nhit,nmis,ndist,mcb
      integer*8 htot(0:nst-1),ntotc
      integer*8 hbest
      integer*8 ckey(0:ncb-1),key,ih
      dimension cvl(0:ncb-1),cvh(0:ncb-1)
      dimension rb(nrb)
      character*16 bits

      common /epsval/ pmin,pmax
      common /pcache/ ckey,cvl,cvh
      common /phist/ hist
      common /thist/ htot

      call get_command_argument(1,slurm)
      slurm=trim(adjustl(slurm))
      read(slurm,*) isl
      wfile='w'//slurm
      hfile='h'//slurm

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
C     task order, fastest first: replicate block, c, u, eps, beta.  beta is
C     outermost so a second intensity appends tasks without moving the
C     first block's indices.

      iblk =mod(isl-1,ntpc)+1
      ic   =mod((isl-1)/ntpc,nc)+1
      iu   =mod((isl-1)/(ntpc*nc),nu)+1
      ie   =mod((isl-1)/(ntpc*nc*nu),neps)+1
      ib   =(isl-1)/(ntpc*nc*nu*neps)+1
      c=cval(ic)
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

      write (4,'(a)')
     & '# run: isl ie eps ic c irun ef ndist ntot nhit nmis'
      write (4,'(a)')
     & '# win: isl eps c irun rank code abund selfpay cc cd dc dd bits'
      write (7,'(a,i6,a,e11.3,a,e11.3,a,f8.4,a,f9.1,a,i5,a,i12)')
     & '# cell: isl ',isl,'  eps ',eps,'  u ',u,'  c ',c,
     & '  beta ',beta,'  nper ',nper,'  itend ',itend
      write (7,'(a)') '# code  count  (summed over nrep)'
      do is=0,nst-1
         htot(is)=0
      enddo
      ntotc=0

C     donation game payoffs

      rr=o1-c
      ss=-c
      tt=o1

C     the payoff cache is cleared once per task, not once per replicate

      mcb=int(ncb,8)-1
      do islot=0,ncb-1
         ckey(islot)=-1
      enddo
      nhit=0
      nmis=0

C     ================= replicate loop =================

      do irep=1,nper

      irun=(iblk-1)*nper+irep
      iseed=6000000+(isl-1)*nper+irep
      call init_genrand(iseed)
      irb=nrb

      do is=0,nst-1
         hist(is)=0
      enddo
      z=o0
      ef=o0

C     initial population: 16 fair coins per player, as in s.f

      do i=1,n
         is=0
         do k=1,16
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

               if (si.le.sj) then
                  ia=si
                  ib=sj
                  isw=0
               else
                  ia=sj
                  ib=si
                  isw=1
               endif
               key=int(ia,8)*65536+int(ib,8)
               ih=ieor(key,ishft(key,-17))
               ih=ih*1000003
               ih=ieor(ih,ishft(ih,-11))
               islot=int(iand(ih,mcb))
               if (ckey(islot).eq.key) then
                  vl=cvl(islot)
                  vh=cvh(islot)
                  nhit=nhit+1
               else
                  call payf3(ia,ib,w0,w1,w2,w3)
                  vl=rr*w0+ss*w1+tt*w2
                  vh=rr*w0+tt*w1+ss*w2
                  ckey(islot)=key
                  cvl(islot)=vl
                  cvh(islot)=vh
                  nmis=nmis+1
               endif
               if (isw.eq.0) then
                  f(i)=f(i)+vl
                  f(j)=f(j)+vh
               else
                  f(i)=f(i)+vh
                  f(j)=f(j)+vl
               endif
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
C                 one integer draw supplies all 16 loci
                  if (irb.ge.nrb) then
                     call mtfill(rb,nrb)
                     irb=0
                  endif
                  irb=irb+1
                  sn(i)=int(rb(irb)*65536.d+00)
               else
C                 legacy: 16 separate uniforms
                  is=0
                  do k=1,16
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

      ef=ef*rrn*rrm/(z*(o1-c))

      ntot=0
      ndist=0
      do k=1,16
         nsetl(k)=0
      enddo
      do is=0,nst-1
         if (hist(is).ne.0) then
            ndist=ndist+1
            ntot=ntot+hist(is)
            htot(is)=htot(is)+hist(is)
            do k=1,16
               if (btest(is,k-1)) nsetl(k)=nsetl(k)+hist(is)
            enddo
         endif
      enddo
      do k=1,16
         ps(k)=(pmax*dble(nsetl(k))
     &         +pmin*dble(ntot-nsetl(k)))*rrn/z
      enddo

      ntotc=ntotc+ntot
      write (3,'(18f16.10)') c,ef,(ps(k),k=1,16)
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

      write (4,'(a,2i7,e11.3,i5,f8.4,i7,f12.7,i9,3i16)') '# ',
     &      isl,ie,eps,ic,c,irun,ef,ndist,ntot,nhit,nmis
      do iw=1,nwin
         is=iwin(iw)
         ab=dble(hist(is))/dble(ntot)
         call payf3(is,is,w0,w1,w2,w3)
         spay=rr*w0+ss*w1+tt*w2
         do k=1,16
            if (btest(is,k-1)) then
               bits(k:k)='C'
            else
               bits(k:k)='D'
            endif
         enddo
         write (4,'(i8,e11.3,f8.4,2i6,i7,f12.8,f12.7,4f11.8,1x,a16)')
     &         isl,eps,c,irun,iw,is,ab,spay,w0,w1,w2,w3,bits
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
