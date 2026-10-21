"""Fixed source scheduler cases preserving legacy dispatch/yield APIs."""
import json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
import generate_biwn_movie_cpu as movie
ROOT=movie.ROOT;base=movie.loader.base
RANGES=[(0xde08,0xde5c),(0xdeb6,0xdee2),(0xdf60,0xdf6c),(0xdf7a,0xdf7c),(0xdf96,0xdf9c)]
def emit(row):
 pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];code=None
 if asm=='move usp, a1':code=['s.cpu.registers[9]=s.cpu.usp;']
 elif asm=='move a1, usp':code=['s.cpu.usp=s.cpu.registers[9];']
 elif asm.startswith('movem.l'):
  indices=[2,3,4,5,6,7,10,11,12,13,14]
  code=[f'CHECK(push(&s,s.cpu.registers[{r}],4));'for r in reversed(indices)]if asm.endswith('-(a7)')else[f'CHECK(read_value(&s,s.cpu.registers[15],4,&v));s.cpu.registers[{r}]=v;pop(&s,4);'for r in indices]
 elif asm.startswith('trap #'):
  number=int(asm[-1]);vector=0x80+4*number;target=0xde08 if number==0 else 0xdeb6
  code=[f'v=s.cpu.sr;bank(&s);s.cpu.registers[15]=s.cpu.ssp;s.cpu.sr|=0x2000u;CHECK(push(&s,{hex(nxt)}u,4));CHECK(push(&s,v,2));CHECK(read_value(&s,{hex(vector)}u,4,&v));if(v!={hex(target)}u)return 4;s.cpu.pc=v;break;']
 elif asm=='rte':
  code=['if(!(s.cpu.sr&0x2000u))return 1;CHECK(read_value(&s,s.cpu.registers[15],2,&v));pop(&s,2);CHECK(read_value(&s,s.cpu.registers[15],4,&u));pop(&s,4);s.cpu.ssp=s.cpu.registers[15];s.cpu.sr=(uint16_t)v;s.cpu.pc=u;if(!(s.cpu.sr&0x2000u))s.cpu.registers[15]=s.cpu.usp;if(!resume||(s.cpu.pc!=0xdf66u&&s.cpu.pc!=0xdf96u)){*state=s.cpu;return 0;}break;']
 elif asm=='rts':code=['CHECK(read_value(&s,s.cpu.registers[15],4,&v));pop(&s,4);s.cpu.pc=v;*state=s.cpu;return 0;']
 if code is None:
  text=movie.emit(row)
  if pc==0xde1c:text=text.replace('   ', '   if(!limit--)return 2;\n   ',1)
  return text
 if not(asm.startswith('trap')or asm in ['rte','rts']):code.append(f's.cpu.pc={hex(nxt)}u;break;')
 return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)
def main():
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();stage=(session/'nextstage-68000-candidate.bin').read_bytes();rows=[]
 for a,b in RANGES:assert ram[a:b]==stage[a-0x4000:b-0x4000];rows+=base.binary_tools.m68k_instructions(ram[a:b],a)[0]
 out=ROOT/'verification/atomic-scheduler-generation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 p=base.PREFIX;start=p.index('struct dispatch');end=p.index('static int invoke(');p=p[start:end]
 p=p.replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];')
 p=re.sub(r'static uint32_t sx(?:8|16)\([^\n]+\n','',p);a=p.index('static void shift(');b=p.index('static int read_value(',a);p=p[:a]+p[b:];p=p.replace('return 2','return 3').replace('?2:0','?3:0')
 text='#include "biwn_scheduler.h"\n#include "biwn_input_dispatch_cpu.h"\nextern void biwn_instruction_observe(const void *);\n'+p+'''\n#define CHECK(e) do{int status=(e);if(status)return status;}while(0)
static int byte_error(void *context,uint32_t address,uint8_t value){(void)context;(void)address;(void)value;return 3;}
static int run(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit,int resume){struct dispatch s;uint32_t v,u;uint64_t budget=(uint64_t)limit*64u+128u;
if(!bus||!state||!limit||!bus->read16||!bus->read32||!bus->write16||!bus->write32)return 1;
s.bus=bus;s.cpu=*state;s.write8=byte_error;s.service=0;s.context=0;
while(budget--){switch(s.cpu.pc){
'''+ '\n'.join(emit(row)for row in rows)+'''\n default:return 1;
}}return 2;}
enum biwn_scheduler_status biwn_scheduler_dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit){if(!cpu||!(cpu->sr&0x2000u))return 1;return run(bus,cpu,limit,0);}
enum biwn_scheduler_status biwn_scheduler_yield(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit){if(!cpu||cpu->sr&0x2000u||cpu->pc!=0xdf60u)return 1;return run(bus,cpu,limit,1);}
enum biwn_scheduler_status biwn_scheduler_remove_dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit){if(!cpu||!(cpu->sr&0x2000u)||cpu->pc!=0xdeb6u)return 1;return run(bus,cpu,limit,0);}
enum biwn_scheduler_status biwn_scheduler_remove(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit){if(!cpu||cpu->sr&0x2000u||cpu->pc!=0xdf7au)return 1;return run(bus,cpu,limit,1);}
enum biwn_scheduler_status biwn_scheduler_resume_saved(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu){if(!cpu||!bus||!bus->read32)return 1;if(cpu->pc!=0xdf66u&&cpu->pc!=0xdf96u)return 0;return run(bus,cpu,128,1);}
'''
 text=re.sub(r'(case 0x[0-9a-f]+u: /\*[^\n]*\*/)',r'\1\n   biwn_instruction_observe(&s.cpu);',text)
 (out/'biwn_scheduler.c').write_text(text);report=dict(status='generated_unverified_instruction_scheduler',directory=str(out),rows=rows,instructions=len(rows),ranges=RANGES,source_sha256=hashlib.sha256(text.encode()).hexdigest(),new_unique_game_coverage=False,whole_game_complete=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/atomic-scheduler-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
