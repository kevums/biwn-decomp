/* Coordinator-owned engine/primitives; case-body authorship in manifest.
 * Source-specific static C, no runtimeopcode decoding or originalGPU calls. */
#include "biwn_gpu_setup57.h"
static void zn(struct biwn_gpu_setup57_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_setup57_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_setup57_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_setup57_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static int rd32(struct biwn_gpu_setup57_bus *bus,uint32_t a,uint32_t *v){return bus->read32(bus->context,a,v)?2:0;}
static int wr32(struct biwn_gpu_setup57_bus *bus,uint32_t a,uint32_t v){return bus->write32(bus->context,a,v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_setup57_status)status;}while(0)
enum biwn_gpu_setup57_status biwn_gpu_setup57_run(struct biwn_gpu_setup57_bus *bus,struct biwn_gpu_setup57_state *state,uint32_t budget){struct biwn_gpu_setup57_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read32||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
case 0xf03240u: s.registers[0][4]=0x58a0u; s.pc=0xf03246u; break;
case 0xf03246u: s.registers[0][1]=0xf02200u; s.pc=0xf0324cu; break;
case 0xf0324cu: CHECK(rd32(bus,s.registers[0][4]&~3u,&v)); s.registers[0][5]=v; s.pc=0xf0324eu; break;
case 0xf0324eu: s.registers[0][2]=0xf02224u; s.pc=0xf03254u; break;
case 0xf03254u: s.registers[0][4]=add(&s,s.registers[0][4],4u); s.pc=0xf03256u; break;
case 0xf03256u: s.registers[0][3]=0xf02238u; s.pc=0xf0325cu; break;
case 0xf0325cu: CHECK(rd32(bus,s.registers[0][4]&~3u,&v)); s.registers[0][8]=v; s.pc=0xf0325eu; break;
case 0xf0325eu: s.registers[0][6]=0x14028u; s.pc=0xf03264u; break;
case 0xf03264u: s.registers[0][4]=add(&s,s.registers[0][4],4u); s.pc=0xf03266u; break;
case 0xf03266u: s.registers[0][9]=0x1800801u; s.pc=0xf0326cu; break;
case 0xf0326cu: s.registers[0][8]|=1u<<16u; zn(&s,s.registers[0][8]); s.pc=0xf0326eu; break;
case 0xf0326eu: s.registers[1][8]=s.registers[0][1]; s.pc=0xf03270u; break;
case 0xf03270u: s.registers[1][9]=s.registers[0][2]; s.pc=0xf03272u; break;
case 0xf03272u: s.registers[1][10]=s.registers[0][3]; s.pc=0xf03274u; break;
case 0xf03274u: CHECK(rd32(bus,s.registers[0][3]&~3u,&v)); s.registers[0][0]=v; s.pc=0xf03276u; break;
case 0xf03276u: s.z=((~s.registers[0][0])>>0u)&1u; s.pc=0xf03278u; break;
case 0xf03278u: if(condition(&s,2)){pending=1;target=0xf03274u;} s.pc=0xf0327au; break;
case 0xf0327au: s.registers[0][7]=0u; s.pc=0xf0327cu; break;
case 0xf0327cu: CHECK(wr32(bus,s.registers[0][2],s.registers[0][5])); s.pc=0xf0327eu; break;
case 0xf0327eu: CHECK(wr32(bus,s.registers[0][1],s.registers[0][4])); s.pc=0xf03280u; break;
case 0xf03280u: s.registers[0][2]=add(&s,s.registers[0][2],4u); s.pc=0xf03282u; break;
case 0xf03282u: s.registers[0][1]=add(&s,s.registers[0][1],4u); s.pc=0xf03284u; break;
case 0xf03284u: CHECK(wr32(bus,s.registers[0][2],s.registers[0][6])); s.pc=0xf03286u; break;
case 0xf03286u: s.registers[0][3]=add(&s,s.registers[0][3],4u); s.pc=0xf03288u; break;
case 0xf03288u: CHECK(wr32(bus,s.registers[0][1],s.registers[0][6])); s.pc=0xf0328au; break;
case 0xf0328au: CHECK(wr32(bus,s.registers[0][3],s.registers[0][8])); s.pc=0xf0328cu; break;
case 0xf0328cu: s.registers[0][2]=add(&s,s.registers[0][2],8u); s.pc=0xf0328eu; break;
case 0xf0328eu: s.registers[0][1]=add(&s,s.registers[0][1],8u); s.pc=0xf03290u; break;
case 0xf03290u: CHECK(wr32(bus,s.registers[0][2],s.registers[0][7])); s.pc=0xf03292u; break;
case 0xf03292u: s.registers[0][3]=sub(&s,s.registers[0][3],4u); s.pc=0xf03294u; break;
case 0xf03294u: CHECK(wr32(bus,s.registers[0][1],s.registers[0][7])); s.pc=0xf03296u; break;
case 0xf03296u: CHECK(wr32(bus,s.registers[0][3],s.registers[0][9])); s.pc=0xf03298u; break;
case 0xf03298u: CHECK(rd32(bus,s.registers[0][3]&~3u,&v)); s.registers[0][0]=v; s.pc=0xf0329au; break;
case 0xf0329au: s.z=((~s.registers[0][0])>>0u)&1u; s.pc=0xf0329cu; break;
case 0xf0329cu: if(condition(&s,2)){pending=1;target=0xf03298u;} s.pc=0xf0329eu; break;
case 0xf0329eu: s.pc=0xf032a0u; break;
case 0xf032a0u: s.registers[0][0]=0x3u; s.pc=0xf032a6u; break;
case 0xf032a6u: s.registers[0][12]=0xf02104u; s.pc=0xf032acu; break;
case 0xf032acu: s.registers[0][13]=1u; s.pc=0xf032aeu; break;
case 0xf032aeu: CHECK(wr32(bus,s.registers[0][12],s.registers[0][0])); s.pc=0xf032b0u; break;
case 0xf032b0u: s.registers[0][14]=1u; s.pc=0xf032b2u; break;
case 0xf032b2u: s.registers[0][13]=sub(&s,0u,s.registers[0][13]); s.pc=0xf032b4u; break;
case 0xf032b4u: s.c=s.registers[0][14]>>31u; s.registers[0][14]<<=15u; zn(&s,s.registers[0][14]); s.pc=0xf032b6u; break;
case 0xf032b6u: s.c=s.registers[0][13]&1u; s.registers[0][13]>>=16u; zn(&s,s.registers[0][13]); s.pc=0xf032b8u; break;
case 0xf032b8u: s.registers[1][1]=s.registers[0][14]; s.pc=0xf032bau; break;
case 0xf032bau: s.registers[1][0]=s.registers[0][13]; s.pc=0xf032bcu; break;
case 0xf032bcu: s.registers[0][15]=0xe0u; s.pc=0xf032c2u; break;
case 0xf032c2u: s.registers[0][16]=0xb4u; s.pc=0xf032c8u; break;
case 0xf032c8u: s.registers[1][2]=s.registers[0][15]; s.pc=0xf032cau; break;
case 0xf032cau: s.registers[1][3]=s.registers[0][16]; s.pc=0xf032ccu; break;
case 0xf032ccu: s.registers[0][17]=0xf0380au; s.pc=0xf032d2u; break;
case 0xf032d2u: s.registers[0][18]=0xf038cau; s.pc=0xf032d8u; break;
case 0xf032d8u: s.registers[0][19]=0xf037e0u; s.pc=0xf032deu; break;
case 0xf032deu: s.registers[0][20]=0xf03ee4u; s.pc=0xf032e4u; break;
case 0xf032e4u: s.registers[1][4]=s.registers[0][17]; s.pc=0xf032e6u; break;
case 0xf032e6u: s.registers[1][5]=s.registers[0][18]; s.pc=0xf032e8u; break;
case 0xf032e8u: s.registers[1][6]=s.registers[0][19]; s.pc=0xf032eau; break;
case 0xf032eau: s.registers[1][7]=s.registers[0][20]; s.pc=0xf032ecu; break;
case 0xf032ecu: s.registers[0][21]=0x10c00u; s.pc=0xf032f2u; break;
case 0xf032f2u: s.registers[0][12]=0xbd83cu; s.pc=0xf032f8u; break;
case 0xf032f8u: s.registers[0][2]=s.registers[1][9]; s.pc=0xf032fau; break;
case 0xf032fau: CHECK(rd32(bus,s.registers[0][12]&~3u,&v)); s.registers[0][5]=v; s.pc=0xf032fcu; break;
case 0xf032fcu: s.registers[0][22]=0x41802c01u; s.pc=0xf03302u; break;
case 0xf03302u: CHECK(wr32(bus,s.registers[0][2],s.registers[0][5])); s.pc=0xf03304u; break;
case 0xf03304u: s.registers[1][11]=s.registers[0][21]; s.pc=0xf03306u; break;
case 0xf03306u: s.registers[0][2]=add(&s,s.registers[0][2],4u); s.pc=0xf03308u; break;
case 0xf03308u: s.registers[1][12]=s.registers[0][22]; s.pc=0xf0330au; break;
case 0xf0330au: s.registers[1][9]=s.registers[0][2]; s.pc=0xf0330cu; break;
case 0xf0330cu: s.registers[0][0]=0xf03204u; s.pc=0xf03312u; break;
case 0xf03312u: s.registers[0][11]=0xf031beu; s.pc=0xf03318u; break;
case 0xf03318u: s.registers[0][10]=0x6380u; s.pc=0xf0331eu; break;
case 0xf0331eu: pending=1;target=s.registers[0][11]; s.pc=0xf03320u; break;
case 0xf03320u: CHECK(wr32(bus,s.registers[0][0],s.registers[0][10])); s.pc=0xf03322u; break;
 default:return BIWN_GPU_SETUP57_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_SETUP57_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_SETUP57_OK;}}return BIWN_GPU_SETUP57_WORK_LIMIT;}
