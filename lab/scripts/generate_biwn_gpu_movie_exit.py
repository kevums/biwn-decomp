"""Execution-proven source GPU initializerF03224..F03274 to dispatcher."""
import json,hashlib,subprocess
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
rename=lambda s:s.replace('gpu_geometry','gpu_movie_exit').replace('GPU_GEOMETRY','GPU_MOVIE_EXIT')
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-exit-GPU-original.json').read_text());payload=(Path(proof['directory'])/'executed-GPU-code.bin').read_bytes()
    pcs={pc for pc in proof['PCs'] if pc<0xf031be}
    for pc in list(pcs):
        word=int.from_bytes(payload[pc-0xf03000:pc-0xf03000+2],'big')
        if word>>10 in [52,53]:pcs.add(pc+2)
    rows=[]
    for pc in sorted(pcs):
        word=int.from_bytes(payload[pc-0xf03000:pc-0xf03000+2],'big');size=6 if word>>10==38 else 2;data=payload[pc-0xf03000:pc-0xf03000+size]
        decoded=subprocess.check_output([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu',hex(pc)],input=data).decode().strip().split('\t');assert int(decoded[0],16)==pc and int(decoded[1],16)==size
        rows.append(dict(address=pc,size=size,bytes=data.hex(),assembly=decoded[2]))
    header=rename(base.HEADER).replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;', 'uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a=header.index('/* Source-specific');b=header.index('enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_init',a)
    header=header[:a]+'''/*10execution-proven static GPU IRQ0 vector/exit-handler instructions, bank0.
 * EntryF03000 readsflags, acknowledgesIRQ0 and drops its sourceframe,
 * returns atF031BE dispatcher before idleloop. CPU_control5 emits its ownIRQframe. Inherited full banks/flags/
 * localRAM and peripheral callbacks; original GPU never executes. Unknown
 * PCs fail, no runtime decoder. Bank1 is unsupported; no other IRQ/main
 * boot/fullgame/physicalhardware claim. Prior bus stores survive host error,
 * inputstate commits only success. Source callbacks must not introduce a
 * another pending enabled GPU IRQ during the handler; that is a separate event. */
''' + header[b:]
    a=header.index('enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_init');b=header.index('enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_run',a);header=header[:a]+header[b:]
    prefix=rename(base.PREFIX)
    remove=('static uint32_t sx16(', 'static uint32_t sar(', 'static int rd16(', 'static int loadw(', 'static void divide(', 'static int matrix(', 'static uint32_t sub(', 'static int wr16(')
    prefix='\n'.join(line for line in prefix.splitlines() if not line.startswith(remove))+'\n'
    prefix=prefix.replace('if(a==0xf02104u){*v=s->matrix_control;return 0;}', 'if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}')
    prefix=prefix.replace('if(a==0xf02104u){s->matrix_control=v;return 0;}', 'if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;if(s->active_bank)return 1;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}')
    prefix+='''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_movie_exit_status)status;}while(0)
enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_run(struct biwn_gpu_movie_exit_bus *bus,struct biwn_gpu_movie_exit_state *state,uint32_t budget){struct biwn_gpu_movie_exit_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read32||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases=[]
    for row in rows:
        word=int(row['bytes'][:4],16);op=word>>10;m=(word>>5)&31;n=word&31
        if op==29:
            count=m&31;N=f's.registers[0][{n}]';cases.append(f'case {hex(row["address"])}u: /* {row["assembly"]} */\n v={N};s.c=v>>31;{N}=(v>>{count})|(v<<{(-count)&31});zn(&s,{N});s.pc={hex(row["address"]+row["size"])}u;break;')
        else:cases.append(rename(base.emit(row)))
    suffix='''default:return BIWN_GPU_MOVIE_EXIT_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_MOVIE_EXIT_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_GPU_MOVIE_EXIT_WORK_LIMIT;}
'''
    header=header.replace('#endif','enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_CPU_control5(struct biwn_gpu_movie_exit_bus *,struct biwn_gpu_movie_exit_state *);\n#endif')
    event="""
enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_CPU_control5(struct biwn_gpu_movie_exit_bus *bus,struct biwn_gpu_movie_exit_state *state){struct biwn_gpu_movie_exit_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;s.control=(s.control&0xf7c0u)|1u;s.control|=0x40u;if(!(s.flags&8u)&&(s.flags&0x10u)){s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03000u;}*state=s;return 0;}
"""
    suffix+=event
    folder=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_gpu_movie_exit.c','biwn_gpu_movie_exit.h'];(folder/names[0]).write_text(prefix+'\n'.join(cases)+suffix);(folder/names[1]).write_text(header)
    record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_sha256={n:sha((folder/n).read_bytes()) for n in names},source_payload_sha256=sha(payload),whole_game_complete=False)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);(session/'GPU-movie-exit-C-generation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(instructions=len(rows),source_sha256=record['source_sha256'])))
if __name__=='__main__':main()
