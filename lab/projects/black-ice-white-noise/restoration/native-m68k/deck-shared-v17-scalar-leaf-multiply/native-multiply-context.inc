/* Coordinator-provided target primitives, not model-authored. */
static inline uint32_t native_math_mul16(uint16_t a,uint16_t b){
 uint32_t v=a;__asm__("mulu.w %1,%0":"+d"(v):"d"(b):"cc");return v;
}
static inline uint32_t native_math_add(uint32_t a,uint32_t b,uint16_t *flags){
 uint16_t f;__asm__("add.l %2,%0\n\tmove.w %%sr,%1":"+d"(a),"=d"(f):"d"(b):"cc");*flags=f&16u;return a;
}
static inline uint16_t native_math_tst16(uint16_t a){
 uint16_t f;__asm__("tst.w %1\n\tmove.w %%sr,%0":"=d"(f):"d"(a):"cc");return f&15u;
}
static inline uint32_t native_math_neg(uint32_t a,uint16_t *flags){
 uint16_t f;__asm__("neg.l %0\n\tmove.w %%sr,%1":"+d"(a),"=d"(f)::"cc");*flags=f&31u;return a;
}
/* Coordinator scalar optimization for successful nonaliasing RAM.
 * Four ordered words and original sign scratch effects remain observable.
 * No IRQ/intermediate virtual register or bus failure claim. */
__attribute__((noinline,used))
static void native_multiply_context(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,sp,a,b,aa,bb,cross,partial,low,absolute,result;
 uint16_t ah,al,bh,bl,sign,flags;
 if(s->error)return;
 sp=r[15];
 ah=(uint16_t)deeper_read(s,sp+4u,2);
 al=(uint16_t)deeper_read(s,sp+6u,2);
 bh=(uint16_t)deeper_read(s,sp+8u,2);
 bl=(uint16_t)deeper_read(s,sp+10u,2);
 a=((uint32_t)ah<<16)|al;b=((uint32_t)bh<<16)|bl;
 deeper_write(s,sp-2u,2,ah);
 if(b&0x80000000u){
  sign=(uint16_t)deeper_read(s,sp-2u,2);
  deeper_write(s,sp-2u,2,(uint16_t)~sign);
 }
 aa=a&0x80000000u?0u-a:a;bb=b&0x80000000u?0u-b:b;
 cross=native_math_mul16((uint16_t)(aa>>16),(uint16_t)bb)
      +native_math_mul16((uint16_t)(bb>>16),(uint16_t)aa);
 partial=(cross&65535u)<<16;
 low=native_math_mul16((uint16_t)aa,(uint16_t)bb);
 absolute=native_math_add(partial,low,&flags);
 sign=(uint16_t)deeper_read(s,sp-2u,2);
 if(sign&0x8000u)result=native_math_neg(absolute,&flags);
 else{result=absolute;flags|=native_math_tst16(sign);}
 r[0]=result;r[1]=low;r[8]=r[2];r[9]=r[3];
 deck_bank(s);s->cpu.sr=(uint16_t)((s->cpu.sr&0xffe0u)|flags);s->cpu.pc=0xe586u;
}
