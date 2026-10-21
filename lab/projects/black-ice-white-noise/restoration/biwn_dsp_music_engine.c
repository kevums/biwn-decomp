/* Source-specific static reconstruction by generate_biwn_dsp_music_engine.py.
 * Not recovered original source. See original-DSP comparison evidence. */
#include "biwn_dsp_music_engine.h"
static uint32_t sx16(uint32_t v){return (v&0x8000u)?(v|0xffff0000u):(v&0xffffu); }
static uint32_t sar(uint32_t v,unsigned n){if(n>=32u)return(v&0x80000000u)?0xffffffffu:0u;return (v>>n)|((v&0x80000000u)&&n?(0xffffffffu<<(32u-n)):0u); }
static void zn(struct biwn_dsp_music_engine_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_dsp_music_engine_state *s,unsigned code){unsigned f=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(f&1u))&&!((code&2u)&&!(f&1u))&&!((code&4u)&&(f&(2u<<(code>>4))))&&!((code&8u)&&!(f&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf1b000u&&a<=0xf1cfffu;}
static int rd32(struct biwn_dsp_music_engine_bus *b,struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t *v){a&=~3u;if(local(a)){*v=be32(s->local_RAM+a-0xf1b000u);return 0;}if(a==0xf1a100u){s->flags=(s->flags&~7u)|s->z|(s->c<<1)|(s->n<<2);*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf1a114u){*v=s->control;return 0;}return b->read32(b->context,a,v)?2:0;}
static int rd8(struct biwn_dsp_music_engine_bus *b,struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t *v){uint8_t x;if(local(a))return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
static int wr32(struct biwn_dsp_music_engine_bus *b,struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t v){a&=~3u;if(local(a)){put32(s->local_RAM+a-0xf1b000u,v);return 0;}if(a==0xf1a100u){s->prestore_bank=s->bank;s->flags_delay=2u;s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1;s->c=(s->flags>>1)&1;s->n=(s->flags>>2)&1;s->control&=~((s->flags&0x3e00u)>>3);s->control&=~((s->flags&0x20000u)>>1);s->bank=(s->flags&8u)?0u:((s->flags>>14)&1u);return 0;}if(a==0xf1a118u){s->modulo=v;return 0;}if(a==0xf1a114u){uint32_t mask=0x1f7c0u;s->control=(s->control&mask)|(v&~mask);return 0;}return b->write32(b->context,a,v)?2:0;}
static int wr16(struct biwn_dsp_music_engine_bus *b,struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t v){(void)s;if(local(a))return 1;return b->write16(b->context,a&~1u,(uint16_t)v)?2:0;}
static int valid(struct biwn_dsp_music_engine_state *s){return s&&s->z<=1&&s->c<=1&&s->n<=1&&s->bank<=1u&&s->prestore_bank<=1u&&s->flags_delay<=2u&&s->bank==((s->flags&8u)?0u:((s->flags>>14)&1u));}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_dsp_music_engine_status)status;}while(0)
enum biwn_dsp_music_engine_status biwn_dsp_music_engine_step(struct biwn_dsp_music_engine_bus *bus,struct biwn_dsp_music_engine_state *state){struct biwn_dsp_music_engine_state s;uint32_t v,target=0;unsigned pending=0,delayed=0;if(!bus||!valid(state)||!bus->read8||!bus->read32||!bus->write32||!bus->write16)return 1;if(!(state->control&1u))return 6;s=*state;
 do{pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf1b000u: /* movei   $f1b030,r29 */
   s.registers[s.bank][29]=0xf1b030u;
   s.pc=0xf1b006u;break;
case 0xf1b006u: /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b008u;break;
  case 0xf1b008u: /* nop */
   s.pc=0xf1b00au;break;
  case 0xf1b010u: /* movei   $f1b77a,r29 */
   s.registers[s.bank][29]=0xf1b77au;
   s.pc=0xf1b016u;break;
case 0xf1b016u: /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b018u;break;
  case 0xf1b018u: /* nop */
   s.pc=0xf1b01au;break;
  case 0xf1b020u: /* movei   $f1b7a8,r29 */
   s.registers[s.bank][29]=0xf1b7a8u;
   s.pc=0xf1b026u;break;
case 0xf1b026u: /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b028u;break;
  case 0xf1b028u: /* nop */
   s.pc=0xf1b02au;break;
  case 0xf1b030u: /* movei   $f1a100,r29 */
   s.registers[s.bank][29]=0xf1a100u;
   s.pc=0xf1b036u;break;
  case 0xf1b036u: /* load    (r29),r30 */
   CHECK(rd32(bus,&s,s.registers[s.bank][29]&~3u,&v));s.registers[s.bank][30]=v;
   s.pc=0xf1b038u;break;
  case 0xf1b038u: /* movei   $f1badc,r25 */
   s.registers[s.bank][25]=0xf1badcu;
   s.pc=0xf1b03eu;break;
  case 0xf1b03eu: /* moveq   0,r0 */
   s.registers[s.bank][0]=0u;
   s.pc=0xf1b040u;break;
  case 0xf1b040u: /* load    (r25),r28 */
   CHECK(rd32(bus,&s,s.registers[s.bank][25]&~3u,&v));s.registers[s.bank][28]=v;
   s.pc=0xf1b042u;break;
  case 0xf1b042u: /* movei   $f1b080,r27 */
   s.registers[s.bank][27]=0xf1b080u;
   s.pc=0xf1b048u;break;
  case 0xf1b048u: /* cmpq    $1,r28 */
   (void)sub(&s,s.registers[s.bank][28],0x1u);
   s.pc=0xf1b04au;break;
case 0xf1b04au: /* jump    nz,(r27) */ if(condition(&s,1)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b04cu;break;
  case 0xf1b04cu: /* nop */
   s.pc=0xf1b04eu;break;
  case 0xf1b04eu: /* bset    $9,r30 */
   s.registers[s.bank][30]|=(1u<<9);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b050u;break;
  case 0xf1b050u: /* bset    $a,r30 */
   s.registers[s.bank][30]|=(1u<<10);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b052u;break;
  case 0xf1b052u: /* bset    $b,r30 */
   s.registers[s.bank][30]|=(1u<<11);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b054u;break;
  case 0xf1b054u: /* bclr    $3,r30 */
   s.registers[s.bank][30]&=~(1u<<3);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b056u;break;
  case 0xf1b056u: /* bset    $4,r30 */
   s.registers[s.bank][30]|=(1u<<4);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b058u;break;
  case 0xf1b058u: /* bclr    $5,r30 */
   s.registers[s.bank][30]&=~(1u<<5);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b05au;break;
  case 0xf1b05au: /* bclr    $6,r30 */
   s.registers[s.bank][30]&=~(1u<<6);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b05cu;break;
  case 0xf1b05cu: /* bclr    $e,r30 */
   s.registers[s.bank][30]&=~(1u<<14);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b05eu;break;
  case 0xf1b05eu: /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b060u;break;
  case 0xf1b060u: /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][29])?(s.registers[s.bank][29]&~3u):s.registers[s.bank][29],s.registers[s.bank][30]));
   s.pc=0xf1b062u;break;
  case 0xf1b062u: /* nop */
   s.pc=0xf1b064u;break;
  case 0xf1b064u: /* nop */
   s.pc=0xf1b066u;break;
  case 0xf1b066u: /* movei   $f10002,r1 */
   s.registers[s.bank][1]=0xf10002u;
   s.pc=0xf1b06cu;break;
  case 0xf1b06cu: /* movei   $f10000,r2 */
   s.registers[s.bank][2]=0xf10000u;
   s.pc=0xf1b072u;break;
