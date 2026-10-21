"""Source DDfe STOP/de02 frame-PC adjustment/RTE and observed2000 operand instruction."""
import json,hashlib
from pathlib import Path
import generate_biwn_video_cpu as video
ROOT=video.ROOT
rename=lambda s:video.rename(s).replace('biwn_video_cpu','biwn_movie_privilege_cpu').replace('BIWN_VIDEO_CPU','BIWN_MOVIE_PRIVILEGE_CPU')
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=video.movie.loader.base.binary_tools.m68k_instructions(ram[0xddfe:0xde08],0xddfe)[0]+video.movie.loader.base.binary_tools.m68k_instructions(ram[0x22a10:0x22a12],0x22a10)[0]
    assert [(x['address'],x['assembly']) for x in rows]==[(0xddfe,'stop #$2000'),(0xde02,'addq.l #$2, $2(a7)'),(0xde06,'rte'),(0x22a10,'move.l d0, d0')]
    prefix=rename(video.movie.loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:];prefix='\n'.join(line for line in prefix.splitlines() if not line.startswith(('static uint32_t sx8(', 'static uint32_t sx16(', 'static int invoke(', 'static void pop(', 'static int push(')))+'\n'
    prefix=prefix.replace('struct dispatch s;uint32_t v,u;','struct dispatch s;uint32_t v,u;(void)full_call;')
    header=rename(video.movie.loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_MOVIE_PRIVILEGE_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_movie_privilege_cpu_status biwn_movie_privilege_cpu_body',a)
    header=header[:a]+'''/* Source DDfe privilege STOP, de02 saved-PC+2, de06 RTE and observed
 * 22A10 operand execution (2000=move.lD0,D0) before normal22A12.
 * Four static source instructions. User STOP exception and nested GPU IRQ
 * use separate real sixbyte frames. No original CPU/runtime decoder.
 * Source STOP yields6 before execution; event API applies its architectural
 * state. RTE commits/restores both stackbanks. Handler/noop handoffs return0.
 * No other privilege instruction, trace, scheduler or physicaltiming proof. */
'''+header[b:]
    cases=[]
    for r in rows:
        if r['address']==0xddfe:cases.append('case 0xddfeu: /* stop #$2000 */\n if(stop_on_yield){*state=s.cpu;return BIWN_MOVIE_PRIVILEGE_CPU_YIELDED;}return 8;')
        else:cases.append(rename(video.emit(r)))
    suffix=rename(video.movie.loader.base.SUFFIX).replace('default:return BIWN_MOVIE_PRIVILEGE_CPU_BAD_PC;','default:return BIWN_MOVIE_PRIVILEGE_CPU_BAD_PC;').replace('}}return BIWN_MOVIE_PRIVILEGE_CPU_WORK_LIMIT;', '}if(s.cpu.pc==0x22a12u){*state=s.cpu;return 0;}}return BIWN_MOVIE_PRIVILEGE_CPU_WORK_LIMIT;')
    header=header.replace('BIWN_MOVIE_PRIVILEGE_CPU_BAD_PC=7','BIWN_MOVIE_PRIVILEGE_CPU_BAD_PC=7,BIWN_MOVIE_PRIVILEGE_CPU_PRIVILEGE_UNIMPLEMENTED=9')
    header=header.replace('#endif','''int biwn_movie_user_STOP_exception(struct biwn_world_bus *,struct biwn_task_cpu *);
int biwn_movie_privilege_STOP_event(struct biwn_task_cpu *);
int biwn_movie_wait_GPU_interrupt(struct biwn_world_bus *,struct biwn_task_cpu *);
int biwn_movie_user_VBI_event(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif''')
    events='''
int biwn_movie_user_STOP_exception(struct biwn_world_bus *bus,struct biwn_task_cpu *state){struct biwn_task_cpu s;uint32_t vector;if(!bus||!state||!bus->read32||!bus->write16||!bus->write32||state->pc!=0x22a0eu||(state->sr&0xa000u))return 1;s=*state;s.usp=s.registers[15];s.registers[15]=s.ssp;s.registers[15]-=4u;if(bus->write32(bus->context,s.registers[15],s.pc))return 2;s.registers[15]-=2u;if(bus->write16(bus->context,s.registers[15],s.sr))return 2;s.ssp=s.registers[15];s.sr|=0x2000u;if(bus->read32(bus->context,0x20u,&vector))return 2;if(vector!=0xddfeu)return 7;s.pc=vector;*state=s;return 0;}
int biwn_movie_privilege_STOP_event(struct biwn_task_cpu *s){if(!s||s->pc!=0xddfeu||!(s->sr&0x2000u))return 1;s->ssp=s->registers[15];s->sr=0x2000u;s->pc=0xde02u;return 0;}
static int irq(struct biwn_world_bus *bus,struct biwn_task_cpu *state){struct biwn_task_cpu s;uint32_t vector;if(!bus||!state||!bus->read32||!bus->write16||!bus->write32||(state->sr&0x8000u))return 1;s=*state;if((s.sr&0x0700u)>=0x0200u)return 0;if(!(s.sr&0x2000u)){s.usp=s.registers[15];s.registers[15]=s.ssp;}s.registers[15]-=4u;if(bus->write32(bus->context,s.registers[15],s.pc))return 2;s.registers[15]-=2u;if(bus->write16(bus->context,s.registers[15],s.sr))return 2;s.ssp=s.registers[15];s.sr=(uint16_t)((s.sr&~0x8700u)|0x2200u);if(bus->read32(bus->context,0x100u,&vector))return 2;if(vector!=0xe7d4u)return 7;s.pc=vector;*state=s;return 0;}
int biwn_movie_wait_GPU_interrupt(struct biwn_world_bus *b,struct biwn_task_cpu *s){if(!s||!(s->sr&0x2000u)||(s->pc!=0xde02u&&s->pc!=0x22a12u))return 1;return irq(b,s);}
int biwn_movie_user_VBI_event(struct biwn_world_bus *b,struct biwn_task_cpu *s){if(!s||s->pc!=0xd4a8u)return 1;return irq(b,s);}
'''
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_movie_privilege_cpu.c','biwn_movie_privilege_cpu.h'];(source/names[0]).write_text(prefix+'\n'.join(cases)+suffix+events);(source/names[1]).write_text(header)
    record=dict(status='generated_unverified',instructions=4,instructions_decoded=rows,source_sha256={n:sha((source/n).read_bytes()) for n in names},whole_game_complete=False);(session/'movie-privilege-fullCPU-generation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(instructions=4,source_sha256=record['source_sha256'])))
if __name__=='__main__':main()
