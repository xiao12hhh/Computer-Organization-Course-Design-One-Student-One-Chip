// RV32I integer instructions and the M extension. No privileged ISA/CSRs.
#include "rv32.h"
#include <stdbool.h>
#include <limits.h>
static uint32_t sx(uint32_t x,unsigned width){uint32_t sign=1u<<(width-1);return (x^sign)-sign;}
static uint32_t sar(uint32_t x,unsigned n){return !n?x:(x>>n)|((x&0x80000000u)?(~0u<<(32-n)):0);}
int rv32_execute(uint32_t i,uint32_t pc,uint32_t r[32],uint32_t *next,rv_read read,rv_write write){
  unsigned op=i&127,rd=(i>>7)&31,f=(i>>12)&7,rs1=(i>>15)&31,rs2=(i>>20)&31,hi=i>>25;
  uint32_t a=r[rs1],b=r[rs2],imm=sx(i>>20,12),value=0,target=pc+4;
  bool wr=true;
  switch(op){
    case 0x37:value=i&0xfffff000u;break;
    case 0x17:value=pc+(i&0xfffff000u);break;
    case 0x6f:
      target=pc+sx(((i>>31)<<20)|(((i>>12)&255)<<12)|(((i>>20)&1)<<11)|(((i>>21)&1023)<<1),21);
      if(target&3)return RV_ILLEGAL;
      value=pc+4;break;
    case 0x67:
      if(f)return RV_ILLEGAL;
      target=(a+imm)&~1u;if(target&3)return RV_ILLEGAL;value=pc+4;break;
    case 0x63:{
      bool taken;
      switch(f){case 0:taken=a==b;break;case 1:taken=a!=b;break;
        case 4:taken=(int32_t)a<(int32_t)b;break;case 5:taken=(int32_t)a>=(int32_t)b;break;
        case 6:taken=a<b;break;case 7:taken=a>=b;break;default:return RV_ILLEGAL;}
      if(taken)target=pc+sx(((i>>31)<<12)|(((i>>7)&1)<<11)|(((i>>25)&63)<<5)|(((i>>8)&15)<<1),13);
      if(target&3)return RV_ILLEGAL;
      wr=false;break;
    }
    case 3:
      switch(f){case 0:value=sx(read(a+imm,1),8);break;case 1:value=sx(read(a+imm,2),16);break;
        case 2:value=read(a+imm,4);break;case 4:value=read(a+imm,1);break;case 5:value=read(a+imm,2);break;
        default:return RV_ILLEGAL;}break;
    case 0x23:
      imm=sx(((i>>25)<<5)|rd,12);
      if(f>2)return RV_ILLEGAL;
      write(a+imm,1<<f,b);wr=false;break;
    case 0x13:
      switch(f){case 0:value=a+imm;break;case 2:value=(int32_t)a<(int32_t)imm;break;
        case 3:value=a<imm;break;case 4:value=a^imm;break;case 6:value=a|imm;break;case 7:value=a&imm;break;
        case 1:if(hi)return RV_ILLEGAL;value=a<<rs2;break;
        case 5:if(hi!=0 && hi!=32)return RV_ILLEGAL;value=hi?sar(a,rs2):a>>rs2;break;
      }break;
    case 0x33:
      if(hi==1){
        int32_t sa=(int32_t)a,sb=(int32_t)b;
        switch(f){
          case 0:value=(uint32_t)((uint64_t)a*b);break;
          case 1:value=(uint32_t)((uint64_t)((int64_t)sa*sb)>>32);break;
          case 2:value=(uint32_t)((uint64_t)((int64_t)sa*(int64_t)(uint64_t)b)>>32);break;
          case 3:value=(uint32_t)(((uint64_t)a*b)>>32);break;
          case 4:value=!b?UINT32_MAX:(sa==INT32_MIN && sb==-1)?a:(uint32_t)(sa/sb);break;
          case 5:value=b?a/b:UINT32_MAX;break;
          case 6:value=!b?a:(sa==INT32_MIN && sb==-1)?0:(uint32_t)(sa%sb);break;
          case 7:value=b?a%b:a;break;
        }
      } else {
        if(hi!=0 && !(hi==32 && (f==0||f==5)))return RV_ILLEGAL;
        switch(f){case 0:value=hi?a-b:a+b;break;case 1:value=a<<(b&31);break;
          case 2:value=(int32_t)a<(int32_t)b;break;case 3:value=a<b;break;case 4:value=a^b;break;
          case 5:value=hi?sar(a,b&31):a>>(b&31);break;case 6:value=a|b;break;case 7:value=a&b;break;}
      }break;
    case 0x0f: // FENCE is a no-op in this sequential, single-hart interpreter.
      if(f!=0)return RV_ILLEGAL;
      wr=false;break;
    case 0x73:if(i==0x00100073){*next=target;r[0]=0;return RV_BREAK;}return RV_ILLEGAL;
    default:return RV_ILLEGAL;
  }
  if(wr && rd)r[rd]=value;
  r[0]=0;*next=target;return RV_OK;
}
