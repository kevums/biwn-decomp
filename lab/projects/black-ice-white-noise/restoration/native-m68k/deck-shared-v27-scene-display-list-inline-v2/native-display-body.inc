/* Native adaptation: two actual memory CLR operations retain M68000 dummy reads. */
/* Structured three-pass185B2..18852 from checked static instruction semantics.
 * Original guest LINK/MOVEM/private table and source jump-table reads retained.
 * Normal completed calls only. Host work limits are not target deadlines.
 * This is restructuring of an already recovered routine, not new original source. */
static void scene_display_list_body(struct biwn_deck_context *s){
 uint32_t v,u,jump;
 if(s->error)return;
 SCENE_DISPLAY_BEGIN(s);
 DL_WORK();
 /* 0x185b2 link.w a6, #$fff0 */
 DL_CHECK(dl_push(s,s->cpu.registers[14],4));s->cpu.registers[14]=s->cpu.registers[15];s->cpu.registers[15]+=dl_sx16(0xfff0u);dl_bank(s);
 /* 0x185b6 movem.l d2-d7/a2-a5, -(a7) */
 DL_CHECK(dl_push(s,s->cpu.registers[13],4));
 DL_CHECK(dl_push(s,s->cpu.registers[12],4));
 DL_CHECK(dl_push(s,s->cpu.registers[11],4));
 DL_CHECK(dl_push(s,s->cpu.registers[10],4));
 DL_CHECK(dl_push(s,s->cpu.registers[7],4));
 DL_CHECK(dl_push(s,s->cpu.registers[6],4));
 DL_CHECK(dl_push(s,s->cpu.registers[5],4));
 DL_CHECK(dl_push(s,s->cpu.registers[4],4));
 DL_CHECK(dl_push(s,s->cpu.registers[3],4));
 DL_CHECK(dl_push(s,s->cpu.registers[2],4));
 /* 0x185ba movea.l $8(a6), a3 */
 DL_CHECK(dl_read_value(s,(s->cpu.registers[14]+0x8u),4,&v));
 s->cpu.registers[11]=v;
 /* 0x185be movea.l $c(a6), a0 */
 DL_CHECK(dl_read_value(s,(s->cpu.registers[14]+0xcu),4,&v));
 s->cpu.registers[8]=v;
 /* 0x185c2 moveq #$1, d2 */
 v=dl_sx8(0x1u);s->cpu.registers[2]=v;dl_nz(s,v,32);
 /* 0x185c4 movea.l a3, a1 */
 v=s->cpu.registers[11];
 s->cpu.registers[9]=v;
 /* 0x185c6 cmpi.w #$4, (a3) */
 v=0x4u;
 DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&u));
 v=dl_alu(s,u,v,16,1,1);
 /* Pass1: count records, including the terminating type4. */
 while(!(s->cpu.sr&4u)){
  DL_WORK();
  /* 0x185cc addq.l #$1, d2 */
  v=0x1u;
  u=s->cpu.registers[2];
  v=dl_alu(s,u,v,32,0,0);
  dl_put(s,2,4,v);
  /* 0x185ce adda.w #$24, a1 */
  v=0x24u;
  s->cpu.registers[9]+=dl_sx16((uint16_t)v);dl_bank(s);
  /* 0x185d2 cmpi.w #$4, (a1) */
  v=0x4u;
  DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),2,&u));
  v=dl_alu(s,u,v,16,1,1);
 }
 /* 0x185d8 move.l d2, d0 */
 v=s->cpu.registers[2];
 dl_put(s,0,4,v);
 dl_nz(s,v,32);
 /* 0x185da asl.l #$2, d0 */
 u=0x2u;
 dl_shift(s,0,32,u&63u,1);
 /* 0x185dc suba.l d0, a7 */
 v=s->cpu.registers[0];
 s->cpu.registers[15]-=v;dl_bank(s);
 /* 0x185de move.l a7, -$4(a6) */
 v=s->cpu.registers[15];
 DL_CHECK(dl_write_value(s,((s->cpu.registers[14])-0x4u),4,v));
 dl_nz(s,v,32);
 /* 0x185e2 move.l #$776f0, d4 */
 v=0x776f0u;
 dl_put(s,4,4,v);
 dl_nz(s,v,32);
 /* 0x185e8 move.l d4, d0 */
 v=s->cpu.registers[4];
 dl_put(s,0,4,v);
 dl_nz(s,v,32);
 if(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u){
  /* 0x185ec move.l #$776f7, d0 */
  v=0x776f7u;
  dl_put(s,0,4,v);
  dl_nz(s,v,32);
 }
 /* 0x185f2 move.l d0, d4 */
 v=s->cpu.registers[0];
 dl_put(s,4,4,v);
 dl_nz(s,v,32);
 /* 0x185f4 asr.l #$3, d4 */
 u=0x3u;
 dl_shift(s,4,32,u&63u,0);
 /* 0x185f6 clr.w d6 */
 v=0;
 dl_put(s,6,2,v);
 dl_nz(s,0,16);
 /* 0x185f8 movea.l a3, a1 */
 v=s->cpu.registers[11];
 s->cpu.registers[9]=v;
 /* 0x185fa movea.l a7, a2 */
 v=s->cpu.registers[15];
 s->cpu.registers[10]=v;
 /* Pass2: build the original dynamically sized guest-stack link table. */
 do{
  DL_WORK();
  /* 0x185fc move.w (a1), d0 */
  DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),2,&v));
  dl_put(s,0,2,v);
  dl_nz(s,v,16);
  /* 0x185fe cmpi.w #$1, d0 */
  v=0x1u;
  u=s->cpu.registers[0];
  v=dl_alu(s,u,v,16,1,1);
  if(s->cpu.sr&4u){
   /* 0x1861a move.l d4, d0 */
   v=s->cpu.registers[4];
   dl_put(s,0,4,v);
   dl_nz(s,v,32);
   /* 0x1861c addq.l #$3, d0 */
   v=0x3u;
   u=s->cpu.registers[0];
   v=dl_alu(s,u,v,32,0,0);
   dl_put(s,0,4,v);
   /* 0x1861e moveq #$fc, d4 */
   v=dl_sx8(0xfcu);s->cpu.registers[4]=v;dl_nz(s,v,32);
   /* 0x18620 and.l d0, d4 */
   v=s->cpu.registers[0];
   u=s->cpu.registers[4];
   v=u&v;
   dl_put(s,4,4,v);
   dl_nz(s,v,32);
   /* 0x18622 moveq #$3, d2 */
   v=dl_sx8(0x3u);s->cpu.registers[2]=v;dl_nz(s,v,32);
  }else if(s->cpu.sr&1u){
   /* 0x1860e move.l d4, d0 */
   v=s->cpu.registers[4];
   dl_put(s,0,4,v);
   dl_nz(s,v,32);
   /* 0x18610 addq.l #$1, d0 */
   v=0x1u;
   u=s->cpu.registers[0];
   v=dl_alu(s,u,v,32,0,0);
   dl_put(s,0,4,v);
   /* 0x18612 moveq #$fe, d4 */
   v=dl_sx8(0xfeu);s->cpu.registers[4]=v;dl_nz(s,v,32);
   /* 0x18614 and.l d0, d4 */
   v=s->cpu.registers[0];
   u=s->cpu.registers[4];
   v=u&v;
   dl_put(s,4,4,v);
   dl_nz(s,v,32);
   /* 0x18616 moveq #$2, d2 */
   v=dl_sx8(0x2u);s->cpu.registers[2]=v;dl_nz(s,v,32);
  }else{
   /* 0x18606 cmpi.w #$4, d0 */
   v=0x4u;
   u=s->cpu.registers[0];
   v=dl_alu(s,u,v,16,1,1);
   if(s->cpu.sr&4u){
    /* 0x18626 moveq #$1, d6 */
    v=dl_sx8(0x1u);s->cpu.registers[6]=v;dl_nz(s,v,32);
   }
   /* 0x18628 moveq #$1, d2 */
   v=dl_sx8(0x1u);s->cpu.registers[2]=v;dl_nz(s,v,32);
  }
  /* 0x1862a move.l d4, (a2)+ */
  v=s->cpu.registers[4];
  DL_CHECK(dl_write_value(s,s->cpu.registers[10],4,v));s->cpu.registers[10]+=4;dl_bank(s);
  dl_nz(s,v,32);
  /* 0x1862c add.l d2, d4 */
  v=s->cpu.registers[2];
  u=s->cpu.registers[4];
  v=dl_alu(s,u,v,32,0,0);
  dl_put(s,4,4,v);
  /* 0x1862e adda.w #$24, a1 */
  v=0x24u;
  s->cpu.registers[9]+=dl_sx16((uint16_t)v);dl_bank(s);
  /* 0x18632 tst.w d6 */
  v=s->cpu.registers[6];
  dl_nz(s,v,16);
 }while(s->cpu.sr&4u);
 /* 0x18636 clr.w d6 */
 v=0;
 dl_put(s,6,2,v);
 dl_nz(s,0,16);
 /* 0x18638 move.l #$776f0, d4 */
 v=0x776f0u;
 dl_put(s,4,4,v);
 dl_nz(s,v,32);
 /* 0x1863e move.l d4, d0 */
 v=s->cpu.registers[4];
 dl_put(s,0,4,v);
 dl_nz(s,v,32);
 if(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u){
  /* 0x18642 move.l #$776f7, d0 */
  v=0x776f7u;
  dl_put(s,0,4,v);
  dl_nz(s,v,32);
 }
 /* 0x18648 move.l d0, d4 */
 v=s->cpu.registers[0];
 dl_put(s,4,4,v);
 dl_nz(s,v,32);
 /* 0x1864a asr.l #$3, d4 */
 u=0x3u;
 dl_shift(s,4,32,u&63u,0);
 /* 0x1864c clr.l -$8(a6) */
 v=0;
 DL_CHECK(native_display_clr_long(s,(s->cpu.registers[14])-0x8u));
 dl_nz(s,0,32);
 /* 0x18650 move.l -$4(a6), -$c(a6) */
 DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0x4u),4,&v));
 DL_CHECK(dl_write_value(s,((s->cpu.registers[14])-0xcu),4,v));
 dl_nz(s,v,32);
 /* 0x18656 lea.l $4(a3), a2 */
 s->cpu.registers[10]=(s->cpu.registers[11]+0x4u);
 /* 0x1865a lea.l $a(a3), a4 */
 s->cpu.registers[12]=(s->cpu.registers[11]+0xau);
 /* 0x1865e lea.l $6(a3), a1 */
 s->cpu.registers[9]=(s->cpu.registers[11]+0x6u);
 /* 0x18662 move.l a3, d5 */
 v=s->cpu.registers[11];
 dl_put(s,5,4,v);
 dl_nz(s,v,32);
 /* 0x18664 addq.l #$2, d5 */
 v=0x2u;
 u=s->cpu.registers[5];
 v=dl_alu(s,u,v,32,0,0);
 dl_put(s,5,4,v);
 /* 0x18666 lea.l $12(a3), a5 */
 s->cpu.registers[13]=(s->cpu.registers[11]+0x12u);
 /* 0x1866a move.l a5, -$10(a6) */
 v=s->cpu.registers[13];
 DL_CHECK(dl_write_value(s,((s->cpu.registers[14])-0x10u),4,v));
 dl_nz(s,v,32);
 /* Pass3: reread records and pack phrases. The switch follows the actual source table. */
 do{
  DL_WORK();
  /* 0x1866e movea.l -$c(a6), a5 */
  DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0xcu),4,&v));
  s->cpu.registers[13]=v;
  /* 0x18672 move.l $4(a5), d1 */
  DL_CHECK(dl_read_value(s,(s->cpu.registers[13]+0x4u),4,&v));
  dl_put(s,1,4,v);
  dl_nz(s,v,32);
  /* 0x18676 cmpi.w #$4, (a3) */
  v=0x4u;
  DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&u));
  v=dl_alu(s,u,v,16,1,1);
  if((s->cpu.sr&5u)!=0){
   /* 0x1867e move.w (a3), -$6(a6) */
   DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&v));
   DL_CHECK(dl_write_value(s,((s->cpu.registers[14])-0x6u),2,v));
   dl_nz(s,v,16);
   /* 0x18682 move.l -$8(a6), d0 */
   DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0x8u),4,&v));
   dl_put(s,0,4,v);
   dl_nz(s,v,32);
   /* 0x18686 add.l d0, d0 */
   v=s->cpu.registers[0];
   u=s->cpu.registers[0];
   v=dl_alu(s,u,v,32,0,0);
   dl_put(s,0,4,v);
   /* 0x18688 move.w $18690(pc, d0.l), d0 */
   DL_CHECK(dl_read_value(s,(0x18690u+s->cpu.registers[0]),2,&v));
   dl_put(s,0,2,v);
   dl_nz(s,v,16);
   jump=0x18690u+dl_sx16((uint16_t)s->cpu.registers[0]);
   switch(jump){
   case 0x1869a: /* ordinary bitmap */
    /* 0x1869a moveq #$1, d2 */
    v=dl_sx8(0x1u);s->cpu.registers[2]=v;dl_nz(s,v,32);
    goto bitmap;
   case 0x1869e: /* scaled bitmap */
    /* 0x1869e moveq #$3, d2 */
    v=dl_sx8(0x3u);s->cpu.registers[2]=v;dl_nz(s,v,32);
   bitmap:
    /* Phrase-alignment padding, including original register effects. */
    /* 0x186c4 move.l d4, d0 */
    v=s->cpu.registers[4];
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x186c6 and.l d2, d0 */
    v=s->cpu.registers[2];
    u=s->cpu.registers[0];
    v=u&v;
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    while(!(s->cpu.sr&4u)){
     DL_WORK();
     /* 0x186a2 addq.l #$1, d4 */
     v=0x1u;
     u=s->cpu.registers[4];
     v=dl_alu(s,u,v,32,0,0);
     dl_put(s,4,4,v);
     /* 0x186a4 move.l d4, d0 */
     v=s->cpu.registers[4];
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
     /* 0x186a6 andi.l #$7ff00, d0 */
     v=0x7ff00u;
     u=s->cpu.registers[0];
     v=u&v;
     dl_nz(s,v,32);
     dl_put(s,0,4,v);
     /* 0x186ac asr.l #$8, d0 */
     u=0x8u;
     dl_shift(s,0,32,u&63u,0);
     /* 0x186ae move.l d0, (a0)+ */
     v=s->cpu.registers[0];
     DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
     dl_nz(s,v,32);
     /* 0x186b0 move.l d4, d0 */
     v=s->cpu.registers[4];
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
     /* 0x186b2 andi.l #$ff, d0 */
     v=0xffu;
     u=s->cpu.registers[0];
     v=u&v;
     dl_nz(s,v,32);
     dl_put(s,0,4,v);
     /* 0x186b8 asl.w #$8, d0 */
     u=0x8u;
     dl_shift(s,0,16,u&63u,1);
     /* 0x186ba swap d0 */
     v=s->cpu.registers[0];v=(v<<16)|(v>>16);s->cpu.registers[0]=v;dl_nz(s,v,32);
     /* 0x186bc clr.w d0 */
     v=0;
     dl_put(s,0,2,v);
     dl_nz(s,0,16);
     /* 0x186be moveq #$3, d7 */
     v=dl_sx8(0x3u);s->cpu.registers[7]=v;dl_nz(s,v,32);
     /* 0x186c0 or.l d0, d7 */
     v=s->cpu.registers[0];
     u=s->cpu.registers[7];
     v=u|v;
     dl_put(s,7,4,v);
     dl_nz(s,v,32);
     /* 0x186c2 move.l d7, (a0)+ */
     v=s->cpu.registers[7];
     DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
     dl_nz(s,v,32);
     /* 0x186c4 move.l d4, d0 */
     v=s->cpu.registers[4];
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
     /* 0x186c6 and.l d2, d0 */
     v=s->cpu.registers[2];
     u=s->cpu.registers[0];
     v=u&v;
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
    }
    /* 0x186ca tst.l (a1) */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),4,&v));
    dl_nz(s,v,32);
    if(!(s->cpu.sr&4u)){
     /* 0x186ce move.l (a1), d0 */
     DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),4,&v));
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
     /* 0x186d0 asl.l #$2, d0 */
     u=0x2u;
     dl_shift(s,0,32,u&63u,1);
     /* 0x186d2 movea.l -$4(a6), a5 */
     DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0x4u),4,&v));
     s->cpu.registers[13]=v;
     /* 0x186d6 move.l -$4(a5, d0.l), d1 */
     DL_CHECK(dl_read_value(s,((s->cpu.registers[13]+s->cpu.registers[0])-0x4u),4,&v));
     dl_put(s,1,4,v);
     dl_nz(s,v,32);
    }
    /* 0x186da move.l (a4), d3 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[12]),4,&v));
    dl_put(s,3,4,v);
    dl_nz(s,v,32);
    /* 0x186dc andi.l #$fffff8, d3 */
    v=0xfffff8u;
    u=s->cpu.registers[3];
    v=u&v;
    dl_nz(s,v,32);
    dl_put(s,3,4,v);
    /* 0x186e2 asl.l #$8, d3 */
    u=0x8u;
    dl_shift(s,3,32,u&63u,1);
    /* 0x186e4 move.l d1, d2 */
    v=s->cpu.registers[1];
    dl_put(s,2,4,v);
    dl_nz(s,v,32);
    /* 0x186e6 andi.l #$7ff00, d2 */
    v=0x7ff00u;
    u=s->cpu.registers[2];
    v=u&v;
    dl_nz(s,v,32);
    dl_put(s,2,4,v);
    /* 0x186ec asr.l #$8, d2 */
    u=0x8u;
    dl_shift(s,2,32,u&63u,0);
    /* 0x186ee andi.l #$ff, d1 */
    v=0xffu;
    u=s->cpu.registers[1];
    v=u&v;
    dl_nz(s,v,32);
    dl_put(s,1,4,v);
    /* 0x186f4 asl.w #$8, d1 */
    u=0x8u;
    dl_shift(s,1,16,u&63u,1);
    /* 0x186f6 swap d1 */
    v=s->cpu.registers[1];v=(v<<16)|(v>>16);s->cpu.registers[1]=v;dl_nz(s,v,32);
    /* 0x186f8 clr.w d1 */
    v=0;
    dl_put(s,1,2,v);
    dl_nz(s,0,16);
    /* 0x186fa clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x186fc move.w $e(a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0xeu),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x18700 moveq #$e, d7 */
    v=dl_sx8(0xeu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x18702 asl.l d7, d0 */
    u=s->cpu.registers[7];
    dl_shift(s,0,32,u&63u,1);
    /* 0x18704 or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18706 clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x18708 move.w (a2), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[10]),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x1870a asl.l #$3, d0 */
    u=0x3u;
    dl_shift(s,0,32,u&63u,1);
    /* 0x1870c or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x1870e clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x18710 move.w (a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x18712 or.l d2, d3 */
    v=s->cpu.registers[2];
    u=s->cpu.registers[3];
    v=u|v;
    dl_put(s,3,4,v);
    dl_nz(s,v,32);
    /* 0x18714 move.l d3, (a0)+ */
    v=s->cpu.registers[3];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x18716 or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18718 move.l d1, (a0)+ */
    v=s->cpu.registers[1];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x1871a move.w $1c(a3), d3 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x1cu),2,&v));
    dl_put(s,3,2,v);
    dl_nz(s,v,16);
    /* 0x1871e asl.w #$1, d3 */
    u=0x1u;
    dl_shift(s,3,16,u&63u,1);
    /* 0x18720 swap d3 */
    v=s->cpu.registers[3];v=(v<<16)|(v>>16);s->cpu.registers[3]=v;dl_nz(s,v,32);
    /* 0x18722 clr.w d3 */
    v=0;
    dl_put(s,3,2,v);
    dl_nz(s,0,16);
    /* 0x18724 clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x18726 move.w $1a(a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x1au),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x1872a moveq #$d, d7 */
    v=dl_sx8(0xdu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x1872c asl.l d7, d0 */
    u=s->cpu.registers[7];
    dl_shift(s,0,32,u&63u,1);
    /* 0x1872e or.l d0, d3 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[3];
    v=u|v;
    dl_put(s,3,4,v);
    dl_nz(s,v,32);
    /* 0x18730 clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x18732 move.w $18(a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x18u),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x18736 asl.l #$6, d0 */
    u=0x6u;
    dl_shift(s,0,32,u&63u,1);
    /* 0x18738 or.l d0, d3 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[3];
    v=u|v;
    dl_put(s,3,4,v);
    dl_nz(s,v,32);
    /* 0x1873a movea.l -$10(a6), a5 */
    DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0x10u),4,&v));
    s->cpu.registers[13]=v;
    /* 0x1873e move.w (a5), d2 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[13]),2,&v));
    dl_put(s,2,2,v);
    dl_nz(s,v,16);
    /* 0x18740 andi.w #$3f0, d2 */
    v=0x3f0u;
    u=s->cpu.registers[2];
    v=u&v;
    dl_nz(s,v,16);
    dl_put(s,2,2,v);
    /* 0x18744 lsr.w #$4, d2 */
    v=s->cpu.registers[2]&0xffffu;u=(v>>3)&1u;v>>=4;dl_put(s,2,2,v);dl_nz(s,v,16);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(u?0x11u:0));
    /* 0x18746 moveq #$3f, d7 */
    v=dl_sx8(0x3fu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x18748 and.l d7, d2 */
    v=s->cpu.registers[7];
    u=s->cpu.registers[2];
    v=u&v;
    dl_put(s,2,4,v);
    dl_nz(s,v,32);
    /* 0x1874a move.w (a5), d1 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[13]),2,&v));
    dl_put(s,1,2,v);
    dl_nz(s,v,16);
    /* 0x1874c moveq #$1c, d7 */
    v=dl_sx8(0x1cu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x1874e asl.l d7, d1 */
    u=s->cpu.registers[7];
    dl_shift(s,1,32,u&63u,1);
    /* 0x18750 move.w $10(a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x10u),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x18754 asl.w #$2, d0 */
    u=0x2u;
    dl_shift(s,0,16,u&63u,1);
    /* 0x18756 swap d0 */
    v=s->cpu.registers[0];v=(v<<16)|(v>>16);s->cpu.registers[0]=v;dl_nz(s,v,32);
    /* 0x18758 clr.w d0 */
    v=0;
    dl_put(s,0,2,v);
    dl_nz(s,0,16);
    /* 0x1875a or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x1875c clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x1875e move.w $16(a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x16u),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x18762 moveq #$f, d7 */
    v=dl_sx8(0xfu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x18764 asl.l d7, d0 */
    u=s->cpu.registers[7];
    dl_shift(s,0,32,u&63u,1);
    /* 0x18766 or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18768 clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x1876a move.w $14(a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x14u),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x1876e moveq #$c, d7 */
    v=dl_sx8(0xcu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x18770 asl.l d7, d0 */
    u=s->cpu.registers[7];
    dl_shift(s,0,32,u&63u,1);
    /* 0x18772 or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18774 movea.l d5, a5 */
    v=s->cpu.registers[5];
    s->cpu.registers[13]=v;
    /* 0x18776 clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x18778 move.w (a5), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[13]),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x1877a or.l d2, d3 */
    v=s->cpu.registers[2];
    u=s->cpu.registers[3];
    v=u|v;
    dl_put(s,3,4,v);
    dl_nz(s,v,32);
    /* 0x1877c move.l d3, (a0)+ */
    v=s->cpu.registers[3];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x1877e or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18780 move.l d1, (a0)+ */
    v=s->cpu.registers[1];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x18782 addq.l #$2, d4 */
    v=0x2u;
    u=s->cpu.registers[4];
    v=dl_alu(s,u,v,32,0,0);
    dl_put(s,4,4,v);
    /* 0x18784 cmpi.w #$1, (a3) */
    v=0x1u;
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&u));
    v=dl_alu(s,u,v,16,1,1);
    if(s->cpu.sr&4u){
     /* 0x1878c move.w $22(a3), d0 */
     DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x22u),2,&v));
     dl_put(s,0,2,v);
     dl_nz(s,v,16);
     /* 0x18790 swap d0 */
     v=s->cpu.registers[0];v=(v<<16)|(v>>16);s->cpu.registers[0]=v;dl_nz(s,v,32);
     /* 0x18792 clr.w d0 */
     v=0;
     dl_put(s,0,2,v);
     dl_nz(s,0,16);
     /* 0x18794 clr.l d1 */
     v=0;
     dl_put(s,1,4,v);
     dl_nz(s,0,32);
     /* 0x18796 move.w $20(a3), d1 */
     DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x20u),2,&v));
     dl_put(s,1,2,v);
     dl_nz(s,v,16);
     /* 0x1879a asl.l #$8, d1 */
     u=0x8u;
     dl_shift(s,1,32,u&63u,1);
     /* 0x1879c or.l d1, d0 */
     v=s->cpu.registers[1];
     u=s->cpu.registers[0];
     v=u|v;
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
     /* 0x1879e clr.l d1 */
     v=0;
     dl_put(s,1,4,v);
     dl_nz(s,0,32);
     /* 0x187a0 move.w $1e(a3), d1 */
     DL_CHECK(dl_read_value(s,(s->cpu.registers[11]+0x1eu),2,&v));
     dl_put(s,1,2,v);
     dl_nz(s,v,16);
     /* 0x187a4 clr.l (a0)+ */
     v=0;
     DL_CHECK(native_display_clr_long(s,s->cpu.registers[8]));s->cpu.registers[8]+=4;dl_bank(s);
     dl_nz(s,0,32);
     /* 0x187bc or.l d1, d0 */
     v=s->cpu.registers[1];
     u=s->cpu.registers[0];
     v=u|v;
     dl_put(s,0,4,v);
     dl_nz(s,v,32);
     /* 0x187be move.l d0, (a0)+ */
     v=s->cpu.registers[0];
     DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
     dl_nz(s,v,32);
     /* 0x187c0 addq.l #$1, d4 */
     v=0x1u;
     u=s->cpu.registers[4];
     v=dl_alu(s,u,v,32,0,0);
     dl_put(s,4,4,v);
    }
    break;
   case 0x187a8: /* type2 GPU object */
    /* 0x187a8 move.l (a4), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[12]),4,&v));
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x187aa moveq #$e, d7 */
    v=dl_sx8(0xeu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x187ac asl.l d7, d0 */
    u=s->cpu.registers[7];
    dl_shift(s,0,32,u&63u,1);
    /* 0x187ae clr.l d1 */
    v=0;
    dl_put(s,1,4,v);
    dl_nz(s,0,32);
    /* 0x187b0 move.w (a2), d1 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[10]),2,&v));
    dl_put(s,1,2,v);
    dl_nz(s,v,16);
    /* 0x187b2 asl.l #$3, d1 */
    u=0x3u;
    dl_shift(s,1,32,u&63u,1);
    /* 0x187b4 or.l d1, d0 */
    v=s->cpu.registers[1];
    u=s->cpu.registers[0];
    v=u|v;
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x187b6 clr.l d1 */
    v=0;
    dl_put(s,1,4,v);
    dl_nz(s,0,32);
    /* 0x187b8 move.w (a3), d1 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&v));
    dl_put(s,1,2,v);
    dl_nz(s,v,16);
    /* 0x187ba move.l (a1), (a0)+ */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),4,&v));
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x187bc or.l d1, d0 */
    v=s->cpu.registers[1];
    u=s->cpu.registers[0];
    v=u|v;
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x187be move.l d0, (a0)+ */
    v=s->cpu.registers[0];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x187c0 addq.l #$1, d4 */
    v=0x1u;
    u=s->cpu.registers[4];
    v=dl_alu(s,u,v,32,0,0);
    dl_put(s,4,4,v);
    break;
   case 0x187c4: /* type3 branch; original packing cursor does not advance */
    /* 0x187c4 move.l (a1), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),4,&v));
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x187c6 asl.l #$2, d0 */
    u=0x2u;
    dl_shift(s,0,32,u&63u,1);
    /* 0x187c8 movea.l -$4(a6), a5 */
    DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0x4u),4,&v));
    s->cpu.registers[13]=v;
    /* 0x187cc move.l (a5, d0.l), d1 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[13]+s->cpu.registers[0]),4,&v));
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x187d0 move.l d1, d0 */
    v=s->cpu.registers[1];
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x187d2 andi.l #$7ff00, d0 */
    v=0x7ff00u;
    u=s->cpu.registers[0];
    v=u&v;
    dl_nz(s,v,32);
    dl_put(s,0,4,v);
    /* 0x187d8 move.l d0, d2 */
    v=s->cpu.registers[0];
    dl_put(s,2,4,v);
    dl_nz(s,v,32);
    /* 0x187da asr.l #$8, d2 */
    u=0x8u;
    dl_shift(s,2,32,u&63u,0);
    /* 0x187dc andi.l #$ff, d1 */
    v=0xffu;
    u=s->cpu.registers[1];
    v=u&v;
    dl_nz(s,v,32);
    dl_put(s,1,4,v);
    /* 0x187e2 asl.w #$8, d1 */
    u=0x8u;
    dl_shift(s,1,16,u&63u,1);
    /* 0x187e4 swap d1 */
    v=s->cpu.registers[1];v=(v<<16)|(v>>16);s->cpu.registers[1]=v;dl_nz(s,v,32);
    /* 0x187e6 clr.w d1 */
    v=0;
    dl_put(s,1,2,v);
    dl_nz(s,0,16);
    /* 0x187e8 movea.l d5, a5 */
    v=s->cpu.registers[5];
    s->cpu.registers[13]=v;
    /* 0x187ea clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x187ec move.w (a5), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[13]),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x187ee moveq #$e, d7 */
    v=dl_sx8(0xeu);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x187f0 asl.l d7, d0 */
    u=s->cpu.registers[7];
    dl_shift(s,0,32,u&63u,1);
    /* 0x187f2 or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x187f4 move.w (a2), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[10]),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x187f6 asl.l #$3, d0 */
    u=0x3u;
    dl_shift(s,0,32,u&63u,1);
    /* 0x187f8 andi.l #$fff8, d0 */
    v=0xfff8u;
    u=s->cpu.registers[0];
    v=u&v;
    dl_nz(s,v,32);
    dl_put(s,0,4,v);
    /* 0x187fe or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18800 clr.l d0 */
    v=0;
    dl_put(s,0,4,v);
    dl_nz(s,0,32);
    /* 0x18802 move.w (a3), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&v));
    dl_put(s,0,2,v);
    dl_nz(s,v,16);
    /* 0x18804 move.l d2, (a0)+ */
    v=s->cpu.registers[2];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x18806 or.l d0, d1 */
    v=s->cpu.registers[0];
    u=s->cpu.registers[1];
    v=u|v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18808 move.l d1, (a0)+ */
    v=s->cpu.registers[1];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    break;
   case 0x1880c: /* type4 stop */
    /* 0x1880c move.l (a4), d0 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[12]),4,&v));
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x1880e asl.l #$4, d0 */
    u=0x4u;
    dl_shift(s,0,32,u&63u,1);
    /* 0x18810 move.w (a2), d1 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[10]),2,&v));
    dl_put(s,1,2,v);
    dl_nz(s,v,16);
    /* 0x18812 moveq #$1, d7 */
    v=dl_sx8(0x1u);s->cpu.registers[7]=v;dl_nz(s,v,32);
    /* 0x18814 and.l d7, d1 */
    v=s->cpu.registers[7];
    u=s->cpu.registers[1];
    v=u&v;
    dl_put(s,1,4,v);
    dl_nz(s,v,32);
    /* 0x18816 asl.l #$3, d1 */
    u=0x3u;
    dl_shift(s,1,32,u&63u,1);
    /* 0x18818 or.l d1, d0 */
    v=s->cpu.registers[1];
    u=s->cpu.registers[0];
    v=u|v;
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x1881a clr.l d1 */
    v=0;
    dl_put(s,1,4,v);
    dl_nz(s,0,32);
    /* 0x1881c move.w (a3), d1 */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[11]),2,&v));
    dl_put(s,1,2,v);
    dl_nz(s,v,16);
    /* 0x1881e move.l (a1), (a0)+ */
    DL_CHECK(dl_read_value(s,(s->cpu.registers[9]),4,&v));
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x18820 or.l d1, d0 */
    v=s->cpu.registers[1];
    u=s->cpu.registers[0];
    v=u|v;
    dl_put(s,0,4,v);
    dl_nz(s,v,32);
    /* 0x18822 move.l d0, (a0)+ */
    v=s->cpu.registers[0];
    DL_CHECK(dl_write_value(s,s->cpu.registers[8],4,v));s->cpu.registers[8]+=4;dl_bank(s);
    dl_nz(s,v,32);
    /* 0x18824 addq.l #$1, d4 */
    v=0x1u;
    u=s->cpu.registers[4];
    v=dl_alu(s,u,v,32,0,0);
    dl_put(s,4,4,v);
    /* 0x18826 moveq #$1, d6 */
    v=dl_sx8(0x1u);s->cpu.registers[6]=v;dl_nz(s,v,32);
    break;
   default:s->error=7;return;
   }
  }
  /* 0x18828 adda.w #$24, a2 */
  v=0x24u;
  s->cpu.registers[10]+=dl_sx16((uint16_t)v);dl_bank(s);
  /* 0x1882c adda.w #$24, a4 */
  v=0x24u;
  s->cpu.registers[12]+=dl_sx16((uint16_t)v);dl_bank(s);
  /* 0x18830 adda.w #$24, a1 */
  v=0x24u;
  s->cpu.registers[9]+=dl_sx16((uint16_t)v);dl_bank(s);
  /* 0x18834 moveq #$24, d7 */
  v=dl_sx8(0x24u);s->cpu.registers[7]=v;dl_nz(s,v,32);
  /* 0x18836 add.l d7, d5 */
  v=s->cpu.registers[7];
  u=s->cpu.registers[5];
  v=dl_alu(s,u,v,32,0,0);
  dl_put(s,5,4,v);
  /* 0x18838 add.l d7, -$10(a6) */
  v=s->cpu.registers[7];
  DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0x10u),4,&u));
  v=dl_alu(s,u,v,32,0,0);
  DL_CHECK(dl_write_value(s,((s->cpu.registers[14])-0x10u),4,v));
  /* 0x1883c adda.w #$24, a3 */
  v=0x24u;
  s->cpu.registers[11]+=dl_sx16((uint16_t)v);dl_bank(s);
  /* 0x18840 addq.l #$4, -$c(a6) */
  v=0x4u;
  DL_CHECK(dl_read_value(s,((s->cpu.registers[14])-0xcu),4,&u));
  v=dl_alu(s,u,v,32,0,0);
  DL_CHECK(dl_write_value(s,((s->cpu.registers[14])-0xcu),4,v));
  /* 0x18844 tst.w d6 */
  v=s->cpu.registers[6];
  dl_nz(s,v,16);
 }while(s->cpu.sr&4u);
 /* Restore original callee saves and LINK frame, leaving outer RTS to the caller. */
 /* 0x1884a movem.l -$38(a6), d2-d7/a2-a5 */
 u=((s->cpu.registers[14])-0x38u);
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[2]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[3]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[4]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[5]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[6]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[7]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[10]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[11]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[12]=v;u+=4u;
 DL_CHECK(dl_read_value(s,u,4,&v));s->cpu.registers[13]=v;u+=4u;
 /* 0x18850 unlk a6 */
 s->cpu.registers[15]=s->cpu.registers[14];dl_bank(s);DL_CHECK(dl_read_value(s,s->cpu.registers[15],4,&v));s->cpu.registers[14]=v;dl_pop(s,4);
 s->cpu.pc=0x18852u;
 SCENE_DISPLAY_END(s);
}
#undef DL_CHECK
#undef DL_WORK
