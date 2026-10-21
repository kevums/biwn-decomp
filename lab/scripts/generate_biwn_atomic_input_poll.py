"""Fixed E4C0 input polling instruction cases, actual row-select bus retained."""
import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
import generate_biwn_atomic_startup_math as math
movie=math.movie;base=math.base;ROOT=math.ROOT

def rename(s):return math.rename(s).replace('biwn_atomic_startup_math','biwn_atomic_input_poll').replace('BIWN_ATOMIC_STARTUP_MATH','BIWN_ATOMIC_INPUT_POLL')
def emit(row):
 pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=base.split(tail)
 if op in ['ror.l','rol.l']:
  count=base.number(parts[0]);reg=base.register(parts[1]);left=op.startswith('rol')
  rotate=f'(v<<{count})|(v>>{32-count})'if left else f'(v>>{count})|(v<<{32-count})'
  carry='v&1u'if left else'v>>31'
  return f'  case {hex(pc)}u: /* {asm} */\n   v=s.cpu.registers[{reg}];v={rotate};put(&s,{reg},4,v);nz(&s,v,32);s.cpu.sr=(uint16_t)(s.cpu.sr|({carry}));s.cpu.pc={hex(nxt)}u;break;'
 if op=='eor.l':
  src,dst=map(base.register,parts)
  return f'  case {hex(pc)}u: /* {asm} */\n   v=s.cpu.registers[{src}]^s.cpu.registers[{dst}];put(&s,{dst},4,v);nz(&s,v,32);s.cpu.pc={hex(nxt)}u;break;'
 return rename(movie.emit(row))
def main():
 ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=base.binary_tools.m68k_instructions(ram[0xe4c0:0xe53c],0xe4c0)[0];out=ROOT/'verification/atomic-input-poll-generation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 prefix=rename(base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
 a=prefix.index('static int invoke(');b=prefix.index('#define CHECK',a);prefix=prefix[:a]+prefix[b:]
 a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:];prefix=re.sub(r'static uint32_t sx16\([^\n]+\n','',prefix)
 a=prefix.index('static uint32_t alu(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
 header=rename(base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_ATOMIC_INPUT_POLL_H');text='extern void biwn_instruction_observe(const void *);\n'+prefix+'\n'.join(emit(v)for v in rows)+'\n'+rename(base.SUFFIX)
 text+='''\nstatic int poll_write8(void *context,uint32_t address,uint8_t value){(void)context;(void)address;(void)value;return 2;}
static int poll_service(void *context,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)context;(void)bus;(void)cpu;(void)target;return 1;}
int biwn_input_poll_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu){if(!cpu||cpu->pc!=0xe4c0u)return 1;return biwn_atomic_input_poll_body(bus,cpu,poll_write8,poll_service,0,128,0);}
int biwn_input_poll_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu){if(!cpu||cpu->pc!=0xe4c0u)return 1;return biwn_atomic_input_poll_call(bus,cpu,poll_write8,poll_service,0,128,0);}
'''
 (out/'biwn_atomic_input_poll.c').write_text(text);(out/'biwn_atomic_input_poll.h').write_text(header);report=dict(status='generated_unverified_input_instruction_candidate',directory=str(out),instructions=len(rows),rows=rows,source_sha256=hashlib.sha256(text.encode()).hexdigest(),physical_controller_verified=False,new_unique_game_coverage=False,whole_game_complete=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/atomic-input-poll-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
