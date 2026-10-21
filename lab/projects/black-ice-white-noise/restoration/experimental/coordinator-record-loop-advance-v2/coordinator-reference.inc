/* Readable170A0 normal-entry record construction. Two original40-record loops;
 * complete logical CPU and original guest MOVEM/argument/JSR frames retained.
 * Copy E3E0 and movement-matrix E220 are explicit providers, not decoded here.
 * Host error/budget atomicity is supplied by the wrapper. Native builds have
 * no synthetic deadline. Private-context aliases and arbitraryIRQ are outside
 * this normal-call contract. This is reconstruction, not original source.
 */
#ifndef GEOMETRY_RECORDS_BEGIN
#define GEOMETRY_RECORDS_BEGIN(s) ((void)(s))
#define GEOMETRY_RECORDS_END(s) ((void)(s))
#endif
static inline uint32_t gr_sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static inline int gr_work(struct biwn_deck_context *s){
 if(s->error)return 0;
#ifndef GEOMETRY_RECORDS_NATIVE_DIRECT
 if(!s->budget){s->error=4;return 0;}s->budget--;
#endif
 return 1;
}
static inline uint32_t gr_read(struct biwn_deck_context *s,uint32_t a,unsigned w){
 uint8_t value=0;if(s->error)return 0;
 if(w==1){if(s->bus->read8(s->bus->context,a&0xffffffu,&value))s->error=2;return value;}
 return deck_read(s,a,w);
}
static inline void gr_move_register(struct biwn_deck_context *s,unsigned n,unsigned w,uint32_t v){
 uint32_t mask=w==4?0xffffffffu:w==2?0xffffu:0xffu;
 s->cpu.registers[n]=(s->cpu.registers[n]&~mask)|(v&mask);deck_nz(s,v,w*8u);
}
static inline void gr_move_memory(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){
 deck_write(s,a,w,v);deck_nz(s,v,w*8u);
}
static inline void gr_clear(struct biwn_deck_context *s,uint32_t a,unsigned w){
 if(s->error)return;
#ifdef GEOMETRY_RECORDS_NATIVE_DIRECT
 volatile void *p=(volatile void *)(a&0xffffffu);
 if(w==2)__asm__ volatile("clr.w (%0)"::"a"(p):"memory","cc");
 else __asm__ volatile("clr.l (%0)"::"a"(p):"memory","cc");
#else
 /* High-level Unicorn traces omit CLR dummy reads. The native bus verifier
  * must qualify the physical read/write operation separately. */
 deck_write(s,a,w,0);
#endif
 deck_nz(s,0,w*8u);
}
/* Both original loop multipliers consume a signed lowword and replace NZVC.
 * X and upperSR survive; the temporary MOVE.W flags are dead before MULS. */
static inline uint32_t gr_record_stride(struct biwn_deck_context *s,uint32_t index,unsigned stride){
#ifdef GEOMETRY_RECORDS_NATIVE_DIRECT
 uint32_t result=index;uint16_t flags;
 if(stride==206u)__asm__("muls.w #206,%0\n\tmove.w %%sr,%1":"+d"(result),"=d"(flags)::"cc");
 else __asm__("muls.w #30,%0\n\tmove.w %%sr,%1":"+d"(result),"=d"(flags)::"cc");
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(flags&15u));return result;
#else
 uint32_t result=gr_sx16(index)*stride;deck_nz(s,result,32);return result;
