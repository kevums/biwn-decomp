"""Source firmware video handler and reached graphics helpers, fixed CPU C."""
import hashlib,json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry
ROOT=entry.ROOT
rename=lambda t:t.replace('biwn_entry_setup_cpu','biwn_firmware_video_irq_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_FIRMWARE_VIDEO_IRQ_CPU')

def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');kind=op.split('.')[0];parts=entry.loader.base.split(tail);code=None
    if kind in ['bsr','jsr']:
        if parts[0].startswith('$'):target=hex(entry.loader.base.number(parts[0].split('.')[0]))+'u'
        else:target=entry.loader.framed.address(parts[0])
        code=f'u={target};CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc=u;break;'
    elif kind=='rts':code='CHECK(read_value(&s,s.cpu.registers[15],4,&v));pop(&s,4);s.cpu.pc=v;break;'
    elif kind=='rte':code='if(!(s.cpu.sr&0x2000u))return 1;CHECK(read_value(&s,s.cpu.registers[15],2,&u));CHECK(read_value(&s,s.cpu.registers[15]+2u,4,&v));s.cpu.registers[15]+=6u;s.cpu.ssp=s.cpu.registers[15];s.cpu.sr=(uint16_t)u;s.cpu.pc=v;if(!(u&0x2000u))s.cpu.registers[15]=s.cpu.usp;*state=s.cpu;return BIWN_FIRMWARE_VIDEO_IRQ_CPU_RETURNED;'
    elif kind in ['bset','bclr']:
        r=entry.loader.base.register(parts[1]);width=4 if r is not None and r<8 else 1;bit=entry.loader.base.number(parts[0])%(width*8)
        lines=[entry.loader.resource.load(parts[1],width),'s.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((v&'+hex(1<<bit)+'u)?0u:4u));','v'+('|='if kind=='bset'else'&=~')+hex(1<<bit)+'u;',entry.loader.resource.store(parts[1],width),f's.cpu.pc={hex(nxt)}u;break;']
        code=' '.join(lines)
    elif op in ['lsr.w','lsl.w'] and not parts[0].startswith('#'):
        count=entry.loader.base.register(parts[0]);reg=entry.loader.base.register(parts[1]);assert count is not None and reg is not None
        line='carry=(v>>15)&1u;v=(v<<1)&0xffffu;'if kind=='lsl'else'carry=v&1u;v>>=1;'
        code=f'{{uint32_t amount=s.cpu.registers[{count}]&63u,carry=0u;v=s.cpu.registers[{reg}]&0xffffu;for(uint32_t i=0;i<amount;i++){{{line}}}put(&s,{reg},2,v);nz(&s,v,16);s.cpu.sr=(uint16_t)((s.cpu.sr&~(amount?0x13u:3u))|(carry?(amount?0x11u:1u):0u));}}s.cpu.pc={hex(nxt)}u;break;'
    elif kind=='ror':
        assert parts[0].startswith('#');count=entry.loader.base.number(parts[0]);reg=entry.loader.base.register(parts[1]);width=2 if op.endswith('.w')else 4;bits=width*8;mask=(1<<bits)-1
        code=f'v=s.cpu.registers[{reg}]&{hex(mask)}u;u=(v>>{count-1})&1u;v=((v>>{count})|(v<<{bits-count}))&{hex(mask)}u;put(&s,{reg},{width},v);nz(&s,v,{bits});s.cpu.sr=(uint16_t)((s.cpu.sr&~3u)|u);s.cpu.pc={hex(nxt)}u;break;'
    elif kind=='mulu':
        reg=entry.loader.base.register(parts[1]);code=entry.loader.resource.load(parts[0],2)+f'v=(v&0xffffu)*(s.cpu.registers[{reg}]&0xffffu);s.cpu.registers[{reg}]=v;nz(&s,v,32);s.cpu.pc={hex(nxt)}u;break;'
    if code is None:return rename(entry.emit(row))
    return f'case {hex(pc)}u: /* {asm} */ {code}'

