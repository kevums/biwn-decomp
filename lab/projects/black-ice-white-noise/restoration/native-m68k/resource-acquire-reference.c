/* Coordinator source/reference; includes semantic helper-visible callee registers.
 * This is not output from any of the rejected local Author attempts.
 */
#include "resource-acquire-native.h"
static void low16(uint32_t *r,uint32_t reg,uint16_t value) {
    r[reg]=(r[reg]&0xffff0000u)|value;
}
void biwn_native_resource_acquire_body(uint32_t *r) {
    uint16_t id=AR16(r[15]+4u);
    uint32_t descriptor_offset=(uint32_t)((int32_t)(int16_t)id*12);
    uint32_t descriptor=0x464d0u+descriptor_offset;
    low16(r,5,id);r[8]=0x464d0u;r[0]=descriptor_offset;
    if(AR32(descriptor)==0u) {
        r[0]=0u;acquire_nz32(r,0u);return;
    }
    low16(r,3,0u);r[10]=0x15b534u;
    for(uint32_t i=0;i<50u;i++) {
        uint32_t offset=i*12u,entry=0x15b534u+offset;
        r[0]=offset;
        if(AR16(entry)==id && AR16(entry+6u)!=0u) {
            uint16_t refs=AR16(entry+6u);
            AW16(entry+6u,acquire_add1w(r,refs));
            uint16_t ready=AR16(entry+8u);
            if(ready==0u) {
                r[2]=offset;r[11]=0x15b534u;acquire_nz32(r,offset);
                do {
                    biwn_native_acquire_wait_capture(r);
                    ready=AR16(entry+8u);acquire_nz16(r,ready);
                } while(ready==0u);
            }
            r[0]=AR32(entry+2u);acquire_nz32(r,r[0]);return;
        }
        low16(r,3,(uint16_t)(i+1u));r[16]&=~16u;
    }
    low16(r,3,0u);r[10]=0x15b534u;r[4]=descriptor_offset;r[11]=0x464d0u;
    for(uint32_t i=0;i<50u;i++) {
        uint32_t entry=0x15b534u+i*12u;
        r[2]=i*12u;
        if(AR16(entry+6u)==0u) {
            acquire_nz16(r,0u);
            biwn_native_acquire_allocate_capture(r,descriptor);
            AW32(entry+2u,r[0]);
            if(r[0]==0u) {acquire_nz32(r,0u);return;}
            AW16(entry+8u,0u);AW16(entry,id);AW16(entry+6u,1u);
            biwn_native_acquire_load_capture(r,descriptor,entry);
            uint16_t refs=AR16(entry+6u);acquire_cmp1w(r,refs);
            if(refs!=1u)biwn_native_acquire_signal_capture(r);
            r[0]=AR32(entry+2u);acquire_nz32(r,r[0]);return;
        }
        low16(r,3,(uint16_t)(i+1u));r[16]&=~16u;
    }
    r[0]=0u;acquire_nz32(r,0u);
}
