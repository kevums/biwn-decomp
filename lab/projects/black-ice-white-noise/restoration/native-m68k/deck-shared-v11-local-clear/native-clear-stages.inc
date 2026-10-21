/* 10968 target-bus specialization. Geometry supplies ordinary private task
 * stack arguments and clears ordinary records; its guest bytes cannot alias
 * the native CPU context. No callee/suspension boundary occurs in the loop.
 * Keep loop registers local and materialize the last ADD/CMP flags at its
 * exit. Byte reads/writes retain original order and one operation per byte.
 * Native direct accesses cannot report host callback failures; the portable
 * coordinator body remains the implementation for callback/error contracts.
 * This does not establish arbitrary IRQ/context-alias equivalence. */
__attribute__((noinline)) static void native_clear_records(struct biwn_deck_context *s,uint32_t budget){
 uint32_t *r=s->cpu.registers,total,address,counter,previous=0,iterations=0;
 r[0]=(r[0]&0xffff0000u)|deeper_read(s,r[15]+4,2);deck_nz(s,r[0],16);
 r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
 r[9]=r[0]+0x47b88u;r[1]&=0xffff0000u;deck_nz(s,0,16);
 r[0]=(r[0]&0xffff0000u)|deeper_read(s,r[15]+6,2);deck_nz(s,r[0],16);
 r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
 if(s->cpu.sr&4u){s->cpu.pc=0x1098e;return;}
 total=r[0];address=r[9];counter=r[1];
 if(s->error)return;
 do {
  volatile uint8_t *byte;
  if(!budget){s->error=4;break;}budget--;
  byte=(volatile uint8_t *)(address&0xffffffu);
  {uint8_t old=*byte;(void)old;*byte=0;}
  address++;previous=counter;
  counter=(counter&0xffff0000u)|((counter+1u)&65535u);iterations++;
 }while(total>deck_sx16(counter));
 r[9]=address;r[1]=counter;
 if(iterations){
  r[8]=deck_sx16(counter);
  (void)scene_alu16(s,previous,1,0,0);
  (void)deck_alu(s,total,r[8],1,1);
 }
 if(!s->error)s->cpu.pc=0x1098e;
}
