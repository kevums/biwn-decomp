/* Read-only diagnostic: keypad input across Deck-to-inventory handoff.
 * This logger never supplies guest inputs, state, timing or acceptance results. */
struct handoff_row {uint32_t frame,pc,task,held,pressed,clock,d0,d1;uint16_t start,selected,deck_mode,player_mode;};
static struct handoff_row handoff_rows[8192];
static unsigned handoff_count,handoff_overflow;
static void handoff_sample(uint32_t pc){
 if(frame<24000u||frame>25600u)return;
 if(handoff_count>=8192u){handoff_overflow++;return;}
 struct handoff_row *r=&handoff_rows[handoff_count++];
 r->frame=frame;r->pc=pc;r->task=rd32(0xc0920u);r->held=rd32(0x49bacu);r->pressed=rd32(0x49ba4u);r->clock=rd32(0x778ccu);
 r->start=rd16(0x49d54u);r->selected=rd16(0x49d56u);r->deck_mode=rd16(0x403d6u);r->player_mode=rd16(0x49c60u);
 if(pc){struct cpu c;read_cpu(&c);r->d0=c.r[0];r->d1=c.r[1];}else r->d0=r->d1=0;
}
void set_frame(uint32_t value){handoff_retained_set_frame(value);handoff_sample(0);}
int32_t observe(uint32_t pc){
 if(pc==0x1a1f0u||pc==0x1a254u||pc==0x1b718u||pc==HANDOFF_DIGIT_NATIVE||pc==HANDOFF_DIGIT_BODY||pc==HANDOFF_OUTER_RETURN||pc==0x11f6au)handoff_sample(pc);
 return handoff_retained_observe(pc);
}
int handoff_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"overflow\":%u,\"events\":[",handoff_overflow);
 for(unsigned i=0;i<handoff_count;i++){
  const struct handoff_row *r=&handoff_rows[i];
  fprintf(f,"%s{\"frame\":%u,\"pc\":%u,\"task\":%u,\"held\":%u,\"pressed\":%u,\"clock\":%u,\"D0\":%u,\"D1\":%u,\"inventory_start\":%u,\"inventory_selected\":%u,\"Deck_mode\":%u,\"player_mode\":%u}",i?",":"",r->frame,r->pc,r->task,r->held,r->pressed,r->clock,r->d0,r->d1,r->start,r->selected,r->deck_mode,r->player_mode);
 }
 fputs("]}\n",f);return fclose(f)!=0;
}
