C=====================================================================
C  payf3 : stationary outcome frequencies of a binary M2 pair, via the
C          GTH (Grassmann-Taksar-Heyman) state-reduction algorithm.
C
C  Why GTH rather than the LU of the original code:
C    * it works on the transition matrix P itself, so no 16x16 matrix
C      (B^T - I) has to be assembled and no normalisation row is needed,
C    * it is subtraction-free, hence unconditionally stable with NO
C      pivoting at all - no 120 comparisons, no row swaps, no branches,
C    * ~1500 flops instead of ~2500 + pivot search,
C    * the inner loop is a stride-1 rank-1 update, so it vectorises,
C    * P starts with only 4 nonzeros per row/column, and the zero test
C      on P(i,n) skips most work in the early (widest) reduction steps.
C
C  Storage: g(j,i) = P(i,j)  (destination first) so that the inner
C  update  P(i,j) += P(i,n)*P(n,j)  runs contiguously over j.
C  Call payf2ini once first (shares the /pfblk/ tables).
C=====================================================================

      subroutine payf3(isa,isb,w0,w1,w2,w3)
      implicit none
      integer isa,isb
      double precision w0,w1,w2,w3

      double precision mb(4,4,0:255)
      integer ipl(0:255),iph(0:255)
      common /pfblk/ mb,ipl,iph

      double precision g(16,16),v(16)
      double precision s,sinv,pin,t
      integer i,j,n,ia,ix,ib,isbt,ipat,ic

      isbt = ipl(iand(isb,255)) + iph(ishft(isb,-8))

      do j=1,16
         do i=1,16
            g(i,j)=0.d0
         enddo
      enddo

C---- P(source,dest): from state (a,b) the chain moves to (x,a).
C     source i = 1+4a+b , destination = 1+4x+a
      do ia=0,3
         ipat = iand(ishft(isa ,-4*ia),15)
     &     + 16*iand(ishft(isbt,-4*ia),15)
         do ib=0,3
            ic = 1+4*ia+ib
            g(1   +ia,ic) = mb(ib+1,1,ipat)
            g(5   +ia,ic) = mb(ib+1,2,ipat)
            g(9   +ia,ic) = mb(ib+1,3,ipat)
            g(13  +ia,ic) = mb(ib+1,4,ipat)
         enddo
      enddo

C---- GTH state reduction
      do n=16,2,-1
         s=0.d0
         do j=1,n-1
            s=s+g(j,n)
         enddo
         sinv=1.d0/s
         do i=1,n-1
            pin=g(n,i)
            if (pin.ne.0.d0) then
               pin=pin*sinv
               g(n,i)=pin
               do j=1,n-1
                  g(j,i)=g(j,i)+pin*g(j,n)
               enddo
            endif
         enddo
      enddo

C---- back substitution
      v(1)=1.d0
      t=1.d0
      do n=2,16
         s=0.d0
         do i=1,n-1
            s=s+v(i)*g(n,i)
         enddo
         v(n)=s
         t=t+s
      enddo
      t=1.d0/t

      w0=(v(1 )+v(2 )+v(3 )+v(4 ))*t
      w1=(v(5 )+v(6 )+v(7 )+v(8 ))*t
      w2=(v(9 )+v(10)+v(11)+v(12))*t
      w3=(v(13)+v(14)+v(15)+v(16))*t
      return
      end