case 0xf1b072u: /* storew  r0,(r1) */ CHECK(wr16(bus,&s,s.registers[s.bank][1],s.registers[s.bank][0]));s.pc=0xf1b074u;break;
  case 0xf1b074u: /* movei   $f1b144,r27 */
   s.registers[s.bank][27]=0xf1b144u;
   s.pc=0xf1b07au;break;
case 0xf1b07au: /* storew  r0,(r2) */ CHECK(wr16(bus,&s,s.registers[s.bank][2],s.registers[s.bank][0]));s.pc=0xf1b07cu;break;
case 0xf1b07cu: /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b07eu;break;
  case 0xf1b07eu: /* store   r0,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][25])?(s.registers[s.bank][25]&~3u):s.registers[s.bank][25],s.registers[s.bank][0]));
   s.pc=0xf1b080u;break;
  case 0xf1b080u: /* movei   $f1b04e,r27 */
   s.registers[s.bank][27]=0xf1b04eu;
   s.pc=0xf1b086u;break;
  case 0xf1b086u: /* cmpq    $2,r28 */
   (void)sub(&s,s.registers[s.bank][28],0x2u);
   s.pc=0xf1b088u;break;
case 0xf1b088u: /* jump    nz,(r27) */ if(condition(&s,1)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b08au;break;
  case 0xf1b08au: /* nop */
   s.pc=0xf1b08cu;break;
  case 0xf1b08cu: /* bset    $9,r30 */
   s.registers[s.bank][30]|=(1u<<9);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b08eu;break;
  case 0xf1b08eu: /* bset    $a,r30 */
   s.registers[s.bank][30]|=(1u<<10);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b090u;break;
  case 0xf1b090u: /* bset    $b,r30 */
   s.registers[s.bank][30]|=(1u<<11);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b092u;break;
  case 0xf1b092u: /* bclr    $3,r30 */
   s.registers[s.bank][30]&=~(1u<<3);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b094u;break;
  case 0xf1b094u: /* bset    $4,r30 */
   s.registers[s.bank][30]|=(1u<<4);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b096u;break;
  case 0xf1b096u: /* bclr    $5,r30 */
   s.registers[s.bank][30]&=~(1u<<5);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b098u;break;
  case 0xf1b098u: /* bclr    $6,r30 */
   s.registers[s.bank][30]&=~(1u<<6);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b09au;break;
  case 0xf1b09au: /* bclr    $e,r30 */
   s.registers[s.bank][30]&=~(1u<<14);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b09cu;break;
  case 0xf1b09cu: /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b09eu;break;
  case 0xf1b09eu: /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][29])?(s.registers[s.bank][29]&~3u):s.registers[s.bank][29],s.registers[s.bank][30]));
   s.pc=0xf1b0a0u;break;
  case 0xf1b0a0u: /* nop */
   s.pc=0xf1b0a2u;break;
  case 0xf1b0a2u: /* nop */
   s.pc=0xf1b0a4u;break;
  case 0xf1b0a4u: /* addq    $4,r25 */
   s.registers[s.bank][25]=add(&s,s.registers[s.bank][25],4u);
   s.pc=0xf1b0a6u;break;
  case 0xf1b0a6u: /* load    (r25),r1 */
   CHECK(rd32(bus,&s,s.registers[s.bank][25]&~3u,&v));s.registers[s.bank][1]=v;
   s.pc=0xf1b0a8u;break;
  case 0xf1b0a8u: /* load    (r1),r2 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][2]=v;
   s.pc=0xf1b0aau;break;
  case 0xf1b0aau: /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0acu;break;
  case 0xf1b0acu: /* load    (r1),r3 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][3]=v;
   s.pc=0xf1b0aeu;break;
  case 0xf1b0aeu: /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0b0u;break;
  case 0xf1b0b0u: /* load    (r1),r4 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][4]=v;
   s.pc=0xf1b0b2u;break;
  case 0xf1b0b2u: /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0b4u;break;
  case 0xf1b0b4u: /* shrq    $2,r4 */
   s.c=s.registers[s.bank][4]&1u;s.registers[s.bank][4]=s.registers[s.bank][4]>>2;zn(&s,s.registers[s.bank][4]);
   s.pc=0xf1b0b6u;break;
  case 0xf1b0b6u: /* load    (r2),r5 */
   CHECK(rd32(bus,&s,s.registers[s.bank][2]&~3u,&v));s.registers[s.bank][5]=v;
   s.pc=0xf1b0b8u;break;
  case 0xf1b0b8u: /* subq    $1,r4 */
   s.registers[s.bank][4]=sub(&s,s.registers[s.bank][4],1u);
   s.pc=0xf1b0bau;break;
  case 0xf1b0bau: /* store   r5,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][3])?(s.registers[s.bank][3]&~3u):s.registers[s.bank][3],s.registers[s.bank][5]));
   s.pc=0xf1b0bcu;break;
  case 0xf1b0bcu: /* addqt   $4,r2 */
   s.registers[s.bank][2]+=4u;
   s.pc=0xf1b0beu;break;
  case 0xf1b0beu: /* jr      nz,00F1B0B6 */
   if(condition(&s,1)){pending=1;target=0xf1b0b6u;}
   s.pc=0xf1b0c0u;break;
  case 0xf1b0c0u: /* addqt   $4,r3 */
   s.registers[s.bank][3]+=4u;
   s.pc=0xf1b0c2u;break;
  case 0xf1b0c2u: /* movei   $f1bb0c,r6 */
   s.registers[s.bank][6]=0xf1bb0cu;
   s.pc=0xf1b0c8u;break;
  case 0xf1b0c8u: /* load    (r1),r7 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][7]=v;
   s.pc=0xf1b0cau;break;
  case 0xf1b0cau: /* store   r7,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][6])?(s.registers[s.bank][6]&~3u):s.registers[s.bank][6],s.registers[s.bank][7]));
   s.pc=0xf1b0ccu;break;
  case 0xf1b0ccu: /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0ceu;break;
  case 0xf1b0ceu: /* movei   $f10002,r8 */
   s.registers[s.bank][8]=0xf10002u;
   s.pc=0xf1b0d4u;break;
  case 0xf1b0d4u: /* load    (r1),r9 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][9]=v;
   s.pc=0xf1b0d6u;break;
case 0xf1b0d6u: /* storew  r9,(r8) */ CHECK(wr16(bus,&s,s.registers[s.bank][8],s.registers[s.bank][9]));s.pc=0xf1b0d8u;break;
  case 0xf1b0d8u: /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0dau;break;
  case 0xf1b0dau: /* movei   $f10000,r10 */
   s.registers[s.bank][10]=0xf10000u;
   s.pc=0xf1b0e0u;break;
  case 0xf1b0e0u: /* load    (r1),r11 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][11]=v;
   s.pc=0xf1b0e2u;break;
case 0xf1b0e2u: /* storew  r11,(r10) */ CHECK(wr16(bus,&s,s.registers[s.bank][10],s.registers[s.bank][11]));s.pc=0xf1b0e4u;break;
  case 0xf1b0e4u: /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0e6u;break;
  case 0xf1b0e6u: /* addq    $4,r25 */
   s.registers[s.bank][25]=add(&s,s.registers[s.bank][25],4u);
   s.pc=0xf1b0e8u;break;
  case 0xf1b0e8u: /* addq    $8,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],8u);
   s.pc=0xf1b0eau;break;
  case 0xf1b0eau: /* load    (r25),r12 */
   CHECK(rd32(bus,&s,s.registers[s.bank][25]&~3u,&v));s.registers[s.bank][12]=v;
   s.pc=0xf1b0ecu;break;
  case 0xf1b0ecu: /* shlq    $2,r12 */
   s.c=s.registers[s.bank][12]>>31;s.registers[s.bank][12]=s.registers[s.bank][12]<<2;zn(&s,s.registers[s.bank][12]);
   s.pc=0xf1b0eeu;break;
  case 0xf1b0eeu: /* add     r12,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],s.registers[s.bank][12]);
   s.pc=0xf1b0f0u;break;
  case 0xf1b0f0u: /* movei   $f1bb08,r13 */
   s.registers[s.bank][13]=0xf1bb08u;
   s.pc=0xf1b0f6u;break;
  case 0xf1b0f6u: /* load    (r1),r14 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][14]=v;
   s.pc=0xf1b0f8u;break;
  case 0xf1b0f8u: /* store   r14,(r13) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][13])?(s.registers[s.bank][13]&~3u):s.registers[s.bank][13],s.registers[s.bank][14]));
   s.pc=0xf1b0fau;break;
  case 0xf1b0fau: /* movei   $f1bd10,r15 */
   s.registers[s.bank][15]=0xf1bd10u;
   s.pc=0xf1b100u;break;
  case 0xf1b100u: /* movei   $fffffffc,r16 */
   s.registers[s.bank][16]=0xfffffffcu;
   s.pc=0xf1b106u;break;
  case 0xf1b106u: /* movei   $50,r17 */
   s.registers[s.bank][17]=0x50u;
   s.pc=0xf1b10cu;break;
  case 0xf1b10cu: /* load    (r15),r18 */
   CHECK(rd32(bus,&s,s.registers[s.bank][15]&~3u,&v));s.registers[s.bank][18]=v;
   s.pc=0xf1b10eu;break;
  case 0xf1b10eu: /* cmpq    $0,r18 */
   (void)sub(&s,s.registers[s.bank][18],0x0u);
   s.pc=0xf1b110u;break;
  case 0xf1b110u: /* jr      z,00F1B11A */
   if(condition(&s,2)){pending=1;target=0xf1b11au;}
   s.pc=0xf1b112u;break;
  case 0xf1b112u: /* nop */
   s.pc=0xf1b114u;break;
  case 0xf1b114u: /* store   r16,(r15) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][15])?(s.registers[s.bank][15]&~3u):s.registers[s.bank][15],s.registers[s.bank][16]));
   s.pc=0xf1b116u;break;
  case 0xf1b116u: /* jr      00F1B10C */
   if(condition(&s,0)){pending=1;target=0xf1b10cu;}
   s.pc=0xf1b118u;break;
  case 0xf1b118u: /* add     r17,r15 */
   s.registers[s.bank][15]=add(&s,s.registers[s.bank][15],s.registers[s.bank][17]);
   s.pc=0xf1b11au;break;
  case 0xf1b11au: /* movei   $f1b148,r27 */
   s.registers[s.bank][27]=0xf1b148u;
   s.pc=0xf1b120u;break;
  case 0xf1b120u: /* subq    $8,r25 */
   s.registers[s.bank][25]=sub(&s,s.registers[s.bank][25],8u);
   s.pc=0xf1b122u;break;
