#include "biwn_signed_division.h"
enum biwn_signed_division_status biwn_signed_division(uint32_t numerator,
 uint32_t denominator,uint32_t *quotient,uint32_t *remainder)
{
 uint32_t n,d,q,r;
 if(!quotient||!remainder||quotient==remainder)return BIWN_SIGNED_DIVISION_BAD_ARGUMENT;
 if(!denominator)return BIWN_SIGNED_DIVISION_ZERO;
 n=numerator&0x80000000u?0u-numerator:numerator;
 d=denominator&0x80000000u?0u-denominator:denominator;
 q=n/d;r=n%d;
 if((numerator^denominator)&0x80000000u)q=0u-q;
 if(numerator&0x80000000u)r=0u-r;
 *quotient=q;*remainder=r;return BIWN_SIGNED_DIVISION_OK;
}
