"""Actual BIOS303C read/seek setup,3042 I2S stop,304E progress CPU code."""
import hashlib,json
from pathlib import Path
import generate_biwn_bios_toc_cpu as toc
entry=toc.entry;mode=toc.mode;ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_bios_mode_cpu','biwn_bios_transport_cpu').replace('BIWN_BIOS_MODE_CPU','BIWN_BIOS_TRANSPORT_CPU')
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=entry.loader.base.split(tail)
    if op.startswith('bclr'):
        r=entry.loader.base.register(parts[1]);bit=entry.loader.base.number(parts[0])%32;assert r is not None and r<8
        return f'case {hex(pc)}u: /* {asm} */ v=s.cpu.registers[{r}];s.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((v&(1u<<{bit}))?0u:4u));s.cpu.registers[{r}]=v&~(1u<<{bit});s.cpu.pc={hex(nxt)}u;break;'
    return rename(toc.emit(row).replace('biwn_bios_toc_cpu','biwn_bios_mode_cpu').replace('BIWN_BIOS_TOC_CPU','BIWN_BIOS_MODE_CPU'))
def main():
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert hashlib.sha256(bios).hexdigest()=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b';resident=bios[0x84a6:0x92a6];rows=[]
    for a,b in [(0x303c,0x3040),(0x3042,0x3046),(0x304e,0x3052),(0x3610,0x3742)]:rows+=entry.loader.base.binary_tools.m68k_instructions(resident[a-0x3000:b-0x3000],a)[0]
    prefix=rename(mode.rename(entry.rename(entry.loader.base.PREFIX))).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(('static uint32_t sx8(','static uint32_t sx16(','static uint32_t alu(')))+'\n'
    header=rename(mode.rename(entry.rename(entry.loader.base.HEADER))).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_BIOS_TRANSPORT_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_bios_transport_cpu_status biwn_bios_transport_cpu_body',a)
    header=header[:a]+'''/* Actual resident BIOS303C read/seek setup and3712 TX wait,3042 I2S
 * disable and304E progress-pointer query. Source GPU transfer descriptor,
 * optional3072bit7 instruction patches and private BSR frames retained.
 * Bus/controller progression supplied; this group does not move payload
 * bytes or execute CDGPU ISR. No runtime decoding/originalCPU calls.
 * Body stops before outerRTS; call consumes it. Firmware boot separate. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_transport_cpu.c','biwn_bios_transport_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+rename(mode.rename(entry.rename(entry.loader.base.SUFFIX))));(src/names[1]).write_text(header);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,BIOS_sha256=hashlib.sha256(bios).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False);(session/'bios-transport-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
