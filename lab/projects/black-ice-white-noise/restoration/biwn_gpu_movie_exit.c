/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_movie_exit.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_movie_exit.h"
#include <string.h>
static void zn(struct biwn_gpu_movie_exit_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_movie_exit_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static int condition(struct biwn_gpu_movie_exit_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_movie_exit_bus *bus,struct biwn_gpu_movie_exit_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int wr32(struct biwn_gpu_movie_exit_bus *bus,struct biwn_gpu_movie_exit_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;if(s->active_bank)return 1;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_movie_exit_status)status;}while(0)
enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_run(struct biwn_gpu_movie_exit_bus *bus,struct biwn_gpu_movie_exit_state *state,uint32_t budget){struct biwn_gpu_movie_exit_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read32||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03000u: /* movei   $f03130,r28 */
   s.registers[0][28]=0xf03130u;
   s.pc=0xf03006u;break;
  case 0xf03006u: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf0300cu;break;
  case 0xf0300cu: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf0300eu;break;
  case 0xf0300eu: /* load    (r30),r29 */
   CHECK(rd32(bus,&s,s.registers[0][30]&~3u,&v));s.registers[0][29]=v;
   s.pc=0xf03010u;break;
  case 0xf03130u: /* movei   $f031be,r28 */
   s.registers[0][28]=0xf031beu;
   s.pc=0xf03136u;break;
  case 0xf03136u: /* bset    $9,r29 */
   s.registers[0][29]|=(1u<<9);
   zn(&s,s.registers[0][29]);
   s.pc=0xf03138u;break;
  case 0xf03138u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0313au;break;
  case 0xf0313au: /* bclr    $3,r29 */
   s.registers[0][29]&=~(1u<<3);
   zn(&s,s.registers[0][29]);
   s.pc=0xf0313cu;break;
  case 0xf0313cu: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf0313eu;break;
  case 0xf0313eu: /* store   r29,(r30) */
   CHECK(wr32(bus,&s,local(s.registers[0][30])?(s.registers[0][30]&~3u):s.registers[0][30],s.registers[0][29]));
   s.pc=0xf03140u;break;default:return BIWN_GPU_MOVIE_EXIT_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_MOVIE_EXIT_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_GPU_MOVIE_EXIT_WORK_LIMIT;}

enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_CPU_control5(struct biwn_gpu_movie_exit_bus *bus,struct biwn_gpu_movie_exit_state *state){struct biwn_gpu_movie_exit_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;s.control=(s.control&0xf7c0u)|1u;s.control|=0x40u;if(!(s.flags&8u)&&(s.flags&0x10u)){s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03000u;}*state=s;return 0;}
