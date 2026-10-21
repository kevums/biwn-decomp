/* E540 recovered multiply adapted to the existing private CPU context.
 * Coordinator authored from the previously qualified arithmetic formulas.
 * No instruction decoder, original arithmetic call, or new scratch arena.
 * Preserve the original four word reads, public sign-word push/NOT/TST,
 * D1 low-product result, A0/A1 clobbers and exact final logical CCR.
 * Successful direct bus; context and ordinary task stack cannot alias.
 */
static inline uint32_t native_math_mul16(uint16_t a,uint16_t b){
 uint32_t result=a;
 __asm__("mulu.w %1,%0":"+d"(result):"d"(b):"cc");
 return result;
}
__attribute__((noinline,used))
static void native_multiply_context(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,a,b,aa,bb,cross,partial,low,absolute,result;
 uint16_t words[4],sign,flags;unsigned i;
 if(s->error)return;
 r[8]=r[2];r[9]=r[3];
 for(i=0;i<4;i++){
  words[i]=(uint16_t)deeper_read(s,r[15]+4u+2u*i,2);
  r[i]=(uint32_t)(int32_t)(int16_t)words[i];
 }
 a=((uint32_t)words[0]<<16)|words[1];
 b=((uint32_t)words[2]<<16)|words[3];
 r[15]-=2;deck_bank(s);deeper_write(s,r[15],2,words[0]);
 if(b&0x80000000u){
  sign=(uint16_t)deeper_read(s,r[15],2);
  deeper_write(s,r[15],2,(uint16_t)~sign);
 }
 aa=a&0x80000000u?0u-a:a;bb=b&0x80000000u?0u-b:b;
 cross=native_math_mul16((uint16_t)(aa>>16),(uint16_t)bb)
      +native_math_mul16((uint16_t)(bb>>16),(uint16_t)aa);
 partial=(cross&65535u)<<16;
 low=native_math_mul16((uint16_t)aa,(uint16_t)bb);
 absolute=partial+low;
 r[1]=low;r[2]=r[8];r[3]=r[9];
 sign=(uint16_t)deeper_read(s,r[15],2);r[15]+=2;deck_bank(s);
 result=sign&0x8000u?0u-absolute:absolute;r[0]=result;
 flags=(uint16_t)((absolute<partial?16u:0u)|(sign?0u:4u)|(sign&0x8000u?8u:0u));
 if(sign&0x8000u)
  flags=(uint16_t)((result?0u:4u)|(result&0x80000000u?8u:0u)
       |(absolute?17u:0u)|(absolute==0x80000000u?2u:0u));
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xffe0u)|flags);s->cpu.pc=0xe586u;
}
