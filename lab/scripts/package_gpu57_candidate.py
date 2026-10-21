"""Wrap inspected local case bodies in coordinator-owned fixedC engine.

No opcode decoder or originalGPU calls. This script does not execute the draft.
"""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HEADER='''#ifndef BIWN_GPU_SETUP57_H
#define BIWN_GPU_SETUP57_H
#include <stdint.h>
struct biwn_gpu_setup57_bus {
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_setup57_state {uint32_t registers[2][32],pc,z,c,n,instructions;};
enum biwn_gpu_setup57_status {BIWN_GPU_SETUP57_OK=0,BIWN_GPU_SETUP57_BAD_ARGUMENT=1,
 BIWN_GPU_SETUP57_BUS_ERROR=2,BIWN_GPU_SETUP57_BAD_PC=3,
 BIWN_GPU_SETUP57_WORK_LIMIT=4,BIWN_GPU_SETUP57_BAD_DELAY=5};
/* Fixed73instruction57A0 program. Incomingbank0/localRAM/control/blitterstate
 * supplied by caller. Bus implements all sharedRAM, GPUlocal/control and
 * pinnedblittereffects. Preserves64registers andZ/C/N; queues6380 thenreturns
 * F031BE. No dispatcher/completion, laterdraw/scanout/viewport/timing claim.
 * Errors preservepriorbuswrites and leaveinputstateunchanged. */
enum biwn_gpu_setup57_status biwn_gpu_setup57_run(struct biwn_gpu_setup57_bus *,struct biwn_gpu_setup57_state *,uint32_t);
#endif
'''
PREFIX='''/* Coordinator-owned engine/primitives; case-body authorship in manifest.
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
'''
SUFFIX=''' default:return BIWN_GPU_SETUP57_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_SETUP57_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_SETUP57_OK;}}return BIWN_GPU_SETUP57_WORK_LIMIT;}
'''
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,required=True);options=parser.parse_args();folder=options.directory.resolve();cases=(folder/'candidate-cases.txt').read_text()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'gpu-render-57a0-overlay/initial-linear-decode.json').read_text());rows=[r for r in mapping['rows']if r['address']<0xf03322];expected=[r['address']for r in rows]
    labels=[int(x,16)for x in re.findall(r'case\s+(0x[0-9a-fA-F]+)u?\s*:',cases)]
    allowed={'CHECK','rd32','wr32','add','sub','zn','condition','if'};calls=set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',cases));assert calls<=allowed,calls-allowed
    assert labels==expected,dict(missing=list(map(hex,set(expected)-set(labels))),extra=list(map(hex,set(labels)-set(expected))))
    assert not re.search(r'#|\bgoto\b|\breturn\b|\bfor\b|\bwhile\b|\bdo\b|\bdefault\b|\bsystem\b|\b__asm\b|\bstruct\b|\btypedef\b|\bstatic\b',cases)
    assert 'rd32'in calls and 'wr32'in calls and 'add'in calls and 'sub'in calls
    (folder/'biwn_gpu_setup57.c').write_text(PREFIX+cases+'\n'+SUFFIX);(folder/'biwn_gpu_setup57.h').write_text(HEADER)
    manifest=dict(status='packaged_unverified',role=json.loads((folder/'protocol.json').read_text())['role'],case_bodies_sha256=hashlib.sha256(cases.encode()).hexdigest(),wrapper_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()for name in ['biwn_gpu_setup57.c','biwn_gpu_setup57.h']},original_payload_sha256=mapping['payload_SHA256'],source_instruction_count=73,coordinator_supplied='interface,engine,integerprimitives,mechanicaldecodefacts,checks',local_model_supplied='casebodies only; pendingoriginalGPUcomparison',existing_C_supplied_to_model=False)
    (folder/'package.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
