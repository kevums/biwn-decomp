#include "frame-acquire-native.h"
/* Coordinator reconstruction. Complete original control flow, not a repaired
 * allocator: retain signed WORDs, strict group limits, zero DIVS and rereads. */
void biwn_frame_acquire_body(uint32_t *r)
{
    uint32_t division_site;
    fa_w(r,6,FA16(r[15]+4u));
    fa_w(r,0,FA16(0x15b530u));
    fa_cmp(r,r[0],3);if((int16_t)r[0]>3)goto failure;
    fa_cmp(r,r[0],1);if((int16_t)r[0]<1)goto failure;
    fa_l(r,0,fa_sx(r[0]));r[8]=0x464c8u;
    fa_l(r,1,r[0]);
    {uint32_t a=r[1],d=a+a;r[1]=d;r[16]=(r[16]&~31u)|(d<a?17u:0u)|(((~(a^a))&(a^d)&0x80000000u)?2u:0u)|(d==0?4u:0u)|((d&0x80000000u)?8u:0u);}
    fa_w(r,4,r[6]);fa_sw(r,4,FA16(r[8]+r[1]));
    r[8]=0x464a0u;fa_w(r,3,FA16(r[8]+r[1]));
    r[8]=0x464a8u;fa_asl(r,0,32,2);r[10]=FA32(r[8]+r[0]);
    r[8]=0x464b8u;r[12]=FA32(r[8]+r[0]);
    fa_nz(r,r[4],16);if((int16_t)r[4]<0)goto failure;
    fa_w(r,2,FA16(0x15b532u));fa_l(r,0,36);fa_sw(r,0,r[3]);fa_cmp(r,r[0],r[2]);
    if((int16_t)r[0]>(int16_t)r[2]) {
        r[8]=0x15b4a0u;fa_w(r,1,r[0]);
        do {
            fa_w(r,0,r[2]);fa_l(r,0,fa_sx(r[0]));fa_asl(r,0,32,2);
            fa_cmp(r,r[6],FA16(r[8]+r[0]));
            if(r[16]&4u) {
                fa_w(r,1,0);fa_cmp(r,r[3],r[1]);
                if((int16_t)r[3]>(int16_t)r[1])do {
                    fa_w(r,0,r[2]);fa_aw(r,0,r[1]);fa_l(r,0,fa_sx(r[0]));fa_asl(r,0,32,2);
                    {uint32_t address=r[8]+r[0]+2u;uint16_t v=fa_arithw(r,FA16(address),1,0,0);FA16(address)=v;}
                    fa_aw(r,1,1);fa_cmp(r,r[3],r[1]);
                }while((int16_t)r[3]>(int16_t)r[1]);
                goto result;
            }
            fa_aw(r,2,r[3]);fa_cmp(r,r[1],r[2]);
        }while((int16_t)r[1]>(int16_t)r[2]);
    }
    fa_w(r,0,r[4]);fa_l(r,0,fa_sx(r[0]));r[18]=0x1ad0cu;
    biwn_frame_acquire_divs_capture(r);
    r[12]+=fa_sx(r[0]);
    fa_w(r,2,FA16(0x15b532u));fa_l(r,0,36);fa_sw(r,0,r[3]);fa_cmp(r,r[0],r[2]);
    if((int16_t)r[0]>(int16_t)r[2]) {
        r[11]=0x15b4a0u;
        fa_w(r,0,r[4]);fa_l(r,0,fa_sx(r[0]));fa_l(r,7,13);fa_asl(r,0,32,13);r[8]=r[0];
        fa_w(r,0,r[3]);fa_l(r,0,fa_sx(r[0]));fa_l(r,5,r[0]);fa_asl(r,5,32,13);
        do {
            fa_w(r,1,r[2]);fa_l(r,1,fa_sx(r[1]));fa_l(r,0,r[1]);fa_asl(r,0,32,2);
            fa_cmp(r,FA16(r[11]+r[0]),0xffffu);
            if(r[16]&4u){division_site=0x1ad4eu;goto load_group;}
            fa_aw(r,2,r[3]);fa_l(r,0,36);fa_sw(r,0,r[3]);fa_cmp(r,r[0],r[2]);
        }while((int16_t)r[0]>(int16_t)r[2]);
    }
    fa_w(r,2,FA16(0x15b532u));fa_l(r,0,36);fa_sw(r,0,r[3]);fa_cmp(r,r[0],r[2]);
    if((int16_t)r[0]<=(int16_t)r[2])goto failure;
    r[11]=0x15b4a0u;
    fa_w(r,0,r[4]);fa_l(r,0,fa_sx(r[0]));fa_l(r,7,13);fa_asl(r,0,32,13);r[8]=r[0];
    fa_w(r,0,r[3]);fa_l(r,0,fa_sx(r[0]));fa_l(r,5,r[0]);fa_asl(r,5,32,13);
    do {
        fa_w(r,1,r[2]);fa_l(r,1,fa_sx(r[1]));fa_l(r,0,r[1]);fa_asl(r,0,32,2);
        fa_nz(r,FA16(r[11]+r[0]+2u),16);
        if(r[16]&4u){division_site=0x1adeau;goto load_group;}
        fa_aw(r,2,r[3]);fa_l(r,0,36);fa_sw(r,0,r[3]);fa_cmp(r,r[0],r[2]);
    }while((int16_t)r[0]>(int16_t)r[2]);
failure:
    fa_l(r,0,0xffffffffu);return;
load_group:
    fa_w(r,0,r[4]);fa_l(r,0,fa_sx(r[0]));r[18]=division_site;
    biwn_frame_acquire_divs_capture(r);
    fa_asl(r,0,16,6);r[9]=r[8]+fa_sx(r[0]);
    fa_l(r,0,r[1]);fa_asl(r,0,32,3);r[8]=0x4674cu;
    {uint32_t value=FA32(r[8]+r[0]);FA32(r[14]-4u)=value;fa_nz(r,value,32);}
    biwn_frame_acquire_load_capture(r);
    fa_w(r,1,0);fa_cmp(r,r[3],r[1]);
    if((int16_t)r[3]>(int16_t)r[1])do {
        fa_w(r,0,r[2]);fa_aw(r,0,r[1]);fa_l(r,0,fa_sx(r[0]));fa_asl(r,0,32,2);
        fa_w(r,7,r[6]);fa_aw(r,7,r[1]);
        FA16(r[11]+r[0])=(uint16_t)r[7];fa_nz(r,r[7],16);
        FA16(r[11]+r[0]+2u)=1;fa_nz(r,1,16);
        fa_aw(r,1,1);fa_cmp(r,r[3],r[1]);
    }while((int16_t)r[3]>(int16_t)r[1]);
result:
    fa_w(r,0,r[2]);
}
