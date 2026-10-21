"""Fixed full-CPU boundary/cleanup source blocks; helpers are providers."""
import hashlib
import json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader

ROOT = loader.ROOT
RANGES = {0x19f2c: 0x1a188, 0x1ae56: 0x1ae88, 0x20cc4: 0x20cf8, 0x20e40: 0x20f78}


def rename(text):
    return (loader.rename(text).replace('generate_biwn_interior_loading_cpu.py', 'generate_biwn_transition_cpu.py')
            .replace('biwn_interior_loading_cpu', 'biwn_transition_cpu')
            .replace('BIWN_INTERIOR_LOADING_CPU', 'BIWN_TRANSITION_CPU'))


def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest() == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows = []
    for start, end in RANGES.items():
        assert image[start - 0x4000:end - 0x4000] == snapshot[start:end]
        rows += loader.base.binary_tools.m68k_instructions(snapshot[start:end], start)[0]
    prefix = rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];',
        'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)', '')
    header = rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H', 'BIWN_TRANSITION_CPU_H')
    start = header.index('/* Static')
    end = header.index('enum biwn_transition_cpu_status biwn_transition_cpu_body', start)
    header = header[:start] + '''/* Fixed boundary 19F2C/19FDA/1A0F8 and cleanup 1AE56/20CC4/20E40/
 * 20E8C/20F0C. Full registers/SR/both stack banks/private argument frames.
 * Helper providers execute up to RTS. Source DF60 yield may propagate
 * complete CPU/private frames for scheduling and continuation. body stops
 * before RTS; call consumes RTS. No runtime decoding or original core calls.
 * Finite valid source lists required; host failures preserve input CPU and
 * prior RAM effects. Generation alone proves no connected transition. */
''' + header[end:]
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_transition_cpu.c', 'biwn_transition_cpu.h']
    (source / names[0]).write_text(prefix + '\n'.join(rename(loader.emit(row)) for row in rows) + '\n' + rename(loader.base.SUFFIX))
    (source / names[1]).write_text(header)
    manifest = {'status': 'generated_unverified', 'instructions': len(rows), 'instructions_decoded': rows,
                'ranges': {hex(start): hex(end) for start, end in RANGES.items()},
                'stage_sha256': hashlib.sha256(image).hexdigest(),
                'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_sha256': {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names},
                'new_published_components': 0, 'whole_game_complete': False}
    (session / 'transition-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: value for key, value in manifest.items() if key != 'instructions_decoded'}))


if __name__ == '__main__':
    main()
