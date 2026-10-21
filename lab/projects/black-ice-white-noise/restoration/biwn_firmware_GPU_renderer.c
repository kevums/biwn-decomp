/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_firmware_GPU_renderer.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_firmware_GPU_renderer.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_firmware_GPU_renderer_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_firmware_GPU_renderer_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int io_sync(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,int after){return b->sync&&b->sync(b->context,s,after)?2:0;}
static int rd32(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(io_sync(b,s,0))return 2;int status=b->read32(b->context,a,v)?2:0;if(io_sync(b,s,1))return 2;return status;}
static int rd16(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){uint16_t x;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(io_sync(b,s,0))return 2;int status=b->read16(b->context,a,&x)?2:0;*v=x;if(io_sync(b,s,1))return 2;return status;}
static int loadw(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);return rd16(b,s,a,v);}
static int rd8(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){uint8_t x;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);if(io_sync(b,s,0))return 2;int status=b->read8(b->context,a,&x)?2:0;*v=x;if(io_sync(b,s,1))return 2;return status;}
static int wr32(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(io_sync(b,s,0))return 2;int status=b->write32(b->context,a,v)?2:0;if(io_sync(b,s,1))return 2;return status;}
static int wr16(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(b,s,a&~1u,v&0xffffu);if(io_sync(b,s,0))return 2;int status=b->write16(b->context,a,(uint16_t)v)?2:0;if(io_sync(b,s,1))return 2;return status;}
static void divide(struct biwn_firmware_GPU_renderer_state *s,unsigned m,unsigned n){uint32_t q=s->registers[s->active_bank][n],r=0,d=s->registers[s->active_bank][m];unsigned i;if(s->division_control&1u){r=q>>16;q<<=16;}for(i=0;i<32;i++){uint32_t sign=r&0x80000000u;r=(r<<1)|(q>>31);r+=sign?d:0u-d;q=(q<<1)|((~r)>>31);}s->registers[s->active_bank][n]=q;s->remainder=r;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_firmware_GPU_renderer_status)status;}while(0)
enum biwn_firmware_GPU_renderer_status biwn_firmware_GPU_renderer_run(struct biwn_firmware_GPU_renderer_bus *bus,struct biwn_firmware_GPU_renderer_state *state,uint32_t budget){struct biwn_firmware_GPU_renderer_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->sync||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget){unsigned delayed=pending;uint32_t resume=target,nxt=0;pending=0;if(!(s.control&1u)&&!delayed){*state=s;return 0;}if(bus->observe_PC)bus->observe_PC(bus->context,&s,s.pc);s.instructions++;switch(s.pc){
case 0xf03000u:
if(s.local_RAM[0]==136u&&s.local_RAM[1]==114u) {nxt=0xf03002u;s.pc=nxt;s.registers[s.active_bank][18]=s.registers[s.active_bank][3];}
else if(s.local_RAM[0]==152u&&s.local_RAM[1]==0u&&s.local_RAM[2]==0u&&s.local_RAM[3]==152u&&s.local_RAM[4]==0u&&s.local_RAM[5]==0u) {nxt=0xf03006u;s.pc=nxt;s.registers[s.active_bank][0]=0x98u;}
else if(s.local_RAM[0]==152u&&s.local_RAM[1]==0u&&s.local_RAM[2]==63u&&s.local_RAM[3]==96u&&s.local_RAM[4]==0u&&s.local_RAM[5]==240u) {nxt=0xf03006u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else if(s.local_RAM[0]==152u&&s.local_RAM[1]==0u&&s.local_RAM[2]==63u&&s.local_RAM[3]==116u&&s.local_RAM[4]==0u&&s.local_RAM[5]==240u) {nxt=0xf03006u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f74u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03002u:
if(s.local_RAM[2]==146u&&s.local_RAM[3]==82u) {nxt=0xf03004u;s.pc=nxt;s.registers[1u-s.active_bank][18]=s.registers[s.active_bank][18];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03004u:
if(s.local_RAM[4]==152u&&s.local_RAM[5]==0u&&s.local_RAM[6]==0u&&s.local_RAM[7]==224u&&s.local_RAM[8]==0u&&s.local_RAM[9]==0u) {nxt=0xf0300au;s.pc=nxt;s.registers[s.active_bank][0]=0xe0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03006u:
if(s.local_RAM[6]==0u&&s.local_RAM[7]==96u) {nxt=0xf03008u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[6]==152u&&s.local_RAM[7]==14u&&s.local_RAM[8]==63u&&s.local_RAM[9]==128u&&s.local_RAM[10]==0u&&s.local_RAM[11]==240u) {nxt=0xf0300cu;s.pc=nxt;s.registers[s.active_bank][14]=0xf03f80u;}
else if(s.local_RAM[6]==164u&&s.local_RAM[7]==29u) {nxt=0xf03008u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][29]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03008u:
if(s.local_RAM[8]==147u&&s.local_RAM[9]==189u) {nxt=0xf0300au;s.pc=nxt;s.registers[1u-s.active_bank][29]=s.registers[s.active_bank][29];}
else if(s.local_RAM[8]==164u&&s.local_RAM[9]==2u) {nxt=0xf0300au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0300au:
if(s.local_RAM[10]==2u&&s.local_RAM[11]==64u) {nxt=0xf0300cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[10]==140u&&s.local_RAM[11]==100u) {nxt=0xf0300cu;s.pc=nxt;s.registers[s.active_bank][4]=3u;}
else if(s.local_RAM[10]==163u&&s.local_RAM[11]==187u) {nxt=0xf0300cu;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][29],&v));s.registers[s.active_bank][27]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0300cu:
if(s.local_RAM[12]==152u&&s.local_RAM[13]==0u&&s.local_RAM[14]==48u&&s.local_RAM[15]==172u&&s.local_RAM[16]==0u&&s.local_RAM[17]==240u) {nxt=0xf03012u;s.pc=nxt;s.registers[s.active_bank][0]=0xf030acu;}
else if(s.local_RAM[12]==152u&&s.local_RAM[13]==0u&&s.local_RAM[14]==63u&&s.local_RAM[15]==96u&&s.local_RAM[16]==0u&&s.local_RAM[17]==240u) {nxt=0xf03012u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else if(s.local_RAM[12]==164u&&s.local_RAM[13]==1u) {nxt=0xf0300eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[12]==164u&&s.local_RAM[13]==2u) {nxt=0xf0300eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0300eu:
if(s.local_RAM[14]==11u&&s.local_RAM[15]==129u) {nxt=0xf03010u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],28u);}
else if(s.local_RAM[14]==152u&&s.local_RAM[15]==0u&&s.local_RAM[16]==0u&&s.local_RAM[17]==228u&&s.local_RAM[18]==0u&&s.local_RAM[19]==0u) {nxt=0xf03014u;s.pc=nxt;s.registers[s.active_bank][0]=0xe4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03010u:
if(s.local_RAM[16]==164u&&s.local_RAM[17]==32u) {nxt=0xf03012u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03012u:
if(s.local_RAM[18]==10u&&s.local_RAM[19]==1u) {nxt=0xf03014u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],16u);}
else if(s.local_RAM[18]==102u&&s.local_RAM[19]==2u) {nxt=0xf03014u;s.pc=nxt;s.c=s.registers[s.active_bank][2]&1u;s.registers[s.active_bank][2]=s.registers[s.active_bank][2]>>16;zn(&s,s.registers[s.active_bank][2]);}
else if(s.local_RAM[18]==124u&&s.local_RAM[19]==27u) {nxt=0xf03014u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][27],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03014u:
if(s.local_RAM[20]==2u&&s.local_RAM[21]==64u) {nxt=0xf03016u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[20]==164u&&s.local_RAM[21]==1u) {nxt=0xf03016u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[20]==164u&&s.local_RAM[21]==34u) {nxt=0xf03016u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][2]=v;}
else if(s.local_RAM[20]==208u&&s.local_RAM[21]==24u) {nxt=0xf03016u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03016u:
if(s.local_RAM[22]==8u&&s.local_RAM[23]==130u) {nxt=0xf03018u;s.pc=nxt;s.registers[s.active_bank][2]=add(&s,s.registers[s.active_bank][2],4u);}
else if(s.local_RAM[22]==36u&&s.local_RAM[23]==130u) {nxt=0xf03018u;s.pc=nxt;s.registers[s.active_bank][2]&=s.registers[s.active_bank][4];
   zn(&s,s.registers[s.active_bank][2]);}
else if(s.local_RAM[22]==164u&&s.local_RAM[23]==1u) {nxt=0xf03018u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[22]==228u&&s.local_RAM[23]==0u) {nxt=0xf03018u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03018u:
if(s.local_RAM[24]==136u&&s.local_RAM[25]==64u) {nxt=0xf0301au;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][2];}
else if(s.local_RAM[24]==152u&&s.local_RAM[25]==0u&&s.local_RAM[26]==48u&&s.local_RAM[27]==78u&&s.local_RAM[28]==0u&&s.local_RAM[29]==240u) {nxt=0xf0301eu;s.pc=nxt;s.registers[s.active_bank][0]=0xf0304eu;}
else if(s.local_RAM[24]==164u&&s.local_RAM[25]==32u) {nxt=0xf0301au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][0]=v;}
else if(s.local_RAM[24]==199u&&s.local_RAM[25]==194u) {nxt=0xf0301au;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+120u,s.registers[s.active_bank][2]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0301au:
if(s.local_RAM[26]==99u&&s.local_RAM[27]==194u) {nxt=0xf0301cu;s.pc=nxt;s.c=s.registers[s.active_bank][2]>>31;s.registers[s.active_bank][2]=s.registers[s.active_bank][2]<<2;zn(&s,s.registers[s.active_bank][2]);}
else if(s.local_RAM[26]==143u&&s.local_RAM[27]==222u) {nxt=0xf0301cu;s.pc=nxt;s.registers[s.active_bank][30]=30u;}
else if(s.local_RAM[26]==152u&&s.local_RAM[27]==24u&&s.local_RAM[28]==0u&&s.local_RAM[29]==252u&&s.local_RAM[30]==0u&&s.local_RAM[31]==0u) {nxt=0xf03020u;s.pc=nxt;s.registers[s.active_bank][24]=0xfcu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0301cu:
if(s.local_RAM[28]==0u&&s.local_RAM[29]==64u) {nxt=0xf0301eu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][2]);}
else if(s.local_RAM[28]==136u&&s.local_RAM[29]==31u) {nxt=0xf0301eu;s.pc=nxt;s.registers[s.active_bank][31]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0301eu:
if(s.local_RAM[30]==136u&&s.local_RAM[31]==39u) {nxt=0xf03020u;s.pc=nxt;s.registers[s.active_bank][7]=s.registers[s.active_bank][1];}
else if(s.local_RAM[30]==164u&&s.local_RAM[31]==24u) {nxt=0xf03020u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][24]=v;}
else if(s.local_RAM[30]==175u&&s.local_RAM[31]==2u) {nxt=0xf03020u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+96u,&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03020u:
if(s.local_RAM[32]==102u&&s.local_RAM[33]==31u) {nxt=0xf03022u;s.pc=nxt;s.c=s.registers[s.active_bank][31]&1u;s.registers[s.active_bank][31]=s.registers[s.active_bank][31]>>16;zn(&s,s.registers[s.active_bank][31]);}
else if(s.local_RAM[32]==140u&&s.local_RAM[33]==161u) {nxt=0xf03022u;s.pc=nxt;s.registers[s.active_bank][1]=5u;}
else if(s.local_RAM[32]==152u&&s.local_RAM[33]==1u&&s.local_RAM[34]==176u&&s.local_RAM[35]==52u&&s.local_RAM[36]==0u&&s.local_RAM[37]==241u) {nxt=0xf03026u;s.pc=nxt;s.registers[s.active_bank][1]=0xf1b034u;}
else if(s.local_RAM[32]==152u&&s.local_RAM[33]==14u&&s.local_RAM[34]==63u&&s.local_RAM[35]==128u&&s.local_RAM[36]==0u&&s.local_RAM[37]==240u) {nxt=0xf03026u;s.pc=nxt;s.registers[s.active_bank][14]=0xf03f80u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03022u:
if(s.local_RAM[34]==16u&&s.local_RAM[35]==65u) {nxt=0xf03024u;s.pc=nxt;s.registers[s.active_bank][1]=sub(&s,s.registers[s.active_bank][1],s.registers[s.active_bank][2]);}
else if(s.local_RAM[34]==102u&&s.local_RAM[35]==7u) {nxt=0xf03024u;s.pc=nxt;s.c=s.registers[s.active_bank][7]&1u;s.registers[s.active_bank][7]=s.registers[s.active_bank][7]>>16;zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03024u:
if(s.local_RAM[36]==39u&&s.local_RAM[37]==223u) {nxt=0xf03026u;s.pc=nxt;s.registers[s.active_bank][31]&=s.registers[s.active_bank][30];
   zn(&s,s.registers[s.active_bank][31]);}
else if(s.local_RAM[36]==120u&&s.local_RAM[37]==59u) {nxt=0xf03026u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][27],s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03026u:
if(s.local_RAM[38]==0u&&s.local_RAM[39]==24u) {nxt=0xf03028u;s.pc=nxt;s.registers[s.active_bank][24]=add(&s,s.registers[s.active_bank][24],s.registers[s.active_bank][0]);}
else if(s.local_RAM[38]==39u&&s.local_RAM[39]==199u) {nxt=0xf03028u;s.pc=nxt;s.registers[s.active_bank][7]&=s.registers[s.active_bank][30];
   zn(&s,s.registers[s.active_bank][7]);}
else if(s.local_RAM[38]==152u&&s.local_RAM[39]==0u&&s.local_RAM[40]==63u&&s.local_RAM[41]==92u&&s.local_RAM[42]==0u&&s.local_RAM[43]==240u) {nxt=0xf0302cu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f5cu;}
else if(s.local_RAM[38]==208u&&s.local_RAM[39]==2u) {nxt=0xf03028u;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03028u:
if(s.local_RAM[40]==100u&&s.local_RAM[41]==62u) {nxt=0xf0302au;s.pc=nxt;s.c=s.registers[s.active_bank][30]&1u;s.registers[s.active_bank][30]=s.registers[s.active_bank][30]>>1;zn(&s,s.registers[s.active_bank][30]);}
else if(s.local_RAM[40]==152u&&s.local_RAM[41]==10u&&s.local_RAM[42]==177u&&s.local_RAM[43]==48u&&s.local_RAM[44]==0u&&s.local_RAM[45]==241u) {nxt=0xf0302eu;s.pc=nxt;s.registers[s.active_bank][10]=0xf1b130u;}
else if(s.local_RAM[40]==228u&&s.local_RAM[41]==0u) {nxt=0xf0302au;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0302au:
if(s.local_RAM[42]==19u&&s.local_RAM[43]==223u) {nxt=0xf0302cu;s.pc=nxt;s.registers[s.active_bank][31]=sub(&s,s.registers[s.active_bank][31],s.registers[s.active_bank][30]);}
else if(s.local_RAM[42]==152u&&s.local_RAM[43]==0u&&s.local_RAM[44]==63u&&s.local_RAM[45]==96u&&s.local_RAM[46]==0u&&s.local_RAM[47]==240u) {nxt=0xf03030u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0302cu:
if(s.local_RAM[44]==164u&&s.local_RAM[45]==1u) {nxt=0xf0302eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[44]==212u&&s.local_RAM[45]==84u) {nxt=0xf0302eu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf03032u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0302eu:
if(s.local_RAM[46]==124u&&s.local_RAM[47]==97u) {nxt=0xf03030u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],0x3u);}
else if(s.local_RAM[46]==152u&&s.local_RAM[47]==2u&&s.local_RAM[48]==0u&&s.local_RAM[49]==63u&&s.local_RAM[50]==0u&&s.local_RAM[51]==0u) {nxt=0xf03034u;s.pc=nxt;s.registers[s.active_bank][2]=0x3fu;}
else if(s.local_RAM[46]==228u&&s.local_RAM[47]==0u) {nxt=0xf03030u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03030u:
if(s.local_RAM[48]==32u&&s.local_RAM[49]==31u) {nxt=0xf03032u;s.pc=nxt;s.registers[s.active_bank][31]=sub(&s,0,s.registers[s.active_bank][31]);}
else if(s.local_RAM[48]==164u&&s.local_RAM[49]==1u) {nxt=0xf03032u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[48]==212u&&s.local_RAM[49]==193u) {nxt=0xf03032u;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf0303eu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03032u:
if(s.local_RAM[50]==8u&&s.local_RAM[51]==1u) {nxt=0xf03034u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],32u);}
else if(s.local_RAM[50]==19u&&s.local_RAM[51]==199u) {nxt=0xf03034u;s.pc=nxt;s.registers[s.active_bank][7]=sub(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][30]);}
else if(s.local_RAM[50]==228u&&s.local_RAM[51]==0u) {nxt=0xf03034u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03034u:
if(s.local_RAM[52]==152u&&s.local_RAM[53]==0u&&s.local_RAM[54]==51u&&s.local_RAM[55]==128u&&s.local_RAM[56]==0u&&s.local_RAM[57]==240u) {nxt=0xf0303au;s.pc=nxt;s.registers[s.active_bank][0]=0xf03380u;}
else if(s.local_RAM[52]==152u&&s.local_RAM[53]==4u&&s.local_RAM[54]==48u&&s.local_RAM[55]==64u&&s.local_RAM[56]==0u&&s.local_RAM[57]==240u) {nxt=0xf0303au;s.pc=nxt;s.registers[s.active_bank][4]=0xf03040u;}
else if(s.local_RAM[52]==164u&&s.local_RAM[53]==61u) {nxt=0xf03036u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][29]=v;}
else if(s.local_RAM[52]==212u&&s.local_RAM[53]==84u) {nxt=0xf03036u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf0303au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03036u:
if(s.local_RAM[54]==147u&&s.local_RAM[55]==189u) {nxt=0xf03038u;s.pc=nxt;s.registers[1u-s.active_bank][29]=s.registers[s.active_bank][29];}
else if(s.local_RAM[54]==228u&&s.local_RAM[55]==0u) {nxt=0xf03038u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03038u:
if(s.local_RAM[56]==32u&&s.local_RAM[57]==7u) {nxt=0xf0303au;s.pc=nxt;s.registers[s.active_bank][7]=sub(&s,0,s.registers[s.active_bank][7]);}
else if(s.local_RAM[56]==163u&&s.local_RAM[57]==187u) {nxt=0xf0303au;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][29],&v));s.registers[s.active_bank][27]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0303au:
if(s.local_RAM[58]==99u&&s.local_RAM[59]==159u) {nxt=0xf0303cu;s.pc=nxt;s.c=s.registers[s.active_bank][31]>>31;s.registers[s.active_bank][31]=s.registers[s.active_bank][31]<<4;zn(&s,s.registers[s.active_bank][31]);}
else if(s.local_RAM[58]==152u&&s.local_RAM[59]==0u&&s.local_RAM[60]==48u&&s.local_RAM[61]==172u&&s.local_RAM[62]==0u&&s.local_RAM[63]==240u) {nxt=0xf03040u;s.pc=nxt;s.registers[s.active_bank][0]=0xf030acu;}
else if(s.local_RAM[58]==152u&&s.local_RAM[59]==5u&&s.local_RAM[60]==48u&&s.local_RAM[61]==0u&&s.local_RAM[62]==0u&&s.local_RAM[63]==0u) {nxt=0xf03040u;s.pc=nxt;s.registers[s.active_bank][5]=0x3000u;}
else if(s.local_RAM[58]==208u&&s.local_RAM[59]==0u) {nxt=0xf0303cu;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0303cu:
if(s.local_RAM[60]==43u&&s.local_RAM[61]==231u) {nxt=0xf0303eu;s.pc=nxt;s.registers[s.active_bank][7]|=s.registers[s.active_bank][31];
   zn(&s,s.registers[s.active_bank][7]);}
else if(s.local_RAM[60]==228u&&s.local_RAM[61]==0u) {nxt=0xf0303eu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0303eu:
if(s.local_RAM[62]==99u&&s.local_RAM[63]==7u) {nxt=0xf03040u;s.pc=nxt;s.c=s.registers[s.active_bank][7]>>31;s.registers[s.active_bank][7]=s.registers[s.active_bank][7]<<8;zn(&s,s.registers[s.active_bank][7]);}
else if(s.local_RAM[62]==163u&&s.local_RAM[63]==16u) {nxt=0xf03040u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][24],&v));s.registers[s.active_bank][16]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03040u:
if(s.local_RAM[64]==124u&&s.local_RAM[65]==27u) {nxt=0xf03042u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][27],0x0u);}
else if(s.local_RAM[64]==136u&&s.local_RAM[65]==52u) {nxt=0xf03042u;s.pc=nxt;s.registers[s.active_bank][20]=s.registers[s.active_bank][1];}
else if(s.local_RAM[64]==152u&&s.local_RAM[65]==0u&&s.local_RAM[66]==0u&&s.local_RAM[67]==4u&&s.local_RAM[68]==0u&&s.local_RAM[69]==0u) {nxt=0xf03046u;s.pc=nxt;s.registers[s.active_bank][0]=0x4u;}
else if(s.local_RAM[64]==152u&&s.local_RAM[65]==10u&&s.local_RAM[66]==3u&&s.local_RAM[67]==0u&&s.local_RAM[68]==0u&&s.local_RAM[69]==0u) {nxt=0xf03046u;s.pc=nxt;s.registers[s.active_bank][10]=0x300u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03042u:
if(s.local_RAM[66]==140u&&s.local_RAM[67]==117u) {nxt=0xf03044u;s.pc=nxt;s.registers[s.active_bank][21]=3u;}
else if(s.local_RAM[66]==208u&&s.local_RAM[67]==24u) {nxt=0xf03044u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03044u:
if(s.local_RAM[68]==46u&&s.local_RAM[69]==214u) {nxt=0xf03046u;s.pc=nxt;s.registers[s.active_bank][22]^=s.registers[s.active_bank][22];zn(&s,s.registers[s.active_bank][22]);}
else if(s.local_RAM[68]==228u&&s.local_RAM[69]==0u) {nxt=0xf03046u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03046u:
if(s.local_RAM[70]==2u&&s.local_RAM[71]==64u) {nxt=0xf03048u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[70]==8u&&s.local_RAM[71]==88u) {nxt=0xf03048u;s.pc=nxt;s.registers[s.active_bank][24]=add(&s,s.registers[s.active_bank][24],2u);}
else if(s.local_RAM[70]==140u&&s.local_RAM[71]==161u) {nxt=0xf03048u;s.pc=nxt;s.registers[s.active_bank][1]=5u;}
else if(s.local_RAM[70]==166u&&s.local_RAM[71]==151u) {nxt=0xf03048u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],&v));s.registers[s.active_bank][23]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03048u:
if(s.local_RAM[72]==8u&&s.local_RAM[73]==148u) {nxt=0xf0304au;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],4u);}
else if(s.local_RAM[72]==16u&&s.local_RAM[73]==65u) {nxt=0xf0304au;s.pc=nxt;s.registers[s.active_bank][1]=sub(&s,s.registers[s.active_bank][1],s.registers[s.active_bank][2]);}
else if(s.local_RAM[72]==152u&&s.local_RAM[73]==0u&&s.local_RAM[74]==63u&&s.local_RAM[75]==64u&&s.local_RAM[76]==0u&&s.local_RAM[77]==240u) {nxt=0xf0304eu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f40u;}
else if(s.local_RAM[72]==164u&&s.local_RAM[73]==23u) {nxt=0xf0304au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][23]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0304au:
if(s.local_RAM[74]==24u&&s.local_RAM[75]==53u) {nxt=0xf0304cu;s.pc=nxt;s.registers[s.active_bank][21]=sub(&s,s.registers[s.active_bank][21],1u);}
else if(s.local_RAM[74]==102u&&s.local_RAM[75]==23u) {nxt=0xf0304cu;s.pc=nxt;s.c=s.registers[s.active_bank][23]&1u;s.registers[s.active_bank][23]=s.registers[s.active_bank][23]>>16;zn(&s,s.registers[s.active_bank][23]);}
else if(s.local_RAM[74]==120u&&s.local_RAM[75]==59u) {nxt=0xf0304cu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][27],s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0304cu:
if(s.local_RAM[76]==152u&&s.local_RAM[77]==0u&&s.local_RAM[78]==0u&&s.local_RAM[79]==8u&&s.local_RAM[80]==0u&&s.local_RAM[81]==0u) {nxt=0xf03052u;s.pc=nxt;s.registers[s.active_bank][0]=0x8u;}
else if(s.local_RAM[76]==208u&&s.local_RAM[77]==1u) {nxt=0xf0304eu;s.pc=nxt;if(condition(&s,1)){pending=1;target=s.registers[s.active_bank][0];}}
else if(s.local_RAM[76]==215u&&s.local_RAM[77]==148u) {nxt=0xf0304eu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf03046u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0304eu:
if(s.local_RAM[78]==2u&&s.local_RAM[79]==246u) {nxt=0xf03050u;s.pc=nxt;s.registers[s.active_bank][22]=add(&s,s.registers[s.active_bank][22],s.registers[s.active_bank][23]);}
else if(s.local_RAM[78]==8u&&s.local_RAM[79]==93u) {nxt=0xf03050u;s.pc=nxt;s.registers[s.active_bank][29]=add(&s,s.registers[s.active_bank][29],2u);}
else if(s.local_RAM[78]==163u&&s.local_RAM[79]==19u) {nxt=0xf03050u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][24],&v));s.registers[s.active_bank][19]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03050u:
if(s.local_RAM[80]==100u&&s.local_RAM[81]==86u) {nxt=0xf03052u;s.pc=nxt;s.c=s.registers[s.active_bank][22]&1u;s.registers[s.active_bank][22]=s.registers[s.active_bank][22]>>2;zn(&s,s.registers[s.active_bank][22]);}
else if(s.local_RAM[80]==152u&&s.local_RAM[81]==15u&&s.local_RAM[82]==1u&&s.local_RAM[83]==126u&&s.local_RAM[84]==0u&&s.local_RAM[85]==0u) {nxt=0xf03056u;s.pc=nxt;s.registers[s.active_bank][15]=0x17eu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03052u:
if(s.local_RAM[82]==2u&&s.local_RAM[83]==64u) {nxt=0xf03054u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[82]==138u&&s.local_RAM[83]==198u) {nxt=0xf03054u;s.pc=nxt;s.registers[s.active_bank][6]=s.registers[s.active_bank][22];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03054u:
if(s.local_RAM[84]==164u&&s.local_RAM[85]==7u) {nxt=0xf03056u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][7]=v;}
else if(s.local_RAM[84]==164u&&s.local_RAM[85]==24u) {nxt=0xf03056u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][24]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03056u:
if(s.local_RAM[86]==8u&&s.local_RAM[87]==88u) {nxt=0xf03058u;s.pc=nxt;s.registers[s.active_bank][24]=add(&s,s.registers[s.active_bank][24],2u);}
else if(s.local_RAM[86]==47u&&s.local_RAM[87]==57u) {nxt=0xf03058u;s.pc=nxt;s.registers[s.active_bank][25]^=s.registers[s.active_bank][25];zn(&s,s.registers[s.active_bank][25]);}
else if(s.local_RAM[86]==102u&&s.local_RAM[87]==24u) {nxt=0xf03058u;s.pc=nxt;s.c=s.registers[s.active_bank][24]&1u;s.registers[s.active_bank][24]=s.registers[s.active_bank][24]>>16;zn(&s,s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03058u:
if(s.local_RAM[88]==136u&&s.local_RAM[89]==26u) {nxt=0xf0305au;s.pc=nxt;s.registers[s.active_bank][26]=s.registers[s.active_bank][0];}
else if(s.local_RAM[88]==152u&&s.local_RAM[89]==29u&&s.local_RAM[90]==52u&&s.local_RAM[91]==246u&&s.local_RAM[92]==0u&&s.local_RAM[93]==240u) {nxt=0xf0305eu;s.pc=nxt;s.registers[s.active_bank][29]=0xf034f6u;}
else if(s.local_RAM[88]==164u&&s.local_RAM[89]==23u) {nxt=0xf0305au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][23]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0305au:
if(s.local_RAM[90]==8u&&s.local_RAM[91]==154u) {nxt=0xf0305cu;s.pc=nxt;s.registers[s.active_bank][26]=add(&s,s.registers[s.active_bank][26],4u);}
else if(s.local_RAM[90]==152u&&s.local_RAM[91]==0u&&s.local_RAM[92]==0u&&s.local_RAM[93]==36u&&s.local_RAM[94]==0u&&s.local_RAM[95]==0u) {nxt=0xf03060u;s.pc=nxt;s.registers[s.active_bank][0]=0x24u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0305cu:
if(s.local_RAM[92]==167u&&s.local_RAM[93]==91u) {nxt=0xf0305eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][26])?(s.registers[s.active_bank][26]&~3u):s.registers[s.active_bank][26],&v));s.registers[s.active_bank][27]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0305eu:
if(s.local_RAM[94]==8u&&s.local_RAM[95]==154u) {nxt=0xf03060u;s.pc=nxt;s.registers[s.active_bank][26]=add(&s,s.registers[s.active_bank][26],4u);}
else if(s.local_RAM[94]==152u&&s.local_RAM[95]==11u&&s.local_RAM[96]==1u&&s.local_RAM[97]==128u&&s.local_RAM[98]==0u&&s.local_RAM[99]==0u) {nxt=0xf03064u;s.pc=nxt;s.registers[s.active_bank][11]=0x180u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03060u:
if(s.local_RAM[96]==0u&&s.local_RAM[97]==96u) {nxt=0xf03062u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[96]==167u&&s.local_RAM[97]==92u) {nxt=0xf03062u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][26])?(s.registers[s.active_bank][26]&~3u):s.registers[s.active_bank][26],&v));s.registers[s.active_bank][28]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03062u:
if(s.local_RAM[98]==123u&&s.local_RAM[99]==103u) {nxt=0xf03064u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][27]);}
else if(s.local_RAM[98]==164u&&s.local_RAM[99]==17u) {nxt=0xf03064u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][17]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03064u:
if(s.local_RAM[100]==152u&&s.local_RAM[101]==0u&&s.local_RAM[102]==0u&&s.local_RAM[103]==40u&&s.local_RAM[104]==0u&&s.local_RAM[105]==0u) {nxt=0xf0306au;s.pc=nxt;s.registers[s.active_bank][0]=0x28u;}
else if(s.local_RAM[100]==152u&&s.local_RAM[101]==12u&&s.local_RAM[102]==1u&&s.local_RAM[103]==128u&&s.local_RAM[104]==0u&&s.local_RAM[105]==0u) {nxt=0xf0306au;s.pc=nxt;s.registers[s.active_bank][12]=0x180u;}
else if(s.local_RAM[100]==212u&&s.local_RAM[101]==148u) {nxt=0xf03066u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf0306eu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03066u:
if(s.local_RAM[102]==123u&&s.local_RAM[103]==124u) {nxt=0xf03068u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0306au:
if(s.local_RAM[106]==0u&&s.local_RAM[107]==96u) {nxt=0xf0306cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[106]==152u&&s.local_RAM[107]==0u&&s.local_RAM[108]==0u&&s.local_RAM[109]==152u&&s.local_RAM[110]==0u&&s.local_RAM[111]==0u) {nxt=0xf03070u;s.pc=nxt;s.registers[s.active_bank][0]=0x98u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0306cu:
if(s.local_RAM[108]==164u&&s.local_RAM[109]==18u) {nxt=0xf0306eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][18]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0306eu:
if(s.local_RAM[110]==8u&&s.local_RAM[111]==129u) {nxt=0xf03070u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else if(s.local_RAM[110]==102u&&s.local_RAM[111]==17u) {nxt=0xf03070u;s.pc=nxt;s.c=s.registers[s.active_bank][17]&1u;s.registers[s.active_bank][17]=s.registers[s.active_bank][17]>>16;zn(&s,s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03070u:
if(s.local_RAM[112]==2u&&s.local_RAM[113]==64u) {nxt=0xf03072u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[112]==102u&&s.local_RAM[113]==18u) {nxt=0xf03072u;s.pc=nxt;s.c=s.registers[s.active_bank][18]&1u;s.registers[s.active_bank][18]=s.registers[s.active_bank][18]>>16;zn(&s,s.registers[s.active_bank][18]);}
else if(s.local_RAM[112]==191u&&s.local_RAM[113]==25u) {nxt=0xf03072u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][24])?(s.registers[s.active_bank][24]&~3u):s.registers[s.active_bank][24],s.registers[s.active_bank][25]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03072u:
if(s.local_RAM[114]==16u&&s.local_RAM[115]==167u) {nxt=0xf03074u;s.pc=nxt;s.registers[s.active_bank][7]=sub(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][5]);}
else if(s.local_RAM[114]==138u&&s.local_RAM[115]==0u) {nxt=0xf03074u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][16];}
else if(s.local_RAM[114]==164u&&s.local_RAM[115]==1u) {nxt=0xf03074u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03074u:
if(s.local_RAM[116]==138u&&s.local_RAM[117]==97u) {nxt=0xf03076u;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][19];}
else if(s.local_RAM[116]==152u&&s.local_RAM[117]==0u&&s.local_RAM[118]==63u&&s.local_RAM[119]==96u&&s.local_RAM[120]==0u&&s.local_RAM[121]==240u) {nxt=0xf0307au;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else if(s.local_RAM[116]==212u&&s.local_RAM[117]==84u) {nxt=0xf03076u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf0307au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03076u:
if(s.local_RAM[118]==8u&&s.local_RAM[119]==152u) {nxt=0xf03078u;s.pc=nxt;s.registers[s.active_bank][24]=add(&s,s.registers[s.active_bank][24],4u);}
else if(s.local_RAM[118]==99u&&s.local_RAM[119]==128u) {nxt=0xf03078u;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<4;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03078u:
if(s.local_RAM[120]==44u&&s.local_RAM[121]==231u) {nxt=0xf0307au;s.pc=nxt;s.registers[s.active_bank][7]^=s.registers[s.active_bank][7];zn(&s,s.registers[s.active_bank][7]);}
else if(s.local_RAM[120]==100u&&s.local_RAM[121]==33u) {nxt=0xf0307au;s.pc=nxt;s.c=s.registers[s.active_bank][1]&1u;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]>>1;zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0307au:
if(s.local_RAM[122]==16u&&s.local_RAM[123]==17u) {nxt=0xf0307cu;s.pc=nxt;s.registers[s.active_bank][17]=sub(&s,s.registers[s.active_bank][17],s.registers[s.active_bank][0]);}
else if(s.local_RAM[122]==102u&&s.local_RAM[123]==1u) {nxt=0xf0307cu;s.pc=nxt;s.c=s.registers[s.active_bank][1]&1u;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]>>16;zn(&s,s.registers[s.active_bank][1]);}
else if(s.local_RAM[122]==120u&&s.local_RAM[123]==199u) {nxt=0xf0307cu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0307cu:
if(s.local_RAM[124]==16u&&s.local_RAM[125]==50u) {nxt=0xf0307eu;s.pc=nxt;s.registers[s.active_bank][18]=sub(&s,s.registers[s.active_bank][18],s.registers[s.active_bank][1]);}
else if(s.local_RAM[124]==164u&&s.local_RAM[125]==2u) {nxt=0xf0307eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][2]=v;}
else if(s.local_RAM[124]==212u&&s.local_RAM[125]==84u) {nxt=0xf0307eu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf03082u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0307eu:
if(s.local_RAM[126]==8u&&s.local_RAM[127]==130u) {nxt=0xf03080u;s.pc=nxt;s.registers[s.active_bank][2]=add(&s,s.registers[s.active_bank][2],4u);}
else if(s.local_RAM[126]==152u&&s.local_RAM[127]==0u&&s.local_RAM[128]==0u&&s.local_RAM[129]==84u&&s.local_RAM[130]==0u&&s.local_RAM[131]==0u) {nxt=0xf03084u;s.pc=nxt;s.registers[s.active_bank][0]=0x54u;}
else if(s.local_RAM[126]==228u&&s.local_RAM[127]==0u) {nxt=0xf03080u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03080u:
if(s.local_RAM[128]==164u&&s.local_RAM[129]==64u) {nxt=0xf03082u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][2])?(s.registers[s.active_bank][2]&~3u):s.registers[s.active_bank][2],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03082u:
if(s.local_RAM[130]==184u&&s.local_RAM[131]==1u) {nxt=0xf03084u;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][0],s.registers[s.active_bank][1]));}
else if(s.local_RAM[130]==188u&&s.local_RAM[131]==7u) {nxt=0xf03084u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][7]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03084u:
if(s.local_RAM[132]==0u&&s.local_RAM[133]==96u) {nxt=0xf03086u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[132]==24u&&s.local_RAM[133]==34u) {nxt=0xf03086u;s.pc=nxt;s.registers[s.active_bank][2]=sub(&s,s.registers[s.active_bank][2],1u);}
else if(s.local_RAM[132]==152u&&s.local_RAM[133]==0u&&s.local_RAM[134]==0u&&s.local_RAM[135]==44u&&s.local_RAM[136]==0u&&s.local_RAM[137]==0u) {nxt=0xf0308au;s.pc=nxt;s.registers[s.active_bank][0]=0x2cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03086u:
if(s.local_RAM[134]==164u&&s.local_RAM[135]==27u) {nxt=0xf03088u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][27]=v;}
else if(s.local_RAM[134]==208u&&s.local_RAM[135]==148u) {nxt=0xf03088u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][4];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03088u:
if(s.local_RAM[136]==8u&&s.local_RAM[137]==128u) {nxt=0xf0308au;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],4u);}
else if(s.local_RAM[136]==152u&&s.local_RAM[137]==0u&&s.local_RAM[138]==0u&&s.local_RAM[139]==184u&&s.local_RAM[140]==0u&&s.local_RAM[141]==0u) {nxt=0xf0308eu;s.pc=nxt;s.registers[s.active_bank][0]=0xb8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0308au:
if(s.local_RAM[138]==2u&&s.local_RAM[139]==64u) {nxt=0xf0308cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[138]==152u&&s.local_RAM[139]==3u&&s.local_RAM[140]==54u&&s.local_RAM[141]==90u&&s.local_RAM[142]==0u&&s.local_RAM[143]==240u) {nxt=0xf03090u;s.pc=nxt;s.registers[s.active_bank][3]=0xf0365au;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0308cu:
if(s.local_RAM[140]==164u&&s.local_RAM[141]==3u) {nxt=0xf0308eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][3]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0308eu:
if(s.local_RAM[142]==0u&&s.local_RAM[143]==96u) {nxt=0xf03090u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[142]==152u&&s.local_RAM[143]==0u&&s.local_RAM[144]==0u&&s.local_RAM[145]==48u&&s.local_RAM[146]==0u&&s.local_RAM[147]==0u) {nxt=0xf03094u;s.pc=nxt;s.registers[s.active_bank][0]=0x30u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03090u:
if(s.local_RAM[144]==164u&&s.local_RAM[145]==9u) {nxt=0xf03092u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][9]=v;}
else if(s.local_RAM[144]==204u&&s.local_RAM[145]==30u) {nxt=0xf03092u;s.pc=nxt;s.registers[s.active_bank][30]=0xf03090u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03092u:
if(s.local_RAM[146]==101u&&s.local_RAM[147]==27u) {nxt=0xf03094u;s.pc=nxt;s.c=s.registers[s.active_bank][27]&1u;s.registers[s.active_bank][27]=s.registers[s.active_bank][27]>>8;zn(&s,s.registers[s.active_bank][27]);}
else if(s.local_RAM[146]==208u&&s.local_RAM[147]==96u) {nxt=0xf03094u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][3];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03094u:
if(s.local_RAM[148]==2u&&s.local_RAM[149]==64u) {nxt=0xf03096u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[148]==8u&&s.local_RAM[149]==222u) {nxt=0xf03096u;s.pc=nxt;s.registers[s.active_bank][30]=add(&s,s.registers[s.active_bank][30],6u);}
else if(s.local_RAM[148]==152u&&s.local_RAM[149]==0u&&s.local_RAM[150]==0u&&s.local_RAM[151]==188u&&s.local_RAM[152]==0u&&s.local_RAM[153]==0u) {nxt=0xf0309au;s.pc=nxt;s.registers[s.active_bank][0]=0xbcu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03096u:
if(s.local_RAM[150]==152u&&s.local_RAM[151]==0u&&s.local_RAM[152]==63u&&s.local_RAM[153]==96u&&s.local_RAM[154]==0u&&s.local_RAM[155]==240u) {nxt=0xf0309cu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else if(s.local_RAM[150]==164u&&s.local_RAM[151]==4u) {nxt=0xf03098u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03098u:
if(s.local_RAM[152]==102u&&s.local_RAM[153]==3u) {nxt=0xf0309au;s.pc=nxt;s.c=s.registers[s.active_bank][3]&1u;s.registers[s.active_bank][3]=s.registers[s.active_bank][3]>>16;zn(&s,s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0309au:
if(s.local_RAM[154]==0u&&s.local_RAM[155]==96u) {nxt=0xf0309cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[154]==102u&&s.local_RAM[155]==4u) {nxt=0xf0309cu;s.pc=nxt;s.c=s.registers[s.active_bank][4]&1u;s.registers[s.active_bank][4]=s.registers[s.active_bank][4]>>16;zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0309cu:
if(s.local_RAM[156]==18u&&s.local_RAM[157]==235u) {nxt=0xf0309eu;s.pc=nxt;s.registers[s.active_bank][11]=sub(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][23]);}
else if(s.local_RAM[156]==164u&&s.local_RAM[157]==1u) {nxt=0xf0309eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[156]==164u&&s.local_RAM[157]==11u) {nxt=0xf0309eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][11]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0309eu:
if(s.local_RAM[158]==8u&&s.local_RAM[159]==1u) {nxt=0xf030a0u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],32u);}
else if(s.local_RAM[158]==19u&&s.local_RAM[159]==12u) {nxt=0xf030a0u;s.pc=nxt;s.registers[s.active_bank][12]=sub(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][24]);}
else if(s.local_RAM[158]==152u&&s.local_RAM[159]==0u&&s.local_RAM[160]==0u&&s.local_RAM[161]==216u&&s.local_RAM[162]==0u&&s.local_RAM[163]==0u) {nxt=0xf030a4u;s.pc=nxt;s.registers[s.active_bank][0]=0xd8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030a0u:
if(s.local_RAM[160]==9u&&s.local_RAM[161]==129u) {nxt=0xf030a2u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],12u);}
else if(s.local_RAM[160]==100u&&s.local_RAM[161]==43u) {nxt=0xf030a2u;s.pc=nxt;s.c=s.registers[s.active_bank][11]&1u;s.registers[s.active_bank][11]=s.registers[s.active_bank][11]>>1;zn(&s,s.registers[s.active_bank][11]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030a2u:
if(s.local_RAM[162]==100u&&s.local_RAM[163]==44u) {nxt=0xf030a4u;s.pc=nxt;s.c=s.registers[s.active_bank][12]&1u;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]>>1;zn(&s,s.registers[s.active_bank][12]);}
else if(s.local_RAM[162]==164u&&s.local_RAM[163]==32u) {nxt=0xf030a4u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030a4u:
if(s.local_RAM[164]==0u&&s.local_RAM[165]==96u) {nxt=0xf030a6u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[164]==8u&&s.local_RAM[165]==129u) {nxt=0xf030a6u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else if(s.local_RAM[164]==152u&&s.local_RAM[165]==27u&&s.local_RAM[166]==0u&&s.local_RAM[167]==192u&&s.local_RAM[168]==0u&&s.local_RAM[169]==0u) {nxt=0xf030aau;s.pc=nxt;s.registers[s.active_bank][27]=0xc0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030a6u:
if(s.local_RAM[166]==164u&&s.local_RAM[167]==12u) {nxt=0xf030a8u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][12]=v;}
else if(s.local_RAM[166]==164u&&s.local_RAM[167]==34u) {nxt=0xf030a8u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030a8u:
if(s.local_RAM[168]==152u&&s.local_RAM[169]==0u&&s.local_RAM[170]==0u&&s.local_RAM[171]==220u&&s.local_RAM[172]==0u&&s.local_RAM[173]==0u) {nxt=0xf030aeu;s.pc=nxt;s.registers[s.active_bank][0]=0xdcu;}
else if(s.local_RAM[168]==160u&&s.local_RAM[169]==67u) {nxt=0xf030aau;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][2],&v));s.registers[s.active_bank][3]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030aau:
if(s.local_RAM[170]==124u&&s.local_RAM[171]==3u) {nxt=0xf030acu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][3],0x0u);}
else if(s.local_RAM[170]==152u&&s.local_RAM[171]==26u&&s.local_RAM[172]==48u&&s.local_RAM[173]==224u&&s.local_RAM[174]==0u&&s.local_RAM[175]==240u) {nxt=0xf030b0u;s.pc=nxt;s.registers[s.active_bank][26]=0xf030e0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030acu:
if(s.local_RAM[172]==44u&&s.local_RAM[173]==33u) {nxt=0xf030aeu;s.pc=nxt;s.registers[s.active_bank][1]^=s.registers[s.active_bank][1];zn(&s,s.registers[s.active_bank][1]);}
else if(s.local_RAM[172]==212u&&s.local_RAM[173]==194u) {nxt=0xf030aeu;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf030bau;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030aeu:
if(s.local_RAM[174]==0u&&s.local_RAM[175]==96u) {nxt=0xf030b0u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[174]==152u&&s.local_RAM[175]==14u&&s.local_RAM[176]==63u&&s.local_RAM[177]==128u&&s.local_RAM[178]==0u&&s.local_RAM[179]==240u) {nxt=0xf030b4u;s.pc=nxt;s.registers[s.active_bank][14]=0xf03f80u;}
else if(s.local_RAM[174]==228u&&s.local_RAM[175]==0u) {nxt=0xf030b0u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030b0u:
if(s.local_RAM[176]==139u&&s.local_RAM[177]==124u) {nxt=0xf030b2u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][27];}
else if(s.local_RAM[176]==152u&&s.local_RAM[177]==1u&&s.local_RAM[178]==49u&&s.local_RAM[179]==118u&&s.local_RAM[180]==0u&&s.local_RAM[181]==240u) {nxt=0xf030b6u;s.pc=nxt;s.registers[s.active_bank][1]=0xf03176u;}
else if(s.local_RAM[176]==164u&&s.local_RAM[177]==13u) {nxt=0xf030b2u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][13]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030b2u:
if(s.local_RAM[178]==19u&&s.local_RAM[179]==99u) {nxt=0xf030b4u;s.pc=nxt;s.registers[s.active_bank][3]=sub(&s,s.registers[s.active_bank][3],s.registers[s.active_bank][27]);}
else if(s.local_RAM[178]==152u&&s.local_RAM[179]==0u&&s.local_RAM[180]==0u&&s.local_RAM[181]==224u&&s.local_RAM[182]==0u&&s.local_RAM[183]==0u) {nxt=0xf030b8u;s.pc=nxt;s.registers[s.active_bank][0]=0xe0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030b4u:
if(s.local_RAM[180]==3u&&s.local_RAM[181]==124u) {nxt=0xf030b6u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][27]);}
else if(s.local_RAM[180]==174u&&s.local_RAM[181]==160u) {nxt=0xf030b6u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+84u,&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030b6u:
if(s.local_RAM[182]==19u&&s.local_RAM[183]==100u) {nxt=0xf030b8u;s.pc=nxt;s.registers[s.active_bank][4]=sub(&s,s.registers[s.active_bank][4],s.registers[s.active_bank][27]);}
else if(s.local_RAM[182]==208u&&s.local_RAM[183]==0u) {nxt=0xf030b8u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else if(s.local_RAM[182]==208u&&s.local_RAM[183]==32u) {nxt=0xf030b8u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][1];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030b8u:
if(s.local_RAM[184]==0u&&s.local_RAM[185]==96u) {nxt=0xf030bau;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[184]==0u&&s.local_RAM[185]==107u) {nxt=0xf030bau;s.pc=nxt;s.registers[s.active_bank][11]=add(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][3]);}
else if(s.local_RAM[184]==228u&&s.local_RAM[185]==0u) {nxt=0xf030bau;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030bau:
if(s.local_RAM[186]==164u&&s.local_RAM[187]==7u) {nxt=0xf030bcu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][7]=v;}
else if(s.local_RAM[186]==211u&&s.local_RAM[187]==88u) {nxt=0xf030bcu;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][26];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030bcu:
if(s.local_RAM[188]==152u&&s.local_RAM[189]==0u&&s.local_RAM[190]==0u&&s.local_RAM[191]==228u&&s.local_RAM[192]==0u&&s.local_RAM[193]==0u) {nxt=0xf030c2u;s.pc=nxt;s.registers[s.active_bank][0]=0xe4u;}
else if(s.local_RAM[188]==228u&&s.local_RAM[189]==0u) {nxt=0xf030beu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030beu:
if(s.local_RAM[190]==123u&&s.local_RAM[191]==139u) {nxt=0xf030c0u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030c0u:
if(s.local_RAM[192]==211u&&s.local_RAM[193]==180u) {nxt=0xf030c2u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030c2u:
if(s.local_RAM[194]==0u&&s.local_RAM[195]==96u) {nxt=0xf030c4u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[194]==228u&&s.local_RAM[195]==0u) {nxt=0xf030c4u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030c4u:
if(s.local_RAM[196]==152u&&s.local_RAM[197]==26u&&s.local_RAM[198]==48u&&s.local_RAM[199]==238u&&s.local_RAM[200]==0u&&s.local_RAM[201]==240u) {nxt=0xf030cau;s.pc=nxt;s.registers[s.active_bank][26]=0xf030eeu;}
else if(s.local_RAM[196]==164u&&s.local_RAM[197]==8u) {nxt=0xf030c6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][8]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030c6u:
if(s.local_RAM[198]==138u&&s.local_RAM[199]==84u) {nxt=0xf030c8u;s.pc=nxt;s.registers[s.active_bank][20]=s.registers[s.active_bank][18];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030c8u:
if(s.local_RAM[200]==138u&&s.local_RAM[201]==33u) {nxt=0xf030cau;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][17];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030cau:
if(s.local_RAM[202]==65u&&s.local_RAM[203]==84u) {nxt=0xf030ccu;s.pc=nxt;s.registers[s.active_bank][20]=(s.registers[s.active_bank][20]&0xffffu)*(s.registers[s.active_bank][10]&0xffffu);
   zn(&s,s.registers[s.active_bank][20]);}
else if(s.local_RAM[202]==152u&&s.local_RAM[203]==25u&&s.local_RAM[204]==48u&&s.local_RAM[205]==242u&&s.local_RAM[206]==0u&&s.local_RAM[207]==240u) {nxt=0xf030d0u;s.pc=nxt;s.registers[s.active_bank][25]=0xf030f2u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030ccu:
if(s.local_RAM[204]==99u&&s.local_RAM[205]==225u) {nxt=0xf030ceu;s.pc=nxt;s.c=s.registers[s.active_bank][1]>>31;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]<<1;zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030ceu:
if(s.local_RAM[206]==2u&&s.local_RAM[207]==244u) {nxt=0xf030d0u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],s.registers[s.active_bank][23]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030d0u:
if(s.local_RAM[208]==0u&&s.local_RAM[209]==52u) {nxt=0xf030d2u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],s.registers[s.active_bank][1]);}
else if(s.local_RAM[208]==0u&&s.local_RAM[209]==140u) {nxt=0xf030d2u;s.pc=nxt;s.registers[s.active_bank][12]=add(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030d2u:
if(s.local_RAM[210]==146u&&s.local_RAM[211]==148u) {nxt=0xf030d4u;s.pc=nxt;s.registers[1u-s.active_bank][20]=s.registers[s.active_bank][20];}
else if(s.local_RAM[210]==211u&&s.local_RAM[211]==88u) {nxt=0xf030d4u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][26];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030d4u:
if(s.local_RAM[212]==144u&&s.local_RAM[213]==231u) {nxt=0xf030d6u;s.pc=nxt;s.registers[1u-s.active_bank][7]=s.registers[s.active_bank][7];}
else if(s.local_RAM[212]==228u&&s.local_RAM[213]==0u) {nxt=0xf030d6u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030d6u:
if(s.local_RAM[214]==123u&&s.local_RAM[215]==140u) {nxt=0xf030d8u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][28]);}
else if(s.local_RAM[214]==145u&&s.local_RAM[215]==8u) {nxt=0xf030d8u;s.pc=nxt;s.registers[1u-s.active_bank][8]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030d8u:
if(s.local_RAM[216]==146u&&s.local_RAM[217]==16u) {nxt=0xf030dau;s.pc=nxt;s.registers[1u-s.active_bank][16]=s.registers[s.active_bank][16];}
else if(s.local_RAM[216]==211u&&s.local_RAM[217]==180u) {nxt=0xf030dau;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030dau:
if(s.local_RAM[218]==143u&&s.local_RAM[219]==246u) {nxt=0xf030dcu;s.pc=nxt;s.registers[s.active_bank][22]=31u;}
else if(s.local_RAM[218]==228u&&s.local_RAM[219]==0u) {nxt=0xf030dcu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030dcu:
if(s.local_RAM[220]==167u&&s.local_RAM[221]==26u) {nxt=0xf030deu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][24])?(s.registers[s.active_bank][24]&~3u):s.registers[s.active_bank][24],&v));s.registers[s.active_bank][26]=v;}
else if(s.local_RAM[220]==211u&&s.local_RAM[221]==32u) {nxt=0xf030deu;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][25];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030deu:
if(s.local_RAM[222]==152u&&s.local_RAM[223]==0u&&s.local_RAM[224]==63u&&s.local_RAM[225]==92u&&s.local_RAM[226]==0u&&s.local_RAM[227]==240u) {nxt=0xf030e4u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f5cu;}
else if(s.local_RAM[222]==228u&&s.local_RAM[223]==0u) {nxt=0xf030e0u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030e4u:
if(s.local_RAM[228]==164u&&s.local_RAM[229]==1u) {nxt=0xf030e6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030e6u:
if(s.local_RAM[230]==124u&&s.local_RAM[231]==1u) {nxt=0xf030e8u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030e8u:
if(s.local_RAM[232]==212u&&s.local_RAM[233]==193u) {nxt=0xf030eau;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf030f6u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030eau:
if(s.local_RAM[234]==228u&&s.local_RAM[235]==0u) {nxt=0xf030ecu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030f2u:
if(s.local_RAM[242]==152u&&s.local_RAM[243]==28u&&s.local_RAM[244]==1u&&s.local_RAM[245]==128u&&s.local_RAM[246]==0u&&s.local_RAM[247]==0u) {nxt=0xf030f8u;s.pc=nxt;s.registers[s.active_bank][28]=0x180u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030f6u:
if(s.local_RAM[246]==124u&&s.local_RAM[247]==65u) {nxt=0xf030f8u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],0x2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030f8u:
if(s.local_RAM[248]==124u&&s.local_RAM[249]==23u) {nxt=0xf030fau;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][23],0x0u);}
else if(s.local_RAM[248]==212u&&s.local_RAM[249]==193u) {nxt=0xf030fau;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf03106u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030fau:
if(s.local_RAM[250]==211u&&s.local_RAM[251]==162u) {nxt=0xf030fcu;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][29];}}
else if(s.local_RAM[250]==228u&&s.local_RAM[251]==0u) {nxt=0xf030fcu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030fcu:
if(s.local_RAM[252]==152u&&s.local_RAM[253]==0u&&s.local_RAM[254]==50u&&s.local_RAM[255]==132u&&s.local_RAM[256]==0u&&s.local_RAM[257]==240u) {nxt=0xf03102u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03284u;}
else if(s.local_RAM[252]==228u&&s.local_RAM[253]==0u) {nxt=0xf030feu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf030feu:
if(s.local_RAM[254]==211u&&s.local_RAM[255]==184u) {nxt=0xf03100u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03100u:
if(s.local_RAM[256]==228u&&s.local_RAM[257]==0u) {nxt=0xf03102u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03102u:
if(s.local_RAM[258]==124u&&s.local_RAM[259]==24u) {nxt=0xf03104u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][24],0x0u);}
else if(s.local_RAM[258]==208u&&s.local_RAM[259]==0u) {nxt=0xf03104u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03104u:
if(s.local_RAM[260]==211u&&s.local_RAM[261]==162u) {nxt=0xf03106u;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][29];}}
else if(s.local_RAM[260]==228u&&s.local_RAM[261]==0u) {nxt=0xf03106u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03106u:
if(s.local_RAM[262]==228u&&s.local_RAM[263]==0u) {nxt=0xf03108u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03108u:
if(s.local_RAM[264]==211u&&s.local_RAM[265]==184u) {nxt=0xf0310au;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0310au:
if(s.local_RAM[266]==228u&&s.local_RAM[267]==0u) {nxt=0xf0310cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0310cu:
if(s.local_RAM[268]==123u&&s.local_RAM[269]==151u) {nxt=0xf0310eu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][23],s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0310eu:
if(s.local_RAM[270]==211u&&s.local_RAM[271]==180u) {nxt=0xf03110u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03110u:
if(s.local_RAM[272]==228u&&s.local_RAM[273]==0u) {nxt=0xf03112u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03112u:
if(s.local_RAM[274]==123u&&s.local_RAM[275]==152u) {nxt=0xf03114u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][24],s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03114u:
if(s.local_RAM[276]==211u&&s.local_RAM[277]==180u) {nxt=0xf03116u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03116u:
if(s.local_RAM[278]==228u&&s.local_RAM[279]==0u) {nxt=0xf03118u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03118u:
if(s.local_RAM[280]==152u&&s.local_RAM[281]==0u&&s.local_RAM[282]==0u&&s.local_RAM[283]==0u&&s.local_RAM[284]==0u&&s.local_RAM[285]==0u) {nxt=0xf0311eu;s.pc=nxt;s.registers[s.active_bank][0]=0x0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0311eu:
if(s.local_RAM[286]==2u&&s.local_RAM[287]==64u) {nxt=0xf03120u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03120u:
if(s.local_RAM[288]==164u&&s.local_RAM[289]==8u) {nxt=0xf03122u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][8]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03122u:
if(s.local_RAM[290]==152u&&s.local_RAM[291]==16u&&s.local_RAM[292]==1u&&s.local_RAM[293]==128u&&s.local_RAM[294]==0u&&s.local_RAM[295]==0u) {nxt=0xf03128u;s.pc=nxt;s.registers[s.active_bank][16]=0x180u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03128u:
if(s.local_RAM[296]==152u&&s.local_RAM[297]==17u&&s.local_RAM[298]==49u&&s.local_RAM[299]==104u&&s.local_RAM[300]==0u&&s.local_RAM[301]==240u) {nxt=0xf0312eu;s.pc=nxt;s.registers[s.active_bank][17]=0xf03168u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0312eu:
if(s.local_RAM[302]==152u&&s.local_RAM[303]==6u&&s.local_RAM[304]==49u&&s.local_RAM[305]==154u&&s.local_RAM[306]==0u&&s.local_RAM[307]==240u) {nxt=0xf03134u;s.pc=nxt;s.registers[s.active_bank][6]=0xf0319au;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03134u:
if(s.local_RAM[308]==123u&&s.local_RAM[309]==16u) {nxt=0xf03136u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][16],s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03136u:
if(s.local_RAM[310]==210u&&s.local_RAM[311]==34u) {nxt=0xf03138u;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][17];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03138u:
if(s.local_RAM[312]==44u&&s.local_RAM[313]==99u) {nxt=0xf0313au;s.pc=nxt;s.registers[s.active_bank][3]^=s.registers[s.active_bank][3];zn(&s,s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0313au:
if(s.local_RAM[314]==44u&&s.local_RAM[315]==132u) {nxt=0xf0313cu;s.pc=nxt;s.registers[s.active_bank][4]^=s.registers[s.active_bank][4];zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0313cu:
if(s.local_RAM[316]==152u&&s.local_RAM[317]==5u&&s.local_RAM[318]==1u&&s.local_RAM[319]==127u&&s.local_RAM[320]==0u&&s.local_RAM[321]==0u) {nxt=0xf03142u;s.pc=nxt;s.registers[s.active_bank][5]=0x17fu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03142u:
if(s.local_RAM[322]==152u&&s.local_RAM[323]==6u&&s.local_RAM[324]==1u&&s.local_RAM[325]==127u&&s.local_RAM[326]==0u&&s.local_RAM[327]==0u) {nxt=0xf03148u;s.pc=nxt;s.registers[s.active_bank][6]=0x17fu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03148u:
if(s.local_RAM[328]==152u&&s.local_RAM[329]==0u&&s.local_RAM[330]==53u&&s.local_RAM[331]==152u&&s.local_RAM[332]==0u&&s.local_RAM[333]==240u) {nxt=0xf0314eu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03598u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0314eu:
if(s.local_RAM[334]==204u&&s.local_RAM[335]==30u) {nxt=0xf03150u;s.pc=nxt;s.registers[s.active_bank][30]=0xf0314eu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03150u:
if(s.local_RAM[336]==208u&&s.local_RAM[337]==0u) {nxt=0xf03152u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03152u:
if(s.local_RAM[338]==8u&&s.local_RAM[339]==222u) {nxt=0xf03154u;s.pc=nxt;s.registers[s.active_bank][30]=add(&s,s.registers[s.active_bank][30],6u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03154u:
if(s.local_RAM[340]==152u&&s.local_RAM[341]==6u&&s.local_RAM[342]==1u&&s.local_RAM[343]==128u&&s.local_RAM[344]==0u&&s.local_RAM[345]==0u) {nxt=0xf0315au;s.pc=nxt;s.registers[s.active_bank][6]=0x180u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0315au:
if(s.local_RAM[346]==139u&&s.local_RAM[347]==4u) {nxt=0xf0315cu;s.pc=nxt;s.registers[s.active_bank][4]=s.registers[s.active_bank][24];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0315cu:
if(s.local_RAM[348]==1u&&s.local_RAM[349]==132u) {nxt=0xf0315eu;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0315eu:
if(s.local_RAM[350]==44u&&s.local_RAM[351]==99u) {nxt=0xf03160u;s.pc=nxt;s.registers[s.active_bank][3]^=s.registers[s.active_bank][3];zn(&s,s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03160u:
if(s.local_RAM[352]==138u&&s.local_RAM[353]==5u) {nxt=0xf03162u;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][16];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03162u:
if(s.local_RAM[354]==152u&&s.local_RAM[355]==0u&&s.local_RAM[356]==53u&&s.local_RAM[357]==152u&&s.local_RAM[358]==0u&&s.local_RAM[359]==240u) {nxt=0xf03168u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03598u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03168u:
if(s.local_RAM[360]==152u&&s.local_RAM[361]==17u&&s.local_RAM[362]==49u&&s.local_RAM[363]==154u&&s.local_RAM[364]==0u&&s.local_RAM[365]==240u) {nxt=0xf0316eu;s.pc=nxt;s.registers[s.active_bank][17]=0xf0319au;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0316eu:
if(s.local_RAM[366]==122u&&s.local_RAM[367]==240u) {nxt=0xf03170u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][16],s.registers[s.active_bank][23]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03170u:
if(s.local_RAM[368]==210u&&s.local_RAM[369]==34u) {nxt=0xf03172u;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][17];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03172u:
if(s.local_RAM[370]==44u&&s.local_RAM[371]==99u) {nxt=0xf03174u;s.pc=nxt;s.registers[s.active_bank][3]^=s.registers[s.active_bank][3];zn(&s,s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03174u:
if(s.local_RAM[372]==137u&&s.local_RAM[373]==132u) {nxt=0xf03176u;s.pc=nxt;s.registers[s.active_bank][4]=s.registers[s.active_bank][12];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03176u:
if(s.local_RAM[374]==124u&&s.local_RAM[375]==35u) {nxt=0xf03178u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][3],0x1u);}
else if(s.local_RAM[374]==137u&&s.local_RAM[375]==134u) {nxt=0xf03178u;s.pc=nxt;s.registers[s.active_bank][6]=s.registers[s.active_bank][12];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03178u:
if(s.local_RAM[376]==3u&&s.local_RAM[377]==6u) {nxt=0xf0317au;s.pc=nxt;s.registers[s.active_bank][6]=add(&s,s.registers[s.active_bank][6],s.registers[s.active_bank][24]);}
else if(s.local_RAM[376]==215u&&s.local_RAM[377]==2u) {nxt=0xf0317au;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf0316au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0317au:
if(s.local_RAM[378]==137u&&s.local_RAM[379]==101u) {nxt=0xf0317cu;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][11];}
else if(s.local_RAM[378]==228u&&s.local_RAM[379]==0u) {nxt=0xf0317cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0317cu:
if(s.local_RAM[380]==44u&&s.local_RAM[381]==99u) {nxt=0xf0317eu;s.pc=nxt;s.registers[s.active_bank][3]^=s.registers[s.active_bank][3];zn(&s,s.registers[s.active_bank][3]);}
else if(s.local_RAM[380]==152u&&s.local_RAM[381]==0u&&s.local_RAM[382]==53u&&s.local_RAM[383]==152u&&s.local_RAM[384]==0u&&s.local_RAM[385]==240u) {nxt=0xf03182u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03598u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0317eu:
if(s.local_RAM[382]==152u&&s.local_RAM[383]==1u&&s.local_RAM[384]==33u&&s.local_RAM[385]==20u&&s.local_RAM[386]==0u&&s.local_RAM[387]==240u) {nxt=0xf03184u;s.pc=nxt;s.registers[s.active_bank][1]=0xf02114u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03182u:
if(s.local_RAM[386]==152u&&s.local_RAM[387]==5u&&s.local_RAM[388]==1u&&s.local_RAM[389]==128u&&s.local_RAM[390]==0u&&s.local_RAM[391]==0u) {nxt=0xf03188u;s.pc=nxt;s.registers[s.active_bank][5]=0x180u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03184u:
if(s.local_RAM[388]==164u&&s.local_RAM[389]==32u) {nxt=0xf03186u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03186u:
if(s.local_RAM[390]==60u&&s.local_RAM[391]==0u) {nxt=0xf03188u;s.pc=nxt;s.registers[s.active_bank][0]&=~(1u<<0);
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03188u:
if(s.local_RAM[392]==138u&&s.local_RAM[393]==227u) {nxt=0xf0318au;s.pc=nxt;s.registers[s.active_bank][3]=s.registers[s.active_bank][23];}
else if(s.local_RAM[392]==188u&&s.local_RAM[393]==32u) {nxt=0xf0318au;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0318au:
if(s.local_RAM[394]==137u&&s.local_RAM[395]==132u) {nxt=0xf0318cu;s.pc=nxt;s.registers[s.active_bank][4]=s.registers[s.active_bank][12];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0318cu:
if(s.local_RAM[396]==137u&&s.local_RAM[397]==134u) {nxt=0xf0318eu;s.pc=nxt;s.registers[s.active_bank][6]=s.registers[s.active_bank][12];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0318eu:
if(s.local_RAM[398]==1u&&s.local_RAM[399]==99u) {nxt=0xf03190u;s.pc=nxt;s.registers[s.active_bank][3]=add(&s,s.registers[s.active_bank][3],s.registers[s.active_bank][11]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03190u:
if(s.local_RAM[400]==3u&&s.local_RAM[401]==6u) {nxt=0xf03192u;s.pc=nxt;s.registers[s.active_bank][6]=add(&s,s.registers[s.active_bank][6],s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03192u:
if(s.local_RAM[402]==24u&&s.local_RAM[403]==131u) {nxt=0xf03194u;s.pc=nxt;s.registers[s.active_bank][3]=sub(&s,s.registers[s.active_bank][3],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03194u:
if(s.local_RAM[404]==152u&&s.local_RAM[405]==0u&&s.local_RAM[406]==53u&&s.local_RAM[407]==152u&&s.local_RAM[408]==0u&&s.local_RAM[409]==240u) {nxt=0xf0319au;s.pc=nxt;s.registers[s.active_bank][0]=0xf03598u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0319au:
if(s.local_RAM[410]==98u&&s.local_RAM[411]==12u) {nxt=0xf0319cu;s.pc=nxt;s.c=s.registers[s.active_bank][12]>>31;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]<<16;zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0319cu:
if(s.local_RAM[412]==152u&&s.local_RAM[413]==0u&&s.local_RAM[414]==63u&&s.local_RAM[415]==128u&&s.local_RAM[416]==0u&&s.local_RAM[417]==240u) {nxt=0xf031a2u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f80u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031a2u:
if(s.local_RAM[418]==41u&&s.local_RAM[419]==108u) {nxt=0xf031a4u;s.pc=nxt;s.registers[s.active_bank][12]|=s.registers[s.active_bank][11];
   zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031a4u:
if(s.local_RAM[420]==188u&&s.local_RAM[421]==12u) {nxt=0xf031a6u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][12]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031a6u:
if(s.local_RAM[422]==152u&&s.local_RAM[423]==13u&&s.local_RAM[424]==34u&&s.local_RAM[425]==56u&&s.local_RAM[426]==0u&&s.local_RAM[427]==240u) {nxt=0xf031acu;s.pc=nxt;s.registers[s.active_bank][13]=0xf02238u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031acu:
if(s.local_RAM[428]==152u&&s.local_RAM[429]==26u&&s.local_RAM[430]==47u&&s.local_RAM[431]==65u&&s.local_RAM[432]==65u&&s.local_RAM[433]==128u) {nxt=0xf031b2u;s.pc=nxt;s.registers[s.active_bank][26]=0x41802f41u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031b2u:
if(s.local_RAM[434]==152u&&s.local_RAM[435]==14u&&s.local_RAM[436]==34u&&s.local_RAM[437]==0u&&s.local_RAM[438]==0u&&s.local_RAM[439]==240u) {nxt=0xf031b8u;s.pc=nxt;s.registers[s.active_bank][14]=0xf02200u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031b8u:
if(s.local_RAM[440]==152u&&s.local_RAM[441]==15u&&s.local_RAM[442]==34u&&s.local_RAM[443]==36u&&s.local_RAM[444]==0u&&s.local_RAM[445]==240u) {nxt=0xf031beu;s.pc=nxt;s.registers[s.active_bank][15]=0xf02224u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031beu:
if(s.local_RAM[446]==152u&&s.local_RAM[447]==1u&&s.local_RAM[448]==0u&&s.local_RAM[449]==0u&&s.local_RAM[450]==0u&&s.local_RAM[451]==128u) {nxt=0xf031c4u;s.pc=nxt;s.registers[s.active_bank][1]=0x800000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031c4u:
if(s.local_RAM[452]==152u&&s.local_RAM[453]==0u&&s.local_RAM[454]==0u&&s.local_RAM[455]==32u&&s.local_RAM[456]==0u&&s.local_RAM[457]==0u) {nxt=0xf031cau;s.pc=nxt;s.registers[s.active_bank][0]=0x20u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031cau:
if(s.local_RAM[458]==2u&&s.local_RAM[459]==64u) {nxt=0xf031ccu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031ccu:
if(s.local_RAM[460]==164u&&s.local_RAM[461]==0u) {nxt=0xf031ceu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031ceu:
if(s.local_RAM[462]==16u&&s.local_RAM[463]==32u) {nxt=0xf031d0u;s.pc=nxt;s.registers[s.active_bank][0]=sub(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031d0u:
if(s.local_RAM[464]==152u&&s.local_RAM[465]==1u&&s.local_RAM[466]==255u&&s.local_RAM[467]==255u&&s.local_RAM[468]==0u&&s.local_RAM[469]==255u) {nxt=0xf031d6u;s.pc=nxt;s.registers[s.active_bank][1]=0xffffffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031d6u:
if(s.local_RAM[470]==36u&&s.local_RAM[471]==32u) {nxt=0xf031d8u;s.pc=nxt;s.registers[s.active_bank][0]&=s.registers[s.active_bank][1];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031d8u:
if(s.local_RAM[472]==152u&&s.local_RAM[473]==1u&&s.local_RAM[474]==34u&&s.local_RAM[475]==104u&&s.local_RAM[476]==0u&&s.local_RAM[477]==240u) {nxt=0xf031deu;s.pc=nxt;s.registers[s.active_bank][1]=0xf02268u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031deu:
if(s.local_RAM[478]==124u&&s.local_RAM[479]==0u) {nxt=0xf031e0u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][0],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031e0u:
if(s.local_RAM[480]==212u&&s.local_RAM[481]==129u) {nxt=0xf031e2u;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf031eau;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031e2u:
if(s.local_RAM[482]==228u&&s.local_RAM[483]==0u) {nxt=0xf031e4u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031eau:
if(s.local_RAM[490]==188u&&s.local_RAM[491]==32u) {nxt=0xf031ecu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031ecu:
if(s.local_RAM[492]==152u&&s.local_RAM[493]==1u&&s.local_RAM[494]==34u&&s.local_RAM[495]==116u&&s.local_RAM[496]==0u&&s.local_RAM[497]==240u) {nxt=0xf031f2u;s.pc=nxt;s.registers[s.active_bank][1]=0xf02274u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031f2u:
if(s.local_RAM[498]==188u&&s.local_RAM[499]==32u) {nxt=0xf031f4u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031f4u:
if(s.local_RAM[500]==152u&&s.local_RAM[501]==1u&&s.local_RAM[502]==34u&&s.local_RAM[503]==112u&&s.local_RAM[504]==0u&&s.local_RAM[505]==240u) {nxt=0xf031fau;s.pc=nxt;s.registers[s.active_bank][1]=0xf02270u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031fau:
if(s.local_RAM[506]==188u&&s.local_RAM[507]==32u) {nxt=0xf031fcu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf031fcu:
if(s.local_RAM[508]==152u&&s.local_RAM[509]==1u&&s.local_RAM[510]==34u&&s.local_RAM[511]==124u&&s.local_RAM[512]==0u&&s.local_RAM[513]==240u) {nxt=0xf03202u;s.pc=nxt;s.registers[s.active_bank][1]=0xf0227cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03202u:
if(s.local_RAM[514]==188u&&s.local_RAM[515]==32u) {nxt=0xf03204u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03204u:
if(s.local_RAM[516]==8u&&s.local_RAM[517]==129u) {nxt=0xf03206u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03206u:
if(s.local_RAM[518]==188u&&s.local_RAM[519]==32u) {nxt=0xf03208u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03208u:
if(s.local_RAM[520]==8u&&s.local_RAM[521]==129u) {nxt=0xf0320au;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0320au:
if(s.local_RAM[522]==188u&&s.local_RAM[523]==32u) {nxt=0xf0320cu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0320cu:
if(s.local_RAM[524]==8u&&s.local_RAM[525]==129u) {nxt=0xf0320eu;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0320eu:
if(s.local_RAM[526]==188u&&s.local_RAM[527]==32u) {nxt=0xf03210u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03210u:
if(s.local_RAM[528]==152u&&s.local_RAM[529]==10u&&s.local_RAM[530]==0u&&s.local_RAM[531]==0u&&s.local_RAM[532]==255u&&s.local_RAM[533]==255u) {nxt=0xf03216u;s.pc=nxt;s.registers[s.active_bank][10]=0xffff0000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03216u:
if(s.local_RAM[534]==152u&&s.local_RAM[535]==9u&&s.local_RAM[536]==255u&&s.local_RAM[537]==255u&&s.local_RAM[538]==0u&&s.local_RAM[539]==0u) {nxt=0xf0321cu;s.pc=nxt;s.registers[s.active_bank][9]=0xffffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0321cu:
if(s.local_RAM[540]==152u&&s.local_RAM[541]==0u&&s.local_RAM[542]==0u&&s.local_RAM[543]==164u&&s.local_RAM[544]==0u&&s.local_RAM[545]==0u) {nxt=0xf03222u;s.pc=nxt;s.registers[s.active_bank][0]=0xa4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03222u:
if(s.local_RAM[546]==2u&&s.local_RAM[547]==64u) {nxt=0xf03224u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03224u:
if(s.local_RAM[548]==164u&&s.local_RAM[549]==19u) {nxt=0xf03226u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][19]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03226u:
if(s.local_RAM[550]==152u&&s.local_RAM[551]==0u&&s.local_RAM[552]==0u&&s.local_RAM[553]==0u&&s.local_RAM[554]==0u&&s.local_RAM[555]==0u) {nxt=0xf0322cu;s.pc=nxt;s.registers[s.active_bank][0]=0x0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0322cu:
if(s.local_RAM[556]==2u&&s.local_RAM[557]==64u) {nxt=0xf0322eu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0322eu:
if(s.local_RAM[558]==164u&&s.local_RAM[559]==1u) {nxt=0xf03230u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03230u:
if(s.local_RAM[560]==189u&&s.local_RAM[561]==225u) {nxt=0xf03232u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][15])?(s.registers[s.active_bank][15]&~3u):s.registers[s.active_bank][15],s.registers[s.active_bank][1]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03232u:
if(s.local_RAM[562]==152u&&s.local_RAM[563]==2u&&s.local_RAM[564]==53u&&s.local_RAM[565]==34u&&s.local_RAM[566]==0u&&s.local_RAM[567]==240u) {nxt=0xf03238u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03522u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03238u:
if(s.local_RAM[568]==152u&&s.local_RAM[569]==0u&&s.local_RAM[570]==0u&&s.local_RAM[571]==140u&&s.local_RAM[572]==0u&&s.local_RAM[573]==0u) {nxt=0xf0323eu;s.pc=nxt;s.registers[s.active_bank][0]=0x8cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0323eu:
if(s.local_RAM[574]==2u&&s.local_RAM[575]==64u) {nxt=0xf03240u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03240u:
if(s.local_RAM[576]==164u&&s.local_RAM[577]==21u) {nxt=0xf03242u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][21]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03242u:
if(s.local_RAM[578]==124u&&s.local_RAM[579]==21u) {nxt=0xf03244u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][21],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03244u:
if(s.local_RAM[580]==208u&&s.local_RAM[581]==65u) {nxt=0xf03246u;s.pc=nxt;if(condition(&s,1)){pending=1;target=s.registers[s.active_bank][2];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03246u:
if(s.local_RAM[582]==228u&&s.local_RAM[583]==0u) {nxt=0xf03248u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03248u:
if(s.local_RAM[584]==152u&&s.local_RAM[585]==21u&&s.local_RAM[586]==68u&&s.local_RAM[587]==32u&&s.local_RAM[588]==0u&&s.local_RAM[589]==3u) {nxt=0xf0324eu;s.pc=nxt;s.registers[s.active_bank][21]=0x34420u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0324eu:
if(s.local_RAM[590]==196u&&s.local_RAM[591]==53u) {nxt=0xf03250u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+4u,s.registers[s.active_bank][21]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03250u:
if(s.local_RAM[592]==40u&&s.local_RAM[593]==21u) {nxt=0xf03252u;s.pc=nxt;s.registers[s.active_bank][21]|=s.registers[s.active_bank][0];
   zn(&s,s.registers[s.active_bank][21]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03252u:
if(s.local_RAM[594]==152u&&s.local_RAM[595]==21u&&s.local_RAM[596]==68u&&s.local_RAM[597]==32u&&s.local_RAM[598]==0u&&s.local_RAM[599]==1u) {nxt=0xf03258u;s.pc=nxt;s.registers[s.active_bank][21]=0x14420u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03258u:
if(s.local_RAM[600]==200u&&s.local_RAM[601]==53u) {nxt=0xf0325au;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][15]+4u,s.registers[s.active_bank][21]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0325au:
if(s.local_RAM[602]==152u&&s.local_RAM[603]==0u&&s.local_RAM[604]==63u&&s.local_RAM[605]==68u&&s.local_RAM[606]==0u&&s.local_RAM[607]==240u) {nxt=0xf03260u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f44u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03260u:
if(s.local_RAM[608]==164u&&s.local_RAM[609]==20u) {nxt=0xf03262u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][20]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03262u:
if(s.local_RAM[610]==189u&&s.local_RAM[611]==212u) {nxt=0xf03264u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][14])?(s.registers[s.active_bank][14]&~3u):s.registers[s.active_bank][14],s.registers[s.active_bank][20]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03264u:
if(s.local_RAM[612]==152u&&s.local_RAM[613]==0u&&s.local_RAM[614]==0u&&s.local_RAM[615]==4u&&s.local_RAM[616]==0u&&s.local_RAM[617]==0u) {nxt=0xf0326au;s.pc=nxt;s.registers[s.active_bank][0]=0x4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0326au:
if(s.local_RAM[618]==2u&&s.local_RAM[619]==64u) {nxt=0xf0326cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0326cu:
if(s.local_RAM[620]==164u&&s.local_RAM[621]==23u) {nxt=0xf0326eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][23]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0326eu:
if(s.local_RAM[622]==102u&&s.local_RAM[623]==23u) {nxt=0xf03270u;s.pc=nxt;s.c=s.registers[s.active_bank][23]&1u;s.registers[s.active_bank][23]=s.registers[s.active_bank][23]>>16;zn(&s,s.registers[s.active_bank][23]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03270u:
if(s.local_RAM[624]==152u&&s.local_RAM[625]==0u&&s.local_RAM[626]==0u&&s.local_RAM[627]==8u&&s.local_RAM[628]==0u&&s.local_RAM[629]==0u) {nxt=0xf03276u;s.pc=nxt;s.registers[s.active_bank][0]=0x8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03276u:
if(s.local_RAM[630]==2u&&s.local_RAM[631]==64u) {nxt=0xf03278u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03278u:
if(s.local_RAM[632]==164u&&s.local_RAM[633]==24u) {nxt=0xf0327au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][24]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0327au:
if(s.local_RAM[634]==102u&&s.local_RAM[635]==24u) {nxt=0xf0327cu;s.pc=nxt;s.c=s.registers[s.active_bank][24]&1u;s.registers[s.active_bank][24]=s.registers[s.active_bank][24]>>16;zn(&s,s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0327cu:
if(s.local_RAM[636]==139u&&s.local_RAM[637]==20u) {nxt=0xf0327eu;s.pc=nxt;s.registers[s.active_bank][20]=s.registers[s.active_bank][24];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0327eu:
if(s.local_RAM[638]==98u&&s.local_RAM[639]==20u) {nxt=0xf03280u;s.pc=nxt;s.c=s.registers[s.active_bank][20]>>31;s.registers[s.active_bank][20]=s.registers[s.active_bank][20]<<16;zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03280u:
if(s.local_RAM[640]==42u&&s.local_RAM[641]==244u) {nxt=0xf03282u;s.pc=nxt;s.registers[s.active_bank][20]|=s.registers[s.active_bank][23];
   zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03282u:
if(s.local_RAM[642]==152u&&s.local_RAM[643]==20u&&s.local_RAM[644]==1u&&s.local_RAM[645]==128u&&s.local_RAM[646]==1u&&s.local_RAM[647]==128u) {nxt=0xf03288u;s.pc=nxt;s.registers[s.active_bank][20]=0x1800180u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03284u:
if(s.local_RAM[644]==152u&&s.local_RAM[645]==21u&&s.local_RAM[646]==51u&&s.local_RAM[647]==16u&&s.local_RAM[648]==0u&&s.local_RAM[649]==240u) {nxt=0xf0328au;s.pc=nxt;s.registers[s.active_bank][21]=0xf03310u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03288u:
if(s.local_RAM[648]==196u&&s.local_RAM[649]==84u) {nxt=0xf0328au;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+8u,s.registers[s.active_bank][20]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0328au:
if(s.local_RAM[650]==138u&&s.local_RAM[651]==235u) {nxt=0xf0328cu;s.pc=nxt;s.registers[s.active_bank][11]=s.registers[s.active_bank][23];}
else if(s.local_RAM[650]==152u&&s.local_RAM[651]==0u&&s.local_RAM[652]==0u&&s.local_RAM[653]==36u&&s.local_RAM[654]==0u&&s.local_RAM[655]==0u) {nxt=0xf03290u;s.pc=nxt;s.registers[s.active_bank][0]=0x24u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0328cu:
if(s.local_RAM[652]==139u&&s.local_RAM[653]==12u) {nxt=0xf0328eu;s.pc=nxt;s.registers[s.active_bank][12]=s.registers[s.active_bank][24];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0328eu:
if(s.local_RAM[654]==152u&&s.local_RAM[655]==0u&&s.local_RAM[656]==0u&&s.local_RAM[657]==12u&&s.local_RAM[658]==0u&&s.local_RAM[659]==0u) {nxt=0xf03294u;s.pc=nxt;s.registers[s.active_bank][0]=0xcu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03290u:
if(s.local_RAM[656]==0u&&s.local_RAM[657]==96u) {nxt=0xf03292u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03292u:
if(s.local_RAM[658]==164u&&s.local_RAM[659]==17u) {nxt=0xf03294u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][17]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03294u:
if(s.local_RAM[660]==2u&&s.local_RAM[661]==64u) {nxt=0xf03296u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[660]==152u&&s.local_RAM[661]==0u&&s.local_RAM[662]==0u&&s.local_RAM[663]==40u&&s.local_RAM[664]==0u&&s.local_RAM[665]==0u) {nxt=0xf0329au;s.pc=nxt;s.registers[s.active_bank][0]=0x28u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03296u:
if(s.local_RAM[662]==164u&&s.local_RAM[663]==20u) {nxt=0xf03298u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][20]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03298u:
if(s.local_RAM[664]==102u&&s.local_RAM[665]==20u) {nxt=0xf0329au;s.pc=nxt;s.c=s.registers[s.active_bank][20]&1u;s.registers[s.active_bank][20]=s.registers[s.active_bank][20]>>16;zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0329au:
if(s.local_RAM[666]==0u&&s.local_RAM[667]==96u) {nxt=0xf0329cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[666]==66u&&s.local_RAM[667]==139u) {nxt=0xf0329cu;s.pc=nxt;s.registers[s.active_bank][11]=(s.registers[s.active_bank][11]&0xffffu)*(s.registers[s.active_bank][20]&0xffffu);
   zn(&s,s.registers[s.active_bank][11]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0329cu:
if(s.local_RAM[668]==152u&&s.local_RAM[669]==0u&&s.local_RAM[670]==0u&&s.local_RAM[671]==16u&&s.local_RAM[672]==0u&&s.local_RAM[673]==0u) {nxt=0xf032a2u;s.pc=nxt;s.registers[s.active_bank][0]=0x10u;}
else if(s.local_RAM[668]==164u&&s.local_RAM[669]==18u) {nxt=0xf0329eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][18]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0329eu:
if(s.local_RAM[670]==102u&&s.local_RAM[671]==17u) {nxt=0xf032a0u;s.pc=nxt;s.c=s.registers[s.active_bank][17]&1u;s.registers[s.active_bank][17]=s.registers[s.active_bank][17]>>16;zn(&s,s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032a0u:
if(s.local_RAM[672]==102u&&s.local_RAM[673]==18u) {nxt=0xf032a2u;s.pc=nxt;s.c=s.registers[s.active_bank][18]&1u;s.registers[s.active_bank][18]=s.registers[s.active_bank][18]>>16;zn(&s,s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032a2u:
if(s.local_RAM[674]==2u&&s.local_RAM[675]==64u) {nxt=0xf032a4u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[674]==152u&&s.local_RAM[675]==0u&&s.local_RAM[676]==0u&&s.local_RAM[677]==132u&&s.local_RAM[678]==0u&&s.local_RAM[679]==0u) {nxt=0xf032a8u;s.pc=nxt;s.registers[s.active_bank][0]=0x84u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032a4u:
if(s.local_RAM[676]==164u&&s.local_RAM[677]==20u) {nxt=0xf032a6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][20]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032a6u:
if(s.local_RAM[678]==102u&&s.local_RAM[679]==20u) {nxt=0xf032a8u;s.pc=nxt;s.c=s.registers[s.active_bank][20]&1u;s.registers[s.active_bank][20]=s.registers[s.active_bank][20]>>16;zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032a8u:
if(s.local_RAM[680]==0u&&s.local_RAM[681]==96u) {nxt=0xf032aau;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[680]==66u&&s.local_RAM[681]==140u) {nxt=0xf032aau;s.pc=nxt;s.registers[s.active_bank][12]=(s.registers[s.active_bank][12]&0xffffu)*(s.registers[s.active_bank][20]&0xffffu);
   zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032aau:
if(s.local_RAM[682]==101u&&s.local_RAM[683]==9u) {nxt=0xf032acu;s.pc=nxt;s.c=s.registers[s.active_bank][9]&1u;s.registers[s.active_bank][9]=s.registers[s.active_bank][9]>>8;zn(&s,s.registers[s.active_bank][9]);}
else if(s.local_RAM[682]==164u&&s.local_RAM[683]==16u) {nxt=0xf032acu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][16]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032acu:
if(s.local_RAM[684]==138u&&s.local_RAM[685]==98u) {nxt=0xf032aeu;s.pc=nxt;s.registers[s.active_bank][2]=s.registers[s.active_bank][19];}
else if(s.local_RAM[684]==152u&&s.local_RAM[685]==0u&&s.local_RAM[686]==0u&&s.local_RAM[687]==136u&&s.local_RAM[688]==0u&&s.local_RAM[689]==0u) {nxt=0xf032b2u;s.pc=nxt;s.registers[s.active_bank][0]=0x88u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032aeu:
if(s.local_RAM[686]==152u&&s.local_RAM[687]==0u&&s.local_RAM[688]==0u&&s.local_RAM[689]==20u&&s.local_RAM[690]==0u&&s.local_RAM[691]==0u) {nxt=0xf032b4u;s.pc=nxt;s.registers[s.active_bank][0]=0x14u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032b2u:
if(s.local_RAM[690]==0u&&s.local_RAM[691]==96u) {nxt=0xf032b4u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032b4u:
if(s.local_RAM[692]==2u&&s.local_RAM[693]==64u) {nxt=0xf032b6u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else if(s.local_RAM[692]==164u&&s.local_RAM[693]==19u) {nxt=0xf032b6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][19]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032b6u:
if(s.local_RAM[694]==101u&&s.local_RAM[695]==16u) {nxt=0xf032b8u;s.pc=nxt;s.c=s.registers[s.active_bank][16]&1u;s.registers[s.active_bank][16]=s.registers[s.active_bank][16]>>8;zn(&s,s.registers[s.active_bank][16]);}
else if(s.local_RAM[694]==164u&&s.local_RAM[695]==20u) {nxt=0xf032b8u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][20]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032b8u:
if(s.local_RAM[696]==101u&&s.local_RAM[697]==19u) {nxt=0xf032bau;s.pc=nxt;s.c=s.registers[s.active_bank][19]&1u;s.registers[s.active_bank][19]=s.registers[s.active_bank][19]>>8;zn(&s,s.registers[s.active_bank][19]);}
else if(s.local_RAM[696]==138u&&s.local_RAM[697]==128u) {nxt=0xf032bau;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][20];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032bau:
if(s.local_RAM[698]==102u&&s.local_RAM[699]==0u) {nxt=0xf032bcu;s.pc=nxt;s.c=s.registers[s.active_bank][0]&1u;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]>>16;zn(&s,s.registers[s.active_bank][0]);}
else if(s.local_RAM[698]==138u&&s.local_RAM[699]==0u) {nxt=0xf032bcu;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][16];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032bcu:
if(s.local_RAM[700]==37u&&s.local_RAM[701]==32u) {nxt=0xf032beu;s.pc=nxt;s.registers[s.active_bank][0]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][0]);}
else if(s.local_RAM[700]==138u&&s.local_RAM[701]==97u) {nxt=0xf032beu;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][19];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032beu:
if(s.local_RAM[702]==0u&&s.local_RAM[703]==64u) {nxt=0xf032c0u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][2]);}
else if(s.local_RAM[702]==100u&&s.local_RAM[703]==32u) {nxt=0xf032c0u;s.pc=nxt;s.c=s.registers[s.active_bank][0]&1u;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]>>1;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032c0u:
if(s.local_RAM[704]==100u&&s.local_RAM[705]==33u) {nxt=0xf032c2u;s.pc=nxt;s.c=s.registers[s.active_bank][1]&1u;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]>>1;zn(&s,s.registers[s.active_bank][1]);}
else if(s.local_RAM[704]==156u&&s.local_RAM[705]==30u) {nxt=0xf032c2u;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][0],&v));s.registers[s.active_bank][30]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032c2u:
if(s.local_RAM[706]==8u&&s.local_RAM[707]==32u) {nxt=0xf032c4u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],1u);}
else if(s.local_RAM[706]==16u&&s.local_RAM[707]==17u) {nxt=0xf032c4u;s.pc=nxt;s.registers[s.active_bank][17]=sub(&s,s.registers[s.active_bank][17],s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032c4u:
if(s.local_RAM[708]==16u&&s.local_RAM[709]==50u) {nxt=0xf032c6u;s.pc=nxt;s.registers[s.active_bank][18]=sub(&s,s.registers[s.active_bank][18],s.registers[s.active_bank][1]);}
else if(s.local_RAM[708]==156u&&s.local_RAM[709]==28u) {nxt=0xf032c6u;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][0],&v));s.registers[s.active_bank][28]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032c6u:
if(s.local_RAM[710]==19u&&s.local_RAM[711]==220u) {nxt=0xf032c8u;s.pc=nxt;s.registers[s.active_bank][28]=sub(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][30]);}
else if(s.local_RAM[710]==138u&&s.local_RAM[711]==84u) {nxt=0xf032c8u;s.pc=nxt;s.registers[s.active_bank][20]=s.registers[s.active_bank][18];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032c8u:
if(s.local_RAM[712]==138u&&s.local_RAM[713]==33u) {nxt=0xf032cau;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][17];}
else if(s.local_RAM[712]==138u&&s.local_RAM[713]==130u) {nxt=0xf032cau;s.pc=nxt;s.registers[s.active_bank][2]=s.registers[s.active_bank][20];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032cau:
if(s.local_RAM[714]==65u&&s.local_RAM[715]==84u) {nxt=0xf032ccu;s.pc=nxt;s.registers[s.active_bank][20]=(s.registers[s.active_bank][20]&0xffffu)*(s.registers[s.active_bank][10]&0xffffu);
   zn(&s,s.registers[s.active_bank][20]);}
else if(s.local_RAM[714]==101u&&s.local_RAM[715]==2u) {nxt=0xf032ccu;s.pc=nxt;s.c=s.registers[s.active_bank][2]&1u;s.registers[s.active_bank][2]=s.registers[s.active_bank][2]>>8;zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032ccu:
if(s.local_RAM[716]==99u&&s.local_RAM[717]==30u) {nxt=0xf032ceu;s.pc=nxt;s.c=s.registers[s.active_bank][30]>>31;s.registers[s.active_bank][30]=s.registers[s.active_bank][30]<<8;zn(&s,s.registers[s.active_bank][30]);}
else if(s.local_RAM[716]==99u&&s.local_RAM[717]==225u) {nxt=0xf032ceu;s.pc=nxt;s.c=s.registers[s.active_bank][1]>>31;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]<<1;zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032ceu:
if(s.local_RAM[718]==2u&&s.local_RAM[719]==244u) {nxt=0xf032d0u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],s.registers[s.active_bank][23]);}
else if(s.local_RAM[718]==37u&&s.local_RAM[719]==34u) {nxt=0xf032d0u;s.pc=nxt;s.registers[s.active_bank][2]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032d0u:
if(s.local_RAM[720]==0u&&s.local_RAM[721]==52u) {nxt=0xf032d2u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],s.registers[s.active_bank][1]);}
else if(s.local_RAM[720]==68u&&s.local_RAM[721]==92u) {nxt=0xf032d2u;s.pc=nxt;s.registers[s.active_bank][28]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.active_bank][28])*(int32_t)sx16(s.registers[s.active_bank][2]));
   zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032d2u:
if(s.local_RAM[722]==3u&&s.local_RAM[723]==220u) {nxt=0xf032d4u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][30]);}
else if(s.local_RAM[722]==146u&&s.local_RAM[723]==148u) {nxt=0xf032d4u;s.pc=nxt;s.registers[1u-s.active_bank][20]=s.registers[s.active_bank][20];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032d4u:
if(s.local_RAM[724]==146u&&s.local_RAM[725]==16u) {nxt=0xf032d6u;s.pc=nxt;s.registers[1u-s.active_bank][16]=s.registers[s.active_bank][16];}
else if(s.local_RAM[724]==152u&&s.local_RAM[725]==1u&&s.local_RAM[726]==128u&&s.local_RAM[727]==0u&&s.local_RAM[728]==0u&&s.local_RAM[729]==0u) {nxt=0xf032dau;s.pc=nxt;s.registers[s.active_bank][1]=0x8000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032d6u:
if(s.local_RAM[726]==108u&&s.local_RAM[727]==140u) {nxt=0xf032d8u;s.pc=nxt;s.c=s.registers[s.active_bank][12]&1u;s.registers[s.active_bank][12]=sar(s.registers[s.active_bank][12],4);zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032d8u:
if(s.local_RAM[728]==108u&&s.local_RAM[729]==141u) {nxt=0xf032dau;s.pc=nxt;s.c=s.registers[s.active_bank][13]&1u;s.registers[s.active_bank][13]=sar(s.registers[s.active_bank][13],4);zn(&s,s.registers[s.active_bank][13]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032dau:
if(s.local_RAM[730]==16u&&s.local_RAM[731]==60u) {nxt=0xf032dcu;s.pc=nxt;s.registers[s.active_bank][28]=sub(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][1]);}
else if(s.local_RAM[730]==108u&&s.local_RAM[731]==73u) {nxt=0xf032dcu;s.pc=nxt;s.c=s.registers[s.active_bank][9]&1u;s.registers[s.active_bank][9]=sar(s.registers[s.active_bank][9],2);zn(&s,s.registers[s.active_bank][9]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032dcu:
if(s.local_RAM[732]==108u&&s.local_RAM[733]==75u) {nxt=0xf032deu;s.pc=nxt;s.c=s.registers[s.active_bank][11]&1u;s.registers[s.active_bank][11]=sar(s.registers[s.active_bank][11],2);zn(&s,s.registers[s.active_bank][11]);}
else if(s.local_RAM[732]==139u&&s.local_RAM[733]==144u) {nxt=0xf032deu;s.pc=nxt;s.registers[s.active_bank][16]=s.registers[s.active_bank][28];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032deu:
if(s.local_RAM[734]==18u&&s.local_RAM[735]==96u) {nxt=0xf032e0u;s.pc=nxt;s.registers[s.active_bank][0]=sub(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][19]);}
else if(s.local_RAM[734]==152u&&s.local_RAM[735]==28u&&s.local_RAM[736]==0u&&s.local_RAM[737]==64u&&s.local_RAM[738]==0u&&s.local_RAM[739]==0u) {nxt=0xf032e4u;s.pc=nxt;s.registers[s.active_bank][28]=0x40u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032e0u:
if(s.local_RAM[736]==152u&&s.local_RAM[737]==1u&&s.local_RAM[738]==0u&&s.local_RAM[739]==63u&&s.local_RAM[740]==0u&&s.local_RAM[741]==0u) {nxt=0xf032e6u;s.pc=nxt;s.registers[s.active_bank][1]=0x3fu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032e4u:
if(s.local_RAM[740]==152u&&s.local_RAM[741]==29u&&s.local_RAM[742]==255u&&s.local_RAM[743]==255u&&s.local_RAM[744]==0u&&s.local_RAM[745]==31u) {nxt=0xf032eau;s.pc=nxt;s.registers[s.active_bank][29]=0x1fffffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032e6u:
if(s.local_RAM[742]==0u&&s.local_RAM[743]==32u) {nxt=0xf032e8u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032e8u:
if(s.local_RAM[744]==37u&&s.local_RAM[745]==32u) {nxt=0xf032eau;s.pc=nxt;s.registers[s.active_bank][0]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032eau:
if(s.local_RAM[746]==2u&&s.local_RAM[747]==96u) {nxt=0xf032ecu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][19]);}
else if(s.local_RAM[746]==152u&&s.local_RAM[747]==0u&&s.local_RAM[748]==0u&&s.local_RAM[749]==240u&&s.local_RAM[750]==0u&&s.local_RAM[751]==0u) {nxt=0xf032f0u;s.pc=nxt;s.registers[s.active_bank][0]=0xf0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032ecu:
if(s.local_RAM[748]==156u&&s.local_RAM[749]==30u) {nxt=0xf032eeu;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][0],&v));s.registers[s.active_bank][30]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032eeu:
if(s.local_RAM[750]==8u&&s.local_RAM[751]==32u) {nxt=0xf032f0u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032f0u:
if(s.local_RAM[752]==0u&&s.local_RAM[753]==96u) {nxt=0xf032f2u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[752]==156u&&s.local_RAM[753]==28u) {nxt=0xf032f2u;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][0],&v));s.registers[s.active_bank][28]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032f2u:
if(s.local_RAM[754]==19u&&s.local_RAM[755]==220u) {nxt=0xf032f4u;s.pc=nxt;s.registers[s.active_bank][28]=sub(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][30]);}
else if(s.local_RAM[754]==164u&&s.local_RAM[755]==1u) {nxt=0xf032f4u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032f4u:
if(s.local_RAM[756]==138u&&s.local_RAM[757]==130u) {nxt=0xf032f6u;s.pc=nxt;s.registers[s.active_bank][2]=s.registers[s.active_bank][20];}
else if(s.local_RAM[756]==152u&&s.local_RAM[757]==0u&&s.local_RAM[758]==0u&&s.local_RAM[759]==244u&&s.local_RAM[760]==0u&&s.local_RAM[761]==0u) {nxt=0xf032fau;s.pc=nxt;s.registers[s.active_bank][0]=0xf4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032f6u:
if(s.local_RAM[758]==101u&&s.local_RAM[759]==2u) {nxt=0xf032f8u;s.pc=nxt;s.c=s.registers[s.active_bank][2]&1u;s.registers[s.active_bank][2]=s.registers[s.active_bank][2]>>8;zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032f8u:
if(s.local_RAM[760]==99u&&s.local_RAM[761]==30u) {nxt=0xf032fau;s.pc=nxt;s.c=s.registers[s.active_bank][30]>>31;s.registers[s.active_bank][30]=s.registers[s.active_bank][30]<<8;zn(&s,s.registers[s.active_bank][30]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032fau:
if(s.local_RAM[762]==0u&&s.local_RAM[763]==96u) {nxt=0xf032fcu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[762]==37u&&s.local_RAM[763]==34u) {nxt=0xf032fcu;s.pc=nxt;s.registers[s.active_bank][2]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032fcu:
if(s.local_RAM[764]==68u&&s.local_RAM[765]==92u) {nxt=0xf032feu;s.pc=nxt;s.registers[s.active_bank][28]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.active_bank][28])*(int32_t)sx16(s.registers[s.active_bank][2]));
   zn(&s,s.registers[s.active_bank][28]);}
else if(s.local_RAM[764]==164u&&s.local_RAM[765]==2u) {nxt=0xf032feu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf032feu:
if(s.local_RAM[766]==3u&&s.local_RAM[767]==220u) {nxt=0xf03300u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][30]);}
else if(s.local_RAM[766]==101u&&s.local_RAM[767]==1u) {nxt=0xf03300u;s.pc=nxt;s.c=s.registers[s.active_bank][1]&1u;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]>>8;zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03300u:
if(s.local_RAM[768]==152u&&s.local_RAM[769]==0u&&s.local_RAM[770]==49u&&s.local_RAM[771]==220u&&s.local_RAM[772]==0u&&s.local_RAM[773]==240u) {nxt=0xf03306u;s.pc=nxt;s.registers[s.active_bank][0]=0xf031dcu;}
else if(s.local_RAM[768]==152u&&s.local_RAM[769]==1u&&s.local_RAM[770]==128u&&s.local_RAM[771]==0u&&s.local_RAM[772]==0u&&s.local_RAM[773]==0u) {nxt=0xf03306u;s.pc=nxt;s.registers[s.active_bank][1]=0x8000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03306u:
if(s.local_RAM[774]==16u&&s.local_RAM[775]==60u) {nxt=0xf03308u;s.pc=nxt;s.registers[s.active_bank][28]=sub(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][1]);}
else if(s.local_RAM[774]==124u&&s.local_RAM[775]==2u) {nxt=0xf03308u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][2],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03308u:
if(s.local_RAM[776]==139u&&s.local_RAM[777]==145u) {nxt=0xf0330au;s.pc=nxt;s.registers[s.active_bank][17]=s.registers[s.active_bank][28];}
else if(s.local_RAM[776]==212u&&s.local_RAM[777]==66u) {nxt=0xf0330au;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf0330eu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0330au:
if(s.local_RAM[778]==99u&&s.local_RAM[779]==11u) {nxt=0xf0330cu;s.pc=nxt;s.c=s.registers[s.active_bank][11]>>31;s.registers[s.active_bank][11]=s.registers[s.active_bank][11]<<8;zn(&s,s.registers[s.active_bank][11]);}
else if(s.local_RAM[778]==228u&&s.local_RAM[779]==0u) {nxt=0xf0330cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0330cu:
if(s.local_RAM[780]==99u&&s.local_RAM[781]==12u) {nxt=0xf0330eu;s.pc=nxt;s.c=s.registers[s.active_bank][12]>>31;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]<<8;zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0330eu:
if(s.local_RAM[782]==137u&&s.local_RAM[783]==99u) {nxt=0xf03310u;s.pc=nxt;s.registers[s.active_bank][3]=s.registers[s.active_bank][11];}
else if(s.local_RAM[782]==144u&&s.local_RAM[783]==66u) {nxt=0xf03310u;s.pc=nxt;s.registers[1u-s.active_bank][2]=s.registers[s.active_bank][2];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03310u:
if(s.local_RAM[784]==136u&&s.local_RAM[785]==226u) {nxt=0xf03312u;s.pc=nxt;s.registers[s.active_bank][2]=s.registers[s.active_bank][7];}
else if(s.local_RAM[784]==146u&&s.local_RAM[785]==32u) {nxt=0xf03312u;s.pc=nxt;s.registers[1u-s.active_bank][0]=s.registers[s.active_bank][17];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03312u:
if(s.local_RAM[786]==137u&&s.local_RAM[787]==1u) {nxt=0xf03314u;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][8];}
else if(s.local_RAM[786]==140u&&s.local_RAM[787]==27u) {nxt=0xf03314u;s.pc=nxt;s.registers[s.active_bank][27]=0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03314u:
if(s.local_RAM[788]==136u&&s.local_RAM[789]==64u) {nxt=0xf03316u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][2];}
else if(s.local_RAM[788]==139u&&s.local_RAM[789]==124u) {nxt=0xf03316u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][27];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03316u:
if(s.local_RAM[790]==88u&&s.local_RAM[791]==3u) {nxt=0xf03318u;s.pc=nxt;s.c=s.registers[s.active_bank][3]>>31;if(s.registers[s.active_bank][3]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][3]=0u-s.registers[s.active_bank][3];s.n=0;s.z=s.registers[s.active_bank][3]==0;}}
else if(s.local_RAM[790]==139u&&s.local_RAM[791]==190u) {nxt=0xf03318u;s.pc=nxt;s.registers[s.active_bank][30]=s.registers[s.active_bank][29];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03318u:
if(s.local_RAM[792]==7u&&s.local_RAM[793]==155u) {nxt=0xf0331au;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else if(s.local_RAM[792]==136u&&s.local_RAM[793]==31u) {nxt=0xf0331au;s.pc=nxt;s.registers[s.active_bank][31]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0331au:
if(s.local_RAM[794]==88u&&s.local_RAM[795]==17u) {nxt=0xf0331cu;s.pc=nxt;s.c=s.registers[s.active_bank][17]>>31;if(s.registers[s.active_bank][17]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][17]=0u-s.registers[s.active_bank][17];s.n=0;s.z=s.registers[s.active_bank][17]==0;}}
else if(s.local_RAM[794]==136u&&s.local_RAM[795]==37u) {nxt=0xf0331cu;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][1];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0331cu:
if(s.local_RAM[796]==7u&&s.local_RAM[797]==155u) {nxt=0xf0331eu;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else if(s.local_RAM[796]==39u&&s.local_RAM[797]==223u) {nxt=0xf0331eu;s.pc=nxt;s.registers[s.active_bank][31]&=s.registers[s.active_bank][30];
   zn(&s,s.registers[s.active_bank][31]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0331eu:
if(s.local_RAM[798]==39u&&s.local_RAM[799]==197u) {nxt=0xf03320u;s.pc=nxt;s.registers[s.active_bank][5]&=s.registers[s.active_bank][30];
   zn(&s,s.registers[s.active_bank][5]);}
else if(s.local_RAM[798]==138u&&s.local_RAM[799]==60u) {nxt=0xf03320u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][17];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03320u:
if(s.local_RAM[800]==64u&&s.local_RAM[801]==124u) {nxt=0xf03322u;s.pc=nxt;s.registers[s.active_bank][28]=(s.registers[s.active_bank][28]&0xffffu)*(s.registers[s.active_bank][3]&0xffffu);
   zn(&s,s.registers[s.active_bank][28]);}
else if(s.local_RAM[800]==100u&&s.local_RAM[801]==62u) {nxt=0xf03322u;s.pc=nxt;s.c=s.registers[s.active_bank][30]&1u;s.registers[s.active_bank][30]=s.registers[s.active_bank][30]>>1;zn(&s,s.registers[s.active_bank][30]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03322u:
if(s.local_RAM[802]==19u&&s.local_RAM[803]==223u) {nxt=0xf03324u;s.pc=nxt;s.registers[s.active_bank][31]=sub(&s,s.registers[s.active_bank][31],s.registers[s.active_bank][30]);}
else if(s.local_RAM[802]==136u&&s.local_RAM[803]==125u) {nxt=0xf03324u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][3];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03324u:
if(s.local_RAM[804]==102u&&s.local_RAM[805]==28u) {nxt=0xf03326u;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>16;zn(&s,s.registers[s.active_bank][28]);}
else if(s.local_RAM[804]==212u&&s.local_RAM[805]==84u) {nxt=0xf03326u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf0332au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03326u:
if(s.local_RAM[806]==102u&&s.local_RAM[807]==29u) {nxt=0xf03328u;s.pc=nxt;s.c=s.registers[s.active_bank][29]&1u;s.registers[s.active_bank][29]=s.registers[s.active_bank][29]>>16;zn(&s,s.registers[s.active_bank][29]);}
else if(s.local_RAM[806]==228u&&s.local_RAM[807]==0u) {nxt=0xf03328u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03328u:
if(s.local_RAM[808]==32u&&s.local_RAM[809]==31u) {nxt=0xf0332au;s.pc=nxt;s.registers[s.active_bank][31]=sub(&s,0,s.registers[s.active_bank][31]);}
else if(s.local_RAM[808]==66u&&s.local_RAM[809]==61u) {nxt=0xf0332au;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][17]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0332au:
if(s.local_RAM[810]==19u&&s.local_RAM[811]==197u) {nxt=0xf0332cu;s.pc=nxt;s.registers[s.active_bank][5]=sub(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][30]);}
else if(s.local_RAM[810]==102u&&s.local_RAM[811]==17u) {nxt=0xf0332cu;s.pc=nxt;s.c=s.registers[s.active_bank][17]&1u;s.registers[s.active_bank][17]=s.registers[s.active_bank][17]>>16;zn(&s,s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0332cu:
if(s.local_RAM[812]==3u&&s.local_RAM[813]==188u) {nxt=0xf0332eu;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else if(s.local_RAM[812]==212u&&s.local_RAM[813]==84u) {nxt=0xf0332eu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf03332u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0332eu:
if(s.local_RAM[814]==138u&&s.local_RAM[815]==61u) {nxt=0xf03330u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][17];}
else if(s.local_RAM[814]==228u&&s.local_RAM[815]==0u) {nxt=0xf03330u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03330u:
if(s.local_RAM[816]==32u&&s.local_RAM[817]==5u) {nxt=0xf03332u;s.pc=nxt;s.registers[s.active_bank][5]=sub(&s,0,s.registers[s.active_bank][5]);}
else if(s.local_RAM[816]==64u&&s.local_RAM[817]==125u) {nxt=0xf03332u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][3]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03332u:
if(s.local_RAM[818]==102u&&s.local_RAM[819]==3u) {nxt=0xf03334u;s.pc=nxt;s.c=s.registers[s.active_bank][3]&1u;s.registers[s.active_bank][3]=s.registers[s.active_bank][3]>>16;zn(&s,s.registers[s.active_bank][3]);}
else if(s.local_RAM[818]==136u&&s.local_RAM[819]==187u) {nxt=0xf03334u;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03334u:
if(s.local_RAM[820]==3u&&s.local_RAM[821]==188u) {nxt=0xf03336u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else if(s.local_RAM[820]==102u&&s.local_RAM[821]==31u) {nxt=0xf03336u;s.pc=nxt;s.c=s.registers[s.active_bank][31]&1u;s.registers[s.active_bank][31]=s.registers[s.active_bank][31]>>16;zn(&s,s.registers[s.active_bank][31]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03336u:
if(s.local_RAM[822]==66u&&s.local_RAM[823]==35u) {nxt=0xf03338u;s.pc=nxt;s.registers[s.active_bank][3]=(s.registers[s.active_bank][3]&0xffffu)*(s.registers[s.active_bank][17]&0xffffu);
   zn(&s,s.registers[s.active_bank][3]);}
else if(s.local_RAM[822]==102u&&s.local_RAM[823]==5u) {nxt=0xf03338u;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]>>16;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03338u:
if(s.local_RAM[824]==98u&&s.local_RAM[825]==3u) {nxt=0xf0333au;s.pc=nxt;s.c=s.registers[s.active_bank][3]>>31;s.registers[s.active_bank][3]=s.registers[s.active_bank][3]<<16;zn(&s,s.registers[s.active_bank][3]);}
else if(s.local_RAM[824]==99u&&s.local_RAM[825]==159u) {nxt=0xf0333au;s.pc=nxt;s.c=s.registers[s.active_bank][31]>>31;s.registers[s.active_bank][31]=s.registers[s.active_bank][31]<<4;zn(&s,s.registers[s.active_bank][31]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0333au:
if(s.local_RAM[826]==3u&&s.local_RAM[827]==131u) {nxt=0xf0333cu;s.pc=nxt;s.registers[s.active_bank][3]=add(&s,s.registers[s.active_bank][3],s.registers[s.active_bank][28]);}
else if(s.local_RAM[826]==43u&&s.local_RAM[827]==229u) {nxt=0xf0333cu;s.pc=nxt;s.registers[s.active_bank][5]|=s.registers[s.active_bank][31];
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0333cu:
if(s.local_RAM[828]==52u&&s.local_RAM[829]==27u) {nxt=0xf0333eu;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>0)&1u;}
else if(s.local_RAM[828]==101u&&s.local_RAM[829]==187u) {nxt=0xf0333eu;s.pc=nxt;s.c=s.registers[s.active_bank][27]&1u;s.registers[s.active_bank][27]=s.registers[s.active_bank][27]>>13;zn(&s,s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0333eu:
if(s.local_RAM[830]==152u&&s.local_RAM[831]==1u&&s.local_RAM[832]==0u&&s.local_RAM[833]==255u&&s.local_RAM[834]==0u&&s.local_RAM[835]==0u) {nxt=0xf03344u;s.pc=nxt;s.registers[s.active_bank][1]=0xffu;}
else if(s.local_RAM[830]==212u&&s.local_RAM[831]==66u) {nxt=0xf03340u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03344u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03340u:
if(s.local_RAM[832]==148u&&s.local_RAM[833]==17u) {nxt=0xf03342u;s.pc=nxt;s.registers[s.active_bank][17]=s.registers[1u-s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03344u:
if(s.local_RAM[836]==137u&&s.local_RAM[837]==100u) {nxt=0xf03346u;s.pc=nxt;s.registers[s.active_bank][4]=s.registers[s.active_bank][11];}
else if(s.local_RAM[836]==148u&&s.local_RAM[837]==66u) {nxt=0xf03346u;s.pc=nxt;s.registers[s.active_bank][2]=s.registers[1u-s.active_bank][2];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03346u:
if(s.local_RAM[838]==124u&&s.local_RAM[839]==2u) {nxt=0xf03348u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][2],0x0u);}
else if(s.local_RAM[838]==146u&&s.local_RAM[839]==0u) {nxt=0xf03348u;s.pc=nxt;s.registers[1u-s.active_bank][0]=s.registers[s.active_bank][16];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03348u:
if(s.local_RAM[840]==140u&&s.local_RAM[841]==27u) {nxt=0xf0334au;s.pc=nxt;s.registers[s.active_bank][27]=0u;}
else if(s.local_RAM[840]==212u&&s.local_RAM[841]==66u) {nxt=0xf0334au;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf0334eu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0334au:
if(s.local_RAM[842]==139u&&s.local_RAM[843]==124u) {nxt=0xf0334cu;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][27];}
else if(s.local_RAM[842]==228u&&s.local_RAM[843]==0u) {nxt=0xf0334cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0334cu:
if(s.local_RAM[844]==88u&&s.local_RAM[845]==4u) {nxt=0xf0334eu;s.pc=nxt;s.c=s.registers[s.active_bank][4]>>31;if(s.registers[s.active_bank][4]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][4]=0u-s.registers[s.active_bank][4];s.n=0;s.z=s.registers[s.active_bank][4]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0334eu:
if(s.local_RAM[846]==7u&&s.local_RAM[847]==155u) {nxt=0xf03350u;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else if(s.local_RAM[846]==99u&&s.local_RAM[847]==5u) {nxt=0xf03350u;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]<<8;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03350u:
if(s.local_RAM[848]==3u&&s.local_RAM[849]==155u) {nxt=0xf03352u;s.pc=nxt;s.registers[s.active_bank][27]=add(&s,s.registers[s.active_bank][27],s.registers[s.active_bank][28]);}
else if(s.local_RAM[848]==88u&&s.local_RAM[849]==16u) {nxt=0xf03352u;s.pc=nxt;s.c=s.registers[s.active_bank][16]>>31;if(s.registers[s.active_bank][16]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][16]=0u-s.registers[s.active_bank][16];s.n=0;s.z=s.registers[s.active_bank][16]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03352u:
if(s.local_RAM[850]==7u&&s.local_RAM[851]==155u) {nxt=0xf03354u;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else if(s.local_RAM[850]==43u&&s.local_RAM[851]==101u) {nxt=0xf03354u;s.pc=nxt;s.registers[s.active_bank][5]|=s.registers[s.active_bank][27];
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03354u:
if(s.local_RAM[852]==138u&&s.local_RAM[853]==28u) {nxt=0xf03356u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][16];}
else if(s.local_RAM[852]==186u&&s.local_RAM[853]==133u) {nxt=0xf03356u;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][20],s.registers[s.active_bank][5]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03356u:
if(s.local_RAM[854]==8u&&s.local_RAM[855]==84u) {nxt=0xf03358u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],2u);}
else if(s.local_RAM[854]==64u&&s.local_RAM[855]==156u) {nxt=0xf03358u;s.pc=nxt;s.registers[s.active_bank][28]=(s.registers[s.active_bank][28]&0xffffu)*(s.registers[s.active_bank][4]&0xffffu);
   zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03358u:
if(s.local_RAM[856]==1u&&s.local_RAM[857]==39u) {nxt=0xf0335au;s.pc=nxt;s.registers[s.active_bank][7]=add(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][9]);}
else if(s.local_RAM[856]==136u&&s.local_RAM[857]==157u) {nxt=0xf0335au;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][4];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0335au:
if(s.local_RAM[858]==1u&&s.local_RAM[859]==104u) {nxt=0xf0335cu;s.pc=nxt;s.registers[s.active_bank][8]=add(&s,s.registers[s.active_bank][8],s.registers[s.active_bank][11]);}
else if(s.local_RAM[858]==102u&&s.local_RAM[859]==28u) {nxt=0xf0335cu;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>16;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0335cu:
if(s.local_RAM[860]==24u&&s.local_RAM[861]==48u) {nxt=0xf0335eu;s.pc=nxt;s.registers[s.active_bank][16]=sub(&s,s.registers[s.active_bank][16],1u);}
else if(s.local_RAM[860]==102u&&s.local_RAM[861]==29u) {nxt=0xf0335eu;s.pc=nxt;s.c=s.registers[s.active_bank][29]&1u;s.registers[s.active_bank][29]=s.registers[s.active_bank][29]>>16;zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0335eu:
if(s.local_RAM[862]==66u&&s.local_RAM[863]==29u) {nxt=0xf03360u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][16]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else if(s.local_RAM[862]==210u&&s.local_RAM[863]==180u) {nxt=0xf03360u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][21];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03360u:
if(s.local_RAM[864]==102u&&s.local_RAM[865]==16u) {nxt=0xf03362u;s.pc=nxt;s.c=s.registers[s.active_bank][16]&1u;s.registers[s.active_bank][16]=s.registers[s.active_bank][16]>>16;zn(&s,s.registers[s.active_bank][16]);}
else if(s.local_RAM[864]==228u&&s.local_RAM[865]==0u) {nxt=0xf03362u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03362u:
if(s.local_RAM[866]==3u&&s.local_RAM[867]==188u) {nxt=0xf03364u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else if(s.local_RAM[866]==148u&&s.local_RAM[867]==231u) {nxt=0xf03364u;s.pc=nxt;s.registers[s.active_bank][7]=s.registers[1u-s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03364u:
if(s.local_RAM[868]==138u&&s.local_RAM[869]==29u) {nxt=0xf03366u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][16];}
else if(s.local_RAM[868]==149u&&s.local_RAM[869]==8u) {nxt=0xf03366u;s.pc=nxt;s.registers[s.active_bank][8]=s.registers[1u-s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03366u:
if(s.local_RAM[870]==64u&&s.local_RAM[871]==157u) {nxt=0xf03368u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][4]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else if(s.local_RAM[870]==150u&&s.local_RAM[871]==148u) {nxt=0xf03368u;s.pc=nxt;s.registers[s.active_bank][20]=s.registers[1u-s.active_bank][20];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03368u:
if(s.local_RAM[872]==102u&&s.local_RAM[873]==4u) {nxt=0xf0336au;s.pc=nxt;s.c=s.registers[s.active_bank][4]&1u;s.registers[s.active_bank][4]=s.registers[s.active_bank][4]>>16;zn(&s,s.registers[s.active_bank][4]);}
else if(s.local_RAM[872]==150u&&s.local_RAM[873]==16u) {nxt=0xf0336au;s.pc=nxt;s.registers[s.active_bank][16]=s.registers[1u-s.active_bank][16];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0336au:
if(s.local_RAM[874]==1u&&s.local_RAM[875]==135u) {nxt=0xf0336cu;s.pc=nxt;s.registers[s.active_bank][7]=add(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][12]);}
else if(s.local_RAM[874]==3u&&s.local_RAM[875]==188u) {nxt=0xf0336cu;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0336cu:
if(s.local_RAM[876]==1u&&s.local_RAM[877]==168u) {nxt=0xf0336eu;s.pc=nxt;s.registers[s.active_bank][8]=add(&s,s.registers[s.active_bank][8],s.registers[s.active_bank][13]);}
else if(s.local_RAM[876]==66u&&s.local_RAM[877]==4u) {nxt=0xf0336eu;s.pc=nxt;s.registers[s.active_bank][4]=(s.registers[s.active_bank][4]&0xffffu)*(s.registers[s.active_bank][16]&0xffffu);
   zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0336eu:
if(s.local_RAM[878]==1u&&s.local_RAM[879]==84u) {nxt=0xf03370u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],s.registers[s.active_bank][10]);}
else if(s.local_RAM[878]==98u&&s.local_RAM[879]==4u) {nxt=0xf03370u;s.pc=nxt;s.c=s.registers[s.active_bank][4]>>31;s.registers[s.active_bank][4]=s.registers[s.active_bank][4]<<16;zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03370u:
if(s.local_RAM[880]==3u&&s.local_RAM[881]==132u) {nxt=0xf03372u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],s.registers[s.active_bank][28]);}
else if(s.local_RAM[880]==144u&&s.local_RAM[881]==231u) {nxt=0xf03372u;s.pc=nxt;s.registers[1u-s.active_bank][7]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03372u:
if(s.local_RAM[882]==52u&&s.local_RAM[883]==27u) {nxt=0xf03374u;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>0)&1u;}
else if(s.local_RAM[882]==145u&&s.local_RAM[883]==8u) {nxt=0xf03374u;s.pc=nxt;s.registers[1u-s.active_bank][8]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03374u:
if(s.local_RAM[884]==24u&&s.local_RAM[885]==51u) {nxt=0xf03376u;s.pc=nxt;s.registers[s.active_bank][19]=sub(&s,s.registers[s.active_bank][19],1u);}
else if(s.local_RAM[884]==212u&&s.local_RAM[885]==66u) {nxt=0xf03376u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf0337au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03376u:
if(s.local_RAM[886]==148u&&s.local_RAM[887]==16u) {nxt=0xf03378u;s.pc=nxt;s.registers[s.active_bank][16]=s.registers[1u-s.active_bank][0];}
else if(s.local_RAM[886]==210u&&s.local_RAM[887]==180u) {nxt=0xf03378u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][21];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03378u:
if(s.local_RAM[888]==146u&&s.local_RAM[889]==148u) {nxt=0xf0337au;s.pc=nxt;s.registers[1u-s.active_bank][20]=s.registers[s.active_bank][20];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0337au:
if(s.local_RAM[890]==137u&&s.local_RAM[891]==133u) {nxt=0xf0337cu;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][12];}
else if(s.local_RAM[890]==174u&&s.local_RAM[891]==160u) {nxt=0xf0337cu;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+84u,&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0337cu:
if(s.local_RAM[892]==146u&&s.local_RAM[893]==0u) {nxt=0xf0337eu;s.pc=nxt;s.registers[1u-s.active_bank][0]=s.registers[s.active_bank][16];}
else if(s.local_RAM[892]==208u&&s.local_RAM[893]==0u) {nxt=0xf0337eu;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0337eu:
if(s.local_RAM[894]==140u&&s.local_RAM[895]==27u) {nxt=0xf03380u;s.pc=nxt;s.registers[s.active_bank][27]=0u;}
else if(s.local_RAM[894]==228u&&s.local_RAM[895]==0u) {nxt=0xf03380u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03380u:
if(s.local_RAM[896]==139u&&s.local_RAM[897]==124u) {nxt=0xf03382u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][27];}
else if(s.local_RAM[896]==152u&&s.local_RAM[897]==0u&&s.local_RAM[898]==63u&&s.local_RAM[899]==96u&&s.local_RAM[900]==0u&&s.local_RAM[901]==240u) {nxt=0xf03386u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03382u:
if(s.local_RAM[898]==88u&&s.local_RAM[899]==5u) {nxt=0xf03384u;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;if(s.registers[s.active_bank][5]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][5]=0u-s.registers[s.active_bank][5];s.n=0;s.z=s.registers[s.active_bank][5]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03384u:
if(s.local_RAM[900]==7u&&s.local_RAM[901]==155u) {nxt=0xf03386u;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03386u:
if(s.local_RAM[902]==88u&&s.local_RAM[903]==16u) {nxt=0xf03388u;s.pc=nxt;s.c=s.registers[s.active_bank][16]>>31;if(s.registers[s.active_bank][16]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][16]=0u-s.registers[s.active_bank][16];s.n=0;s.z=s.registers[s.active_bank][16]==0;}}
else if(s.local_RAM[902]==164u&&s.local_RAM[903]==1u) {nxt=0xf03388u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03388u:
if(s.local_RAM[904]==7u&&s.local_RAM[905]==155u) {nxt=0xf0338au;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else if(s.local_RAM[904]==9u&&s.local_RAM[905]==1u) {nxt=0xf0338au;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],8u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0338au:
if(s.local_RAM[906]==138u&&s.local_RAM[907]==28u) {nxt=0xf0338cu;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][16];}
else if(s.local_RAM[906]==164u&&s.local_RAM[907]==34u) {nxt=0xf0338cu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0338cu:
if(s.local_RAM[908]==64u&&s.local_RAM[909]==188u) {nxt=0xf0338eu;s.pc=nxt;s.registers[s.active_bank][28]=(s.registers[s.active_bank][28]&0xffffu)*(s.registers[s.active_bank][5]&0xffffu);
   zn(&s,s.registers[s.active_bank][28]);}
else if(s.local_RAM[908]==152u&&s.local_RAM[909]==0u&&s.local_RAM[910]==0u&&s.local_RAM[911]==192u&&s.local_RAM[912]==0u&&s.local_RAM[913]==0u) {nxt=0xf03392u;s.pc=nxt;s.registers[s.active_bank][0]=0xc0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0338eu:
if(s.local_RAM[910]==136u&&s.local_RAM[911]==189u) {nxt=0xf03390u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03390u:
if(s.local_RAM[912]==102u&&s.local_RAM[913]==28u) {nxt=0xf03392u;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>16;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03392u:
if(s.local_RAM[914]==0u&&s.local_RAM[915]==2u) {nxt=0xf03394u;s.pc=nxt;s.registers[s.active_bank][2]=add(&s,s.registers[s.active_bank][2],s.registers[s.active_bank][0]);}
else if(s.local_RAM[914]==102u&&s.local_RAM[915]==29u) {nxt=0xf03394u;s.pc=nxt;s.c=s.registers[s.active_bank][29]&1u;s.registers[s.active_bank][29]=s.registers[s.active_bank][29]>>16;zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03394u:
if(s.local_RAM[916]==66u&&s.local_RAM[917]==29u) {nxt=0xf03396u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][16]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else if(s.local_RAM[916]==152u&&s.local_RAM[917]==0u&&s.local_RAM[918]==0u&&s.local_RAM[919]==36u&&s.local_RAM[920]==0u&&s.local_RAM[921]==0u) {nxt=0xf0339au;s.pc=nxt;s.registers[s.active_bank][0]=0x24u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03396u:
if(s.local_RAM[918]==102u&&s.local_RAM[919]==16u) {nxt=0xf03398u;s.pc=nxt;s.c=s.registers[s.active_bank][16]&1u;s.registers[s.active_bank][16]=s.registers[s.active_bank][16]>>16;zn(&s,s.registers[s.active_bank][16]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03398u:
if(s.local_RAM[920]==3u&&s.local_RAM[921]==188u) {nxt=0xf0339au;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0339au:
if(s.local_RAM[922]==0u&&s.local_RAM[923]==96u) {nxt=0xf0339cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[922]==138u&&s.local_RAM[923]==29u) {nxt=0xf0339cu;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][16];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0339cu:
if(s.local_RAM[924]==64u&&s.local_RAM[925]==189u) {nxt=0xf0339eu;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][5]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else if(s.local_RAM[924]==164u&&s.local_RAM[925]==4u) {nxt=0xf0339eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0339eu:
if(s.local_RAM[926]==102u&&s.local_RAM[927]==5u) {nxt=0xf033a0u;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]>>16;zn(&s,s.registers[s.active_bank][5]);}
else if(s.local_RAM[926]==152u&&s.local_RAM[927]==0u&&s.local_RAM[928]==0u&&s.local_RAM[929]==40u&&s.local_RAM[930]==0u&&s.local_RAM[931]==0u) {nxt=0xf033a4u;s.pc=nxt;s.registers[s.active_bank][0]=0x28u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033a0u:
if(s.local_RAM[928]==3u&&s.local_RAM[929]==188u) {nxt=0xf033a2u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033a2u:
if(s.local_RAM[930]==66u&&s.local_RAM[931]==5u) {nxt=0xf033a4u;s.pc=nxt;s.registers[s.active_bank][5]=(s.registers[s.active_bank][5]&0xffffu)*(s.registers[s.active_bank][16]&0xffffu);
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033a4u:
if(s.local_RAM[932]==0u&&s.local_RAM[933]==96u) {nxt=0xf033a6u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[932]==98u&&s.local_RAM[933]==5u) {nxt=0xf033a6u;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]<<16;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033a6u:
if(s.local_RAM[934]==3u&&s.local_RAM[935]==133u) {nxt=0xf033a8u;s.pc=nxt;s.registers[s.active_bank][5]=add(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][28]);}
else if(s.local_RAM[934]==164u&&s.local_RAM[935]==5u) {nxt=0xf033a8u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][5]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033a8u:
if(s.local_RAM[936]==52u&&s.local_RAM[937]==27u) {nxt=0xf033aau;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>0)&1u;}
else if(s.local_RAM[936]==99u&&s.local_RAM[937]==229u) {nxt=0xf033aau;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]<<1;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033aau:
if(s.local_RAM[938]==188u&&s.local_RAM[939]==68u) {nxt=0xf033acu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][2])?(s.registers[s.active_bank][2]&~3u):s.registers[s.active_bank][2],s.registers[s.active_bank][4]));}
else if(s.local_RAM[938]==212u&&s.local_RAM[939]==66u) {nxt=0xf033acu;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf033b0u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033acu:
if(s.local_RAM[940]==8u&&s.local_RAM[941]==130u) {nxt=0xf033aeu;s.pc=nxt;s.registers[s.active_bank][2]=add(&s,s.registers[s.active_bank][2],4u);}
else if(s.local_RAM[940]==148u&&s.local_RAM[941]==16u) {nxt=0xf033aeu;s.pc=nxt;s.registers[s.active_bank][16]=s.registers[1u-s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033aeu:
if(s.local_RAM[942]==188u&&s.local_RAM[943]==69u) {nxt=0xf033b0u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][2])?(s.registers[s.active_bank][2]&~3u):s.registers[s.active_bank][2],s.registers[s.active_bank][5]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033b0u:
if(s.local_RAM[944]==9u&&s.local_RAM[945]==2u) {nxt=0xf033b2u;s.pc=nxt;s.registers[s.active_bank][2]=add(&s,s.registers[s.active_bank][2],8u);}
else if(s.local_RAM[944]==32u&&s.local_RAM[945]==5u) {nxt=0xf033b2u;s.pc=nxt;s.registers[s.active_bank][5]=sub(&s,0,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033b2u:
if(s.local_RAM[946]==137u&&s.local_RAM[947]==134u) {nxt=0xf033b4u;s.pc=nxt;s.registers[s.active_bank][6]=s.registers[s.active_bank][12];}
else if(s.local_RAM[946]==152u&&s.local_RAM[947]==0u&&s.local_RAM[948]==0u&&s.local_RAM[949]==5u&&s.local_RAM[950]==0u&&s.local_RAM[951]==0u) {nxt=0xf033b8u;s.pc=nxt;s.registers[s.active_bank][0]=0x5u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033b4u:
if(s.local_RAM[948]==146u&&s.local_RAM[949]==32u) {nxt=0xf033b6u;s.pc=nxt;s.registers[1u-s.active_bank][0]=s.registers[s.active_bank][17];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033b6u:
if(s.local_RAM[950]==140u&&s.local_RAM[951]==27u) {nxt=0xf033b8u;s.pc=nxt;s.registers[s.active_bank][27]=0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033b8u:
if(s.local_RAM[952]==139u&&s.local_RAM[953]==124u) {nxt=0xf033bau;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][27];}
else if(s.local_RAM[952]==184u&&s.local_RAM[953]==64u) {nxt=0xf033bau;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][2],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033bau:
if(s.local_RAM[954]==88u&&s.local_RAM[955]==6u) {nxt=0xf033bcu;s.pc=nxt;s.c=s.registers[s.active_bank][6]>>31;if(s.registers[s.active_bank][6]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][6]=0u-s.registers[s.active_bank][6];s.n=0;s.z=s.registers[s.active_bank][6]==0;}}
else if(s.local_RAM[954]==152u&&s.local_RAM[955]==0u&&s.local_RAM[956]==0u&&s.local_RAM[957]==84u&&s.local_RAM[958]==0u&&s.local_RAM[959]==0u) {nxt=0xf033c0u;s.pc=nxt;s.registers[s.active_bank][0]=0x54u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033bcu:
if(s.local_RAM[956]==7u&&s.local_RAM[957]==155u) {nxt=0xf033beu;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033beu:
if(s.local_RAM[958]==88u&&s.local_RAM[959]==17u) {nxt=0xf033c0u;s.pc=nxt;s.c=s.registers[s.active_bank][17]>>31;if(s.registers[s.active_bank][17]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][17]=0u-s.registers[s.active_bank][17];s.n=0;s.z=s.registers[s.active_bank][17]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033c0u:
if(s.local_RAM[960]==0u&&s.local_RAM[961]==96u) {nxt=0xf033c2u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[960]==7u&&s.local_RAM[961]==155u) {nxt=0xf033c2u;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033c2u:
if(s.local_RAM[962]==138u&&s.local_RAM[963]==60u) {nxt=0xf033c4u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][17];}
else if(s.local_RAM[962]==164u&&s.local_RAM[963]==27u) {nxt=0xf033c4u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][27]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033c4u:
if(s.local_RAM[964]==64u&&s.local_RAM[965]==220u) {nxt=0xf033c6u;s.pc=nxt;s.registers[s.active_bank][28]=(s.registers[s.active_bank][28]&0xffffu)*(s.registers[s.active_bank][6]&0xffffu);
   zn(&s,s.registers[s.active_bank][28]);}
else if(s.local_RAM[964]==101u&&s.local_RAM[965]==27u) {nxt=0xf033c6u;s.pc=nxt;s.c=s.registers[s.active_bank][27]&1u;s.registers[s.active_bank][27]=s.registers[s.active_bank][27]>>8;zn(&s,s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033c6u:
if(s.local_RAM[966]==136u&&s.local_RAM[967]==221u) {nxt=0xf033c8u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][6];}
else if(s.local_RAM[966]==152u&&s.local_RAM[967]==0u&&s.local_RAM[968]==0u&&s.local_RAM[969]==224u&&s.local_RAM[970]==0u&&s.local_RAM[971]==0u) {nxt=0xf033ccu;s.pc=nxt;s.registers[s.active_bank][0]=0xe0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033c8u:
if(s.local_RAM[968]==102u&&s.local_RAM[969]==28u) {nxt=0xf033cau;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>16;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033cau:
if(s.local_RAM[970]==102u&&s.local_RAM[971]==29u) {nxt=0xf033ccu;s.pc=nxt;s.c=s.registers[s.active_bank][29]&1u;s.registers[s.active_bank][29]=s.registers[s.active_bank][29]>>16;zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033ccu:
if(s.local_RAM[972]==0u&&s.local_RAM[973]==96u) {nxt=0xf033ceu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[972]==66u&&s.local_RAM[973]==61u) {nxt=0xf033ceu;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][17]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033ceu:
if(s.local_RAM[974]==102u&&s.local_RAM[975]==17u) {nxt=0xf033d0u;s.pc=nxt;s.c=s.registers[s.active_bank][17]&1u;s.registers[s.active_bank][17]=s.registers[s.active_bank][17]>>16;zn(&s,s.registers[s.active_bank][17]);}
else if(s.local_RAM[974]==164u&&s.local_RAM[975]==7u) {nxt=0xf033d0u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][7]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033d0u:
if(s.local_RAM[976]==3u&&s.local_RAM[977]==188u) {nxt=0xf033d2u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else if(s.local_RAM[976]==152u&&s.local_RAM[977]==0u&&s.local_RAM[978]==0u&&s.local_RAM[979]==228u&&s.local_RAM[980]==0u&&s.local_RAM[981]==0u) {nxt=0xf033d6u;s.pc=nxt;s.registers[s.active_bank][0]=0xe4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033d2u:
if(s.local_RAM[978]==138u&&s.local_RAM[979]==61u) {nxt=0xf033d4u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][17];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033d4u:
if(s.local_RAM[980]==64u&&s.local_RAM[981]==221u) {nxt=0xf033d6u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][6]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033d6u:
if(s.local_RAM[982]==0u&&s.local_RAM[983]==96u) {nxt=0xf033d8u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else if(s.local_RAM[982]==102u&&s.local_RAM[983]==6u) {nxt=0xf033d8u;s.pc=nxt;s.c=s.registers[s.active_bank][6]&1u;s.registers[s.active_bank][6]=s.registers[s.active_bank][6]>>16;zn(&s,s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033d8u:
if(s.local_RAM[984]==3u&&s.local_RAM[985]==188u) {nxt=0xf033dau;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else if(s.local_RAM[984]==164u&&s.local_RAM[985]==8u) {nxt=0xf033dau;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][8]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033dau:
if(s.local_RAM[986]==66u&&s.local_RAM[987]==38u) {nxt=0xf033dcu;s.pc=nxt;s.registers[s.active_bank][6]=(s.registers[s.active_bank][6]&0xffffu)*(s.registers[s.active_bank][17]&0xffffu);
   zn(&s,s.registers[s.active_bank][6]);}
else if(s.local_RAM[986]==152u&&s.local_RAM[987]==29u&&s.local_RAM[988]==255u&&s.local_RAM[989]==255u&&s.local_RAM[990]==0u&&s.local_RAM[991]==31u) {nxt=0xf033e0u;s.pc=nxt;s.registers[s.active_bank][29]=0x1fffffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033dcu:
if(s.local_RAM[988]==98u&&s.local_RAM[989]==6u) {nxt=0xf033deu;s.pc=nxt;s.c=s.registers[s.active_bank][6]>>31;s.registers[s.active_bank][6]=s.registers[s.active_bank][6]<<16;zn(&s,s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033deu:
if(s.local_RAM[990]==3u&&s.local_RAM[991]==134u) {nxt=0xf033e0u;s.pc=nxt;s.registers[s.active_bank][6]=add(&s,s.registers[s.active_bank][6],s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033e0u:
if(s.local_RAM[992]==52u&&s.local_RAM[993]==27u) {nxt=0xf033e2u;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>0)&1u;}
else if(s.local_RAM[992]==137u&&s.local_RAM[993]==1u) {nxt=0xf033e2u;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033e2u:
if(s.local_RAM[994]==136u&&s.local_RAM[995]==224u) {nxt=0xf033e4u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][7];}
else if(s.local_RAM[994]==212u&&s.local_RAM[995]==66u) {nxt=0xf033e4u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf033e8u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033e4u:
if(s.local_RAM[996]==139u&&s.local_RAM[997]==190u) {nxt=0xf033e6u;s.pc=nxt;s.registers[s.active_bank][30]=s.registers[s.active_bank][29];}
else if(s.local_RAM[996]==148u&&s.local_RAM[997]==17u) {nxt=0xf033e6u;s.pc=nxt;s.registers[s.active_bank][17]=s.registers[1u-s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033e6u:
if(s.local_RAM[998]==136u&&s.local_RAM[999]==31u) {nxt=0xf033e8u;s.pc=nxt;s.registers[s.active_bank][31]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033e8u:
if(s.local_RAM[1000]==136u&&s.local_RAM[1001]==37u) {nxt=0xf033eau;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][1];}
else if(s.local_RAM[1000]==152u&&s.local_RAM[1001]==9u&&s.local_RAM[1002]==255u&&s.local_RAM[1003]==255u&&s.local_RAM[1004]==0u&&s.local_RAM[1005]==0u) {nxt=0xf033eeu;s.pc=nxt;s.registers[s.active_bank][9]=0xffffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033eau:
if(s.local_RAM[1002]==39u&&s.local_RAM[1003]==223u) {nxt=0xf033ecu;s.pc=nxt;s.registers[s.active_bank][31]&=s.registers[s.active_bank][30];
   zn(&s,s.registers[s.active_bank][31]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033ecu:
if(s.local_RAM[1004]==39u&&s.local_RAM[1005]==197u) {nxt=0xf033eeu;s.pc=nxt;s.registers[s.active_bank][5]&=s.registers[s.active_bank][30];
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033eeu:
if(s.local_RAM[1006]==100u&&s.local_RAM[1007]==62u) {nxt=0xf033f0u;s.pc=nxt;s.c=s.registers[s.active_bank][30]&1u;s.registers[s.active_bank][30]=s.registers[s.active_bank][30]>>1;zn(&s,s.registers[s.active_bank][30]);}
else if(s.local_RAM[1006]==136u&&s.local_RAM[1007]==103u) {nxt=0xf033f0u;s.pc=nxt;s.registers[s.active_bank][7]=s.registers[s.active_bank][3];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033f0u:
if(s.local_RAM[1008]==19u&&s.local_RAM[1009]==223u) {nxt=0xf033f2u;s.pc=nxt;s.registers[s.active_bank][31]=sub(&s,s.registers[s.active_bank][31],s.registers[s.active_bank][30]);}
else if(s.local_RAM[1008]==136u&&s.local_RAM[1009]==245u) {nxt=0xf033f2u;s.pc=nxt;s.registers[s.active_bank][21]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033f2u:
if(s.local_RAM[1010]==136u&&s.local_RAM[1011]==251u) {nxt=0xf033f4u;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][7];}
else if(s.local_RAM[1010]==212u&&s.local_RAM[1011]==84u) {nxt=0xf033f4u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf033f8u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033f4u:
if(s.local_RAM[1012]==88u&&s.local_RAM[1013]==7u) {nxt=0xf033f6u;s.pc=nxt;s.c=s.registers[s.active_bank][7]>>31;if(s.registers[s.active_bank][7]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][7]=0u-s.registers[s.active_bank][7];s.n=0;s.z=s.registers[s.active_bank][7]==0;}}
else if(s.local_RAM[1012]==228u&&s.local_RAM[1013]==0u) {nxt=0xf033f6u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033f6u:
if(s.local_RAM[1014]==32u&&s.local_RAM[1015]==31u) {nxt=0xf033f8u;s.pc=nxt;s.registers[s.active_bank][31]=sub(&s,0,s.registers[s.active_bank][31]);}
else if(s.local_RAM[1014]==86u&&s.local_RAM[1015]==231u) {nxt=0xf033f8u;s.pc=nxt;divide(&s,23,7);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033f8u:
if(s.local_RAM[1016]==19u&&s.local_RAM[1017]==197u) {nxt=0xf033fau;s.pc=nxt;s.registers[s.active_bank][5]=sub(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][30]);}
else if(s.local_RAM[1016]==55u&&s.local_RAM[1017]==251u) {nxt=0xf033fau;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>31)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033fau:
if(s.local_RAM[1018]==212u&&s.local_RAM[1019]==66u) {nxt=0xf033fcu;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03400u;}}
else if(s.local_RAM[1018]==212u&&s.local_RAM[1019]==84u) {nxt=0xf033fcu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf03400u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf033fcu:
if(s.local_RAM[1020]==228u&&s.local_RAM[1021]==0u) {nxt=0xf033feu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03400u:
if(s.local_RAM[1024]==102u&&s.local_RAM[1025]==31u) {nxt=0xf03402u;s.pc=nxt;s.c=s.registers[s.active_bank][31]&1u;s.registers[s.active_bank][31]=s.registers[s.active_bank][31]>>16;zn(&s,s.registers[s.active_bank][31]);}
else if(s.local_RAM[1024]==136u&&s.local_RAM[1025]==232u) {nxt=0xf03402u;s.pc=nxt;s.registers[s.active_bank][8]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03402u:
if(s.local_RAM[1026]==102u&&s.local_RAM[1027]==5u) {nxt=0xf03404u;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]>>16;zn(&s,s.registers[s.active_bank][5]);}
else if(s.local_RAM[1026]==102u&&s.local_RAM[1027]==7u) {nxt=0xf03404u;s.pc=nxt;s.c=s.registers[s.active_bank][7]&1u;s.registers[s.active_bank][7]=s.registers[s.active_bank][7]>>16;zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03404u:
if(s.local_RAM[1028]==37u&&s.local_RAM[1029]==40u) {nxt=0xf03406u;s.pc=nxt;s.registers[s.active_bank][8]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][8]);}
else if(s.local_RAM[1028]==99u&&s.local_RAM[1029]==159u) {nxt=0xf03406u;s.pc=nxt;s.c=s.registers[s.active_bank][31]>>31;s.registers[s.active_bank][31]=s.registers[s.active_bank][31]<<4;zn(&s,s.registers[s.active_bank][31]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03406u:
if(s.local_RAM[1030]==43u&&s.local_RAM[1031]==229u) {nxt=0xf03408u;s.pc=nxt;s.registers[s.active_bank][5]|=s.registers[s.active_bank][31];
   zn(&s,s.registers[s.active_bank][5]);}
else if(s.local_RAM[1030]==136u&&s.local_RAM[1031]==139u) {nxt=0xf03408u;s.pc=nxt;s.registers[s.active_bank][11]=s.registers[s.active_bank][4];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03408u:
if(s.local_RAM[1032]==99u&&s.local_RAM[1033]==5u) {nxt=0xf0340au;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]<<8;zn(&s,s.registers[s.active_bank][5]);}
else if(s.local_RAM[1032]==137u&&s.local_RAM[1033]==118u) {nxt=0xf0340au;s.pc=nxt;s.registers[s.active_bank][22]=s.registers[s.active_bank][11];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0340au:
if(s.local_RAM[1034]==137u&&s.local_RAM[1035]==123u) {nxt=0xf0340cu;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][11];}
else if(s.local_RAM[1034]==152u&&s.local_RAM[1035]==0u&&s.local_RAM[1036]==63u&&s.local_RAM[1037]==96u&&s.local_RAM[1038]==0u&&s.local_RAM[1039]==240u) {nxt=0xf03410u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0340cu:
if(s.local_RAM[1036]==88u&&s.local_RAM[1037]==11u) {nxt=0xf0340eu;s.pc=nxt;s.c=s.registers[s.active_bank][11]>>31;if(s.registers[s.active_bank][11]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][11]=0u-s.registers[s.active_bank][11];s.n=0;s.z=s.registers[s.active_bank][11]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0340eu:
if(s.local_RAM[1038]==86u&&s.local_RAM[1039]==235u) {nxt=0xf03410u;s.pc=nxt;divide(&s,23,11);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03410u:
if(s.local_RAM[1040]==43u&&s.local_RAM[1041]==101u) {nxt=0xf03412u;s.pc=nxt;s.registers[s.active_bank][5]|=s.registers[s.active_bank][27];
   zn(&s,s.registers[s.active_bank][5]);}
else if(s.local_RAM[1040]==55u&&s.local_RAM[1041]==251u) {nxt=0xf03412u;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>31)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03412u:
if(s.local_RAM[1042]==164u&&s.local_RAM[1043]==1u) {nxt=0xf03414u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else if(s.local_RAM[1042]==212u&&s.local_RAM[1043]==66u) {nxt=0xf03414u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03418u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03414u:
if(s.local_RAM[1044]==24u&&s.local_RAM[1045]==129u) {nxt=0xf03416u;s.pc=nxt;s.registers[s.active_bank][1]=sub(&s,s.registers[s.active_bank][1],4u);}
else if(s.local_RAM[1044]==228u&&s.local_RAM[1045]==0u) {nxt=0xf03416u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03416u:
if(s.local_RAM[1046]==184u&&s.local_RAM[1047]==37u) {nxt=0xf03418u;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][1],s.registers[s.active_bank][5]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03418u:
if(s.local_RAM[1048]==137u&&s.local_RAM[1049]==108u) {nxt=0xf0341au;s.pc=nxt;s.registers[s.active_bank][12]=s.registers[s.active_bank][11];}
else if(s.local_RAM[1048]==174u&&s.local_RAM[1049]==160u) {nxt=0xf0341au;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+84u,&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0341au:
if(s.local_RAM[1050]==37u&&s.local_RAM[1051]==75u) {nxt=0xf0341cu;s.pc=nxt;s.registers[s.active_bank][11]&=s.registers[s.active_bank][10];
   zn(&s,s.registers[s.active_bank][11]);}
else if(s.local_RAM[1050]==208u&&s.local_RAM[1051]==0u) {nxt=0xf0341cu;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0341cu:
if(s.local_RAM[1052]==98u&&s.local_RAM[1053]==12u) {nxt=0xf0341eu;s.pc=nxt;s.c=s.registers[s.active_bank][12]>>31;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]<<16;zn(&s,s.registers[s.active_bank][12]);}
else if(s.local_RAM[1052]==228u&&s.local_RAM[1053]==0u) {nxt=0xf0341eu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0341eu:
if(s.local_RAM[1054]==41u&&s.local_RAM[1055]==103u) {nxt=0xf03420u;s.pc=nxt;s.registers[s.active_bank][7]|=s.registers[s.active_bank][11];
   zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03420u:
if(s.local_RAM[1056]==41u&&s.local_RAM[1057]==136u) {nxt=0xf03422u;s.pc=nxt;s.registers[s.active_bank][8]|=s.registers[s.active_bank][12];
   zn(&s,s.registers[s.active_bank][8]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03422u:
if(s.local_RAM[1058]==144u&&s.local_RAM[1059]==231u) {nxt=0xf03424u;s.pc=nxt;s.registers[1u-s.active_bank][7]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03424u:
if(s.local_RAM[1060]==145u&&s.local_RAM[1061]==8u) {nxt=0xf03426u;s.pc=nxt;s.registers[1u-s.active_bank][8]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03426u:
if(s.local_RAM[1062]==136u&&s.local_RAM[1063]==167u) {nxt=0xf03428u;s.pc=nxt;s.registers[s.active_bank][7]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03428u:
if(s.local_RAM[1064]==136u&&s.local_RAM[1065]==251u) {nxt=0xf0342au;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0342au:
if(s.local_RAM[1066]==88u&&s.local_RAM[1067]==7u) {nxt=0xf0342cu;s.pc=nxt;s.c=s.registers[s.active_bank][7]>>31;if(s.registers[s.active_bank][7]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][7]=0u-s.registers[s.active_bank][7];s.n=0;s.z=s.registers[s.active_bank][7]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0342cu:
if(s.local_RAM[1068]==87u&&s.local_RAM[1069]==7u) {nxt=0xf0342eu;s.pc=nxt;divide(&s,24,7);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0342eu:
if(s.local_RAM[1070]==55u&&s.local_RAM[1071]==251u) {nxt=0xf03430u;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>31)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03430u:
if(s.local_RAM[1072]==212u&&s.local_RAM[1073]==66u) {nxt=0xf03432u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03436u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03432u:
if(s.local_RAM[1074]==228u&&s.local_RAM[1075]==0u) {nxt=0xf03434u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03436u:
if(s.local_RAM[1078]==18u&&s.local_RAM[1079]==167u) {nxt=0xf03438u;s.pc=nxt;s.registers[s.active_bank][7]=sub(&s,s.registers[s.active_bank][7],s.registers[s.active_bank][21]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03438u:
if(s.local_RAM[1080]==136u&&s.local_RAM[1081]==232u) {nxt=0xf0343au;s.pc=nxt;s.registers[s.active_bank][8]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0343au:
if(s.local_RAM[1082]==102u&&s.local_RAM[1083]==7u) {nxt=0xf0343cu;s.pc=nxt;s.c=s.registers[s.active_bank][7]&1u;s.registers[s.active_bank][7]=s.registers[s.active_bank][7]>>16;zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0343cu:
if(s.local_RAM[1084]==37u&&s.local_RAM[1085]==40u) {nxt=0xf0343eu;s.pc=nxt;s.registers[s.active_bank][8]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][8]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0343eu:
if(s.local_RAM[1086]==136u&&s.local_RAM[1087]==203u) {nxt=0xf03440u;s.pc=nxt;s.registers[s.active_bank][11]=s.registers[s.active_bank][6];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03440u:
if(s.local_RAM[1088]==137u&&s.local_RAM[1089]==123u) {nxt=0xf03442u;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][11];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03442u:
if(s.local_RAM[1090]==88u&&s.local_RAM[1091]==11u) {nxt=0xf03444u;s.pc=nxt;s.c=s.registers[s.active_bank][11]>>31;if(s.registers[s.active_bank][11]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][11]=0u-s.registers[s.active_bank][11];s.n=0;s.z=s.registers[s.active_bank][11]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03444u:
if(s.local_RAM[1092]==87u&&s.local_RAM[1093]==11u) {nxt=0xf03446u;s.pc=nxt;divide(&s,24,11);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03446u:
if(s.local_RAM[1094]==55u&&s.local_RAM[1095]==251u) {nxt=0xf03448u;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>31)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03448u:
if(s.local_RAM[1096]==212u&&s.local_RAM[1097]==66u) {nxt=0xf0344au;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf0344eu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0344au:
if(s.local_RAM[1098]==228u&&s.local_RAM[1099]==0u) {nxt=0xf0344cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0344eu:
if(s.local_RAM[1102]==18u&&s.local_RAM[1103]==203u) {nxt=0xf03450u;s.pc=nxt;s.registers[s.active_bank][11]=sub(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][22]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03450u:
if(s.local_RAM[1104]==137u&&s.local_RAM[1105]==108u) {nxt=0xf03452u;s.pc=nxt;s.registers[s.active_bank][12]=s.registers[s.active_bank][11];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03452u:
if(s.local_RAM[1106]==37u&&s.local_RAM[1107]==75u) {nxt=0xf03454u;s.pc=nxt;s.registers[s.active_bank][11]&=s.registers[s.active_bank][10];
   zn(&s,s.registers[s.active_bank][11]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03454u:
if(s.local_RAM[1108]==98u&&s.local_RAM[1109]==12u) {nxt=0xf03456u;s.pc=nxt;s.c=s.registers[s.active_bank][12]>>31;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]<<16;zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03456u:
if(s.local_RAM[1110]==41u&&s.local_RAM[1111]==103u) {nxt=0xf03458u;s.pc=nxt;s.registers[s.active_bank][7]|=s.registers[s.active_bank][11];
   zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03458u:
if(s.local_RAM[1112]==41u&&s.local_RAM[1113]==136u) {nxt=0xf0345au;s.pc=nxt;s.registers[s.active_bank][8]|=s.registers[s.active_bank][12];
   zn(&s,s.registers[s.active_bank][8]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0345au:
if(s.local_RAM[1114]==152u&&s.local_RAM[1115]==27u&&s.local_RAM[1116]==128u&&s.local_RAM[1117]==0u&&s.local_RAM[1118]==0u&&s.local_RAM[1119]==0u) {nxt=0xf03460u;s.pc=nxt;s.registers[s.active_bank][27]=0x8000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03460u:
if(s.local_RAM[1120]==152u&&s.local_RAM[1121]==0u&&s.local_RAM[1122]==0u&&s.local_RAM[1123]==24u&&s.local_RAM[1124]==0u&&s.local_RAM[1125]==0u) {nxt=0xf03466u;s.pc=nxt;s.registers[s.active_bank][0]=0x18u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03466u:
if(s.local_RAM[1126]==2u&&s.local_RAM[1127]==64u) {nxt=0xf03468u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03468u:
if(s.local_RAM[1128]==164u&&s.local_RAM[1129]==11u) {nxt=0xf0346au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][11]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0346au:
if(s.local_RAM[1130]==3u&&s.local_RAM[1131]==107u) {nxt=0xf0346cu;s.pc=nxt;s.registers[s.active_bank][11]=add(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0346cu:
if(s.local_RAM[1132]==152u&&s.local_RAM[1133]==0u&&s.local_RAM[1134]==0u&&s.local_RAM[1135]==28u&&s.local_RAM[1136]==0u&&s.local_RAM[1137]==0u) {nxt=0xf03472u;s.pc=nxt;s.registers[s.active_bank][0]=0x1cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03472u:
if(s.local_RAM[1138]==2u&&s.local_RAM[1139]==64u) {nxt=0xf03474u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03474u:
if(s.local_RAM[1140]==164u&&s.local_RAM[1141]==12u) {nxt=0xf03476u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][12]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03476u:
if(s.local_RAM[1142]==3u&&s.local_RAM[1143]==108u) {nxt=0xf03478u;s.pc=nxt;s.registers[s.active_bank][12]=add(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03478u:
if(s.local_RAM[1144]==108u&&s.local_RAM[1145]==35u) {nxt=0xf0347au;s.pc=nxt;s.c=s.registers[s.active_bank][3]&1u;s.registers[s.active_bank][3]=sar(s.registers[s.active_bank][3],1);zn(&s,s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0347au:
if(s.local_RAM[1146]==108u&&s.local_RAM[1147]==36u) {nxt=0xf0347cu;s.pc=nxt;s.c=s.registers[s.active_bank][4]&1u;s.registers[s.active_bank][4]=sar(s.registers[s.active_bank][4],1);zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0347cu:
if(s.local_RAM[1148]==16u&&s.local_RAM[1149]==107u) {nxt=0xf0347eu;s.pc=nxt;s.registers[s.active_bank][11]=sub(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0347eu:
if(s.local_RAM[1150]==108u&&s.local_RAM[1151]==37u) {nxt=0xf03480u;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=sar(s.registers[s.active_bank][5],1);zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03480u:
if(s.local_RAM[1152]==16u&&s.local_RAM[1153]==140u) {nxt=0xf03482u;s.pc=nxt;s.registers[s.active_bank][12]=sub(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03482u:
if(s.local_RAM[1154]==108u&&s.local_RAM[1155]==38u) {nxt=0xf03484u;s.pc=nxt;s.c=s.registers[s.active_bank][6]&1u;s.registers[s.active_bank][6]=sar(s.registers[s.active_bank][6],1);zn(&s,s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03484u:
if(s.local_RAM[1156]==16u&&s.local_RAM[1157]==171u) {nxt=0xf03486u;s.pc=nxt;s.registers[s.active_bank][11]=sub(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03486u:
if(s.local_RAM[1158]==16u&&s.local_RAM[1159]==204u) {nxt=0xf03488u;s.pc=nxt;s.registers[s.active_bank][12]=sub(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03488u:
if(s.local_RAM[1160]==137u&&s.local_RAM[1161]==101u) {nxt=0xf0348au;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][11];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0348au:
if(s.local_RAM[1162]==137u&&s.local_RAM[1163]==102u) {nxt=0xf0348cu;s.pc=nxt;s.registers[s.active_bank][6]=s.registers[s.active_bank][11];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0348cu:
if(s.local_RAM[1164]==102u&&s.local_RAM[1165]==5u) {nxt=0xf0348eu;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]>>16;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0348eu:
if(s.local_RAM[1166]==37u&&s.local_RAM[1167]==38u) {nxt=0xf03490u;s.pc=nxt;s.registers[s.active_bank][6]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03490u:
if(s.local_RAM[1168]==137u&&s.local_RAM[1169]==139u) {nxt=0xf03492u;s.pc=nxt;s.registers[s.active_bank][11]=s.registers[s.active_bank][12];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03492u:
if(s.local_RAM[1170]==98u&&s.local_RAM[1171]==12u) {nxt=0xf03494u;s.pc=nxt;s.c=s.registers[s.active_bank][12]>>31;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]<<16;zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03494u:
if(s.local_RAM[1172]==37u&&s.local_RAM[1173]==75u) {nxt=0xf03496u;s.pc=nxt;s.registers[s.active_bank][11]&=s.registers[s.active_bank][10];
   zn(&s,s.registers[s.active_bank][11]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03496u:
if(s.local_RAM[1174]==41u&&s.local_RAM[1175]==134u) {nxt=0xf03498u;s.pc=nxt;s.registers[s.active_bank][6]|=s.registers[s.active_bank][12];
   zn(&s,s.registers[s.active_bank][6]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03498u:
if(s.local_RAM[1176]==41u&&s.local_RAM[1177]==101u) {nxt=0xf0349au;s.pc=nxt;s.registers[s.active_bank][5]|=s.registers[s.active_bank][11];
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0349au:
if(s.local_RAM[1178]==165u&&s.local_RAM[1179]==160u) {nxt=0xf0349cu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][13])?(s.registers[s.active_bank][13]&~3u):s.registers[s.active_bank][13],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0349cu:
if(s.local_RAM[1180]==52u&&s.local_RAM[1181]==0u) {nxt=0xf0349eu;s.pc=nxt;s.z=((~s.registers[s.active_bank][0])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0349eu:
if(s.local_RAM[1182]==215u&&s.local_RAM[1183]==162u) {nxt=0xf034a0u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf0349au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034a0u:
if(s.local_RAM[1184]==228u&&s.local_RAM[1185]==0u) {nxt=0xf034a2u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034a2u:
if(s.local_RAM[1186]==196u&&s.local_RAM[1187]==101u) {nxt=0xf034a4u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+12u,s.registers[s.active_bank][5]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034a4u:
if(s.local_RAM[1188]==196u&&s.local_RAM[1189]==198u) {nxt=0xf034a6u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+24u,s.registers[s.active_bank][6]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034a6u:
if(s.local_RAM[1190]==196u&&s.local_RAM[1191]==135u) {nxt=0xf034a8u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+16u,s.registers[s.active_bank][7]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034a8u:
if(s.local_RAM[1192]==196u&&s.local_RAM[1193]==168u) {nxt=0xf034aau;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+20u,s.registers[s.active_bank][8]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034aau:
if(s.local_RAM[1194]==148u&&s.local_RAM[1195]==231u) {nxt=0xf034acu;s.pc=nxt;s.registers[s.active_bank][7]=s.registers[1u-s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034acu:
if(s.local_RAM[1196]==149u&&s.local_RAM[1197]==8u) {nxt=0xf034aeu;s.pc=nxt;s.registers[s.active_bank][8]=s.registers[1u-s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034aeu:
if(s.local_RAM[1198]==196u&&s.local_RAM[1199]==231u) {nxt=0xf034b0u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+28u,s.registers[s.active_bank][7]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034b0u:
if(s.local_RAM[1200]==197u&&s.local_RAM[1201]==8u) {nxt=0xf034b2u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+32u,s.registers[s.active_bank][8]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034b2u:
if(s.local_RAM[1202]==138u&&s.local_RAM[1203]==224u) {nxt=0xf034b4u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][23];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034b4u:
if(s.local_RAM[1204]==32u&&s.local_RAM[1205]==0u) {nxt=0xf034b6u;s.pc=nxt;s.registers[s.active_bank][0]=sub(&s,0,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034b6u:
if(s.local_RAM[1206]==37u&&s.local_RAM[1207]==32u) {nxt=0xf034b8u;s.pc=nxt;s.registers[s.active_bank][0]&=s.registers[s.active_bank][9];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034b8u:
if(s.local_RAM[1208]==58u&&s.local_RAM[1209]==0u) {nxt=0xf034bau;s.pc=nxt;s.registers[s.active_bank][0]|=(1u<<16);
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034bau:
if(s.local_RAM[1210]==200u&&s.local_RAM[1211]==128u) {nxt=0xf034bcu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][15]+16u,s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034bcu:
if(s.local_RAM[1212]==152u&&s.local_RAM[1213]==0u&&s.local_RAM[1214]==63u&&s.local_RAM[1215]==128u&&s.local_RAM[1216]==0u&&s.local_RAM[1217]==240u) {nxt=0xf034c2u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f80u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034c2u:
if(s.local_RAM[1218]==164u&&s.local_RAM[1219]==21u) {nxt=0xf034c4u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][21]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034c4u:
if(s.local_RAM[1220]==200u&&s.local_RAM[1221]==117u) {nxt=0xf034c6u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][15]+12u,s.registers[s.active_bank][21]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034c6u:
if(s.local_RAM[1222]==98u&&s.local_RAM[1223]==24u) {nxt=0xf034c8u;s.pc=nxt;s.c=s.registers[s.active_bank][24]>>31;s.registers[s.active_bank][24]=s.registers[s.active_bank][24]<<16;zn(&s,s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034c8u:
if(s.local_RAM[1224]==43u&&s.local_RAM[1225]==23u) {nxt=0xf034cau;s.pc=nxt;s.registers[s.active_bank][23]|=s.registers[s.active_bank][24];
   zn(&s,s.registers[s.active_bank][23]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034cau:
if(s.local_RAM[1226]==152u&&s.local_RAM[1227]==0u&&s.local_RAM[1228]==34u&&s.local_RAM[1229]==60u&&s.local_RAM[1230]==0u&&s.local_RAM[1231]==240u) {nxt=0xf034d0u;s.pc=nxt;s.registers[s.active_bank][0]=0xf0223cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034d0u:
if(s.local_RAM[1232]==188u&&s.local_RAM[1233]==23u) {nxt=0xf034d2u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][23]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034d2u:
if(s.local_RAM[1234]==189u&&s.local_RAM[1235]==186u) {nxt=0xf034d4u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][13])?(s.registers[s.active_bank][13]&~3u):s.registers[s.active_bank][13],s.registers[s.active_bank][26]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034d4u:
if(s.local_RAM[1236]==165u&&s.local_RAM[1237]==160u) {nxt=0xf034d6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][13])?(s.registers[s.active_bank][13]&~3u):s.registers[s.active_bank][13],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034d6u:
if(s.local_RAM[1238]==52u&&s.local_RAM[1239]==0u) {nxt=0xf034d8u;s.pc=nxt;s.z=((~s.registers[s.active_bank][0])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034d8u:
if(s.local_RAM[1240]==215u&&s.local_RAM[1241]==162u) {nxt=0xf034dau;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf034d4u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034dau:
if(s.local_RAM[1242]==228u&&s.local_RAM[1243]==0u) {nxt=0xf034dcu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034dcu:
if(s.local_RAM[1244]==152u&&s.local_RAM[1245]==0u&&s.local_RAM[1246]==53u&&s.local_RAM[1247]==22u&&s.local_RAM[1248]==0u&&s.local_RAM[1249]==240u) {nxt=0xf034e2u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03516u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034e2u:
if(s.local_RAM[1250]==208u&&s.local_RAM[1251]==0u) {nxt=0xf034e4u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf034e4u:
if(s.local_RAM[1252]==228u&&s.local_RAM[1253]==0u) {nxt=0xf034e6u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03516u:
if(s.local_RAM[1302]==152u&&s.local_RAM[1303]==14u&&s.local_RAM[1304]==63u&&s.local_RAM[1305]==128u&&s.local_RAM[1306]==0u&&s.local_RAM[1307]==240u) {nxt=0xf0351cu;s.pc=nxt;s.registers[s.active_bank][14]=0xf03f80u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0351cu:
if(s.local_RAM[1308]==174u&&s.local_RAM[1309]==160u) {nxt=0xf0351eu;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+84u,&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0351eu:
if(s.local_RAM[1310]==208u&&s.local_RAM[1311]==0u) {nxt=0xf03520u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03520u:
if(s.local_RAM[1312]==228u&&s.local_RAM[1313]==0u) {nxt=0xf03522u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03598u:
if(s.local_RAM[1432]==152u&&s.local_RAM[1433]==29u&&s.local_RAM[1434]==54u&&s.local_RAM[1435]==26u&&s.local_RAM[1436]==0u&&s.local_RAM[1437]==240u) {nxt=0xf0359eu;s.pc=nxt;s.registers[s.active_bank][29]=0xf0361au;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0359eu:
if(s.local_RAM[1438]==120u&&s.local_RAM[1439]==101u) {nxt=0xf035a0u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035a0u:
if(s.local_RAM[1440]==211u&&s.local_RAM[1441]==184u) {nxt=0xf035a2u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035a2u:
if(s.local_RAM[1442]==228u&&s.local_RAM[1443]==0u) {nxt=0xf035a4u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035a4u:
if(s.local_RAM[1444]==120u&&s.local_RAM[1445]==134u) {nxt=0xf035a6u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][6],s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035a6u:
if(s.local_RAM[1446]==211u&&s.local_RAM[1447]==184u) {nxt=0xf035a8u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035a8u:
if(s.local_RAM[1448]==228u&&s.local_RAM[1449]==0u) {nxt=0xf035aau;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035aau:
if(s.local_RAM[1450]==152u&&s.local_RAM[1451]==14u&&s.local_RAM[1452]==34u&&s.local_RAM[1453]==0u&&s.local_RAM[1454]==0u&&s.local_RAM[1455]==240u) {nxt=0xf035b0u;s.pc=nxt;s.registers[s.active_bank][14]=0xf02200u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035b0u:
if(s.local_RAM[1456]==152u&&s.local_RAM[1457]==17u&&s.local_RAM[1458]==34u&&s.local_RAM[1459]==56u&&s.local_RAM[1460]==0u&&s.local_RAM[1461]==240u) {nxt=0xf035b6u;s.pc=nxt;s.registers[s.active_bank][17]=0xf02238u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035b6u:
if(s.local_RAM[1462]==136u&&s.local_RAM[1463]==128u) {nxt=0xf035b8u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][4];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035b8u:
if(s.local_RAM[1464]==98u&&s.local_RAM[1465]==0u) {nxt=0xf035bau;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<16;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035bau:
if(s.local_RAM[1466]==40u&&s.local_RAM[1467]==96u) {nxt=0xf035bcu;s.pc=nxt;s.registers[s.active_bank][0]|=s.registers[s.active_bank][3];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035bcu:
if(s.local_RAM[1468]==196u&&s.local_RAM[1469]==96u) {nxt=0xf035beu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+12u,s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035beu:
if(s.local_RAM[1470]==136u&&s.local_RAM[1471]==224u) {nxt=0xf035c0u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035c0u:
if(s.local_RAM[1472]==98u&&s.local_RAM[1473]==0u) {nxt=0xf035c2u;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<16;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035c2u:
if(s.local_RAM[1474]==40u&&s.local_RAM[1475]==224u) {nxt=0xf035c4u;s.pc=nxt;s.registers[s.active_bank][0]|=s.registers[s.active_bank][7];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035c4u:
if(s.local_RAM[1476]==152u&&s.local_RAM[1477]==1u&&s.local_RAM[1478]==34u&&s.local_RAM[1479]==104u&&s.local_RAM[1480]==0u&&s.local_RAM[1481]==240u) {nxt=0xf035cau;s.pc=nxt;s.registers[s.active_bank][1]=0xf02268u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035cau:
if(s.local_RAM[1482]==188u&&s.local_RAM[1483]==32u) {nxt=0xf035ccu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035ccu:
if(s.local_RAM[1484]==8u&&s.local_RAM[1485]==129u) {nxt=0xf035ceu;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035ceu:
if(s.local_RAM[1486]==188u&&s.local_RAM[1487]==32u) {nxt=0xf035d0u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035d0u:
if(s.local_RAM[1488]==189u&&s.local_RAM[1489]==200u) {nxt=0xf035d2u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][14])?(s.registers[s.active_bank][14]&~3u):s.registers[s.active_bank][14],s.registers[s.active_bank][8]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035d2u:
if(s.local_RAM[1490]==152u&&s.local_RAM[1491]==0u&&s.local_RAM[1492]==68u&&s.local_RAM[1493]==32u&&s.local_RAM[1494]==0u&&s.local_RAM[1495]==0u) {nxt=0xf035d8u;s.pc=nxt;s.registers[s.active_bank][0]=0x4420u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035d8u:
if(s.local_RAM[1496]==196u&&s.local_RAM[1497]==32u) {nxt=0xf035dau;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+4u,s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035dau:
if(s.local_RAM[1498]==152u&&s.local_RAM[1499]==29u&&s.local_RAM[1500]==54u&&s.local_RAM[1501]==26u&&s.local_RAM[1502]==0u&&s.local_RAM[1503]==240u) {nxt=0xf035e0u;s.pc=nxt;s.registers[s.active_bank][29]=0xf0361au;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035e0u:
if(s.local_RAM[1504]==136u&&s.local_RAM[1505]==187u) {nxt=0xf035e2u;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035e2u:
if(s.local_RAM[1506]==136u&&s.local_RAM[1507]==220u) {nxt=0xf035e4u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][6];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035e4u:
if(s.local_RAM[1508]==16u&&s.local_RAM[1509]==123u) {nxt=0xf035e6u;s.pc=nxt;s.registers[s.active_bank][27]=sub(&s,s.registers[s.active_bank][27],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035e6u:
if(s.local_RAM[1510]==211u&&s.local_RAM[1511]==184u) {nxt=0xf035e8u;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035e8u:
if(s.local_RAM[1512]==16u&&s.local_RAM[1513]==156u) {nxt=0xf035eau;s.pc=nxt;s.registers[s.active_bank][28]=sub(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035eau:
if(s.local_RAM[1514]==211u&&s.local_RAM[1515]==184u) {nxt=0xf035ecu;s.pc=nxt;if(condition(&s,24)){pending=1;target=s.registers[s.active_bank][29];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035ecu:
if(s.local_RAM[1516]==8u&&s.local_RAM[1517]==59u) {nxt=0xf035eeu;s.pc=nxt;s.registers[s.active_bank][27]=add(&s,s.registers[s.active_bank][27],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035eeu:
if(s.local_RAM[1518]==8u&&s.local_RAM[1519]==60u) {nxt=0xf035f0u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035f0u:
if(s.local_RAM[1520]==228u&&s.local_RAM[1521]==0u) {nxt=0xf035f2u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035f2u:
if(s.local_RAM[1522]==139u&&s.local_RAM[1523]==96u) {nxt=0xf035f4u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][27];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035f4u:
if(s.local_RAM[1524]==32u&&s.local_RAM[1525]==0u) {nxt=0xf035f6u;s.pc=nxt;s.registers[s.active_bank][0]=sub(&s,0,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035f6u:
if(s.local_RAM[1526]==98u&&s.local_RAM[1527]==0u) {nxt=0xf035f8u;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<16;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035f8u:
if(s.local_RAM[1528]==102u&&s.local_RAM[1529]==0u) {nxt=0xf035fau;s.pc=nxt;s.c=s.registers[s.active_bank][0]&1u;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]>>16;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035fau:
if(s.local_RAM[1530]==58u&&s.local_RAM[1531]==0u) {nxt=0xf035fcu;s.pc=nxt;s.registers[s.active_bank][0]|=(1u<<16);
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035fcu:
if(s.local_RAM[1532]==196u&&s.local_RAM[1533]==128u) {nxt=0xf035feu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+16u,s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf035feu:
if(s.local_RAM[1534]==152u&&s.local_RAM[1535]==0u&&s.local_RAM[1536]==34u&&s.local_RAM[1537]==60u&&s.local_RAM[1538]==0u&&s.local_RAM[1539]==240u) {nxt=0xf03604u;s.pc=nxt;s.registers[s.active_bank][0]=0xf0223cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03604u:
if(s.local_RAM[1540]==98u&&s.local_RAM[1541]==28u) {nxt=0xf03606u;s.pc=nxt;s.c=s.registers[s.active_bank][28]>>31;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]<<16;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03606u:
if(s.local_RAM[1542]==43u&&s.local_RAM[1543]==124u) {nxt=0xf03608u;s.pc=nxt;s.registers[s.active_bank][28]|=s.registers[s.active_bank][27];
   zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03608u:
if(s.local_RAM[1544]==188u&&s.local_RAM[1545]==28u) {nxt=0xf0360au;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][28]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0360au:
if(s.local_RAM[1546]==152u&&s.local_RAM[1547]==0u&&s.local_RAM[1548]==2u&&s.local_RAM[1549]==0u&&s.local_RAM[1550]==0u&&s.local_RAM[1551]==1u) {nxt=0xf03610u;s.pc=nxt;s.registers[s.active_bank][0]=0x10200u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03610u:
if(s.local_RAM[1552]==190u&&s.local_RAM[1553]==32u) {nxt=0xf03612u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][17])?(s.registers[s.active_bank][17]&~3u):s.registers[s.active_bank][17],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03612u:
if(s.local_RAM[1554]==166u&&s.local_RAM[1555]==32u) {nxt=0xf03614u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][17])?(s.registers[s.active_bank][17]&~3u):s.registers[s.active_bank][17],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03614u:
if(s.local_RAM[1556]==52u&&s.local_RAM[1557]==0u) {nxt=0xf03616u;s.pc=nxt;s.z=((~s.registers[s.active_bank][0])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03616u:
if(s.local_RAM[1558]==215u&&s.local_RAM[1559]==162u) {nxt=0xf03618u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03612u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03618u:
if(s.local_RAM[1560]==228u&&s.local_RAM[1561]==0u) {nxt=0xf0361au;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0361au:
if(s.local_RAM[1562]==211u&&s.local_RAM[1563]==192u) {nxt=0xf0361cu;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][30];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0361cu:
if(s.local_RAM[1564]==0u&&s.local_RAM[1565]==0u) {nxt=0xf0361eu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0365au:
if(s.local_RAM[1626]==152u&&s.local_RAM[1627]==0u&&s.local_RAM[1628]==63u&&s.local_RAM[1629]==96u&&s.local_RAM[1630]==0u&&s.local_RAM[1631]==240u) {nxt=0xf03660u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f60u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03660u:
if(s.local_RAM[1632]==164u&&s.local_RAM[1633]==1u) {nxt=0xf03662u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03662u:
if(s.local_RAM[1634]==11u&&s.local_RAM[1635]==129u) {nxt=0xf03664u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],28u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03664u:
if(s.local_RAM[1636]==164u&&s.local_RAM[1637]==36u) {nxt=0xf03666u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03666u:
if(s.local_RAM[1638]==9u&&s.local_RAM[1639]==1u) {nxt=0xf03668u;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],8u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03668u:
if(s.local_RAM[1640]==164u&&s.local_RAM[1641]==41u) {nxt=0xf0366au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][9]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0366au:
if(s.local_RAM[1642]==8u&&s.local_RAM[1643]==129u) {nxt=0xf0366cu;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0366cu:
if(s.local_RAM[1644]==164u&&s.local_RAM[1645]==42u) {nxt=0xf0366eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][10]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0366eu:
if(s.local_RAM[1646]==152u&&s.local_RAM[1647]==19u&&s.local_RAM[1648]==2u&&s.local_RAM[1649]==0u&&s.local_RAM[1650]==0u&&s.local_RAM[1651]==0u) {nxt=0xf03674u;s.pc=nxt;s.registers[s.active_bank][19]=0x200u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03674u:
if(s.local_RAM[1652]==140u&&s.local_RAM[1653]==139u) {nxt=0xf03676u;s.pc=nxt;s.registers[s.active_bank][11]=4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03676u:
if(s.local_RAM[1654]==152u&&s.local_RAM[1655]==12u&&s.local_RAM[1656]==54u&&s.local_RAM[1657]==144u&&s.local_RAM[1658]==0u&&s.local_RAM[1659]==240u) {nxt=0xf0367cu;s.pc=nxt;s.registers[s.active_bank][12]=0xf03690u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0367cu:
if(s.local_RAM[1660]==152u&&s.local_RAM[1661]==13u&&s.local_RAM[1662]==54u&&s.local_RAM[1663]==170u&&s.local_RAM[1664]==0u&&s.local_RAM[1665]==240u) {nxt=0xf03682u;s.pc=nxt;s.registers[s.active_bank][13]=0xf036aau;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03682u:
if(s.local_RAM[1666]==152u&&s.local_RAM[1667]==0u&&s.local_RAM[1668]==63u&&s.local_RAM[1669]==60u&&s.local_RAM[1670]==0u&&s.local_RAM[1671]==240u) {nxt=0xf03688u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f3cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03688u:
if(s.local_RAM[1672]==164u&&s.local_RAM[1673]==20u) {nxt=0xf0368au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][20]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0368au:
if(s.local_RAM[1674]==46u&&s.local_RAM[1675]==49u) {nxt=0xf0368cu;s.pc=nxt;s.registers[s.active_bank][17]^=s.registers[s.active_bank][17];zn(&s,s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0368cu:
if(s.local_RAM[1676]==101u&&s.local_RAM[1677]==20u) {nxt=0xf0368eu;s.pc=nxt;s.c=s.registers[s.active_bank][20]&1u;s.registers[s.active_bank][20]=s.registers[s.active_bank][20]>>8;zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0368eu:
if(s.local_RAM[1678]==140u&&s.local_RAM[1679]==60u) {nxt=0xf03690u;s.pc=nxt;s.registers[s.active_bank][28]=1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03690u:
if(s.local_RAM[1680]==161u&&s.local_RAM[1681]==37u) {nxt=0xf03692u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][9],&v));s.registers[s.active_bank][5]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03692u:
if(s.local_RAM[1682]==44u&&s.local_RAM[1683]==231u) {nxt=0xf03694u;s.pc=nxt;s.registers[s.active_bank][7]^=s.registers[s.active_bank][7];zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03694u:
if(s.local_RAM[1684]==8u&&s.local_RAM[1685]==73u) {nxt=0xf03696u;s.pc=nxt;s.registers[s.active_bank][9]=add(&s,s.registers[s.active_bank][9],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03696u:
if(s.local_RAM[1686]==161u&&s.local_RAM[1687]==38u) {nxt=0xf03698u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][9],&v));s.registers[s.active_bank][6]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03698u:
if(s.local_RAM[1688]==136u&&s.local_RAM[1689]==200u) {nxt=0xf0369au;s.pc=nxt;s.registers[s.active_bank][8]=s.registers[s.active_bank][6];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0369au:
if(s.local_RAM[1690]==8u&&s.local_RAM[1691]==73u) {nxt=0xf0369cu;s.pc=nxt;s.registers[s.active_bank][9]=add(&s,s.registers[s.active_bank][9],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0369cu:
if(s.local_RAM[1692]==16u&&s.local_RAM[1693]==168u) {nxt=0xf0369eu;s.pc=nxt;s.registers[s.active_bank][8]=sub(&s,s.registers[s.active_bank][8],s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0369eu:
if(s.local_RAM[1694]==212u&&s.local_RAM[1695]==116u) {nxt=0xf036a0u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf036a6u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036a0u:
if(s.local_RAM[1696]==228u&&s.local_RAM[1697]==0u) {nxt=0xf036a2u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036a6u:
if(s.local_RAM[1702]==99u&&s.local_RAM[1703]==197u) {nxt=0xf036a8u;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]<<2;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036a8u:
if(s.local_RAM[1704]==0u&&s.local_RAM[1705]==133u) {nxt=0xf036aau;s.pc=nxt;s.registers[s.active_bank][5]=add(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036aau:
if(s.local_RAM[1706]==164u&&s.local_RAM[1707]==160u) {nxt=0xf036acu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][5])?(s.registers[s.active_bank][5]&~3u):s.registers[s.active_bank][5],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036acu:
if(s.local_RAM[1708]==120u&&s.local_RAM[1709]==224u) {nxt=0xf036aeu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036aeu:
if(s.local_RAM[1710]==212u&&s.local_RAM[1711]==88u) {nxt=0xf036b0u;s.pc=nxt;if(condition(&s,24)){pending=1;target=0xf036b4u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036b0u:
if(s.local_RAM[1712]==8u&&s.local_RAM[1713]==133u) {nxt=0xf036b2u;s.pc=nxt;s.registers[s.active_bank][5]=add(&s,s.registers[s.active_bank][5],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036b2u:
if(s.local_RAM[1714]==136u&&s.local_RAM[1715]==7u) {nxt=0xf036b4u;s.pc=nxt;s.registers[s.active_bank][7]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036b4u:
if(s.local_RAM[1716]==24u&&s.local_RAM[1717]==40u) {nxt=0xf036b6u;s.pc=nxt;s.registers[s.active_bank][8]=sub(&s,s.registers[s.active_bank][8],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036b6u:
if(s.local_RAM[1718]==215u&&s.local_RAM[1719]==52u) {nxt=0xf036b8u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf036aau;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036b8u:
if(s.local_RAM[1720]==228u&&s.local_RAM[1721]==0u) {nxt=0xf036bau;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036bau:
if(s.local_RAM[1722]==99u&&s.local_RAM[1723]==231u) {nxt=0xf036bcu;s.pc=nxt;s.c=s.registers[s.active_bank][7]>>31;s.registers[s.active_bank][7]=s.registers[s.active_bank][7]<<1;zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036bcu:
if(s.local_RAM[1724]==132u&&s.local_RAM[1725]==7u) {nxt=0xf036beu;s.pc=nxt;s.registers[s.active_bank][7]=(s.registers[s.active_bank][7]&0x80000000u)?0u:(s.registers[s.active_bank][7]>0xffffu?0xffffu:s.registers[s.active_bank][7]);zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036beu:
if(s.local_RAM[1726]==161u&&s.local_RAM[1727]==82u) {nxt=0xf036c0u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][10],&v));s.registers[s.active_bank][18]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036c0u:
if(s.local_RAM[1728]==18u&&s.local_RAM[1729]==114u) {nxt=0xf036c2u;s.pc=nxt;s.registers[s.active_bank][18]=sub(&s,s.registers[s.active_bank][18],s.registers[s.active_bank][19]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036c2u:
if(s.local_RAM[1730]==120u&&s.local_RAM[1731]==242u) {nxt=0xf036c4u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][18],s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036c4u:
if(s.local_RAM[1732]==212u&&s.local_RAM[1733]==84u) {nxt=0xf036c6u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf036cau;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036c6u:
if(s.local_RAM[1734]==228u&&s.local_RAM[1735]==0u) {nxt=0xf036c8u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036c8u:
if(s.local_RAM[1736]==136u&&s.local_RAM[1737]==242u) {nxt=0xf036cau;s.pc=nxt;s.registers[s.active_bank][18]=s.registers[s.active_bank][7];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036cau:
if(s.local_RAM[1738]==185u&&s.local_RAM[1739]==82u) {nxt=0xf036ccu;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][10],s.registers[s.active_bank][18]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036ccu:
if(s.local_RAM[1740]==152u&&s.local_RAM[1741]==29u&&s.local_RAM[1742]==3u&&s.local_RAM[1743]==0u&&s.local_RAM[1744]==0u&&s.local_RAM[1745]==0u) {nxt=0xf036d2u;s.pc=nxt;s.registers[s.active_bank][29]=0x300u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036d2u:
if(s.local_RAM[1746]==161u&&s.local_RAM[1747]==32u) {nxt=0xf036d4u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][9],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036d4u:
if(s.local_RAM[1748]==8u&&s.local_RAM[1749]==73u) {nxt=0xf036d6u;s.pc=nxt;s.registers[s.active_bank][9]=add(&s,s.registers[s.active_bank][9],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036d6u:
if(s.local_RAM[1750]==161u&&s.local_RAM[1751]==33u) {nxt=0xf036d8u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][9],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036d8u:
if(s.local_RAM[1752]==44u&&s.local_RAM[1753]==66u) {nxt=0xf036dau;s.pc=nxt;s.registers[s.active_bank][2]^=s.registers[s.active_bank][2];zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036dau:
if(s.local_RAM[1754]==120u&&s.local_RAM[1755]==224u) {nxt=0xf036dcu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036dcu:
if(s.local_RAM[1756]==212u&&s.local_RAM[1757]==180u) {nxt=0xf036deu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf036e8u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036deu:
if(s.local_RAM[1758]==228u&&s.local_RAM[1759]==0u) {nxt=0xf036e0u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036e8u:
if(s.local_RAM[1768]==44u&&s.local_RAM[1769]==66u) {nxt=0xf036eau;s.pc=nxt;s.registers[s.active_bank][2]^=s.registers[s.active_bank][2];zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036eau:
if(s.local_RAM[1770]==19u&&s.local_RAM[1771]==160u) {nxt=0xf036ecu;s.pc=nxt;s.registers[s.active_bank][0]=sub(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036ecu:
if(s.local_RAM[1772]==212u&&s.local_RAM[1773]==84u) {nxt=0xf036eeu;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf036f2u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036eeu:
if(s.local_RAM[1774]==228u&&s.local_RAM[1775]==0u) {nxt=0xf036f0u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036f2u:
if(s.local_RAM[1778]==120u&&s.local_RAM[1779]==225u) {nxt=0xf036f4u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036f4u:
if(s.local_RAM[1780]==212u&&s.local_RAM[1781]==88u) {nxt=0xf036f6u;s.pc=nxt;if(condition(&s,24)){pending=1;target=0xf036fau;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036f6u:
if(s.local_RAM[1782]==228u&&s.local_RAM[1783]==0u) {nxt=0xf036f8u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036f8u:
if(s.local_RAM[1784]==44u&&s.local_RAM[1785]==66u) {nxt=0xf036fau;s.pc=nxt;s.registers[s.active_bank][2]^=s.registers[s.active_bank][2];zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036fau:
if(s.local_RAM[1786]==40u&&s.local_RAM[1787]==81u) {nxt=0xf036fcu;s.pc=nxt;s.registers[s.active_bank][17]|=s.registers[s.active_bank][2];
   zn(&s,s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036fcu:
if(s.local_RAM[1788]==44u&&s.local_RAM[1789]==84u) {nxt=0xf036feu;s.pc=nxt;s.registers[s.active_bank][20]^=s.registers[s.active_bank][2];zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf036feu:
if(s.local_RAM[1790]==24u&&s.local_RAM[1791]==73u) {nxt=0xf03700u;s.pc=nxt;s.registers[s.active_bank][9]=sub(&s,s.registers[s.active_bank][9],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03700u:
if(s.local_RAM[1792]==185u&&s.local_RAM[1793]==32u) {nxt=0xf03702u;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][9],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03702u:
if(s.local_RAM[1794]==8u&&s.local_RAM[1795]==137u) {nxt=0xf03704u;s.pc=nxt;s.registers[s.active_bank][9]=add(&s,s.registers[s.active_bank][9],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03704u:
if(s.local_RAM[1796]==99u&&s.local_RAM[1797]==252u) {nxt=0xf03706u;s.pc=nxt;s.c=s.registers[s.active_bank][28]>>31;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]<<1;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03706u:
if(s.local_RAM[1798]==24u&&s.local_RAM[1799]==43u) {nxt=0xf03708u;s.pc=nxt;s.registers[s.active_bank][11]=sub(&s,s.registers[s.active_bank][11],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03708u:
if(s.local_RAM[1800]==209u&&s.local_RAM[1801]==148u) {nxt=0xf0370au;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][12];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0370au:
if(s.local_RAM[1802]==8u&&s.local_RAM[1803]==74u) {nxt=0xf0370cu;s.pc=nxt;s.registers[s.active_bank][10]=add(&s,s.registers[s.active_bank][10],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0370cu:
if(s.local_RAM[1804]==99u&&s.local_RAM[1805]==20u) {nxt=0xf0370eu;s.pc=nxt;s.c=s.registers[s.active_bank][20]>>31;s.registers[s.active_bank][20]=s.registers[s.active_bank][20]<<8;zn(&s,s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0370eu:
if(s.local_RAM[1806]==152u&&s.local_RAM[1807]==0u&&s.local_RAM[1808]==63u&&s.local_RAM[1809]==60u&&s.local_RAM[1810]==0u&&s.local_RAM[1811]==240u) {nxt=0xf03714u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f3cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03714u:
if(s.local_RAM[1812]==42u&&s.local_RAM[1813]==145u) {nxt=0xf03716u;s.pc=nxt;s.registers[s.active_bank][17]|=s.registers[s.active_bank][20];
   zn(&s,s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03716u:
if(s.local_RAM[1814]==188u&&s.local_RAM[1815]==17u) {nxt=0xf03718u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][17]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03718u:
if(s.local_RAM[1816]==211u&&s.local_RAM[1817]==192u) {nxt=0xf0371au;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][30];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf0371au:
if(s.local_RAM[1818]==228u&&s.local_RAM[1819]==0u) {nxt=0xf0371cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a78u:
if(s.local_RAM[2680]==152u&&s.local_RAM[2681]==14u&&s.local_RAM[2682]==63u&&s.local_RAM[2683]==128u&&s.local_RAM[2684]==0u&&s.local_RAM[2685]==240u) {nxt=0xf03a7eu;s.pc=nxt;s.registers[s.active_bank][14]=0xf03f80u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a7eu:
if(s.local_RAM[2686]==152u&&s.local_RAM[2687]==0u&&s.local_RAM[2688]==63u&&s.local_RAM[2689]==76u&&s.local_RAM[2690]==0u&&s.local_RAM[2691]==240u) {nxt=0xf03a84u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f4cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a84u:
if(s.local_RAM[2692]==140u&&s.local_RAM[2693]==33u) {nxt=0xf03a86u;s.pc=nxt;s.registers[s.active_bank][1]=1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a86u:
if(s.local_RAM[2694]==188u&&s.local_RAM[2695]==1u) {nxt=0xf03a88u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][1]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a88u:
if(s.local_RAM[2696]==164u&&s.local_RAM[2697]==1u) {nxt=0xf03a8au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a8au:
if(s.local_RAM[2698]==124u&&s.local_RAM[2699]==1u) {nxt=0xf03a8cu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a8cu:
if(s.local_RAM[2700]==215u&&s.local_RAM[2701]==161u) {nxt=0xf03a8eu;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf03a88u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a8eu:
if(s.local_RAM[2702]==228u&&s.local_RAM[2703]==0u) {nxt=0xf03a90u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a90u:
if(s.local_RAM[2704]==152u&&s.local_RAM[2705]==2u&&s.local_RAM[2706]==63u&&s.local_RAM[2707]==104u&&s.local_RAM[2708]==0u&&s.local_RAM[2709]==240u) {nxt=0xf03a96u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03f68u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a96u:
if(s.local_RAM[2710]==140u&&s.local_RAM[2711]==161u) {nxt=0xf03a98u;s.pc=nxt;s.registers[s.active_bank][1]=5u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a98u:
if(s.local_RAM[2712]==164u&&s.local_RAM[2713]==64u) {nxt=0xf03a9au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][2])?(s.registers[s.active_bank][2]&~3u):s.registers[s.active_bank][2],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a9au:
if(s.local_RAM[2714]==40u&&s.local_RAM[2715]==33u) {nxt=0xf03a9cu;s.pc=nxt;s.registers[s.active_bank][1]|=s.registers[s.active_bank][1];
   zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a9cu:
if(s.local_RAM[2716]==199u&&s.local_RAM[2717]==1u) {nxt=0xf03a9eu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+96u,s.registers[s.active_bank][1]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03a9eu:
if(s.local_RAM[2718]==152u&&s.local_RAM[2719]==2u&&s.local_RAM[2720]==61u&&s.local_RAM[2721]==192u&&s.local_RAM[2722]==0u&&s.local_RAM[2723]==240u) {nxt=0xf03aa4u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03dc0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aa4u:
if(s.local_RAM[2724]==164u&&s.local_RAM[2725]==3u) {nxt=0xf03aa6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][3]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aa6u:
if(s.local_RAM[2726]==8u&&s.local_RAM[2727]==128u) {nxt=0xf03aa8u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aa8u:
if(s.local_RAM[2728]==124u&&s.local_RAM[2729]==3u) {nxt=0xf03aaau;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][3],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aaau:
if(s.local_RAM[2730]==208u&&s.local_RAM[2731]==66u) {nxt=0xf03aacu;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][2];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aacu:
if(s.local_RAM[2732]==228u&&s.local_RAM[2733]==0u) {nxt=0xf03aaeu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aaeu:
if(s.local_RAM[2734]==40u&&s.local_RAM[2735]==99u) {nxt=0xf03ab0u;s.pc=nxt;s.registers[s.active_bank][3]|=s.registers[s.active_bank][3];
   zn(&s,s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ab0u:
if(s.local_RAM[2736]==40u&&s.local_RAM[2737]==0u) {nxt=0xf03ab2u;s.pc=nxt;s.registers[s.active_bank][0]|=s.registers[s.active_bank][0];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ab2u:
if(s.local_RAM[2738]==198u&&s.local_RAM[2739]==227u) {nxt=0xf03ab4u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+92u,s.registers[s.active_bank][3]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ab4u:
if(s.local_RAM[2740]==199u&&s.local_RAM[2741]==32u) {nxt=0xf03ab6u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+100u,s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ab6u:
if(s.local_RAM[2742]==152u&&s.local_RAM[2743]==1u&&s.local_RAM[2744]==0u&&s.local_RAM[2745]==0u&&s.local_RAM[2746]==0u&&s.local_RAM[2747]==10u) {nxt=0xf03abcu;s.pc=nxt;s.registers[s.active_bank][1]=0xa0000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03abcu:
if(s.local_RAM[2748]==152u&&s.local_RAM[2749]==2u&&s.local_RAM[2750]==58u&&s.local_RAM[2751]==208u&&s.local_RAM[2752]==0u&&s.local_RAM[2753]==240u) {nxt=0xf03ac2u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03ad0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ac2u:
if(s.local_RAM[2754]==152u&&s.local_RAM[2755]==0u&&s.local_RAM[2756]==62u&&s.local_RAM[2757]==130u&&s.local_RAM[2758]==0u&&s.local_RAM[2759]==240u) {nxt=0xf03ac8u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03e82u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ac8u:
if(s.local_RAM[2760]==40u&&s.local_RAM[2761]==66u) {nxt=0xf03acau;s.pc=nxt;s.registers[s.active_bank][2]|=s.registers[s.active_bank][2];
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03acau:
if(s.local_RAM[2762]==198u&&s.local_RAM[2763]==162u) {nxt=0xf03accu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+84u,s.registers[s.active_bank][2]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03accu:
if(s.local_RAM[2764]==208u&&s.local_RAM[2765]==0u) {nxt=0xf03aceu;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03aceu:
if(s.local_RAM[2766]==228u&&s.local_RAM[2767]==0u) {nxt=0xf03ad0u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ad0u:
if(s.local_RAM[2768]==152u&&s.local_RAM[2769]==0u&&s.local_RAM[2770]==59u&&s.local_RAM[2771]==100u&&s.local_RAM[2772]==0u&&s.local_RAM[2773]==240u) {nxt=0xf03ad6u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03b64u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ad6u:
if(s.local_RAM[2774]==124u&&s.local_RAM[2775]==1u) {nxt=0xf03ad8u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ad8u:
if(s.local_RAM[2776]==208u&&s.local_RAM[2777]==2u) {nxt=0xf03adau;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03adau:
if(s.local_RAM[2778]==228u&&s.local_RAM[2779]==0u) {nxt=0xf03adcu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b64u:
if(s.local_RAM[2916]==174u&&s.local_RAM[2917]==227u) {nxt=0xf03b66u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+92u,&v));s.registers[s.active_bank][3]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b66u:
if(s.local_RAM[2918]==152u&&s.local_RAM[2919]==0u&&s.local_RAM[2920]==63u&&s.local_RAM[2921]==84u&&s.local_RAM[2922]==0u&&s.local_RAM[2923]==240u) {nxt=0xf03b6cu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f54u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b6cu:
if(s.local_RAM[2924]==164u&&s.local_RAM[2925]==1u) {nxt=0xf03b6eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b6eu:
if(s.local_RAM[2926]==152u&&s.local_RAM[2927]==0u&&s.local_RAM[2928]==0u&&s.local_RAM[2929]==0u&&s.local_RAM[2930]==0u&&s.local_RAM[2931]==0u) {nxt=0xf03b74u;s.pc=nxt;s.registers[s.active_bank][0]=0x0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b74u:
if(s.local_RAM[2932]==0u&&s.local_RAM[2933]==96u) {nxt=0xf03b76u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b76u:
if(s.local_RAM[2934]==188u&&s.local_RAM[2935]==1u) {nxt=0xf03b78u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][1]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b78u:
if(s.local_RAM[2936]==152u&&s.local_RAM[2937]==0u&&s.local_RAM[2938]==63u&&s.local_RAM[2939]==60u&&s.local_RAM[2940]==0u&&s.local_RAM[2941]==240u) {nxt=0xf03b7eu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f3cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b7eu:
if(s.local_RAM[2942]==164u&&s.local_RAM[2943]==1u) {nxt=0xf03b80u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b80u:
if(s.local_RAM[2944]==152u&&s.local_RAM[2945]==0u&&s.local_RAM[2946]==0u&&s.local_RAM[2947]==240u&&s.local_RAM[2948]==0u&&s.local_RAM[2949]==0u) {nxt=0xf03b86u;s.pc=nxt;s.registers[s.active_bank][0]=0xf0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b86u:
if(s.local_RAM[2950]==0u&&s.local_RAM[2951]==96u) {nxt=0xf03b88u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b88u:
if(s.local_RAM[2952]==188u&&s.local_RAM[2953]==1u) {nxt=0xf03b8au;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][1]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b8au:
if(s.local_RAM[2954]==44u&&s.local_RAM[2955]==33u) {nxt=0xf03b8cu;s.pc=nxt;s.registers[s.active_bank][1]^=s.registers[s.active_bank][1];zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b8cu:
if(s.local_RAM[2956]==152u&&s.local_RAM[2957]==0u&&s.local_RAM[2958]==63u&&s.local_RAM[2959]==88u&&s.local_RAM[2960]==0u&&s.local_RAM[2961]==240u) {nxt=0xf03b92u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f58u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b92u:
if(s.local_RAM[2962]==188u&&s.local_RAM[2963]==1u) {nxt=0xf03b94u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][1]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b94u:
if(s.local_RAM[2964]==152u&&s.local_RAM[2965]==0u&&s.local_RAM[2966]==0u&&s.local_RAM[2967]==252u&&s.local_RAM[2968]==0u&&s.local_RAM[2969]==0u) {nxt=0xf03b9au;s.pc=nxt;s.registers[s.active_bank][0]=0xfcu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b9au:
if(s.local_RAM[2970]==0u&&s.local_RAM[2971]==96u) {nxt=0xf03b9cu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][3]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b9cu:
if(s.local_RAM[2972]==164u&&s.local_RAM[2973]==1u) {nxt=0xf03b9eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03b9eu:
if(s.local_RAM[2974]==152u&&s.local_RAM[2975]==2u&&s.local_RAM[2976]==59u&&s.local_RAM[2977]==178u&&s.local_RAM[2978]==0u&&s.local_RAM[2979]==240u) {nxt=0xf03ba4u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03bb2u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ba4u:
if(s.local_RAM[2980]==152u&&s.local_RAM[2981]==0u&&s.local_RAM[2982]==62u&&s.local_RAM[2983]==130u&&s.local_RAM[2984]==0u&&s.local_RAM[2985]==240u) {nxt=0xf03baau;s.pc=nxt;s.registers[s.active_bank][0]=0xf03e82u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03baau:
if(s.local_RAM[2986]==40u&&s.local_RAM[2987]==66u) {nxt=0xf03bacu;s.pc=nxt;s.registers[s.active_bank][2]|=s.registers[s.active_bank][2];
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bacu:
if(s.local_RAM[2988]==198u&&s.local_RAM[2989]==162u) {nxt=0xf03baeu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+84u,s.registers[s.active_bank][2]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03baeu:
if(s.local_RAM[2990]==208u&&s.local_RAM[2991]==0u) {nxt=0xf03bb0u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bb0u:
if(s.local_RAM[2992]==228u&&s.local_RAM[2993]==0u) {nxt=0xf03bb2u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bb2u:
if(s.local_RAM[2994]==148u&&s.local_RAM[2995]==99u) {nxt=0xf03bb4u;s.pc=nxt;s.registers[s.active_bank][3]=s.registers[1u-s.active_bank][3];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bb4u:
if(s.local_RAM[2996]==149u&&s.local_RAM[2997]==206u) {nxt=0xf03bb6u;s.pc=nxt;s.registers[s.active_bank][14]=s.registers[1u-s.active_bank][14];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bb6u:
if(s.local_RAM[2998]==152u&&s.local_RAM[2999]==0u&&s.local_RAM[3000]==3u&&s.local_RAM[3001]==0u&&s.local_RAM[3002]==0u&&s.local_RAM[3003]==0u) {nxt=0xf03bbcu;s.pc=nxt;s.registers[s.active_bank][0]=0x300u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bbcu:
if(s.local_RAM[3004]==140u&&s.local_RAM[3005]==225u) {nxt=0xf03bbeu;s.pc=nxt;s.registers[s.active_bank][1]=7u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bbeu:
if(s.local_RAM[3006]==0u&&s.local_RAM[3007]==3u) {nxt=0xf03bc0u;s.pc=nxt;s.registers[s.active_bank][3]=add(&s,s.registers[s.active_bank][3],s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bc0u:
if(s.local_RAM[3008]==152u&&s.local_RAM[3009]==20u&&s.local_RAM[3010]==59u&&s.local_RAM[3011]==200u&&s.local_RAM[3012]==0u&&s.local_RAM[3013]==240u) {nxt=0xf03bc6u;s.pc=nxt;s.registers[s.active_bank][20]=0xf03bc8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bc6u:
if(s.local_RAM[3014]==136u&&s.local_RAM[3015]==118u) {nxt=0xf03bc8u;s.pc=nxt;s.registers[s.active_bank][22]=s.registers[s.active_bank][3];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bc8u:
if(s.local_RAM[3016]==166u&&s.local_RAM[3017]==213u) {nxt=0xf03bcau;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][22])?(s.registers[s.active_bank][22]&~3u):s.registers[s.active_bank][22],&v));s.registers[s.active_bank][21]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bcau:
if(s.local_RAM[3018]==8u&&s.local_RAM[3019]==150u) {nxt=0xf03bccu;s.pc=nxt;s.registers[s.active_bank][22]=add(&s,s.registers[s.active_bank][22],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bccu:
if(s.local_RAM[3020]==166u&&s.local_RAM[3021]==192u) {nxt=0xf03bceu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][22])?(s.registers[s.active_bank][22]&~3u):s.registers[s.active_bank][22],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bceu:
if(s.local_RAM[3022]==9u&&s.local_RAM[3023]==22u) {nxt=0xf03bd0u;s.pc=nxt;s.registers[s.active_bank][22]=add(&s,s.registers[s.active_bank][22],8u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bd0u:
if(s.local_RAM[3024]==166u&&s.local_RAM[3025]==196u) {nxt=0xf03bd2u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][22])?(s.registers[s.active_bank][22]&~3u):s.registers[s.active_bank][22],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bd2u:
if(s.local_RAM[3026]==25u&&s.local_RAM[3027]==150u) {nxt=0xf03bd4u;s.pc=nxt;s.registers[s.active_bank][22]=sub(&s,s.registers[s.active_bank][22],12u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bd4u:
if(s.local_RAM[3028]==124u&&s.local_RAM[3029]==196u) {nxt=0xf03bd6u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][4],0x6u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bd6u:
if(s.local_RAM[3030]==212u&&s.local_RAM[3031]==65u) {nxt=0xf03bd8u;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf03bdcu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bd8u:
if(s.local_RAM[3032]==228u&&s.local_RAM[3033]==0u) {nxt=0xf03bdau;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bdcu:
if(s.local_RAM[3036]==0u&&s.local_RAM[3037]==21u) {nxt=0xf03bdeu;s.pc=nxt;s.registers[s.active_bank][21]=add(&s,s.registers[s.active_bank][21],s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bdeu:
if(s.local_RAM[3038]==190u&&s.local_RAM[3039]==213u) {nxt=0xf03be0u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][22])?(s.registers[s.active_bank][22]&~3u):s.registers[s.active_bank][22],s.registers[s.active_bank][21]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03be0u:
if(s.local_RAM[3040]==10u&&s.local_RAM[3041]==22u) {nxt=0xf03be2u;s.pc=nxt;s.registers[s.active_bank][22]=add(&s,s.registers[s.active_bank][22],16u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03be2u:
if(s.local_RAM[3042]==24u&&s.local_RAM[3043]==33u) {nxt=0xf03be4u;s.pc=nxt;s.registers[s.active_bank][1]=sub(&s,s.registers[s.active_bank][1],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03be4u:
if(s.local_RAM[3044]==210u&&s.local_RAM[3045]==148u) {nxt=0xf03be6u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][20];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03be6u:
if(s.local_RAM[3046]==228u&&s.local_RAM[3047]==0u) {nxt=0xf03be8u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03be8u:
if(s.local_RAM[3048]==152u&&s.local_RAM[3049]==0u&&s.local_RAM[3050]==63u&&s.local_RAM[3051]==100u&&s.local_RAM[3052]==0u&&s.local_RAM[3053]==240u) {nxt=0xf03beeu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f64u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03beeu:
if(s.local_RAM[3054]==164u&&s.local_RAM[3055]==4u) {nxt=0xf03bf0u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bf0u:
if(s.local_RAM[3056]==10u&&s.local_RAM[3057]==0u) {nxt=0xf03bf2u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],16u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bf2u:
if(s.local_RAM[3058]==152u&&s.local_RAM[3059]==20u&&s.local_RAM[3060]==255u&&s.local_RAM[3061]==255u&&s.local_RAM[3062]==0u&&s.local_RAM[3063]==0u) {nxt=0xf03bf8u;s.pc=nxt;s.registers[s.active_bank][20]=0xffffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bf8u:
if(s.local_RAM[3064]==152u&&s.local_RAM[3065]==21u&&s.local_RAM[3066]==0u&&s.local_RAM[3067]==255u&&s.local_RAM[3068]==0u&&s.local_RAM[3069]==0u) {nxt=0xf03bfeu;s.pc=nxt;s.registers[s.active_bank][21]=0xffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03bfeu:
if(s.local_RAM[3070]==152u&&s.local_RAM[3071]==22u&&s.local_RAM[3072]==0u&&s.local_RAM[3073]==8u&&s.local_RAM[3074]==0u&&s.local_RAM[3075]==0u) {nxt=0xf03c04u;s.pc=nxt;s.registers[s.active_bank][22]=0x8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c04u:
if(s.local_RAM[3076]==152u&&s.local_RAM[3077]==23u&&s.local_RAM[3078]==60u&&s.local_RAM[3079]==16u&&s.local_RAM[3080]==0u&&s.local_RAM[3081]==240u) {nxt=0xf03c0au;s.pc=nxt;s.registers[s.active_bank][23]=0xf03c10u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c0au:
if(s.local_RAM[3082]==152u&&s.local_RAM[3083]==24u&&s.local_RAM[3084]==60u&&s.local_RAM[3085]==84u&&s.local_RAM[3086]==0u&&s.local_RAM[3087]==240u) {nxt=0xf03c10u;s.pc=nxt;s.registers[s.active_bank][24]=0xf03c54u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c10u:
if(s.local_RAM[3088]==164u&&s.local_RAM[3089]==106u) {nxt=0xf03c12u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][3])?(s.registers[s.active_bank][3]&~3u):s.registers[s.active_bank][3],&v));s.registers[s.active_bank][10]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c12u:
if(s.local_RAM[3090]==9u&&s.local_RAM[3091]==3u) {nxt=0xf03c14u;s.pc=nxt;s.registers[s.active_bank][3]=add(&s,s.registers[s.active_bank][3],8u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c14u:
if(s.local_RAM[3092]==164u&&s.local_RAM[3093]==107u) {nxt=0xf03c16u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][3])?(s.registers[s.active_bank][3]&~3u):s.registers[s.active_bank][3],&v));s.registers[s.active_bank][11]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c16u:
if(s.local_RAM[3094]==8u&&s.local_RAM[3095]==131u) {nxt=0xf03c18u;s.pc=nxt;s.registers[s.active_bank][3]=add(&s,s.registers[s.active_bank][3],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c18u:
if(s.local_RAM[3096]==164u&&s.local_RAM[3097]==108u) {nxt=0xf03c1au;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][3])?(s.registers[s.active_bank][3]&~3u):s.registers[s.active_bank][3],&v));s.registers[s.active_bank][12]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c1au:
if(s.local_RAM[3098]==8u&&s.local_RAM[3099]==131u) {nxt=0xf03c1cu;s.pc=nxt;s.registers[s.active_bank][3]=add(&s,s.registers[s.active_bank][3],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c1cu:
if(s.local_RAM[3100]==124u&&s.local_RAM[3101]==236u) {nxt=0xf03c1eu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][12],0x7u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c1eu:
if(s.local_RAM[3102]==213u&&s.local_RAM[3103]==24u) {nxt=0xf03c20u;s.pc=nxt;if(condition(&s,24)){pending=1;target=0xf03c30u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c20u:
if(s.local_RAM[3104]==137u&&s.local_RAM[3105]==129u) {nxt=0xf03c22u;s.pc=nxt;s.registers[s.active_bank][1]=s.registers[s.active_bank][12];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c30u:
if(s.local_RAM[3120]==124u&&s.local_RAM[3121]==108u) {nxt=0xf03c32u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][12],0x3u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c32u:
if(s.local_RAM[3122]==212u&&s.local_RAM[3123]==97u) {nxt=0xf03c34u;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf03c3au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c34u:
if(s.local_RAM[3124]==137u&&s.local_RAM[3125]==76u) {nxt=0xf03c36u;s.pc=nxt;s.registers[s.active_bank][12]=s.registers[s.active_bank][10];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c3au:
if(s.local_RAM[3130]==137u&&s.local_RAM[3131]==79u) {nxt=0xf03c3cu;s.pc=nxt;s.registers[s.active_bank][15]=s.registers[s.active_bank][10];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c3cu:
if(s.local_RAM[3132]==102u&&s.local_RAM[3133]==10u) {nxt=0xf03c3eu;s.pc=nxt;s.c=s.registers[s.active_bank][10]&1u;s.registers[s.active_bank][10]=s.registers[s.active_bank][10]>>16;zn(&s,s.registers[s.active_bank][10]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c3eu:
if(s.local_RAM[3134]==38u&&s.local_RAM[3135]==170u) {nxt=0xf03c40u;s.pc=nxt;s.registers[s.active_bank][10]&=s.registers[s.active_bank][21];
   zn(&s,s.registers[s.active_bank][10]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c40u:
if(s.local_RAM[3136]==1u&&s.local_RAM[3137]==75u) {nxt=0xf03c42u;s.pc=nxt;s.registers[s.active_bank][11]=add(&s,s.registers[s.active_bank][11],s.registers[s.active_bank][10]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c42u:
if(s.local_RAM[3138]==157u&&s.local_RAM[3139]==108u) {nxt=0xf03c44u;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][11],&v));s.registers[s.active_bank][12]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c44u:
if(s.local_RAM[3140]==8u&&s.local_RAM[3141]==43u) {nxt=0xf03c46u;s.pc=nxt;s.registers[s.active_bank][11]=add(&s,s.registers[s.active_bank][11],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c46u:
if(s.local_RAM[3142]==157u&&s.local_RAM[3143]==109u) {nxt=0xf03c48u;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][11],&v));s.registers[s.active_bank][13]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c48u:
if(s.local_RAM[3144]==101u&&s.local_RAM[3145]==15u) {nxt=0xf03c4au;s.pc=nxt;s.c=s.registers[s.active_bank][15]&1u;s.registers[s.active_bank][15]=s.registers[s.active_bank][15]>>8;zn(&s,s.registers[s.active_bank][15]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c4au:
if(s.local_RAM[3146]==17u&&s.local_RAM[3147]==141u) {nxt=0xf03c4cu;s.pc=nxt;s.registers[s.active_bank][13]=sub(&s,s.registers[s.active_bank][13],s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c4cu:
if(s.local_RAM[3148]==38u&&s.local_RAM[3149]==175u) {nxt=0xf03c4eu;s.pc=nxt;s.registers[s.active_bank][15]&=s.registers[s.active_bank][21];
   zn(&s,s.registers[s.active_bank][15]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c4eu:
if(s.local_RAM[3150]==99u&&s.local_RAM[3151]==12u) {nxt=0xf03c50u;s.pc=nxt;s.c=s.registers[s.active_bank][12]>>31;s.registers[s.active_bank][12]=s.registers[s.active_bank][12]<<8;zn(&s,s.registers[s.active_bank][12]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c50u:
if(s.local_RAM[3152]==69u&&s.local_RAM[3153]==237u) {nxt=0xf03c52u;s.pc=nxt;s.registers[s.active_bank][13]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.active_bank][13])*(int32_t)sx16(s.registers[s.active_bank][15]));
   zn(&s,s.registers[s.active_bank][13]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c52u:
if(s.local_RAM[3154]==1u&&s.local_RAM[3155]==172u) {nxt=0xf03c54u;s.pc=nxt;s.registers[s.active_bank][12]=add(&s,s.registers[s.active_bank][12],s.registers[s.active_bank][13]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c54u:
if(s.local_RAM[3156]==184u&&s.local_RAM[3157]==140u) {nxt=0xf03c56u;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][4],s.registers[s.active_bank][12]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c56u:
if(s.local_RAM[3158]==8u&&s.local_RAM[3159]==68u) {nxt=0xf03c58u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c58u:
if(s.local_RAM[3160]==24u&&s.local_RAM[3161]==54u) {nxt=0xf03c5au;s.pc=nxt;s.registers[s.active_bank][22]=sub(&s,s.registers[s.active_bank][22],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c5au:
if(s.local_RAM[3162]==210u&&s.local_RAM[3163]==225u) {nxt=0xf03c5cu;s.pc=nxt;if(condition(&s,1)){pending=1;target=s.registers[s.active_bank][23];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c5cu:
if(s.local_RAM[3164]==228u&&s.local_RAM[3165]==0u) {nxt=0xf03c5eu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c5eu:
if(s.local_RAM[3166]==152u&&s.local_RAM[3167]==0u&&s.local_RAM[3168]==63u&&s.local_RAM[3169]==108u&&s.local_RAM[3170]==0u&&s.local_RAM[3171]==240u) {nxt=0xf03c64u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f6cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c64u:
if(s.local_RAM[3172]==174u&&s.local_RAM[3173]==246u) {nxt=0xf03c66u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+92u,&v));s.registers[s.active_bank][22]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c66u:
if(s.local_RAM[3174]==152u&&s.local_RAM[3175]==26u&&s.local_RAM[3176]==0u&&s.local_RAM[3177]==63u&&s.local_RAM[3178]==0u&&s.local_RAM[3179]==0u) {nxt=0xf03c6cu;s.pc=nxt;s.registers[s.active_bank][26]=0x3fu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c6cu:
if(s.local_RAM[3180]==152u&&s.local_RAM[3181]==2u&&s.local_RAM[3182]==1u&&s.local_RAM[3183]==0u&&s.local_RAM[3184]==0u&&s.local_RAM[3185]==0u) {nxt=0xf03c72u;s.pc=nxt;s.registers[s.active_bank][2]=0x100u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c72u:
if(s.local_RAM[3186]==138u&&s.local_RAM[3187]==215u) {nxt=0xf03c74u;s.pc=nxt;s.registers[s.active_bank][23]=s.registers[s.active_bank][22];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c74u:
if(s.local_RAM[3188]==138u&&s.local_RAM[3189]==217u) {nxt=0xf03c76u;s.pc=nxt;s.registers[s.active_bank][25]=s.registers[s.active_bank][22];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c76u:
if(s.local_RAM[3190]==0u&&s.local_RAM[3191]==89u) {nxt=0xf03c78u;s.pc=nxt;s.registers[s.active_bank][25]=add(&s,s.registers[s.active_bank][25],s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c78u:
if(s.local_RAM[3192]==0u&&s.local_RAM[3193]==87u) {nxt=0xf03c7au;s.pc=nxt;s.registers[s.active_bank][23]=add(&s,s.registers[s.active_bank][23],s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c7au:
if(s.local_RAM[3194]==0u&&s.local_RAM[3195]==89u) {nxt=0xf03c7cu;s.pc=nxt;s.registers[s.active_bank][25]=add(&s,s.registers[s.active_bank][25],s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c7cu:
if(s.local_RAM[3196]==164u&&s.local_RAM[3197]==24u) {nxt=0xf03c7eu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][24]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c7eu:
if(s.local_RAM[3198]==162u&&s.local_RAM[3199]==225u) {nxt=0xf03c80u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][23],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c80u:
if(s.local_RAM[3200]==152u&&s.local_RAM[3201]==2u&&s.local_RAM[3202]==61u&&s.local_RAM[3203]==170u&&s.local_RAM[3204]==0u&&s.local_RAM[3205]==240u) {nxt=0xf03c86u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03daau;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c86u:
if(s.local_RAM[3206]==8u&&s.local_RAM[3207]==87u) {nxt=0xf03c88u;s.pc=nxt;s.registers[s.active_bank][23]=add(&s,s.registers[s.active_bank][23],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c88u:
if(s.local_RAM[3208]==124u&&s.local_RAM[3209]==1u) {nxt=0xf03c8au;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][1],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c8au:
if(s.local_RAM[3210]==208u&&s.local_RAM[3211]==66u) {nxt=0xf03c8cu;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][2];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c8cu:
if(s.local_RAM[3212]==98u&&s.local_RAM[3213]==1u) {nxt=0xf03c8eu;s.pc=nxt;s.c=s.registers[s.active_bank][1]>>31;s.registers[s.active_bank][1]=s.registers[s.active_bank][1]<<16;zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c8eu:
if(s.local_RAM[3214]==162u&&s.local_RAM[3215]==226u) {nxt=0xf03c90u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][23],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c90u:
if(s.local_RAM[3216]==40u&&s.local_RAM[3217]==65u) {nxt=0xf03c92u;s.pc=nxt;s.registers[s.active_bank][1]|=s.registers[s.active_bank][2];
   zn(&s,s.registers[s.active_bank][1]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c92u:
if(s.local_RAM[3218]==152u&&s.local_RAM[3219]==0u&&s.local_RAM[3220]==0u&&s.local_RAM[3221]==63u&&s.local_RAM[3222]==0u&&s.local_RAM[3223]==0u) {nxt=0xf03c98u;s.pc=nxt;s.registers[s.active_bank][0]=0x3fu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c98u:
if(s.local_RAM[3224]==19u&&s.local_RAM[3225]==64u) {nxt=0xf03c9au;s.pc=nxt;s.registers[s.active_bank][0]=sub(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][26]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c9au:
if(s.local_RAM[3226]==99u&&s.local_RAM[3227]==160u) {nxt=0xf03c9cu;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<3;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c9cu:
if(s.local_RAM[3228]==136u&&s.local_RAM[3229]==2u) {nxt=0xf03c9eu;s.pc=nxt;s.registers[s.active_bank][2]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03c9eu:
if(s.local_RAM[3230]==99u&&s.local_RAM[3231]==192u) {nxt=0xf03ca0u;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<2;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ca0u:
if(s.local_RAM[3232]==0u&&s.local_RAM[3233]==64u) {nxt=0xf03ca2u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ca2u:
if(s.local_RAM[3234]==152u&&s.local_RAM[3235]==2u&&s.local_RAM[3236]==63u&&s.local_RAM[3237]==112u&&s.local_RAM[3238]==0u&&s.local_RAM[3239]==240u) {nxt=0xf03ca8u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03f70u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ca8u:
if(s.local_RAM[3240]==164u&&s.local_RAM[3241]==91u) {nxt=0xf03caau;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][2])?(s.registers[s.active_bank][2]&~3u):s.registers[s.active_bank][2],&v));s.registers[s.active_bank][27]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03caau:
if(s.local_RAM[3242]==3u&&s.local_RAM[3243]==96u) {nxt=0xf03cacu;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cacu:
if(s.local_RAM[3244]==143u&&s.local_RAM[3245]==219u) {nxt=0xf03caeu;s.pc=nxt;s.registers[s.active_bank][27]=30u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03caeu:
if(s.local_RAM[3246]==3u&&s.local_RAM[3247]==96u) {nxt=0xf03cb0u;s.pc=nxt;s.registers[s.active_bank][0]=add(&s,s.registers[s.active_bank][0],s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cb0u:
if(s.local_RAM[3248]==25u&&s.local_RAM[3249]==130u) {nxt=0xf03cb2u;s.pc=nxt;s.registers[s.active_bank][2]=sub(&s,s.registers[s.active_bank][2],12u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cb2u:
if(s.local_RAM[3250]==164u&&s.local_RAM[3251]==72u) {nxt=0xf03cb4u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][2])?(s.registers[s.active_bank][2]&~3u):s.registers[s.active_bank][2],&v));s.registers[s.active_bank][8]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cb4u:
if(s.local_RAM[3252]==136u&&s.local_RAM[3253]==60u) {nxt=0xf03cb6u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][1];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cb6u:
if(s.local_RAM[3254]==139u&&s.local_RAM[3255]==53u) {nxt=0xf03cb8u;s.pc=nxt;s.registers[s.active_bank][21]=s.registers[s.active_bank][25];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cb8u:
if(s.local_RAM[3256]==136u&&s.local_RAM[3257]==4u) {nxt=0xf03cbau;s.pc=nxt;s.registers[s.active_bank][4]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cbau:
if(s.local_RAM[3258]==137u&&s.local_RAM[3259]==16u) {nxt=0xf03cbcu;s.pc=nxt;s.registers[s.active_bank][16]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cbcu:
if(s.local_RAM[3260]==139u&&s.local_RAM[3261]==147u) {nxt=0xf03cbeu;s.pc=nxt;s.registers[s.active_bank][19]=s.registers[s.active_bank][28];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cbeu:
if(s.local_RAM[3262]==10u&&s.local_RAM[3263]==16u) {nxt=0xf03cc0u;s.pc=nxt;s.registers[s.active_bank][16]=add(&s,s.registers[s.active_bank][16],16u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cc0u:
if(s.local_RAM[3264]==102u&&s.local_RAM[3265]==28u) {nxt=0xf03cc2u;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>16;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cc2u:
if(s.local_RAM[3266]==100u&&s.local_RAM[3267]==51u) {nxt=0xf03cc4u;s.pc=nxt;s.c=s.registers[s.active_bank][19]&1u;s.registers[s.active_bank][19]=s.registers[s.active_bank][19]>>1;zn(&s,s.registers[s.active_bank][19]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cc4u:
if(s.local_RAM[3268]==10u&&s.local_RAM[3269]==16u) {nxt=0xf03cc6u;s.pc=nxt;s.registers[s.active_bank][16]=add(&s,s.registers[s.active_bank][16],16u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cc6u:
if(s.local_RAM[3270]==141u&&s.local_RAM[3271]==3u) {nxt=0xf03cc8u;s.pc=nxt;s.registers[s.active_bank][3]=8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cc8u:
if(s.local_RAM[3272]==152u&&s.local_RAM[3273]==5u&&s.local_RAM[3274]==127u&&s.local_RAM[3275]==255u&&s.local_RAM[3276]==0u&&s.local_RAM[3277]==0u) {nxt=0xf03cceu;s.pc=nxt;s.registers[s.active_bank][5]=0x7fffu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cceu:
if(s.local_RAM[3278]==152u&&s.local_RAM[3279]==7u&&s.local_RAM[3280]==60u&&s.local_RAM[3281]==232u&&s.local_RAM[3282]==0u&&s.local_RAM[3283]==240u) {nxt=0xf03cd4u;s.pc=nxt;s.registers[s.active_bank][7]=0xf03ce8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cd4u:
if(s.local_RAM[3284]==36u&&s.local_RAM[3285]==179u) {nxt=0xf03cd6u;s.pc=nxt;s.registers[s.active_bank][19]&=s.registers[s.active_bank][5];
   zn(&s,s.registers[s.active_bank][19]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cd6u:
if(s.local_RAM[3286]==136u&&s.local_RAM[3287]==187u) {nxt=0xf03cd8u;s.pc=nxt;s.registers[s.active_bank][27]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cd8u:
if(s.local_RAM[3288]==99u&&s.local_RAM[3289]==251u) {nxt=0xf03cdau;s.pc=nxt;s.c=s.registers[s.active_bank][27]>>31;s.registers[s.active_bank][27]=s.registers[s.active_bank][27]<<1;zn(&s,s.registers[s.active_bank][27]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cdau:
if(s.local_RAM[3290]==152u&&s.local_RAM[3291]==10u&&s.local_RAM[3292]==60u&&s.local_RAM[3293]==248u&&s.local_RAM[3294]==0u&&s.local_RAM[3295]==240u) {nxt=0xf03ce0u;s.pc=nxt;s.registers[s.active_bank][10]=0xf03cf8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ce0u:
if(s.local_RAM[3296]==152u&&s.local_RAM[3297]==17u&&s.local_RAM[3298]==128u&&s.local_RAM[3299]==0u&&s.local_RAM[3300]==0u&&s.local_RAM[3301]==0u) {nxt=0xf03ce6u;s.pc=nxt;s.registers[s.active_bank][17]=0x8000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ce6u:
if(s.local_RAM[3302]==46u&&s.local_RAM[3303]==82u) {nxt=0xf03ce8u;s.pc=nxt;s.registers[s.active_bank][18]^=s.registers[s.active_bank][18];zn(&s,s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ce8u:
if(s.local_RAM[3304]==52u&&s.local_RAM[3305]==28u) {nxt=0xf03ceau;s.pc=nxt;s.z=((~s.registers[s.active_bank][28])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ceau:
if(s.local_RAM[3306]==209u&&s.local_RAM[3307]==66u) {nxt=0xf03cecu;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][10];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cecu:
if(s.local_RAM[3308]==228u&&s.local_RAM[3309]==0u) {nxt=0xf03ceeu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ceeu:
if(s.local_RAM[3310]==161u&&s.local_RAM[3311]==1u) {nxt=0xf03cf0u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][8],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cf0u:
if(s.local_RAM[3312]==18u&&s.local_RAM[3313]==33u) {nxt=0xf03cf2u;s.pc=nxt;s.registers[s.active_bank][1]=sub(&s,s.registers[s.active_bank][1],s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cf2u:
if(s.local_RAM[3314]==68u&&s.local_RAM[3315]==37u) {nxt=0xf03cf4u;s.pc=nxt;s.registers[s.active_bank][5]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.active_bank][5])*(int32_t)sx16(s.registers[s.active_bank][1]));
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cf4u:
if(s.local_RAM[3316]==110u&&s.local_RAM[3317]==5u) {nxt=0xf03cf6u;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=sar(s.registers[s.active_bank][5],16);zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cf6u:
if(s.local_RAM[3318]==0u&&s.local_RAM[3319]==178u) {nxt=0xf03cf8u;s.pc=nxt;s.registers[s.active_bank][18]=add(&s,s.registers[s.active_bank][18],s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cf8u:
if(s.local_RAM[3320]==53u&&s.local_RAM[3321]==28u) {nxt=0xf03cfau;s.pc=nxt;s.z=((~s.registers[s.active_bank][28])>>8)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cfau:
if(s.local_RAM[3322]==212u&&s.local_RAM[3323]==66u) {nxt=0xf03cfcu;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03d00u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03cfcu:
if(s.local_RAM[3324]==100u&&s.local_RAM[3325]==60u) {nxt=0xf03cfeu;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>1;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d00u:
if(s.local_RAM[3328]==8u&&s.local_RAM[3329]==80u) {nxt=0xf03d02u;s.pc=nxt;s.registers[s.active_bank][16]=add(&s,s.registers[s.active_bank][16],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d02u:
if(s.local_RAM[3330]==24u&&s.local_RAM[3331]==35u) {nxt=0xf03d04u;s.pc=nxt;s.registers[s.active_bank][3]=sub(&s,s.registers[s.active_bank][3],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d04u:
if(s.local_RAM[3332]==208u&&s.local_RAM[3333]==225u) {nxt=0xf03d06u;s.pc=nxt;if(condition(&s,1)){pending=1;target=s.registers[s.active_bank][7];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d06u:
if(s.local_RAM[3334]==8u&&s.local_RAM[3335]==72u) {nxt=0xf03d08u;s.pc=nxt;s.registers[s.active_bank][8]=add(&s,s.registers[s.active_bank][8],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d08u:
if(s.local_RAM[3336]==67u&&s.local_RAM[3337]==115u) {nxt=0xf03d0au;s.pc=nxt;s.registers[s.active_bank][19]=(s.registers[s.active_bank][19]&0xffffu)*(s.registers[s.active_bank][27]&0xffffu);
   zn(&s,s.registers[s.active_bank][19]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d0au:
if(s.local_RAM[3338]==102u&&s.local_RAM[3339]==19u) {nxt=0xf03d0cu;s.pc=nxt;s.c=s.registers[s.active_bank][19]&1u;s.registers[s.active_bank][19]=s.registers[s.active_bank][19]>>16;zn(&s,s.registers[s.active_bank][19]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d0cu:
if(s.local_RAM[3340]==70u&&s.local_RAM[3341]==114u) {nxt=0xf03d0eu;s.pc=nxt;s.registers[s.active_bank][18]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[s.active_bank][18])*(int32_t)sx16(s.registers[s.active_bank][19]));
   zn(&s,s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d0eu:
if(s.local_RAM[3342]==109u&&s.local_RAM[3343]==242u) {nxt=0xf03d10u;s.pc=nxt;s.c=s.registers[s.active_bank][18]&1u;s.registers[s.active_bank][18]=sar(s.registers[s.active_bank][18],15);zn(&s,s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d10u:
if(s.local_RAM[3344]==124u&&s.local_RAM[3345]==18u) {nxt=0xf03d12u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][18],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d12u:
if(s.local_RAM[3346]==212u&&s.local_RAM[3347]==52u) {nxt=0xf03d14u;s.pc=nxt;if(condition(&s,20)){pending=1;target=0xf03d16u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d14u:
if(s.local_RAM[3348]==2u&&s.local_RAM[3349]==50u) {nxt=0xf03d16u;s.pc=nxt;s.registers[s.active_bank][18]=add(&s,s.registers[s.active_bank][18],s.registers[s.active_bank][17]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d16u:
if(s.local_RAM[3350]==42u&&s.local_RAM[3351]==82u) {nxt=0xf03d18u;s.pc=nxt;s.registers[s.active_bank][18]|=s.registers[s.active_bank][18];
   zn(&s,s.registers[s.active_bank][18]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d18u:
if(s.local_RAM[3352]==198u&&s.local_RAM[3353]==210u) {nxt=0xf03d1au;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+88u,s.registers[s.active_bank][18]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d1au:
if(s.local_RAM[3354]==138u&&s.local_RAM[3355]==69u) {nxt=0xf03d1cu;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][18];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d1cu:
if(s.local_RAM[3356]==174u&&s.local_RAM[3357]==230u) {nxt=0xf03d1eu;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+92u,&v));s.registers[s.active_bank][6]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d1eu:
if(s.local_RAM[3358]==8u&&s.local_RAM[3359]==100u) {nxt=0xf03d20u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],3u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d20u:
if(s.local_RAM[3360]==156u&&s.local_RAM[3361]==137u) {nxt=0xf03d22u;s.pc=nxt;CHECK(rd8(bus,&s,s.registers[s.active_bank][4],&v));s.registers[s.active_bank][9]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d22u:
if(s.local_RAM[3362]==8u&&s.local_RAM[3363]==36u) {nxt=0xf03d24u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d24u:
if(s.local_RAM[3364]==160u&&s.local_RAM[3365]==128u) {nxt=0xf03d26u;s.pc=nxt;CHECK(loadw(bus,&s,s.registers[s.active_bank][4],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d26u:
if(s.local_RAM[3366]==8u&&s.local_RAM[3367]==68u) {nxt=0xf03d28u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d28u:
if(s.local_RAM[3368]==99u&&s.local_RAM[3369]==192u) {nxt=0xf03d2au;s.pc=nxt;s.c=s.registers[s.active_bank][0]>>31;s.registers[s.active_bank][0]=s.registers[s.active_bank][0]<<2;zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d2au:
if(s.local_RAM[3370]==164u&&s.local_RAM[3371]==136u) {nxt=0xf03d2cu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][4])?(s.registers[s.active_bank][4]&~3u):s.registers[s.active_bank][4],&v));s.registers[s.active_bank][8]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d2cu:
if(s.local_RAM[3372]==0u&&s.local_RAM[3373]==6u) {nxt=0xf03d2eu;s.pc=nxt;s.registers[s.active_bank][6]=add(&s,s.registers[s.active_bank][6],s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d2eu:
if(s.local_RAM[3374]==137u&&s.local_RAM[3375]==10u) {nxt=0xf03d30u;s.pc=nxt;s.registers[s.active_bank][10]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d30u:
if(s.local_RAM[3376]==44u&&s.local_RAM[3377]==231u) {nxt=0xf03d32u;s.pc=nxt;s.registers[s.active_bank][7]^=s.registers[s.active_bank][7];zn(&s,s.registers[s.active_bank][7]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d32u:
if(s.local_RAM[3378]==100u&&s.local_RAM[3379]==42u) {nxt=0xf03d34u;s.pc=nxt;s.c=s.registers[s.active_bank][10]&1u;s.registers[s.active_bank][10]=s.registers[s.active_bank][10]>>1;zn(&s,s.registers[s.active_bank][10]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d34u:
if(s.local_RAM[3380]==52u&&s.local_RAM[3381]==233u) {nxt=0xf03d36u;s.pc=nxt;s.z=((~s.registers[s.active_bank][9])>>7)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d36u:
if(s.local_RAM[3382]==212u&&s.local_RAM[3383]==66u) {nxt=0xf03d38u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03d3cu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d38u:
if(s.local_RAM[3384]==60u&&s.local_RAM[3385]==233u) {nxt=0xf03d3au;s.pc=nxt;s.registers[s.active_bank][9]&=~(1u<<7);
   zn(&s,s.registers[s.active_bank][9]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d3au:
if(s.local_RAM[3386]==140u&&s.local_RAM[3387]==39u) {nxt=0xf03d3cu;s.pc=nxt;s.registers[s.active_bank][7]=1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d3cu:
if(s.local_RAM[3388]==152u&&s.local_RAM[3389]==0u&&s.local_RAM[3390]==61u&&s.local_RAM[3391]==86u&&s.local_RAM[3392]==0u&&s.local_RAM[3393]==240u) {nxt=0xf03d42u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03d56u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d42u:
if(s.local_RAM[3394]==124u&&s.local_RAM[3395]==73u) {nxt=0xf03d44u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][9],0x2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d44u:
if(s.local_RAM[3396]==208u&&s.local_RAM[3397]==2u) {nxt=0xf03d46u;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d46u:
if(s.local_RAM[3398]==228u&&s.local_RAM[3399]==0u) {nxt=0xf03d48u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d56u:
if(s.local_RAM[3414]==136u&&s.local_RAM[3415]==190u) {nxt=0xf03d58u;s.pc=nxt;s.registers[s.active_bank][30]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d58u:
if(s.local_RAM[3416]==140u&&s.local_RAM[3417]==27u) {nxt=0xf03d5au;s.pc=nxt;s.registers[s.active_bank][27]=0u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d5au:
if(s.local_RAM[3418]==139u&&s.local_RAM[3419]==124u) {nxt=0xf03d5cu;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][27];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d5cu:
if(s.local_RAM[3420]==88u&&s.local_RAM[3421]==8u) {nxt=0xf03d5eu;s.pc=nxt;s.c=s.registers[s.active_bank][8]>>31;if(s.registers[s.active_bank][8]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][8]=0u-s.registers[s.active_bank][8];s.n=0;s.z=s.registers[s.active_bank][8]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d5eu:
if(s.local_RAM[3422]==7u&&s.local_RAM[3423]==155u) {nxt=0xf03d60u;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d60u:
if(s.local_RAM[3424]==88u&&s.local_RAM[3425]==5u) {nxt=0xf03d62u;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;if(s.registers[s.active_bank][5]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[s.active_bank][5]=0u-s.registers[s.active_bank][5];s.n=0;s.z=s.registers[s.active_bank][5]==0;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d62u:
if(s.local_RAM[3426]==7u&&s.local_RAM[3427]==155u) {nxt=0xf03d64u;s.pc=nxt;{uint64_t t=(uint64_t)s.registers[s.active_bank][27]+s.registers[s.active_bank][28]+s.c;s.registers[s.active_bank][27]=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,s.registers[s.active_bank][27]);}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d64u:
if(s.local_RAM[3428]==136u&&s.local_RAM[3429]==188u) {nxt=0xf03d66u;s.pc=nxt;s.registers[s.active_bank][28]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d66u:
if(s.local_RAM[3430]==65u&&s.local_RAM[3431]==28u) {nxt=0xf03d68u;s.pc=nxt;s.registers[s.active_bank][28]=(s.registers[s.active_bank][28]&0xffffu)*(s.registers[s.active_bank][8]&0xffffu);
   zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d68u:
if(s.local_RAM[3432]==137u&&s.local_RAM[3433]==29u) {nxt=0xf03d6au;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][8];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d6au:
if(s.local_RAM[3434]==102u&&s.local_RAM[3435]==28u) {nxt=0xf03d6cu;s.pc=nxt;s.c=s.registers[s.active_bank][28]&1u;s.registers[s.active_bank][28]=s.registers[s.active_bank][28]>>16;zn(&s,s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d6cu:
if(s.local_RAM[3436]==102u&&s.local_RAM[3437]==29u) {nxt=0xf03d6eu;s.pc=nxt;s.c=s.registers[s.active_bank][29]&1u;s.registers[s.active_bank][29]=s.registers[s.active_bank][29]>>16;zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d6eu:
if(s.local_RAM[3438]==64u&&s.local_RAM[3439]==189u) {nxt=0xf03d70u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][5]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d70u:
if(s.local_RAM[3440]==102u&&s.local_RAM[3441]==5u) {nxt=0xf03d72u;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]>>16;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d72u:
if(s.local_RAM[3442]==3u&&s.local_RAM[3443]==188u) {nxt=0xf03d74u;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d74u:
if(s.local_RAM[3444]==136u&&s.local_RAM[3445]==189u) {nxt=0xf03d76u;s.pc=nxt;s.registers[s.active_bank][29]=s.registers[s.active_bank][5];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d76u:
if(s.local_RAM[3446]==65u&&s.local_RAM[3447]==29u) {nxt=0xf03d78u;s.pc=nxt;s.registers[s.active_bank][29]=(s.registers[s.active_bank][29]&0xffffu)*(s.registers[s.active_bank][8]&0xffffu);
   zn(&s,s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d78u:
if(s.local_RAM[3448]==102u&&s.local_RAM[3449]==8u) {nxt=0xf03d7au;s.pc=nxt;s.c=s.registers[s.active_bank][8]&1u;s.registers[s.active_bank][8]=s.registers[s.active_bank][8]>>16;zn(&s,s.registers[s.active_bank][8]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d7au:
if(s.local_RAM[3450]==3u&&s.local_RAM[3451]==188u) {nxt=0xf03d7cu;s.pc=nxt;s.registers[s.active_bank][28]=add(&s,s.registers[s.active_bank][28],s.registers[s.active_bank][29]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d7cu:
if(s.local_RAM[3452]==64u&&s.local_RAM[3453]==168u) {nxt=0xf03d7eu;s.pc=nxt;s.registers[s.active_bank][8]=(s.registers[s.active_bank][8]&0xffffu)*(s.registers[s.active_bank][5]&0xffffu);
   zn(&s,s.registers[s.active_bank][8]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d7eu:
if(s.local_RAM[3454]==98u&&s.local_RAM[3455]==8u) {nxt=0xf03d80u;s.pc=nxt;s.c=s.registers[s.active_bank][8]>>31;s.registers[s.active_bank][8]=s.registers[s.active_bank][8]<<16;zn(&s,s.registers[s.active_bank][8]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d80u:
if(s.local_RAM[3456]==3u&&s.local_RAM[3457]==136u) {nxt=0xf03d82u;s.pc=nxt;s.registers[s.active_bank][8]=add(&s,s.registers[s.active_bank][8],s.registers[s.active_bank][28]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d82u:
if(s.local_RAM[3458]==52u&&s.local_RAM[3459]==27u) {nxt=0xf03d84u;s.pc=nxt;s.z=((~s.registers[s.active_bank][27])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d84u:
if(s.local_RAM[3460]==212u&&s.local_RAM[3461]==66u) {nxt=0xf03d86u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03d8au;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d86u:
if(s.local_RAM[3462]==139u&&s.local_RAM[3463]==197u) {nxt=0xf03d88u;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][30];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d8au:
if(s.local_RAM[3466]==124u&&s.local_RAM[3467]==21u) {nxt=0xf03d8cu;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][21],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d8cu:
if(s.local_RAM[3468]==212u&&s.local_RAM[3469]==97u) {nxt=0xf03d8eu;s.pc=nxt;if(condition(&s,1)){pending=1;target=0xf03d94u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d8eu:
if(s.local_RAM[3470]==228u&&s.local_RAM[3471]==0u) {nxt=0xf03d90u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d94u:
if(s.local_RAM[3476]==228u&&s.local_RAM[3477]==0u) {nxt=0xf03d96u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d96u:
if(s.local_RAM[3478]==17u&&s.local_RAM[3479]==72u) {nxt=0xf03d98u;s.pc=nxt;s.registers[s.active_bank][8]=sub(&s,s.registers[s.active_bank][8],s.registers[s.active_bank][10]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d98u:
if(s.local_RAM[3480]==124u&&s.local_RAM[3481]==21u) {nxt=0xf03d9au;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][21],0x0u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d9au:
if(s.local_RAM[3482]==212u&&s.local_RAM[3483]==98u) {nxt=0xf03d9cu;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03da2u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d9cu:
if(s.local_RAM[3484]==228u&&s.local_RAM[3485]==0u) {nxt=0xf03d9eu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03d9eu:
if(s.local_RAM[3486]==166u&&s.local_RAM[3487]==160u) {nxt=0xf03da0u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][21])?(s.registers[s.active_bank][21]&~3u):s.registers[s.active_bank][21],&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03da0u:
if(s.local_RAM[3488]==0u&&s.local_RAM[3489]==8u) {nxt=0xf03da2u;s.pc=nxt;s.registers[s.active_bank][8]=add(&s,s.registers[s.active_bank][8],s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03da2u:
if(s.local_RAM[3490]==188u&&s.local_RAM[3491]==200u) {nxt=0xf03da4u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][6])?(s.registers[s.active_bank][6]&~3u):s.registers[s.active_bank][6],s.registers[s.active_bank][8]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03da4u:
if(s.local_RAM[3492]==174u&&s.local_RAM[3493]==192u) {nxt=0xf03da6u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+88u,&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03da6u:
if(s.local_RAM[3494]==40u&&s.local_RAM[3495]==0u) {nxt=0xf03da8u;s.pc=nxt;s.registers[s.active_bank][0]|=s.registers[s.active_bank][0];
   zn(&s,s.registers[s.active_bank][0]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03da8u:
if(s.local_RAM[3496]==187u&&s.local_RAM[3497]==0u) {nxt=0xf03daau;s.pc=nxt;CHECK(wr16(bus,&s,s.registers[s.active_bank][24],s.registers[s.active_bank][0]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03daau:
if(s.local_RAM[3498]==8u&&s.local_RAM[3499]==88u) {nxt=0xf03dacu;s.pc=nxt;s.registers[s.active_bank][24]=add(&s,s.registers[s.active_bank][24],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dacu:
if(s.local_RAM[3500]==8u&&s.local_RAM[3501]==87u) {nxt=0xf03daeu;s.pc=nxt;s.registers[s.active_bank][23]=add(&s,s.registers[s.active_bank][23],2u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03daeu:
if(s.local_RAM[3502]==8u&&s.local_RAM[3503]==153u) {nxt=0xf03db0u;s.pc=nxt;s.registers[s.active_bank][25]=add(&s,s.registers[s.active_bank][25],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03db0u:
if(s.local_RAM[3504]==8u&&s.local_RAM[3505]==150u) {nxt=0xf03db2u;s.pc=nxt;s.registers[s.active_bank][22]=add(&s,s.registers[s.active_bank][22],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03db2u:
if(s.local_RAM[3506]==152u&&s.local_RAM[3507]==0u&&s.local_RAM[3508]==60u&&s.local_RAM[3509]==126u&&s.local_RAM[3510]==0u&&s.local_RAM[3511]==240u) {nxt=0xf03db8u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03c7eu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03db8u:
if(s.local_RAM[3512]==24u&&s.local_RAM[3513]==58u) {nxt=0xf03dbau;s.pc=nxt;s.registers[s.active_bank][26]=sub(&s,s.registers[s.active_bank][26],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dbau:
if(s.local_RAM[3514]==208u&&s.local_RAM[3515]==20u) {nxt=0xf03dbcu;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dbcu:
if(s.local_RAM[3516]==228u&&s.local_RAM[3517]==0u) {nxt=0xf03dbeu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dbeu:
if(s.local_RAM[3518]==175u&&s.local_RAM[3519]==32u) {nxt=0xf03dc0u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+100u,&v));s.registers[s.active_bank][0]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dc0u:
if(s.local_RAM[3520]==175u&&s.local_RAM[3521]==2u) {nxt=0xf03dc2u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+96u,&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dc2u:
if(s.local_RAM[3522]==24u&&s.local_RAM[3523]==34u) {nxt=0xf03dc4u;s.pc=nxt;s.registers[s.active_bank][2]=sub(&s,s.registers[s.active_bank][2],1u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dc4u:
if(s.local_RAM[3524]==152u&&s.local_RAM[3525]==3u&&s.local_RAM[3526]==58u&&s.local_RAM[3527]==158u&&s.local_RAM[3528]==0u&&s.local_RAM[3529]==240u) {nxt=0xf03dcau;s.pc=nxt;s.registers[s.active_bank][3]=0xf03a9eu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dcau:
if(s.local_RAM[3530]==40u&&s.local_RAM[3531]==66u) {nxt=0xf03dccu;s.pc=nxt;s.registers[s.active_bank][2]|=s.registers[s.active_bank][2];
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dccu:
if(s.local_RAM[3532]==199u&&s.local_RAM[3533]==2u) {nxt=0xf03dceu;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+96u,s.registers[s.active_bank][2]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dceu:
if(s.local_RAM[3534]==208u&&s.local_RAM[3535]==116u) {nxt=0xf03dd0u;s.pc=nxt;if(condition(&s,20)){pending=1;target=s.registers[s.active_bank][3];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dd0u:
if(s.local_RAM[3536]==228u&&s.local_RAM[3537]==0u) {nxt=0xf03dd2u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dd2u:
if(s.local_RAM[3538]==152u&&s.local_RAM[3539]==2u&&s.local_RAM[3540]==61u&&s.local_RAM[3541]==236u&&s.local_RAM[3542]==0u&&s.local_RAM[3543]==240u) {nxt=0xf03dd8u;s.pc=nxt;s.registers[s.active_bank][2]=0xf03decu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03dd8u:
if(s.local_RAM[3544]==152u&&s.local_RAM[3545]==1u&&s.local_RAM[3546]==0u&&s.local_RAM[3547]==0u&&s.local_RAM[3548]==0u&&s.local_RAM[3549]==3u) {nxt=0xf03ddeu;s.pc=nxt;s.registers[s.active_bank][1]=0x30000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ddeu:
if(s.local_RAM[3550]==152u&&s.local_RAM[3551]==0u&&s.local_RAM[3552]==62u&&s.local_RAM[3553]==130u&&s.local_RAM[3554]==0u&&s.local_RAM[3555]==240u) {nxt=0xf03de4u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03e82u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03de4u:
if(s.local_RAM[3556]==40u&&s.local_RAM[3557]==66u) {nxt=0xf03de6u;s.pc=nxt;s.registers[s.active_bank][2]|=s.registers[s.active_bank][2];
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03de6u:
if(s.local_RAM[3558]==198u&&s.local_RAM[3559]==162u) {nxt=0xf03de8u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+84u,s.registers[s.active_bank][2]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03de8u:
if(s.local_RAM[3560]==208u&&s.local_RAM[3561]==0u) {nxt=0xf03deau;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03deau:
if(s.local_RAM[3562]==228u&&s.local_RAM[3563]==0u) {nxt=0xf03decu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e00u:
if(s.local_RAM[3584]==152u&&s.local_RAM[3585]==20u&&s.local_RAM[3586]==34u&&s.local_RAM[3587]==56u&&s.local_RAM[3588]==0u&&s.local_RAM[3589]==240u) {nxt=0xf03e06u;s.pc=nxt;s.registers[s.active_bank][20]=0xf02238u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e06u:
if(s.local_RAM[3590]==166u&&s.local_RAM[3591]==149u) {nxt=0xf03e08u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],&v));s.registers[s.active_bank][21]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e08u:
if(s.local_RAM[3592]==52u&&s.local_RAM[3593]==21u) {nxt=0xf03e0au;s.pc=nxt;s.z=((~s.registers[s.active_bank][21])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e0au:
if(s.local_RAM[3594]==215u&&s.local_RAM[3595]==162u) {nxt=0xf03e0cu;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03e06u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e0cu:
if(s.local_RAM[3596]==228u&&s.local_RAM[3597]==0u) {nxt=0xf03e0eu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e0eu:
if(s.local_RAM[3598]==152u&&s.local_RAM[3599]==20u&&s.local_RAM[3600]==34u&&s.local_RAM[3601]==0u&&s.local_RAM[3602]==0u&&s.local_RAM[3603]==240u) {nxt=0xf03e14u;s.pc=nxt;s.registers[s.active_bank][20]=0xf02200u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e14u:
if(s.local_RAM[3604]==152u&&s.local_RAM[3605]==21u&&s.local_RAM[3606]==34u&&s.local_RAM[3607]==36u&&s.local_RAM[3608]==0u&&s.local_RAM[3609]==240u) {nxt=0xf03e1au;s.pc=nxt;s.registers[s.active_bank][21]=0xf02224u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e1au:
if(s.local_RAM[3610]==136u&&s.local_RAM[3611]==57u) {nxt=0xf03e1cu;s.pc=nxt;s.registers[s.active_bank][25]=s.registers[s.active_bank][1];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e1cu:
if(s.local_RAM[3612]==152u&&s.local_RAM[3613]==26u&&s.local_RAM[3614]==255u&&s.local_RAM[3615]==248u&&s.local_RAM[3616]==255u&&s.local_RAM[3617]==255u) {nxt=0xf03e22u;s.pc=nxt;s.registers[s.active_bank][26]=0xfffffff8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e22u:
if(s.local_RAM[3618]==139u&&s.local_RAM[3619]==56u) {nxt=0xf03e24u;s.pc=nxt;s.registers[s.active_bank][24]=s.registers[s.active_bank][25];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e24u:
if(s.local_RAM[3620]==39u&&s.local_RAM[3621]==89u) {nxt=0xf03e26u;s.pc=nxt;s.registers[s.active_bank][25]&=s.registers[s.active_bank][26];
   zn(&s,s.registers[s.active_bank][25]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e26u:
if(s.local_RAM[3622]==19u&&s.local_RAM[3623]==56u) {nxt=0xf03e28u;s.pc=nxt;s.registers[s.active_bank][24]=sub(&s,s.registers[s.active_bank][24],s.registers[s.active_bank][25]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e28u:
if(s.local_RAM[3624]==190u&&s.local_RAM[3625]==153u) {nxt=0xf03e2au;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],s.registers[s.active_bank][25]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e2au:
if(s.local_RAM[3626]==8u&&s.local_RAM[3627]==148u) {nxt=0xf03e2cu;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e2cu:
if(s.local_RAM[3628]==152u&&s.local_RAM[3629]==22u&&s.local_RAM[3630]==64u&&s.local_RAM[3631]==32u&&s.local_RAM[3632]==0u&&s.local_RAM[3633]==0u) {nxt=0xf03e32u;s.pc=nxt;s.registers[s.active_bank][22]=0x4020u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e32u:
if(s.local_RAM[3634]==190u&&s.local_RAM[3635]==150u) {nxt=0xf03e34u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],s.registers[s.active_bank][22]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e34u:
if(s.local_RAM[3636]==9u&&s.local_RAM[3637]==20u) {nxt=0xf03e36u;s.pc=nxt;s.registers[s.active_bank][20]=add(&s,s.registers[s.active_bank][20],8u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e36u:
if(s.local_RAM[3638]==100u&&s.local_RAM[3639]==56u) {nxt=0xf03e38u;s.pc=nxt;s.c=s.registers[s.active_bank][24]&1u;s.registers[s.active_bank][24]=s.registers[s.active_bank][24]>>1;zn(&s,s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e38u:
if(s.local_RAM[3640]==190u&&s.local_RAM[3641]==152u) {nxt=0xf03e3au;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],s.registers[s.active_bank][24]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e3au:
if(s.local_RAM[3642]==136u&&s.local_RAM[3643]==25u) {nxt=0xf03e3cu;s.pc=nxt;s.registers[s.active_bank][25]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e3cu:
if(s.local_RAM[3644]==136u&&s.local_RAM[3645]==23u) {nxt=0xf03e3eu;s.pc=nxt;s.registers[s.active_bank][23]=s.registers[s.active_bank][0];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e3eu:
if(s.local_RAM[3646]==39u&&s.local_RAM[3647]==89u) {nxt=0xf03e40u;s.pc=nxt;s.registers[s.active_bank][25]&=s.registers[s.active_bank][26];
   zn(&s,s.registers[s.active_bank][25]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e40u:
if(s.local_RAM[3648]==19u&&s.local_RAM[3649]==55u) {nxt=0xf03e42u;s.pc=nxt;s.registers[s.active_bank][23]=sub(&s,s.registers[s.active_bank][23],s.registers[s.active_bank][25]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e42u:
if(s.local_RAM[3650]==190u&&s.local_RAM[3651]==185u) {nxt=0xf03e44u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][21])?(s.registers[s.active_bank][21]&~3u):s.registers[s.active_bank][21],s.registers[s.active_bank][25]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e44u:
if(s.local_RAM[3652]==8u&&s.local_RAM[3653]==149u) {nxt=0xf03e46u;s.pc=nxt;s.registers[s.active_bank][21]=add(&s,s.registers[s.active_bank][21],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e46u:
if(s.local_RAM[3654]==190u&&s.local_RAM[3655]==182u) {nxt=0xf03e48u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][21])?(s.registers[s.active_bank][21]&~3u):s.registers[s.active_bank][21],s.registers[s.active_bank][22]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e48u:
if(s.local_RAM[3656]==9u&&s.local_RAM[3657]==21u) {nxt=0xf03e4au;s.pc=nxt;s.registers[s.active_bank][21]=add(&s,s.registers[s.active_bank][21],8u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e4au:
if(s.local_RAM[3658]==100u&&s.local_RAM[3659]==55u) {nxt=0xf03e4cu;s.pc=nxt;s.c=s.registers[s.active_bank][23]&1u;s.registers[s.active_bank][23]=s.registers[s.active_bank][23]>>1;zn(&s,s.registers[s.active_bank][23]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e4cu:
if(s.local_RAM[3660]==190u&&s.local_RAM[3661]==183u) {nxt=0xf03e4eu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][21])?(s.registers[s.active_bank][21]&~3u):s.registers[s.active_bank][21],s.registers[s.active_bank][23]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e4eu:
if(s.local_RAM[3662]==100u&&s.local_RAM[3663]==34u) {nxt=0xf03e50u;s.pc=nxt;s.c=s.registers[s.active_bank][2]&1u;s.registers[s.active_bank][2]=s.registers[s.active_bank][2]>>1;zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e50u:
if(s.local_RAM[3664]==152u&&s.local_RAM[3665]==25u&&s.local_RAM[3666]==34u&&s.local_RAM[3667]==60u&&s.local_RAM[3668]==0u&&s.local_RAM[3669]==240u) {nxt=0xf03e56u;s.pc=nxt;s.registers[s.active_bank][25]=0xf0223cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e56u:
if(s.local_RAM[3670]==58u&&s.local_RAM[3671]==2u) {nxt=0xf03e58u;s.pc=nxt;s.registers[s.active_bank][2]|=(1u<<16);
   zn(&s,s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e58u:
if(s.local_RAM[3672]==191u&&s.local_RAM[3673]==34u) {nxt=0xf03e5au;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][25])?(s.registers[s.active_bank][25]&~3u):s.registers[s.active_bank][25],s.registers[s.active_bank][2]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e5au:
if(s.local_RAM[3674]==152u&&s.local_RAM[3675]==22u&&s.local_RAM[3676]==0u&&s.local_RAM[3677]==1u&&s.local_RAM[3678]==1u&&s.local_RAM[3679]==128u) {nxt=0xf03e60u;s.pc=nxt;s.registers[s.active_bank][22]=0x1800001u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e60u:
if(s.local_RAM[3680]==42u&&s.local_RAM[3681]==248u) {nxt=0xf03e62u;s.pc=nxt;s.registers[s.active_bank][24]|=s.registers[s.active_bank][23];
   zn(&s,s.registers[s.active_bank][24]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e62u:
if(s.local_RAM[3682]==212u&&s.local_RAM[3683]==130u) {nxt=0xf03e64u;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03e6cu;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e64u:
if(s.local_RAM[3684]==228u&&s.local_RAM[3685]==0u) {nxt=0xf03e66u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e6cu:
if(s.local_RAM[3692]==152u&&s.local_RAM[3693]==20u&&s.local_RAM[3694]==34u&&s.local_RAM[3695]==56u&&s.local_RAM[3696]==0u&&s.local_RAM[3697]==240u) {nxt=0xf03e72u;s.pc=nxt;s.registers[s.active_bank][20]=0xf02238u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e72u:
if(s.local_RAM[3698]==190u&&s.local_RAM[3699]==150u) {nxt=0xf03e74u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],s.registers[s.active_bank][22]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e74u:
if(s.local_RAM[3700]==166u&&s.local_RAM[3701]==149u) {nxt=0xf03e76u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][20])?(s.registers[s.active_bank][20]&~3u):s.registers[s.active_bank][20],&v));s.registers[s.active_bank][21]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e76u:
if(s.local_RAM[3702]==52u&&s.local_RAM[3703]==21u) {nxt=0xf03e78u;s.pc=nxt;s.z=((~s.registers[s.active_bank][21])>>0)&1u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e78u:
if(s.local_RAM[3704]==215u&&s.local_RAM[3705]==162u) {nxt=0xf03e7au;s.pc=nxt;if(condition(&s,2)){pending=1;target=0xf03e74u;}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e7au:
if(s.local_RAM[3706]==228u&&s.local_RAM[3707]==0u) {nxt=0xf03e7cu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e7cu:
if(s.local_RAM[3708]==174u&&s.local_RAM[3709]==180u) {nxt=0xf03e7eu;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+84u,&v));s.registers[s.active_bank][20]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e7eu:
if(s.local_RAM[3710]==210u&&s.local_RAM[3711]==128u) {nxt=0xf03e80u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][20];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e80u:
if(s.local_RAM[3712]==228u&&s.local_RAM[3713]==0u) {nxt=0xf03e82u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e82u:
if(s.local_RAM[3714]==144u&&s.local_RAM[3715]==99u) {nxt=0xf03e84u;s.pc=nxt;s.registers[1u-s.active_bank][3]=s.registers[s.active_bank][3];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e84u:
if(s.local_RAM[3716]==145u&&s.local_RAM[3717]==206u) {nxt=0xf03e86u;s.pc=nxt;s.registers[1u-s.active_bank][14]=s.registers[s.active_bank][14];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e86u:
if(s.local_RAM[3718]==136u&&s.local_RAM[3719]==36u) {nxt=0xf03e88u;s.pc=nxt;s.registers[s.active_bank][4]=s.registers[s.active_bank][1];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e88u:
if(s.local_RAM[3720]==136u&&s.local_RAM[3721]==37u) {nxt=0xf03e8au;s.pc=nxt;s.registers[s.active_bank][5]=s.registers[s.active_bank][1];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e8au:
if(s.local_RAM[3722]==98u&&s.local_RAM[3723]==4u) {nxt=0xf03e8cu;s.pc=nxt;s.c=s.registers[s.active_bank][4]>>31;s.registers[s.active_bank][4]=s.registers[s.active_bank][4]<<16;zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e8cu:
if(s.local_RAM[3724]==102u&&s.local_RAM[3725]==5u) {nxt=0xf03e8eu;s.pc=nxt;s.c=s.registers[s.active_bank][5]&1u;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]>>16;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e8eu:
if(s.local_RAM[3726]==102u&&s.local_RAM[3727]==4u) {nxt=0xf03e90u;s.pc=nxt;s.c=s.registers[s.active_bank][4]&1u;s.registers[s.active_bank][4]=s.registers[s.active_bank][4]>>16;zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e90u:
if(s.local_RAM[3728]==152u&&s.local_RAM[3729]==0u&&s.local_RAM[3730]==63u&&s.local_RAM[3731]==92u&&s.local_RAM[3732]==0u&&s.local_RAM[3733]==240u) {nxt=0xf03e96u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f5cu;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e96u:
if(s.local_RAM[3734]==188u&&s.local_RAM[3735]==4u) {nxt=0xf03e98u;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],s.registers[s.active_bank][4]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e98u:
if(s.local_RAM[3736]==152u&&s.local_RAM[3737]==0u&&s.local_RAM[3738]==48u&&s.local_RAM[3739]==0u&&s.local_RAM[3740]==0u&&s.local_RAM[3741]==240u) {nxt=0xf03e9eu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03e9eu:
if(s.local_RAM[3742]==152u&&s.local_RAM[3743]==1u&&s.local_RAM[3744]==62u&&s.local_RAM[3745]==248u&&s.local_RAM[3746]==0u&&s.local_RAM[3747]==240u) {nxt=0xf03ea4u;s.pc=nxt;s.registers[s.active_bank][1]=0xf03ef8u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ea4u:
if(s.local_RAM[3748]==164u&&s.local_RAM[3749]==34u) {nxt=0xf03ea6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ea6u:
if(s.local_RAM[3750]==120u&&s.local_RAM[3751]==69u) {nxt=0xf03ea8u;s.pc=nxt;(void)sub(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][2]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ea8u:
if(s.local_RAM[3752]==208u&&s.local_RAM[3753]==2u) {nxt=0xf03eaau;s.pc=nxt;if(condition(&s,2)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eaau:
if(s.local_RAM[3754]==228u&&s.local_RAM[3755]==0u) {nxt=0xf03eacu;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eacu:
if(s.local_RAM[3756]==188u&&s.local_RAM[3757]==37u) {nxt=0xf03eaeu;s.pc=nxt;CHECK(wr32(bus,&s,local(s.registers[s.active_bank][1])?(s.registers[s.active_bank][1]&~3u):s.registers[s.active_bank][1],s.registers[s.active_bank][5]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eaeu:
if(s.local_RAM[3758]==152u&&s.local_RAM[3759]==0u&&s.local_RAM[3760]==63u&&s.local_RAM[3761]==72u&&s.local_RAM[3762]==0u&&s.local_RAM[3763]==240u) {nxt=0xf03eb4u;s.pc=nxt;s.registers[s.active_bank][0]=0xf03f48u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eb4u:
if(s.local_RAM[3764]==164u&&s.local_RAM[3765]==4u) {nxt=0xf03eb6u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][0])?(s.registers[s.active_bank][0]&~3u):s.registers[s.active_bank][0],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eb6u:
if(s.local_RAM[3766]==99u&&s.local_RAM[3767]==197u) {nxt=0xf03eb8u;s.pc=nxt;s.c=s.registers[s.active_bank][5]>>31;s.registers[s.active_bank][5]=s.registers[s.active_bank][5]<<2;zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eb8u:
if(s.local_RAM[3768]==0u&&s.local_RAM[3769]==133u) {nxt=0xf03ebau;s.pc=nxt;s.registers[s.active_bank][5]=add(&s,s.registers[s.active_bank][5],s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ebau:
if(s.local_RAM[3770]==164u&&s.local_RAM[3771]==164u) {nxt=0xf03ebcu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][5])?(s.registers[s.active_bank][5]&~3u):s.registers[s.active_bank][5],&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ebcu:
if(s.local_RAM[3772]==164u&&s.local_RAM[3773]==129u) {nxt=0xf03ebeu;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][4])?(s.registers[s.active_bank][4]&~3u):s.registers[s.active_bank][4],&v));s.registers[s.active_bank][1]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ebeu:
if(s.local_RAM[3774]==8u&&s.local_RAM[3775]==132u) {nxt=0xf03ec0u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ec0u:
if(s.local_RAM[3776]==164u&&s.local_RAM[3777]==130u) {nxt=0xf03ec2u;s.pc=nxt;CHECK(rd32(bus,&s,local(s.registers[s.active_bank][4])?(s.registers[s.active_bank][4]&~3u):s.registers[s.active_bank][4],&v));s.registers[s.active_bank][2]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ec2u:
if(s.local_RAM[3778]==8u&&s.local_RAM[3779]==132u) {nxt=0xf03ec4u;s.pc=nxt;s.registers[s.active_bank][4]=add(&s,s.registers[s.active_bank][4],4u);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ec4u:
if(s.local_RAM[3780]==136u&&s.local_RAM[3781]==128u) {nxt=0xf03ec6u;s.pc=nxt;s.registers[s.active_bank][0]=s.registers[s.active_bank][4];}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ec6u:
if(s.local_RAM[3782]==174u&&s.local_RAM[3783]==164u) {nxt=0xf03ec8u;s.pc=nxt;CHECK(rd32(bus,&s,s.registers[s.active_bank][14]+84u,&v));s.registers[s.active_bank][4]=v;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ec8u:
if(s.local_RAM[3784]==152u&&s.local_RAM[3785]==5u&&s.local_RAM[3786]==62u&&s.local_RAM[3787]==228u&&s.local_RAM[3788]==0u&&s.local_RAM[3789]==240u) {nxt=0xf03eceu;s.pc=nxt;s.registers[s.active_bank][5]=0xf03ee4u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eceu:
if(s.local_RAM[3790]==152u&&s.local_RAM[3791]==6u&&s.local_RAM[3792]==62u&&s.local_RAM[3793]==0u&&s.local_RAM[3794]==0u&&s.local_RAM[3795]==240u) {nxt=0xf03ed4u;s.pc=nxt;s.registers[s.active_bank][6]=0xf03e00u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ed4u:
if(s.local_RAM[3796]==152u&&s.local_RAM[3797]==20u&&s.local_RAM[3798]==128u&&s.local_RAM[3799]==0u&&s.local_RAM[3800]==0u&&s.local_RAM[3801]==0u) {nxt=0xf03edau;s.pc=nxt;s.registers[s.active_bank][20]=0x8000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03edau:
if(s.local_RAM[3802]==40u&&s.local_RAM[3803]==165u) {nxt=0xf03edcu;s.pc=nxt;s.registers[s.active_bank][5]|=s.registers[s.active_bank][5];
   zn(&s,s.registers[s.active_bank][5]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03edcu:
if(s.local_RAM[3804]==2u&&s.local_RAM[3805]==129u) {nxt=0xf03edeu;s.pc=nxt;s.registers[s.active_bank][1]=add(&s,s.registers[s.active_bank][1],s.registers[s.active_bank][20]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03edeu:
if(s.local_RAM[3806]==198u&&s.local_RAM[3807]==165u) {nxt=0xf03ee0u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+84u,s.registers[s.active_bank][5]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ee0u:
if(s.local_RAM[3808]==208u&&s.local_RAM[3809]==192u) {nxt=0xf03ee2u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][6];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ee2u:
if(s.local_RAM[3810]==228u&&s.local_RAM[3811]==0u) {nxt=0xf03ee4u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ee4u:
if(s.local_RAM[3812]==40u&&s.local_RAM[3813]==132u) {nxt=0xf03ee6u;s.pc=nxt;s.registers[s.active_bank][4]|=s.registers[s.active_bank][4];
   zn(&s,s.registers[s.active_bank][4]);}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ee6u:
if(s.local_RAM[3814]==198u&&s.local_RAM[3815]==164u) {nxt=0xf03ee8u;s.pc=nxt;CHECK(wr32(bus,&s,s.registers[s.active_bank][14]+84u,s.registers[s.active_bank][4]));}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ee8u:
if(s.local_RAM[3816]==152u&&s.local_RAM[3817]==0u&&s.local_RAM[3818]==48u&&s.local_RAM[3819]==0u&&s.local_RAM[3820]==0u&&s.local_RAM[3821]==240u) {nxt=0xf03eeeu;s.pc=nxt;s.registers[s.active_bank][0]=0xf03000u;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03eeeu:
if(s.local_RAM[3822]==208u&&s.local_RAM[3823]==0u) {nxt=0xf03ef0u;s.pc=nxt;if(condition(&s,0)){pending=1;target=s.registers[s.active_bank][0];}}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
case 0xf03ef0u:
if(s.local_RAM[3824]==228u&&s.local_RAM[3825]==0u) {nxt=0xf03ef2u;s.pc=nxt;}
else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;
default:return BIWN_FIRMWARE_GPU_RENDERER_BAD_PC;
}if(delayed){if(pending)return BIWN_FIRMWARE_GPU_RENDERER_BAD_DELAY;if(s.pc==nxt)s.pc=resume;}if(!pending){budget--;if(!(s.control&1u)){*state=s;return 0;}}}*state=s;return 4;}