def main():
    probe=json.loads((ROOT/'verification/firmware-CPU-video-IRQ-native-discovery.json').read_text());irq=probe['CPU_video_IRQ_observation'];assert irq['stop_reason']=='source_handler_RTE_returned'and irq['source_mailbox_clear_reached']and not irq['source_C_verified']
    rows=irq['visited_instructions'];assert len(rows)==327
    ram=(Path(probe['directory'])/'RAM-after-video-IRQ.bin').read_bytes()
    for r in rows:assert ram[r['address']:r['address']+r['size']].hex()==r['bytes']
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static int invoke('))+'\n'
    prefix=prefix.replace('s.bus=bus;', '(void)full_call;s.bus=bus;')
    prefix=prefix.replace('switch(s.cpu.pc){','if(s.service(s.context,s.bus,&s.cpu,s.cpu.pc))return BIWN_FIRMWARE_VIDEO_IRQ_CPU_SERVICE_ERROR;switch(s.cpu.pc){')
    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_FIRMWARE_VIDEO_IRQ_CPU_H').replace('BIWN_FIRMWARE_VIDEO_IRQ_CPU_BAD_PC=7','BIWN_FIRMWARE_VIDEO_IRQ_CPU_BAD_PC=7,BIWN_FIRMWARE_VIDEO_IRQ_CPU_RETURNED=8')
    a=header.index('/* Static');b=header.index('enum biwn_firmware_video_irq_cpu_status biwn_firmware_video_irq_cpu_body',a)
    header=header[:a]+'''/* Observed firmware video handler194C90 and327 reached CPU instructions,
 * including graphics helpers and source-patched RTS196446. No runtime
 * decoder/originalCPU; internal source BSR/JSR/RTS stay in one fixed body.
 * RETURNED8 consumes real six-byte RTE frame and stops at interruptedPC.
 * Service observes sourcePC before each instruction. Initial live firmware
 * RAM/CPU/GPU/peripheral state and explicit VBI event are dependencies.
 * Reached path only; other graphics inputs/events/helper branches, GPU
 * execution, global timing/disc loading/fullboot/playability separate. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_firmware_video_irq_cpu.c','biwn_firmware_video_irq_cpu.h'];(source/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+rename(entry.rename(entry.loader.base.SUFFIX)));(source/names[1]).write_text(header)
    event='''#include "biwn_firmware_video_irq_cpu.h"
int biwn_firmware_video_irq_event(struct biwn_world_bus *bus,struct biwn_task_cpu *state){struct biwn_task_cpu s;uint16_t old;uint32_t vector;if(!bus||!state||!bus->read32||!bus->write16||!bus->write32)return 1;if((state->sr&0x0700u)>=0x0200u)return 3;s=*state;old=s.sr;if(old&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];s.registers[15]=s.ssp;s.sr=(uint16_t)((old&~0x8700u)|0x2200u);s.registers[15]-=4u;if(bus->write32(bus->context,s.registers[15],s.pc))return 2;s.registers[15]-=2u;if(bus->write16(bus->context,s.registers[15],old))return 2;s.ssp=s.registers[15];if(bus->read32(bus->context,0x100u,&vector))return 2;if(vector!=0x194c90u)return 1;s.pc=vector;*state=s;return 0;}
'''
    (source/'biwn_firmware_video_irq_event.c').write_text(event);names.append('biwn_firmware_video_irq_event.c')
    mapping=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,native_discovery=probe['directory'],source_BIOS_sha256=probe['source_BIOS_sha256'],source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),implementation_authorship='coordinator',full_firmware_boot_verified=False,whole_game_complete=False)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);(session/'firmware-video-IRQ-generation.json').write_text(json.dumps(mapping,indent=2)+'\n');print(json.dumps({k:v for k,v in mapping.items()if k!='instructions_decoded'}))

if __name__=='__main__':main()
