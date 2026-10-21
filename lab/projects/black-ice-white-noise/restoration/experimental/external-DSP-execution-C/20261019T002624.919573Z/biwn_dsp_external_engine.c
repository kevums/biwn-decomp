static unsigned biwn_DSP_last_operands[2];
/* Source-specific static reconstruction by generate_biwn_dsp_external_engine.py.
 * Not recovered original source. See original-DSP comparison evidence. */
#include "biwn_dsp_external_engine.h"
static uint32_t sx16(uint32_t v){return (v&0x8000u)?(v|0xffff0000u):(v&0xffffu); }
static uint32_t sar(uint32_t v,unsigned n){if(n>=32u)return(v&0x80000000u)?0xffffffffu:0u;return (v>>n)|((v&0x80000000u)&&n?(0xffffffffu<<(32u-n)):0u); }
static void zn(struct biwn_dsp_external_engine_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_dsp_external_engine_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_dsp_external_engine_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_dsp_external_engine_state *s,unsigned code){unsigned f=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(f&1u))&&!((code&2u)&&!(f&1u))&&!((code&4u)&&(f&(2u<<(code>>4))))&&!((code&8u)&&!(f&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf1b000u&&a<=0xf1cfffu;}
static int rd32(struct biwn_dsp_external_engine_bus *b,struct biwn_dsp_external_engine_state *s,uint32_t a,uint32_t *v){a&=~3u;if(local(a)){*v=be32(s->local_RAM+a-0xf1b000u);return 0;}if(a==0xf1a100u){s->flags=(s->flags&~7u)|s->z|(s->c<<1)|(s->n<<2);*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf1a114u){*v=s->control;return 0;}return b->read32(b->context,a,v)?2:0;}
static int rd8(struct biwn_dsp_external_engine_bus *b,struct biwn_dsp_external_engine_state *s,uint32_t a,uint32_t *v){uint8_t x;if(local(a))return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
static int wr32(struct biwn_dsp_external_engine_bus *b,struct biwn_dsp_external_engine_state *s,uint32_t a,uint32_t v){a&=~3u;if(local(a)){put32(s->local_RAM+a-0xf1b000u,v);return 0;}if(a==0xf1a100u){s->prestore_bank=s->bank;s->flags_delay=2u;s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1;s->c=(s->flags>>1)&1;s->n=(s->flags>>2)&1;s->control&=~((s->flags&0x3e00u)>>3);s->control&=~((s->flags&0x20000u)>>1);s->bank=(s->flags&8u)?0u:((s->flags>>14)&1u);return b->write32(b->context,a,v)?2:0;}if(a==0xf1a118u){s->modulo=v;return 0;}if(a==0xf1a114u){uint32_t mask=0x1f7c0u;s->control=(s->control&mask)|(v&~mask);return b->write32(b->context,a,v)?2:0;}return b->write32(b->context,a,v)?2:0;}
static int wr16(struct biwn_dsp_external_engine_bus *b,struct biwn_dsp_external_engine_state *s,uint32_t a,uint32_t v){(void)s;if(local(a))return 1;return b->write16(b->context,a&~1u,(uint16_t)v)?2:0;}
static int valid(struct biwn_dsp_external_engine_state *s){return s&&s->z<=1&&s->c<=1&&s->n<=1&&s->bank<=1u&&s->prestore_bank<=1u&&s->flags_delay<=2u&&s->bank==((s->flags&8u)?0u:((s->flags>>14)&1u));}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_dsp_external_engine_status)status;}while(0)
enum biwn_dsp_external_engine_status biwn_dsp_external_engine_step(struct biwn_dsp_external_engine_bus *bus,struct biwn_dsp_external_engine_state *state){struct biwn_dsp_external_engine_state s;uint32_t v,target=0;unsigned pending=0,delayed=0;if(!bus||!valid(state)||!bus->read8||!bus->read32||!bus->write32||!bus->write16)return 1;if(!(state->control&1u))return 6;s=*state;
 do{pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf1b000u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=29u; /* movei   $f1b030,r29 */
   s.registers[s.bank][29]=0xf1b030u;
   s.pc=0xf1b006u;break;
case 0xf1b006u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=0u; /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b008u;break;
  case 0xf1b008u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b00au;break;
  case 0xf1b010u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=29u; /* movei   $f1b77a,r29 */
   s.registers[s.bank][29]=0xf1b77au;
   s.pc=0xf1b016u;break;
case 0xf1b016u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=0u; /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b018u;break;
  case 0xf1b018u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b01au;break;
  case 0xf1b020u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=29u; /* movei   $f1b7a8,r29 */
   s.registers[s.bank][29]=0xf1b7a8u;
   s.pc=0xf1b026u;break;
case 0xf1b026u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=0u; /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b028u;break;
  case 0xf1b028u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b02au;break;
  case 0xf1b030u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=29u; /* movei   $f1a100,r29 */
   s.registers[s.bank][29]=0xf1a100u;
   s.pc=0xf1b036u;break;
  case 0xf1b036u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=30u; /* load    (r29),r30 */
   CHECK(rd32(bus,&s,s.registers[s.bank][29]&~3u,&v));s.registers[s.bank][30]=v;
   s.pc=0xf1b038u;break;
  case 0xf1b038u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=25u; /* movei   $f1badc,r25 */
   s.registers[s.bank][25]=0xf1badcu;
   s.pc=0xf1b03eu;break;
  case 0xf1b03eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* moveq   0,r0 */
   s.registers[s.bank][0]=0u;
   s.pc=0xf1b040u;break;
  case 0xf1b040u:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=28u; /* load    (r25),r28 */
   CHECK(rd32(bus,&s,s.registers[s.bank][25]&~3u,&v));s.registers[s.bank][28]=v;
   s.pc=0xf1b042u;break;
  case 0xf1b042u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=27u; /* movei   $f1b080,r27 */
   s.registers[s.bank][27]=0xf1b080u;
   s.pc=0xf1b048u;break;
  case 0xf1b048u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=28u; /* cmpq    $1,r28 */
   (void)sub(&s,s.registers[s.bank][28],0x1u);
   s.pc=0xf1b04au;break;
case 0xf1b04au:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=1u; /* jump    nz,(r27) */ if(condition(&s,1)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b04cu;break;
  case 0xf1b04cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b04eu;break;
  case 0xf1b04eu:biwn_DSP_last_operands[0]=9u;biwn_DSP_last_operands[1]=30u; /* bset    $9,r30 */
   s.registers[s.bank][30]|=(1u<<9);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b050u;break;
  case 0xf1b050u:biwn_DSP_last_operands[0]=10u;biwn_DSP_last_operands[1]=30u; /* bset    $a,r30 */
   s.registers[s.bank][30]|=(1u<<10);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b052u;break;
  case 0xf1b052u:biwn_DSP_last_operands[0]=11u;biwn_DSP_last_operands[1]=30u; /* bset    $b,r30 */
   s.registers[s.bank][30]|=(1u<<11);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b054u;break;
  case 0xf1b054u:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=30u; /* bclr    $3,r30 */
   s.registers[s.bank][30]&=~(1u<<3);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b056u;break;
  case 0xf1b056u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=30u; /* bset    $4,r30 */
   s.registers[s.bank][30]|=(1u<<4);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b058u;break;
  case 0xf1b058u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=30u; /* bclr    $5,r30 */
   s.registers[s.bank][30]&=~(1u<<5);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b05au;break;
  case 0xf1b05au:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=30u; /* bclr    $6,r30 */
   s.registers[s.bank][30]&=~(1u<<6);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b05cu;break;
  case 0xf1b05cu:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=30u; /* bclr    $e,r30 */
   s.registers[s.bank][30]&=~(1u<<14);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b05eu;break;
  case 0xf1b05eu:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=31u; /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b060u;break;
  case 0xf1b060u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=30u; /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][29])?(s.registers[s.bank][29]&~3u):s.registers[s.bank][29],s.registers[s.bank][30]));
   s.pc=0xf1b062u;break;
  case 0xf1b062u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b064u;break;
  case 0xf1b064u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b066u;break;
  case 0xf1b066u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=1u; /* movei   $f10002,r1 */
   s.registers[s.bank][1]=0xf10002u;
   s.pc=0xf1b06cu;break;
  case 0xf1b06cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=2u; /* movei   $f10000,r2 */
   s.registers[s.bank][2]=0xf10000u;
   s.pc=0xf1b072u;break;
case 0xf1b072u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=0u; /* storew  r0,(r1) */ CHECK(wr16(bus,&s,s.registers[s.bank][1],s.registers[s.bank][0]));s.pc=0xf1b074u;break;
  case 0xf1b074u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=27u; /* movei   $f1b144,r27 */
   s.registers[s.bank][27]=0xf1b144u;
   s.pc=0xf1b07au;break;
case 0xf1b07au:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=0u; /* storew  r0,(r2) */ CHECK(wr16(bus,&s,s.registers[s.bank][2],s.registers[s.bank][0]));s.pc=0xf1b07cu;break;
case 0xf1b07cu:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=0u; /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b07eu;break;
  case 0xf1b07eu:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=0u; /* store   r0,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][25])?(s.registers[s.bank][25]&~3u):s.registers[s.bank][25],s.registers[s.bank][0]));
   s.pc=0xf1b080u;break;
  case 0xf1b080u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=27u; /* movei   $f1b04e,r27 */
   s.registers[s.bank][27]=0xf1b04eu;
   s.pc=0xf1b086u;break;
  case 0xf1b086u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=28u; /* cmpq    $2,r28 */
   (void)sub(&s,s.registers[s.bank][28],0x2u);
   s.pc=0xf1b088u;break;
