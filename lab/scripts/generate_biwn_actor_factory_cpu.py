"""Full-CPU actor dispatch/create blocks and task-create wrapper/body.

The 13620..13706 jump table remains data read through the bus. Static-object
137E0 and empty-task-pool ILLEGAL are explicit unimplemented paths here.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader

ROOT = loader.ROOT
RANGES = {0x13ae0: 0x13b5a, 0x134dc: 0x13620, 0x13706: 0x137e0,
          0xde5c: 0xdeb4, 0xdf6c: 0xdf7a}


def rename(text):
    return (loader.rename(text).replace('generate_biwn_interior_loading_cpu.py', 'generate_biwn_actor_factory_cpu.py')
            .replace('biwn_interior_loading_cpu', 'biwn_actor_factory_cpu')
            .replace('BIWN_INTERIOR_LOADING_CPU', 'BIWN_ACTOR_FACTORY_CPU'))


def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    ram = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest() == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows = []
    for start, end in RANGES.items():
        assert image[start - 0x4000:end - 0x4000] == ram[start:end]
        rows += loader.base.binary_tools.m68k_instructions(ram[start:end], start)[0]
    prefix = rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];',
        'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)', '')
    header = rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H', 'BIWN_ACTOR_FACTORY_CPU_H')
    start = header.index('/* Static')
    end = header.index('enum biwn_actor_factory_cpu_status biwn_actor_factory_cpu_body', start)
    header = header[:start] + '''/* Source-specific actor dispatcher13AE0, actor134DC/table targets13706,
 * taskcreateDE5C/DF6C. Full CPU/private MOVEM/args/JMP/RTS frames; both banks.
 * 13620..13706 table is data, not executable blocks. Static-object137E0 is a
 * provider; empty task pool reaches unsupported DEB4 rather than emulating
 * ILLEGAL. No runtime decoding/core calls. body stops before RTS; call
 * consumes it. Caller supplies valid source records/list indices. Generation
 * alone proves no actor creation, scheduler context reuse or game completion. */
''' + header[end:]
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_actor_factory_cpu.c', 'biwn_actor_factory_cpu.h']
    (source / names[0]).write_text(prefix + '\n'.join(rename(loader.emit(row)) for row in rows) + '\n' + rename(loader.base.SUFFIX))
    (source / names[1]).write_text(header)
    manifest = {'status': 'generated_unverified', 'instructions': len(rows), 'instructions_decoded': rows,
                'ranges': {hex(start): hex(end) for start, end in RANGES.items()},
                'jump_table_data_interval': ['0x13620', '0x13706'],
                'stage_sha256': hashlib.sha256(image).hexdigest(),
                'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_sha256': {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names},
                'new_published_components': 0, 'whole_game_complete': False}
    (session / 'actor-factory-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: value for key, value in manifest.items() if key != 'instructions_decoded'}))


if __name__ == '__main__':
    main()
