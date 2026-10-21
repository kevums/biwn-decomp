"""Complete fixed resident58A0 candidate; no acceptance from generation alone."""
import hashlib,json
from pathlib import Path
import generate_biwn_gpu_geometry as base
import generate_biwn_gpu_projection as projection
ROOT=base.ROOT
def rename(s):return s.replace('gpu_geometry','gpu_resident').replace('GPU_GEOMETRY','GPU_RESIDENT').replace('gpu_projection','gpu_resident').replace('GPU_PROJECTION','GPU_RESIDENT')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);folder=session/'gpu-resident-C-candidate';folder.mkdir(exist_ok=True);mapping=json.loads((session/'gpu-render-58a0-overlay/initial-linear-decode.json').read_text());payload=(session/'gpu-render-58a0-overlay/original-overlay.bin').read_bytes()
    assert hashlib.sha256(payload).hexdigest()=='9f14522e92bc2a5b3d9bb2db0adb7a2dfb897709bf3f500ef7c6f58203ef25ff'
    rows=[r for r in mapping['rows']if r['address']<0xf03eca];assert len(rows)==1275
    header=rename(projection.HEADER).replace(' int (*write16)(void *,uint32_t,uint16_t);\n','').replace(' void (*observe_PC)', ' int (*blitter_write32)(void *,uint32_t,uint32_t,uint8_t *);\n void (*observe_PC)')
    a=header.index('/* Fixed450');b=header.index('enum biwn_gpu_resident_status biwn_gpu_resident_run',a)
    header=header[:a]+'''/* Fixed1275-instruction resident drawing candidate, entry F03440 or F03CA0.
 * Preserve both banks, flags, accumulator/divider/matrix and complete GPU RAM.
 * Source image is already installed by57A0; caller supplies actual inherited
 * state and finite valid source buffers. Stop at dispatcher F031BE, without
 * running dispatcher. No opcode decoder/original GPU execution on C side.
 * blitter_write32 receives current4096byte localRAM on command writeF02238;
 * backend must publish it before DMA and copy any DMA localRAM effects back.
 * Other external writes use write32. Synchronous blitter backend required.
 * Errors retain prior external stores/DMA effects; input state unchanged.
 * No async timing, interrupts, scanout/fullgame or hardware accuracy claim. */
'''+header[b:]
    prefix=rename(base.PREFIX).replace('GPU4D80','GPU58A0').replace('generate_biwn_gpu_geometry.py','generate_biwn_gpu_resident.py')
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static int wr16('))+'\n'
    old='return bus->write32(bus->context,a,v)?2:0;}'
    assert old in prefix;prefix=prefix.replace(old,'if(a==0xf02238u)return bus->blitter_write32(bus->context,a,v,s->local_RAM)?2:0;return bus->write32(bus->context,a,v)?2:0;}')
    functions='''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_resident_status)status;}while(0)
enum biwn_gpu_resident_status biwn_gpu_resident_run(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *state,uint32_t budget){struct biwn_gpu_resident_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write32||!bus->blitter_write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases=[]
    for row in rows:
        word=int(row['bytes'][:4],16);op=word>>10;m=(word>>5)&31;n=word&31;N=f's.registers[0][{n}]'
        if op==7:lines=[f'{N}-={m or 32}u;']
        elif op==29:
            count=(m or 32)&31;lines=[f'v={N};s.c=v>>31;',f'{N}=(v>>{count})|(v<<{(-count)&31});',f'zn(&s,{N});']
        elif op==32:lines=[f'{N}=({N}&0x80000000u)?0u:({N}>255u?255u:{N});',f'zn(&s,{N});']
        elif op==37:lines=[f'{N}=s.registers[1][{m}];']
        else:cases.append(rename(base.emit(row)));continue
        lines.append(f's.pc={hex(row["address"]+row["size"])}u;break;');cases.append(f'case {hex(row["address"])}u: /* {row["assembly"]} */\n '+'\n '.join(lines))
    suffix='''default:return BIWN_GPU_RESIDENT_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_RESIDENT_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_RESIDENT_OK;}}return BIWN_GPU_RESIDENT_WORK_LIMIT;}
'''
    (folder/'biwn_gpu_resident.h').write_text(header);(folder/'biwn_gpu_resident.c').write_text(prefix+functions+'\n'.join(cases)+'\n'+suffix)
    report=dict(status='generated_unverified',CPU_header='0x58a0',source_instruction_count=1275,source_interval=['0xf03440','0xf03eca'],trailing_padding_and_scratch_interval=['0xf03eca','0xf03f18'],source_entries=['0xf03440','0xf03ca0'],payload_sha256=hashlib.sha256(payload).hexdigest(),source_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()for name in ['biwn_gpu_resident.c','biwn_gpu_resident.h']},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),shared_generator_sha256=hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),instructions_decoded=rows,coordinator_authored=True,local_model_case_bodies=False,full_renderer_C=False,scope='Full contiguous source code candidate through final jump/delay F03EC6/F03EC8. Tail contains padding and scratch fields referenced by source stores/matrix use. Classification and all instruction coverage still require original execution/control-flow evidence; generation alone is no acceptance.')
    (folder/'C-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
