
#include "format-core-native.h"
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
static inline void np_push_width(uint32_t *r,uint32_t v,unsigned width){r[15]-=width;if(width==2)PW16(r[15],v);else PW32(r[15],v);}

static inline uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static void np_shift(uint32_t *r,unsigned index,unsigned bits,unsigned n,int left,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v=r[index]&mask;unsigned c=0,ov=0,i;
 for(i=0;i<n;i++){if(left){uint32_t old=v;c=(v&sign)!=0;v=(v<<1)&mask;ov|=((old^v)&sign)!=0;}else{c=v&1u;v=(v>>1)|(v&sign);}}
 np_put(r,index,bits/8,v);
 uint32_t f=(v?0u:4u)|(v&sign?8u:0u)|(c?(n?17u:1u):0u)|(ov?2u:0u);
 if(!n)live&=~16u;
 r[16]=(r[16]&~live)|(f&live);
}

void biwn_native_format_core_body(uint32_t *r){
 uint32_t v,u;
 goto L_1b29c;
L_1b29c: /* link.w a6, #$fffc; CCR mask 0 */
   np_push_width(r,r[14],4);r[14]=r[15];r[15]+=sx16(0xfffcu);
   goto L_1b2a0;
L_1b2a0: /* movem.l d2-d6/a2-a4, -(a7); CCR mask 0 */
   np_push_width(r,r[12],4);
   np_push_width(r,r[11],4);
   np_push_width(r,r[10],4);
   np_push_width(r,r[6],4);
   np_push_width(r,r[5],4);
   np_push_width(r,r[4],4);
   np_push_width(r,r[3],4);
   np_push_width(r,r[2],4);
   goto L_1b2a4;
L_1b2a4: /* move.l $8(a6), d6; CCR mask 0 */
   v=PR32((r[14]+0x8u));
   np_put(r,6,4,v);
   np_logic(r,v,32,0u);
   goto L_1b2a8;
L_1b2a8: /* movea.l $c(a6), a4; CCR mask 0 */
   v=PR32((r[14]+0xcu));
   r[12]=v;
   goto L_1b2ac;
L_1b2ac: /* movea.l $10(a6), a3; CCR mask 0 */
   v=PR32((r[14]+0x10u));
   r[11]=v;
   goto L_1b2b0;
L_1b2b0: /* movea.l d6, a2; CCR mask 0 */
   v=r[6];
   r[10]=v;
   goto L_1b2b2;
L_1b2b2: /* move.w #$fe, -$2(a6); CCR mask 0 */
   v=0xfeu;
   PW16(((r[14])-0x2u),v);
   np_logic(r,v,16,0u);
   goto L_1b2b8;
L_1b2b8: /* move.b (a4)+, d1; CCR mask 4 */
   v=PR8(r[12]);r[12]+=1;
   np_put(r,1,1,v);
   np_logic(r,v,8,4u);
   goto L_1b2ba;
L_1b2ba: /* beq.w $1b44a; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b44a;}
   goto L_1b2be;
L_1b2be: /* move.b #$d0, d5; CCR mask 0 */
   v=0xd0u;
   np_put(r,5,1,v);
   np_logic(r,v,8,0u);
   goto L_1b2c2;
L_1b2c2: /* cmpi.b #$25, d1; CCR mask 4 */
   v=0x25u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b2c6;
L_1b2c6: /* beq.b $1b2d8; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b2d8;}
   goto L_1b2c8;
L_1b2c8: /* move.w #$1, -(a7); CCR mask 0 */
   v=0x1u;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b2cc;
L_1b2cc: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b2d0;
L_1b2d0: /* ext.w d1; CCR mask 0 */
   v=sx8((uint8_t)r[1]);
   np_put(r,1,2,v);
   np_logic(r,v,16,0u);
   goto L_1b2d2;
L_1b2d2: /* move.w d1, -(a7); CCR mask 0 */
   v=r[1];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b2d4;
L_1b2d4: /* bra.w $1b37e; CCR mask 0 */
   if((1)){goto L_1b37e;}
   goto L_1b2d8;
L_1b2d8: /* move.b (a4)+, d1; CCR mask 0 */
   v=PR8(r[12]);r[12]+=1;
   np_put(r,1,1,v);
   np_logic(r,v,8,0u);
   goto L_1b2da;
L_1b2da: /* clr.w d3; CCR mask 0 */
   v=0;
   np_put(r,3,2,v);
   np_logic(r,0,16,0u);
   goto L_1b2dc;
L_1b2dc: /* clr.w d2; CCR mask 0 */
   v=0;
   np_put(r,2,2,v);
   np_logic(r,0,16,0u);
   goto L_1b2de;
L_1b2de: /* move.b #$20, d4; CCR mask 0 */
   v=0x20u;
   np_put(r,4,1,v);
   np_logic(r,v,8,0u);
   goto L_1b2e2;
L_1b2e2: /* cmpi.b #$30, d1; CCR mask 4 */
   v=0x30u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b2e6;
L_1b2e6: /* bne.b $1b30a; CCR mask 0 */
   if(((r[16]&4u)==0)){goto L_1b30a;}
   goto L_1b2e8;
L_1b2e8: /* move.b d1, d4; CCR mask 0 */
   v=r[1];
   np_put(r,4,1,v);
   np_logic(r,v,8,0u);
   goto L_1b2ea;
L_1b2ea: /* bra.b $1b30a; CCR mask 0 */
   if((1)){goto L_1b30a;}
   goto L_1b2ec;
L_1b2ec: /* move.b d1, d0; CCR mask 0 */
   v=r[1];
   np_put(r,0,1,v);
   np_logic(r,v,8,0u);
   goto L_1b2ee;
L_1b2ee: /* add.b d5, d0; CCR mask 16 */
   v=r[5];
   u=r[0];
   v=np_alu(r,u,v,8,0,0,16u);
   np_put(r,0,1,v);
   goto L_1b2f0;
L_1b2f0: /* cmpi.b #$9, d0; CCR mask 5 */
   v=0x9u;
   u=r[0];
   v=np_alu(r,u,v,8,1,1,5u);
   goto L_1b2f4;
L_1b2f4: /* bhi.b $1b30e; CCR mask 0 */
   if((!(r[16]&5u))){goto L_1b30e;}
   goto L_1b2f6;
L_1b2f6: /* move.w d3, d0; CCR mask 0 */
   v=r[3];
   np_put(r,0,2,v);
   np_logic(r,v,16,0u);
   goto L_1b2f8;
L_1b2f8: /* asl.w #$2, d0; CCR mask 0 */
   u=0x2u;
   np_shift(r,0,16,u&63u,1,0u);
   goto L_1b2fa;
L_1b2fa: /* add.w d3, d0; CCR mask 0 */
   v=r[3];
   u=r[0];
   v=np_alu(r,u,v,16,0,0,0u);
   np_put(r,0,2,v);
   goto L_1b2fc;
L_1b2fc: /* asl.w #$1, d0; CCR mask 0 */
   u=0x1u;
   np_shift(r,0,16,u&63u,1,0u);
   goto L_1b2fe;
L_1b2fe: /* addi.w #$ffd0, d0; CCR mask 0 */
   v=0xffd0u;
   u=r[0];
   v=np_alu(r,u,v,16,0,0,0u);
   np_put(r,0,2,v);
   goto L_1b302;
L_1b302: /* ext.w d1; CCR mask 0 */
   v=sx8((uint8_t)r[1]);
   np_put(r,1,2,v);
   np_logic(r,v,16,0u);
   goto L_1b304;
L_1b304: /* move.w d0, d3; CCR mask 0 */
   v=r[0];
   np_put(r,3,2,v);
   np_logic(r,v,16,0u);
   goto L_1b306;
L_1b306: /* add.w d1, d3; CCR mask 16 */
   v=r[1];
   u=r[3];
   v=np_alu(r,u,v,16,0,0,16u);
   np_put(r,3,2,v);
   goto L_1b308;
L_1b308: /* move.b (a4)+, d1; CCR mask 0 */
   v=PR8(r[12]);r[12]+=1;
   np_put(r,1,1,v);
   np_logic(r,v,8,0u);
   goto L_1b30a;
L_1b30a: /* tst.b d1; CCR mask 4 */
   v=r[1];
   np_logic(r,v,8,4u);
   goto L_1b30c;
L_1b30c: /* bne.b $1b2ec; CCR mask 0 */
   if(((r[16]&4u)==0)){goto L_1b2ec;}
   goto L_1b30e;
L_1b30e: /* cmpi.b #$6c, d1; CCR mask 4 */
   v=0x6cu;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b312;
L_1b312: /* beq.b $1b31a; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b31a;}
   goto L_1b314;
L_1b314: /* cmpi.b #$4c, d1; CCR mask 4 */
   v=0x4cu;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b318;
L_1b318: /* bne.b $1b31e; CCR mask 0 */
   if(((r[16]&4u)==0)){goto L_1b31e;}
   goto L_1b31a;
L_1b31a: /* moveq #$1, d2; CCR mask 0 */
   v=sx8(0x1u);r[2]=v;np_logic(r,v,32,0u);
   goto L_1b31c;
L_1b31c: /* move.b (a4)+, d1; CCR mask 0 */
   v=PR8(r[12]);r[12]+=1;
   np_put(r,1,1,v);
   np_logic(r,v,8,0u);
   goto L_1b31e;
L_1b31e: /* tst.b d1; CCR mask 4 */
   v=r[1];
   np_logic(r,v,8,4u);
   goto L_1b320;
L_1b320: /* beq.w $1b44a; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b44a;}
   goto L_1b324;
L_1b324: /* cmpi.b #$6f, d1; CCR mask 14 */
   v=0x6fu;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,14u);
   goto L_1b328;
