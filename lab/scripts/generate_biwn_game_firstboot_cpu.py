"""Fixed game180000 loader through natural JMP4000, BIOS services supplied."""
import hashlib,json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry
ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_entry_setup_cpu','biwn_game_firstboot_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_GAME_FIRSTBOOT_CPU')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);boot=(session/'boot-payload-68000-candidate.bin').read_bytes();assert hashlib.sha256(boot).hexdigest()=='235b342638e4face19e82b68d1fdd6592e58dbf689792ee41d572db465cfc8a4';rows=entry.loader.base.binary_tools.m68k_instructions(boot[:0x188],0x180000)[0]
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('switch(s.cpu.pc){','if(s.cpu.pc==0x4000u){*state=s.cpu;return BIWN_GAME_FIRSTBOOT_CPU_READY;}if(s.service(s.context,s.bus,&s.cpu,s.cpu.pc))return BIWN_GAME_FIRSTBOOT_CPU_SERVICE_ERROR;switch(s.cpu.pc){')
    prefix=prefix.replace('s.bus=bus;', '(void)full_call;s.bus=bus;')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static uint32_t sx16('))+'\n'
    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_GAME_FIRSTBOOT_CPU_H').replace('BIWN_GAME_FIRSTBOOT_CPU_BAD_PC=7','BIWN_GAME_FIRSTBOOT_CPU_BAD_PC=7,BIWN_GAME_FIRSTBOOT_CPU_READY=8')
    a=header.index('/* Static');b=header.index('enum biwn_game_firstboot_cpu_status biwn_game_firstboot_cpu_body',a)
    header=header[:a]+'''/* Actual game180000..180188 video/GPU copy, BIOS mode/marker setup,
 * firmware TOC selection/MSF subtraction, marker read/progress>100000,
 * I2S stop/GPU stop flag/poll and natural JMP4000. READY8 stops before
 * game4000 instruction. BIOS/controller/GPU execution, initial boot payload,
 * firmware TOC/state and event delivery are dependencies, not scripted here.
 * Service receives sourcePC before each selected instruction for trace.
 * No runtime decoder/originalCPU execution. Complete BIOS boot separate. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_game_firstboot_cpu.c','biwn_game_firstboot_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(rename(entry.emit(r))for r in rows)+'\n'+rename(entry.rename(entry.loader.base.SUFFIX)));(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,boot_sha256=hashlib.sha256(boot).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False)
    (session/'game-firstboot-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
