"""Fixed4000 caller, disc/video/heap/list/music CPU initialization blocks."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT
RANGES={0x4000:0x4088,0xdff4:0xe00a,0xe6a0:0xe7aa,0x1557a:0x155c2,0x17340:0x1737a,0xe942:0xe9ec,0xea08:0xea16}
def rename(t):return loader.rename(t).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_entry_setup_cpu.py').replace('biwn_interior_loading_cpu','biwn_entry_setup_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_ENTRY_SETUP_CPU')
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=loader.base.split(tail)
    if asm=='move.w #$2700, sr':
        return f'  case {hex(pc)}u: /* {asm} */\n   if(!(s.cpu.sr&0x2000u))return BIWN_ENTRY_SETUP_CPU_BAD_ARGUMENT;s.cpu.sr=0x2700u;s.cpu.pc={hex(nxt)}u;break;'
    if asm=='movea.l #$200000, a7':
        return f'  case {hex(pc)}u: /* {asm} */\n   s.cpu.registers[15]=0x200000u;bank(&s);s.cpu.pc={hex(nxt)}u;break;'
    if op in ['lsl.w','lsl.l','lsr.l']:
        width=2 if op.endswith('.w')else 4;bits=width*8;count=loader.base.number(parts[0]);r=loader.base.register(parts[1]);mask=0xffff if width==2 else 0xffffffff;assert 1<=count<=8
        carry=f'(v>>{bits-count})&1u'if op.startswith('lsl')else f'(v>>{count-1})&1u';value=f'(v<<{count})&{hex(mask)}u'if op.startswith('lsl')else f'v>>{count}'
        return f'  case {hex(pc)}u: /* {asm} */\n   v=s.cpu.registers[{r}]&{hex(mask)}u;u={carry};v={value};put(&s,{r},{width},v);nz(&s,v,{bits});s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));s.cpu.pc={hex(nxt)}u;break;'
    if op=='subi.l':return rename(loader.emit({**row,'assembly':asm.replace('subi.l','sub.l',1)}))
    return rename(loader.emit(row))
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';rows=[]
    for a,b in RANGES.items():assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    assert len(rows)==142
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('switch(s.cpu.pc){','if(s.cpu.pc==0xdd40u){*state=s.cpu;return BIWN_ENTRY_SETUP_CPU_READY;}switch(s.cpu.pc){')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_ENTRY_SETUP_CPU_H').replace('BIWN_ENTRY_SETUP_CPU_BAD_PC=7','BIWN_ENTRY_SETUP_CPU_BAD_PC=7,BIWN_ENTRY_SETUP_CPU_READY=8');a=header.index('/* Static');b=header.index('enum biwn_entry_setup_cpu_status biwn_entry_setup_cpu_body',a)
    header=header[:a]+'''/* Source4000 caller up toDD40, DFF4 disc-mode/TOC calls,
 * E6A0 region/video/object-list descriptors,1557A allocator,17340 lists,
 * E942/E96C/EA08 music DSP load/mailbox wait. Source private frames/banks.
 * READY8 stops beforeDD40. BIOS/GPU/video/music execution and timer
 * progression are explicit providers; generation alone proves no boot.
 * Source4000 requires supervisor entry; no privilege-exception emulation.
 * No runtime decoder/originalCPU calls. Body stops before outerRTS;
 * call consumesRTS. PriorRAMeffects retained on hosterrors. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_entry_setup_cpu.c','biwn_entry_setup_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+rename(loader.base.SUFFIX));(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},stage_sha256=hashlib.sha256(stage).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False,new_published_components=0);(session/'entry-setup-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
