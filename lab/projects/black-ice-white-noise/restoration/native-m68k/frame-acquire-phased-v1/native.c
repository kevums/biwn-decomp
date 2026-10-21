#include "../frame-acquire-lean.h"
/* The original algorithm is split only at DIVS and the loader call.
 * All persistent state crosses a boundary in actual guest CPU registers.
 * No compiler frame survives either helper, a yield, or a nested acquire. */
enum { DONE=0, DIV_FIRST=1, DIV_EMPTY=2, DIV_EVICT=3, LOAD=4 };
static inline uint32_t result(uint32_t *r) {
    fl_w(r,0,r[2]);fl_nz(r,r[0],16);return DONE;
}
static inline uint32_t failure(uint32_t *r) {
    fl_l(r,0,0xffffffffu);fl_nz(r,r[0],32);return DONE;
}
uint32_t biwn_frame_phased_start(uint32_t *r) {
    fl_w(r,6,FA16(r[15]+4u));
    fl_w(r,0,FA16(0x15b530u));
    if((int16_t)r[0]>3)return failure(r);
    if((int16_t)r[0]<1)return failure(r);
    fl_l(r,0,fl_sx(r[0]));r[8]=0x464c8u;
    fl_l(r,1,r[0]);r[1]+=r[1];r[16]&=~16u;
    fl_w(r,4,r[6]);fl_sw(r,4,FA16(r[8]+r[1]));
    r[8]=0x464a0u;fl_w(r,3,FA16(r[8]+r[1]));
    r[8]=0x464a8u;fl_asl(r,0,32,2);r[10]=FA32(r[8]+r[0]);
    r[8]=0x464b8u;r[12]=FA32(r[8]+r[0]);
    if((int16_t)r[4]<0)return failure(r);
    fl_w(r,2,FA16(0x15b532u));fl_l(r,0,36);fl_sw(r,0,r[3]);
    if((int16_t)r[0]>(int16_t)r[2]) {
        r[8]=0x15b4a0u;fl_w(r,1,r[0]);
        do {
            fl_w(r,0,r[2]);fl_l(r,0,fl_sx(r[0]));fl_asl(r,0,32,2);
            if((uint16_t)r[6]==FA16(r[8]+r[0])) {
                fl_w(r,1,0);
                if((int16_t)r[3]>(int16_t)r[1])do {
                    fl_w(r,0,r[2]);fl_aw(r,0,r[1]);fl_l(r,0,fl_sx(r[0]));fl_asl(r,0,32,2);
                    uint32_t address=r[8]+r[0]+2u;uint16_t v=fl_arithw(r,FA16(address),1,0,0);FA16(address)=v;
                    fl_aw(r,1,1);
                }while((int16_t)r[3]>(int16_t)r[1]);
                return result(r);
            }
            fl_aw(r,2,r[3]);
        }while((int16_t)r[1]>(int16_t)r[2]);
    }
    fl_w(r,0,r[4]);fl_l(r,0,fl_sx(r[0]));r[18]=0x1ad0cu;
    fl_nz(r,r[0],32);return DIV_FIRST;
}
uint32_t biwn_frame_phased_after_first_divs(uint32_t *r) {
    uint32_t action;
    r[12]+=fl_sx(r[0]);
    fl_w(r,2,FA16(0x15b532u));fl_l(r,0,36);fl_sw(r,0,r[3]);
    if((int16_t)r[0]>(int16_t)r[2]) {
        r[11]=0x15b4a0u;
        fl_w(r,0,r[4]);fl_l(r,0,fl_sx(r[0]));fl_l(r,7,13);fl_asl(r,0,32,13);r[8]=r[0];
        fl_w(r,0,r[3]);fl_l(r,0,fl_sx(r[0]));fl_l(r,5,r[0]);fl_asl(r,5,32,13);
        do {
            fl_w(r,1,r[2]);fl_l(r,1,fl_sx(r[1]));fl_l(r,0,r[1]);fl_asl(r,0,32,2);
            if(FA16(r[11]+r[0])==0xffffu){action=DIV_EMPTY;goto load_group;}
            fl_aw(r,2,r[3]);fl_l(r,0,36);fl_sw(r,0,r[3]);
        }while((int16_t)r[0]>(int16_t)r[2]);
    }
    fl_w(r,2,FA16(0x15b532u));fl_l(r,0,36);fl_sw(r,0,r[3]);
    if((int16_t)r[0]<=(int16_t)r[2])return failure(r);
    r[11]=0x15b4a0u;
    fl_w(r,0,r[4]);fl_l(r,0,fl_sx(r[0]));fl_l(r,7,13);fl_asl(r,0,32,13);r[8]=r[0];
    fl_w(r,0,r[3]);fl_l(r,0,fl_sx(r[0]));fl_l(r,5,r[0]);fl_asl(r,5,32,13);
    do {
        fl_w(r,1,r[2]);fl_l(r,1,fl_sx(r[1]));fl_l(r,0,r[1]);fl_asl(r,0,32,2);
        if(FA16(r[11]+r[0]+2u)==0u){action=DIV_EVICT;goto load_group;}
        fl_aw(r,2,r[3]);fl_l(r,0,36);fl_sw(r,0,r[3]);
    }while((int16_t)r[0]>(int16_t)r[2]);
    return failure(r);
load_group:
    fl_w(r,0,r[4]);fl_l(r,0,fl_sx(r[0]));r[18]=action==DIV_EMPTY?0x1ad4eu:0x1adeau;
    fl_nz(r,r[0],32);return action;
}
uint32_t biwn_frame_phased_after_group_divs(uint32_t *r) {
    fl_asl(r,0,16,6);r[9]=r[8]+fl_sx(r[0]);
    fl_l(r,0,r[1]);fl_asl(r,0,32,3);r[8]=0x4674cu;
    FA32(r[14]-4u)=FA32(r[8]+r[0]);
    return LOAD;
}
uint32_t biwn_frame_phased_after_load(uint32_t *r) {
    fl_w(r,1,0);
    if((int16_t)r[3]>(int16_t)r[1])do {
        fl_w(r,0,r[2]);fl_aw(r,0,r[1]);fl_l(r,0,fl_sx(r[0]));fl_asl(r,0,32,2);
        fl_w(r,7,r[6]);fl_aw(r,7,r[1]);
        FA16(r[11]+r[0])=(uint16_t)r[7];FA16(r[11]+r[0]+2u)=1;
        fl_aw(r,1,1);
    }while((int16_t)r[3]>(int16_t)r[1]);
    return result(r);
}