case 0xf1b122u: /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b124u;break;
  case 0xf1b124u: /* store   r0,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][25])?(s.registers[s.bank][25]&~3u):s.registers[s.bank][25],s.registers[s.bank][0]));
   s.pc=0xf1b126u;break;
  case 0xf1b126u: /* movei   $f1b010,r31 */
   s.registers[s.bank][31]=0xf1b010u;
   s.pc=0xf1b12cu;break;
case 0xf1b12cu: /* moveta  r31,r31 */ s.registers[1u-s.bank][31]=s.registers[s.bank][31];s.pc=0xf1b12eu;break;
  case 0xf1b12eu: /* movei   $f1a100,r29 */
   s.registers[s.bank][29]=0xf1a100u;
   s.pc=0xf1b134u;break;
  case 0xf1b134u: /* load    (r29),r30 */
   CHECK(rd32(bus,&s,s.registers[s.bank][29]&~3u,&v));s.registers[s.bank][30]=v;
   s.pc=0xf1b136u;break;
  case 0xf1b136u: /* bset    $4,r30 */
   s.registers[s.bank][30]|=(1u<<4);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b138u;break;
  case 0xf1b138u: /* bclr    $5,r30 */
   s.registers[s.bank][30]&=~(1u<<5);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b13au;break;
  case 0xf1b13au: /* bclr    $6,r30 */
   s.registers[s.bank][30]&=~(1u<<6);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b13cu;break;
  case 0xf1b13cu: /* bclr    $e,r30 */
   s.registers[s.bank][30]&=~(1u<<14);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b13eu;break;
  case 0xf1b13eu: /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][29])?(s.registers[s.bank][29]&~3u):s.registers[s.bank][29],s.registers[s.bank][30]));
   s.pc=0xf1b140u;break;
  case 0xf1b140u: /* nop */
   s.pc=0xf1b142u;break;
  case 0xf1b142u: /* nop */
   s.pc=0xf1b144u;break;
  case 0xf1b148u: /* movei   $f1bd10,r0 */
   s.registers[s.bank][0]=0xf1bd10u;
   s.pc=0xf1b14eu;break;
  case 0xf1b14eu: /* movei   $f1b1dc,r1 */
   s.registers[s.bank][1]=0xf1b1dcu;
   s.pc=0xf1b154u;break;
  case 0xf1b154u: /* movei   $f1bb54,r2 */
   s.registers[s.bank][2]=0xf1bb54u;
   s.pc=0xf1b15au;break;
  case 0xf1b15au: /* movei   $4c,r3 */
   s.registers[s.bank][3]=0x4cu;
   s.pc=0xf1b160u;break;
  case 0xf1b160u: /* movei   $f1b1ca,r10 */
   s.registers[s.bank][10]=0xf1b1cau;
   s.pc=0xf1b166u;break;
  case 0xf1b166u: /* movei   $f1b2dc,r13 */
   s.registers[s.bank][13]=0xf1b2dcu;
   s.pc=0xf1b16cu;break;
  case 0xf1b16cu: /* movei   $ff,r11 */
   s.registers[s.bank][11]=0xffu;
   s.pc=0xf1b172u;break;
  case 0xf1b172u: /* movei   $7fff,r14 */
   s.registers[s.bank][14]=0x7fffu;
   s.pc=0xf1b178u;break;
  case 0xf1b178u: /* movei   $fffffffc,r15 */
   s.registers[s.bank][15]=0xfffffffcu;
   s.pc=0xf1b17eu;break;
  case 0xf1b17eu: /* movei   $7fffff,r19 */
   s.registers[s.bank][19]=0x7fffffu;
   s.pc=0xf1b184u;break;
  case 0xf1b184u: /* movei   $f1d200,r18 */
   s.registers[s.bank][18]=0xf1d200u;
   s.pc=0xf1b18au;break;
  case 0xf1b18au: /* movei   $f1bb08,r17 */
   s.registers[s.bank][17]=0xf1bb08u;
   s.pc=0xf1b190u;break;
  case 0xf1b190u: /* movei   $f1bb04,r16 */
   s.registers[s.bank][16]=0xf1bb04u;
   s.pc=0xf1b196u;break;
  case 0xf1b196u: /* moveq   0,r21 */
   s.registers[s.bank][21]=0u;
   s.pc=0xf1b198u;break;
  case 0xf1b198u: /* store   r21,(r16) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][16])?(s.registers[s.bank][16]&~3u):s.registers[s.bank][16],s.registers[s.bank][21]));
   s.pc=0xf1b19au;break;
  case 0xf1b19au: /* movei   $f1a148,r9 */
   s.registers[s.bank][9]=0xf1a148u;
   s.pc=0xf1b1a0u;break;
  case 0xf1b1a0u: /* movei   $f1a100,r20 */
   s.registers[s.bank][20]=0xf1a100u;
   s.pc=0xf1b1a6u;break;
  case 0xf1b1a6u: /* movei   $f1baf8,r24 */
   s.registers[s.bank][24]=0xf1baf8u;
   s.pc=0xf1b1acu;break;
  case 0xf1b1acu: /* load    (r20),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][20]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b1aeu;break;
  case 0xf1b1aeu: /* bset    $e,r29 */
   s.registers[s.bank][29]|=(1u<<14);
   zn(&s,s.registers[s.bank][29]);
   s.pc=0xf1b1b0u;break;
  case 0xf1b1b0u: /* bset    $5,r29 */
   s.registers[s.bank][29]|=(1u<<5);
   zn(&s,s.registers[s.bank][29]);
   s.pc=0xf1b1b2u;break;
  case 0xf1b1b2u: /* bset    $6,r29 */
   s.registers[s.bank][29]|=(1u<<6);
   zn(&s,s.registers[s.bank][29]);
   s.pc=0xf1b1b4u;break;
  case 0xf1b1b4u: /* store   r29,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][29]));
   s.pc=0xf1b1b6u;break;
  case 0xf1b1b6u: /* nop */
   s.pc=0xf1b1b8u;break;
  case 0xf1b1b8u: /* nop */
   s.pc=0xf1b1bau;break;
  case 0xf1b1bau: /* moveq   0,r28 */
   s.registers[s.bank][28]=0u;
   s.pc=0xf1b1bcu;break;
  case 0xf1b1bcu: /* movei   $f1a118,r1 */
   s.registers[s.bank][1]=0xf1a118u;
   s.pc=0xf1b1c2u;break;
  case 0xf1b1c2u: /* movei   $fffffe00,r0 */
   s.registers[s.bank][0]=0xfffffe00u;
   s.pc=0xf1b1c8u;break;
  case 0xf1b1c8u: /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][1])?(s.registers[s.bank][1]&~3u):s.registers[s.bank][1],s.registers[s.bank][0]));
   s.pc=0xf1b1cau;break;
