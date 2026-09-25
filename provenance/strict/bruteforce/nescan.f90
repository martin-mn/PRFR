! =====================================================================
!  nescan.f90 -- the strict-NE category over the WHOLE strategy space.
!
!  nashe.f90 answers "is sigma a Nash equilibrium at eps" for a short
!  candidate list -- the ten most abundant.  At N=100, beta=3 that list
!  carries a median of 2.1% of the stationary mass, so it cannot say how
!  important the category is.  This program asks the same question for
!  every one of the 65536 residents, which is what a frequency needs.
!
!      sigma is STRICT Nash at eps  <=>  pi(sigma,sigma) > pi(tau,sigma)
!                                        for every tau /= sigma
!
!  Strict, not weak: the field treats strict NE as an absolute category.
!  Measured on the top-ten verdicts of all 512 cells, the two notions
!  coincide here -- zero exact ties, only 10 of 5120 margins inside
!  1e-15 -- so the choice changes no number, but the claim is now the
!  one the reader expects.
!
!  Convention is nashe.f90's, which is disksweep.f90's: pi(a,b) =
!  cR*w0 + cS*w1 + cT*w2 with (w0..w3) = payf3(a,b), payf3(t,s) giving
!  the frequencies t sees against s.
!
!  WHAT IT WRITES, per game:
!    ne_<gid>.dat  one summary line:
!        gid tag u v  nne massne  n10 n100 n1000  m10 m100 m1000
!      nne     how many of the 65536 are strict NE
!      massne  their total stationary mass -- the frequency, in [0,1]
!      nK      how many of the K most abundant are strict NE
!      mK      what fraction of the mass those K carry (so nK can be read)
!    ne_<gid>.bin  the MARGIN, pi(s,s) - max_t pi(t,s), float64 x 65536,
!      in strategy order.  Strict NE is margin > 0, so the indicator and
!      every top-K count follow from this file; and the CONTINUOUS
!      measures (pi-weighted invader gain, mass within a tolerance) that
!      resolve the category in later figures come out of it with no
!      further compute.  524 KB a cell, 268 MB for the grid -- cheap
!      against the 431 core-h it costs to produce.
!
!  Cost: one payf3 per (game, resident, tau) = 4.295e9 a game.  Measured
!  from nashe.x at 1.42e6 payf3 calls per core-second, that is ~0.84
!  core-h a game; read the true rate off the probe, do not trust this.
!
!  usage: ./nescan.x <games.dat> <first> <last> <keps> <simdir> <outdir>
!    first/last are ROW INDICES into games.dat, not gids -- nashe.x's
!    trap, and an out-of-range first silently produces nothing.
!    simdir supplies sim_<gid>.bin, the pi this weights by.
! =====================================================================
program nescan
   implicit none
   integer, parameter :: dp = kind(1.0d0), NST = 65536
   integer, parameter :: MAXG = 4096
   character(len=256) :: gfile,sdir,odir,arg,lbuf,fn
   integer :: ifirst,ilast,keps,ng,ig,ios,i,u2,u3
   integer :: gidv(MAXG),icv(MAXG)
   real(dp) :: gcR(MAXG),gcS(MAXG),gcT(MAXG),gu(MAXG),gv(MAXG)
   character(len=32) :: gtag(MAXG)
   integer :: s,t,nne,n10,n100,n1000,k,kbest
   real(dp) :: cR,cS,cT,w0,w1,w2,w3,selfp,best,pv,eps
   real(dp) :: massne,m10,m100,m1000,pb
   real(dp) :: pmin,pmax
   common /epsval/ pmin,pmax
   real(dp), allocatable :: pin(:),mrg(:)
   logical, allocatable :: used(:)
   integer, allocatable :: ord(:)
   logical :: ex
   real :: t0,t1

   call get_command_argument(1,gfile)
   call get_command_argument(2,arg); read(arg,*) ifirst
   call get_command_argument(3,arg); read(arg,*) ilast
   call get_command_argument(4,arg); read(arg,*) keps
   call get_command_argument(5,sdir)
   call get_command_argument(6,odir)
   eps = 10.0_dp**(-real(keps,dp))
   pmin = eps; pmax = 1.0_dp - eps
   call payf2ini

   open(unit=9,file=trim(gfile),status='old'); ng = 0
   do
      read(9,'(a)',iostat=ios) lbuf
      if (ios /= 0) exit
      if (len_trim(adjustl(lbuf)) == 0) cycle
      if (lbuf(1:1) == '#') cycle
      ng = ng + 1
      read(lbuf,*) gidv(ng),icv(ng),gcR(ng),gcS(ng),gcT(ng),gu(ng),gv(ng), &
                   gtag(ng)
   end do
   close(9)
   if (ilast > ng) ilast = ng
   if (ifirst < 1 .or. ifirst > ng) then
      write(*,'(a,i0,a,i0)') 'first row ',ifirst,' outside 1..',ng
      stop 2
   end if
   write(*,'(a,i0,a,i0,a,es9.2)') 'rows ',ifirst,'..',ilast,'   eps = ',eps
   flush(6)

   allocate(pin(0:NST-1),mrg(0:NST-1),used(0:NST-1),ord(1000))

   do ig = ifirst,ilast
      cR = gcR(ig); cS = gcS(ig); cT = gcT(ig)
      write(fn,'(a,a,i0,a)') trim(sdir),'/sim_',gidv(ig),'.bin'
      inquire(file=trim(fn),exist=ex)
      if (.not. ex) then
         write(*,'(a,a)') 'no pi for ',trim(fn); flush(6); cycle
      end if
      open(newunit=u3,file=trim(fn),form='unformatted',access='stream', &
           status='old')
      read(u3) pin
      close(u3)

      call cpu_time(t0)
      ! parallelise over the RESIDENT: each thread owns a whole inner scan,
      ! so there is no reduction across threads and no false sharing on mrg
      !$omp parallel do private(s,t,w0,w1,w2,w3,selfp,best,pv) &
      !$omp             schedule(dynamic,16)
      do s = 0,NST-1
         call payf3(s,s,w0,w1,w2,w3)
         selfp = cR*w0 + cS*w1 + cT*w2
         best = -huge(1.0_dp)
         do t = 0,NST-1
            if (t == s) cycle
            call payf3(t,s,w0,w1,w2,w3)
            pv = cR*w0 + cS*w1 + cT*w2
            if (pv > best) best = pv
         end do
         mrg(s) = selfp - best
      end do
      !$omp end parallel do
      call cpu_time(t1)

      nne = 0; massne = 0.0_dp
      do s = 0,NST-1
         if (mrg(s) > 0.0_dp) then
            nne = nne + 1; massne = massne + pin(s)
         end if
      end do

      ! the 1000 most abundant, by repeated max: 1000*65536 = 6.6e7 ops,
      ! nothing beside the 4.3e9 payf3 calls above, and obviously correct
      used = .false.
      do k = 1,1000
         pb = -1.0_dp; kbest = -1
         do s = 0,NST-1
            if (.not. used(s) .and. pin(s) > pb) then
               pb = pin(s); kbest = s
            end if
         end do
         ord(k) = kbest; used(kbest) = .true.
      end do
      n10 = 0; n100 = 0; n1000 = 0
      m10 = 0.0_dp; m100 = 0.0_dp; m1000 = 0.0_dp
      do k = 1,1000
         s = ord(k)
         if (k <= 10)  then
            m10 = m10 + pin(s);   if (mrg(s) > 0.0_dp) n10 = n10 + 1
         end if
         if (k <= 100) then
            m100 = m100 + pin(s); if (mrg(s) > 0.0_dp) n100 = n100 + 1
         end if
         m1000 = m1000 + pin(s);  if (mrg(s) > 0.0_dp) n1000 = n1000 + 1
      end do

      write(fn,'(a,a,i0,a)') trim(odir),'/ne_',gidv(ig),'.bin'
      open(newunit=u3,file=trim(fn),form='unformatted',access='stream', &
           status='replace')
      write(u3) mrg
      close(u3)
      write(fn,'(a,a,i0,a)') trim(odir),'/ne_',gidv(ig),'.dat'
      open(newunit=u2,file=trim(fn),status='replace')
      write(u2,'(i8,1x,a12,2f10.4,i8,es22.14,3i6,3es22.14)') &
           gidv(ig),trim(gtag(ig)),gu(ig),gv(ig),nne,massne, &
           n10,n100,n1000,m10,m100,m1000
      close(u2)
      write(*,'(a,i6,1x,a,a,i6,a,es11.4,a,3i5,a,f7.1,a)') &
           'gid ',gidv(ig),trim(gtag(ig)),'  nNE ',nne,'  mass ',massne, &
           '  top10/100/1000 ',n10,n100,n1000,'  [',t1-t0,' cpu-s]'
      flush(6)
   end do
end program nescan
