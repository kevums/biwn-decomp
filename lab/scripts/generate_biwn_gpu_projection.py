"""Build-time fixed GPU52E0 C; shares checked integer primitives with4D80."""
import hashlib,json
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
HEADER='''#ifndef BIWN_GPU_PROJECTION_H
#define BIWN_GPU_PROJECTION_H
#include <stdint.h>
struct biwn_gpu_projection_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_projection_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_projection_status {BIWN_GPU_PROJECTION_OK=0,
 BIWN_GPU_PROJECTION_BAD_ARGUMENT=1,BIWN_GPU_PROJECTION_BUS_ERROR=2,
 BIWN_GPU_PROJECTION_BAD_PC=3,BIWN_GPU_PROJECTION_WORK_LIMIT=4,
 BIWN_GPU_PROJECTION_BAD_DELAY=5};
/* Fixed450-instruction source program. Bank0 active. Preserve both incoming
 * register banks/flags/accumulator/divider/matrix state and all4KBlocalRAM.
 * prepare loads the frozen overlay and sourceE19E mailbox values without
 * resettingGPUstate. Caller supplies E19E's mainRAM10A684=1 store.
 * Positive finite record buffers required. run returns atF031BE; no source
 * dispatcher, timing, interrupts, drawing/rasterization or scanout claim.
 * Errors retain prior external stores and leave inputstate unchanged. */
enum biwn_gpu_projection_status biwn_gpu_projection_prepare(struct biwn_gpu_projection_state *,uint32_t);
enum biwn_gpu_projection_status biwn_gpu_projection_run(struct biwn_gpu_projection_bus *,struct biwn_gpu_projection_state *,uint32_t);
#endif
'''
def rename(s):return s.replace('gpu_geometry','gpu_projection').replace('GPU_GEOMETRY','GPU_PROJECTION')
def emit(row):
    pc=row['address'];w=int(row['bytes'][:4],16);op=w>>10;m=(w>>5)&31;n=w&31
    if op not in [18,19,20,37]:return base.emit(row)
    M=f's.registers[0][{m}]';N=f's.registers[0][{n}]'
    product=f'(uint32_t)((int64_t)(int32_t)sx16({N})*(int32_t)sx16({M}))'
    lines={18:[f's.accumulator={product};','zn(&s,s.accumulator);'],19:[f'{N}=s.accumulator;'],20:[f's.accumulator+={product};'],37:[f'{N}=s.registers[1][{m}];']}[op]
    lines.append(f's.pc={hex(pc+row["size"])}u;break;')
    return f'  case {hex(pc)}u: /* {row["assembly"]} */\n   '+'\n   '.join(lines)
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);folder=session/'gpu-render-52e0-overlay';mapping=json.loads((folder/'initial-linear-decode.json').read_text());payload=(folder/'original-overlay.bin').read_bytes()
    assert hashlib.sha256(payload).hexdigest()==mapping['payload_SHA256']=='015e07d4c6fbfa726c9af2f5bc9a15b99e4d0ff225d38402f23eff4239bd9b92'
    rows=[r for r in mapping['rows']if r['address']<0xf0362c];assert len(rows)==450
    prefix=rename(base.PREFIX).replace('GPU4D80','GPU52E0').replace('generate_biwn_gpu_geometry.py','generate_biwn_gpu_projection.py')
    image='static const uint8_t source_image[1200]={\n'+',\n'.join(','.join(hex(x)for x in payload[i:i+24])for i in range(0,len(payload),24))+'\n};\n'
    functions='''enum biwn_gpu_projection_status biwn_gpu_projection_prepare(struct biwn_gpu_projection_state *s,uint32_t count){if(!s||!count||s->z>1||s->c>1||s->n>1)return 1;memcpy(s->local_RAM+0x240,source_image,1200);put32(s->local_RAM+0x204,0x52e0);put32(s->local_RAM+0x20c,0x47b88);put32(s->local_RAM+0x210,0x47bc8);put32(s->local_RAM+0x214,count);put32(s->local_RAM+0x218,64);put32(s->local_RAM+0x21c,0x10a684);s->pc=0xf03240;s->instructions=0;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_projection_status)status;}while(0)
enum biwn_gpu_projection_status biwn_gpu_projection_run(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *state,uint32_t budget){struct biwn_gpu_projection_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    suffix='''  default:return BIWN_GPU_PROJECTION_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_PROJECTION_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_PROJECTION_OK;}}return BIWN_GPU_PROJECTION_WORK_LIMIT;}
'''
    source=ROOT/'projects/black-ice-white-noise/restoration';(source/'biwn_gpu_projection.h').write_text(HEADER);(source/'biwn_gpu_projection.c').write_text(prefix+image+functions+'\n'.join(emit(r)for r in rows)+'\n'+suffix)
    report=dict(status='generated_unverified',instructions=450,source_interval=['0xf03240','0xf0362c'],payload_bytes=1200,payload_sha256=mapping['payload_SHA256'],generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),shared_generator_sha256=hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_gpu_projection.c','biwn_gpu_projection.h']},instructions_decoded=rows,whole_game_complete=False)
    (folder/'C-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
