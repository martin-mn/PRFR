C=====================================================================
C  payf2 : same result as payf, but
C    * the 4 diagonal 4x4 transition blocks are looked up from a table
C      of 256 precomputed blocks (a block depends on only 8 bits:
C      4 bits of A and the 4 matching bits of the remapped B),
C    * all elimination inner loops have constant trip count 16, so they
C      unroll/vectorise; the extra work on already-eliminated columns
C      is never read back.
C  Call payf2ini once before first use.
C=====================================================================

      subroutine payf2ini
      implicit none
      double precision pmin,pmax
      common /epsval/ pmin,pmax
      double precision mb(4,4,0:255)
      integer ipl(0:255),iph(0:255)
      common /pfblk/ mb,ipl,iph

      double precision pv(0:1),pk,qk
      integer ip,iq,ipat,b,i,k,j,ib,map(16)
      data map /1,3,2,4, 9,11,10,12, 5,7,6,8, 13,15,14,16/

      pv(0)=pmin
      pv(1)=pmax

C---- mb(b+1,x+1,ipat) = prob( outcome x | state (a,b) ), a implicit:
C     ipat holds A's 4 bits (low) and remapped-B's 4 bits (high) for
C     the four states b=0..3 of the group.
      do ipat=0,255
         do b=0,3
            ip=iand(ishft(ipat,-b),1)
            iq=iand(ishft(ipat,-(b+4)),1)
            pk=pv(ip)
            qk=pv(iq)
            mb(b+1,1,ipat)=pk*qk
            mb(b+1,2,ipat)=pk*(1.d0-qk)
            mb(b+1,3,ipat)=(1.d0-pk)*qk
            mb(b+1,4,ipat)=(1.d0-pk)*(1.d0-qk)
         enddo
      enddo

C---- bit permutation tables: isbt = own-order view of partner's code
      do i=0,255
         ipl(i)=0
         iph(i)=0
      enddo
      do k=1,16
         ib=map(k)-1
         do i=0,255
            if (ib.le.7) then
               if (btest(i,ib)) ipl(i)=ibset(ipl(i),k-1)
            else
               if (btest(i,ib-8)) iph(i)=ibset(iph(i),k-1)
            endif
         enddo
      enddo
      return
      end

C---------------------------------------------------------------------

      subroutine payf2(isa,isb,w0,w1,w2,w3)
      implicit none
      integer isa,isb
      double precision w0,w1,w2,w3

      double precision mb(4,4,0:255)
      integer ipl(0:255),iph(0:255)
      common /pfblk/ mb,ipl,iph

      double precision at(16,16),x(16)
      double precision t,amax,dinv,fac
      integer i,j,k,mm,ia,ix,ic,ir,ipat,isbt

      isbt = ipl(iand(isb,255)) + iph(ishft(isb,-8))

      do j=1,16
         do i=1,16
            at(i,j)=0.d0
         enddo
         x(j)=0.d0
      enddo
      x(16)=1.d0

C---- at(col,row) = A(row,col); group a fills 4 contiguous columns
      do ia=0,3
         ipat = iand(ishft(isa ,-4*ia),15)
     &     + 16*iand(ishft(isbt,-4*ia),15)
         ic = 4*ia
         do ix=0,3
            ir = ia+1+4*ix
            at(ic+1,ir)=mb(1,ix+1,ipat)
            at(ic+2,ir)=mb(2,ix+1,ipat)
            at(ic+3,ir)=mb(3,ix+1,ipat)
            at(ic+4,ir)=mb(4,ix+1,ipat)
         enddo
      enddo
      do k=1,15
         at(k,k)=at(k,k)-1.d0
      enddo
      do i=1,16
         at(i,16)=1.d0
      enddo

C---- forward elimination, partial pivoting; column k lives in at(k,*)
      do k=1,15
         mm   = k
         amax = dabs(at(k,k))
         do i=k+1,16
            t = dabs(at(k,i))
            if (t.gt.amax) then
               amax = t
               mm   = i
            endif
         enddo
         if (mm.ne.k) then
            do j=1,16
               t        = at(j,k)
               at(j,k)  = at(j,mm)
               at(j,mm) = t
            enddo
            t     = x(k)
            x(k)  = x(mm)
            x(mm) = t
         endif
         dinv = 1.d0/at(k,k)
         do i=k+1,16
            fac = at(k,i)*dinv
            x(i) = x(i) - fac*x(k)
            do j=1,16
               at(j,i) = at(j,i) - fac*at(j,k)
            enddo
         enddo
      enddo

      do i=16,1,-1
         t = x(i)
         do j=i+1,16
            t = t - at(j,i)*x(j)
         enddo
         x(i) = t/at(i,i)
      enddo

      w0 = x(1 )+x(2 )+x(3 )+x(4 )
      w1 = x(5 )+x(6 )+x(7 )+x(8 )
      w2 = x(9 )+x(10)+x(11)+x(12)
      w3 = x(13)+x(14)+x(15)+x(16)
      return
      end
