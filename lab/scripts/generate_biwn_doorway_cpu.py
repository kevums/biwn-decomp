"""Fixed full-CPU source 10430 entrance selection; no runtime decoding."""
import hashlib
import json
from pathlib import Path
import generate_biwn_resource_cpu as resource

ROOT = resource.ROOT


def rename(text):
    return (text.replace('generate_biwn_input_dispatch_cpu.py', 'generate_biwn_doorway_cpu.py')
            .replace('biwn_input_dispatch_cpu', 'biwn_doorway_cpu')
            .replace('biwn_dispatch_cpu_status', 'biwn_doorway_cpu_status')
            .replace('BIWN_DISPATCH_CPU', 'BIWN_DOORWAY_CPU')
            .replace('BIWN_RESOURCE_CPU', 'BIWN_DOORWAY_CPU'))


def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    ram = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest() == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    assert image[0x10430 - 0x4000:0x10520 - 0x4000] == ram[0x10430:0x10520]
    rows, _ = resource.base.binary_tools.m68k_instructions(ram[0x10430:0x10520], 0x10430)
    prefix = rename(resource.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];',
        'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)', '')
    start = prefix.index('static int invoke(')
    prefix = prefix[:start] + prefix[prefix.index('#define CHECK', start):]
    header = rename(resource.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H', 'BIWN_DOORWAY_CPU_H')
    start = header.index('/* Static')
    end = header.index('enum biwn_doorway_cpu_status biwn_doorway_cpu_body', start)
    header = header[:start] + '''/* Source-specific static 10430 entrance selection, full registers/SR,
 * both stack banks, MOVEM frames and object writes. body stops before RTS;
 * call consumes RTS. No helper calls, runtime CPU decoding or core execution.
 * Caller supplies valid mapped records and pointers. A successful entrance
 * check alone does not load a scene or prove doorway reachability/gameplay.
 * Host errors preserve input CPU and retain earlier RAM stores. */
''' + header[end:]
    folder = ROOT / 'projects/black-ice-white-noise/restoration'
    text = prefix + '\n'.join(rename(resource.emit(row)) for row in rows) + '\n' + rename(resource.base.SUFFIX)
    names = ['biwn_doorway_cpu.c', 'biwn_doorway_cpu.h']
    (folder / names[0]).write_text(text)
    (folder / names[1]).write_text(header)
    manifest = {'status': 'generated_unverified', 'instructions': len(rows),
                'instructions_decoded': rows, 'ranges': {'0x10430': '0x10520'},
                'stage_sha256': hashlib.sha256(image).hexdigest(),
                'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_sha256': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in names},
                'new_published_components': 0, 'whole_game_complete': False}
    (session / 'doorway-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: value for key, value in manifest.items() if key != 'instructions_decoded'}))


if __name__ == '__main__':
    main()