case 0xf1b1cau: /* movefa  r0,r15 */ s.registers[s.bank][15]=s.registers[1u-s.bank][0];s.pc=0xf1b1ccu;break;
  case 0xf1b1ccu: /* moveq   0,r26 */
   s.registers[s.bank][26]=0u;
   s.pc=0xf1b1ceu;break;
  case 0xf1b1ceu: /* moveq   0,r9 */
   s.registers[s.bank][9]=0u;
   s.pc=0xf1b1d0u;break;
case 0xf1b1d0u: /* movefa  r1,r27 */ s.registers[s.bank][27]=s.registers[1u-s.bank][1];s.pc=0xf1b1d2u;break;
  case 0xf1b1d2u: /* load    (r15),r16 */
   CHECK(rd32(bus,&s,s.registers[s.bank][15]&~3u,&v));s.registers[s.bank][16]=v;
   s.pc=0xf1b1d4u;break;
case 0xf1b1d4u: /* movefa  r2,r14 */ s.registers[s.bank][14]=s.registers[1u-s.bank][2];s.pc=0xf1b1d6u;break;
case 0xf1b1d6u: /* load    (r14+r16),r25 */ CHECK(rd32(bus,&s,s.registers[s.bank][14]+s.registers[s.bank][16],&v));s.registers[s.bank][25]=v;s.pc=0xf1b1d8u;break;
case 0xf1b1d8u: /* jump    (r25) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][25];}s.pc=0xf1b1dau;break;
  case 0xf1b1dau: /* addq    $4,r15 */
   s.registers[s.bank][15]=add(&s,s.registers[s.bank][15],4u);
   s.pc=0xf1b1dcu;break;
case 0xf1b1dcu: /* movefa  r3,r1 */ s.registers[s.bank][1]=s.registers[1u-s.bank][3];s.pc=0xf1b1deu;break;
  case 0xf1b1deu: /* jr      00F1B1D2 */
   if(condition(&s,0)){pending=1;target=0xf1b1d2u;}
   s.pc=0xf1b1e0u;break;
  case 0xf1b1e0u: /* add     r1,r15 */
   s.registers[s.bank][15]=add(&s,s.registers[s.bank][15],s.registers[s.bank][1]);
   s.pc=0xf1b1e2u;break;
  case 0xf1b1e2u: /* movei   $f1bb00,r2 */
   s.registers[s.bank][2]=0xf1bb00u;
   s.pc=0xf1b1e8u;break;
  case 0xf1b1e8u: /* sharq   $f,r26 */
   s.c=s.registers[s.bank][26]&1u;s.registers[s.bank][26]=sar(s.registers[s.bank][26],15);zn(&s,s.registers[s.bank][26]);
   s.pc=0xf1b1eau;break;
  case 0xf1b1eau: /* load    (r2),r1 */
   CHECK(rd32(bus,&s,s.registers[s.bank][2]&~3u,&v));s.registers[s.bank][1]=v;
   s.pc=0xf1b1ecu;break;
  case 0xf1b1ecu: /* sharq   $f,r9 */
   s.c=s.registers[s.bank][9]&1u;s.registers[s.bank][9]=sar(s.registers[s.bank][9],15);zn(&s,s.registers[s.bank][9]);
   s.pc=0xf1b1eeu;break;
  case 0xf1b1eeu: /* imult   r1,r26 */
   s.registers[s.bank][26]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][26])*(int32_t)sx16(s.registers[s.bank][1]));
   zn(&s,s.registers[s.bank][26]);
   s.pc=0xf1b1f0u;break;
  case 0xf1b1f0u: /* movei   $f1bb10,r2 */
   s.registers[s.bank][2]=0xf1bb10u;
   s.pc=0xf1b1f6u;break;
  case 0xf1b1f6u: /* shlq    $3,r28 */
   s.c=s.registers[s.bank][28]>>31;s.registers[s.bank][28]=s.registers[s.bank][28]<<3;zn(&s,s.registers[s.bank][28]);
   s.pc=0xf1b1f8u;break;
  case 0xf1b1f8u: /* imult   r1,r9 */
   s.registers[s.bank][9]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][9])*(int32_t)sx16(s.registers[s.bank][1]));
   zn(&s,s.registers[s.bank][9]);
   s.pc=0xf1b1fau;break;
  case 0xf1b1fau: /* add     r28,r2 */
   s.registers[s.bank][2]=add(&s,s.registers[s.bank][2],s.registers[s.bank][28]);
   s.pc=0xf1b1fcu;break;
  case 0xf1b1fcu: /* sharq   $f,r26 */
   s.c=s.registers[s.bank][26]&1u;s.registers[s.bank][26]=sar(s.registers[s.bank][26],15);zn(&s,s.registers[s.bank][26]);
   s.pc=0xf1b1feu;break;
  case 0xf1b1feu: /* shrq    $3,r28 */
   s.c=s.registers[s.bank][28]&1u;s.registers[s.bank][28]=s.registers[s.bank][28]>>3;zn(&s,s.registers[s.bank][28]);
   s.pc=0xf1b200u;break;
  case 0xf1b200u: /* sharq   $f,r9 */
   s.c=s.registers[s.bank][9]&1u;s.registers[s.bank][9]=sar(s.registers[s.bank][9],15);zn(&s,s.registers[s.bank][9]);
   s.pc=0xf1b202u;break;
  case 0xf1b202u: /* store   r26,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][2])?(s.registers[s.bank][2]&~3u):s.registers[s.bank][2],s.registers[s.bank][26]));
   s.pc=0xf1b204u;break;
  case 0xf1b204u: /* addq    $1,r28 */
   s.registers[s.bank][28]=add(&s,s.registers[s.bank][28],1u);
   s.pc=0xf1b206u;break;
  case 0xf1b206u: /* addq    $4,r2 */
   s.registers[s.bank][2]=add(&s,s.registers[s.bank][2],4u);
   s.pc=0xf1b208u;break;
  case 0xf1b208u: /* bclr    $3,r28 */
   s.registers[s.bank][28]&=~(1u<<3);
   zn(&s,s.registers[s.bank][28]);
   s.pc=0xf1b20au;break;
  case 0xf1b20au: /* moveq   0,r0 */
   s.registers[s.bank][0]=0u;
   s.pc=0xf1b20cu;break;
  case 0xf1b20cu: /* store   r9,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][2])?(s.registers[s.bank][2]&~3u):s.registers[s.bank][2],s.registers[s.bank][9]));
   s.pc=0xf1b20eu;break;
  case 0xf1b20eu: /* subq    $1,r0 */
   s.registers[s.bank][0]=sub(&s,s.registers[s.bank][0],1u);
   s.pc=0xf1b210u;break;
