// Exact eps->0 limit of the stationary distribution of two binary memory-two strategies
// with independent implementation errors, via GTH state reduction in leading-order
// (coefficient, exponent) arithmetic. All operations are on positive quantities, so the
// leading term of every intermediate is exact; no threshold, no extrapolation.
// Strategy convention (NE.pdf): state j = 4*recent + before, outcomes CC=0,CD=1,DC=2,DD=3
// (own action first); bit j of the 16-bit integer is 1 for C.  ALLC = 65535, ALLD = 0.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NS 16
#define EINF 1000000000
static inline int bitC(unsigned s,int j){return (s>>j)&1;}
static inline int swapo(int o){return ((o&1)<<1)|(o>>1);}
static void build(unsigned sig,unsigned tau,double c[NS][NS],int e[NS][NS]){
  for(int i=0;i<NS;i++)for(int j=0;j<NS;j++){c[i][j]=0;e[i][j]=EINF;}
  for(int j=0;j<NS;j++){
    int o1=j>>2,o0=j&3; int jt=4*swapo(o1)+swapo(o0);
    int dS=1-bitC(sig,j), dT=1-bitC(tau,jt);
    for(int fs=0;fs<2;fs++)for(int ft=0;ft<2;ft++){
      int onew=2*(dS^fs)+(dT^ft); int nxt=4*onew+o1;
      c[j][nxt]=1.0; e[j][nxt]=fs+ft;
    }
  }
}
static void gth(double c[NS][NS],int e[NS][NS],double w[NS]){
  for(int k=NS-1;k>=1;k--){
    int es=EINF;double cs=0;
    for(int j=0;j<k;j++){int ej=e[k][j]; if(ej<es){es=ej;cs=c[k][j];} else if(ej==es&&es<EINF){cs+=c[k][j];}}
    for(int i=0;i<k;i++){ if(e[i][k]<EINF){c[i][k]/=cs;e[i][k]-=es;} }
    for(int i=0;i<k;i++){ if(e[i][k]>=EINF)continue; int eik=e[i][k]; double cik=c[i][k];
      for(int j=0;j<k;j++){ if(e[k][j]>=EINF)continue; int en=eik+e[k][j]; double cn=cik*c[k][j];
        if(en<e[i][j]){e[i][j]=en;c[i][j]=cn;} else if(en==e[i][j]){c[i][j]+=cn;} } }
  }
  double pc[NS];int pe[NS]; pc[0]=1;pe[0]=0;
  for(int k=1;k<NS;k++){int ek=EINF;double ck=0;
    for(int i=0;i<k;i++){ if(e[i][k]>=EINF||pe[i]>=EINF)continue; int en=pe[i]+e[i][k]; double cn=pc[i]*c[i][k];
      if(en<ek){ek=en;ck=cn;} else if(en==ek){ck+=cn;} }
    pc[k]=ck;pe[k]=ek;}
  int emin=EINF;double ct=0;
  for(int k=0;k<NS;k++){ if(pe[k]<emin){emin=pe[k];ct=pc[k];} else if(pe[k]==emin){ct+=pc[k];} }
  for(int k=0;k<NS;k++) w[k]=(pe[k]==emin)?pc[k]/ct:0.0;
}
// limit outcome frequencies from sigma's view: W[0]=CC,W[1]=CD,W[2]=DC,W[3]=DD
static void freqs(unsigned sig,unsigned tau,double W[4]){
  double c[NS][NS];int e[NS][NS];double w[NS];
  build(sig,tau,c,e); gth(c,e,w);
  W[0]=W[1]=W[2]=W[3]=0; for(int j=0;j<NS;j++) W[j>>2]+=w[j];
}
int main(int argc,char**argv){
  if(argc<4){fprintf(stderr,"usage: pairs self|rival|nash stripe nstripes [sign|u v] \n");return 1;}
  const char*mode=argv[1]; int stripe=atoi(argv[2]), nstr=atoi(argv[3]);
  double TOL=1e-9;
  if(!strcmp(mode,"self")){
    for(unsigned s=stripe;s<65536;s+=nstr){double W[4];freqs(s,s,W);
      printf("%u %.17g %.17g %.17g %.17g\n",s,W[0],W[1],W[2],W[3]);}
  } else if(!strcmp(mode,"rival")){
    int sign=atoi(argv[4]);   // +1: T>S reading (need wDC>=wCD vs all tau); -1: T<S reading (wCD>=wDC)
    double gapmin=1e9; long ntau_total=0;
    for(unsigned s=stripe;s<65536;s+=nstr){
      long beater=-1; long tried=0;
      for(long t0=0;t0<65536;t0++){ unsigned t=(unsigned)t0; double W[4]; freqs(s,t,W); tried++;
        double d=sign*(W[2]-W[1]);        // >=0 means sigma not outperformed
        double ad=d<0?-d:d; if(ad>0 && ad<gapmin) gapmin=ad;
        if(d<-TOL){beater=t;break;} }
      ntau_total+=tried;
      printf("%u %ld\n",s,beater);
    }
    fprintf(stderr,"stripe %d: gapmin(nonzero |wDC-wCD|)=%.3e, chains=%ld\n",stripe,gapmin,ntau_total);
  } else if(!strcmp(mode,"nash")){
    double u=atof(argv[4]), v=atof(argv[5]); double Emax=1.0; if((1+u+v)/2>Emax)Emax=(1+u+v)/2;
    for(unsigned s=stripe;s<65536;s+=nstr){
      double Ws[4];freqs(s,s,Ws); double self=Ws[0]+u*Ws[1]+(1+v)*Ws[2];
      double maxpay=-1e9; int tieviol=0; long ntie=0; long firstbeat=-1;
      for(long t0=0;t0<65536;t0++){unsigned t=(unsigned)t0; double W[4];freqs(s,t,W);
        double ptau=W[0]+(1+v)*W[1]+u*W[2];      // co-player's payoff against sigma
        double psig=W[0]+u*W[1]+(1+v)*W[2];      // sigma's payoff against tau
        if(ptau>maxpay)maxpay=ptau;
        if(ptau>=self-TOL && ptau<=self+TOL){ntie++; if(psig<self-TOL)tieviol=1;}
        if(ptau>self+TOL && firstbeat<0) firstbeat=t;
        if(maxpay>Emax+TOL) break; }
      printf("%u %.17g %.17g %d %ld %ld\n",s,self,maxpay,tieviol,ntie,firstbeat);
    }
  } else if(!strcmp(mode,"pair")){
    unsigned s=(unsigned)atol(argv[2]), t=(unsigned)atol(argv[3]); double W[4]; freqs(s,t,W);
    printf("%u %u %.17g %.17g %.17g %.17g\n",s,t,W[0],W[1],W[2],W[3]);
  } else if(!strcmp(mode,"gap")){
    // argv[2]=listfile of sigma ids, argv[3]=stripe, argv[4]=nstripes: full sweep, report smallest |wDC-wCD| above 1e-13 and count in (1e-13,1e-6)
    FILE*f=fopen(argv[2],"r"); int st=atoi(argv[3]), ns=atoi(argv[4]); long s; long idx=0; double gmin=1e9; long nsmall=0, ntot=0;
    while(fscanf(f,"%ld",&s)==1){ if((idx++)%ns!=st) continue;
      for(long t=0;t<65536;t++){ double W[4]; freqs((unsigned)s,(unsigned)t,W); double d=W[2]-W[1]; if(d<0)d=-d; ntot++;
        if(d>1e-13){ if(d<gmin)gmin=d; if(d<1e-6)nsmall++; } } }
    printf("stripe %d: chains=%ld smallest |wDC-wCD| above 1e-13 = %.6e ; count in (1e-13,1e-6) = %ld\n",st,ntot,gmin,nsmall);
  }
  return 0;
}
