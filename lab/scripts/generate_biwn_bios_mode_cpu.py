"""Actual resident BIOS3006 mode request and3544 DSA wait/retry/status code."""
import hashlib,json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry
ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_entry_setup_cpu','biwn_bios_mode_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_BIOS_MODE_CPU')
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=entry.loader.base.split(tail)
    if op.startswith('bsr'):
        target=entry.loader.base.number(parts[0]);return f'case {hex(pc)}u: /* {asm} */ CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;CHECK(invoke(&s,{hex(target)}u,{hex(nxt)}u));break;'
    if op.startswith('bset'):
        r=entry.loader.base.register(parts[1]);bit=entry.loader.base.number(parts[0])%32;assert r is not None and r<8
        return f'case {hex(pc)}u: /* {asm} */ v=s.cpu.registers[{r}];s.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((v&(1u<<{bit}))?0u:4u));s.cpu.registers[{r}]=v|(1u<<{bit});s.cpu.pc={hex(nxt)}u;break;'
    return rename(entry.emit(row))
def main():
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert hashlib.sha256(bios).hexdigest()=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b';resident=bios[0x84a6:0x92a6];rows=[]
    for a,b in [(0x3006,0x300a),(0x34d2,0x3506),(0x3544,0x357e)]:rows+=entry.loader.base.binary_tools.m68k_instructions(resident[a-0x3000:b-0x3000],a)[0]
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','');a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:];prefix='\n'.join(l for l in prefix.splitlines()if not l.startswith(('static uint32_t sx8(','static uint32_t sx16(')))+'\n'
    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_BIOS_MODE_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_bios_mode_cpu_status biwn_bios_mode_cpu_body',a)
    header=header[:a]+'''/* Actual user BIOS3006 mode/DSA wait/retry and3544 helper.
 * D0.w bits0/1 map to four DSA speed/audio-data payloads; source waits
 * for BUTCH response, preserves nested BSR/word frames, updates3E00 status
 * and retries on unmatched echo. Devices/response timing are supplied.
 * Body stops before outerRTS; call consumes it. No runtime decoder or
 * originalCPU calls. Full firmware boot/transport/GPU ISR remain separate. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_mode_cpu.c','biwn_bios_mode_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+rename(entry.rename(entry.loader.base.SUFFIX)));(src/names[1]).write_text(header);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,BIOS_sha256=hashlib.sha256(bios).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False);(session/'bios-mode-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