case 0xf1b210u: /* movefa  r21,r2 */ s.registers[s.bank][2]=s.registers[1u-s.bank][21];s.pc=0xf1b212u;break;
  case 0xf1b212u: /* cmp     r28,r2 */
   (void)sub(&s,s.registers[s.bank][2],s.registers[s.bank][28]);
   s.pc=0xf1b214u;break;
  case 0xf1b214u: /* addqt   $1,r0 */
   s.registers[s.bank][0]+=1u;
   s.pc=0xf1b216u;break;
  case 0xf1b216u: /* jr      z,00F1B212 */
   if(condition(&s,2)){pending=1;target=0xf1b212u;}
   s.pc=0xf1b218u;break;
case 0xf1b218u: /* movefa  r21,r2 */ s.registers[s.bank][2]=s.registers[1u-s.bank][21];s.pc=0xf1b21au;break;
case 0xf1b21au: /* movefa  r24,r1 */ s.registers[s.bank][1]=s.registers[1u-s.bank][24];s.pc=0xf1b21cu;break;
case 0xf1b21cu: /* movefa  r10,r27 */ s.registers[s.bank][27]=s.registers[1u-s.bank][10];s.pc=0xf1b21eu;break;
case 0xf1b21eu: /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b220u;break;
  case 0xf1b220u: /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][1])?(s.registers[s.bank][1]&~3u):s.registers[s.bank][1],s.registers[s.bank][0]));
   s.pc=0xf1b222u;break;
case 0xf1b2f6u: /* load    (r15+$8),r2 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+8u,&v));s.registers[s.bank][2]=v;s.pc=0xf1b2f8u;break;
case 0xf1b2f8u: /* movefa  r11,r24 */ s.registers[s.bank][24]=s.registers[1u-s.bank][11];s.pc=0xf1b2fau;break;
case 0xf1b2fau: /* load    (r15+$14),r5 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+20u,&v));s.registers[s.bank][5]=v;s.pc=0xf1b2fcu;break;
case 0xf1b2fcu: /* load    (r15+$c),r3 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+12u,&v));s.registers[s.bank][3]=v;s.pc=0xf1b2feu;break;
  case 0xf1b2feu: /* add     r2,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],s.registers[s.bank][2]);
   s.pc=0xf1b300u;break;
  case 0xf1b300u: /* load    (r15),r0 */
   CHECK(rd32(bus,&s,s.registers[s.bank][15]&~3u,&v));s.registers[s.bank][0]=v;
   s.pc=0xf1b302u;break;
  case 0xf1b302u: /* cmp     r5,r3 */
   (void)sub(&s,s.registers[s.bank][3],s.registers[s.bank][5]);
   s.pc=0xf1b304u;break;
case 0xf1b304u: /* load    (r15+$10),r4 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+16u,&v));s.registers[s.bank][4]=v;s.pc=0xf1b306u;break;
  case 0xf1b306u: /* jr      nn,00F1B318 */
   if(condition(&s,20)){pending=1;target=0xf1b318u;}
   s.pc=0xf1b308u;break;
  case 0xf1b308u: /* btst    $1f,r0 */
   s.z=((~s.registers[s.bank][0])>>31)&1u;
   s.pc=0xf1b30au;break;
  case 0xf1b318u: /* move    r5,r4 */
   s.registers[s.bank][4]=s.registers[s.bank][5];
   s.pc=0xf1b31au;break;
case 0xf1b31au: /* store   r5,(r15+$14) */ CHECK(wr32(bus,&s,s.registers[s.bank][15]+20u,s.registers[s.bank][5]));s.pc=0xf1b31cu;break;
  case 0xf1b31cu: /* shrq    $8,r5 */
   s.c=s.registers[s.bank][5]&1u;s.registers[s.bank][5]=s.registers[s.bank][5]>>8;zn(&s,s.registers[s.bank][5]);
   s.pc=0xf1b31eu;break;
  case 0xf1b31eu: /* and     r24,r4 */
   s.registers[s.bank][4]&=s.registers[s.bank][24];
   zn(&s,s.registers[s.bank][4]);
   s.pc=0xf1b320u;break;
case 0xf1b320u: /* movefa  r14,r20 */ s.registers[s.bank][20]=s.registers[1u-s.bank][14];s.pc=0xf1b322u;break;
case 0xf1b322u: /* load    (r15+$4),r1 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+4u,&v));s.registers[s.bank][1]=v;s.pc=0xf1b324u;break;
  case 0xf1b324u: /* move    r24,r6 */
   s.registers[s.bank][6]=s.registers[s.bank][24];
   s.pc=0xf1b326u;break;
  case 0xf1b326u: /* add     r1,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],s.registers[s.bank][1]);
   s.pc=0xf1b328u;break;
  case 0xf1b328u: /* sub     r4,r6 */
   s.registers[s.bank][6]=sub(&s,s.registers[s.bank][6],s.registers[s.bank][4]);
   s.pc=0xf1b32au;break;
