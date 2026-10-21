/* Structured full-CPU recovery of17F14..17F66 from the existing decoded source.
 * Stops before outer RTS. The original185B2 service remains explicit.
 * PEA, address adjustment and MOVEA preserve the helper's final flags.
 * This is native integration of an existing recovered routine, not new discovery.
 */
#ifndef SCENE_ROTATION_BEGIN
#define SCENE_ROTATION_BEGIN(s) ((void)(s))
#define SCENE_ROTATION_END(s) ((void)(s))
#endif
static void scene_rotation_body(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,v;
 SCENE_ROTATION_BEGIN(s);
 deck_push(s,r[10]);deck_nz(s,r[10],32);
 r[8]=0xbd83c;
 r[0]=deck_read(s,r[8],4);deck_nz(s,r[0],32);
 r[9]=0xbd840;
 v=deck_read(s,r[9],4);deck_write(s,r[8],4,v);deck_nz(s,v,32);
 r[8]=0xbd844;
 v=deck_read(s,r[8],4);deck_write(s,r[9],4,v);deck_nz(s,v,32);
 deck_write(s,r[8],4,r[0]);deck_nz(s,r[0],32);
 r[9]=0xbd830;
 r[0]=deck_read(s,r[9],4);deck_nz(s,r[0],32);
 r[10]=0xbd834;
 v=deck_read(s,r[10],4);deck_write(s,r[9],4,v);deck_nz(s,v,32);
 r[8]=0xbd838;
 v=deck_read(s,r[8],4);deck_write(s,r[10],4,v);deck_nz(s,v,32);
 deck_write(s,r[8],4,r[0]);deck_nz(s,r[0],32);
 v=deck_read(s,r[9],4);deck_write(s,0x43daa,4,v);deck_nz(s,v,32);
 deck_push(s,0x777c0);deck_push(s,0x43da0);
 deck_call(s,0x185b2,0x17f62);
 deck_adjust(s,8);r[10]=deck_pop(s);
 s->cpu.pc=0x17f66;
 SCENE_ROTATION_END(s);
}
