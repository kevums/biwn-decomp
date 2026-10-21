"""Fixed guarded firmware GPU renderer variants, with source code overlays.

Only observed PC/byte variants are compiled. C must recreate local code
through its own stores and shared blitter operations; no overlay payloads
are installed by this module and no original GPU instructions execute.
"""
import hashlib,json,re
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
rename=lambda t:t.replace('gpu_geometry','firmware_GPU_renderer').replace('GPU_GEOMETRY','FIRMWARE_GPU_RENDERER')

def operations(row):
    word=int(row['bytes'][:4],16);op,m,n=word>>10,(word>>5)&31,word&31;imm=m or 32
    M=f's.registers[s.active_bank][{m}]';N=f's.registers[s.active_bank][{n}]';lines=None
    if op==1:lines=[f'{{uint64_t t=(uint64_t){N}+{M}+s.c;{N}=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,{N});}}']
    elif op==11:lines=[f'{N}^={M};zn(&s,{N});']
    elif op==33:lines=[f'{N}=({N}&0x80000000u)?0u:({N}>0xffffu?0xffffu:{N});zn(&s,{N});']
    elif op==36:lines=[f's.registers[1u-s.active_bank][{n}]={M};']
    elif op==37:lines=[f'{N}=s.registers[1u-s.active_bank][{m}];']
    elif op==39:lines=[f'CHECK(rd8(bus,&s,{M},&v));{N}=v;']
    elif op==41:lines=[f'CHECK(rd32(bus,&s,local({M})?({M}&~3u):{M},&v));{N}=v;']
    elif op in [43,44]:lines=[f'CHECK(rd32(bus,&s,s.registers[s.active_bank][{14 if op==43 else 15}]+{imm*4}u,&v));{N}=v;']
    elif op in [49,50]:lines=[f'CHECK(wr32(bus,&s,s.registers[s.active_bank][{14 if op==49 else 15}]+{imm*4}u,{N}));']
    if lines is not None:return ' '.join(lines)
    emitted=rename(base.emit(row)).replace('s.registers[0][','s.registers[s.active_bank][')
    body=emitted.split('*/',1)[1]
    return re.sub(r's\.pc=0x[0-9a-f]+u;break;\s*$','',body).strip()

