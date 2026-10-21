"""Fixed EDC4 merchant task, asset initialization, distance/facing/dialog calls.

External message/video/input helpers remain providers. This is generation,
not acceptance of interaction branches or a complete NPC/game workflow.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader

ROOT = loader.ROOT
RANGES = {0xedc4: 0xef90, 0x101e0: 0x10252, 0x10252: 0x1028e,
          0x1404c: 0x140f0, 0xed60: 0xedc4, 0x207cc: 0x20812, 0xdfa6: 0xdfb2}


def rename(text):
    return (loader.rename(text).replace('generate_biwn_interior_loading_cpu.py', 'generate_biwn_npc_cpu.py')
            .replace('biwn_interior_loading_cpu', 'biwn_npc_cpu')
            .replace('BIWN_INTERIOR_LOADING_CPU', 'BIWN_NPC_CPU'))


def emit(row):
    if row['assembly'] == 'jsr $df7a.l':
        pc = row['address']
        return (f'  case {hex(pc)}u: /* actual removal boundary */\n'
                f'   CHECK(push(&s,{hex(pc + row["size"])}u,4));s.cpu.pc=0xdf7au;'
                '*state=s.cpu;return BIWN_NPC_CPU_YIELDED;')
    return rename(loader.emit(row))


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
    prefix=prefix.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)')
    prefix=prefix.replace('while(budget--){switch(s.cpu.pc){',
        'while(budget--){if(full_call==2&&s.cpu.pc==0xee20u){*state=s.cpu;return BIWN_NPC_CPU_READY;}switch(s.cpu.pc){')
    header = rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H', 'BIWN_NPC_CPU_H')
    start = header.index('/* Static')
    end = header.index('enum biwn_npc_cpu_status biwn_npc_cpu_body', start)
    header = header[:start] + '''/* Fixed EDC4 task/101E0asset init/10252distance squared/1404Cfacing/
 * ED60choice/207CCmessage caller. Full CPU/private frames, both stack banks.
 * DF60 and DF7A stop with complete state/private frames for scheduler yield
 * or removal. Nested resource DF8C waits retain CPU/private frames.
 * Internal PC continuation supported. Helpers remain providers;
 * some message/video/input branches are unported. body stops before RTS;
 * call consumes RTS. No runtime decoding/core calls. Generation does not
 * prove dialog, sprite rendering, NPC behavior or whole-game completion. */
''' + header[end:]
    header=header.replace('BIWN_NPC_CPU_BAD_PC=7};','BIWN_NPC_CPU_BAD_PC=7,BIWN_NPC_CPU_READY=8};')
    header=header.replace('#endif','''/* Added host observation boundary only: commit state before EE20's first
 * loop instruction, returning READY. Existing body/call behavior unchanged.
 * This lets declared external inputs be applied at the same source PC on
 * native and C paths; it is not a guest instruction or completion claim. */
enum biwn_npc_cpu_status biwn_npc_cpu_until_loop(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif''')
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_npc_cpu.c', 'biwn_npc_cpu.h']
    until='enum biwn_npc_cpu_status biwn_npc_cpu_until_loop(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,biwn_input_write8 w8,biwn_world_cpu_service svc,void *ctx,uint32_t budget,int yield){return run(bus,cpu,w8,svc,ctx,budget,yield,2);}\n'
    (source / names[0]).write_text(prefix + '\n'.join(emit(row) for row in rows) + '\n' + rename(loader.base.SUFFIX)+until)
    (source / names[1]).write_text(header)
    manifest = {'status': 'generated_unverified', 'instructions': len(rows), 'instructions_decoded': rows,
                'ranges': {hex(start): hex(end) for start, end in RANGES.items()},
                'stage_sha256': hashlib.sha256(image).hexdigest(),
                'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_sha256': {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names},
                'new_published_components': 0, 'whole_game_complete': False}
    (session / 'npc-fullCPU-generation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: value for key, value in manifest.items() if key != 'instructions_decoded'}))


if __name__ == '__main__':
    main()
