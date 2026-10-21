"""Recover fixed source1B480..1B4EA task; generation alone is not verification."""
import json,hashlib
from pathlib import Path
import generate_biwn_entry_setup_cpu as gen
ROOT=gen.ROOT
observation=json.loads((ROOT/'verification/task-1b4e8-observation-current.json').read_text());ram=(Path(observation['directory'])/'task-start-RAM.bin').read_bytes();rows=gen.loader.base.binary_tools.m68k_instructions(ram[0x1b480:0x1b4ea],0x1b480)[0];stage=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'nextstage-68000-candidate.bin';assert ram[0x1b480:0x1b4ea]==stage.read_bytes()[0x1b480-0x4000:0x1b4ea-0x4000]
def rename(text):return gen.rename(text).replace('biwn_entry_setup_cpu','biwn_proximity_message_task_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_PROXIMITY_MESSAGE_TASK_CPU')
prefix=rename(gen.loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
start=prefix.index('static void shift(');end=prefix.index('static int read_value(',start);prefix=prefix[:start]+prefix[end:];prefix='\n'.join(line for line in prefix.split('\n')if not line.startswith('static uint32_t sx8('))
prefix=prefix.replace('struct dispatch s;', '(void)full_call;struct dispatch s;')
body='\n'.join(rename(gen.emit({**r,'assembly':r['assembly'].replace('addi.l','add.l',1)}))for r in rows);suffix=rename(gen.loader.base.SUFFIX);header=rename(gen.loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_PROXIMITY_MESSAGE_TASK_CPU_H');start=header.index('/* Static');end=header.index('enum biwn_proximity_message_task_cpu_status biwn_proximity_message_task_cpu_body',start);header=header[:start]+'''/* Source1B480 task initialization and warm1B4E8 loop. Enable43D98,
 * once46880, (X-24380)^2+(Z-26784)^2 signedcomparison<=1024, then
 * source207CC message3 call and flag1. E540multiply and207CCmessage
 * are explicit service interfaces. FullCPU/privateframes/stackbanks.
 * Task yields atDF60 with actualJSRframe. Allsourceblocks generated,
 * helper/device/globaltiming/game proof separate. */
'''+header[end:];dest=ROOT/'projects/black-ice-white-noise/restoration/experimental';dest.mkdir(exist_ok=True);(dest/'biwn_proximity_message_task_cpu.c').write_text(prefix+body+'\n'+suffix);(dest/'biwn_proximity_message_task_cpu.h').write_text(header)
record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_range=['0x1b480','0x1b4ea'],source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [dest/'biwn_proximity_message_task_cpu.c',dest/'biwn_proximity_message_task_cpu.h']},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False)
(ROOT/'verification/proximity-message-task-generation.json').write_text(json.dumps(record,indent=2)+'\n');print(len(rows),'fixed source instructions generated')