case 0xf1b088u:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=1u; /* jump    nz,(r27) */ if(condition(&s,1)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b08au;break;
  case 0xf1b08au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b08cu;break;
  case 0xf1b08cu:biwn_DSP_last_operands[0]=9u;biwn_DSP_last_operands[1]=30u; /* bset    $9,r30 */
   s.registers[s.bank][30]|=(1u<<9);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b08eu;break;
  case 0xf1b08eu:biwn_DSP_last_operands[0]=10u;biwn_DSP_last_operands[1]=30u; /* bset    $a,r30 */
   s.registers[s.bank][30]|=(1u<<10);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b090u;break;
  case 0xf1b090u:biwn_DSP_last_operands[0]=11u;biwn_DSP_last_operands[1]=30u; /* bset    $b,r30 */
   s.registers[s.bank][30]|=(1u<<11);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b092u;break;
  case 0xf1b092u:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=30u; /* bclr    $3,r30 */
   s.registers[s.bank][30]&=~(1u<<3);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b094u;break;
  case 0xf1b094u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=30u; /* bset    $4,r30 */
   s.registers[s.bank][30]|=(1u<<4);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b096u;break;
  case 0xf1b096u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=30u; /* bclr    $5,r30 */
   s.registers[s.bank][30]&=~(1u<<5);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b098u;break;
  case 0xf1b098u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=30u; /* bclr    $6,r30 */
   s.registers[s.bank][30]&=~(1u<<6);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b09au;break;
  case 0xf1b09au:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=30u; /* bclr    $e,r30 */
   s.registers[s.bank][30]&=~(1u<<14);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b09cu;break;
  case 0xf1b09cu:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=31u; /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b09eu;break;
  case 0xf1b09eu:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=30u; /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][29])?(s.registers[s.bank][29]&~3u):s.registers[s.bank][29],s.registers[s.bank][30]));
   s.pc=0xf1b0a0u;break;
  case 0xf1b0a0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b0a2u;break;
  case 0xf1b0a2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b0a4u;break;
  case 0xf1b0a4u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=25u; /* addq    $4,r25 */
   s.registers[s.bank][25]=add(&s,s.registers[s.bank][25],4u);
   s.pc=0xf1b0a6u;break;
  case 0xf1b0a6u:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=1u; /* load    (r25),r1 */
   CHECK(rd32(bus,&s,s.registers[s.bank][25]&~3u,&v));s.registers[s.bank][1]=v;
   s.pc=0xf1b0a8u;break;
  case 0xf1b0a8u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=2u; /* load    (r1),r2 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][2]=v;
   s.pc=0xf1b0aau;break;
  case 0xf1b0aau:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=1u; /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0acu;break;
  case 0xf1b0acu:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=3u; /* load    (r1),r3 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][3]=v;
   s.pc=0xf1b0aeu;break;
  case 0xf1b0aeu:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=1u; /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0b0u;break;
  case 0xf1b0b0u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=4u; /* load    (r1),r4 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][4]=v;
   s.pc=0xf1b0b2u;break;
  case 0xf1b0b2u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=1u; /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0b4u;break;
  case 0xf1b0b4u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=4u; /* shrq    $2,r4 */
   s.c=s.registers[s.bank][4]&1u;s.registers[s.bank][4]=s.registers[s.bank][4]>>2;zn(&s,s.registers[s.bank][4]);
   s.pc=0xf1b0b6u;break;
  case 0xf1b0b6u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=5u; /* load    (r2),r5 */
   CHECK(rd32(bus,&s,s.registers[s.bank][2]&~3u,&v));s.registers[s.bank][5]=v;
   s.pc=0xf1b0b8u;break;
  case 0xf1b0b8u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=4u; /* subq    $1,r4 */
   s.registers[s.bank][4]=sub(&s,s.registers[s.bank][4],1u);
   s.pc=0xf1b0bau;break;
  case 0xf1b0bau:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=5u; /* store   r5,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][3])?(s.registers[s.bank][3]&~3u):s.registers[s.bank][3],s.registers[s.bank][5]));
   s.pc=0xf1b0bcu;break;
  case 0xf1b0bcu:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=2u; /* addqt   $4,r2 */
   s.registers[s.bank][2]+=4u;
   s.pc=0xf1b0beu;break;
  case 0xf1b0beu:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=1u; /* jr      nz,00F1B0B6 */
   if(condition(&s,1)){pending=1;target=0xf1b0b6u;}
   s.pc=0xf1b0c0u;break;
  case 0xf1b0c0u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=3u; /* addqt   $4,r3 */
   s.registers[s.bank][3]+=4u;
   s.pc=0xf1b0c2u;break;
  case 0xf1b0c2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=6u; /* movei   $f1bb0c,r6 */
   s.registers[s.bank][6]=0xf1bb0cu;
   s.pc=0xf1b0c8u;break;
  case 0xf1b0c8u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=7u; /* load    (r1),r7 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][7]=v;
   s.pc=0xf1b0cau;break;
  case 0xf1b0cau:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=7u; /* store   r7,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][6])?(s.registers[s.bank][6]&~3u):s.registers[s.bank][6],s.registers[s.bank][7]));
   s.pc=0xf1b0ccu;break;
  case 0xf1b0ccu:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=1u; /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0ceu;break;
  case 0xf1b0ceu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=8u; /* movei   $f10002,r8 */
   s.registers[s.bank][8]=0xf10002u;
   s.pc=0xf1b0d4u;break;
  case 0xf1b0d4u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=9u; /* load    (r1),r9 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][9]=v;
   s.pc=0xf1b0d6u;break;
case 0xf1b0d6u:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=9u; /* storew  r9,(r8) */ CHECK(wr16(bus,&s,s.registers[s.bank][8],s.registers[s.bank][9]));s.pc=0xf1b0d8u;break;
  case 0xf1b0d8u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=1u; /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0dau;break;
  case 0xf1b0dau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=10u; /* movei   $f10000,r10 */
   s.registers[s.bank][10]=0xf10000u;
   s.pc=0xf1b0e0u;break;
  case 0xf1b0e0u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=11u; /* load    (r1),r11 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][11]=v;
   s.pc=0xf1b0e2u;break;
case 0xf1b0e2u:biwn_DSP_last_operands[0]=10u;biwn_DSP_last_operands[1]=11u; /* storew  r11,(r10) */ CHECK(wr16(bus,&s,s.registers[s.bank][10],s.registers[s.bank][11]));s.pc=0xf1b0e4u;break;
  case 0xf1b0e4u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=1u; /* addq    $4,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],4u);
   s.pc=0xf1b0e6u;break;
  case 0xf1b0e6u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=25u; /* addq    $4,r25 */
   s.registers[s.bank][25]=add(&s,s.registers[s.bank][25],4u);
   s.pc=0xf1b0e8u;break;
  case 0xf1b0e8u:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=1u; /* addq    $8,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],8u);
   s.pc=0xf1b0eau;break;
  case 0xf1b0eau:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=12u; /* load    (r25),r12 */
   CHECK(rd32(bus,&s,s.registers[s.bank][25]&~3u,&v));s.registers[s.bank][12]=v;
   s.pc=0xf1b0ecu;break;
  case 0xf1b0ecu:biwn_DSP_last_operands[0]=30u;biwn_DSP_last_operands[1]=12u; /* shlq    $2,r12 */
   s.c=s.registers[s.bank][12]>>31;s.registers[s.bank][12]=s.registers[s.bank][12]<<2;zn(&s,s.registers[s.bank][12]);
   s.pc=0xf1b0eeu;break;
  case 0xf1b0eeu:biwn_DSP_last_operands[0]=12u;biwn_DSP_last_operands[1]=1u; /* add     r12,r1 */
   s.registers[s.bank][1]=add(&s,s.registers[s.bank][1],s.registers[s.bank][12]);
   s.pc=0xf1b0f0u;break;
  case 0xf1b0f0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=13u; /* movei   $f1bb08,r13 */
   s.registers[s.bank][13]=0xf1bb08u;
   s.pc=0xf1b0f6u;break;
  case 0xf1b0f6u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=14u; /* load    (r1),r14 */
   CHECK(rd32(bus,&s,s.registers[s.bank][1]&~3u,&v));s.registers[s.bank][14]=v;
   s.pc=0xf1b0f8u;break;
  case 0xf1b0f8u:biwn_DSP_last_operands[0]=13u;biwn_DSP_last_operands[1]=14u; /* store   r14,(r13) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][13])?(s.registers[s.bank][13]&~3u):s.registers[s.bank][13],s.registers[s.bank][14]));
   s.pc=0xf1b0fau;break;
  case 0xf1b0fau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=15u; /* movei   $f1bd10,r15 */
   s.registers[s.bank][15]=0xf1bd10u;
   s.pc=0xf1b100u;break;
  case 0xf1b100u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=16u; /* movei   $fffffffc,r16 */
   s.registers[s.bank][16]=0xfffffffcu;
   s.pc=0xf1b106u;break;
  case 0xf1b106u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=17u; /* movei   $50,r17 */
   s.registers[s.bank][17]=0x50u;
   s.pc=0xf1b10cu;break;
  case 0xf1b10cu:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=18u; /* load    (r15),r18 */
   CHECK(rd32(bus,&s,s.registers[s.bank][15]&~3u,&v));s.registers[s.bank][18]=v;
   s.pc=0xf1b10eu;break;
  case 0xf1b10eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=18u; /* cmpq    $0,r18 */
   (void)sub(&s,s.registers[s.bank][18],0x0u);
   s.pc=0xf1b110u;break;
  case 0xf1b110u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=2u; /* jr      z,00F1B11A */
   if(condition(&s,2)){pending=1;target=0xf1b11au;}
   s.pc=0xf1b112u;break;
  case 0xf1b112u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b114u;break;
  case 0xf1b114u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=16u; /* store   r16,(r15) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][15])?(s.registers[s.bank][15]&~3u):s.registers[s.bank][15],s.registers[s.bank][16]));
   s.pc=0xf1b116u;break;
  case 0xf1b116u:biwn_DSP_last_operands[0]=26u;biwn_DSP_last_operands[1]=0u; /* jr      00F1B10C */
   if(condition(&s,0)){pending=1;target=0xf1b10cu;}
   s.pc=0xf1b118u;break;
  case 0xf1b118u:biwn_DSP_last_operands[0]=17u;biwn_DSP_last_operands[1]=15u; /* add     r17,r15 */
   s.registers[s.bank][15]=add(&s,s.registers[s.bank][15],s.registers[s.bank][17]);
   s.pc=0xf1b11au;break;
  case 0xf1b11au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=27u; /* movei   $f1b148,r27 */
   s.registers[s.bank][27]=0xf1b148u;
   s.pc=0xf1b120u;break;
  case 0xf1b120u:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=25u; /* subq    $8,r25 */
   s.registers[s.bank][25]=sub(&s,s.registers[s.bank][25],8u);
   s.pc=0xf1b122u;break;
case 0xf1b122u:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=0u; /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b124u;break;
  case 0xf1b124u:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=0u; /* store   r0,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][25])?(s.registers[s.bank][25]&~3u):s.registers[s.bank][25],s.registers[s.bank][0]));
   s.pc=0xf1b126u;break;
  case 0xf1b126u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=31u; /* movei   $f1b010,r31 */
   s.registers[s.bank][31]=0xf1b010u;
   s.pc=0xf1b12cu;break;
