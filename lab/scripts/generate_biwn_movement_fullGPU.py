"""Static GPU4320 blocks with inherited full logical GPU state.

The prior 1025-case movement proof establishes these code addresses, including
mandatory delays. This variant retains all inherited banks/device fields so it
can run after the movie without a GPU register reset. Generated is not verified.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_gpu_geometry as base

ROOT = base.ROOT
rename = lambda s: s.replace('gpu_geometry', 'movement_fullGPU').replace('GPU_GEOMETRY', 'MOVEMENT_FULLGPU')
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    folder = session / 'gpu-movement-overlay'
    rows = json.loads((folder / 'original-code-decode.json').read_text())['instructions']
    prior = json.loads((ROOT / 'verification/biwn-movement-matrix-checks.json').read_text())
    assert prior['GPU_code_instructions'] == prior['GPU_instructions_covered'] == len(rows) == 353
    payload = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x4328:0x4720]
    assert sha(payload) == json.loads((folder / 'mapping.json').read_text())['sha256']
    for r in rows:
        off = r['address'] - 0xf03240
        assert payload[off:off+r['size']].hex() == r['bytes']
    header = rename(base.HEADER).replace(
        'uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;',
        'uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n '
        'uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a = header.index('/* Source-specific')
    b = header.index('enum biwn_movement_fullGPU_status biwn_movement_fullGPU_run', a)
    header = header[:a] + '''/* Fixed source GPU4320 movement instructions, bank0, supplied inherited
 * full logical GPU state and source-loaded local RAM. Stops at resident
 * dispatcher F031BE; executes taken branch delay slots. No init/reset,
 * runtime decoder, original GPU calls or high-level matrix substitution.
 * Errors leave input state unchanged and retain external writes. Finite
 * source buffers/budget required. No timing/interrupt/full game claim. */
''' + header[b:]
    prefix = rename(base.PREFIX)
    prefix = '\n'.join(line for line in prefix.splitlines() if not line.startswith(
        ('static void divide(', 'static int matrix('))) + '\n'
    prefix += '''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_movement_fullGPU_status)status;}while(0)
enum biwn_movement_fullGPU_status biwn_movement_fullGPU_run(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *state,uint32_t budget){struct biwn_movement_fullGPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases = []
    for row in rows:
        word = int(row['bytes'][:4], 16)
        op, m, n = word >> 10, (word >> 5) & 31, word & 31
        if op == 37:
            lines = [f's.registers[0][{n}]=s.registers[1][{m}];']
        elif op == 41:
            M = f's.registers[0][{m}]'
            lines = [f'CHECK(rd32(bus,&s,local({M})?({M}&~3u):{M},&v));s.registers[0][{n}]=v;']
        else:
            cases.append(rename(base.emit(row)))
            continue
        cases.append(f'case {hex(row["address"])}u: /* {row["assembly"]} */\n '
                     + '\n '.join(lines) + f'\n s.pc={hex(row["address"]+row["size"])}u;break;')
    suffix = '''default:return BIWN_MOVEMENT_FULLGPU_BAD_PC;
}if(delayed){if(pending)return BIWN_MOVEMENT_FULLGPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_MOVEMENT_FULLGPU_WORK_LIMIT;}
'''
    src = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_movement_fullGPU.c', 'biwn_movement_fullGPU.h']
    (src / names[0]).write_text(prefix + '\n'.join(cases) + '\n' + suffix)
    (src / names[1]).write_text(header)
    record = dict(status='generated_unverified', instructions=len(rows), instructions_decoded=rows,
                  source_sha256={n: sha((src/n).read_bytes()) for n in names},
                  generator_sha256=sha(Path(__file__).read_bytes()), payload_sha256=sha(payload),
                  prior_source_code_coverage_report=str(ROOT/'verification/biwn-movement-matrix-checks.json'),
                  full_inherited_GPU_state_verified=False, whole_game_complete=False)
    (folder / 'fullGPU-C-generation.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'instructions_decoded'}))


if __name__ == '__main__':
    main()
