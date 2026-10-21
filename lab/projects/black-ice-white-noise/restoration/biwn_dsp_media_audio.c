/* Source-specific static reconstruction by generate_biwn_dsp_media_audio.py.
 * Not recovered original source. See original-DSP comparison evidence. */
#include "biwn_dsp_media_audio.h"
static void zn(struct biwn_dsp_media_audio_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_dsp_media_audio_state *s,unsigned code){unsigned f=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(f&1u))&&!((code&2u)&&!(f&1u))&&!((code&4u)&&(f&(2u<<(code>>4))))&&!((code&8u)&&!(f&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf1b000u&&a<=0xf1cfffu;}
static int rd32(struct biwn_dsp_media_audio_bus *b,struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t *v){a&=~3u;if(local(a)){*v=be32(s->local_RAM+a-0xf1b000u);return 0;}if(a==0xf1a100u){s->flags=(s->flags&~7u)|s->z|(s->c<<1)|(s->n<<2);*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf1a114u){*v=s->control;return 0;}return b->read32(b->context,a,v)?2:0;}
static int rd8(struct biwn_dsp_media_audio_bus *b,struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t *v){uint8_t x;if(local(a))return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
static int wr32(struct biwn_dsp_media_audio_bus *b,struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t v){a&=~3u;if(local(a)){put32(s->local_RAM+a-0xf1b000u,v);return 0;}if(a==0xf1a100u){if(v&0x4000u)return 1;s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1;s->c=(s->flags>>1)&1;s->n=(s->flags>>2)&1;s->control&=~((s->flags&0x3e00u)>>3);s->control&=~((s->flags&0x20000u)>>1);return 0;}if(a==0xf1a114u){uint32_t mask=0x1f7c0u;s->control=(s->control&mask)|(v&~mask);return 0;}return b->write32(b->context,a,v)?2:0;}
static int valid(struct biwn_dsp_media_audio_state *s){return s&&s->z<=1&&s->c<=1&&s->n<=1&&!(s->flags&0x4000u);}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_dsp_media_audio_status)status;}while(0)
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_step(struct biwn_dsp_media_audio_bus *bus,struct biwn_dsp_media_audio_state *state){struct biwn_dsp_media_audio_state s;uint32_t v,target=0;unsigned pending=0,delayed=0;if(!bus||!valid(state)||!bus->read8||!bus->read32||!bus->write32)return 1;if(!(state->control&1u))return 6;s=*state;
 do{pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf1b010u: /* movei   $f1b10e,r29 */
   s.registers[0][29]=0xf1b10eu;
   s.pc=0xf1b016u;break;
  case 0xf1b016u: /* jump    (r29) */
   if(condition(&s,0)){pending=1;target=s.registers[0][29];}
   s.pc=0xf1b018u;break;
  case 0xf1b018u: /* nop */
   s.pc=0xf1b01au;break;
  case 0xf1b01au: /* nop */
   s.pc=0xf1b01cu;break;
  case 0xf1b01cu: /* movei   $f1b144,r0 */
   s.registers[0][0]=0xf1b144u;
   s.pc=0xf1b022u;break;
  case 0xf1b022u: /* load    (r0),r23 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][23]=v;
   s.pc=0xf1b024u;break;
  case 0xf1b024u: /* movei   $f1a148,r10 */
   s.registers[0][10]=0xf1a148u;
   s.pc=0xf1b02au;break;
  case 0xf1b02au: /* movei   $f1a14c,r11 */
   s.registers[0][11]=0xf1a14cu;
   s.pc=0xf1b030u;break;
  case 0xf1b030u: /* movei   $f1b126,r16 */
   s.registers[0][16]=0xf1b126u;
   s.pc=0xf1b036u;break;
  case 0xf1b036u: /* movei   $f1b074,r17 */
   s.registers[0][17]=0xf1b074u;
   s.pc=0xf1b03cu;break;
  case 0xf1b03cu: /* movei   $f1b138,r20 */
   s.registers[0][20]=0xf1b138u;
   s.pc=0xf1b042u;break;
  case 0xf1b042u: /* movei   $80000000,r24 */
   s.registers[0][24]=0x80000000u;
   s.pc=0xf1b048u;break;
  case 0xf1b048u: /* movei   $f1b0d4,r25 */
   s.registers[0][25]=0xf1b0d4u;
   s.pc=0xf1b04eu;break;
  case 0xf1b04eu: /* movei   $f1b140,r26 */
   s.registers[0][26]=0xf1b140u;
   s.pc=0xf1b054u;break;
  case 0xf1b054u: /* movei   $f1b190,r31 */
   s.registers[0][31]=0xf1b190u;
   s.pc=0xf1b05au;break;
  case 0xf1b05au: /* movei   $f1b148,r13 */
   s.registers[0][13]=0xf1b148u;
   s.pc=0xf1b060u;break;
  case 0xf1b060u: /* moveq   0,r14 */
   s.registers[0][14]=0u;
   s.pc=0xf1b062u;break;
  case 0xf1b062u: /* moveq   0,r15 */
   s.registers[0][15]=0u;
   s.pc=0xf1b064u;break;
  case 0xf1b064u: /* moveq   0,r27 */
   s.registers[0][27]=0u;
   s.pc=0xf1b066u;break;
  case 0xf1b066u: /* moveq   0,r7 */
   s.registers[0][7]=0u;
   s.pc=0xf1b068u;break;
  case 0xf1b068u: /* movei   $f1a100,r2 */
   s.registers[0][2]=0xf1a100u;
   s.pc=0xf1b06eu;break;
  case 0xf1b06eu: /* load    (r2),r0 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf1b070u;break;
  case 0xf1b070u: /* bset    $5,r0 */
   s.registers[0][0]|=(1u<<5);
   zn(&s,s.registers[0][0]);
   s.pc=0xf1b072u;break;
  case 0xf1b072u: /* store   r0,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][0]));
   s.pc=0xf1b074u;break;
  case 0xf1b074u: /* or      r27,r27 */
   s.registers[0][27]|=s.registers[0][27];
   zn(&s,s.registers[0][27]);
   s.pc=0xf1b076u;break;
  case 0xf1b076u: /* jr      z,00F1B074 */
   if(condition(&s,2)){pending=1;target=0xf1b074u;}
   s.pc=0xf1b078u;break;
  case 0xf1b078u: /* nop */
   s.pc=0xf1b07au;break;
case 0xf1b07au: /* xor     r27,r27 */ s.registers[0][27]^=s.registers[0][27];zn(&s,s.registers[0][27]);s.pc=0xf1b07cu;break;
  case 0xf1b07cu: /* load    (r26),r0 */
   CHECK(rd32(bus,&s,s.registers[0][26]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf1b07eu;break;
  case 0xf1b07eu: /* or      r0,r0 */
   s.registers[0][0]|=s.registers[0][0];
   zn(&s,s.registers[0][0]);
   s.pc=0xf1b080u;break;
  case 0xf1b080u: /* jump    nz,(r16) */
   if(condition(&s,1)){pending=1;target=s.registers[0][16];}
   s.pc=0xf1b082u;break;
  case 0xf1b082u: /* nop */
   s.pc=0xf1b084u;break;
  case 0xf1b084u: /* load    (r20),r0 */
   CHECK(rd32(bus,&s,s.registers[0][20]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf1b086u;break;
  case 0xf1b086u: /* cmpq    $0,r0 */
   (void)sub(&s,s.registers[0][0],0x0u);
   s.pc=0xf1b088u;break;
  case 0xf1b088u: /* jr      z,00F1B0A6 */
   if(condition(&s,2)){pending=1;target=0xf1b0a6u;}
   s.pc=0xf1b08au;break;
  case 0xf1b08au: /* move    r13,r5 */
   s.registers[0][5]=s.registers[0][13];
   s.pc=0xf1b08cu;break;
  case 0xf1b08cu: /* shlq    $3,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<3;zn(&s,s.registers[0][14]);
   s.pc=0xf1b08eu;break;
  case 0xf1b08eu: /* add     r14,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][14]);
   s.pc=0xf1b090u;break;
  case 0xf1b090u: /* shrq    $3,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=s.registers[0][14]>>3;zn(&s,s.registers[0][14]);
   s.pc=0xf1b092u;break;
  case 0xf1b092u: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf1b094u;break;
  case 0xf1b094u: /* addq    $4,r20 */
   s.registers[0][20]=add(&s,s.registers[0][20],4u);
   s.pc=0xf1b096u;break;
  case 0xf1b096u: /* load    (r20),r0 */
   CHECK(rd32(bus,&s,s.registers[0][20]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf1b098u;break;
  case 0xf1b098u: /* subq    $4,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],4u);
   s.pc=0xf1b09au;break;
  case 0xf1b09au: /* addq    $4,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],4u);
   s.pc=0xf1b09cu;break;
  case 0xf1b09cu: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf1b09eu;break;
  case 0xf1b09eu: /* addq    $1,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],1u);
   s.pc=0xf1b0a0u;break;
  case 0xf1b0a0u: /* bclr    $3,r14 */
   s.registers[0][14]&=~(1u<<3);
   zn(&s,s.registers[0][14]);
   s.pc=0xf1b0a2u;break;
  case 0xf1b0a2u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf1b0a4u;break;
  case 0xf1b0a4u: /* store   r0,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[0][20])?(s.registers[0][20]&~3u):s.registers[0][20],s.registers[0][0]));
   s.pc=0xf1b0a6u;break;
  case 0xf1b0a6u: /* or      r7,r7 */
   s.registers[0][7]|=s.registers[0][7];
   zn(&s,s.registers[0][7]);
   s.pc=0xf1b0a8u;break;
  case 0xf1b0a8u: /* jump    nz,(r25) */
   if(condition(&s,1)){pending=1;target=s.registers[0][25];}
   s.pc=0xf1b0aau;break;
  case 0xf1b0aau: /* nop */
   s.pc=0xf1b0acu;break;
  case 0xf1b0acu: /* move    r13,r5 */
   s.registers[0][5]=s.registers[0][13];
   s.pc=0xf1b0aeu;break;
  case 0xf1b0aeu: /* shlq    $3,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<3;zn(&s,s.registers[0][15]);
   s.pc=0xf1b0b0u;break;
  case 0xf1b0b0u: /* add     r15,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][15]);
   s.pc=0xf1b0b2u;break;
  case 0xf1b0b2u: /* shrq    $3,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=s.registers[0][15]>>3;zn(&s,s.registers[0][15]);
   s.pc=0xf1b0b4u;break;
  case 0xf1b0b4u: /* load    (r5),r7 */
   CHECK(rd32(bus,&s,s.registers[0][5]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf1b0b6u;break;
  case 0xf1b0b6u: /* cmpq    $0,r7 */
   (void)sub(&s,s.registers[0][7],0x0u);
   s.pc=0xf1b0b8u;break;
  case 0xf1b0b8u: /* jr      z,00F1B0CA */
   if(condition(&s,2)){pending=1;target=0xf1b0cau;}
   s.pc=0xf1b0bau;break;
  case 0xf1b0bau: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf1b0bcu;break;
  case 0xf1b0bcu: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf1b0beu;break;
  case 0xf1b0beu: /* addq    $4,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],4u);
   s.pc=0xf1b0c0u;break;
  case 0xf1b0c0u: /* load    (r5),r4 */
   CHECK(rd32(bus,&s,s.registers[0][5]&~3u,&v));s.registers[0][4]=v;
   s.pc=0xf1b0c2u;break;
  case 0xf1b0c2u: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf1b0c4u;break;
  case 0xf1b0c4u: /* addq    $1,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],1u);
   s.pc=0xf1b0c6u;break;
  case 0xf1b0c6u: /* bclr    $3,r15 */
   s.registers[0][15]&=~(1u<<3);
   zn(&s,s.registers[0][15]);
   s.pc=0xf1b0c8u;break;
  case 0xf1b0c8u: /* jr      00F1B0D4 */
   if(condition(&s,0)){pending=1;target=0xf1b0d4u;}
   s.pc=0xf1b0cau;break;
  case 0xf1b0cau: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf1b0ccu;break;
  case 0xf1b0ccu: /* store   r0,(r10) */
   CHECK(wr32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],s.registers[0][0]));
   s.pc=0xf1b0ceu;break;
  case 0xf1b0ceu: /* store   r0,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][0]));
   s.pc=0xf1b0d0u;break;
  case 0xf1b0d0u: /* jump    (r17) */
   if(condition(&s,0)){pending=1;target=s.registers[0][17];}
   s.pc=0xf1b0d2u;break;
  case 0xf1b0d2u: /* nop */
   s.pc=0xf1b0d4u;break;
case 0xf1b0d4u: /* loadb   (r4),r0 */ CHECK(rd8(bus,&s,s.registers[0][4],&v));s.registers[0][0]=v;s.pc=0xf1b0d6u;break;
  case 0xf1b0d6u: /* shlq    $8,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<8;zn(&s,s.registers[0][0]);
   s.pc=0xf1b0d8u;break;
  case 0xf1b0d8u: /* store   r0,(r10) */
   CHECK(wr32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],s.registers[0][0]));
   s.pc=0xf1b0dau;break;
  case 0xf1b0dau: /* store   r0,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][0]));
   s.pc=0xf1b0dcu;break;
  case 0xf1b0dcu: /* addq    $1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],1u);
   s.pc=0xf1b0deu;break;
  case 0xf1b0deu: /* subq    $1,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],1u);
   s.pc=0xf1b0e0u;break;
  case 0xf1b0e0u: /* add     r23,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],s.registers[0][23]);
   s.pc=0xf1b0e2u;break;
  case 0xf1b0e2u: /* jump    nc,(r17) */
   if(condition(&s,4)){pending=1;target=s.registers[0][17];}
   s.pc=0xf1b0e4u;break;
  case 0xf1b0e4u: /* nop */
   s.pc=0xf1b0e6u;break;
  case 0xf1b0e6u: /* addq    $1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],1u);
   s.pc=0xf1b0e8u;break;
  case 0xf1b0e8u: /* subq    $1,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],1u);
   s.pc=0xf1b0eau;break;
  case 0xf1b0eau: /* jump    nn,(r17) */
   if(condition(&s,20)){pending=1;target=s.registers[0][17];}
   s.pc=0xf1b0ecu;break;
  case 0xf1b0ecu: /* nop */
   s.pc=0xf1b0eeu;break;
  case 0xf1b0eeu: /* move    r13,r5 */
   s.registers[0][5]=s.registers[0][13];
   s.pc=0xf1b0f0u;break;
  case 0xf1b0f0u: /* shlq    $3,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<3;zn(&s,s.registers[0][15]);
   s.pc=0xf1b0f2u;break;
  case 0xf1b0f2u: /* add     r15,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][15]);
   s.pc=0xf1b0f4u;break;
  case 0xf1b0f4u: /* shrq    $3,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=s.registers[0][15]>>3;zn(&s,s.registers[0][15]);
   s.pc=0xf1b0f6u;break;
  case 0xf1b0f6u: /* load    (r5),r7 */
   CHECK(rd32(bus,&s,s.registers[0][5]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf1b0f8u;break;
  case 0xf1b0f8u: /* cmpq    $0,r7 */
   (void)sub(&s,s.registers[0][7],0x0u);
   s.pc=0xf1b0fau;break;
  case 0xf1b0fau: /* jump    z,(r17) */
   if(condition(&s,2)){pending=1;target=s.registers[0][17];}
   s.pc=0xf1b0fcu;break;
  case 0xf1b0fcu: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf1b0feu;break;
  case 0xf1b0feu: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf1b100u;break;
  case 0xf1b100u: /* addq    $4,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],4u);
   s.pc=0xf1b102u;break;
  case 0xf1b102u: /* load    (r5),r4 */
   CHECK(rd32(bus,&s,s.registers[0][5]&~3u,&v));s.registers[0][4]=v;
   s.pc=0xf1b104u;break;
  case 0xf1b104u: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf1b106u;break;
  case 0xf1b106u: /* addq    $1,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],1u);
   s.pc=0xf1b108u;break;
  case 0xf1b108u: /* bclr    $3,r15 */
   s.registers[0][15]&=~(1u<<3);
   zn(&s,s.registers[0][15]);
   s.pc=0xf1b10au;break;
  case 0xf1b10au: /* jump    (r17) */
   if(condition(&s,0)){pending=1;target=s.registers[0][17];}
   s.pc=0xf1b10cu;break;
  case 0xf1b10cu: /* nop */
   s.pc=0xf1b10eu;break;
  case 0xf1b10eu: /* movei   $f1a100,r30 */
   s.registers[0][30]=0xf1a100u;
   s.pc=0xf1b114u;break;
  case 0xf1b114u: /* load    (r30),r29 */
   CHECK(rd32(bus,&s,s.registers[0][30]&~3u,&v));s.registers[0][29]=v;
   s.pc=0xf1b116u;break;
  case 0xf1b116u: /* moveq   1,r27 */
   s.registers[0][27]=1u;
   s.pc=0xf1b118u;break;
  case 0xf1b118u: /* bclr    $3,r29 */
   s.registers[0][29]&=~(1u<<3);
   zn(&s,s.registers[0][29]);
   s.pc=0xf1b11au;break;
  case 0xf1b11au: /* load    (r31),r28 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf1b11cu;break;
  case 0xf1b11cu: /* bset    $a,r29 */
   s.registers[0][29]|=(1u<<10);
   zn(&s,s.registers[0][29]);
   s.pc=0xf1b11eu;break;
  case 0xf1b11eu: /* addq    $2,r28 */
   s.registers[0][28]=add(&s,s.registers[0][28],2u);
   s.pc=0xf1b120u;break;
  case 0xf1b120u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf1b122u;break;
  case 0xf1b122u: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf1b124u;break;
  case 0xf1b124u: /* store   r29,(r30) */
   CHECK(wr32(bus,&s,local(s.registers[0][30])?(s.registers[0][30]&~3u):s.registers[0][30],s.registers[0][29]));
   s.pc=0xf1b126u;break;
  case 0xf1b126u: /* movei   $f1a114,r0 */
   s.registers[0][0]=0xf1a114u;
   s.pc=0xf1b12cu;break;
  case 0xf1b12cu: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf1b12eu;break;
  case 0xf1b12eu: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf1b130u;break;
  case 0xf1b130u: /* nop */
   s.pc=0xf1b132u;break;
  case 0xf1b132u: /* nop */
   s.pc=0xf1b134u;break;
  case 0xf1b134u: /* nop */
   s.pc=0xf1b136u;break;
  case 0xf1b136u: /* nop */
   s.pc=0xf1b138u;break;
default:return BIWN_DSP_MEDIA_AUDIO_BAD_PC;
 }if(delayed){if(pending)return BIWN_DSP_MEDIA_AUDIO_BAD_DELAY;s.pc=target;break;}delayed=pending;
 }while(delayed);*state=s;return 0;}
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_run(struct biwn_dsp_media_audio_bus *bus,struct biwn_dsp_media_audio_state *state,uint32_t budget){struct biwn_dsp_media_audio_state s;int status;if(!bus||!valid(state)||!budget||!bus->read8||!bus->read32||!bus->write32)return 1;s=*state;while(budget--){if(!(s.control&1u)||(s.pc==0xf1b074u&&s.registers[0][27]==0&&!(s.flags&8u))){*state=s;return 0;}status=biwn_dsp_media_audio_step(bus,&s);if(status)return(enum biwn_dsp_media_audio_status)status;}return 4;}
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_ssi_interrupt(struct biwn_dsp_media_audio_state *state){struct biwn_dsp_media_audio_state s;uint32_t sp;if(!valid(state))return 1;s=*state;s.control|=0x80u;if((s.flags&8u)||!(s.flags&0x20u)){*state=s;return 0;}sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.flags|=8u;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b010u;*state=s;return 0;}