#endif
}
static inline int gr_ble(const struct biwn_deck_context *s){
 return(s->cpu.sr&4u)||(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u);
}
#ifdef GEOMETRY_RECORDS_NATIVE_DIRECT
#include "model-native-advance.inc"
#endif
static inline int gr_next(struct biwn_deck_context *s){
#ifdef GEOMETRY_RECORDS_NATIVE_DIRECT
 return gr_next_native(s);
#else
 uint32_t u=scene_alu16(s,s->cpu.registers[3],1,0,0);
 s->cpu.registers[3]=(s->cpu.registers[3]&0xffff0000u)|u;
 (void)scene_alu16(s,s->cpu.registers[3],39,1,1);return gr_ble(s);
#endif
}
#define GR_R(a,w,v) do{(v)=gr_read(s,(a),(w));if(s->error)return;}while(0)
#define GR_M(a,w,v) do{gr_move_memory(s,(a),(w),(v));if(s->error)return;}while(0)
#define GR_LOAD(n,w,a) do{GR_R((a),(w),v);gr_move_register(s,(n),(w),v);}while(0)
#define GR_PUSH(v) do{deck_push(s,(v));if(s->error)return;}while(0)
#define GR_CALL(a,ret) do{deck_call(s,(a),(ret));if(s->error)return;}while(0)
#define GR_CLR(a,w) do{gr_clear(s,(a),(w));if(s->error)return;}while(0)
#define GR_CLEAR_PUSH() do{r[15]-=4u;deck_bank(s);GR_CLR(r[15],4);}while(0)
static void geometry_records_body(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,v,u;
 if(!gr_work(s))return;
 GEOMETRY_RECORDS_BEGIN(s);
 /* MOVEM predecrement order: A5,A4,A3,A2,D4,D3,D2. */
 for(int n=13;n>=10;n--)GR_PUSH(r[n]);
 for(int n=4;n>=2;n--)GR_PUSH(r[n]);
 GR_R(0x49b88u,4,u);v=deck_alu(s,u,1,0,0);deck_write(s,0x49b88u,4,v);if(s->error)return;
 r[11]=0x49b8au;GR_R(r[11],2,v);GR_M(0x49d0cu,2,v);
 GR_LOAD(0,4,0x49b88u);r[0]=scene_shift(s,r[0],6,1);r[10]=0x47b88u;
 GR_PUSH(0x40u);GR_PUSH(r[10]+r[0]);GR_PUSH(0x49cccu);GR_CALL(0xe3e0u,0x170d8u);deck_adjust(s,12);
 GR_LOAD(0,4,0x49b88u);r[0]=deck_alu(s,r[0],1,1,0);r[0]=scene_shift(s,r[0],6,1);
 GR_R(r[11],2,v);GR_M(r[10]+r[0]+0x18u,2,v);
 GR_LOAD(0,4,0x49b88u);r[0]=scene_shift(s,r[0],6,1);GR_LOAD(4,2,0x49b8eu);
 GR_R(r[10]+r[0]+0x14u,2,u);v=scene_alu16(s,u,r[4],1,0);deck_write(s,r[10]+r[0]+0x14u,2,v);if(s->error)return;
 GR_R(0x49caau,4,r[8]);GR_R(r[8],4,v);GR_M(r[10]+r[0]+0x3cu,4,v);
 gr_move_register(s,3,2,0);r[12]=0x49d6cu;r[13]=r[11];r[11]=r[10];
 /* Actor descriptors have a signed206-byte stride and optional model handle. */
 do{
  if(!gr_work(s))return;
  r[2]=gr_record_stride(s,r[3],206u);
  GR_R(r[12]+r[2],2,v);deck_nz(s,v,16);
  if(v){
   GR_R(0x49c60u,2,v);(void)scene_alu16(s,v,2,1,1);
   if(v==2u){
    GR_R(r[12]+r[2]+0x2au,2,v);r[8]=gr_sx16(v);GR_R(0x49c1cu,4,v);(void)deck_alu(s,r[8],v,1,1);
    if(r[8]!=v)goto actor_next;
   }
   GR_R(0x49b88u,4,u);v=deck_alu(s,u,1,0,0);deck_write(s,0x49b88u,4,v);if(s->error)return;
   r[10]=r[12]+r[2];GR_R(r[13],2,v);GR_M(r[10]+0xc0u,2,v);
   GR_LOAD(0,4,0x49b88u);r[0]=scene_shift(s,r[0],6,1);
   GR_PUSH(0x40u);GR_PUSH(r[11]+r[0]);gr_move_register(s,4,4,r[2]);r[4]=deck_alu(s,r[4],0x49decu,0,0);
   GR_PUSH(r[4]);deck_nz(s,r[4],32);GR_CALL(0xe3e0u,0x17166u);deck_adjust(s,12);
   GR_LOAD(1,4,0x49b88u);r[1]=deck_alu(s,r[1],1,1,0);gr_move_register(s,0,4,r[1]);r[0]=scene_shift(s,r[0],6,1);
   GR_R(r[13],2,v);GR_M(r[11]+r[0]+0x18u,2,v);
   GR_LOAD(0,4,0x49b88u);r[0]=scene_shift(s,r[0],6,1);
   GR_LOAD(4,2,r[12]+r[2]+6u);GR_R(0x49c52u,2,v);gr_move_register(s,4,2,scene_alu16(s,r[4],v,1,0));
   /* A MOVE after SUB clears V/C while preserving the SUB-produced X. */
   GR_M(r[11]+r[0]+0x12u,2,r[4]);GR_R(r[12]+r[2]+8u,2,v);GR_M(r[11]+r[0]+0x14u,2,v);
   GR_LOAD(4,2,r[12]+r[2]+12u);GR_R(0x49c58u,2,v);u=scene_alu16(s,r[4],v,1,0);r[4]=(r[4]&0xffff0000u)|u;
   GR_M(r[11]+r[0]+0x16u,2,r[4]);GR_LOAD(4,2,0x49b8eu);
   GR_R(r[11]+r[0]+0x14u,2,u);v=scene_alu16(s,u,r[4],1,0);deck_write(s,r[11]+r[0]+0x14u,2,v);if(s->error)return;
   GR_R(r[10]+0xa0u,2,v);(void)scene_alu16(s,v,8,1,1);
   if(v==8u){
    GR_R(r[12]+r[2]+0x5eu,4,v);deck_nz(s,v,32);
    if(v){GR_R(r[12]+r[2]+0x5eu,4,r[8]);GR_R(r[8],4,v);GR_M(r[11]+r[0]+0x3cu,4,v);}
    else GR_M(0x49b88u,4,r[1]);
   }
  }
actor_next:;
 }while(gr_next(s));
 /* Static descriptors have a signed30-byte stride and table-driven matrix flag. */
 gr_move_register(s,3,2,0);r[11]=0x4bd9cu;r[10]=0x47b88u;
 do{
  if(!gr_work(s))return;
  r[2]=gr_record_stride(s,r[3],30u);
  GR_R(r[11]+r[2],2,v);deck_nz(s,v,16);
  if(v){
   GR_R(0x49c60u,2,v);(void)scene_alu16(s,v,2,1,1);
   if(v==2u){
    GR_R(r[11]+r[2]+16u,2,v);r[8]=gr_sx16(v);GR_R(0x49c1cu,4,v);(void)deck_alu(s,r[8],v,1,1);
    if(r[8]!=v)goto static_next;
   }
   GR_R(0x49b88u,4,u);v=deck_alu(s,u,1,0,0);deck_write(s,0x49b88u,4,v);if(s->error)return;
   GR_LOAD(0,4,0x49b88u);r[0]=scene_shift(s,r[0],6,1);r[8]=r[0]+0x47bacu;
   for(unsigned n=0;n<6;n++){GR_R(0x437e0u+n*4u,4,v);GR_M(r[8],4,v);if(n<5)r[8]+=4u;}
   GR_LOAD(0,4,0x49b88u);r[0]=deck_alu(s,r[0],1,1,0);r[0]=scene_shift(s,r[0],6,1);
   GR_R(0x49b8au,2,v);GR_M(r[10]+r[0]+0x18u,2,v);
   GR_LOAD(0,4,0x49b88u);gr_move_register(s,1,4,r[0]);r[1]=scene_shift(s,r[1],6,1);
   GR_LOAD(4,2,r[11]+r[2]+4u);GR_R(0x49c52u,2,v);u=scene_alu16(s,r[4],v,1,0);r[4]=(r[4]&0xffff0000u)|u;
   GR_M(r[10]+r[1]+0x12u,2,r[4]);GR_R(r[11]+r[2]+6u,2,v);GR_M(r[10]+r[1]+0x14u,2,v);
   GR_LOAD(4,2,r[11]+r[2]+10u);GR_R(0x49c58u,2,v);u=scene_alu16(s,r[4],v,1,0);r[4]=(r[4]&0xffff0000u)|u;
   GR_M(r[10]+r[1]+0x16u,2,r[4]);GR_LOAD(4,2,0x49b8eu);
   GR_R(r[10]+r[1]+0x14u,2,u);v=scene_alu16(s,u,r[4],1,0);deck_write(s,r[10]+r[1]+0x14u,2,v);if(s->error)return;
   gr_move_register(s,0,4,0);GR_LOAD(0,2,r[11]+r[2]);r[8]=0x4208cu;GR_R(r[8]+r[0],1,v);
   s->cpu.sr=(uint16_t)((s->cpu.sr&~4u)|((v&2u)?0:4u));
   if(v&2u){
    GR_M(r[10]+r[1]+0x20u,2,7);GR_R(r[11]+r[2]+24u,4,v);GR_M(r[10]+r[1]+0x3cu,4,v);
    GR_CLEAR_PUSH();GR_CLEAR_PUSH();gr_move_register(s,0,4,0);GR_LOAD(0,1,r[11]+r[2]+12u);
    GR_PUSH(r[0]);deck_nz(s,r[0],32);GR_CLEAR_PUSH();GR_PUSH(r[10]+r[1]);GR_CALL(0xe220u,0x172c4u);deck_adjust(s,20);
   }else{
    r[8]=r[10]+r[1];GR_M(r[8]+16u,2,0x4000u);GR_M(r[8]+8u,2,0x4000u);GR_M(r[8],2,0x4000u);
    GR_CLR(r[8]+6u,2);GR_CLR(r[8]+4u,2);GR_CLR(r[10]+r[1]+2u,2);
    GR_CLR(r[8]+14u,2);GR_CLR(r[8]+12u,2);GR_CLR(r[10]+r[1]+10u,2);GR_M(r[10]+r[1]+0x20u,2,8);
    GR_R(r[11]+r[2]+20u,4,r[8]);GR_R(r[8],4,v);GR_M(r[10]+r[1]+0x3cu,4,v);
   }
  }
static_next:;
 }while(gr_next(s));
 GR_LOAD(0,4,0x49b88u);r[0]=scene_shift(s,r[0],6,1);r[8]=0x47b88u;GR_CLR(r[8]+r[0]+0x18u,2);
 /* MOVEM postincrement restores registers without changing condition codes. */
 for(unsigned n=2;n<=4;n++){r[n]=deck_pop(s);if(s->error)return;}
 for(unsigned n=10;n<=13;n++){r[n]=deck_pop(s);if(s->error)return;}
 s->cpu.pc=0x17324u;GEOMETRY_RECORDS_END(s);
}
#undef GR_R
#undef GR_M
#undef GR_LOAD
#undef GR_PUSH
#undef GR_CALL
#undef GR_CLR
#undef GR_CLEAR_PUSH