case 0xf1b32au: /* loadb   (r5),r13 */ CHECK(rd8(bus,&s,s.registers[s.bank][5],&v));s.registers[s.bank][13]=v;s.pc=0xf1b32cu;break;
  case 0xf1b32cu: /* addq    $1,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],1u);
   s.pc=0xf1b32eu;break;
case 0xf1b32eu: /* loadb   (r5),r7 */ CHECK(rd8(bus,&s,s.registers[s.bank][5],&v));s.registers[s.bank][7]=v;s.pc=0xf1b330u;break;
  case 0xf1b330u: /* move    r13,r1 */
   s.registers[s.bank][1]=s.registers[s.bank][13];
   s.pc=0xf1b332u;break;
  case 0xf1b332u: /* bclr    $7,r13 */
   s.registers[s.bank][13]&=~(1u<<7);
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b334u;break;
  case 0xf1b334u: /* btst    $7,r1 */
   s.z=((~s.registers[s.bank][1])>>7)&1u;
   s.pc=0xf1b336u;break;
  case 0xf1b336u: /* jr      z,00F1B33C */
   if(condition(&s,2)){pending=1;target=0xf1b33cu;}
   s.pc=0xf1b338u;break;
  case 0xf1b338u: /* mult    r13,r13 */
   s.registers[s.bank][13]=(s.registers[s.bank][13]&0xffffu)*(s.registers[s.bank][13]&0xffffu);
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b33au;break;
  case 0xf1b33au: /* neg     r13 */
   s.registers[s.bank][13]=sub(&s,0,s.registers[s.bank][13]);
   s.pc=0xf1b33cu;break;
  case 0xf1b33cu: /* move    r7,r2 */
   s.registers[s.bank][2]=s.registers[s.bank][7];
   s.pc=0xf1b33eu;break;
  case 0xf1b33eu: /* bclr    $7,r7 */
   s.registers[s.bank][7]&=~(1u<<7);
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b340u;break;
  case 0xf1b340u: /* btst    $7,r2 */
   s.z=((~s.registers[s.bank][2])>>7)&1u;
   s.pc=0xf1b342u;break;
  case 0xf1b342u: /* jr      z,00F1B348 */
   if(condition(&s,2)){pending=1;target=0xf1b348u;}
   s.pc=0xf1b344u;break;
  case 0xf1b344u: /* mult    r7,r7 */
   s.registers[s.bank][7]=(s.registers[s.bank][7]&0xffffu)*(s.registers[s.bank][7]&0xffffu);
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b346u;break;
  case 0xf1b346u: /* neg     r7 */
   s.registers[s.bank][7]=sub(&s,0,s.registers[s.bank][7]);
   s.pc=0xf1b348u;break;
  case 0xf1b348u: /* imult   r6,r13 */
   s.registers[s.bank][13]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][13])*(int32_t)sx16(s.registers[s.bank][6]));
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b34au;break;
  case 0xf1b34au: /* imult   r4,r7 */
   s.registers[s.bank][7]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][7])*(int32_t)sx16(s.registers[s.bank][4]));
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b34cu;break;
  case 0xf1b34cu: /* add     r7,r13 */
   s.registers[s.bank][13]=add(&s,s.registers[s.bank][13],s.registers[s.bank][7]);
   s.pc=0xf1b34eu;break;
case 0xf1b34eu: /* load    (r15+$48),r19 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+72u,&v));s.registers[s.bank][19]=v;s.pc=0xf1b350u;break;
  case 0xf1b350u: /* sharq   $7,r13 */
   s.c=s.registers[s.bank][13]&1u;s.registers[s.bank][13]=sar(s.registers[s.bank][13],7);zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b352u;break;
  case 0xf1b352u: /* imult   r0,r13 */
   s.registers[s.bank][13]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][13])*(int32_t)sx16(s.registers[s.bank][0]));
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b354u;break;
  case 0xf1b354u: /* sharq   $f,r13 */
   s.c=s.registers[s.bank][13]&1u;s.registers[s.bank][13]=sar(s.registers[s.bank][13],15);zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b356u;break;
  case 0xf1b356u: /* sub     r19,r20 */
   s.registers[s.bank][20]=sub(&s,s.registers[s.bank][20],s.registers[s.bank][19]);
   s.pc=0xf1b358u;break;
  case 0xf1b358u: /* imult   r13,r19 */
   s.registers[s.bank][19]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][19])*(int32_t)sx16(s.registers[s.bank][13]));
   zn(&s,s.registers[s.bank][19]);
   s.pc=0xf1b35au;break;
  case 0xf1b35au: /* imult   r13,r20 */
   s.registers[s.bank][20]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][20])*(int32_t)sx16(s.registers[s.bank][13]));
   zn(&s,s.registers[s.bank][20]);
   s.pc=0xf1b35cu;break;
  case 0xf1b35cu: /* add     r19,r9 */
   s.registers[s.bank][9]=add(&s,s.registers[s.bank][9],s.registers[s.bank][19]);
   s.pc=0xf1b35eu;break;
case 0xf1b35eu: /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b360u;break;
  case 0xf1b360u: /* add     r20,r26 */
   s.registers[s.bank][26]=add(&s,s.registers[s.bank][26],s.registers[s.bank][20]);
   s.pc=0xf1b362u;break;
  case 0xf1b77au: /* load    (r20),r30 */
   CHECK(rd32(bus,&s,s.registers[s.bank][20]&~3u,&v));s.registers[s.bank][30]=v;
   s.pc=0xf1b77cu;break;
  case 0xf1b77cu: /* shlq    $3,r21 */
   s.c=s.registers[s.bank][21]>>31;s.registers[s.bank][21]=s.registers[s.bank][21]<<3;zn(&s,s.registers[s.bank][21]);
   s.pc=0xf1b77eu;break;
  case 0xf1b77eu: /* bset    $a,r30 */
   s.registers[s.bank][30]|=(1u<<10);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b780u;break;
  case 0xf1b780u: /* movei   $f1bb10,r28 */
   s.registers[s.bank][28]=0xf1bb10u;
   s.pc=0xf1b786u;break;
  case 0xf1b786u: /* bclr    $3,r30 */
   s.registers[s.bank][30]&=~(1u<<3);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b788u;break;
  case 0xf1b788u: /* add     r21,r28 */
   s.registers[s.bank][28]=add(&s,s.registers[s.bank][28],s.registers[s.bank][21]);
   s.pc=0xf1b78au;break;
  case 0xf1b78au: /* load    (r28),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][28]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b78cu;break;
  case 0xf1b78cu: /* shrq    $3,r21 */
   s.c=s.registers[s.bank][21]&1u;s.registers[s.bank][21]=s.registers[s.bank][21]>>3;zn(&s,s.registers[s.bank][21]);
   s.pc=0xf1b78eu;break;
  case 0xf1b78eu: /* store   r29,(r9) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][9])?(s.registers[s.bank][9]&~3u):s.registers[s.bank][9],s.registers[s.bank][29]));
   s.pc=0xf1b790u;break;
  case 0xf1b790u: /* addq    $4,r28 */
   s.registers[s.bank][28]=add(&s,s.registers[s.bank][28],4u);
   s.pc=0xf1b792u;break;
  case 0xf1b792u: /* addq    $4,r9 */
   s.registers[s.bank][9]=add(&s,s.registers[s.bank][9],4u);
   s.pc=0xf1b794u;break;
  case 0xf1b794u: /* load    (r28),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][28]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b796u;break;
  case 0xf1b796u: /* addq    $1,r21 */
   s.registers[s.bank][21]=add(&s,s.registers[s.bank][21],1u);
   s.pc=0xf1b798u;break;
  case 0xf1b798u: /* store   r29,(r9) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][9])?(s.registers[s.bank][9]&~3u):s.registers[s.bank][9],s.registers[s.bank][29]));
   s.pc=0xf1b79au;break;
  case 0xf1b79au: /* bclr    $3,r21 */
   s.registers[s.bank][21]&=~(1u<<3);
   zn(&s,s.registers[s.bank][21]);
   s.pc=0xf1b79cu;break;
  case 0xf1b79cu: /* load    (r31),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][31]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b79eu;break;
  case 0xf1b79eu: /* subq    $4,r9 */
   s.registers[s.bank][9]=sub(&s,s.registers[s.bank][9],4u);
   s.pc=0xf1b7a0u;break;
  case 0xf1b7a0u: /* addq    $2,r29 */
   s.registers[s.bank][29]=add(&s,s.registers[s.bank][29],2u);
   s.pc=0xf1b7a2u;break;
  case 0xf1b7a2u: /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b7a4u;break;
