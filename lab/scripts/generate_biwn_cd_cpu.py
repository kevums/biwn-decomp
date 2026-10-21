"""Static CPU reconstruction of the game's offset and CD BIOS wrappers."""
import hashlib, json
from pathlib import Path
import generate_biwn_resource_cpu as resource
base = resource.base
ROOT = base.ROOT
RANGES = {0xd1e0: 0xd206, 0xd206: 0xd2a0, 0xd2f0: 0xd306, 0xd306: 0xd30a}

def emit(row):
    pc = row['address']; nxt = pc+row['size']
    op, _, tail = row['assembly'].partition(' ')
    kind = op.split('.')[0]; parts = base.split(tail)
    if kind == 'bvs':
        code = [f's.cpu.pc=(s.cpu.sr&2u)?{hex(base.number(parts[0]))}u:{hex(nxt)}u;break;']
    elif kind == 'bsr':
        target = base.number(parts[0])
        code = [f'CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;CHECK(invoke(&s,{hex(target)}u,{hex(nxt)}u));break;']
    elif kind == 'divu':
        reg = base.register(parts[1])
        code = [resource.load(parts[0], 2), 'v&=65535u;if(!v)return BIWN_CD_CPU_DIVIDE_ZERO;', f'u=s.cpu.registers[{reg}];',
                'if(u/v>65535u){s.cpu.sr=(uint16_t)((s.cpu.sr&~3u)|2u);}else{',
                f's.cpu.registers[{reg}]=((u%v)<<16)|(u/v);nz(&s,u/v,16);}}', f's.cpu.pc={hex(nxt)}u;break;']
    elif kind in ['lsl', 'lsr']:
        width = {'b': 8, 'w': 16, 'l': 32}[op[-1]]
        code = [resource.load(parts[0], 4, 'u'), f'logical_shift(&s,{base.register(parts[1])},{width},u&63u,{int(kind=="lsl")});s.cpu.pc={hex(nxt)}u;break;']
    elif pc == 0xd306:
        assert row['assembly'] == 'jmp $3042.w'
        code = ['s.cpu.pc=0x3042u;CHECK(s.service(s.context,s.bus,&s.cpu,0x3042u)?3:0);',
                'if(full_call){CHECK(read_value(&s,s.cpu.registers[15],4,&v));s.cpu.pc=v;pop(&s,4);}*state=s.cpu;return BIWN_CD_CPU_OK;']
    else:
        return resource.emit(row).replace('BIWN_RESOURCE_CPU', 'BIWN_CD_CPU')
    return '  case '+hex(pc)+'u: /* '+row['assembly']+' */\n   '+'\n   '.join(code)

def main():
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session/'nextstage-68000-candidate.bin').read_bytes()
    snapshot = (ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    rows = []
    for start, end in RANGES.items():
        assert snapshot[start:end] == image[start-0x4000:end-0x4000]
        part, _ = base.binary_tools.m68k_instructions(snapshot[start:end], start)
        rows += part
    prefix = base.PREFIX.replace('biwn_input_dispatch_cpu', 'biwn_cd_cpu').replace('biwn_dispatch_cpu_status', 'biwn_cd_cpu_status').replace('BIWN_DISPATCH_CPU', 'BIWN_CD_CPU').replace('generate_biwn_input_dispatch_cpu.py', 'generate_biwn_cd_cpu.py')
    prefix = prefix.replace('s->cpu.usp=s->cpu.registers[15];', 'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)', '')
    prefix = '\n'.join(line for line in prefix.split('\n') if not line.startswith('static uint32_t sx'))
    helper = '''static void logical_shift(struct dispatch *s,unsigned r,unsigned bits,unsigned n,int left){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,v=s->cpu.registers[r]&mask;unsigned c=0,i;
 for(i=0;i<n;i++){if(left){c=(v>>(bits-1))&1u;v=(v<<1)&mask;}else{c=v&1u;v>>=1;}}
 put(s,r,bits/8,v);nz(s,v,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(n?0x13u:3u))|(c?(n?0x11u:1u):0));}
'''
    prefix = prefix.replace('static int read_value', helper+'static int read_value')
    suffix = base.SUFFIX.replace('biwn_input_dispatch_cpu', 'biwn_cd_cpu').replace('biwn_dispatch_cpu_status', 'biwn_cd_cpu_status').replace('BIWN_DISPATCH_CPU', 'BIWN_CD_CPU')
    header = '''#ifndef BIWN_CD_CPU_H
#define BIWN_CD_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_cd_cpu_status {BIWN_CD_CPU_OK=0,BIWN_CD_CPU_BAD_ARGUMENT=1,
 BIWN_CD_CPU_BUS_ERROR=2,BIWN_CD_CPU_SERVICE_ERROR=3,BIWN_CD_CPU_WORK_LIMIT=4,
 BIWN_CD_CPU_BAD_RETURN=5,BIWN_CD_CPU_YIELDED=6,BIWN_CD_CPU_BAD_PC=7,
 BIWN_CD_CPU_DIVIDE_ZERO=8};
/* Fixed source-specific CPU blocks: D1E0 division, D206 offset/MSF,
 * D2F0 start and D306 stop. Body stops at outer RTS (or BIOS tail RTS);
 * call consumes it. D1E0 nested calls execute through the provider.
 * BIOS303C/3042 remain explicit providers, not reconstructed firmware.
 * Zero divisor returns host status8, not a reproduced CPU exception.
 * DIVU overflow N/Z are architecturally undefined; subsequent source
 * instructions replace them before return. No asynchronous loading,
 * hardware timing or full-game claim. No runtime CPU instruction decode. */
enum biwn_cd_cpu_status biwn_cd_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_cd_cpu_status biwn_cd_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
    folder = ROOT/'projects/black-ice-white-noise/restoration'
    text = prefix+'\n'.join(emit(row) for row in rows)+'\n'+suffix
    (folder/'biwn_cd_cpu.c').write_text(text); (folder/'biwn_cd_cpu.h').write_text(header)
    manifest = {'status': 'generated_unverified', 'instructions': len(rows), 'instructions_decoded': rows, 'ranges': {hex(a): hex(b) for a,b in RANGES.items()}, 'stage_sha256': hashlib.sha256(image).hexdigest(), 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'source_sha256': {name: hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in ['biwn_cd_cpu.c', 'biwn_cd_cpu.h']}, 'whole_game_complete': False}
    (session/'cd-wrapper-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='instructions_decoded'}))

if __name__ == '__main__': main()
