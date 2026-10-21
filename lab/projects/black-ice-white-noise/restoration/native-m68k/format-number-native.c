
#include "format-number-native.h"
#include "m68k-fact-helpers-v2.h"
static inline uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static inline void np_put(uint32_t *r,unsigned i,unsigned width,uint32_t v){
 uint32_t mask=width==4?0xffffffffu:(1u<<(width*8))-1u;
 r[i]=(r[i]&~mask)|(v&mask);
}
static inline void np_logic(uint32_t *r,uint32_t v,unsigned bits,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),f;
 v&=mask;f=(v?0u:4u)|(v&sign?8u:0u);r[16]=(r[16]&~live)|(f&live);
}
static inline uint32_t np_alu(uint32_t *r,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v,f;
 a&=mask;b&=mask;v=(sub?a-b:a+b)&mask;
 f=((sub?a<b:v<a)?(cmp?1u:17u):0u)|
  ((sub?((a^b)&(a^v)&sign):((~(a^b))&(a^v)&sign))?2u:0u)|(v?0u:4u)|(v&sign?8u:0u);
 r[16]=(r[16]&~live)|(f&live);return v;
}
static inline void np_push(uint32_t *r,uint32_t v){r[15]-=4;PW32(r[15],v);}
static void np_unsigned(uint32_t *r,int remainder){
 uint32_t sp=r[15];int fault=remainder?biwn_native_unsigned_remainder_body(r):biwn_native_unsigned_divide_body(r);
 if(fault){
  if(remainder)r[15]=sp-12;
  biwn_native_semantic_divide_zero(r);
  mf_move32(r,3,r[9]);mf_move32(r,2,r[8]);
  if(remainder){(void)PR32(r[15]);r[15]+=12;mf_move32(r,0,r[1]);}
 }
 /* Complete the helper's original outer RTS public read/pop. */
 (void)PR32(r[15]);r[15]+=4;
}

