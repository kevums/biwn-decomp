"""Fixed DD40 task-system setup and DDCC clock/yield loop CPU blocks."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT;RANGES={0xdd40:0xddee,0xddf2:0xddfe}
def rename(text):return loader.rename(text).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_system_cpu.py').replace('biwn_interior_loading_cpu','biwn_system_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_SYSTEM_CPU').replace('BIWN_SYSTEM_CPU_YIELDED','BIWN_SYSTEM_CPU_SWITCHED')
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=loader.base.split(tail);code=None
    if asm=='move a1, usp':code=['s.cpu.usp=s.cpu.registers[9];']
    elif asm=='move.w sr, d0':code=['put(&s,0,2,s.cpu.sr);']
    elif asm=='move.w d0, sr':code=['v=s.cpu.registers[0]&0xffffu;if((v^s.cpu.sr)&0x2000u){bank(&s);s.cpu.registers[15]=(v&0x2000u)?s.cpu.ssp:s.cpu.usp;}s.cpu.sr=(uint16_t)v;']
    elif op.startswith('bsr'):
        target=loader.base.number(parts[0]);code=[f'CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;CHECK(invoke(&s,{hex(target)}u,{hex(nxt)}u));break;']
    elif asm=='trap #$0':
        code=[f'v=s.cpu.sr;s.cpu.usp=s.cpu.registers[15];s.cpu.registers[15]=s.cpu.ssp;s.cpu.sr|=0x2000u;CHECK(push(&s,{hex(nxt)}u,4));CHECK(push(&s,v,2));CHECK(read_value(&s,0x80u,4,&v));if(v!=0xde08u)return BIWN_SYSTEM_CPU_BAD_VECTOR;s.cpu.pc=v;CHECK(s.service(s.context,s.bus,&s.cpu,v));*state=s.cpu;return BIWN_SYSTEM_CPU_SWITCHED;']
    if code is None:return rename(loader.emit(row))
    if not(op.startswith('bsr')or asm=='trap #$0'):code.append(f's.cpu.pc={hex(nxt)}u;break;')
    return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';rows=[]
    for a,b in RANGES.items():assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(('static uint32_t sx16(','static uint32_t sx8(')))+'\n'
    suffix=rename(loader.base.SUFFIX).replace('default:return BIWN_SYSTEM_CPU_BAD_PC;','default:return BIWN_SYSTEM_CPU_BAD_PC;')
    suffix=suffix.replace('}}return BIWN_SYSTEM_CPU_WORK_LIMIT;','}}*state=s.cpu;return BIWN_SYSTEM_CPU_WORK_LIMIT;')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_SYSTEM_CPU_H').replace('BIWN_SYSTEM_CPU_BAD_PC=7','BIWN_SYSTEM_CPU_BAD_PC=7,BIWN_SYSTEM_CPU_BAD_VECTOR=8')
    header=header.replace('BIWN_SYSTEM_CPU_YIELDED=6','BIWN_SYSTEM_CPU_SWITCHED=6');prefix=prefix.replace('BIWN_SYSTEM_CPU_YIELDED','BIWN_SYSTEM_CPU_SWITCHED')
    a=header.index('/* Static');b=header.index('enum biwn_system_cpu_status biwn_system_cpu_body',a)
    header=header[:a]+'''/* Source DD40 pool/system-context/vector setup, DDCC/DDF2 render
 * creation and DDD2 clock loop/TRAP0. DDEE..DDF2 is data, not CPU blocks.
 * Source USP/SR bank transition and exact TRAP exception frame retained.
 * DE5C task creation and DE08 dispatch/RTE are explicit body providers.
 * SWITCHED6 commits selected context; WORK_LIMIT4 commits completed fixed
 * instructions, allowing host stepping at source clock observations.
 * Other errors preserve input CPU and earlier RAM effects. No runtime
 * decoding/original CPU calls. Generation proves no whole boot or game. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_system_cpu.c','biwn_system_cpu.h'];(source/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+suffix);(source/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},clock_data_interval=['0xddee','0xddf2'],stage_sha256=hashlib.sha256(stage).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_published_components=0,whole_game_complete=False);(session/'system-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
