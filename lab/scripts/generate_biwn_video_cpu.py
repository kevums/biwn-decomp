"""Source CPU GPU relocation loader, video wrappers and movie IRQ/STOP/RTE."""
import hashlib,json
from pathlib import Path
import generate_biwn_movie_cpu as movie
ROOT=movie.ROOT
RANGES={0xd340:0xd3c6,0xe7aa:0xe822,0x22780:0x22a18}
def rename(s):return movie.rename(s).replace('generate_biwn_movie_cpu.py','generate_biwn_video_cpu.py').replace('biwn_movie_cpu','biwn_video_cpu').replace('BIWN_MOVIE_CPU','BIWN_VIDEO_CPU')
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=movie.loader.base.split(tail);kind=op.split('.')[0];code=None;terminal=False
    if asm=='move.w sr, d0':code=['put(&s,0,2,s.cpu.sr);']
    elif asm=='move.w d0, sr':code=['if(!(s.cpu.sr&0x2000u))return BIWN_VIDEO_CPU_PRIVILEGE_UNIMPLEMENTED;',
        '{uint16_t sr=(uint16_t)s.cpu.registers[0];bank(&s);s.cpu.sr=sr;s.cpu.registers[15]=(sr&0x2000u)?s.cpu.ssp:s.cpu.usp;}']
    elif kind=='ori':
        width={'b':1,'w':2,'l':4}[op[-1]];code=[movie.loader.resource.load(parts[0],width),movie.loader.resource.load(parts[1],width,'u'),'v|=u;',movie.loader.resource.store(parts[1],width),f'nz(&s,v,{width*8});']
    elif kind=='subi':
        width={'b':1,'w':2,'l':4}[op[-1]];code=[movie.loader.resource.load(parts[0],width),movie.loader.resource.load(parts[1],width,'u'),f'v=alu(&s,u,v,{width*8},1,0);',movie.loader.resource.store(parts[1],width)]
    elif kind=='stop':
        assert pc==0x22a0e and asm=='stop #$2000'
        code=['if(stop_on_yield){*state=s.cpu;return BIWN_VIDEO_CPU_YIELDED;}return BIWN_VIDEO_CPU_STOP_UNIMPLEMENTED;'];terminal=True
    elif kind=='rte':
        code=['if(!(s.cpu.sr&0x2000u))return BIWN_VIDEO_CPU_PRIVILEGE_UNIMPLEMENTED;',
            'CHECK(read_value(&s,s.cpu.registers[15],2,&u));CHECK(read_value(&s,s.cpu.registers[15]+2u,4,&v));s.cpu.registers[15]+=6u;s.cpu.ssp=s.cpu.registers[15];s.cpu.sr=(uint16_t)u;s.cpu.pc=v;if(!(u&0x2000u))s.cpu.registers[15]=s.cpu.usp;*state=s.cpu;return BIWN_VIDEO_CPU_OK;'];terminal=True
    if code is None:return rename(movie.emit(row))
    if not terminal:code.append(f's.cpu.pc={hex(nxt)}u;break;')
    return f'case {hex(pc)}u: /* {asm} */\n '+'\n '.join(code)

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for a,b in RANGES.items():assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=movie.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    prefix=rename(movie.loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0x22a0eu)')
    # These routines contain no arithmetic shifts.
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    header=rename(movie.loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_VIDEO_CPU_H').replace('BIWN_VIDEO_CPU_BAD_PC=7','BIWN_VIDEO_CPU_BAD_PC=7,BIWN_VIDEO_CPU_STOP_UNIMPLEMENTED=8,BIWN_VIDEO_CPU_PRIVILEGE_UNIMPLEMENTED=9')
    a=header.index('/* Static');b=header.index('enum biwn_video_cpu_status biwn_video_cpu_body',a)
    header=header[:a]+'''/* Source D340 GPU relocation copy/start/copyback, E7AA IRQ setup,
 * E7D4 IRQ handler/RTE and22780/227A0/228D4/229F4 video interfaces.
 * Full CPU/private LINK/MOVEM/args/both stack banks. body stops before
 * RTS; call consumes it. RTE consumes its real six-byte source frame.
 * STOP22A0E suspends before execution with status6 when requested;
 * separate stop/GPU interrupt event APIs perform the architectural event.
 * Other host errors preserve input CPU with prior bus writes retained.
 * Privilege violations return9, not a fabricated source exception. No
 * runtime instruction decoder or original CPU instructions. GPU/device,
 * BIOS progress and timing remain explicit providers. */
''' + header[b:]
    header=header.replace('#endif','''enum biwn_video_cpu_status biwn_video_cpu_stop(struct biwn_task_cpu *);
enum biwn_video_cpu_status biwn_video_cpu_GPU_interrupt(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif''')
    events='''
enum biwn_video_cpu_status biwn_video_cpu_stop(struct biwn_task_cpu *state){if(!state||state->pc!=0x22a0eu)return 1;if(!(state->sr&0x2000u))return 9;state->ssp=state->registers[15];state->sr=0x2000u;state->pc=0x22a12u;return 0;}
enum biwn_video_cpu_status biwn_video_cpu_GPU_interrupt(struct biwn_world_bus *bus,struct biwn_task_cpu *state){struct biwn_task_cpu cpu;uint32_t vector;if(!bus||!state||!bus->read32||!bus->write16||!bus->write32||!(state->sr&0x2000u)||state->pc!=0x22a12u)return 1;cpu=*state;if((cpu.sr&0x0700u)>=0x0200u)return 0;cpu.ssp=cpu.registers[15];cpu.registers[15]-=4u;if(bus->write32(bus->context,cpu.registers[15],cpu.pc))return 2;cpu.registers[15]-=2u;if(bus->write16(bus->context,cpu.registers[15],cpu.sr))return 2;cpu.ssp=cpu.registers[15];cpu.sr=(uint16_t)((cpu.sr&~0x8700u)|0x2200u);if(bus->read32(bus->context,0x100u,&vector))return 2;if(vector!=0xe7d4u)return 7;cpu.pc=vector;*state=cpu;return 0;}
'''
    source=ROOT/'projects/black-ice-white-noise/restoration';files=['biwn_video_cpu.c','biwn_video_cpu.h']
    (source/files[0]).write_text(prefix+'\n'.join(emit(row) for row in rows)+'\n'+rename(movie.loader.base.SUFFIX)+events);(source/files[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b) for a,b in RANGES.items()},source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in files},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False,new_published_components=0)
    (session/'video-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='instructions_decoded'}))

if __name__=='__main__':main()
