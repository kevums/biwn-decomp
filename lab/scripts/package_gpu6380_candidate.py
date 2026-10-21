"""Quarantine the exact local case bodies in a coordinator-owned fixed engine."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HEADER='''#ifndef BIWN_GPU_CONSUMER6380_H
#define BIWN_GPU_CONSUMER6380_H
#include <stdint.h>
struct biwn_gpu_consumer6380_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_consumer6380_state {
 uint32_t registers[2][32],pc,z,c,n,instructions;
};
enum biwn_gpu_consumer6380_status {BIWN_GPU_CONSUMER6380_OK=0,
 BIWN_GPU_CONSUMER6380_BAD_ARGUMENT=1,BIWN_GPU_CONSUMER6380_BUS_ERROR=2,
 BIWN_GPU_CONSUMER6380_BAD_PC=3,BIWN_GPU_CONSUMER6380_WORK_LIMIT=4,
 BIWN_GPU_CONSUMER6380_BAD_DELAY=5};
/* Fixed original6380 list consumer, bank0 entry F03240. Preserve both register
 * banks and flags; caller supplies the actual GPU/main RAM through the bus.
 * Returns at dispatcher F031BE or resident handoff F03440/F03CA0 after delay.
 * Does not run those recipient programs or load source overlays. No runtime
 * opcode decoding/core execution, timing, interrupt or full renderer claim.
 * Errors retain prior external stores but leave input state unchanged.
 * Valid finite source list/record/table buffers required. */
enum biwn_gpu_consumer6380_status biwn_gpu_consumer6380_run(struct biwn_gpu_consumer6380_bus *,struct biwn_gpu_consumer6380_state *,uint32_t);
#endif
'''
PREFIX='''/* Coordinator-owned engine/primitives; local case authorship in manifest.
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
'''
SUFFIX='''default:return BIWN_GPU_CONSUMER6380_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_CONSUMER6380_BAD_DELAY;s.pc=resume;}
if(s.pc==0xf031beu||s.pc==0xf03440u||s.pc==0xf03ca0u){*state=s;return BIWN_GPU_CONSUMER6380_OK;}}
return BIWN_GPU_CONSUMER6380_WORK_LIMIT;}
'''
def main():
    pointer=json.loads((ROOT/'verification/GPU6380-local-author-current.json').read_text());author=Path(pointer['directory']);body=(author/'candidate-cases.txt').read_text()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'gpu-render-6380-overlay/initial-linear-decode.json').read_text());expected=[r['address']for r in mapping['rows']if r['address']<0xf03312]
    plain=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S);assert not any(token in plain for token in ['#','"',"'",'`']), 'Unexpected directives or strings'
    found=[int(v,16)for v in re.findall(r'case\s+(0x[0-9a-fA-F]+)u?\s*:',plain)];assert found==expected
    allowed={'case','u','s','registers','pc','z','c','n','v','pending','target','bus','CHECK','loadw','rd32','wr32','zn','add','sub','condition','if','else','break','void','uint32_t','uint16_t'}
    identifiers=set(re.findall(r'\b[A-Za-z_]\w*\b',re.sub(r'0x[0-9a-fA-F]+[uU]?|\b\d+[uU]?','0',plain)))
    assert identifiers<=allowed,identifiers-allowed
    assert 'return'not in plain and 'goto'not in plain
    out=author/'candidate';out.mkdir(exist_ok=True);(out/'biwn_gpu_consumer6380.h').write_text(HEADER);(out/'biwn_gpu_consumer6380.c').write_text(PREFIX+body+'\n'+SUFFIX)
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='packaged_unverified_local_case_bodies_unchanged',directory=str(out),author_directory=str(author),case_bodies_sha256=hashlib.sha256(body.encode()).hexdigest(),local_model='local/advertising-qwen38,27B6bit',coordinator_edited_case_bodies=False,coordinator_authored='interface, execution engine, integer primitives, decoder facts, native observer and tests',source_payload_sha256=mapping['payload_SHA256'],source_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest()for name in ['biwn_gpu_consumer6380.c','biwn_gpu_consumer6380.h']},source_instructions=67,full_renderer_C=False)
    (out/'package.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
