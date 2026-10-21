/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_main_boot.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_main_boot.h"
#include <string.h>
static void zn(struct biwn_gpu_main_boot_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_main_boot_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static int condition(struct biwn_gpu_main_boot_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_main_boot_bus *bus,struct biwn_gpu_main_boot_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int wr32(struct biwn_gpu_main_boot_bus *bus,struct biwn_gpu_main_boot_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;if(s->active_bank)return 1;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_main_boot_bus *bus,struct biwn_gpu_main_boot_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_main_boot_status)status;}while(0)
enum biwn_gpu_main_boot_status biwn_gpu_main_boot_run(struct biwn_gpu_main_boot_bus *bus,struct biwn_gpu_main_boot_state *state,uint32_t budget){struct biwn_gpu_main_boot_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03224u: /* movei   $f04000,r31 */
   s.registers[0][31]=0xf04000u;
   s.pc=0xf0322au;break;
  case 0xf0322au: /* movei   $f02100,r0 */
   s.registers[0][0]=0xf02100u;
   s.pc=0xf03230u;break;
  case 0xf03230u: /* load    (r0),r1 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03232u;break;
  case 0xf03232u: /* movei   $d0,r2 */
   s.registers[0][2]=0xd0u;
   s.pc=0xf03238u;break;
  case 0xf03238u: /* or      r2,r1 */
   s.registers[0][1]|=s.registers[0][2];
   zn(&s,s.registers[0][1]);
   s.pc=0xf0323au;break;
  case 0xf0323au: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf0323cu;break;
  case 0xf0323cu: /* movei   $f00020,r3 */
   s.registers[0][3]=0xf00020u;
   s.pc=0xf03242u;break;
  case 0xf03242u: /* movei   $776d8,r4 */
   s.registers[0][4]=0x776d8u;
   s.pc=0xf03248u;break;
case 0xf03248u: /* rorq    $10,r4 */
 v=s.registers[0][4];s.c=v>>31;s.registers[0][4]=(v>>16)|(v<<16);zn(&s,s.registers[0][4]);s.pc=0xf0324au;break;
  case 0xf0324au: /* store   r4,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][4]));
   s.pc=0xf0324cu;break;
  case 0xf0324cu: /* movei   $f00050,r5 */
   s.registers[0][5]=0xf00050u;
   s.pc=0xf03252u;break;
  case 0xf03252u: /* moveq   3,r6 */
   s.registers[0][6]=3u;
   s.pc=0xf03254u;break;
  case 0xf03254u: /* storew  r6,(r5) */
   CHECK(wr16(bus,&s,s.registers[0][5],s.registers[0][6]));
   s.pc=0xf03256u;break;
  case 0xf03256u: /* addq    $2,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],2u);
   s.pc=0xf03258u;break;
  case 0xf03258u: /* movei   $568e,r6 */
   s.registers[0][6]=0x568eu;
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* storew  r6,(r5) */
   CHECK(wr16(bus,&s,s.registers[0][5],s.registers[0][6]));
   s.pc=0xf03260u;break;
  case 0xf03260u: /* movei   $f031be,r9 */
   s.registers[0][9]=0xf031beu;
   s.pc=0xf03266u;break;
  case 0xf03266u: /* movei   $f00028,r7 */
   s.registers[0][7]=0xf00028u;
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* movei   $6c1,r8 */
   s.registers[0][8]=0x6c1u;
   s.pc=0xf03272u;break;
  case 0xf03272u: /* jump    (r9) */
   if(condition(&s,0)){pending=1;target=s.registers[0][9];}
   s.pc=0xf03274u;break;
  case 0xf03274u: /* storew  r8,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][8]));
   s.pc=0xf03276u;break;default:return BIWN_GPU_MAIN_BOOT_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_MAIN_BOOT_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_GPU_MAIN_BOOT_WORK_LIMIT;}
