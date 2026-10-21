"""Fixed resident GPU IRQ2 game/video clock handler with own event frame."""
import hashlib,json,subprocess
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
rename=lambda t:t.replace('gpu_geometry','gpu_timer').replace('GPU_GEOMETRY','GPU_TIMER')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();payload=ram[0x40a8:0x4324];rows=[]
    for a,b in [(0xf03020,0xf03030),(0xf03140,0xf03178),(0xf031ac,0xf031be)]:
        data=payload[a-0xf03000:b-0xf03000];decoded=subprocess.check_output([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu',hex(a)],input=data).decode().strip().splitlines()
        for line in decoded:
            pc,size,asm=line.split('\t');pc=int(pc,16);size=int(size,16);rows.append(dict(address=pc,size=size,bytes=payload[pc-0xf03000:pc-0xf03000+size].hex(),assembly=asm))
    header=rename(base.HEADER).replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;','uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a=header.index('/* Source-specific');b=header.index('enum biwn_gpu_timer_status biwn_gpu_timer_init',a);header=header[:a]+'''/* Resident GPU IRQ2 vector/clock handler and common return epilogue.
 * Fixed source blocks, own timer event/PC-2 frame, full logical state.
 * Handler uses bank0; event may enter from bank1 and return to it.
 * Clock778CC increments; BD854+BD858 carry increments wordBD852.
 * No runtime decoder/originalGPU calls. run stops on returned originalPC.
 * Timer delivery/period and other IRQs remain explicit host dependencies. */
'''+header[b:];a=header.index('enum biwn_gpu_timer_status biwn_gpu_timer_init');b=header.index('enum biwn_gpu_timer_status biwn_gpu_timer_run',a);header=header[:a]+header[b:];header=header.replace('struct biwn_gpu_timer_state *,uint32_t);','struct biwn_gpu_timer_state *,uint32_t,uint32_t);')
    header=header.replace('#endif','enum biwn_gpu_timer_status biwn_gpu_timer_assert(struct biwn_gpu_timer_bus *,struct biwn_gpu_timer_state *);\n#endif')
    prefix=rename(base.PREFIX);remove=('static uint32_t sx16(','static uint32_t sar(','static void divide(','static int matrix(');prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(remove))+'\n'
    prefix=prefix.replace('if(a==0xf02104u){*v=s->matrix_control;return 0;}','if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}')
    prefix=prefix.replace('if(a==0xf02104u){s->matrix_control=v;return 0;}','if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}')
    prefix+='''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_timer_status)status;}while(0)
enum biwn_gpu_timer_status biwn_gpu_timer_run(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *state,uint32_t budget,uint32_t returnPC){struct biwn_gpu_timer_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases='\n'.join(rename(base.emit(r))for r in rows)
    suffix='''default:return BIWN_GPU_TIMER_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_TIMER_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==returnPC){*state=s;return 0;}}return BIWN_GPU_TIMER_WORK_LIMIT;}
enum biwn_gpu_timer_status biwn_gpu_timer_assert(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *state){struct biwn_gpu_timer_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;if(!(s.control&1u))return 6;s.control|=0x100u;if((s.control&8u)||(s.flags&8u)||!(s.flags&0x40u)){*state=s;return 7;}s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03020u;*state=s;return 0;}
'''
    header=header.replace('BIWN_GPU_TIMER_BAD_DELAY=5','BIWN_GPU_TIMER_BAD_DELAY=5,BIWN_GPU_TIMER_HALTED=6,BIWN_GPU_TIMER_LATCHED=7')
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_gpu_timer.c','biwn_gpu_timer.h'];(src/names[0]).write_text(prefix+cases+suffix);(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_payload_sha256=hashlib.sha256(payload).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False,new_published_components=0);(session/'GPU-timer-C-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