case 0xf1b12cu:biwn_DSP_last_operands[0]=31u;biwn_DSP_last_operands[1]=31u; /* moveta  r31,r31 */ s.registers[1u-s.bank][31]=s.registers[s.bank][31];s.pc=0xf1b12eu;break;
  case 0xf1b12eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=29u; /* movei   $f1a100,r29 */
   s.registers[s.bank][29]=0xf1a100u;
   s.pc=0xf1b134u;break;
  case 0xf1b134u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=30u; /* load    (r29),r30 */
   CHECK(rd32(bus,&s,s.registers[s.bank][29]&~3u,&v));s.registers[s.bank][30]=v;
   s.pc=0xf1b136u;break;
  case 0xf1b136u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=30u; /* bset    $4,r30 */
   s.registers[s.bank][30]|=(1u<<4);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b138u;break;
  case 0xf1b138u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=30u; /* bclr    $5,r30 */
   s.registers[s.bank][30]&=~(1u<<5);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b13au;break;
  case 0xf1b13au:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=30u; /* bclr    $6,r30 */
   s.registers[s.bank][30]&=~(1u<<6);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b13cu;break;
  case 0xf1b13cu:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=30u; /* bclr    $e,r30 */
   s.registers[s.bank][30]&=~(1u<<14);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b13eu;break;
  case 0xf1b13eu:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=30u; /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][29])?(s.registers[s.bank][29]&~3u):s.registers[s.bank][29],s.registers[s.bank][30]));
   s.pc=0xf1b140u;break;
  case 0xf1b140u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b142u;break;
  case 0xf1b142u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b144u;break;
  case 0xf1b148u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* movei   $f1bd10,r0 */
   s.registers[s.bank][0]=0xf1bd10u;
   s.pc=0xf1b14eu;break;
  case 0xf1b14eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=1u; /* movei   $f1b1dc,r1 */
   s.registers[s.bank][1]=0xf1b1dcu;
   s.pc=0xf1b154u;break;
  case 0xf1b154u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=2u; /* movei   $f1bb54,r2 */
   s.registers[s.bank][2]=0xf1bb54u;
   s.pc=0xf1b15au;break;
  case 0xf1b15au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=3u; /* movei   $4c,r3 */
   s.registers[s.bank][3]=0x4cu;
   s.pc=0xf1b160u;break;
  case 0xf1b160u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=10u; /* movei   $f1b1ca,r10 */
   s.registers[s.bank][10]=0xf1b1cau;
   s.pc=0xf1b166u;break;
  case 0xf1b166u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=13u; /* movei   $f1b2dc,r13 */
   s.registers[s.bank][13]=0xf1b2dcu;
   s.pc=0xf1b16cu;break;
  case 0xf1b16cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=11u; /* movei   $ff,r11 */
   s.registers[s.bank][11]=0xffu;
   s.pc=0xf1b172u;break;
  case 0xf1b172u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=14u; /* movei   $7fff,r14 */
   s.registers[s.bank][14]=0x7fffu;
   s.pc=0xf1b178u;break;
  case 0xf1b178u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=15u; /* movei   $fffffffc,r15 */
   s.registers[s.bank][15]=0xfffffffcu;
   s.pc=0xf1b17eu;break;
  case 0xf1b17eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=19u; /* movei   $7fffff,r19 */
   s.registers[s.bank][19]=0x7fffffu;
   s.pc=0xf1b184u;break;
  case 0xf1b184u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=18u; /* movei   $f1d200,r18 */
   s.registers[s.bank][18]=0xf1d200u;
   s.pc=0xf1b18au;break;
  case 0xf1b18au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=17u; /* movei   $f1bb08,r17 */
   s.registers[s.bank][17]=0xf1bb08u;
   s.pc=0xf1b190u;break;
  case 0xf1b190u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=16u; /* movei   $f1bb04,r16 */
   s.registers[s.bank][16]=0xf1bb04u;
   s.pc=0xf1b196u;break;
  case 0xf1b196u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=21u; /* moveq   0,r21 */
   s.registers[s.bank][21]=0u;
   s.pc=0xf1b198u;break;
  case 0xf1b198u:biwn_DSP_last_operands[0]=16u;biwn_DSP_last_operands[1]=21u; /* store   r21,(r16) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][16])?(s.registers[s.bank][16]&~3u):s.registers[s.bank][16],s.registers[s.bank][21]));
   s.pc=0xf1b19au;break;
  case 0xf1b19au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=9u; /* movei   $f1a148,r9 */
   s.registers[s.bank][9]=0xf1a148u;
   s.pc=0xf1b1a0u;break;
  case 0xf1b1a0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=20u; /* movei   $f1a100,r20 */
   s.registers[s.bank][20]=0xf1a100u;
   s.pc=0xf1b1a6u;break;
  case 0xf1b1a6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=24u; /* movei   $f1baf8,r24 */
   s.registers[s.bank][24]=0xf1baf8u;
   s.pc=0xf1b1acu;break;
  case 0xf1b1acu:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=29u; /* load    (r20),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][20]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b1aeu;break;
  case 0xf1b1aeu:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=29u; /* bset    $e,r29 */
   s.registers[s.bank][29]|=(1u<<14);
   zn(&s,s.registers[s.bank][29]);
   s.pc=0xf1b1b0u;break;
  case 0xf1b1b0u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=29u; /* bset    $5,r29 */
   s.registers[s.bank][29]|=(1u<<5);
   zn(&s,s.registers[s.bank][29]);
   s.pc=0xf1b1b2u;break;
  case 0xf1b1b2u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=29u; /* bset    $6,r29 */
   s.registers[s.bank][29]|=(1u<<6);
   zn(&s,s.registers[s.bank][29]);
   s.pc=0xf1b1b4u;break;
  case 0xf1b1b4u:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=29u; /* store   r29,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][29]));
   s.pc=0xf1b1b6u;break;
  case 0xf1b1b6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b1b8u;break;
  case 0xf1b1b8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b1bau;break;
  case 0xf1b1bau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=28u; /* moveq   0,r28 */
   s.registers[s.bank][28]=0u;
   s.pc=0xf1b1bcu;break;
  case 0xf1b1bcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=1u; /* movei   $f1a118,r1 */
   s.registers[s.bank][1]=0xf1a118u;
   s.pc=0xf1b1c2u;break;
  case 0xf1b1c2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* movei   $fffffe00,r0 */
   s.registers[s.bank][0]=0xfffffe00u;
   s.pc=0xf1b1c8u;break;
  case 0xf1b1c8u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=0u; /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][1])?(s.registers[s.bank][1]&~3u):s.registers[s.bank][1],s.registers[s.bank][0]));
   s.pc=0xf1b1cau;break;
case 0xf1b1cau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=15u; /* movefa  r0,r15 */ s.registers[s.bank][15]=s.registers[1u-s.bank][0];s.pc=0xf1b1ccu;break;
  case 0xf1b1ccu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=26u; /* moveq   0,r26 */
   s.registers[s.bank][26]=0u;
   s.pc=0xf1b1ceu;break;
  case 0xf1b1ceu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=9u; /* moveq   0,r9 */
   s.registers[s.bank][9]=0u;
   s.pc=0xf1b1d0u;break;
case 0xf1b1d0u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=27u; /* movefa  r1,r27 */ s.registers[s.bank][27]=s.registers[1u-s.bank][1];s.pc=0xf1b1d2u;break;
  case 0xf1b1d2u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=16u; /* load    (r15),r16 */
   CHECK(rd32(bus,&s,s.registers[s.bank][15]&~3u,&v));s.registers[s.bank][16]=v;
   s.pc=0xf1b1d4u;break;
case 0xf1b1d4u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=14u; /* movefa  r2,r14 */ s.registers[s.bank][14]=s.registers[1u-s.bank][2];s.pc=0xf1b1d6u;break;
case 0xf1b1d6u:biwn_DSP_last_operands[0]=16u;biwn_DSP_last_operands[1]=25u; /* load    (r14+r16),r25 */ CHECK(rd32(bus,&s,s.registers[s.bank][14]+s.registers[s.bank][16],&v));s.registers[s.bank][25]=v;s.pc=0xf1b1d8u;break;
case 0xf1b1d8u:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=0u; /* jump    (r25) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][25];}s.pc=0xf1b1dau;break;
  case 0xf1b1dau:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=15u; /* addq    $4,r15 */
   s.registers[s.bank][15]=add(&s,s.registers[s.bank][15],4u);
   s.pc=0xf1b1dcu;break;
case 0xf1b1dcu:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=1u; /* movefa  r3,r1 */ s.registers[s.bank][1]=s.registers[1u-s.bank][3];s.pc=0xf1b1deu;break;
  case 0xf1b1deu:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=0u; /* jr      00F1B1D2 */
   if(condition(&s,0)){pending=1;target=0xf1b1d2u;}
   s.pc=0xf1b1e0u;break;
  case 0xf1b1e0u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=15u; /* add     r1,r15 */
   s.registers[s.bank][15]=add(&s,s.registers[s.bank][15],s.registers[s.bank][1]);
   s.pc=0xf1b1e2u;break;
  case 0xf1b1e2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=2u; /* movei   $f1bb00,r2 */
   s.registers[s.bank][2]=0xf1bb00u;
   s.pc=0xf1b1e8u;break;
  case 0xf1b1e8u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=26u; /* sharq   $f,r26 */
   s.c=s.registers[s.bank][26]&1u;s.registers[s.bank][26]=sar(s.registers[s.bank][26],15);zn(&s,s.registers[s.bank][26]);
   s.pc=0xf1b1eau;break;
  case 0xf1b1eau:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=1u; /* load    (r2),r1 */
   CHECK(rd32(bus,&s,s.registers[s.bank][2]&~3u,&v));s.registers[s.bank][1]=v;
   s.pc=0xf1b1ecu;break;
  case 0xf1b1ecu:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=9u; /* sharq   $f,r9 */
   s.c=s.registers[s.bank][9]&1u;s.registers[s.bank][9]=sar(s.registers[s.bank][9],15);zn(&s,s.registers[s.bank][9]);
   s.pc=0xf1b1eeu;break;
  case 0xf1b1eeu:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=26u; /* imult   r1,r26 */
   s.registers[s.bank][26]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][26])*(int32_t)sx16(s.registers[s.bank][1]));
   zn(&s,s.registers[s.bank][26]);
   s.pc=0xf1b1f0u;break;
  case 0xf1b1f0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=2u; /* movei   $f1bb10,r2 */
   s.registers[s.bank][2]=0xf1bb10u;
   s.pc=0xf1b1f6u;break;
  case 0xf1b1f6u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=28u; /* shlq    $3,r28 */
   s.c=s.registers[s.bank][28]>>31;s.registers[s.bank][28]=s.registers[s.bank][28]<<3;zn(&s,s.registers[s.bank][28]);
   s.pc=0xf1b1f8u;break;
  case 0xf1b1f8u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=9u; /* imult   r1,r9 */
   s.registers[s.bank][9]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][9])*(int32_t)sx16(s.registers[s.bank][1]));
   zn(&s,s.registers[s.bank][9]);
   s.pc=0xf1b1fau;break;
  case 0xf1b1fau:biwn_DSP_last_operands[0]=28u;biwn_DSP_last_operands[1]=2u; /* add     r28,r2 */
   s.registers[s.bank][2]=add(&s,s.registers[s.bank][2],s.registers[s.bank][28]);
   s.pc=0xf1b1fcu;break;
  case 0xf1b1fcu:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=26u; /* sharq   $f,r26 */
   s.c=s.registers[s.bank][26]&1u;s.registers[s.bank][26]=sar(s.registers[s.bank][26],15);zn(&s,s.registers[s.bank][26]);
   s.pc=0xf1b1feu;break;
  case 0xf1b1feu:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=28u; /* shrq    $3,r28 */
   s.c=s.registers[s.bank][28]&1u;s.registers[s.bank][28]=s.registers[s.bank][28]>>3;zn(&s,s.registers[s.bank][28]);
   s.pc=0xf1b200u;break;
  case 0xf1b200u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=9u; /* sharq   $f,r9 */
   s.c=s.registers[s.bank][9]&1u;s.registers[s.bank][9]=sar(s.registers[s.bank][9],15);zn(&s,s.registers[s.bank][9]);
   s.pc=0xf1b202u;break;
  case 0xf1b202u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=26u; /* store   r26,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][2])?(s.registers[s.bank][2]&~3u):s.registers[s.bank][2],s.registers[s.bank][26]));
   s.pc=0xf1b204u;break;
  case 0xf1b204u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=28u; /* addq    $1,r28 */
   s.registers[s.bank][28]=add(&s,s.registers[s.bank][28],1u);
   s.pc=0xf1b206u;break;
  case 0xf1b206u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=2u; /* addq    $4,r2 */
   s.registers[s.bank][2]=add(&s,s.registers[s.bank][2],4u);
   s.pc=0xf1b208u;break;
  case 0xf1b208u:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=28u; /* bclr    $3,r28 */
   s.registers[s.bank][28]&=~(1u<<3);
   zn(&s,s.registers[s.bank][28]);
   s.pc=0xf1b20au;break;
  case 0xf1b20au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* moveq   0,r0 */
   s.registers[s.bank][0]=0u;
   s.pc=0xf1b20cu;break;
  case 0xf1b20cu:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=9u; /* store   r9,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][2])?(s.registers[s.bank][2]&~3u):s.registers[s.bank][2],s.registers[s.bank][9]));
   s.pc=0xf1b20eu;break;
  case 0xf1b20eu:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=0u; /* subq    $1,r0 */
   s.registers[s.bank][0]=sub(&s,s.registers[s.bank][0],1u);
   s.pc=0xf1b210u;break;
