/* Read-only boundary observations. Never owns or replaces an instruction. */
static const uint8_t *ram;
static uint32_t frame,event_count,overflow;
struct event {
 uint32_t frame,pc,stage,clock,previous,dt,held,edges,state,speed,remainder;
 uint32_t animation,queued_animation,animation_flags,heading,x,z;
 uint32_t di[3],df[3],pf[3],camera[3],cf[3];
};
static struct event events[2048];
static uint32_t r16(uint32_t a){return (uint32_t)ram[a]*256u+ram[a+1];}
static uint32_t r32(uint32_t a){return r16(a)*65536u+r16(a+2);}
void setup(const uint8_t *p){ram=p;}
void set_frame(uint32_t f){frame=f;}
int32_t observe(uint32_t pc){
 for(unsigned i=0;i<7;i++)if(pc==addresses[i])counts[i]++;
 uint32_t stage=pc==0x191f4u?1u:pc==0x1a26cu?2u:pc==0x1a2c2u?3u:0u;
 if(stage){
  if(event_count>=2048u){overflow++;return 0;}
  struct event *e=&events[event_count++];
  e->frame=frame;e->pc=pc;e->stage=stage;e->clock=r32(0x778ccu);e->previous=r32(0x46252u);
  e->dt=r32(0x4c24cu);e->held=r32(0x49ba4u);e->edges=r32(0x49bacu);e->state=r16(0x49cb8u);
  e->speed=r32(0x49cc4u);e->remainder=r32(0x49cc8u);e->animation=r32(0x49cb0u);
  e->queued_animation=r32(0x49cb4u);e->animation_flags=e->animation<0x1ffffdu?ram[e->animation+2u]:0xffffffffu;
  e->heading=ram[0x49cbau];e->x=r32(0x49c50u);e->z=r32(0x49c56u);
  for(unsigned i=0;i<3;i++){
   e->di[i]=r16(0x49cdeu+i*2u);e->df[i]=r16(0x49ce6u+i*2u);e->pf[i]=r16(0x49c5au+i*2u);
   e->camera[i]=r16(0x49b8cu+i*2u);e->cf[i]=r16(0x49b92u+i*2u);
  }
 }
 return 0;
}
uint64_t stat(unsigned i){return i<7?counts[i]:0;}
int dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;fprintf(f,"{\"overflow\":%u,\"events\":[\n",overflow);
 for(uint32_t i=0;i<event_count;i++){
  const struct event *e=&events[i];
  fprintf(f,"%s{\"frame\":%u,\"pc\":%u,\"stage\":%u,\"clock\":%u,\"previous\":%u,\"dt\":%u,\"held\":%u,\"edges\":%u,\"state\":%u,\"speed\":%u,\"remainder\":%u,\"animation\":%u,\"queued_animation\":%u,\"animation_flags\":%u,\"heading\":%u,\"x\":%u,\"z\":%u",
   i?",\n":"",e->frame,e->pc,e->stage,e->clock,e->previous,e->dt,e->held,e->edges,e->state,e->speed,e->remainder,e->animation,e->queued_animation,e->animation_flags,e->heading,e->x,e->z);
  const uint32_t *arrays[]={e->di,e->df,e->pf,e->camera,e->cf};
  const char *names[]={"delta_integer","delta_fraction","player_fraction","camera","camera_fraction"};
  for(unsigned j=0;j<5;j++)fprintf(f,",\"%s\":[%u,%u,%u]",names[j],arrays[j][0],arrays[j][1],arrays[j][2]);
  fprintf(f,"}");
 }
 fprintf(f,"\n]}\n");return fclose(f);
}
