"""Read-only live direction observer and host shadow oracle generation.
The oracle shares earlier recovered formulas; native original fixtures qualify it.
It writes only its own128byte private-stack copy, never guest RAM.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def model_source():
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    body=(nd/'actor-direction-reference-v2.c').read_text().replace('#include "actor-direction-native.h"','').replace('void biwn_native_actor_direction_body(uint32_t *r)','static void ad_shadow_body(uint32_t *r)')
    pre=r'''
#include <stdint.h>
#include <string.h>
static const unsigned char *ad_model_ram;
static unsigned char ad_model_stack[160];
static uint32_t ad_model_low;
static unsigned ad_model_error;
static uint32_t ad_read(uint32_t address,unsigned width){
 const unsigned char *p;
 if(address>=ad_model_low&&address+width<=ad_model_low+160u)p=ad_model_stack+address-ad_model_low;
 else if(address<=0x200000u-width)p=ad_model_ram+address;
 else{ad_model_error++;return 0;}
 uint32_t value=0;for(unsigned i=0;i<width;i++)value=(value<<8)|p[i];return value;
}
static void ad_write(uint32_t address,uint32_t value){
 if(address<ad_model_low||address>ad_model_low+156u){ad_model_error++;return;}
 for(unsigned i=0;i<4;i++)ad_model_stack[address-ad_model_low+i]=(unsigned char)(value>>(24u-8u*i));
}
#define ADR16(a) ((uint16_t)ad_read((a),2))
#define ADR32(a) ad_read((a),4)
#define ADW32(a,v) ad_write((a),(v))
static void biwn_native_actor_direction_division_capture(uint32_t *r){
 uint32_t a=ADR32(r[15]),b=ADR32(r[15]+4u),d2=r[2],d3=r[3];
 if(!b){ad_model_error++;return;}
 uint32_t aa=a&0x80000000u?0u-a:a,bb=b&0x80000000u?0u-b:b;
 uint32_t q=aa/bb,rem=aa%bb;unsigned x=(r[16]&16u)!=0;
 if((a^b)&0x80000000u)q=0u-q;
 if(a&0x80000000u)rem=0u-rem;
 if(b&0x80000000u)x=1;
 if(a&0x80000000u)x=1;
 if(aa>=bb&&(b>>16))x=0;
 if(a&0x80000000u)x=rem!=0;
 if((a^b)&0x80000000u)x=q!=0;
 r[0]=q;r[1]=rem;r[8]=d2;r[9]=d3;
 r[16]=(r[16]&0xffe0u)|(x?16u:0u)|(d2?0u:4u)|(d2&0x80000000u?8u:0u);
}
'''
    post=r'''
int biwn_direction_predict(const unsigned char *memory,const uint32_t *input,uint16_t sr,uint32_t *output,uint16_t *out_sr){
 uint32_t r[19]={0};memcpy(r,input,64);r[16]=sr;r[17]=0x13440u;
 if(r[15]<128u||r[15]>0x200000u-32u)return 1;
 ad_model_ram=memory;ad_model_low=r[15]-128u;ad_model_error=0;
 memcpy(ad_model_stack,memory+ad_model_low,160);ad_shadow_body(r);
 memcpy(output,r,64);*out_sr=(uint16_t)r[16];return ad_model_error!=0;
}
'''
    return pre+body+post

def render(build):
    path=ROOT/'scripts/native_actor_direction_observer.inc.c'
    source=path.read_text();symbols=build['direction_symbols']
    replacements={'__DIR_START__':build['direction_start'],'__DIR_END__':build['direction_end'],'__DIR_COMPILED__':symbols['biwn_native_actor_direction'],'__DIR_RETURN__':symbols['biwn_native_actor_direction_return'],'__DIR_BODY__':symbols['biwn_native_actor_direction_body']}
    for key,value in replacements.items():assert key in source;source=source.replace(key,str(value)+'u')
    return source,path
