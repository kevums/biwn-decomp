/* Structured normal-call E098/E0A6/E0F2/E148/E19E/E202 family.
 * Reconstructed from the existing logical and pinned full-CPU references.
 * Ordered mailbox/global accesses and original internal guest JSR/RTS words
 * are retained. This is not original source or an IRQ/cycle-equivalence claim.
 */
#ifndef SCENE_GPU_BEGIN
#define SCENE_GPU_BEGIN(s, entry) ((void)(s), (void)(entry))
#define SCENE_GPU_END(s, entry) ((void)(s), (void)(entry))
#endif
#ifndef SCENE_GPU_WAIT_BEGIN
#define SCENE_GPU_WAIT_BEGIN(s) ((void)(s))
#define SCENE_GPU_WAIT_END(s) ((void)(s))
#endif
#ifndef SCENE_GPU_READ32
#define SCENE_GPU_READ32(s, address) deck_read((s), (address), 4)
#endif
static inline int scene_gpu_work(struct biwn_deck_context *s) {
 if(s->error)return 0;
#ifndef SCENE_GPU_NATIVE_DIRECT
 if(!s->budget){s->error=4;return 0;}s->budget--;
#endif
 return 1;
}
static void scene_gpu_wait_body(struct biwn_deck_context *s) {
 uint32_t value;
 do {
  if(!scene_gpu_work(s))return;
  value=SCENE_GPU_READ32(s,0xf03200u);if(s->error)return;
  (void)deck_alu(s,value,0,1,1);
 }while(!(s->cpu.sr&4u));
 s->cpu.pc=0xe0a4u;
}
static inline void scene_gpu_wait_call(struct biwn_deck_context *s,uint32_t ret) {
 uint32_t actual;
 if(s->error)return;
 deck_push(s,ret);if(s->error)return;s->cpu.pc=0xe098u;
 SCENE_GPU_WAIT_BEGIN(s);
 scene_gpu_wait_body(s);if(s->error)return;
 SCENE_GPU_WAIT_END(s);
 actual=deck_pop(s);if(s->error)return;
 if(actual!=ret){s->error=5;return;}s->cpu.pc=ret;
}
static inline void scene_gpu_move(struct biwn_deck_context *s,uint32_t address,uint32_t value) {
 deck_write(s,address,4,value);if(s->error)return;deck_nz(s,value,32);
}
static void scene_gpu_family_body(struct biwn_deck_context *s) {
 uint32_t entry=s->cpu.pc,command=0,first=0,last=0,value;
 if(!scene_gpu_work(s))return;
 switch(entry) {
 case 0xe098u:break;
 case 0xe0a6u:command=0x4d80u;first=0xe0acu;last=0xe0f0u;break;
 case 0xe0f2u:command=0x6ae0u;first=0xe0f8u;last=0xe146u;break;
 case 0xe148u:command=0x6da0u;first=0xe14eu;last=0xe19cu;break;
 case 0xe19eu:command=0x52e0u;first=0xe1a4u;last=0xe200u;break;
 case 0xe202u:command=0x57a0u;first=0xe208u;last=0xe21eu;break;
 default:s->error=7;return;
 }
 SCENE_GPU_BEGIN(s,entry);
 if(entry==0xe098u){scene_gpu_wait_body(s);goto done;}
 scene_gpu_wait_call(s,first);if(s->error)return;
 if(entry==0xe19eu) {
  scene_gpu_move(s,0x10a684u,1);if(s->error)return;
  s->cpu.registers[0]=0x47b88u;deck_nz(s,s->cpu.registers[0],32);
  scene_gpu_move(s,0xf0320cu,s->cpu.registers[0]);if(s->error)return;
  s->cpu.registers[0]=deck_alu(s,s->cpu.registers[0],0x40u,0,0);
  scene_gpu_move(s,0xf03210u,s->cpu.registers[0]);if(s->error)return;
  value=SCENE_GPU_READ32(s,0x49b88u);if(s->error)return;
  scene_gpu_move(s,0xf03214u,value);if(s->error)return;
  scene_gpu_move(s,0xf03218u,0x40u);if(s->error)return;
  scene_gpu_move(s,0xf0321cu,0x10a684u);if(s->error)return;
 }else if(entry!=0xe202u) {
  scene_gpu_move(s,0xf0320cu,entry==0xe148u?0x47bc8u:0x47b88u);if(s->error)return;
  scene_gpu_move(s,0xf03210u,0x49b8cu);if(s->error)return;
  if(entry==0xe0a6u) {
   scene_gpu_move(s,0xf03214u,0x49bb4u);if(s->error)return;
   scene_gpu_move(s,0xf03218u,0x49b88u);if(s->error)return;
  }else {
   value=SCENE_GPU_READ32(s,0x49c18u);if(s->error)return;
   scene_gpu_move(s,0xf03214u,value);if(s->error)return;
   value=SCENE_GPU_READ32(s,0x49c1cu);if(s->error)return;
   scene_gpu_move(s,0xf03218u,value);if(s->error)return;
   scene_gpu_move(s,0xf0321cu,entry==0xe0f2u?0x10d688u:0x49b88u);if(s->error)return;
  }
 }
 scene_gpu_move(s,0xf03204u,command);if(s->error)return;
 do {
  if(!scene_gpu_work(s))return;
  value=SCENE_GPU_READ32(s,0xf03204u);if(s->error)return;
  (void)deck_alu(s,value,command,1,1);
 }while(s->cpu.sr&4u);
 if(entry==0xe202u)s->cpu.pc=last;
 else scene_gpu_wait_call(s,last);
done:
 if(!s->error)SCENE_GPU_END(s,entry);
}
