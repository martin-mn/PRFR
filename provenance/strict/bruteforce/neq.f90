! =====================================================================
!  neq.f90 -- re-adjudicate borderline strict-NE verdicts in QUADRUPLE
!  precision.
!
!  THE DEFECT.  nescan.f90 decides strict Nash by the sign of
!      margin(s) = pi(s,s) - max_{t/=s} pi(t,s)
!  formed as a DOUBLE subtraction of two payoffs.  In self-play a binary
!  memory-two pair chain visits at most 4 of its 16 states, so at eps = 0
!  every resident ties exactly with at least 4095 others: the strict-NE
!  category here exists only because of the implementation error, and the
!  margins it creates are of order eps^4 ~ 1e-16.  One ulp of a payoff of
!  order 1 is 2.22e-16 -- LARGER -- so for residents whose self-payoff is
!  O(1) (ALLC in the Harmony and Stag Hunt corners) the sign of that
!  subtraction is roundoff, not arithmetic.  The symptom is visible in the
!  shipped margins: gids 2046, 2067 and 2211 record exactly -1.1102e-16 or
!  -2.2204e-16 for ALLC, i.e. -0.5 and -1.0 ulp of 1.0.
!
!  TWO-SIDED, DELIBERATELY.  Of the 2014 verdicts with |margin| <= 1e-14,
!  only 161 are non-positive; 1853 are currently counted AS strict NE and
!  are just as likely to be false positives, and 124 are exactly 0.
!  Re-adjudicating one side only would fix the count in one direction and
!  leave it wrong in the other.
!
!  HOW.  No source is edited: payf2.f and payf3.f are compiled unchanged
!  with gfortran's -freal-8-real-16, which promotes every double to
!  real(16).  The pair chain, the mb table, the eps common block and this
!  driver are then all quad (ulp ~1e-34, eighteen orders below the margins
!  being decided), and there is no hand-transcribed second copy of the
!  payoff code to get wrong.  That is the whole point of the flag.
!
!  eps is formed as 10**(-keps) in quad.  It differs from the double 1e-4
!  the original scan used by ~5.6e-21 relative, which moves an O(eps^4)
!  margin by ~1e-32 -- far below any margin here, so the two agree on
!  every sign.
!
!  usage: ./neq.x <games.dat> <candfile> <keps> <out>
!    candfile: one "gid s margin_double" per line, ASCENDING IN gid so that
!    each cell's payoffs are set up once.
!
!  WRITES, one line per candidate:
!    gid s margin_double margin_quad verdict_double verdict_quad
!  with verdict = 1 iff margin > 0.
! =====================================================================
program neq
   implicit none
   integer, parameter :: qp = kind(1.0d0)       ! real(16) under -freal-8-real-16
   integer, parameter :: NST = 65536, MAXG = 4096, MAXC = 200000
   character(len=256) :: gfile,cfile,ofile,arg,lbuf
   integer :: keps,ng,ios,i,j,nc,u2,gid,s,t,ig,vd,vq
   integer :: gidv(MAXG),icv(MAXG)
   real(qp) :: gcR(MAXG),gcS(MAXG),gcT(MAXG),gu(MAXG),gv(MAXG)
   character(len=32) :: gtag(MAXG)
   ! kg/ks/km, NOT cg/cs/cm: Fortran is case-insensitive and cs would
   ! be the same symbol as the payoff cS.  See CODE_AND_DATA.md trap 3.
   integer :: kg(MAXC),ks(MAXC)
   real(qp) :: km(MAXC)
   real(qp) :: cR,cS,cT,eps,w0,w1,w2,w3,selfp,best,pv,mq
   real(qp) :: pmin,pmax
   common /epsval/ pmin,pmax
   real :: t0,t1

   call get_command_argument(1,gfile)
   call get_command_argument(2,cfile)
   call get_command_argument(3,arg); read(arg,*) keps
   call get_command_argument(4,ofile)
   eps = 10.0_qp**(-real(keps,qp))
   pmin = eps; pmax = 1.0_qp - eps
   call payf2ini
   write(*,'(a,i0,a,i0)') 'quad precision: kind = ',qp, &
        '   digits = ',precision(eps)

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

   open(unit=10,file=trim(cfile),status='old'); nc = 0
   do
      read(10,*,iostat=ios) gid,s,mq
      if (ios /= 0) exit
      nc = nc + 1; kg(nc) = gid; ks(nc) = s; km(nc) = mq
   end do
   close(10)
   write(*,'(a,i0,a)') 'candidates: ',nc,'  (re-adjudicating both signs)'
   flush(6)

   open(newunit=u2,file=trim(ofile),status='replace')
   ig = -1
   call cpu_time(t0)
   do i = 1,nc
      if (ig < 0 .or. gidv(ig) /= kg(i)) then
         ig = -1
         do j = 1,ng
            if (gidv(j) == kg(i)) ig = j
         end do
         if (ig < 0) then
            write(*,'(a,i0)') 'gid not in games file: ',kg(i); stop 2
         end if
         cR = gcR(ig); cS = gcS(ig); cT = gcT(ig)
      end if
      s = ks(i)
      call payf3(s,s,w0,w1,w2,w3)
      selfp = cR*w0 + cS*w1 + cT*w2
      best = -huge(1.0_qp)
      ! the whole 65535 in quad -- NOT a double shortlist.  At eps = 0 the
      ! tie set is thousands of strategies deep, so "the top few by the
      ! double payoff" is exactly the set whose ordering is unreliable.
      !$omp parallel do private(t,w0,w1,w2,w3,pv) reduction(max:best) &
      !$omp             schedule(static)
      do t = 0,NST-1
         if (t /= s) then
            call payf3(t,s,w0,w1,w2,w3)
            pv = cR*w0 + cS*w1 + cT*w2
            if (pv > best) best = pv
         end if
      end do
      !$omp end parallel do
      mq = selfp - best
      vd = 0; if (km(i) > 0.0_qp) vd = 1
      vq = 0; if (mq    > 0.0_qp) vq = 1
      write(u2,'(i8,i8,es26.17,es44.34,2i3)') kg(i),s,km(i),mq,vd,vq
      if (mod(i,200) == 0) then
         call cpu_time(t1)
         write(*,'(a,i7,a,i7,a,f8.1,a)') '   ',i,' of ',nc,'  [',t1-t0,' cpu-s]'
         flush(6)
      end if
   end do
   close(u2)
   call cpu_time(t1)
   write(*,'(a,i0,a,f9.1,a)') 'done ',nc,' candidates, ',t1-t0,' cpu-s'
end program neq