def main():
    proof=json.loads((ROOT/'verification/firmware-video-IRQ-live-checks.json').read_text())
    source=Path(proof['GPU_followup_native_directory']);observation=json.loads((source/'report.json').read_text());gpu=observation['GPU_after_video_IRQ_observation']
    assert observation['emulator_shutdown_completed']and gpu['stop_reason']=='source_GPU_GO_cleared'
    rows=list(gpu['visited_instructions']);assert len(rows)==1317
    renderer_keys={(r['address'],r['bytes'])for r in rows}
    initial=observation['GPU_shutdown_observation']['visited_instructions']
    rows.extend({**r,'initial_wait_only':True}for r in initial if(r['address'],r['bytes'])not in renderer_keys)
    assert len(rows)==1321
    grouped={}
    for row in rows:grouped.setdefault(row['address'],[]).append(row)
    header=rename(base.HEADER).replace(' int (*read16)', ' int (*read8)(void *,uint32_t,uint8_t *);\n int (*read16)')
    header=header.replace('struct biwn_firmware_GPU_renderer_bus {','struct biwn_firmware_GPU_renderer_state;\nstruct biwn_firmware_GPU_renderer_bus {')
    header=header.replace(' void (*observe_PC)(void *,uint32_t);',' void (*observe_PC)(void *,struct biwn_firmware_GPU_renderer_state *,uint32_t);\n int (*sync)(void *,struct biwn_firmware_GPU_renderer_state *,int);')
    header=header.replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;','uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    header=header.replace('BIWN_FIRMWARE_GPU_RENDERER_BAD_DELAY=5','BIWN_FIRMWARE_GPU_RENDERER_BAD_DELAY=5,BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE=7')
    a=header.index('/* Source-specific');b=header.index('enum biwn_firmware_GPU_renderer_status biwn_firmware_GPU_renderer_init',a)
    header=header[:a]+'''/* Observed initialGPUwait+renderer:1017PCs/1321exact byte variants,
 * including code copied/patched in localRAM by source operations.
 * Guards check all instruction/immediate bytes before each compiled block.
 * No runtime decoder, source overlay hostcopy or originalGPU execution.
 * sync exports C logicalstate to shared peripheralbus before external IO,
 * imports peripheral/DMA effects afterward. Blitter and GPU MMIO/IRQ entry
 * are shared hardware-model dependencies, not reconstructed here.
 * run returns0 atsourceGO clear,4 atbudget withstate retained; othererrors
 * leave inputstate unchanged withprior externalstores retained.
 * Source input/initialCPU-DSP-videoIRQ/providedtail and explicitsequencing
 * remain dependencies. Otherqueues/bytevariants/inputs/clocks/discboot/
 * physicalscanout/playability separate; generated code is unverified. */
'''+header[b:]
    a=header.index('enum biwn_firmware_GPU_renderer_status biwn_firmware_GPU_renderer_init');b=header.index('enum biwn_firmware_GPU_renderer_status biwn_firmware_GPU_renderer_run',a);header=header[:a]+header[b:]
    prefix=rename(base.PREFIX).replace('s->registers[0][','s->registers[s->active_bank][')
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static int matrix('))+'\n'
    # Preserve the pinned bus's exact external address semantics. Local SRAM
    # LOAD/LOADB use the source full-word aligned access convention.
    a=prefix.index('static int rd32(');b=prefix.index('static void divide(',a)
    prefix=prefix[:a]+'''static int io_sync(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,int after){return b->sync&&b->sync(b->context,s,after)?2:0;}
static int rd32(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(io_sync(b,s,0))return 2;int status=b->read32(b->context,a,v)?2:0;if(io_sync(b,s,1))return 2;return status;}
static int rd16(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){uint16_t x;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(io_sync(b,s,0))return 2;int status=b->read16(b->context,a,&x)?2:0;*v=x;if(io_sync(b,s,1))return 2;return status;}
static int loadw(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);return rd16(b,s,a,v);}
static int rd8(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t *v){uint8_t x;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);if(io_sync(b,s,0))return 2;int status=b->read8(b->context,a,&x)?2:0;*v=x;if(io_sync(b,s,1))return 2;return status;}
static int wr32(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(io_sync(b,s,0))return 2;int status=b->write32(b->context,a,v)?2:0;if(io_sync(b,s,1))return 2;return status;}
static int wr16(struct biwn_firmware_GPU_renderer_bus *b,struct biwn_firmware_GPU_renderer_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(b,s,a&~1u,v&0xffffu);if(io_sync(b,s,0))return 2;int status=b->write16(b->context,a,(uint16_t)v)?2:0;if(io_sync(b,s,1))return 2;return status;}
''' +prefix[b:]
    prefix+='''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_firmware_GPU_renderer_status)status;}while(0)
enum biwn_firmware_GPU_renderer_status biwn_firmware_GPU_renderer_run(struct biwn_firmware_GPU_renderer_bus *bus,struct biwn_firmware_GPU_renderer_state *state,uint32_t budget){struct biwn_firmware_GPU_renderer_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->sync||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget){unsigned delayed=pending;uint32_t resume=target,nxt=0;pending=0;if(!(s.control&1u)&&!delayed){*state=s;return 0;}if(bus->observe_PC)bus->observe_PC(bus->context,&s,s.pc);s.instructions++;switch(s.pc){
'''
    cases=[]
    for pc,versions in sorted(grouped.items()):
        code=f'case {hex(pc)}u:\n'
        for i,row in enumerate(versions):
            payload=bytes.fromhex(row['bytes']);guard='&&'.join(f's.local_RAM[{pc-0xf03000+j}]=={value}u'for j,value in enumerate(payload))
            code+=('if'if i==0 else'else if')+'('+guard+') {'+f'nxt={hex(pc+row["size"])}u;s.pc=nxt;'+operations(row)+'}\n'
        code+='else return BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE;break;'
        cases.append(code)
    suffix='''default:return BIWN_FIRMWARE_GPU_RENDERER_BAD_PC;
}if(delayed){if(pending)return BIWN_FIRMWARE_GPU_RENDERER_BAD_DELAY;if(s.pc==nxt)s.pc=resume;}if(!pending){budget--;if(!(s.control&1u)){*state=s;return 0;}}}*state=s;return 4;}
'''
    destination=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_firmware_GPU_renderer.c','biwn_firmware_GPU_renderer.h'];(destination/names[0]).write_text(prefix+'\n'.join(cases)+'\n'+suffix);(destination/names[1]).write_text(header)
    mapping=dict(status='generated_unverified',native_directory=str(source),instructions=len(rows),PCs=len(grouped),renderer_instruction_versions=1317,initial_wait_extra_versions=4,instruction_versions=rows,source_GPU_initial_image_source='liveCPU/GPU wait+sourceCvideoIRQ; no generatedmodule copies inputimage',source_sha256={name:hashlib.sha256((destination/name).read_bytes()).hexdigest()for name in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_emitter_sha256=hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),live_byte_guards=True,source_code_overlay_hostcopy=False,shared_peripheral_DMA_sync=True,original_GPU_instructions_on_C_path=0,implementation_authorship='coordinator',whole_game_complete=False)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);(session/'firmware-GPU-renderer-generation.json').write_text(json.dumps(mapping,indent=2)+'\n');print(json.dumps({k:v for k,v in mapping.items()if k!='instruction_versions'}))

if __name__=='__main__':main()
