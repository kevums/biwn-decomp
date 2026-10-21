"""Geometry monitor/gate fault controls with stubbed CPU/RAM, not a game run."""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    v = ROOT / 'verification'
    run = json.loads((v / 'outer-observer-preflight-v1-current.json').read_text())
    source = Path(run['observer'])
    text = source.read_text()
    start = text.index('static unsigned g4_pending[101]')
    stop = text.index('static int32_t o6_retained_observe(uint32_t pc)', start)
    dump_start=text.index('int geometry_dump(',stop)
    dump_end=text.index('static const uint32_t o6_inner_returns',dump_start)
    monitor = text[start:stop] + text[dump_start:dump_end]
    build = json.loads((v / 'native-Deck-six-disc-build-v1-current.json').read_text())
    symbols = build['shared_Deck_symbols']
    out = v / 'geometry-outer-observer-qualification-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    stub = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu {uint32_t r[16];};
static struct cpu current;
static uint8_t memory[0x200000];
static uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)memory[a]<<8)|memory[a+1];}
static void read_cpu(struct cpu *out){*out=current;}
'''
    hooks = r'''
void fixture_reset(void){
 memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));
 memset(g4_pending,0,sizeof(g4_pending));memset(g4_helper_pending,0,sizeof(g4_helper_pending));
 memset(g4_incoming,0,sizeof(g4_incoming));memset(g4_return_word,0,sizeof(g4_return_word));
 memset(g4_helpers,0,sizeof(g4_helpers));memset(g4_helper_returns,0,sizeof(g4_helper_returns));
 g4_entries=g4_returns=g4_body_steps=g4_errors=g4_parent_returns=0;
}
void fixture_register(unsigned i,uint32_t value){if(i<16)current.r[i]=value;}
void fixture_word(uint32_t a,uint16_t value){memory[a]=(uint8_t)(value>>8);memory[a+1]=(uint8_t)value;}
void fixture_long(uint32_t a,uint32_t value){memory[a]=(uint8_t)(value>>24);memory[a+1]=(uint8_t)(value>>16);memory[a+2]=(uint8_t)(value>>8);memory[a+3]=(uint8_t)value;}
void fixture_pc(uint32_t pc){g4_watch(pc);}
'''
    fixture = out / 'monitor-fixture.c'
    fixture.write_text(stub + monitor + hooks)
    library = out / 'monitor-fixture.dylib'
    compile_result = subprocess.run(['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
                                     str(fixture), '-o', str(library)], capture_output=True, text=True)
    (out / 'compile.log').write_text(compile_result.stdout + compile_result.stderr)
    assert compile_result.returncode == 0, compile_result.stderr
    lib = c.CDLL(str(library))
    lib.fixture_register.argtypes = [c.c_uint, c.c_uint32]
    lib.fixture_word.argtypes = [c.c_uint32, c.c_uint16]
    lib.fixture_long.argtypes = [c.c_uint32, c.c_uint32]
    lib.fixture_pc.argtypes = [c.c_uint32]
    lib.geometry_dump.argtypes = [c.c_char_p]
    targets = [0x10968, 0x11384, 0x10ba4, 0x1142e, 0x10734]
    logical = [0x11ae6, 0x11b32, 0x11b38, 0x11b3e, 0x11b44]
    rows = []
    variants = [('legal_native', True), ('legal_original', False), ('wrong_argument', True),
                ('wrong_helper_return_SP', True), ('wrong_outer_return_word', True),
                ('wrong_preserved_D2', True), ('missing_helper_return', True),
                ('duplicate_public_entry', True), ('invalid_task', True), ('missing_helper', True), ('legal_native_outer', True), ('bad_outer_saved_PC', True), ('bad_outer_saved_SP', True)]
    for name, native in variants:
        lib.fixture_reset()
        sp = 0x1e0000
        lib.fixture_long(0xc0920, 0xc0928 + 6 * 1024 if name != 'invalid_task' else 1)
        lib.fixture_register(15, sp)
        lib.fixture_register(2, 0xdead0012)
        lib.fixture_register(3, 0xa55a1234)
        outer_variant=name in ['legal_native_outer','bad_outer_saved_PC','bad_outer_saved_SP']
        outer_frame=build['outer_arena_address']+6*576+16
        lib.fixture_long(outer_frame+106,sp+2 if name=='bad_outer_saved_SP'else sp)
        lib.fixture_long(outer_frame+110,0x11ee6 if name=='bad_outer_saved_PC'else 0x11ee4)
        lib.fixture_long(sp,build['outer_symbols']['biwn_outer_helper_return']if outer_variant else 0x11ee4)
        lib.fixture_pc(0x11ad4)
        if name == 'duplicate_public_entry':
            lib.fixture_pc(0x11ad4)
        for h, target in enumerate(targets):
            if name == 'missing_helper' and h == 2:
                continue
            lib.fixture_register(15, sp - 16)
            lib.fixture_long(sp - 16, symbols['biwn_v4_geometry_helper_return'] if native else logical[h])
            lib.fixture_word(sp - 12, 2 if name == 'wrong_argument' and h == 2 else 1)
            lib.fixture_word(sp - 10, 7)
            lib.fixture_pc(target)
            if name == 'missing_helper_return' and h == 4:
                continue
            lib.fixture_register(15, sp - 10 if name == 'wrong_helper_return_SP' and h == 2 else sp - 12)
            lib.fixture_pc(symbols['biwn_v4_geometry_helper_return'] if native else logical[h])
        lib.fixture_register(15, sp)
        if name == 'wrong_outer_return_word':
            lib.fixture_long(sp, 0x11ee6)
        if name == 'wrong_preserved_D2':
            lib.fixture_register(2, 0xdead0013)
        lib.fixture_pc(symbols['biwn_v4_geometry_return'] if native else 0x11b4a)
        path = out / (name + '.json')
        assert lib.geometry_dump(str(path).encode()) == 0
        actual = json.loads(path.read_text())
        accepted = (actual['errors'] == actual['pending'] == 0 and
                    actual['entries'] == actual['returns'] == actual['matched_outer_parent_returns'] == 1 and
                    actual['helper_entries'] == actual['helper_returns'] == [1] * 5)
        assert accepted == name.startswith('legal_'), (name, actual)
        rows.append(dict(case=name, completion_gate_accepted=accepted, counters=actual))
    (out / 'cases.json').write_text(json.dumps(rows, indent=2) + '\n')
    proof = dict(status='terminal_geometry_outer_observer_three_legal_ten_fault_controls_pass', directory=str(out),
                 legal_controls=3, rejected_fault_controls=10, actual_game_execution=False,
                 source_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                [Path(__file__), source, fixture, library, out / 'cases.json']},
                 scope=__doc__ + ' Extracted geometry watcher code is unchanged. CPU register prefix and RAM reads '
                 'are fixtures. Tests arguments, helper/outer return stack, saved D2, pending helper, duplicate entry, '
                 'invalid task and missing-helper count gate. It does not qualify every retained observer, '
                 'helper order, full CPU ABI, emulator nonintrusion, game fidelity or IRQ behavior.')
    (out / 'review.json').write_text(json.dumps(proof, indent=2) + '\n')
    (v / 'geometry-outer-observer-qualified-v1-current.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(proof['status'])


if __name__ == '__main__':
    main()
