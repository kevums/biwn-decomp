/* Coordinator-owned engine/primitives; local case authorship in manifest.
 * Static recompilation, not recovered original source. */
#include "biwn_gpu_dispatcher.h"
static void zn(struct biwn_gpu_dispatcher_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_dispatcher_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_dispatcher_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_dispatcher_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static int rd32(struct biwn_gpu_dispatcher_bus *bus,uint32_t a,uint32_t *v){return bus->read32(bus->context,a,v)?2:0;}
static int wr32(struct biwn_gpu_dispatcher_bus *bus,uint32_t a,uint32_t v){return bus->write32(bus->context,a,v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_dispatcher_status)status;}while(0)
enum biwn_gpu_dispatcher_status biwn_gpu_dispatcher_run(struct biwn_gpu_dispatcher_bus *bus,struct biwn_gpu_dispatcher_state *state,uint32_t budget,uint32_t yield_idle){struct biwn_gpu_dispatcher_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||yield_idle>1||!bus->read32||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&yield_idle&&s.pc==0xf031ceu){CHECK(rd32(bus,0xf03204u,&v));if(v==0xffffffffu){CHECK(rd32(bus,0xf03200u,&v));if(v==0){*state=s;return BIWN_GPU_DISPATCHER_OK;}}}if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc,s.z,s.c,s.n);s.instructions++;switch(s.pc){
case 0xf031be:
    s.registers[0][3] = 0xf03200u;
    s.pc = 0xf031c4;
    break;


case 0xf031c4:
    s.registers[0][0] = 0u;
    s.pc = 0xf031c6;
    break;


case 0xf031c6:
    CHECK(wr32(bus, s.registers[0][3], s.registers[0][0]));
    s.pc = 0xf031c8;
    break;


case 0xf031c8:
    s.registers[0][2] = 1u;
    s.pc = 0xf031ca;
    break;


case 0xf031ca: s.registers[0][3] = add(&s, s.registers[0][3], 4); s.pc = 0xf031cc; break;


case 0xf031cc:
    s.registers[0][2] = sub(&s, 0u, s.registers[0][2]);
    s.pc = 0xf031ce;
    break;


case 0xf031ce:
    CHECK(rd32(bus, s.registers[0][3] & ~3u, &v));
    s.registers[0][4] = v;
    s.pc = 0xf031d0;
    break;


case 0xf031d0u:
sub(&s, s.registers[0][2], s.registers[0][4]); s.pc = 0xf031d2; break;

case 0xf031d2:
    if (condition(&s, 2)) {
        pending = 1;
        target = 0xf031be;
    }
    s.pc = 0xf031d4;
    break;


case 0xf031d4:
    s.registers[0][3] = sub(&s, s.registers[0][3], 4u);
    s.pc = 0xf031d6;
    break;


case 0xf031d6:
    CHECK(wr32(bus, s.registers[0][3], s.registers[0][2]));
    s.pc = 0xf031d8;
    break;


case 0xf031d8: s.registers[0][3] = add(&s, s.registers[0][3], 4); s.pc = 0xf031da; break;


case 0xf031da:
    CHECK(wr32(bus, s.registers[0][3], s.registers[0][2]));
    s.pc = 0xf031dc;
    break;


case 0xf031dc: s.registers[0][3] = add(&s, s.registers[0][3], 4); s.pc = 0xf031de; break;


case 0xf031de:
    CHECK(rd32(bus, s.registers[0][4] & ~3u, &v));
    s.registers[0][5] = v;
    s.pc = 0xf031e0;
    break;


case 0xf031e0:
    CHECK(rd32(bus, s.registers[0][3] & ~3u, &v));
    s.registers[0][0] = v;
    s.pc = 0xf031e2;
    break;


case 0xf031e2u:
sub(&s, s.registers[0][0], s.registers[0][4]); s.pc = 0xf031e4; break;

case 0xf031e4:
    if (condition(&s, 2)) {
        pending = 1;
        target = s.registers[0][5];
    }
    s.pc = 0xf031e6;
    break;


case 0xf031e6:
    CHECK(wr32(bus, s.registers[0][3], s.registers[0][4]));
    s.pc = 0xf031e8;
    break;


case 0xf031e8: s.registers[0][4] = add(&s, s.registers[0][4], 4); s.pc = 0xf031ea; break;


case 0xf031ea:
    s.registers[0][1] = s.registers[0][5];
    s.pc = 0xf031ec;
    break;


case 0xf031ec:
    CHECK(rd32(bus, s.registers[0][4] & ~3u, &v));
    s.registers[0][6] = v;
    s.pc = 0xf031ee;
    break;


case 0xf031ee: s.registers[0][4] = add(&s, s.registers[0][4], 4); s.pc = 0xf031f0; break;


case 0xf031f0:
    CHECK(rd32(bus, s.registers[0][4] & ~3u, &v));
    s.registers[0][0] = v;
    s.pc = 0xf031f2;
    break;


case 0xf031f2:
    CHECK(wr32(bus, s.registers[0][5], s.registers[0][0]));
    s.pc = 0xf031f4;
    break;


case 0xf031f4:
    s.registers[0][4] += 4u;
    s.pc = 0xf031f6;
    break;


case 0xf031f6:
    s.registers[0][6] = sub(&s, s.registers[0][6], 1u);
    s.pc = 0xf031f8;
    break;


case 0xf031f8:
    if (condition(&s, 1)) {
        pending = 1;
        target = 0xf031f0;
    }
    s.pc = 0xf031fa;
    break;


case 0xf031fa:
    s.registers[0][5] += 4u;
    s.pc = 0xf031fc;
    break;


case 0xf031fc:
    pending = 1;
    target = s.registers[0][1];
    s.pc = 0xf031fe;
    break;


case 0xf031fe:
    s.pc = 0xf03200;
    break;

default:return BIWN_GPU_DISPATCHER_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_DISPATCHER_BAD_DELAY;s.pc=resume;}
if(s.pc<0xf031beu||s.pc>=0xf03200u){*state=s;return BIWN_GPU_DISPATCHER_OK;}}
return BIWN_GPU_DISPATCHER_WORK_LIMIT;}