case 0xf1b210u:biwn_DSP_last_operands[0]=21u;biwn_DSP_last_operands[1]=2u; /* movefa  r21,r2 */ s.registers[s.bank][2]=s.registers[1u-s.bank][21];s.pc=0xf1b212u;break;
  case 0xf1b212u:biwn_DSP_last_operands[0]=28u;biwn_DSP_last_operands[1]=2u; /* cmp     r28,r2 */
   (void)sub(&s,s.registers[s.bank][2],s.registers[s.bank][28]);
   s.pc=0xf1b214u;break;
  case 0xf1b214u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=0u; /* addqt   $1,r0 */
   s.registers[s.bank][0]+=1u;
   s.pc=0xf1b216u;break;
  case 0xf1b216u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=2u; /* jr      z,00F1B212 */
   if(condition(&s,2)){pending=1;target=0xf1b212u;}
   s.pc=0xf1b218u;break;
case 0xf1b218u:biwn_DSP_last_operands[0]=21u;biwn_DSP_last_operands[1]=2u; /* movefa  r21,r2 */ s.registers[s.bank][2]=s.registers[1u-s.bank][21];s.pc=0xf1b21au;break;
case 0xf1b21au:biwn_DSP_last_operands[0]=24u;biwn_DSP_last_operands[1]=1u; /* movefa  r24,r1 */ s.registers[s.bank][1]=s.registers[1u-s.bank][24];s.pc=0xf1b21cu;break;
case 0xf1b21cu:biwn_DSP_last_operands[0]=10u;biwn_DSP_last_operands[1]=27u; /* movefa  r10,r27 */ s.registers[s.bank][27]=s.registers[1u-s.bank][10];s.pc=0xf1b21eu;break;
case 0xf1b21eu:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=0u; /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b220u;break;
  case 0xf1b220u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=0u; /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][1])?(s.registers[s.bank][1]&~3u):s.registers[s.bank][1],s.registers[s.bank][0]));
   s.pc=0xf1b222u;break;
case 0xf1b2f6u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=2u; /* load    (r15+$8),r2 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+8u,&v));s.registers[s.bank][2]=v;s.pc=0xf1b2f8u;break;
case 0xf1b2f8u:biwn_DSP_last_operands[0]=11u;biwn_DSP_last_operands[1]=24u; /* movefa  r11,r24 */ s.registers[s.bank][24]=s.registers[1u-s.bank][11];s.pc=0xf1b2fau;break;
case 0xf1b2fau:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=5u; /* load    (r15+$14),r5 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+20u,&v));s.registers[s.bank][5]=v;s.pc=0xf1b2fcu;break;
case 0xf1b2fcu:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=3u; /* load    (r15+$c),r3 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+12u,&v));s.registers[s.bank][3]=v;s.pc=0xf1b2feu;break;
  case 0xf1b2feu:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=5u; /* add     r2,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],s.registers[s.bank][2]);
   s.pc=0xf1b300u;break;
  case 0xf1b300u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=0u; /* load    (r15),r0 */
   CHECK(rd32(bus,&s,s.registers[s.bank][15]&~3u,&v));s.registers[s.bank][0]=v;
   s.pc=0xf1b302u;break;
  case 0xf1b302u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=3u; /* cmp     r5,r3 */
   (void)sub(&s,s.registers[s.bank][3],s.registers[s.bank][5]);
   s.pc=0xf1b304u;break;
case 0xf1b304u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=4u; /* load    (r15+$10),r4 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+16u,&v));s.registers[s.bank][4]=v;s.pc=0xf1b306u;break;
  case 0xf1b306u:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=20u; /* jr      nn,00F1B318 */
   if(condition(&s,20)){pending=1;target=0xf1b318u;}
   s.pc=0xf1b308u;break;
  case 0xf1b308u:biwn_DSP_last_operands[0]=31u;biwn_DSP_last_operands[1]=0u; /* btst    $1f,r0 */
   s.z=((~s.registers[s.bank][0])>>31)&1u;
   s.pc=0xf1b30au;break;
  case 0xf1b318u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=4u; /* move    r5,r4 */
   s.registers[s.bank][4]=s.registers[s.bank][5];
   s.pc=0xf1b31au;break;
case 0xf1b31au:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=5u; /* store   r5,(r15+$14) */ CHECK(wr32(bus,&s,s.registers[s.bank][15]+20u,s.registers[s.bank][5]));s.pc=0xf1b31cu;break;
  case 0xf1b31cu:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=5u; /* shrq    $8,r5 */
   s.c=s.registers[s.bank][5]&1u;s.registers[s.bank][5]=s.registers[s.bank][5]>>8;zn(&s,s.registers[s.bank][5]);
   s.pc=0xf1b31eu;break;
  case 0xf1b31eu:biwn_DSP_last_operands[0]=24u;biwn_DSP_last_operands[1]=4u; /* and     r24,r4 */
   s.registers[s.bank][4]&=s.registers[s.bank][24];
   zn(&s,s.registers[s.bank][4]);
   s.pc=0xf1b320u;break;
case 0xf1b320u:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=20u; /* movefa  r14,r20 */ s.registers[s.bank][20]=s.registers[1u-s.bank][14];s.pc=0xf1b322u;break;
case 0xf1b322u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=1u; /* load    (r15+$4),r1 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+4u,&v));s.registers[s.bank][1]=v;s.pc=0xf1b324u;break;
  case 0xf1b324u:biwn_DSP_last_operands[0]=24u;biwn_DSP_last_operands[1]=6u; /* move    r24,r6 */
   s.registers[s.bank][6]=s.registers[s.bank][24];
   s.pc=0xf1b326u;break;
  case 0xf1b326u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=5u; /* add     r1,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],s.registers[s.bank][1]);
   s.pc=0xf1b328u;break;
  case 0xf1b328u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=6u; /* sub     r4,r6 */
   s.registers[s.bank][6]=sub(&s,s.registers[s.bank][6],s.registers[s.bank][4]);
   s.pc=0xf1b32au;break;
case 0xf1b32au:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=13u; /* loadb   (r5),r13 */ CHECK(rd8(bus,&s,s.registers[s.bank][5],&v));s.registers[s.bank][13]=v;s.pc=0xf1b32cu;break;
  case 0xf1b32cu:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=5u; /* addq    $1,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],1u);
   s.pc=0xf1b32eu;break;
case 0xf1b32eu:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=7u; /* loadb   (r5),r7 */ CHECK(rd8(bus,&s,s.registers[s.bank][5],&v));s.registers[s.bank][7]=v;s.pc=0xf1b330u;break;
  case 0xf1b330u:biwn_DSP_last_operands[0]=13u;biwn_DSP_last_operands[1]=1u; /* move    r13,r1 */
   s.registers[s.bank][1]=s.registers[s.bank][13];
   s.pc=0xf1b332u;break;
  case 0xf1b332u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=13u; /* bclr    $7,r13 */
   s.registers[s.bank][13]&=~(1u<<7);
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b334u;break;
  case 0xf1b334u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=1u; /* btst    $7,r1 */
   s.z=((~s.registers[s.bank][1])>>7)&1u;
   s.pc=0xf1b336u;break;
  case 0xf1b336u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=2u; /* jr      z,00F1B33C */
   if(condition(&s,2)){pending=1;target=0xf1b33cu;}
   s.pc=0xf1b338u;break;
  case 0xf1b338u:biwn_DSP_last_operands[0]=13u;biwn_DSP_last_operands[1]=13u; /* mult    r13,r13 */
   s.registers[s.bank][13]=(s.registers[s.bank][13]&0xffffu)*(s.registers[s.bank][13]&0xffffu);
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b33au;break;
  case 0xf1b33au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=13u; /* neg     r13 */
   s.registers[s.bank][13]=sub(&s,0,s.registers[s.bank][13]);
   s.pc=0xf1b33cu;break;
  case 0xf1b33cu:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=2u; /* move    r7,r2 */
   s.registers[s.bank][2]=s.registers[s.bank][7];
   s.pc=0xf1b33eu;break;
  case 0xf1b33eu:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=7u; /* bclr    $7,r7 */
   s.registers[s.bank][7]&=~(1u<<7);
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b340u;break;
  case 0xf1b340u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=2u; /* btst    $7,r2 */
   s.z=((~s.registers[s.bank][2])>>7)&1u;
   s.pc=0xf1b342u;break;
  case 0xf1b342u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=2u; /* jr      z,00F1B348 */
   if(condition(&s,2)){pending=1;target=0xf1b348u;}
   s.pc=0xf1b344u;break;
  case 0xf1b344u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=7u; /* mult    r7,r7 */
   s.registers[s.bank][7]=(s.registers[s.bank][7]&0xffffu)*(s.registers[s.bank][7]&0xffffu);
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b346u;break;
  case 0xf1b346u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=7u; /* neg     r7 */
   s.registers[s.bank][7]=sub(&s,0,s.registers[s.bank][7]);
   s.pc=0xf1b348u;break;
  case 0xf1b348u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=13u; /* imult   r6,r13 */
   s.registers[s.bank][13]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][13])*(int32_t)sx16(s.registers[s.bank][6]));
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b34au;break;
  case 0xf1b34au:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=7u; /* imult   r4,r7 */
   s.registers[s.bank][7]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][7])*(int32_t)sx16(s.registers[s.bank][4]));
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b34cu;break;
  case 0xf1b34cu:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=13u; /* add     r7,r13 */
   s.registers[s.bank][13]=add(&s,s.registers[s.bank][13],s.registers[s.bank][7]);
   s.pc=0xf1b34eu;break;
