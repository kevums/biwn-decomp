"""Source health task and DF7C/TRAP3/DEE2 timeout wrapper."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT;RANGES={0x18b86:0x18ba8,0xdf7c:0xdf8c,0xdee2:0xdef6}
def rename(t):return loader.rename(t).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_health_timeout_cpu.py').replace('biwn_interior_loading_cpu','biwn_health_timeout_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_HEALTH_TIMEOUT_CPU')
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly']
    if asm in ['jsr $df7c.l','jsr $df7a.l']:
        target=0xdf7c if 'df7c'in asm else 0xdf7a
        return f'  case {hex(pc)}u: /* {asm} */\n   CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;*state=s.cpu;return BIWN_HEALTH_TIMEOUT_CPU_SWITCHED;'
    if asm=='trap #$3':
        return f'  case {hex(pc)}u: /* {asm} */\n   v=s.cpu.sr;s.cpu.usp=s.cpu.registers[15];s.cpu.registers[15]=s.cpu.ssp;s.cpu.sr|=0x2000u;CHECK(push(&s,{hex(nxt)}u,4));CHECK(push(&s,v,2));CHECK(read_value(&s,0x8cu,4,&v));if(v!=0xdee2u)return BIWN_HEALTH_TIMEOUT_CPU_BAD_VECTOR;s.cpu.pc=v;break;'
    return rename(loader.emit(row)).replace('BIWN_HEALTH_TIMEOUT_CPU_YIELDED','BIWN_HEALTH_TIMEOUT_CPU_SWITCHED')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';rows=[]
    for a,b in RANGES.items():assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:];prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(('static uint32_t sx16(','static uint32_t sx8(')))+'\n'
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_HEALTH_TIMEOUT_CPU_H').replace('BIWN_HEALTH_TIMEOUT_CPU_YIELDED','BIWN_HEALTH_TIMEOUT_CPU_SWITCHED').replace('BIWN_HEALTH_TIMEOUT_CPU_BAD_PC=7','BIWN_HEALTH_TIMEOUT_CPU_BAD_PC=7,BIWN_HEALTH_TIMEOUT_CPU_BAD_VECTOR=8')
    a=header.index('/* Static');b=header.index('enum biwn_health_timeout_cpu_status biwn_health_timeout_cpu_body',a)
    header=header[:a]+'''/* Source18B86 health task, DF7C sleep wrapper andDEE2 deadline handler.
 * SWITCHED6 commits either DF7C/DF7A source-call boundary/privateframe,
 * or the context selected by supplied DE08 dispatch/RTE provider.
 * SourceTRAP3 saves exact SR/PC onSSP and deadline uses raw clock+duration.
 * Body/call retain source MOVEM and nested arguments. No runtime decoding
 * or originalCPUcalls. Generation alone proves no scheduling/boot/game. */
'''+header[b:]
    tail='  case 0xde08u: CHECK(s.service(s.context,s.bus,&s.cpu,0xde08u));*state=s.cpu;return BIWN_HEALTH_TIMEOUT_CPU_SWITCHED;\n'
    text=prefix+'\n'.join(emit(r)for r in rows)+'\n'+tail+rename(loader.base.SUFFIX)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_health_timeout_cpu.c','biwn_health_timeout_cpu.h'];(source/names[0]).write_text(text);(source/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},stage_sha256=hashlib.sha256(stage).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_published_components=0,whole_game_complete=False);(session/'health-timeout-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
