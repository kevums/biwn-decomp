/* Complete normal-call185B2algorithm: original guest LINK/MOVEM/local/link table,
 * exact ordered descriptor/stack accesses, and full final CPU/bank state.
 * Based on checked logical packing and static CPU references, not original source.
 * Intermediate shadow CPU state/IRQ and private-context aliases are excluded.
 */
#ifndef SCENE_DISPLAY_BEGIN
#define SCENE_DISPLAY_BEGIN(s) ((void)(s))
#define SCENE_DISPLAY_END(s) ((void)(s))
#endif
static inline int scene_display_work(struct biwn_deck_context *s){
#ifdef SCENE_DISPLAY_NATIVE_DIRECT
 return !s->error;
#else
 if(s->error)return 0;if(!s->budget){s->error=4;return 0;}s->budget--;return 1;
#endif
}
static inline void scene_display_clr(struct biwn_deck_context *s,uint32_t a){
 if(s->error)return;
#ifdef SCENE_DISPLAY_NATIVE_DIRECT
 volatile void *p=(volatile void *)(a&0xffffffu);
 __asm__ volatile("clr.l (%0)"::"a"(p):"memory","cc");
#else
 /* Unicorn's data trace omits the68000CLRdummyread. Native bus proof is separate. */
 deck_write(s,a,4,0);
#endif
}
#define DL_R(a,w,v) do{v=deck_read(s,(a),(w));if(s->error)return;}while(0)
#define DL_W(a,w,v) do{deck_write(s,(a),(w),(v));if(s->error)return;}while(0)
#define DL_OUT(v) do{DL_W(output,4,(v));output+=4u;}while(0)
static void scene_display_list_body(struct biwn_deck_context *restrict s){
 uint32_t sp=s->cpu.registers[15],frame,records,output,row,count=1,cursor,table,at;
 uint32_t d0=0,d1=0,d2,d3,value,index,mask,word,type,field4,field10,field6,field2,carry=0;
 int stop=0;
 if(!scene_display_work(s))return;
 SCENE_DISPLAY_BEGIN(s);
 sp-=4;DL_W(sp,4,s->cpu.registers[14]);frame=sp;sp-=16;
 /* Original predecrement MOVEM order. */
 for(int i=13;i>=10;i--){sp-=4;DL_W(sp,4,s->cpu.registers[i]);}
 for(int i=7;i>=2;i--){sp-=4;DL_W(sp,4,s->cpu.registers[i]);}
 DL_R(frame+8u,4,records);DL_R(frame+12u,4,output);
 row=records;DL_R(row,2,type);
 while(type!=4u){if(!scene_display_work(s))return;count++;row+=36u;DL_R(row,2,type);}
 sp-=count*4u;DL_W(frame-4u,4,sp);cursor=0x776f0u>>3;row=records;at=sp;
 /* Pass2 writes the actual private guest table, not a host array. */
 do{
  if(!scene_display_work(s))return;DL_R(row,2,type);
  if(type==0u){cursor=(cursor+1u)&0xfffffffeu;value=2;}
  else if(type==1u){cursor=(cursor+3u)&0xfffffffcu;value=3;}
  else{value=1;if(type==4u)stop=1;}
  DL_W(at,4,cursor);at+=4u;cursor+=value;row+=36u;
 }while(!stop);
 stop=0;cursor=0x776f0u>>3;scene_display_clr(s,frame-8u);if(s->error)return;
 DL_R(frame-4u,4,value);DL_W(frame-12u,4,value);
 field4=records+4u;field10=records+10u;field6=records+6u;field2=records+2u;
 DL_W(frame-16u,4,records+18u);
 do{
  if(!scene_display_work(s))return;
  DL_R(frame-12u,4,table);DL_R(table+4u,4,d1); /* Includes final unused one-past read. */
  DL_R(records,2,type);
  if(type<=4u){
   DL_R(records,2,type);DL_W(frame-6u,2,type);
   DL_R(frame-8u,4,value);DL_R(0x18690u+value*2u,2,word);
   switch(0x18690u+deck_sx16(word)){
   case 0x1869au:case 0x1869eu:
    mask=word==0xau?1u:3u;
    while(cursor&mask){if(!scene_display_work(s))return;cursor++;d0=(cursor&0x7ff00u)>>8;DL_OUT(d0);d0=(cursor&0xffu)<<24;DL_OUT(d0|3u);}
    DL_R(field6,4,value);
    if(value){DL_R(field6,4,value);index=value<<2;DL_R(frame-4u,4,table);DL_R(table+index-4u,4,d1);}
    DL_R(field10,4,d3);d3=(d3&0xfffff8u)<<8;d2=(d1&0x7ff00u)>>8;d1=(d1&0xffu)<<24;
    DL_R(records+14u,2,word);d0=word<<14;d1|=d0;DL_R(field4,2,word);d0=word<<3;d1|=d0;
    DL_R(records,2,d0);d3|=d2;DL_OUT(d3);d1|=d0;DL_OUT(d1);
    DL_R(records+28u,2,word);d3=(uint32_t)(uint16_t)(word<<1)<<16;
    DL_R(records+26u,2,word);d0=word<<13;d3|=d0;DL_R(records+24u,2,word);d0=word<<6;d3|=d0;
    DL_R(frame-16u,4,at);DL_R(at,2,word);d2=(word&0x3f0u)>>4;DL_R(at,2,word);d1=word<<28;
    DL_R(records+16u,2,word);d0=(uint32_t)(uint16_t)(word<<2)<<16;d1|=d0;
    DL_R(records+22u,2,word);d0=word<<15;d1|=d0;DL_R(records+20u,2,word);d0=word<<12;d1|=d0;
    DL_R(field2,2,d0);d3|=d2;DL_OUT(d3);d1|=d0;DL_OUT(d1);cursor+=2u;
    DL_R(records,2,type);
    if(type==1u){
     DL_R(records+34u,2,word);d0=word<<16;DL_R(records+32u,2,word);d1=word<<8;d0|=d1;
     DL_R(records+30u,2,d1);scene_display_clr(s,output);if(s->error)return;output+=4u;d0|=d1;DL_OUT(d0);cursor++;
    }
    break;
   case 0x187a8u:
    DL_R(field10,4,d0);d0<<=14;DL_R(field4,2,word);d1=word<<3;d0|=d1;
    DL_R(records,2,d1);DL_R(field6,4,value);DL_OUT(value);d0|=d1;DL_OUT(d0);cursor++;break;
   case 0x187c4u:
    DL_R(field6,4,value);index=value<<2;DL_R(frame-4u,4,table);DL_R(table+index,4,d1);
    d0=d1&0x7ff00u;d2=d0>>8;d1=(d1&0xffu)<<24;
    DL_R(field2,2,word);d0=word<<14;d1|=d0;DL_R(field4,2,word);d0=(word<<3)&0xfff8u;d1|=d0;
    DL_R(records,2,d0);DL_OUT(d2);d1|=d0;DL_OUT(d1);break; /* No cursor advance. */
   case 0x1880cu:
    DL_R(field10,4,d0);d0<<=4;DL_R(field4,2,word);d1=(word&1u)<<3;d0|=d1;
    DL_R(records,2,d1);DL_R(field6,4,value);DL_OUT(value);d0|=d1;DL_OUT(d0);cursor++;stop=1;break;
   default:s->error=7;return;
   }
  }
  field4+=36u;field10+=36u;field6+=36u;field2+=36u;
  DL_R(frame-16u,4,value);value+=36u;DL_W(frame-16u,4,value);
  records+=36u;DL_R(frame-12u,4,value);index=value+4u;carry=index<value;DL_W(frame-12u,4,index);
 }while(!stop);
 /* MOVEM reloads the original guest saves; UNLK reads the original saved A6. */
 at=frame-56u;
 for(unsigned i=2;i<=7;i++){DL_R(at,4,value);s->cpu.registers[i]=value;at+=4u;}
 for(unsigned i=10;i<=13;i++){DL_R(at,4,value);s->cpu.registers[i]=value;at+=4u;}
 DL_R(frame,4,value);s->cpu.registers[14]=value;s->cpu.registers[15]=frame+4u;deck_bank(s);
 s->cpu.registers[0]=d0;s->cpu.registers[1]=d1;s->cpu.registers[8]=output;s->cpu.registers[9]=field6;
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xffe0u)|(carry?0x10u:0u));s->cpu.pc=0x18852u;
 SCENE_DISPLAY_END(s);
}
#undef DL_R
#undef DL_W
#undef DL_OUT
