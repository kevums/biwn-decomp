/* Coordinator-owned engine/primitives; local case authorship in manifest.
 * Static recompilation, not recovered original source. */
#include "biwn_gpu_consumer6380.h"
static void zn(struct biwn_gpu_consumer6380_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_consumer6380_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_consumer6380_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_consumer6380_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static int rd32(struct biwn_gpu_consumer6380_bus *bus,uint32_t a,uint32_t *v){return bus->read32(bus->context,a,v)?2:0;}
static int loadw(struct biwn_gpu_consumer6380_bus *bus,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,a&~3u,v);if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int wr32(struct biwn_gpu_consumer6380_bus *bus,uint32_t a,uint32_t v){return bus->write32(bus->context,a,v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_consumer6380_status)status;}while(0)
enum biwn_gpu_consumer6380_status biwn_gpu_consumer6380_run(struct biwn_gpu_consumer6380_bus *bus,struct biwn_gpu_consumer6380_state *state,uint32_t budget){struct biwn_gpu_consumer6380_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
case 0xf03240:
    s.registers[0][1] = 0x10a684u;
    s.pc = 0xf03246;
    break;
case 0xf03246:
    s.registers[0][9] = 0xf03258u;
    s.pc = 0xf0324c;
    break;
case 0xf0324c:
    s.registers[0][10] = 0xf031beu;
    s.pc = 0xf03252;
    break;
case 0xf03252:
    s.registers[0][7] = 0x40u;
    s.pc = 0xf03258;
    break;
case 0xf03258:
    CHECK(rd32(bus, s.registers[0][1] & ~3u, &v));
    s.registers[0][2] = v;
    s.pc = 0xf0325a;
    break;
case 0xf0325a:
    s.registers[0][24] = 0x47b88u;
    s.pc = 0xf03260;
    break;
case 0xf03260:
    (void)sub(&s, s.registers[0][2], 0);
    s.pc = 0xf03262;
    break;
case 0xf03262:
    if (condition(&s, 2)) { pending = 1; target = s.registers[0][10]; }
    s.pc = 0xf03264;
    break;
case 0xf03264:
    s.registers[0][2] = (uint32_t)((s.registers[0][7] & 0xffffu) * (s.registers[0][2] & 0xffffu));
    zn(&s, s.registers[0][2]);
    s.pc = 0xf03266;
    break;
case 0xf03266:
    s.registers[0][4] = 0x18u;
    s.pc = 0xf0326c;
    break;
case 0xf0326c:
    s.registers[0][24] = add(&s, s.registers[0][24], s.registers[0][2]);
    s.pc = 0xf0326e;
    break;
case 0xf0326e:
    s.registers[0][5] = 0x20u;
    s.pc = 0xf03274;
    break;
case 0xf03274:
    s.registers[0][0] = s.registers[0][24];
    s.pc = 0xf03276;
    break;
case 0xf03276:
    s.registers[0][8] = 0xffffu;
    s.pc = 0xf0327c;
    break;
case 0xf0327c:
    s.registers[0][24] = add(&s, s.registers[0][24], s.registers[0][4]);
    s.pc = 0xf0327e;
    break;
case 0xf0327e:
    s.registers[0][0] = add(&s, s.registers[0][0], s.registers[0][5]);
    s.pc = 0xf03280;
    break;
case 0xf03280:
    CHECK(loadw(bus, s.registers[0][24], &v));
    s.registers[0][2] = v;
    s.pc = 0xf03282;
    break;
case 0xf03282:
    CHECK(loadw(bus, s.registers[0][0], &v));
    s.registers[0][3] = v;
    s.pc = 0xf03284;
    break;
case 0xf03284:
    s.registers[0][24] = sub(&s, s.registers[0][24], s.registers[0][4]);
    s.pc = 0xf03286;
    break;
case 0xf03286:
    (void)sub(&s, s.registers[0][8], s.registers[0][3]);
    s.pc = 0xf03288;
    break;
case 0xf03288:
    if (condition(&s, 2)) { pending = 1; target = s.registers[0][9]; }
    s.pc = 0xf0328a;
    break;
case 0xf0328a:
    CHECK(wr32(bus, s.registers[0][1], s.registers[0][2]));
    s.pc = 0xf0328c;
    break;
case 0xf0328c:
    s.registers[0][13] = 0xf03210u;
    s.pc = 0xf03292;
    break;
case 0xf03292:
    s.registers[0][14] = 0x10a688u;
    s.pc = 0xf03298;
    break;
case 0xf03298:
    CHECK(wr32(bus, s.registers[0][13], s.registers[0][24]));
    s.pc = 0xf0329a;
    break;
case 0xf0329a:
    s.registers[0][6] = 0x3cu;
    s.pc = 0xf032a0;
    break;
case 0xf032a0:
    s.registers[0][13] = add(&s, s.registers[0][13], 4);
    s.pc = 0xf032a2;
    break;
case 0xf032a2:
    s.registers[0][24] = add(&s, s.registers[0][24], s.registers[0][6]);
    s.pc = 0xf032a4;
    break;
case 0xf032a4:
    CHECK(wr32(bus, s.registers[0][13], s.registers[0][14]));
    s.pc = 0xf032a6;
    break;
case 0xf032a6:
    CHECK(rd32(bus, s.registers[0][24] & ~3u, &v));
    s.registers[0][25] = v;
    s.pc = 0xf032a8;
    break;
case 0xf032a8:
    s.registers[0][13] = sub(&s, s.registers[0][13], 8);
    s.pc = 0xf032aa;
    break;
case 0xf032aa:
    s.registers[0][24] = sub(&s, s.registers[0][24], s.registers[0][6]);
    s.pc = 0xf032ac;
    break;
case 0xf032ac:
    CHECK(wr32(bus, s.registers[0][13], s.registers[0][25]));
    s.pc = 0xf032ae;
    break;
case 0xf032ae:
    s.registers[0][11] = 0xf03440u;
    s.pc = 0xf032b4;
    break;
case 0xf032b4:
    (void)sub(&s, s.registers[0][3], 7);
    s.pc = 0xf032b6;
    break;
case 0xf032b6:
    if (condition(&s, 2)) { pending = 1; target = s.registers[0][11]; }
    s.pc = 0xf032b8;
    break;
case 0xf032b8:
    s.pc = 0xf032ba;
    break;
case 0xf032ba:
    s.registers[0][12] = 0xf03ca0u;
    s.pc = 0xf032c0;
    break;
case 0xf032c0:
    (void)sub(&s, s.registers[0][3], 8);
    s.pc = 0xf032c2;
    break;
case 0xf032c2:
    if (condition(&s, 2)) { pending = 1; target = s.registers[0][12]; }
    s.pc = 0xf032c4;
    break;
case 0xf032c4:
    s.pc = 0xf032c6;
    break;
case 0xf032c6:
    if (2 == 32) {
        s.registers[0][3] = 0;
    } else {
        s.registers[0][3] = s.registers[0][3] << 2;
    }
    zn(&s, s.registers[0][3]);
    s.pc = 0xf032c8;
    break;
case 0xf032c8:
    s.registers[0][15] = 0x3bc80u;
    s.pc = 0xf032ce;
    break;
case 0xf032ce:
    s.registers[0][15] = add(&s, s.registers[0][15], s.registers[0][3]);
    s.pc = 0xf032d0;
    break;
case 0xf032d0:
    CHECK(rd32(bus, s.registers[0][15] & ~3u, &v));
    s.registers[0][16] = v;
    s.pc = 0xf032d2;
    break;
case 0xf032d2:
    (void)sub(&s, s.registers[0][16], 0);
    s.pc = 0xf032d4;
    break;
case 0xf032d4:
    if (condition(&s, 2)) { pending = 1; target = s.registers[0][9]; }
    s.pc = 0xf032d6;
    break;
case 0xf032d6:
    s.pc = 0xf032d8;
    break;
case 0xf032d8:
    s.registers[0][25] = 0x10e688u;
    s.pc = 0xf032de;
    break;
case 0xf032de:
    s.registers[0][18] = 0x4674cu;
    s.pc = 0xf032e4;
    break;
case 0xf032e4:
    CHECK(wr32(bus, s.registers[0][13], s.registers[0][25]));
    s.pc = 0xf032e6;
    break;
case 0xf032e6:
    s.registers[0][20] = 0x1000u;
    s.pc = 0xf032ec;
    break;
case 0xf032ec:
    s.registers[0][26] = s.registers[0][25];
    s.pc = 0xf032ee;
    break;
case 0xf032ee:
    s.registers[0][19] = 0x3cf80u;
    s.pc = 0xf032f4;
    break;
case 0xf032f4:
    s.registers[0][25] = add(&s, s.registers[0][25], 8);
    s.pc = 0xf032f6;
    break;
case 0xf032f6:
    s.registers[0][26] = add(&s, s.registers[0][26], 16);
    s.pc = 0xf032f8;
    break;
case 0xf032f8:
    CHECK(wr32(bus, s.registers[0][25], s.registers[0][18]));
    s.pc = 0xf032fa;
    break;
case 0xf032fa:
    s.registers[0][27] = s.registers[0][26];
    s.pc = 0xf032fc;
    break;
case 0xf032fc:
    s.registers[0][25] = add(&s, s.registers[0][25], 4);
    s.pc = 0xf032fe;
    break;
case 0xf032fe:
    s.registers[0][27] = add(&s, s.registers[0][27], s.registers[0][20]);
    s.pc = 0xf03300;
    break;
case 0xf03300:
    CHECK(wr32(bus, s.registers[0][25], s.registers[0][19]));
    s.pc = 0xf03302;
    break;
case 0xf03302:
    s.registers[0][17] = 0xf03204u;
    s.pc = 0xf03308;
    break;
case 0xf03308:
    s.registers[0][25] = sub(&s, s.registers[0][25], 8);
    s.pc = 0xf0330a;
    break;
case 0xf0330a:
    CHECK(wr32(bus, s.registers[0][17], s.registers[0][16]));
    s.pc = 0xf0330c;
    break;
case 0xf0330c:
    CHECK(wr32(bus, s.registers[0][25], s.registers[0][27]));
    s.pc = 0xf0330e;
    break;
case 0xf0330e:
    if (condition(&s, 0)) { pending = 1; target = s.registers[0][10]; }
    s.pc = 0xf03310;
    break;
case 0xf03310:
    s.registers[0][25] = sub(&s, s.registers[0][25], 4);
    s.pc = 0xf03312;
    break;
default:return BIWN_GPU_CONSUMER6380_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_CONSUMER6380_BAD_DELAY;s.pc=resume;}
if(s.pc==0xf031beu||s.pc==0xf03440u||s.pc==0xf03ca0u){*state=s;return BIWN_GPU_CONSUMER6380_OK;}}
return BIWN_GPU_CONSUMER6380_WORK_LIMIT;}
