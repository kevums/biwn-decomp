"""Candidate fixed geometry instruction boundaries for existing four entries."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import generate_biwn_atomic_startup_math as math
movie=math.movie;base=math.base;ROOT=math.ROOT;RANGES=[(0x1028e,0x10430),(0x10652,0x106c4)]
def rename(s):return math.rename(s).replace('biwn_atomic_startup_math','biwn_atomic_geometry').replace('BIWN_ATOMIC_STARTUP_MATH','BIWN_ATOMIC_GEOMETRY')
def emit(row):
 if row['assembly']=='sge.b d0':
  return f"  case {hex(row['address'])}u: /* sge.b d0 */\n   v=!(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u)?0xffu:0;put(&s,0,1,v);s.cpu.pc={hex(row['address']+row['size'])}u;break;"
 text=rename(movie.emit(row))
 if row['address']==0x102fe:text=text.replace('   ','   if(s.context&&!( *(uint32_t *)s.context )--)return 10;\n   ',1)
 return text
def main():
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
 for a,b in RANGES:assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=base.binary_tools.m68k_instructions(ram[a:b],a)[0]
 out=ROOT/'verification/atomic-geometry-generation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 prefix=rename(base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
 a=prefix.index('static int invoke(');b=prefix.index('#define CHECK',a);prefix=prefix[:a]+prefix[b:]
 header=rename(base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_ATOMIC_GEOMETRY_H').replace('BIWN_ATOMIC_GEOMETRY_BAD_PC=7','BIWN_ATOMIC_GEOMETRY_BAD_PC=7,BIWN_ATOMIC_GEOMETRY_DIVISION_BY_ZERO=9,BIWN_ATOMIC_GEOMETRY_SCAN_LIMIT=10')
 text='extern void biwn_instruction_observe(const void *);\n'+prefix+'\n'.join(emit(v)for v in rows)+'\n'+rename(base.SUFFIX)
 text+='''\nstatic int geo_write8(void *context,uint32_t address,uint8_t value){(void)context;(void)address;(void)value;return 2;}
static int geo_service(void *context,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)context;(void)target;return biwn_atomic_geometry_body(bus,cpu,geo_write8,geo_service,0,500000,0);}
int biwn_geometry_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit){int status;uint32_t budget=limit>=65535u?4194432u:limit*64u+128u;if(!cpu||cpu->sr&0x2000u||(cpu->pc!=0x1028eu&&cpu->pc!=0x102c4u&&cpu->pc!=0x1039cu&&cpu->pc!=0x10652u)||(cpu->pc==0x102c4u&&!limit))return 1;status=biwn_atomic_geometry_body(bus,cpu,geo_write8,geo_service,&limit,budget,0);return status==10||status==4?2:status==2?3:status;}
int biwn_geometry_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit){struct biwn_task_cpu s;uint32_t pc;int status;if(!cpu)return 1;s=*cpu;status=biwn_geometry_cpu_body(bus,&s,limit);if(status)return status;if(bus->read32(bus->context,s.registers[15],&pc))return 3;s.pc=pc;s.registers[15]+=4;s.usp=s.registers[15];*cpu=s;return 0;}
'''
 (out/'biwn_atomic_geometry.c').write_text(text);(out/'biwn_atomic_geometry.h').write_text(header);report=dict(status='generated_unverified_geometry_instruction_candidate',directory=str(out),instructions=len(rows),rows=rows,ranges=RANGES,source_sha256=hashlib.sha256(text.encode()).hexdigest(),legacy_scan_limit_error_ABI_not_yet_matched=True,new_unique_game_coverage=False,whole_game_complete=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/atomic-geometry-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
