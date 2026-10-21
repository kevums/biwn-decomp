"""Source E9EC stop request and EA08 mailbox polling, full CPU/private frames."""
import hashlib,json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry
ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_entry_setup_cpu','biwn_music_stop_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_MUSIC_STOP_CPU')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';rows=entry.loader.base.binary_tools.m68k_instructions(stage[0xe9ec-0x4000:0xea16-0x4000],0xe9ec)[0]
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(l for l in prefix.splitlines()if not l.startswith(('static uint32_t sx16(', 'static uint32_t sx8(', 'static void put(')))+'\n'

    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_MUSIC_STOP_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_music_stop_cpu_status biwn_music_stop_cpu_body',a)
    header=header[:a]+'''/* Source E9EC writes command1/CPU interrupt and polls EA08.
 * Full source CPU/stackbanks/private JSR frame. DSP acknowledgement is
 * required from a declared source DSP provider; no mailbox completion script
 * or original CPU instruction calls in this translation. Body stops before
 * outer RTS; call consumes it. Generation alone is not verification. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_music_stop_cpu.c','biwn_music_stop_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(rename(entry.emit(r))for r in rows)+'\n'+rename(entry.rename(entry.loader.base.SUFFIX)));(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False);(session/'music-stop-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