case 0xf1b7a4u: /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b7a6u;break;
  case 0xf1b7a6u: /* store   r30,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][30]));
   s.pc=0xf1b7a8u;break;
  case 0xf1b7a8u: /* load    (r20),r22 */
   CHECK(rd32(bus,&s,s.registers[s.bank][20]&~3u,&v));s.registers[s.bank][22]=v;
   s.pc=0xf1b7aau;break;
  case 0xf1b7aau: /* bset    $b,r22 */
   s.registers[s.bank][22]|=(1u<<11);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7acu;break;
  case 0xf1b7acu: /* bclr    $3,r22 */
   s.registers[s.bank][22]&=~(1u<<3);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7aeu;break;
  case 0xf1b7aeu: /* bclr    $6,r22 */
   s.registers[s.bank][22]&=~(1u<<6);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7b0u;break;
  case 0xf1b7b0u: /* bclr    $e,r22 */
   s.registers[s.bank][22]&=~(1u<<14);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7b2u;break;
  case 0xf1b7b2u: /* store   r22,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][22]));
   s.pc=0xf1b7b4u;break;
  case 0xf1b7b4u: /* nop */
   s.pc=0xf1b7b6u;break;
  case 0xf1b7b6u: /* nop */
   s.pc=0xf1b7b8u;break;
  case 0xf1b7b8u: /* load    (r16),r4 */
   CHECK(rd32(bus,&s,s.registers[s.bank][16]&~3u,&v));s.registers[s.bank][4]=v;
   s.pc=0xf1b7bau;break;
  case 0xf1b7bau: /* load    (r17),r5 */
   CHECK(rd32(bus,&s,s.registers[s.bank][17]&~3u,&v));s.registers[s.bank][5]=v;
   s.pc=0xf1b7bcu;break;
  case 0xf1b7bcu: /* addq    $1,r4 */
   s.registers[s.bank][4]=add(&s,s.registers[s.bank][4],1u);
   s.pc=0xf1b7beu;break;
  case 0xf1b7beu: /* load    (r5),r6 */
   CHECK(rd32(bus,&s,s.registers[s.bank][5]&~3u,&v));s.registers[s.bank][6]=v;
   s.pc=0xf1b7c0u;break;
  case 0xf1b7c0u: /* movei   $f1b81c,r8 */
   s.registers[s.bank][8]=0xf1b81cu;
   s.pc=0xf1b7c6u;break;
  case 0xf1b7c6u: /* cmp     r4,r6 */
   (void)sub(&s,s.registers[s.bank][6],s.registers[s.bank][4]);
   s.pc=0xf1b7c8u;break;
  case 0xf1b7c8u: /* jr      n,00F1B7D0 */
   if(condition(&s,24)){pending=1;target=0xf1b7d0u;}
   s.pc=0xf1b7cau;break;
  case 0xf1b7cau: /* nop */
   s.pc=0xf1b7ccu;break;
  case 0xf1b7d0u: /* addq    $4,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],4u);
   s.pc=0xf1b7d2u;break;
  case 0xf1b7d2u: /* load    (r5),r6 */
   CHECK(rd32(bus,&s,s.registers[s.bank][5]&~3u,&v));s.registers[s.bank][6]=v;
   s.pc=0xf1b7d4u;break;
  case 0xf1b7d4u: /* addq    $4,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],4u);
   s.pc=0xf1b7d6u;break;
  case 0xf1b7d6u: /* move    r6,r7 */
   s.registers[s.bank][7]=s.registers[s.bank][6];
   s.pc=0xf1b7d8u;break;
  case 0xf1b7d8u: /* shlq    $3,r7 */
   s.c=s.registers[s.bank][7]>>31;s.registers[s.bank][7]=s.registers[s.bank][7]<<3;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b7dau;break;
  case 0xf1b7dau: /* shrq    $1d,r7 */
   s.c=s.registers[s.bank][7]&1u;s.registers[s.bank][7]=s.registers[s.bank][7]>>29;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b7dcu;break;
  case 0xf1b7dcu: /* shlq    $2,r7 */
   s.c=s.registers[s.bank][7]>>31;s.registers[s.bank][7]=s.registers[s.bank][7]<<2;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b7deu;break;
  case 0xf1b7deu: /* movei   $f1bc30,r23 */
   s.registers[s.bank][23]=0xf1bc30u;
   s.pc=0xf1b7e4u;break;
  case 0xf1b7e4u: /* movei   $f1bc70,r25 */
   s.registers[s.bank][25]=0xf1bc70u;
   s.pc=0xf1b7eau;break;
  case 0xf1b7eau: /* movei   $f1bcac,r26 */
   s.registers[s.bank][26]=0xf1bcacu;
   s.pc=0xf1b7f0u;break;
  case 0xf1b7f0u: /* movei   $f1bcec,r27 */
   s.registers[s.bank][27]=0xf1bcecu;
   s.pc=0xf1b7f6u;break;
  case 0xf1b7f6u: /* add     r7,r23 */
   s.registers[s.bank][23]=add(&s,s.registers[s.bank][23],s.registers[s.bank][7]);
   s.pc=0xf1b7f8u;break;
  case 0xf1b7f8u: /* add     r7,r26 */
   s.registers[s.bank][26]=add(&s,s.registers[s.bank][26],s.registers[s.bank][7]);
   s.pc=0xf1b7fau;break;
  case 0xf1b7fau: /* store   r23,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][25])?(s.registers[s.bank][25]&~3u):s.registers[s.bank][25],s.registers[s.bank][23]));
   s.pc=0xf1b7fcu;break;
  case 0xf1b7fcu: /* store   r26,(r27) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][27])?(s.registers[s.bank][27]&~3u):s.registers[s.bank][27],s.registers[s.bank][26]));
   s.pc=0xf1b7feu;break;
  case 0xf1b7feu: /* shrq    $2,r7 */
   s.c=s.registers[s.bank][7]&1u;s.registers[s.bank][7]=s.registers[s.bank][7]>>2;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b800u;break;
  case 0xf1b800u: /* move    r3,r27 */
   s.registers[s.bank][27]=s.registers[s.bank][3];
   s.pc=0xf1b802u;break;
  case 0xf1b802u: /* addq    $4,r27 */
   s.registers[s.bank][27]=add(&s,s.registers[s.bank][27],4u);
   s.pc=0xf1b804u;break;
  case 0xf1b804u: /* mult    r27,r7 */
   s.registers[s.bank][7]=(s.registers[s.bank][7]&0xffffu)*(s.registers[s.bank][27]&0xffffu);
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b806u;break;
  case 0xf1b806u: /* add     r0,r7 */
   s.registers[s.bank][7]=add(&s,s.registers[s.bank][7],s.registers[s.bank][0]);
   s.pc=0xf1b808u;break;
  case 0xf1b808u: /* move    r6,r23 */
   s.registers[s.bank][23]=s.registers[s.bank][6];
   s.pc=0xf1b80au;break;
  case 0xf1b80au: /* shrq    $1d,r23 */
   s.c=s.registers[s.bank][23]&1u;s.registers[s.bank][23]=s.registers[s.bank][23]>>29;zn(&s,s.registers[s.bank][23]);
   s.pc=0xf1b80cu;break;
  case 0xf1b80cu: /* shlq    $2,r23 */
   s.c=s.registers[s.bank][23]>>31;s.registers[s.bank][23]=s.registers[s.bank][23]<<2;zn(&s,s.registers[s.bank][23]);
   s.pc=0xf1b80eu;break;
  case 0xf1b80eu: /* movei   $f1bcf0,r26 */
   s.registers[s.bank][26]=0xf1bcf0u;
   s.pc=0xf1b814u;break;
  case 0xf1b814u: /* add     r23,r26 */
   s.registers[s.bank][26]=add(&s,s.registers[s.bank][26],s.registers[s.bank][23]);
   s.pc=0xf1b816u;break;
  case 0xf1b816u: /* load    (r26),r25 */
   CHECK(rd32(bus,&s,s.registers[s.bank][26]&~3u,&v));s.registers[s.bank][25]=v;
   s.pc=0xf1b818u;break;
