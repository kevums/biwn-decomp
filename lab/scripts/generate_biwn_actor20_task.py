"""Recover fixed source1B480..1B4EA task; generation alone is not verification."""
import json,hashlib
from pathlib import Path
import generate_biwn_entry_setup_cpu as gen
ROOT=gen.ROOT
observation=json.loads((ROOT/'verification/natural-proximity-task-current.json').read_text());ram=(Path(observation['directory'])/'native-RAM.bin').read_bytes();rows=gen.loader.base.binary_tools.m68k_instructions(ram[0xec20:0xed4e],0xec20)[0];stage=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'nextstage-68000-candidate.bin';assert ram[0xec20:0xed4e]==stage.read_bytes()[0xec20-0x4000:0xed4e-0x4000]
def rename(text):return gen.rename(text).replace('biwn_entry_setup_cpu','biwn_actor20_task_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_ACTOR20_TASK_CPU')
prefix=rename(gen.loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
# This source uses MOVEQ and ASL, so retain sx8/shift helpers.
prefix=prefix.replace('struct dispatch s;', '(void)full_call;struct dispatch s;')
body='\n'.join(rename(gen.emit({**r,'assembly':r['assembly'].replace('addi.l','add.l',1)}))for r in rows);suffix=rename(gen.loader.base.SUFFIX);header=rename(gen.loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_ACTOR20_TASK_CPU_H');start=header.index('/* Static');end=header.index('enum biwn_actor20_task_cpu_status biwn_actor20_task_cpu_body',start);header=header[:start]+'''/* SourceEC20..ED4E type20actor scan/lifecycle task. Scans40records
 * at49D6C,stride206; initializes/updates type20 through declared
 * 101E0/10252/1404C/EB04/13C9A/resource/sound helper interfaces.
 * Real source privateframes/stackbanks/yields. Generation is not
 * verification of lifecycle/helpers/audio/game/globaltiming. */
'''+header[end:];dest=ROOT/'projects/black-ice-white-noise/restoration/experimental';dest.mkdir(exist_ok=True);(dest/'biwn_actor20_task_cpu.c').write_text(prefix+body+'\n'+suffix);(dest/'biwn_actor20_task_cpu.h').write_text(header)
record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_range=['0xec20','0xed4e'],source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [dest/'biwn_actor20_task_cpu.c',dest/'biwn_actor20_task_cpu.h']},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False)
(ROOT/'verification/actor20-task-generation.json').write_text(json.dumps(record,indent=2)+'\n');print(len(rows),'fixed source instructions generated')
