"""Source12EE0..13440; keep13116..13122 as jump-table data."""
import json,hashlib
from pathlib import Path
import generate_biwn_entry_setup_cpu as gen
ROOT=gen.ROOT;observed=json.loads((ROOT/'verification/natural-actor6-task-current.json').read_text());ram=(Path(observed['directory'])/'native-RAM.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert ram[0x12ee0:0x13440]==stage[0x12ee0-0x4000:0x13440-0x4000];rows=[]
for a,b in [(0x12ee0,0x13116),(0x13122,0x13440)]:rows+=gen.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
def rename(text):return gen.rename(text).replace('biwn_entry_setup_cpu','biwn_actor5_task_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_ACTOR5_TASK_CPU')
prefix=rename(gen.loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','').replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)').replace('struct dispatch s;', '(void)full_call;struct dispatch s;')
def emit(row):
 if row['address']==0x1310e:return '''  case 0x1310eu: /* MOVE.W13116(PC,D0.L),D0: table words are data */
   CHECK(read_value(&s,0x13116u+s.cpu.registers[0],2,&v));put(&s,0,2,v);nz(&s,v,16);s.cpu.pc=0x13112u;break;'''
 if row['address']==0x13112:return '''  case 0x13112u: /* JMP13116(PC,D0.W), signed word displacement, CCR unchanged */
   s.cpu.pc=0x13116u+sx16((uint16_t)s.cpu.registers[0]);break;'''
 return rename(gen.emit({**row,'assembly':row['assembly'].replace('addi.l','add.l',1)}))
body='\n'.join(emit(row)for row in rows);header=rename(gen.loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_ACTOR5_TASK_CPU_H');start=header.index('/* Static');end=header.index('enum biwn_actor5_task_cpu_status biwn_actor5_task_cpu_body',start);header=header[:start]+'''/* Source type5 actor scan, respawn, follow, approach, dialogue/distance task.
 * Table13116..13122 stays data; reads runtime bus words and signs JMP offset.
 * Source privateframes, both stack banks and nestedDF8C waits retained.
 * Helpers remain explicit; generation is not validation or fullgame proof. */
'''+header[end:];dest=ROOT/'projects/black-ice-white-noise/restoration/experimental';(dest/'biwn_actor5_task_cpu.c').write_text(prefix+body+'\n'+rename(gen.loader.base.SUFFIX));(dest/'biwn_actor5_task_cpu.h').write_text(header)
report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,code_ranges=[['0x12ee0','0x13116'],['0x13122','0x13440']],jump_table_data_interval=['0x13116','0x13122'],table_bytes=ram[0x13116:0x13122].hex(),table_is_not_instruction_code=True,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [dest/'biwn_actor5_task_cpu.c',dest/'biwn_actor5_task_cpu.h']},whole_game_complete=False);(ROOT/'verification/actor5-task-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(len(rows),'source instructions generated;6data words excluded')
