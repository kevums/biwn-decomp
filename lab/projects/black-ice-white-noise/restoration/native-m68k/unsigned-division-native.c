/* Coordinator C recovery from original E61C..E68C instructions.
 * Numerical unsigned long division with original CCR and public stack ABI.
 * No original arithmetic entry, CPU interpreter or division runtime. */
#include "unsigned-division-native.h"
static uint32_t nz32(uint32_t v){return(v?0u:4u)|(v&0x80000000u?8u:0u);}
int biwn_native_unsigned_divide_body(uint32_t *r)
{
 uint32_t sp=r[15],d2=r[2],d3=r[3],sr=r[16],den,num,q=0,rem=0;
 r[8]=d2;r[9]=d3;r[0]=0;
 den=UR32(sp+8);r[2]=den;
 if(!den){r[16]=(sr&0xfff0u)|4u;return 1;}
 num=UR32(sp+4);
 if(num<den)rem=num;
 else {
  uint16_t high=UR16(sp+8);unsigned i;
  for(i=0;i<32;i++){
   rem=(rem<<1)|(num>>31);num<<=1;q<<=1;
   if(rem>=den){rem-=den;q|=1;}
  }
  /* Original32-step path clearsX; short DIVU path preservesX. */
  if(high)sr&=~16u;
 }
 r[0]=q;r[1]=rem;r[2]=d2;r[3]=d3;
 r[16]=(sr&0xfff0u)|nz32(d2);return 0;
}
int biwn_native_unsigned_remainder_body(uint32_t *r)
{
 uint32_t sp=r[15],den,num;int fault;
 den=UR32(sp+8);UW32(sp-4,den);
 num=UR32(sp+4);UW32(sp-8,num);
 UW32(sp-12,0xe686u);r[15]=sp-12;
 fault=biwn_native_unsigned_divide_body(r);r[15]=sp;
 if(fault)return 1;
 (void)UR32(sp-12); /* Original helper RTS consumes saved E686. */
 r[0]=r[1];r[16]=(r[16]&0xfff0u)|nz32(r[0]);return 0;
}
