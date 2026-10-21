"""Source world caller, digit selector and task loop with nested continuations.

Separate candidate preserves the accepted older world caller. Generation alone
does not verify game integration, input behavior or uninterrupted startup.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader

ROOT = loader.ROOT
RANGES = {0x1a188: 0x1a552, 0x1b718: 0x1b780}


def rename(text):
    return (loader.rename(text)
        .replace('generate_biwn_interior_loading_cpu.py', 'generate_biwn_world_flow_cpu.py')
        .replace('biwn_interior_loading_cpu', 'biwn_world_flow_cpu')
        .replace('BIWN_INTERIOR_LOADING_CPU', 'BIWN_WORLD_FLOW_CPU'))


def emit(row):
    if row['assembly'] == 'lsr.w d4, d0':
        pc = row['address']
        return (f'  case {hex(pc)}u: /* lsr.w d4, d0 */\n'
            '   {unsigned count=s.cpu.registers[4]&63u;uint32_t old=s.cpu.registers[0]&65535u;'
            'unsigned carry=count&&count<=16u?((old>>(count-1u))&1u):0u;'
            'v=count<16u?old>>count:0u;put(&s,0,2,v);nz(&s,v,16);'
            'if(count)s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(carry?0x11u:0));}'
            f's.cpu.pc={hex(pc+row["size"])}u;break;')
    return rename(loader.emit(row))


def main():
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session/'nextstage-68000-candidate.bin').read_bytes()
    ram = (ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest() == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows = []
    for start, end in RANGES.items():
        assert image[start-0x4000:end-0x4000] == ram[start:end]
        rows += loader.base.binary_tools.m68k_instructions(ram[start:end], start)[0]
    prefix = rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];',
        'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)', '')
    # This program uses logical register-count shifts, emitted above. Remove
    # the generic arithmetic-shift helper which this fixed program never uses.
    start = prefix.index('static void shift(')
    end = prefix.index('static int read_value(', start)
    prefix = prefix[:start] + prefix[end:]
    header = rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H', 'BIWN_WORLD_FLOW_CPU_H')
    start = header.index('/* Static')
    end = header.index('enum biwn_world_flow_cpu_status biwn_world_flow_cpu_body', start)
    header = header[:start] + '''/* Fixed source world1A188/taskloop1A544/digit1B718 blocks. Full CPU,
 * both stack banks and source private frames. Arbitrary decoded continuation
 * supported after nested source input/boundary/loading yields at DF60. Nested
 * providers execute up to RTS; body stops before RTS, call consumes it. No
 * runtime instruction decoding or original CPU-core calls. Generation alone
 * proves no input, scheduler, loading, drawing or full-game integration. */
''' + header[end:]
    source = ROOT/'projects/black-ice-white-noise/restoration'
    names = ['biwn_world_flow_cpu.c', 'biwn_world_flow_cpu.h']
    (source/names[0]).write_text(prefix+'\n'.join(emit(row) for row in rows)+'\n'+rename(loader.base.SUFFIX))
    (source/names[1]).write_text(header)
    manifest = dict(status='generated_unverified', instructions=len(rows), instructions_decoded=rows,
        ranges={hex(a):hex(b) for a,b in RANGES.items()}, stage_sha256=hashlib.sha256(image).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},
        replaces_no_accepted_source=True, new_published_components=0, whole_game_complete=False)
    (session/'world-flow-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='instructions_decoded'}))


if __name__ == '__main__':
    main()
