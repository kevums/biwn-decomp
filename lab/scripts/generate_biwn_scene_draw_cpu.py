"""Fixed CPU scene dispatch, framebuffer clear and triple-buffer rotation."""
import hashlib
import json
from pathlib import Path
import generate_biwn_resource_cpu as resource

base = resource.base
ROOT = base.ROOT
RANGES = {0xe03a: 0xe098, 0x17e0e: 0x17f14, 0x17f14: 0x17f68}

def emit(row):
    if row['assembly'] == 'lsr.w #$1, d0':
        # Logical shift preserves D0's upper word; C and X receive old bit 0.
        return ('  case 0xe044u: /* lsr.w #$1, d0 */\n'
                '   u=s.cpu.registers[0]&1u;v=(s.cpu.registers[0]&0xffffu)>>1;'
                'put(&s,0,2,v);nz(&s,v,16);'
                's.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));'
                's.cpu.pc=0xe046u;break;')
    return resource.emit(row).replace('BIWN_RESOURCE_CPU', 'BIWN_SCENE_DRAW_CPU')

def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest() == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows = []
    for start, end in RANGES.items():
        assert snapshot[start:end] == image[start-0x4000:end-0x4000]
        decoded, _ = base.binary_tools.m68k_instructions(snapshot[start:end], start)
        rows.extend(decoded)
    assert len(rows) == 102
    prefix = base.PREFIX.replace('generate_biwn_input_dispatch_cpu.py', 'generate_biwn_scene_draw_cpu.py').replace('biwn_input_dispatch_cpu', 'biwn_scene_draw_cpu').replace('biwn_dispatch_cpu_status', 'biwn_scene_draw_cpu_status').replace('BIWN_DISPATCH_CPU', 'BIWN_SCENE_DRAW_CPU')
    prefix = prefix.replace('s->cpu.usp=s->cpu.registers[15];', 'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)', '')
    prefix = prefix.replace('static uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}\n', '')
    suffix = base.SUFFIX.replace('biwn_input_dispatch_cpu', 'biwn_scene_draw_cpu').replace('biwn_dispatch_cpu_status', 'biwn_scene_draw_cpu_status').replace('BIWN_DISPATCH_CPU', 'BIWN_SCENE_DRAW_CPU')
    header = '''#ifndef BIWN_SCENE_DRAW_CPU_H
#define BIWN_SCENE_DRAW_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_scene_draw_cpu_status {BIWN_SCENE_DRAW_CPU_OK=0,
 BIWN_SCENE_DRAW_CPU_BAD_ARGUMENT=1,BIWN_SCENE_DRAW_CPU_BUS_ERROR=2,
 BIWN_SCENE_DRAW_CPU_SERVICE_ERROR=3,BIWN_SCENE_DRAW_CPU_WORK_LIMIT=4,
 BIWN_SCENE_DRAW_CPU_BAD_RETURN=5,BIWN_SCENE_DRAW_CPU_YIELDED=6,
 BIWN_SCENE_DRAW_CPU_BAD_PC=7};
/* Static full CPU/source frames for E03A clear,17E0E scene caller and
 * 17F14 buffer rotation. Both stack banks. body stops at outer RTS;
 * call consumes it. Dependencies execute up to RTS through a provider.
 * Device rasterization, six scene/geometry helpers,E098 wait and185B2
 * display-list builder are separate dependencies. No whole viewport claim.
 * No runtime instruction decoding or original CPU calls. */
enum biwn_scene_draw_cpu_status biwn_scene_draw_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_scene_draw_cpu_status biwn_scene_draw_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    (source / 'biwn_scene_draw_cpu.c').write_text(prefix + '\n'.join(emit(row) for row in rows) + '\n' + suffix)
    (source / 'biwn_scene_draw_cpu.h').write_text(header)
    manifest = dict(status='generated_unverified', instructions=len(rows), ranges={hex(a): hex(b) for a,b in RANGES.items()}, instructions_decoded=rows,
                    stage_sha256=hashlib.sha256(image).hexdigest(), generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    source_sha256={n: hashlib.sha256((source / n).read_bytes()).hexdigest() for n in ['biwn_scene_draw_cpu.c', 'biwn_scene_draw_cpu.h']}, whole_game_complete=False)
    (session / 'scene-draw-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k:v for k,v in manifest.items() if k != 'instructions_decoded'}))

if __name__ == '__main__':
    main()
