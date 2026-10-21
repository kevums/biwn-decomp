"""Static source CPU for startup money/status HUD helpers."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT
RANGES={0x1b786:0x1bc78,0x18888:0x18b86}
def rename(text):return loader.rename(text).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_startup_HUD_cpu.py').replace('biwn_interior_loading_cpu','biwn_startup_HUD_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_STARTUP_HUD_CPU')
def emit(row):
    pc=row['address'];op,_,tail=row['assembly'].partition(' ');parts=loader.base.split(tail)
    if op=='lsr.l'and parts[0]=='#$1':
        r=loader.base.register(parts[1]);return f'  case {hex(pc)}u: /* {row["assembly"]} */\n   v=s.cpu.registers[{r}];u=v&1u;v>>=1;put(&s,{r},4,v);nz(&s,v,32);s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));s.cpu.pc={hex(pc+row["size"])}u;break;'
    if op=='eori.l':
        return f'  case {hex(pc)}u: /* {row["assembly"]} */\n   '+loader.resource.load(parts[1],4)+f'v^={hex(loader.base.number(parts[0]))}u;'+loader.resource.store(parts[1],4)+f'nz(&s,v,32);s.cpu.pc={hex(pc+row["size"])}u;break;'
    return rename(loader.emit(row))
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for a,b in RANGES.items():assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    assert len(rows)==572
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_STARTUP_HUD_CPU_H').replace('BIWN_STARTUP_HUD_CPU_BAD_PC=7','BIWN_STARTUP_HUD_CPU_BAD_PC=7,BIWN_STARTUP_HUD_CPU_DIVISION_BY_ZERO=8,BIWN_STARTUP_HUD_CPU_DIVISION_OVERFLOW=9');a=header.index('/* Static');b=header.index('enum biwn_startup_HUD_cpu_status biwn_startup_HUD_cpu_body',a)
    header=header[:a]+'''/* Source1B786 money/status HUD and18888 health/status drawing.
 * Fixed572 instruction blocks/fullCPU/private frames/both stack banks.
 * Text149AE, formatter1B45A and spriteE2B8 execute through helper bodies.
 * No runtime decoding/original CPU calls. Generation alone proves no
 * source path, complete GPU context, scanout, boot or playable game. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_startup_HUD_cpu.c','biwn_startup_HUD_cpu.h'];(source/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+rename(loader.base.SUFFIX));(source/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=572,instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},stage_sha256=hashlib.sha256(stage).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_published_components=0,whole_game_complete=False)
    (session/'startup-HUD-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