case 0xf1b818u: /* jump    (r25) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][25];}s.pc=0xf1b81au;break;
  case 0xf1b81au: /* nop */
   s.pc=0xf1b81cu;break;
  case 0xf1b81cu: /* store   r4,(r16) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][16])?(s.registers[s.bank][16]&~3u):s.registers[s.bank][16],s.registers[s.bank][4]));
   s.pc=0xf1b81eu;break;
  case 0xf1b81eu: /* store   r5,(r17) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][17])?(s.registers[s.bank][17]&~3u):s.registers[s.bank][17],s.registers[s.bank][5]));
   s.pc=0xf1b820u;break;
  case 0xf1b820u: /* bset    $6,r22 */
   s.registers[s.bank][22]|=(1u<<6);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b822u;break;
  case 0xf1b822u: /* load    (r31),r27 */
   CHECK(rd32(bus,&s,s.registers[s.bank][31]&~3u,&v));s.registers[s.bank][27]=v;
   s.pc=0xf1b824u;break;
  case 0xf1b824u: /* bset    $e,r22 */
   s.registers[s.bank][22]|=(1u<<14);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b826u;break;
  case 0xf1b826u: /* addq    $2,r27 */
   s.registers[s.bank][27]=add(&s,s.registers[s.bank][27],2u);
   s.pc=0xf1b828u;break;
  case 0xf1b828u: /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b82au;break;
case 0xf1b82au: /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b82cu;break;
  case 0xf1b82cu: /* store   r22,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][22]));
   s.pc=0xf1b82eu;break;
  case 0xf1b9a2u: /* moveq   15,r23 */
   s.registers[s.bank][23]=15u;
   s.pc=0xf1b9a4u;break;
  case 0xf1b9a4u: /* and     r6,r23 */
   s.registers[s.bank][23]&=s.registers[s.bank][6];
   zn(&s,s.registers[s.bank][23]);
   s.pc=0xf1b9a6u;break;
  case 0xf1b9a6u: /* jr      z,00F1B9C4 */
   if(condition(&s,2)){pending=1;target=0xf1b9c4u;}
   s.pc=0xf1b9a8u;break;
  case 0xf1b9a8u: /* btst    $1c,r6 */
   s.z=((~s.registers[s.bank][6])>>28)&1u;
   s.pc=0xf1b9aau;break;
  case 0xf1b9aau: /* jr      nz,00F1B9B6 */
   if(condition(&s,1)){pending=1;target=0xf1b9b6u;}
   s.pc=0xf1b9acu;break;
  case 0xf1b9acu: /* nop */
   s.pc=0xf1b9aeu;break;
  case 0xf1b9b6u: /* shlq    $4,r6 */
   s.c=s.registers[s.bank][6]>>31;s.registers[s.bank][6]=s.registers[s.bank][6]<<4;zn(&s,s.registers[s.bank][6]);
   s.pc=0xf1b9b8u;break;
  case 0xf1b9b8u: /* sharq   $c,r6 */
   s.c=s.registers[s.bank][6]&1u;s.registers[s.bank][6]=sar(s.registers[s.bank][6],12);zn(&s,s.registers[s.bank][6]);
   s.pc=0xf1b9bau;break;
  case 0xf1b9bau: /* shlq    $3,r6 */
   s.c=s.registers[s.bank][6]>>31;s.registers[s.bank][6]=s.registers[s.bank][6]<<3;zn(&s,s.registers[s.bank][6]);
   s.pc=0xf1b9bcu;break;
  case 0xf1b9bcu: /* add     r6,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],s.registers[s.bank][6]);
   s.pc=0xf1b9beu;break;
  case 0xf1b9beu: /* load    (r5),r4 */
   CHECK(rd32(bus,&s,s.registers[s.bank][5]&~3u,&v));s.registers[s.bank][4]=v;
   s.pc=0xf1b9c0u;break;
case 0xf1b9c0u: /* jump    (r8) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][8];}s.pc=0xf1b9c2u;break;
  case 0xf1b9c2u: /* nop */
   s.pc=0xf1b9c4u;break;
default:return BIWN_DSP_MUSIC_ENGINE_BAD_PC;
 }if(delayed){if(pending)return BIWN_DSP_MUSIC_ENGINE_BAD_DELAY;s.pc=target;s.flags_delay=0;break;}delayed=pending;
 if(s.flags_delay)s.flags_delay--; }while(delayed);*state=s;return 0;}
enum biwn_dsp_music_engine_status biwn_dsp_music_engine_assert_interrupt(struct biwn_dsp_music_engine_state *state,uint32_t irq){struct biwn_dsp_music_engine_state s;uint32_t mask,bits,sp;unsigned which=0;if(!valid(state)||(irq>2u))return 1;s=*state;mask=0x40u<<irq;s.control|=mask;if((s.flags&8u)||s.flags_delay){*state=s;return 0;}bits=((s.control>>6)&31u)&((s.flags>>4)&31u);if(!bits){*state=s;return 0;}for(unsigned i=0;i<5;i++)if(bits&(1u<<i))which=i;if(which>2u)return 1;s.flags|=8u;s.bank=0;s.flags_delay=0;s.prestore_bank=0;sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b000u+which*16u;*state=s;return 0;}