case 0xf1b34eu:biwn_DSP_last_operands[0]=18u;biwn_DSP_last_operands[1]=19u; /* load    (r15+$48),r19 */ CHECK(rd32(bus,&s,s.registers[s.bank][15]+72u,&v));s.registers[s.bank][19]=v;s.pc=0xf1b350u;break;
  case 0xf1b350u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=13u; /* sharq   $7,r13 */
   s.c=s.registers[s.bank][13]&1u;s.registers[s.bank][13]=sar(s.registers[s.bank][13],7);zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b352u;break;
  case 0xf1b352u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=13u; /* imult   r0,r13 */
   s.registers[s.bank][13]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][13])*(int32_t)sx16(s.registers[s.bank][0]));
   zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b354u;break;
  case 0xf1b354u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=13u; /* sharq   $f,r13 */
   s.c=s.registers[s.bank][13]&1u;s.registers[s.bank][13]=sar(s.registers[s.bank][13],15);zn(&s,s.registers[s.bank][13]);
   s.pc=0xf1b356u;break;
  case 0xf1b356u:biwn_DSP_last_operands[0]=19u;biwn_DSP_last_operands[1]=20u; /* sub     r19,r20 */
   s.registers[s.bank][20]=sub(&s,s.registers[s.bank][20],s.registers[s.bank][19]);
   s.pc=0xf1b358u;break;
  case 0xf1b358u:biwn_DSP_last_operands[0]=13u;biwn_DSP_last_operands[1]=19u; /* imult   r13,r19 */
   s.registers[s.bank][19]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][19])*(int32_t)sx16(s.registers[s.bank][13]));
   zn(&s,s.registers[s.bank][19]);
   s.pc=0xf1b35au;break;
  case 0xf1b35au:biwn_DSP_last_operands[0]=13u;biwn_DSP_last_operands[1]=20u; /* imult   r13,r20 */
   s.registers[s.bank][20]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.bank][20])*(int32_t)sx16(s.registers[s.bank][13]));
   zn(&s,s.registers[s.bank][20]);
   s.pc=0xf1b35cu;break;
  case 0xf1b35cu:biwn_DSP_last_operands[0]=19u;biwn_DSP_last_operands[1]=9u; /* add     r19,r9 */
   s.registers[s.bank][9]=add(&s,s.registers[s.bank][9],s.registers[s.bank][19]);
   s.pc=0xf1b35eu;break;
case 0xf1b35eu:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=0u; /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b360u;break;
  case 0xf1b360u:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=26u; /* add     r20,r26 */
   s.registers[s.bank][26]=add(&s,s.registers[s.bank][26],s.registers[s.bank][20]);
   s.pc=0xf1b362u;break;
  case 0xf1b77au:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=30u; /* load    (r20),r30 */
   CHECK(rd32(bus,&s,s.registers[s.bank][20]&~3u,&v));s.registers[s.bank][30]=v;
   s.pc=0xf1b77cu;break;
  case 0xf1b77cu:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=21u; /* shlq    $3,r21 */
   s.c=s.registers[s.bank][21]>>31;s.registers[s.bank][21]=s.registers[s.bank][21]<<3;zn(&s,s.registers[s.bank][21]);
   s.pc=0xf1b77eu;break;
  case 0xf1b77eu:biwn_DSP_last_operands[0]=10u;biwn_DSP_last_operands[1]=30u; /* bset    $a,r30 */
   s.registers[s.bank][30]|=(1u<<10);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b780u;break;
  case 0xf1b780u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=28u; /* movei   $f1bb10,r28 */
   s.registers[s.bank][28]=0xf1bb10u;
   s.pc=0xf1b786u;break;
  case 0xf1b786u:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=30u; /* bclr    $3,r30 */
   s.registers[s.bank][30]&=~(1u<<3);
   zn(&s,s.registers[s.bank][30]);
   s.pc=0xf1b788u;break;
  case 0xf1b788u:biwn_DSP_last_operands[0]=21u;biwn_DSP_last_operands[1]=28u; /* add     r21,r28 */
   s.registers[s.bank][28]=add(&s,s.registers[s.bank][28],s.registers[s.bank][21]);
   s.pc=0xf1b78au;break;
  case 0xf1b78au:biwn_DSP_last_operands[0]=28u;biwn_DSP_last_operands[1]=29u; /* load    (r28),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][28]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b78cu;break;
  case 0xf1b78cu:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=21u; /* shrq    $3,r21 */
   s.c=s.registers[s.bank][21]&1u;s.registers[s.bank][21]=s.registers[s.bank][21]>>3;zn(&s,s.registers[s.bank][21]);
   s.pc=0xf1b78eu;break;
  case 0xf1b78eu:biwn_DSP_last_operands[0]=9u;biwn_DSP_last_operands[1]=29u; /* store   r29,(r9) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][9])?(s.registers[s.bank][9]&~3u):s.registers[s.bank][9],s.registers[s.bank][29]));
   s.pc=0xf1b790u;break;
  case 0xf1b790u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=28u; /* addq    $4,r28 */
   s.registers[s.bank][28]=add(&s,s.registers[s.bank][28],4u);
   s.pc=0xf1b792u;break;
  case 0xf1b792u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=9u; /* addq    $4,r9 */
   s.registers[s.bank][9]=add(&s,s.registers[s.bank][9],4u);
   s.pc=0xf1b794u;break;
  case 0xf1b794u:biwn_DSP_last_operands[0]=28u;biwn_DSP_last_operands[1]=29u; /* load    (r28),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][28]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b796u;break;
  case 0xf1b796u:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=21u; /* addq    $1,r21 */
   s.registers[s.bank][21]=add(&s,s.registers[s.bank][21],1u);
   s.pc=0xf1b798u;break;
  case 0xf1b798u:biwn_DSP_last_operands[0]=9u;biwn_DSP_last_operands[1]=29u; /* store   r29,(r9) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][9])?(s.registers[s.bank][9]&~3u):s.registers[s.bank][9],s.registers[s.bank][29]));
   s.pc=0xf1b79au;break;
  case 0xf1b79au:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=21u; /* bclr    $3,r21 */
   s.registers[s.bank][21]&=~(1u<<3);
   zn(&s,s.registers[s.bank][21]);
   s.pc=0xf1b79cu;break;
  case 0xf1b79cu:biwn_DSP_last_operands[0]=31u;biwn_DSP_last_operands[1]=29u; /* load    (r31),r29 */
   CHECK(rd32(bus,&s,s.registers[s.bank][31]&~3u,&v));s.registers[s.bank][29]=v;
   s.pc=0xf1b79eu;break;
  case 0xf1b79eu:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=9u; /* subq    $4,r9 */
   s.registers[s.bank][9]=sub(&s,s.registers[s.bank][9],4u);
   s.pc=0xf1b7a0u;break;
  case 0xf1b7a0u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=29u; /* addq    $2,r29 */
   s.registers[s.bank][29]=add(&s,s.registers[s.bank][29],2u);
   s.pc=0xf1b7a2u;break;
  case 0xf1b7a2u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=31u; /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b7a4u;break;
