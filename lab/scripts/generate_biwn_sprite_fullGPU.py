"""Static GPU4B00 blocks with inherited full logical GPU state.

The sprite overlay code/table classification supplies these static addresses.
Execution proof and coverage remain separate. This variant retains all inherited banks/device fields so it
can run after the movie without a GPU register reset. Generated is not verified.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_gpu_geometry as base

ROOT = base.ROOT
rename = lambda s: s.replace('gpu_geometry', 'sprite_fullGPU').replace('GPU_GEOMETRY', 'SPRITE_FULLGPU')
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    folder = session / 'gpu-sprite-overlay'
    rows = json.loads((folder / 'original-decode.json').read_text())['rows']
    rows = [r for r in rows if r['classification']=='decoded_instruction']
    assert len(rows)==214
    payload = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x4b08:0x4d68]
    assert sha(payload) == json.loads((folder / 'mapping.json').read_text())['overlay_sha256']
    for r in rows:
        off = r['address'] - 0xf03240
        assert payload[off:off+r['size']].hex() == r['bytes']
    header = rename(base.HEADER).replace(
        'uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;',
        'uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n '
        'uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a = header.index('/* Source-specific')
    b = header.index('enum biwn_sprite_fullGPU_status biwn_sprite_fullGPU_run', a)
    header = header[:a] + '''/* Fixed source GPU4B00 movement instructions, bank0, supplied inherited
 * full logical GPU state and source-loaded local RAM. Stops at resident
 * dispatcher F031BE; executes taken branch delay slots. No init/reset,
 * runtime decoder, original GPU calls or high-level matrix substitution.
 * Errors leave input state unchanged and retain external writes. Finite
 * source buffers/budget required. No timing/interrupt/full game claim. */
''' + header[b:]
    header = header.replace(' int (*read16)', ' int (*read8)(void *,uint32_t,uint8_t *);\n int (*read16)')
    prefix = rename(base.PREFIX)
    prefix = '\n'.join(line for line in prefix.splitlines() if not line.startswith(
        ('static uint32_t sx16(', 'static void divide(', 'static int matrix('))) + '\n'
    prefix = prefix.replace('if(a==0xf02104u){s->matrix_control=v;return 0;}', 'if(a==0xf0211cu){s->division_control=v;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}')
    prefix += '''static int rd8(struct biwn_sprite_fullGPU_bus *b,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t *v){uint8_t x;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_sprite_fullGPU_status)status;}while(0)
enum biwn_sprite_fullGPU_status biwn_sprite_fullGPU_run(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *state,uint32_t budget){struct biwn_sprite_fullGPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases = []
    for row in rows:
        word = int(row['bytes'][:4], 16)
        op, m, n = word >> 10, (word >> 5) & 31, word & 31
        M=f's.registers[0][{m}]';N=f's.registers[0][{n}]'
        if op == 39:
            lines=[f'CHECK(rd8(bus,&s,{M},&v));{N}=v;']
        elif op == 7:
            lines=[f'{N}-={m or 32}u;']
        elif op == 23:
            lines=[f'v={M};if(v&0x80000000u){{s.c={N}>>31;{N}=(v<=0xffffffe0u)?0:{N}<<(0u-v);}}else{{s.c={N}&1u;{N}=v>=32?0:{N}>>v;}}zn(&s,{N});']
        elif op == 12:
            lines=[f'{N}=~{N};zn(&s,{N});']
        elif op == 37:
            lines = [f's.registers[0][{n}]=s.registers[1][{m}];']
        elif op == 41:
            M = f's.registers[0][{m}]'
            lines = [f'CHECK(rd32(bus,&s,local({M})?({M}&~3u):{M},&v));s.registers[0][{n}]=v;']
        else:
            cases.append(rename(base.emit(row)))
            continue
        cases.append(f'case {hex(row["address"])}u: /* {row["assembly"]} */\n '
                     + '\n '.join(lines) + f'\n s.pc={hex(row["address"]+row["size"])}u;break;')
    suffix = '''default:return BIWN_SPRITE_FULLGPU_BAD_PC;
}if(delayed){if(pending)return BIWN_SPRITE_FULLGPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_SPRITE_FULLGPU_WORK_LIMIT;}
'''
    src = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_sprite_fullGPU.c', 'biwn_sprite_fullGPU.h']
    (src / names[0]).write_text(prefix + '\n'.join(cases) + '\n' + suffix)
    (src / names[1]).write_text(header)
    record = dict(status='generated_unverified', instructions=len(rows), instructions_decoded=rows,
                  source_sha256={n: sha((src/n).read_bytes()) for n in names},
                  generator_sha256=sha(Path(__file__).read_bytes()), payload_sha256=sha(payload),
                  source_decode_classification='214 static code rows, excluding tables/padding; generation alone is not execution coverage',
                  full_inherited_GPU_state_verified=False, whole_game_complete=False)
    (folder / 'fullGPU-C-generation.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'instructions_decoded'}))


if __name__ == '__main__':
    main()