/* Deterministic lowering of pinned recovered instruction semantics; not model C. */
void biwn_native_format_number_body(uint32_t *r){
 uint32_t v,u;
 goto L_1b212;
L_1b212: /* movem.l d2-d4/a2-a6, -(a7); CCR mask 0 */
   np_push(r,r[14]);
   np_push(r,r[13]);
   np_push(r,r[12]);
   np_push(r,r[11]);
   np_push(r,r[10]);
   np_push(r,r[4]);
   np_push(r,r[3]);
   np_push(r,r[2]);
   goto L_1b216;
L_1b216: /* movea.l $24(a7), a2; CCR mask 0 */
   v=PR32((r[15]+0x24u));
   r[10]=v;
   goto L_1b21a;
L_1b21a: /* move.l $28(a7), d2; CCR mask 0 */
   v=PR32((r[15]+0x28u));
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b21e;
L_1b21e: /* movea.l $2e(a7), a5; CCR mask 0 */
   v=PR32((r[15]+0x2eu));
   r[13]=v;
   goto L_1b222;
L_1b222: /* move.w $32(a7), d3; CCR mask 0 */
   v=PR16((r[15]+0x32u));
   np_put(r,3,2,v);
   np_logic(r,v,16,0u);
   goto L_1b226;
L_1b226: /* clr.w d4; CCR mask 0 */
   v=0;
   np_put(r,4,2,v);
   np_logic(r,0,16,0u);
   goto L_1b228;
L_1b228: /* lea.l $15b7a0.l, a3; CCR mask 0 */
   r[11]=0x15b7a0u;
   goto L_1b22e;
L_1b22e: /* movea.w $2c(a7), a4; CCR mask 0 */
   v=PR16((r[15]+0x2cu));
   r[12]=sx16((uint16_t)v);
   goto L_1b232;
L_1b232: /* lea.l $1b200.l, a6; CCR mask 0 */
   r[14]=0x1b200u;
   goto L_1b238;
L_1b238: /* move.l a4, -(a7); CCR mask 0 */
   v=r[12];
   np_push(r,v);
   np_logic(r,v,32,0u);
   goto L_1b23a;
L_1b23a: /* move.l d2, -(a7); CCR mask 15 */
   v=r[2];
   np_push(r,v);
   np_logic(r,v,32,15u);
   goto L_1b23c;
L_1b23c: /* jsr $e67c.l; CCR mask 16 */
 np_push(r,0x1b242u);
 np_unsigned(r,1);
 goto L_1b242;
L_1b242: /* addq.w #$8, a7; CCR mask 0 */
   v=0x8u;
   r[15]+=sx16((uint16_t)v);
   goto L_1b244;
L_1b244: /* move.b (a6, d0.l), (a3)+; CCR mask 0 */
   v=PR8((r[14]+r[0]));
   PW8(r[11],v);r[11]+=1;
   np_logic(r,v,8,0u);
   goto L_1b248;
L_1b248: /* move.l a4, -(a7); CCR mask 0 */
   v=r[12];
   np_push(r,v);
   np_logic(r,v,32,0u);
   goto L_1b24a;
L_1b24a: /* move.l d2, -(a7); CCR mask 15 */
   v=r[2];
   np_push(r,v);
   np_logic(r,v,32,15u);
   goto L_1b24c;
L_1b24c: /* jsr $e61c.l; CCR mask 0 */
 np_push(r,0x1b252u);
 np_unsigned(r,0);
 goto L_1b252;
L_1b252: /* addq.w #$8, a7; CCR mask 0 */
   v=0x8u;
   r[15]+=sx16((uint16_t)v);
   goto L_1b254;
L_1b254: /* move.l d0, d2; CCR mask 0 */
   v=r[0];
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b256;
L_1b256: /* subq.w #$1, d3; CCR mask 16 */
   v=0x1u;
   u=r[3];
   v=np_alu(r,u,v,16,1,0,16u);
   np_put(r,3,2,v);
   goto L_1b258;
L_1b258: /* tst.l d2; CCR mask 4 */
   v=r[2];
   np_logic(r,v,32,4u);
   goto L_1b25a;
L_1b25a: /* bne.b $1b238; CCR mask 0 */
   if(((r[16]&4u)==0)){goto L_1b238;}
   goto L_1b25c;
L_1b25c: /* move.w d3, d0; CCR mask 0 */
   v=r[3];
   np_put(r,0,2,v);
   np_logic(r,v,16,0u);
   goto L_1b25e;
L_1b25e: /* subq.w #$1, d3; CCR mask 16 */
   v=0x1u;
   u=r[3];
   v=np_alu(r,u,v,16,1,0,16u);
   np_put(r,3,2,v);
   goto L_1b260;
L_1b260: /* tst.w d0; CCR mask 14 */
   v=r[0];
   np_logic(r,v,16,14u);
   goto L_1b262;
L_1b262: /* ble.b $1b27a; CCR mask 0 */
   if(((r[16]&4u)||(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b27a;}
   goto L_1b264;
L_1b264: /* move.b $35(a7), d1; CCR mask 0 */
   v=PR8((r[15]+0x35u));
   np_put(r,1,1,v);
   np_logic(r,v,8,0u);
   goto L_1b268;
L_1b268: /* tst.w (a5); CCR mask 14 */
   v=PR16((r[13]));
   np_logic(r,v,16,14u);
   goto L_1b26a;
L_1b26a: /* ble.b $1b294; CCR mask 0 */
   if(((r[16]&4u)||(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b294;}
   goto L_1b26c;
L_1b26c: /* move.b d1, (a2)+; CCR mask 0 */
   v=r[1];
   PW8(r[10],v);r[10]+=1;
   np_logic(r,v,8,0u);
   goto L_1b26e;
L_1b26e: /* addq.w #$1, d4; CCR mask 0 */
   v=0x1u;
   u=r[4];
   v=np_alu(r,u,v,16,0,0,0u);
   np_put(r,4,2,v);
   goto L_1b270;
L_1b270: /* subq.w #$1, (a5); CCR mask 0 */
   v=0x1u;
   u=PR16((r[13]));
   v=np_alu(r,u,v,16,1,0,0u);
   PW16((r[13]),v);
   goto L_1b272;
L_1b272: /* move.w d3, d0; CCR mask 0 */
   v=r[3];
   np_put(r,0,2,v);
   np_logic(r,v,16,0u);
   goto L_1b274;
L_1b274: /* subq.w #$1, d3; CCR mask 16 */
   v=0x1u;
   u=r[3];
   v=np_alu(r,u,v,16,1,0,16u);
   np_put(r,3,2,v);
   goto L_1b276;
L_1b276: /* tst.w d0; CCR mask 14 */
   v=r[0];
   np_logic(r,v,16,14u);
   goto L_1b278;
L_1b278: /* bgt.b $1b268; CCR mask 0 */
   if((!(r[16]&4u)&&!(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b268;}
   goto L_1b27a;
L_1b27a: /* tst.w (a5); CCR mask 14 */
   v=PR16((r[13]));
   np_logic(r,v,16,14u);
   goto L_1b27c;
L_1b27c: /* ble.b $1b294; CCR mask 0 */
   if(((r[16]&4u)||(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b294;}
   goto L_1b27e;
L_1b27e: /* move.l #$15b7a0, d1; CCR mask 0 */
   v=0x15b7a0u;
   np_put(r,1,4,v);
   np_logic(r,v,32,0u);
   goto L_1b284;
L_1b284: /* cmp.l a3, d1; CCR mask 4 */
   v=r[11];
   u=r[1];
   (void)np_alu(r,u,v,32,1,1,4u);
   goto L_1b286;
L_1b286: /* beq.b $1b294; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b294;}
   goto L_1b288;
L_1b288: /* move.b -(a3), (a2)+; CCR mask 0 */
   r[11]-=1;v=PR8(r[11]);
   PW8(r[10],v);r[10]+=1;
   np_logic(r,v,8,0u);
   goto L_1b28a;
L_1b28a: /* addq.w #$1, d4; CCR mask 0 */
   v=0x1u;
   u=r[4];
   v=np_alu(r,u,v,16,0,0,0u);
   np_put(r,4,2,v);
   goto L_1b28c;
L_1b28c: /* move.w (a5), d0; CCR mask 0 */
   v=PR16((r[13]));
   np_put(r,0,2,v);
   np_logic(r,v,16,0u);
   goto L_1b28e;
L_1b28e: /* subq.w #$1, d0; CCR mask 16 */
   v=0x1u;
   u=r[0];
   v=np_alu(r,u,v,16,1,0,16u);
   np_put(r,0,2,v);
   goto L_1b290;
L_1b290: /* move.w d0, (a5); CCR mask 14 */
   v=r[0];
   PW16((r[13]),v);
   np_logic(r,v,16,14u);
   goto L_1b292;
L_1b292: /* bgt.b $1b284; CCR mask 0 */
   if((!(r[16]&4u)&&!(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b284;}
   goto L_1b294;
L_1b294: /* move.w d4, d0; CCR mask 15 */
   v=r[4];
   np_put(r,0,2,v);
   np_logic(r,v,16,15u);
   goto L_1b296;
L_1b296: /* movem.l (a7)+, d2-d4/a2-a6; CCR mask 0 */
   v=PR32(r[15]);r[2]=v;r[15]+=4;
   v=PR32(r[15]);r[3]=v;r[15]+=4;
   v=PR32(r[15]);r[4]=v;r[15]+=4;
   v=PR32(r[15]);r[10]=v;r[15]+=4;
   v=PR32(r[15]);r[11]=v;r[15]+=4;
   v=PR32(r[15]);r[12]=v;r[15]+=4;
   v=PR32(r[15]);r[13]=v;r[15]+=4;
   v=PR32(r[15]);r[14]=v;r[15]+=4;
   goto L_1b29a;
L_1b29a: /* rts; CCR mask 0 */
 return;
}