case 0xf1b7a4u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=0u; /* jump    (r29) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][29];}s.pc=0xf1b7a6u;break;
  case 0xf1b7a6u:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=30u; /* store   r30,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][30]));
   s.pc=0xf1b7a8u;break;
  case 0xf1b7a8u:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=22u; /* load    (r20),r22 */
   CHECK(rd32(bus,&s,s.registers[s.bank][20]&~3u,&v));s.registers[s.bank][22]=v;
   s.pc=0xf1b7aau;break;
  case 0xf1b7aau:biwn_DSP_last_operands[0]=11u;biwn_DSP_last_operands[1]=22u; /* bset    $b,r22 */
   s.registers[s.bank][22]|=(1u<<11);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7acu;break;
  case 0xf1b7acu:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=22u; /* bclr    $3,r22 */
   s.registers[s.bank][22]&=~(1u<<3);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7aeu;break;
  case 0xf1b7aeu:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=22u; /* bclr    $6,r22 */
   s.registers[s.bank][22]&=~(1u<<6);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7b0u;break;
  case 0xf1b7b0u:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=22u; /* bclr    $e,r22 */
   s.registers[s.bank][22]&=~(1u<<14);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b7b2u;break;
  case 0xf1b7b2u:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=22u; /* store   r22,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][22]));
   s.pc=0xf1b7b4u;break;
  case 0xf1b7b4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b7b6u;break;
  case 0xf1b7b6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b7b8u;break;
  case 0xf1b7b8u:biwn_DSP_last_operands[0]=16u;biwn_DSP_last_operands[1]=4u; /* load    (r16),r4 */
   CHECK(rd32(bus,&s,s.registers[s.bank][16]&~3u,&v));s.registers[s.bank][4]=v;
   s.pc=0xf1b7bau;break;
  case 0xf1b7bau:biwn_DSP_last_operands[0]=17u;biwn_DSP_last_operands[1]=5u; /* load    (r17),r5 */
   CHECK(rd32(bus,&s,s.registers[s.bank][17]&~3u,&v));s.registers[s.bank][5]=v;
   s.pc=0xf1b7bcu;break;
  case 0xf1b7bcu:biwn_DSP_last_operands[0]=1u;biwn_DSP_last_operands[1]=4u; /* addq    $1,r4 */
   s.registers[s.bank][4]=add(&s,s.registers[s.bank][4],1u);
   s.pc=0xf1b7beu;break;
  case 0xf1b7beu:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=6u; /* load    (r5),r6 */
   CHECK(rd32(bus,&s,s.registers[s.bank][5]&~3u,&v));s.registers[s.bank][6]=v;
   s.pc=0xf1b7c0u;break;
  case 0xf1b7c0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=8u; /* movei   $f1b81c,r8 */
   s.registers[s.bank][8]=0xf1b81cu;
   s.pc=0xf1b7c6u;break;
  case 0xf1b7c6u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=6u; /* cmp     r4,r6 */
   (void)sub(&s,s.registers[s.bank][6],s.registers[s.bank][4]);
   s.pc=0xf1b7c8u;break;
  case 0xf1b7c8u:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=24u; /* jr      n,00F1B7D0 */
   if(condition(&s,24)){pending=1;target=0xf1b7d0u;}
   s.pc=0xf1b7cau;break;
  case 0xf1b7cau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b7ccu;break;
  case 0xf1b7d0u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=5u; /* addq    $4,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],4u);
   s.pc=0xf1b7d2u;break;
  case 0xf1b7d2u:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=6u; /* load    (r5),r6 */
   CHECK(rd32(bus,&s,s.registers[s.bank][5]&~3u,&v));s.registers[s.bank][6]=v;
   s.pc=0xf1b7d4u;break;
  case 0xf1b7d4u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=5u; /* addq    $4,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],4u);
   s.pc=0xf1b7d6u;break;
  case 0xf1b7d6u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=7u; /* move    r6,r7 */
   s.registers[s.bank][7]=s.registers[s.bank][6];
   s.pc=0xf1b7d8u;break;
  case 0xf1b7d8u:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=7u; /* shlq    $3,r7 */
   s.c=s.registers[s.bank][7]>>31;s.registers[s.bank][7]=s.registers[s.bank][7]<<3;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b7dau;break;
  case 0xf1b7dau:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=7u; /* shrq    $1d,r7 */
   s.c=s.registers[s.bank][7]&1u;s.registers[s.bank][7]=s.registers[s.bank][7]>>29;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b7dcu;break;
  case 0xf1b7dcu:biwn_DSP_last_operands[0]=30u;biwn_DSP_last_operands[1]=7u; /* shlq    $2,r7 */
   s.c=s.registers[s.bank][7]>>31;s.registers[s.bank][7]=s.registers[s.bank][7]<<2;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b7deu;break;
  case 0xf1b7deu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=23u; /* movei   $f1bc30,r23 */
   s.registers[s.bank][23]=0xf1bc30u;
   s.pc=0xf1b7e4u;break;
  case 0xf1b7e4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=25u; /* movei   $f1bc70,r25 */
   s.registers[s.bank][25]=0xf1bc70u;
   s.pc=0xf1b7eau;break;
  case 0xf1b7eau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=26u; /* movei   $f1bcac,r26 */
   s.registers[s.bank][26]=0xf1bcacu;
   s.pc=0xf1b7f0u;break;
  case 0xf1b7f0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=27u; /* movei   $f1bcec,r27 */
   s.registers[s.bank][27]=0xf1bcecu;
   s.pc=0xf1b7f6u;break;
  case 0xf1b7f6u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=23u; /* add     r7,r23 */
   s.registers[s.bank][23]=add(&s,s.registers[s.bank][23],s.registers[s.bank][7]);
   s.pc=0xf1b7f8u;break;
  case 0xf1b7f8u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=26u; /* add     r7,r26 */
   s.registers[s.bank][26]=add(&s,s.registers[s.bank][26],s.registers[s.bank][7]);
   s.pc=0xf1b7fau;break;
  case 0xf1b7fau:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=23u; /* store   r23,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][25])?(s.registers[s.bank][25]&~3u):s.registers[s.bank][25],s.registers[s.bank][23]));
   s.pc=0xf1b7fcu;break;
  case 0xf1b7fcu:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=26u; /* store   r26,(r27) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][27])?(s.registers[s.bank][27]&~3u):s.registers[s.bank][27],s.registers[s.bank][26]));
   s.pc=0xf1b7feu;break;
  case 0xf1b7feu:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=7u; /* shrq    $2,r7 */
   s.c=s.registers[s.bank][7]&1u;s.registers[s.bank][7]=s.registers[s.bank][7]>>2;zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b800u;break;
  case 0xf1b800u:biwn_DSP_last_operands[0]=3u;biwn_DSP_last_operands[1]=27u; /* move    r3,r27 */
   s.registers[s.bank][27]=s.registers[s.bank][3];
   s.pc=0xf1b802u;break;
  case 0xf1b802u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=27u; /* addq    $4,r27 */
   s.registers[s.bank][27]=add(&s,s.registers[s.bank][27],4u);
   s.pc=0xf1b804u;break;
  case 0xf1b804u:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=7u; /* mult    r27,r7 */
   s.registers[s.bank][7]=(s.registers[s.bank][7]&0xffffu)*(s.registers[s.bank][27]&0xffffu);
   zn(&s,s.registers[s.bank][7]);
   s.pc=0xf1b806u;break;
  case 0xf1b806u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=7u; /* add     r0,r7 */
   s.registers[s.bank][7]=add(&s,s.registers[s.bank][7],s.registers[s.bank][0]);
   s.pc=0xf1b808u;break;
  case 0xf1b808u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=23u; /* move    r6,r23 */
   s.registers[s.bank][23]=s.registers[s.bank][6];
   s.pc=0xf1b80au;break;
  case 0xf1b80au:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=23u; /* shrq    $1d,r23 */
   s.c=s.registers[s.bank][23]&1u;s.registers[s.bank][23]=s.registers[s.bank][23]>>29;zn(&s,s.registers[s.bank][23]);
   s.pc=0xf1b80cu;break;
  case 0xf1b80cu:biwn_DSP_last_operands[0]=30u;biwn_DSP_last_operands[1]=23u; /* shlq    $2,r23 */
   s.c=s.registers[s.bank][23]>>31;s.registers[s.bank][23]=s.registers[s.bank][23]<<2;zn(&s,s.registers[s.bank][23]);
   s.pc=0xf1b80eu;break;
  case 0xf1b80eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=26u; /* movei   $f1bcf0,r26 */
   s.registers[s.bank][26]=0xf1bcf0u;
   s.pc=0xf1b814u;break;
  case 0xf1b814u:biwn_DSP_last_operands[0]=23u;biwn_DSP_last_operands[1]=26u; /* add     r23,r26 */
   s.registers[s.bank][26]=add(&s,s.registers[s.bank][26],s.registers[s.bank][23]);
   s.pc=0xf1b816u;break;
  case 0xf1b816u:biwn_DSP_last_operands[0]=26u;biwn_DSP_last_operands[1]=25u; /* load    (r26),r25 */
   CHECK(rd32(bus,&s,s.registers[s.bank][26]&~3u,&v));s.registers[s.bank][25]=v;
   s.pc=0xf1b818u;break;
case 0xf1b818u:biwn_DSP_last_operands[0]=25u;biwn_DSP_last_operands[1]=0u; /* jump    (r25) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][25];}s.pc=0xf1b81au;break;
  case 0xf1b81au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b81cu;break;
  case 0xf1b81cu:biwn_DSP_last_operands[0]=16u;biwn_DSP_last_operands[1]=4u; /* store   r4,(r16) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][16])?(s.registers[s.bank][16]&~3u):s.registers[s.bank][16],s.registers[s.bank][4]));
   s.pc=0xf1b81eu;break;
  case 0xf1b81eu:biwn_DSP_last_operands[0]=17u;biwn_DSP_last_operands[1]=5u; /* store   r5,(r17) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][17])?(s.registers[s.bank][17]&~3u):s.registers[s.bank][17],s.registers[s.bank][5]));
   s.pc=0xf1b820u;break;
  case 0xf1b820u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=22u; /* bset    $6,r22 */
   s.registers[s.bank][22]|=(1u<<6);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b822u;break;
  case 0xf1b822u:biwn_DSP_last_operands[0]=31u;biwn_DSP_last_operands[1]=27u; /* load    (r31),r27 */
   CHECK(rd32(bus,&s,s.registers[s.bank][31]&~3u,&v));s.registers[s.bank][27]=v;
   s.pc=0xf1b824u;break;
  case 0xf1b824u:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=22u; /* bset    $e,r22 */
   s.registers[s.bank][22]|=(1u<<14);
   zn(&s,s.registers[s.bank][22]);
   s.pc=0xf1b826u;break;
  case 0xf1b826u:biwn_DSP_last_operands[0]=2u;biwn_DSP_last_operands[1]=27u; /* addq    $2,r27 */
   s.registers[s.bank][27]=add(&s,s.registers[s.bank][27],2u);
   s.pc=0xf1b828u;break;
  case 0xf1b828u:biwn_DSP_last_operands[0]=4u;biwn_DSP_last_operands[1]=31u; /* addq    $4,r31 */
   s.registers[s.bank][31]=add(&s,s.registers[s.bank][31],4u);
   s.pc=0xf1b82au;break;
case 0xf1b82au:biwn_DSP_last_operands[0]=27u;biwn_DSP_last_operands[1]=0u; /* jump    (r27) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][27];}s.pc=0xf1b82cu;break;
  case 0xf1b82cu:biwn_DSP_last_operands[0]=20u;biwn_DSP_last_operands[1]=22u; /* store   r22,(r20) */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][20])?(s.registers[s.bank][20]&~3u):s.registers[s.bank][20],s.registers[s.bank][22]));
   s.pc=0xf1b82eu;break;
  case 0xf1b9a2u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=23u; /* moveq   15,r23 */
   s.registers[s.bank][23]=15u;
   s.pc=0xf1b9a4u;break;
  case 0xf1b9a4u:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=23u; /* and     r6,r23 */
   s.registers[s.bank][23]&=s.registers[s.bank][6];
   zn(&s,s.registers[s.bank][23]);
   s.pc=0xf1b9a6u;break;
  case 0xf1b9a6u:biwn_DSP_last_operands[0]=14u;biwn_DSP_last_operands[1]=2u; /* jr      z,00F1B9C4 */
   if(condition(&s,2)){pending=1;target=0xf1b9c4u;}
   s.pc=0xf1b9a8u;break;
  case 0xf1b9a8u:biwn_DSP_last_operands[0]=28u;biwn_DSP_last_operands[1]=6u; /* btst    $1c,r6 */
   s.z=((~s.registers[s.bank][6])>>28)&1u;
   s.pc=0xf1b9aau;break;
  case 0xf1b9aau:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=1u; /* jr      nz,00F1B9B6 */
   if(condition(&s,1)){pending=1;target=0xf1b9b6u;}
   s.pc=0xf1b9acu;break;
  case 0xf1b9acu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b9aeu;break;
  case 0xf1b9b6u:biwn_DSP_last_operands[0]=28u;biwn_DSP_last_operands[1]=6u; /* shlq    $4,r6 */
   s.c=s.registers[s.bank][6]>>31;s.registers[s.bank][6]=s.registers[s.bank][6]<<4;zn(&s,s.registers[s.bank][6]);
   s.pc=0xf1b9b8u;break;
  case 0xf1b9b8u:biwn_DSP_last_operands[0]=12u;biwn_DSP_last_operands[1]=6u; /* sharq   $c,r6 */
   s.c=s.registers[s.bank][6]&1u;s.registers[s.bank][6]=sar(s.registers[s.bank][6],12);zn(&s,s.registers[s.bank][6]);
   s.pc=0xf1b9bau;break;
  case 0xf1b9bau:biwn_DSP_last_operands[0]=29u;biwn_DSP_last_operands[1]=6u; /* shlq    $3,r6 */
   s.c=s.registers[s.bank][6]>>31;s.registers[s.bank][6]=s.registers[s.bank][6]<<3;zn(&s,s.registers[s.bank][6]);
   s.pc=0xf1b9bcu;break;
  case 0xf1b9bcu:biwn_DSP_last_operands[0]=6u;biwn_DSP_last_operands[1]=5u; /* add     r6,r5 */
   s.registers[s.bank][5]=add(&s,s.registers[s.bank][5],s.registers[s.bank][6]);
   s.pc=0xf1b9beu;break;
  case 0xf1b9beu:biwn_DSP_last_operands[0]=5u;biwn_DSP_last_operands[1]=4u; /* load    (r5),r4 */
   CHECK(rd32(bus,&s,s.registers[s.bank][5]&~3u,&v));s.registers[s.bank][4]=v;
   s.pc=0xf1b9c0u;break;
