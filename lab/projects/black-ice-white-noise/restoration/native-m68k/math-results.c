/* Native ABI adaptation of the already recovered arithmetic and flag formulas.
 * Coordinator-authored glue; no CPU decoder or original game calls. */
#include <stdint.h>
#include <stddef.h>
#include "../biwn_camera.h"
#include "../biwn_signed_division.h"
struct __attribute__((packed,aligned(2))) math_result {
 uint32_t d0,d1;uint16_t sr;uint32_t original_d2,original_d3;
};
typedef char check_d2_offset[offsetof(struct math_result,original_d2)==10?1:-1];
typedef char check_result_size[sizeof(struct math_result)==18?1:-1];
static uint16_t nz32(uint32_t v){return (uint16_t)((v?0:4)|(v&0x80000000u?8:0));}
void biwn_native_multiply_result(uint32_t a,uint32_t b,uint32_t incoming_sr,struct math_result *out)
{
 uint32_t aa=a&0x80000000u?0u-a:a,bb=b&0x80000000u?0u-b:b;
 uint32_t cross=biwn_multiply32(aa>>16,bb&0xffffu)+biwn_multiply32(bb>>16,aa&0xffffu);
 uint32_t partial=(cross&0xffffu)<<16,low=biwn_multiply32(aa&0xffffu,bb&0xffffu),absolute=partial+low;
 uint16_t sign=(uint16_t)(a>>16),flags;
 if(b&0x80000000u)sign=(uint16_t)~sign;
 out->d0=biwn_multiply32(a,b);out->d1=low;
 flags=(uint16_t)((absolute<partial?16:0)|(sign?0:4)|(sign&0x8000u?8:0));
 if(sign&0x8000u)flags=(uint16_t)(nz32(out->d0)|(absolute?17:0)|(absolute==0x80000000u?2:0));
 out->sr=(uint16_t)((incoming_sr&0xffe0u)|flags);
}
void biwn_native_division_result(uint32_t a,uint32_t b,uint32_t incoming_sr,struct math_result *out)
{
 uint32_t q=0,r=0,aa=a&0x80000000u?0u-a:a,bb=b&0x80000000u?0u-b:b;
 unsigned x=(incoming_sr&16u)!=0;
 /* Zero takes the native processor-exception entry before this C function. */
 if(biwn_signed_division(a,b,&q,&r))__builtin_trap();
 if(b&0x80000000u)x=1;
 if(a&0x80000000u)x=1;
 if(aa>=bb&&(b>>16))x=0;
 if(a&0x80000000u)x=r!=0;
 if((a^b)&0x80000000u)x=q!=0;
 out->d0=q;out->d1=r;
 out->sr=(uint16_t)((incoming_sr&0xffe0u)|(x?16:0)|nz32(out->original_d2));
}
void biwn_native_remainder_result(uint32_t a,uint32_t b,uint32_t sr,struct math_result *out)
{
 biwn_native_division_result(a,b,sr,out);out->d0=out->d1;
 out->sr=(uint16_t)((out->sr&0xfff0u)|nz32(out->d0));
}
