c-----------------------------------------------------------------------
c  mtfill : fill rb(1:nb) with exactly the sequence that repeated calls
c           to genrand_real3() would return.  Identical stream, but the
c           per-number subroutine-call overhead is gone and the temper /
c           convert loop vectorises.
c-----------------------------------------------------------------------
      subroutine mtfill(rb,nb)
      integer nb
      double precision rb(nb)
      integer N,M,DONE
      parameter (N=624)
      parameter (M=397)
      parameter (DONE=123456789)
      integer UPPER_MASK,LOWER_MASK,MATRIX_A,T1_MASK,T2_MASK
      integer mti,initialized
      integer mt(0:N-1)
      integer mag01(0:1)
      common /mt_state1/ mti,initialized
      common /mt_state2/ mt
      common /mt_mask3/ UPPER_MASK,LOWER_MASK,MATRIX_A,T1_MASK,T2_MASK
      common /mt_mag01/ mag01
      integer ii,kk,y,nc,j
      integer*8 iy
      double precision r
      double precision rnorm
      parameter (rnorm=1.d0/4294967296.d0)
c
      if(initialized.ne.DONE) call init_genrand(21641)
      ii=1
 10   if(ii.gt.nb) return
      if(mti.ge.N)then
        do 100 kk=0,N-M-1
          y=ior(iand(mt(kk),UPPER_MASK),iand(mt(kk+1),LOWER_MASK))
          mt(kk)=ieor(ieor(mt(kk+M),ishft(y,-1)),mag01(iand(y,1)))
  100   continue
        do 200 kk=N-M,N-1-1
          y=ior(iand(mt(kk),UPPER_MASK),iand(mt(kk+1),LOWER_MASK))
          mt(kk)=ieor(ieor(mt(kk+(M-N)),ishft(y,-1)),mag01(iand(y,1)))
  200   continue
        y=ior(iand(mt(N-1),UPPER_MASK),iand(mt(0),LOWER_MASK))
        mt(kk)=ieor(ieor(mt(M-1),ishft(y,-1)),mag01(iand(y,1)))
        mti=0
      endif
      nc=min(nb-ii+1,N-mti)
      do 300 j=0,nc-1
        y=mt(mti+j)
        y=ieor(y,ishft(y,-11))
        y=ieor(y,iand(ishft(y,7),T1_MASK))
        y=ieor(y,iand(ishft(y,15),T2_MASK))
        y=ieor(y,ishft(y,-18))
        iy=iand(int(y,8),4294967295_8)
        rb(ii+j)=(dble(iy)+0.5d0)*rnorm
  300 continue
      mti=mti+nc
      ii=ii+nc
      goto 10
      end