case 0xf1b9c0u:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=0u; /* jump    (r8) */ if(condition(&s,0)){pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][8];}s.pc=0xf1b9c2u;break;
  case 0xf1b9c2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* nop */
   s.pc=0xf1b9c4u;break;
case 0xf1b144u:biwn_DSP_last_operands[0]=31u;biwn_DSP_last_operands[1]=0u; /* observed JR -1, always */ pending=1;target=0xf1b144u;s.pc=0xf1b146u;break;
case 0xf1b146u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* observed delay NOP */ s.pc=0xf1b148u;break;
  case 0x0u:biwn_DSP_last_operands[0]=7u;biwn_DSP_last_operands[1]=17u; /* Observed DSP op0 r7,r17 */
   s.registers[s.bank][17]=add(&s,s.registers[s.bank][17],s.registers[s.bank][7]);
   s.pc=0x2u;break;
  case 0x2u:biwn_DSP_last_operands[0]=8u;biwn_DSP_last_operands[1]=17u; /* Observed DSP op47 r8,r17 */
   CHECK(wr32(bus,&s,local(s.registers[s.bank][8])?(s.registers[s.bank][8]&~3u):s.registers[s.bank][8],s.registers[s.bank][17]));
   s.pc=0x4u;break;
  case 0x4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=24u; /* Observed DSP op0 r0,r24 */
   s.registers[s.bank][24]=add(&s,s.registers[s.bank][24],s.registers[s.bank][0]);
   s.pc=0x6u;break;
  case 0x6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x8u;break;
  case 0x8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xau;break;
case 0xau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xcu;break;
  case 0xcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xeu;break;
case 0xeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x10u;break;
  case 0x10u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x12u;break;
case 0x12u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=2u; s.registers[s.bank][2]=biwn_external_addc(&s,s.registers[s.bank][2],s.registers[s.bank][0]);s.pc=0x14u;break;
  case 0x14u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x16u;break;
case 0x16u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x18u;break;
  case 0x18u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1au;break;
case 0x1au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1cu;break;
  case 0x1cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1eu;break;
case 0x1eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x20u;break;
  case 0x20u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x22u;break;
case 0x22u:biwn_DSP_last_operands[0]=15u;biwn_DSP_last_operands[1]=30u; s.registers[s.bank][30]=biwn_external_mtoi(s.registers[s.bank][15]);zn(&s,s.registers[s.bank][30]);s.pc=0x24u;break;
  case 0x24u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x26u;break;
case 0x26u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x28u;break;
  case 0x28u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2au;break;
case 0x2au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2cu;break;
  case 0x2cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2eu;break;
case 0x2eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x30u;break;
  case 0x30u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x32u;break;
case 0x32u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x34u;break;
  case 0x34u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x36u;break;
case 0x36u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x38u;break;
  case 0x38u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x3au;break;
case 0x3au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x3cu;break;
  case 0x3cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x3eu;break;
case 0x3eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x40u;break;
  case 0x40u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x42u;break;
case 0x42u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x44u;break;
  case 0x44u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x46u;break;
case 0x46u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x48u;break;
  case 0x48u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x4au;break;
case 0x4au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x4cu;break;
  case 0x4cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x4eu;break;
case 0x4eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x50u;break;
  case 0x50u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x52u;break;
case 0x52u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x54u;break;
  case 0x54u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x56u;break;
case 0x56u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x58u;break;
  case 0x58u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x5au;break;
case 0x5au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x5cu;break;
  case 0x5cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x5eu;break;
case 0x5eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x60u;break;
  case 0x60u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x62u;break;
case 0x62u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x64u;break;
  case 0x64u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x66u;break;
case 0x66u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x68u;break;
  case 0x68u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x6au;break;
case 0x6au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x6cu;break;
  case 0x6cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x6eu;break;
case 0x6eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x70u;break;
  case 0x70u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x72u;break;
case 0x72u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x74u;break;
  case 0x74u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x76u;break;
case 0x76u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x78u;break;
  case 0x78u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x7au;break;
case 0x7au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x7cu;break;
  case 0x7cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x7eu;break;
case 0x7eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x80u;break;
  case 0x80u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x82u;break;
case 0x82u:biwn_DSP_last_operands[0]=16u;biwn_DSP_last_operands[1]=8u; s.registers[s.bank][8]=biwn_external_mtoi(s.registers[s.bank][16]);zn(&s,s.registers[s.bank][8]);s.pc=0x84u;break;
  case 0x84u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x86u;break;
case 0x86u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x88u;break;
  case 0x88u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x8au;break;
case 0x8au:biwn_DSP_last_operands[0]=21u;biwn_DSP_last_operands[1]=22u; s.registers[s.bank][22]=biwn_external_mtoi(s.registers[s.bank][21]);zn(&s,s.registers[s.bank][22]);s.pc=0x8cu;break;
  case 0x8cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x8eu;break;
case 0x8eu:biwn_DSP_last_operands[0]=23u;biwn_DSP_last_operands[1]=2u; s.registers[s.bank][2]=biwn_external_mtoi(s.registers[s.bank][23]);zn(&s,s.registers[s.bank][2]);s.pc=0x90u;break;
  case 0x90u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x92u;break;
case 0x92u:biwn_DSP_last_operands[0]=23u;biwn_DSP_last_operands[1]=22u; s.registers[s.bank][22]=biwn_external_mtoi(s.registers[s.bank][23]);zn(&s,s.registers[s.bank][22]);s.pc=0x94u;break;
  case 0x94u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x96u;break;
case 0x96u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x98u;break;
  case 0x98u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x9au;break;
case 0x9au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x9cu;break;
  case 0x9cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x9eu;break;
case 0x9eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xa0u;break;
  case 0xa0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xa2u;break;
case 0xa2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xa4u;break;
  case 0xa4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xa6u;break;
case 0xa6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xa8u;break;
  case 0xa8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xaau;break;
case 0xaau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xacu;break;
  case 0xacu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xaeu;break;
case 0xaeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xb0u;break;
  case 0xb0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xb2u;break;
case 0xb2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xb4u;break;
  case 0xb4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xb6u;break;
case 0xb6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xb8u;break;
  case 0xb8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xbau;break;
case 0xbau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xbcu;break;
  case 0xbcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xbeu;break;
case 0xbeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xc0u;break;
  case 0xc0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xc2u;break;
case 0xc2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xc4u;break;
  case 0xc4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xc6u;break;
case 0xc6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xc8u;break;
  case 0xc8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xcau;break;
case 0xcau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xccu;break;
  case 0xccu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xceu;break;
case 0xceu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xd0u;break;
  case 0xd0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xd2u;break;
case 0xd2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xd4u;break;
  case 0xd4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xd6u;break;
case 0xd6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xd8u;break;
  case 0xd8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xdau;break;
case 0xdau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xdcu;break;
  case 0xdcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xdeu;break;
case 0xdeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xe0u;break;
  case 0xe0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xe2u;break;
case 0xe2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xe4u;break;
  case 0xe4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xe6u;break;
case 0xe6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xe8u;break;
  case 0xe8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xeau;break;
case 0xeau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xecu;break;
  case 0xecu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xeeu;break;
case 0xeeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xf0u;break;
  case 0xf0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xf2u;break;
case 0xf2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xf4u;break;
  case 0xf4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xf6u;break;
case 0xf6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xf8u;break;
  case 0xf8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xfau;break;
case 0xfau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0xfcu;break;
  case 0xfcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0xfeu;break;
case 0xfeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x100u;break;
  case 0x100u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x102u;break;
  case 0x102u:biwn_DSP_last_operands[0]=30u;biwn_DSP_last_operands[1]=20u; /* Observed DSP op57 r30,r20 */
   s.pc=0x104u;break;
  case 0x104u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x106u;break;
case 0x106u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x108u;break;
  case 0x108u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x10au;break;
case 0x10au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x10cu;break;
  case 0x10cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x10eu;break;
case 0x10eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x110u;break;
  case 0x110u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x112u;break;
case 0x112u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x114u;break;
  case 0x114u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x116u;break;
case 0x116u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x118u;break;
  case 0x118u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x11au;break;
case 0x11au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x11cu;break;
  case 0x11cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x11eu;break;
case 0x11eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x120u;break;
  case 0x120u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x122u;break;
case 0x122u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x124u;break;
  case 0x124u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x126u;break;
case 0x126u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x128u;break;
  case 0x128u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x12au;break;
case 0x12au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x12cu;break;
  case 0x12cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x12eu;break;
case 0x12eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x130u;break;
  case 0x130u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x132u;break;
case 0x132u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x134u;break;
  case 0x134u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x136u;break;
case 0x136u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x138u;break;
  case 0x138u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x13au;break;
case 0x13au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x13cu;break;
  case 0x13cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x13eu;break;
case 0x13eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x140u;break;
  case 0x140u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x142u;break;
case 0x142u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x144u;break;
  case 0x144u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x146u;break;
case 0x146u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x148u;break;
  case 0x148u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x14au;break;
case 0x14au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x14cu;break;
  case 0x14cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x14eu;break;
case 0x14eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x150u;break;
  case 0x150u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x152u;break;
case 0x152u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x154u;break;
  case 0x154u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x156u;break;
case 0x156u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x158u;break;
  case 0x158u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x15au;break;
case 0x15au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x15cu;break;
  case 0x15cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x15eu;break;
case 0x15eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x160u;break;
  case 0x160u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x162u;break;
case 0x162u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x164u;break;
  case 0x164u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x166u;break;
case 0x166u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x168u;break;
  case 0x168u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x16au;break;
case 0x16au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x16cu;break;
  case 0x16cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x16eu;break;
case 0x16eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x170u;break;
  case 0x170u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x172u;break;
case 0x172u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x174u;break;
  case 0x174u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x176u;break;
case 0x176u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x178u;break;
  case 0x178u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x17au;break;
case 0x17au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x17cu;break;
  case 0x17cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x17eu;break;
case 0x17eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x180u;break;
  case 0x180u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x182u;break;
case 0x182u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x184u;break;
  case 0x184u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x186u;break;
case 0x186u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x188u;break;
  case 0x188u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x18au;break;
case 0x18au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x18cu;break;
  case 0x18cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x18eu;break;
case 0x18eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x190u;break;
  case 0x190u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x192u;break;
case 0x192u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x194u;break;
  case 0x194u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x196u;break;
case 0x196u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x198u;break;
  case 0x198u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x19au;break;
case 0x19au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x19cu;break;
  case 0x19cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x19eu;break;
case 0x19eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1a0u;break;
  case 0x1a0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1a2u;break;
case 0x1a2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1a4u;break;
  case 0x1a4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1a6u;break;
case 0x1a6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1a8u;break;
  case 0x1a8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1aau;break;
case 0x1aau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1acu;break;
  case 0x1acu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1aeu;break;