L_1b328: /* beq.w $1b3e0; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b3e0;}
   goto L_1b32c;
L_1b32c: /* bgt.b $1b34a; CCR mask 0 */
   if((!(r[16]&4u)&&!(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b34a;}
   goto L_1b32e;
L_1b32e: /* cmpi.b #$63, d1; CCR mask 14 */
   v=0x63u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,14u);
   goto L_1b332;
L_1b332: /* beq.b $1b376; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b376;}
   goto L_1b334;
L_1b334: /* bgt.b $1b340; CCR mask 0 */
   if((!(r[16]&4u)&&!(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b340;}
   goto L_1b336;
L_1b336: /* cmpi.b #$25, d1; CCR mask 4 */
   v=0x25u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b33a;
L_1b33a: /* beq.b $1b36a; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b36a;}
   goto L_1b33c;
L_1b33c: /* bra.w $1b444; CCR mask 0 */
   if((1)){goto L_1b444;}
   goto L_1b340;
L_1b340: /* cmpi.b #$64, d1; CCR mask 4 */
   v=0x64u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b344;
L_1b344: /* beq.b $1b3ae; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b3ae;}
   goto L_1b346;
L_1b346: /* bra.w $1b444; CCR mask 0 */
   if((1)){goto L_1b444;}
   goto L_1b34a;
L_1b34a: /* cmpi.b #$75, d1; CCR mask 14 */
   v=0x75u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,14u);
   goto L_1b34e;
L_1b34e: /* beq.w $1b418; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b418;}
   goto L_1b352;
L_1b352: /* bgt.b $1b35e; CCR mask 0 */
   if((!(r[16]&4u)&&!(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b35e;}
   goto L_1b354;
L_1b354: /* cmpi.b #$73, d1; CCR mask 4 */
   v=0x73u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b358;
L_1b358: /* beq.b $1b392; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b392;}
   goto L_1b35a;
L_1b35a: /* bra.w $1b444; CCR mask 0 */
   if((1)){goto L_1b444;}
   goto L_1b35e;
L_1b35e: /* cmpi.b #$78, d1; CCR mask 4 */
   v=0x78u;
   u=r[1];
   v=np_alu(r,u,v,8,1,1,4u);
   goto L_1b362;
L_1b362: /* beq.w $1b3fc; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b3fc;}
   goto L_1b366;
L_1b366: /* bra.w $1b444; CCR mask 0 */
   if((1)){goto L_1b444;}
   goto L_1b36a;
L_1b36a: /* move.w d3, -(a7); CCR mask 0 */
   v=r[3];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b36c;
L_1b36c: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b370;
L_1b370: /* move.w #$25, -(a7); CCR mask 0 */
   v=0x25u;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b374;
L_1b374: /* bra.b $1b37e; CCR mask 0 */
   if((1)){goto L_1b37e;}
   goto L_1b376;
L_1b376: /* move.w d3, -(a7); CCR mask 0 */
   v=r[3];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b378;
L_1b378: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b37c;
L_1b37c: /* move.w (a3)+, -(a7); CCR mask 0 */
   v=PR16(r[11]);r[11]+=2;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b37e;
L_1b37e: /* move.l a2, -(a7); CCR mask 15 */
   v=r[10];
   np_push_width(r,v,4);
   np_logic(r,v,32,15u);
   goto L_1b380;
L_1b380: /* jsr $1b160.l; CCR mask 16 */
 np_push_width(r,0x1b386u,4);
 biwn_native_format_pad_body(r);
 (void)PR32(r[15]);r[15]+=4;
 goto L_1b386;
L_1b386: /* movea.w d0, a0; CCR mask 0 */
   v=r[0];
   r[8]=sx16((uint16_t)v);
   goto L_1b388;
L_1b388: /* adda.l a0, a2; CCR mask 0 */
   v=r[8];
   r[10]+=v;
   goto L_1b38a;
L_1b38a: /* adda.w #$c, a7; CCR mask 0 */
   v=0xcu;
   r[15]+=sx16((uint16_t)v);
   goto L_1b38e;
L_1b38e: /* bra.w $1b444; CCR mask 0 */
   if((1)){goto L_1b444;}
   goto L_1b392;
L_1b392: /* move.w d3, -(a7); CCR mask 0 */
   v=r[3];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b394;
L_1b394: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b398;
L_1b398: /* move.l (a3)+, -(a7); CCR mask 0 */
   v=PR32(r[11]);r[11]+=4;
   np_push_width(r,v,4);
   np_logic(r,v,32,0u);
   goto L_1b39a;
L_1b39a: /* move.l a2, -(a7); CCR mask 15 */
   v=r[10];
   np_push_width(r,v,4);
   np_logic(r,v,32,15u);
   goto L_1b39c;
L_1b39c: /* jsr $1b1a8.l; CCR mask 16 */
 np_push_width(r,0x1b3a2u,4);
 biwn_native_format_string_body(r);
 (void)PR32(r[15]);r[15]+=4;
 goto L_1b3a2;
L_1b3a2: /* movea.w d0, a0; CCR mask 0 */
   v=r[0];
   r[8]=sx16((uint16_t)v);
   goto L_1b3a4;
L_1b3a4: /* adda.l a0, a2; CCR mask 0 */
   v=r[8];
   r[10]+=v;
   goto L_1b3a6;
L_1b3a6: /* adda.w #$e, a7; CCR mask 0 */
   v=0xeu;
   r[15]+=sx16((uint16_t)v);
   goto L_1b3aa;
L_1b3aa: /* bra.w $1b444; CCR mask 0 */
   if((1)){goto L_1b444;}
   goto L_1b3ae;
L_1b3ae: /* tst.w d2; CCR mask 4 */
   v=r[2];
   np_logic(r,v,16,4u);
   goto L_1b3b0;
L_1b3b0: /* beq.b $1b3b6; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b3b6;}
   goto L_1b3b2;
L_1b3b2: /* move.l (a3)+, d2; CCR mask 0 */
   v=PR32(r[11]);r[11]+=4;
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b3b4;
L_1b3b4: /* bra.b $1b3ba; CCR mask 0 */
   if((1)){goto L_1b3ba;}
   goto L_1b3b6;
L_1b3b6: /* move.w (a3)+, d2; CCR mask 0 */
   v=PR16(r[11]);r[11]+=2;
   np_put(r,2,2,v);
   np_logic(r,v,16,0u);
   goto L_1b3b8;
L_1b3b8: /* ext.l d2; CCR mask 0 */
   v=sx16((uint16_t)r[2]);
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b3ba;
L_1b3ba: /* tst.l d2; CCR mask 10 */
   v=r[2];
   np_logic(r,v,32,10u);
   goto L_1b3bc;
L_1b3bc: /* bge.b $1b424; CCR mask 0 */
   if((!(((r[16]>>3)^(r[16]>>1))&1u))){goto L_1b424;}
   goto L_1b3be;
L_1b3be: /* move.w #$1, -(a7); CCR mask 0 */
   v=0x1u;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b3c2;
L_1b3c2: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b3c6;
L_1b3c6: /* move.w #$2d, -(a7); CCR mask 0 */
   v=0x2du;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b3ca;
L_1b3ca: /* move.l a2, -(a7); CCR mask 15 */
   v=r[10];
   np_push_width(r,v,4);
   np_logic(r,v,32,15u);
   goto L_1b3cc;
L_1b3cc: /* jsr $1b160.l; CCR mask 0 */
 np_push_width(r,0x1b3d2u,4);
 biwn_native_format_pad_body(r);
 (void)PR32(r[15]);r[15]+=4;
 goto L_1b3d2;
L_1b3d2: /* movea.w d0, a0; CCR mask 0 */
   v=r[0];
   r[8]=sx16((uint16_t)v);
   goto L_1b3d4;
L_1b3d4: /* adda.l a0, a2; CCR mask 0 */
   v=r[8];
   r[10]+=v;
   goto L_1b3d6;
L_1b3d6: /* subq.w #$1, d3; CCR mask 0 */
   v=0x1u;
   u=r[3];
   v=np_alu(r,u,v,16,1,0,0u);
   np_put(r,3,2,v);
   goto L_1b3d8;
L_1b3d8: /* neg.l d2; CCR mask 16 */
   v=r[2];
   v=np_alu(r,0,v,32,1,0,16u);
   np_put(r,2,4,v);
   goto L_1b3da;
L_1b3da: /* adda.w #$c, a7; CCR mask 0 */
   v=0xcu;
   r[15]+=sx16((uint16_t)v);
   goto L_1b3de;
L_1b3de: /* bra.b $1b424; CCR mask 0 */
   if((1)){goto L_1b424;}
   goto L_1b3e0;
L_1b3e0: /* tst.w d2; CCR mask 4 */
   v=r[2];
   np_logic(r,v,16,4u);
   goto L_1b3e2;
L_1b3e2: /* beq.b $1b3e8; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b3e8;}
   goto L_1b3e4;
L_1b3e4: /* move.l (a3)+, d2; CCR mask 0 */
   v=PR32(r[11]);r[11]+=4;
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b3e6;
L_1b3e6: /* bra.b $1b3ec; CCR mask 0 */
   if((1)){goto L_1b3ec;}
   goto L_1b3e8;
L_1b3e8: /* moveq #$0, d2; CCR mask 0 */
   v=sx8(0x0u);r[2]=v;np_logic(r,v,32,0u);
   goto L_1b3ea;
L_1b3ea: /* move.w (a3)+, d2; CCR mask 0 */
   v=PR16(r[11]);r[11]+=2;
   np_put(r,2,2,v);
   np_logic(r,v,16,0u);
   goto L_1b3ec;
L_1b3ec: /* ext.w d4; CCR mask 0 */
   v=sx8((uint8_t)r[4]);
   np_put(r,4,2,v);
   np_logic(r,v,16,0u);
   goto L_1b3ee;
L_1b3ee: /* move.w d4, -(a7); CCR mask 0 */
   v=r[4];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b3f0;
L_1b3f0: /* move.w d3, -(a7); CCR mask 0 */
   v=r[3];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b3f2;
L_1b3f2: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b3f6;
L_1b3f6: /* move.w #$8, -(a7); CCR mask 0 */
   v=0x8u;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b3fa;
L_1b3fa: /* bra.b $1b432; CCR mask 0 */
   if((1)){goto L_1b432;}
   goto L_1b3fc;
L_1b3fc: /* tst.w d2; CCR mask 4 */
   v=r[2];
   np_logic(r,v,16,4u);
   goto L_1b3fe;
L_1b3fe: /* beq.b $1b404; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b404;}
   goto L_1b400;
L_1b400: /* move.l (a3)+, d2; CCR mask 0 */
   v=PR32(r[11]);r[11]+=4;
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b402;
L_1b402: /* bra.b $1b408; CCR mask 0 */
   if((1)){goto L_1b408;}
   goto L_1b404;
L_1b404: /* moveq #$0, d2; CCR mask 0 */
   v=sx8(0x0u);r[2]=v;np_logic(r,v,32,0u);
   goto L_1b406;
L_1b406: /* move.w (a3)+, d2; CCR mask 0 */
   v=PR16(r[11]);r[11]+=2;
   np_put(r,2,2,v);
   np_logic(r,v,16,0u);
   goto L_1b408;
L_1b408: /* ext.w d4; CCR mask 0 */
   v=sx8((uint8_t)r[4]);
   np_put(r,4,2,v);
   np_logic(r,v,16,0u);
   goto L_1b40a;
L_1b40a: /* move.w d4, -(a7); CCR mask 0 */
   v=r[4];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b40c;
L_1b40c: /* move.w d3, -(a7); CCR mask 0 */
   v=r[3];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b40e;
L_1b40e: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b412;
L_1b412: /* move.w #$10, -(a7); CCR mask 0 */
   v=0x10u;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b416;
L_1b416: /* bra.b $1b432; CCR mask 0 */
   if((1)){goto L_1b432;}
   goto L_1b418;
L_1b418: /* tst.w d2; CCR mask 4 */
   v=r[2];
   np_logic(r,v,16,4u);
   goto L_1b41a;
L_1b41a: /* beq.b $1b420; CCR mask 0 */
   if(((r[16]&4u)!=0)){goto L_1b420;}
   goto L_1b41c;
L_1b41c: /* move.l (a3)+, d2; CCR mask 0 */
   v=PR32(r[11]);r[11]+=4;
   np_put(r,2,4,v);
   np_logic(r,v,32,0u);
   goto L_1b41e;
L_1b41e: /* bra.b $1b424; CCR mask 0 */
   if((1)){goto L_1b424;}
   goto L_1b420;
L_1b420: /* moveq #$0, d2; CCR mask 0 */
   v=sx8(0x0u);r[2]=v;np_logic(r,v,32,0u);
   goto L_1b422;
L_1b422: /* move.w (a3)+, d2; CCR mask 0 */
   v=PR16(r[11]);r[11]+=2;
   np_put(r,2,2,v);
   np_logic(r,v,16,0u);
   goto L_1b424;
L_1b424: /* ext.w d4; CCR mask 0 */
   v=sx8((uint8_t)r[4]);
   np_put(r,4,2,v);
   np_logic(r,v,16,0u);
   goto L_1b426;
L_1b426: /* move.w d4, -(a7); CCR mask 0 */
   v=r[4];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b428;
L_1b428: /* move.w d3, -(a7); CCR mask 0 */
   v=r[3];
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b42a;
L_1b42a: /* pea.l -$2(a6); CCR mask 0 */
   np_push_width(r,((r[14])-0x2u),4);
   goto L_1b42e;
L_1b42e: /* move.w #$a, -(a7); CCR mask 0 */
   v=0xau;
   np_push_width(r,v,2);
   np_logic(r,v,16,0u);
   goto L_1b432;
L_1b432: /* move.l d2, -(a7); CCR mask 0 */
   v=r[2];
   np_push_width(r,v,4);
   np_logic(r,v,32,0u);
   goto L_1b434;
L_1b434: /* move.l a2, -(a7); CCR mask 15 */
   v=r[10];
   np_push_width(r,v,4);
   np_logic(r,v,32,15u);
   goto L_1b436;
L_1b436: /* jsr $1b212.l; CCR mask 16 */
 np_push_width(r,0x1b43cu,4);
 biwn_native_format_number_body(r);
 (void)PR32(r[15]);r[15]+=4;
 goto L_1b43c;
L_1b43c: /* movea.w d0, a0; CCR mask 0 */
   v=r[0];
   r[8]=sx16((uint16_t)v);
   goto L_1b43e;
L_1b43e: /* adda.l a0, a2; CCR mask 0 */
   v=r[8];
   r[10]+=v;
   goto L_1b440;
L_1b440: /* adda.w #$12, a7; CCR mask 0 */
   v=0x12u;
   r[15]+=sx16((uint16_t)v);
   goto L_1b444;
L_1b444: /* move.b (a4)+, d1; CCR mask 4 */
   v=PR8(r[12]);r[12]+=1;
   np_put(r,1,1,v);
   np_logic(r,v,8,4u);
   goto L_1b446;
L_1b446: /* bne.w $1b2c2; CCR mask 0 */
   if(((r[16]&4u)==0)){goto L_1b2c2;}
   goto L_1b44a;
L_1b44a: /* clr.b (a2); CCR mask 0 */
   v=0;
   PW8((r[10]),v);
   np_logic(r,0,8,0u);
   goto L_1b44c;
L_1b44c: /* move.w a2, d0; CCR mask 0 */
   v=r[10];
   np_put(r,0,2,v);
   np_logic(r,v,16,0u);
   goto L_1b44e;
L_1b44e: /* sub.w d6, d0; CCR mask 31 */
   v=r[6];
   u=r[0];
   v=np_alu(r,u,v,16,1,0,31u);
   np_put(r,0,2,v);
   goto L_1b450;
L_1b450: /* movem.l -$24(a6), d2-d6/a2-a4; CCR mask 0 */
   u=((r[14])-0x24u);
   v=PR32(u);r[2]=v;u+=4u;
   v=PR32(u);r[3]=v;u+=4u;
   v=PR32(u);r[4]=v;u+=4u;
   v=PR32(u);r[5]=v;u+=4u;
   v=PR32(u);r[6]=v;u+=4u;
   v=PR32(u);r[10]=v;u+=4u;
   v=PR32(u);r[11]=v;u+=4u;
   v=PR32(u);r[12]=v;u+=4u;
   goto L_1b456;
L_1b456: /* unlk a6; CCR mask 0 */
   r[15]=r[14];v=PR32(r[15]);r[14]=v;r[15]+=4;
   goto L_1b458;
L_1b458: /* rts; CCR mask 0 */
 return;
}
void biwn_native_format_variadic_body(uint32_t *r){
 uint32_t v;
 goto L_1b45a;
L_1b45a: /* link.w a6, #$0; CCR mask 0 */
   np_push_width(r,r[14],4);r[14]=r[15];r[15]+=sx16(0x0u);
   goto L_1b45e;
L_1b45e: /* pea.l $10(a6); CCR mask 0 */
   np_push_width(r,(r[14]+0x10u),4);
   goto L_1b462;
L_1b462: /* move.l $c(a6), -(a7); CCR mask 0 */
   v=PR32((r[14]+0xcu));
   np_push_width(r,v,4);
   np_logic(r,v,32,0u);
   goto L_1b466;
L_1b466: /* move.l $8(a6), -(a7); CCR mask 15 */
   v=PR32((r[14]+0x8u));
   np_push_width(r,v,4);
   np_logic(r,v,32,15u);
   goto L_1b46a;
L_1b46a: /* jsr $1b29c.l; CCR mask 31 */
 np_push_width(r,0x1b470u,4);
 biwn_native_format_core_body(r);
 (void)PR32(r[15]);r[15]+=4;
 goto L_1b470;
L_1b470: /* adda.w #$c, a7; CCR mask 0 */
   v=0xcu;
   r[15]+=sx16((uint16_t)v);
   goto L_1b474;
L_1b474: /* unlk a6; CCR mask 0 */
   r[15]=r[14];v=PR32(r[15]);r[14]=v;r[15]+=4;
   goto L_1b476;
L_1b476: /* rts; CCR mask 0 */
 return;
}
