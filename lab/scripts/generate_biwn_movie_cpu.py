"""Source movie controller, state handlers and CPU audio interfaces.

The D4E0..D500 pointer table stays data. Direct TRAP0 suspends at its source
PC for the scheduler, without inventing a JSR or a DF60 private frame.
"""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT
RANGES={0xd3c6:0xd3f8,0xd3fc:0xd4e0,0xd500:0xdc7c,0xdca2:0xdd40,0xe8e2:0xe942}

def rename(text):
    return loader.rename(text).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_movie_cpu.py').replace('biwn_interior_loading_cpu','biwn_movie_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_MOVIE_CPU')

def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=loader.base.split(tail);kind=op.split('.')[0];code=None;terminal=False
    if kind=='bsr':
        target=loader.base.number(parts[0]);code=[f'CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;CHECK(invoke(&s,{hex(target)}u,{hex(nxt)}u));break;'];terminal=True
    elif kind=='trap':
        assert pc==0xd414 and asm=='trap #$0'
        code=['if(stop_on_yield){*state=s.cpu;return BIWN_MOVIE_CPU_YIELDED;}return BIWN_MOVIE_CPU_UNIMPLEMENTED_TRAP;'];terminal=True
    elif kind in ['lsl','lsr']:
        width={'w':2,'l':4}[op[-1]];r=loader.base.register(parts[1]);left=kind=='lsl'
        code=[loader.resource.load(parts[0],4,'u'),f'{{unsigned count=u&63u,i,carry=0;uint32_t mask={hex((1<<(width*8))-1)}u,sign={hex(1<<(width*8-1))}u;v=s.cpu.registers[{r}]&mask;for(i=0;i<count;i++){{carry='+('(v&sign)!=0;v=(v<<1)&mask;' if left else '(v&1u);v>>=1;')+f'}}put(&s,{r},{width},v);nz(&s,v,{width*8});s.cpu.sr=(uint16_t)((s.cpu.sr&~(count?0x13u:3u))|(carry?(count?0x11u:1u):0));}}']
        if not left:code[-1]=code[-1].replace(',sign='+hex(1<<(width*8-1))+'u','')
    elif kind=='mulu':
        code=[loader.resource.load(parts[0],2),loader.resource.load(parts[1],2,'u'),'v=(uint32_t)(uint16_t)v*(uint32_t)(uint16_t)u;',loader.resource.store(parts[1],4),'nz(&s,v,32);']
    elif kind=='divu':
        r=loader.base.register(parts[1]);code=[loader.resource.load(parts[0],2),f'{{uint32_t divisor=(uint16_t)v,dividend=s.cpu.registers[{r}],q,rem;if(!divisor)return BIWN_MOVIE_CPU_DIVISION_BY_ZERO;q=dividend/divisor;rem=dividend%divisor;if(q>65535u){{s.cpu.sr=(uint16_t)((s.cpu.sr&~1u)|0xau);}}else{{s.cpu.registers[{r}]=(rem<<16)|q;nz(&s,q,16);}}}}']
    elif kind=='bvs':
        code=[f's.cpu.pc=(s.cpu.sr&2u)?{hex(loader.base.number(parts[0]))}u:{hex(nxt)}u;break;'];terminal=True
    elif kind=='bclr':
        r=loader.base.register(parts[1]);assert r is not None and r<8
        bit=loader.base.number(parts[0])&31;code=[f's.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((s.cpu.registers[{r}]&(1u<<{bit}))?0:4));s.cpu.registers[{r}]&=~(1u<<{bit});']
    if code is None:return rename(loader.emit(row))
    if not terminal:code.append(f's.cpu.pc={hex(nxt)}u;break;')
    return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(stage).hexdigest()==loader.base.binary_tools.sha(session/'nextstage-68000-candidate.bin')=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for a,b in RANGES.items():
        assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xd414u)')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_MOVIE_CPU_H').replace('BIWN_MOVIE_CPU_BAD_PC=7','BIWN_MOVIE_CPU_BAD_PC=7,BIWN_MOVIE_CPU_UNIMPLEMENTED_TRAP=8,BIWN_MOVIE_CPU_DIVISION_BY_ZERO=9')
    a=header.index('/* Static');b=header.index('enum biwn_movie_cpu_status biwn_movie_cpu_body',a)
    header=header[:a]+'''/* Fixed movie caller/state handlers, marker scan, TOC/MSF conversion,
 * debug-cart writes and E8E2/E902/E918 audio interfaces. Full registers,
 * SR and both stack banks; source pointer table remains data. body stops
 * before RTS; call consumes RTS. Nested providers retain source frames.
 * Direct D414 TRAP0 stops before execution with status6 when requested;
 * scheduler must execute its actual exception separately. Otherwise8.
 * Division-by-zero is host9, not a source exception; DIVU overflow flags
 * follow the pinned reference core (not physical undefined-flag proof).
 * No runtime decoding or original CPU calls. BIOS/progress, video GPU,
 * input and DSP clock/stop completion require explicit providers.
 * Generation alone proves no movie streaming or in-game playback. */
''' + header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_movie_cpu.c','biwn_movie_cpu.h']
    (source/names[0]).write_text(prefix+'\n'.join(emit(row) for row in rows)+'\n'+rename(loader.base.SUFFIX));(source/names[1]).write_text(header)
    record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b) for a,b in RANGES.items()},table_data_interval=['0xd4e0','0xd500'],source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_published_components=0,whole_game_complete=False)
    (session/'movie-fullCPU-generation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='instructions_decoded'}))

if __name__=='__main__':main()