case 0x1aeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1b0u;break;
  case 0x1b0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1b2u;break;
case 0x1b2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1b4u;break;
  case 0x1b4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1b6u;break;
case 0x1b6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1b8u;break;
  case 0x1b8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1bau;break;
case 0x1bau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1bcu;break;
  case 0x1bcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1beu;break;
case 0x1beu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1c0u;break;
  case 0x1c0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1c2u;break;
case 0x1c2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1c4u;break;
  case 0x1c4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1c6u;break;
case 0x1c6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1c8u;break;
  case 0x1c8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1cau;break;
case 0x1cau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1ccu;break;
  case 0x1ccu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1ceu;break;
case 0x1ceu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1d0u;break;
  case 0x1d0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1d2u;break;
case 0x1d2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1d4u;break;
  case 0x1d4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1d6u;break;
case 0x1d6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1d8u;break;
  case 0x1d8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1dau;break;
case 0x1dau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1dcu;break;
  case 0x1dcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1deu;break;
case 0x1deu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1e0u;break;
  case 0x1e0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1e2u;break;
case 0x1e2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1e4u;break;
  case 0x1e4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1e6u;break;
case 0x1e6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1e8u;break;
  case 0x1e8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1eau;break;
case 0x1eau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1ecu;break;
  case 0x1ecu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1eeu;break;
case 0x1eeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1f0u;break;
  case 0x1f0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1f2u;break;
case 0x1f2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1f4u;break;
  case 0x1f4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1f6u;break;
case 0x1f6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1f8u;break;
  case 0x1f8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1fau;break;
case 0x1fau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x1fcu;break;
  case 0x1fcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x1feu;break;
case 0x1feu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x200u;break;
  case 0x200u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x202u;break;
case 0x202u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x204u;break;
  case 0x204u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x206u;break;
case 0x206u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x208u;break;
  case 0x208u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x20au;break;
case 0x20au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x20cu;break;
  case 0x20cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x20eu;break;
case 0x20eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x210u;break;
  case 0x210u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x212u;break;
case 0x212u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x214u;break;
  case 0x214u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x216u;break;
case 0x216u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x218u;break;
  case 0x218u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x21au;break;
case 0x21au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x21cu;break;
  case 0x21cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x21eu;break;
case 0x21eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x220u;break;
  case 0x220u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x222u;break;
case 0x222u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x224u;break;
  case 0x224u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x226u;break;
case 0x226u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x228u;break;
  case 0x228u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x22au;break;
case 0x22au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x22cu;break;
  case 0x22cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x22eu;break;
case 0x22eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x230u;break;
  case 0x230u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x232u;break;
case 0x232u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x234u;break;
  case 0x234u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x236u;break;
case 0x236u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x238u;break;
  case 0x238u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x23au;break;
case 0x23au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x23cu;break;
  case 0x23cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x23eu;break;
case 0x23eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x240u;break;
  case 0x240u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x242u;break;
case 0x242u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x244u;break;
  case 0x244u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x246u;break;
case 0x246u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x248u;break;
  case 0x248u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x24au;break;
case 0x24au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x24cu;break;
  case 0x24cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x24eu;break;
case 0x24eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x250u;break;
  case 0x250u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x252u;break;
case 0x252u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x254u;break;
  case 0x254u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x256u;break;
case 0x256u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x258u;break;
  case 0x258u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x25au;break;
case 0x25au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x25cu;break;
  case 0x25cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x25eu;break;
case 0x25eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x260u;break;
  case 0x260u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x262u;break;
case 0x262u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x264u;break;
  case 0x264u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x266u;break;
case 0x266u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x268u;break;
  case 0x268u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x26au;break;
case 0x26au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x26cu;break;
  case 0x26cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x26eu;break;
case 0x26eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x270u;break;
  case 0x270u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x272u;break;
case 0x272u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x274u;break;
  case 0x274u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x276u;break;
case 0x276u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x278u;break;
  case 0x278u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x27au;break;
case 0x27au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x27cu;break;
  case 0x27cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x27eu;break;
case 0x27eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x280u;break;
  case 0x280u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x282u;break;
case 0x282u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x284u;break;
  case 0x284u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x286u;break;
case 0x286u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x288u;break;
  case 0x288u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x28au;break;
case 0x28au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x28cu;break;
  case 0x28cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x28eu;break;
case 0x28eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x290u;break;
  case 0x290u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x292u;break;
case 0x292u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x294u;break;
  case 0x294u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x296u;break;
case 0x296u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x298u;break;
  case 0x298u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x29au;break;
case 0x29au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x29cu;break;
  case 0x29cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x29eu;break;
case 0x29eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2a0u;break;
  case 0x2a0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2a2u;break;
case 0x2a2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2a4u;break;
  case 0x2a4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2a6u;break;
case 0x2a6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2a8u;break;
  case 0x2a8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2aau;break;
case 0x2aau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2acu;break;
  case 0x2acu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2aeu;break;
case 0x2aeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2b0u;break;
  case 0x2b0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2b2u;break;
case 0x2b2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2b4u;break;
  case 0x2b4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2b6u;break;
case 0x2b6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2b8u;break;
  case 0x2b8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2bau;break;
case 0x2bau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2bcu;break;
  case 0x2bcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2beu;break;
case 0x2beu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2c0u;break;
  case 0x2c0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2c2u;break;
case 0x2c2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2c4u;break;
  case 0x2c4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2c6u;break;
case 0x2c6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2c8u;break;
  case 0x2c8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2cau;break;
case 0x2cau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2ccu;break;
  case 0x2ccu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2ceu;break;
case 0x2ceu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2d0u;break;
  case 0x2d0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2d2u;break;
case 0x2d2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2d4u;break;
  case 0x2d4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2d6u;break;
case 0x2d6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2d8u;break;
  case 0x2d8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2dau;break;
case 0x2dau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2dcu;break;
  case 0x2dcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2deu;break;
case 0x2deu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2e0u;break;
  case 0x2e0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2e2u;break;
case 0x2e2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2e4u;break;
  case 0x2e4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2e6u;break;
case 0x2e6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2e8u;break;
  case 0x2e8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2eau;break;
case 0x2eau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2ecu;break;
  case 0x2ecu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2eeu;break;
case 0x2eeu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2f0u;break;
  case 0x2f0u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2f2u;break;
case 0x2f2u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2f4u;break;
  case 0x2f4u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2f6u;break;
case 0x2f6u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2f8u;break;
  case 0x2f8u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2fau;break;
case 0x2fau:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x2fcu;break;
  case 0x2fcu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x2feu;break;
case 0x2feu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x300u;break;
  case 0x300u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x302u;break;
case 0x302u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x304u;break;
  case 0x304u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x306u;break;
case 0x306u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x308u;break;
  case 0x308u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x30au;break;
case 0x30au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x30cu;break;
  case 0x30cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x30eu;break;
case 0x30eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x310u;break;
  case 0x310u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x312u;break;
case 0x312u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x314u;break;
  case 0x314u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x316u;break;
case 0x316u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x318u;break;
  case 0x318u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x31au;break;
case 0x31au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x31cu;break;
  case 0x31cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x31eu;break;
case 0x31eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x320u;break;
  case 0x320u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x322u;break;
case 0x322u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x324u;break;
  case 0x324u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x326u;break;
case 0x326u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x328u;break;
  case 0x328u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x32au;break;
case 0x32au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x32cu;break;
  case 0x32cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x32eu;break;
case 0x32eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x330u;break;
  case 0x330u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x332u;break;
case 0x332u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x334u;break;
  case 0x334u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x336u;break;
case 0x336u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x338u;break;
  case 0x338u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x33au;break;
case 0x33au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x33cu;break;
  case 0x33cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x33eu;break;
case 0x33eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x340u;break;
  case 0x340u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x342u;break;
case 0x342u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x344u;break;
  case 0x344u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x346u;break;
case 0x346u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x348u;break;
  case 0x348u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x34au;break;
case 0x34au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x34cu;break;
  case 0x34cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x34eu;break;
case 0x34eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x350u;break;
  case 0x350u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x352u;break;
case 0x352u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x354u;break;
  case 0x354u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x356u;break;
case 0x356u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x358u;break;
  case 0x358u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x35au;break;
case 0x35au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x35cu;break;
  case 0x35cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x35eu;break;
case 0x35eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x360u;break;
  case 0x360u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x362u;break;
case 0x362u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x364u;break;
  case 0x364u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x366u;break;
case 0x366u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x368u;break;
  case 0x368u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x36au;break;
case 0x36au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x36cu;break;
  case 0x36cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x36eu;break;
case 0x36eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x370u;break;
  case 0x370u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x372u;break;
case 0x372u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x374u;break;
  case 0x374u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x376u;break;
case 0x376u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x378u;break;
  case 0x378u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x37au;break;
case 0x37au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x37cu;break;
  case 0x37cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x37eu;break;
case 0x37eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x380u;break;
  case 0x380u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x382u;break;
case 0x382u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x384u;break;
  case 0x384u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x386u;break;
case 0x386u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x388u;break;
  case 0x388u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x38au;break;
case 0x38au:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x38cu;break;
  case 0x38cu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x38eu;break;
case 0x38eu:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x390u;break;
  case 0x390u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x392u;break;
case 0x392u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x394u;break;
  case 0x394u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; /* Observed DSP op0 r0,r0 */
   s.registers[s.bank][0]=add(&s,s.registers[s.bank][0],s.registers[s.bank][0]);
   s.pc=0x396u;break;
case 0x396u:biwn_DSP_last_operands[0]=0u;biwn_DSP_last_operands[1]=0u; s.registers[s.bank][0]=biwn_external_addc(&s,s.registers[s.bank][0],s.registers[s.bank][0]);s.pc=0x398u;break;
default:return BIWN_DSP_EXTERNAL_ENGINE_BAD_PC;
 }if(delayed){if(pending)return BIWN_DSP_EXTERNAL_ENGINE_BAD_DELAY;s.pc=target;s.flags_delay=0;break;}delayed=pending;
 if(s.flags_delay)s.flags_delay--; }while(delayed);*state=s;return 0;}
enum biwn_dsp_external_engine_status biwn_dsp_external_engine_assert_interrupt(struct biwn_dsp_external_engine_state *state,uint32_t irq){struct biwn_dsp_external_engine_state s;uint32_t mask,bits,sp;unsigned which=0;if(!valid(state)||(irq>2u))return 1;s=*state;mask=0x40u<<irq;s.control|=mask;if((s.flags&8u)||s.flags_delay){*state=s;return 0;}bits=((s.control>>6)&31u)&((s.flags>>4)&31u);if(!bits){*state=s;return 0;}for(unsigned i=0;i<5;i++)if(bits&(1u<<i))which=i;if(which>2u)return 1;s.flags|=8u;s.bank=0;s.flags_delay=0;s.prestore_bank=0;sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b000u+which*16u;*state=s;return 0;}

void biwn_external_last_operands(unsigned*p){p[0]=biwn_DSP_last_operands[0];p[1]=biwn_DSP_last_operands[1];}
