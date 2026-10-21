"""Replay readable attack semantics from naturally observed native game calls.

An isolated read-only observer records entry/return RAM and CPU. Original
120/300frame controller runs must remain byte-identical to earlier references.
The readable body and real C RNG then run on private copies of those inputs;
they are not substituted into the live instruction-level frame runtime.
"""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import check_biwn_attack_effect as attack

ROOT = Path(__file__).resolve().parents[1]
TRACE_TYPE = np.dtype({'names': ['D0', 'sp', 'pc'], 'formats': ['>u4', '>u4', '>u4'],
                       'offsets': [0, 60, 64], 'itemsize': 78})

OBSERVER = r'''
static unsigned capture_count, capture_pending;
static uint32_t capture_sp, capture_return;
static uint64_t capture_trace_head;
extern uint32_t OPGetListPointer(void);
static int capture_trace_write(void)
{
    const char *directory=getenv("BIWN_ATTACK_CAPTURE_DIR");char path[4096];
    uint64_t i,end=vjtrace_ring_head();vjtrace_ev event;FILE *f;int length,failed=0;
    if(end<capture_trace_head||end-capture_trace_head>100000)return 1;
    length=snprintf(path,sizeof(path),"%s/call-%02u-events.txt",directory,capture_count);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"w");if(!f)return 1;
    for(i=capture_trace_head;i<end;i++){
        if(!vjtrace_ring_read(i,&event)){failed=1;break;}
        if(fprintf(f,"%llu %u %u %u %u %u %u %u\n",(unsigned long long)event.seq,
             event.frame,(unsigned)event.halfline,(unsigned)event.type,(unsigned)event.who,
             event.pc,event.addr,event.value)<0){failed=1;break;}
    }
    if(fclose(f))failed=1;return failed;
}
static int capture_write(const char *phase, const struct biwn_task_cpu *s)
{
    const char *directory=getenv("BIWN_ATTACK_CAPTURE_DIR");
    char path[4096];FILE *f;uint8_t cpu[78];unsigned i;int length,failed;
    if(!directory)return 1;
    for(i=0;i<16;i++)put32(cpu+i*4,s->registers[i]);
    put32(cpu+64,s->pc);put32(cpu+68,s->usp);put32(cpu+72,s->ssp);
    cpu[76]=(uint8_t)(s->sr>>8);cpu[77]=(uint8_t)s->sr;
    length=snprintf(path,sizeof(path),"%s/call-%02u-%s.cpu",directory,capture_count,phase);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"wb");if(!f)return 1;
    failed=fwrite(cpu,1,sizeof(cpu),f)!=sizeof(cpu);if(fclose(f))failed=1;if(failed)return 1;
    length=snprintf(path,sizeof(path),"%s/call-%02u-%s.ram",directory,capture_count,phase);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"wb");if(!f)return 1;
    failed=fwrite(H.RAM,1,0x200000,f)!=0x200000;if(fclose(f))failed=1;if(failed)return 1;
    length=snprintf(path,sizeof(path),"%s/call-%02u-%s.index",directory,capture_count,phase);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"w");if(!f)return 1;
    failed=fprintf(f,"%llu\n",(unsigned long long)(S.calls-1))<0;
    if(fclose(f))failed=1;return failed;
}
static int capture_attack(uint32_t pc,const struct biwn_task_cpu *s)
{
    uint32_t sp=s->registers[15];
    if(capture_pending&&pc==capture_return&&sp==capture_sp+4){
        if(capture_write("return",s)||capture_trace_write())return 1;
        vjtrace_disarm();vjtrace_watch_clear();capture_pending=0;
    }
    if(pc==0x18df2u){
        if(capture_pending||capture_count>=32||sp>0x1ffffcu)return 1;
        capture_count++;capture_sp=sp;
        capture_return=((uint32_t)H.RAM[sp]<<24)|((uint32_t)H.RAM[sp+1]<<16)|
                       ((uint32_t)H.RAM[sp+2]<<8)|H.RAM[sp+3];
        if(vjtrace_armed||vjtrace_nwatch)return 1;
        vjtrace_init();capture_trace_head=vjtrace_ring_head();
        if(vjtrace_watch_add(0,0x1fffffu,2)<0)return 1;
        vjtrace_arm();
        if(capture_write("entry",s))return 1;capture_pending=1;
    }
    return 0;
}
'''


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = ROOT / 'verification/natural-attack-effect' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    original_proof = json.loads((ROOT / 'verification/ordinary-gameplay-damage-current.json').read_text())
    base = json.loads((ROOT / 'verification/main-static-native-CPU-experimental-candidate.json').read_text())
    base_source = Path(base['directory']) / 'fast_CPU_bridge.c'
    assert digest(base_source) == base['source_sha256']
    source = base_source.read_text()
    marker = 'int32_t biwn_fast_CPU_owner(uint32_t PC)'
    assert source.count(marker) == 1
    source = source.replace(marker, OBSERVER + '\n' + marker)
    marker = 'if(s.pc!=PC)return fail(PC,91);if(state_file)'
    assert source.count(marker) == 1
    source = source.replace(marker, 'if(s.pc!=PC)return fail(PC,91);if(capture_attack(PC,&s))return fail(PC,177);if(state_file)')
    core = Path(json.loads((ROOT / 'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    assert digest(core) == base['required_core_sha256']
    trace_header = core.parent / 'src/core/vjtrace.h'
    source = '#include <stdlib.h>\n#define VJ_TRACE 1\n#include "' + str(trace_header) + '"\n' + source
    bridge_source = out / 'capture_bridge.c'
    bridge_source.write_text(source)
    shutil.copytree(Path(base['directory']) / 'pinned-CPU-headers', out / 'pinned-CPU-headers')
    library = out / 'libcapture-bridge.dylib'
    compile_command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
                       '-I', str(ROOT / 'projects/black-ice-white-noise/restoration'), str(bridge_source),
                       base['CPU_library'], base['cost_library'], str(core), '-o', str(library)]
    compiled = subprocess.run(compile_command, capture_output=True, text=True,
                              env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.log').write_text(compiled.stdout + compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr
    capture_candidate = out / 'capture-candidate.json'
    save(capture_candidate, dict(base, directory=str(out), library=str(library),
                                 source_sha256=digest(bridge_source), status='read_only_observer_unverified',
                                 observer_scope='Entry/return snapshots only; game execution uses original processors.'))
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), commands=[],
                 original_gameplay_proof=str(ROOT / 'verification/ordinary-gameplay-damage-current.json'),
                 capture_source=str(bridge_source), capture_source_sha256=digest(bridge_source),
                 capture_library_sha256=digest(library), compile_command=compile_command,
                 trace_header_sha256=digest(trace_header), OP_source=str(core.parent / 'src/tom/op.c'),
                 OP_source_sha256=digest(core.parent / 'src/tom/op.c'),
                 source_function='0x18DF2', high_level_component_in_frame_runtime=False,
                 whole_game_complete=False)

    def checkpoint():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/natural-attack-effect-active.json', state)

    checkpoint()
    try:
        readable_out = out / 'readable-build'
        readable_out.mkdir()
        readable = ROOT / 'projects/black-ice-white-noise/restoration/biwn_attack_effect.c'
        accepted = json.loads((ROOT / 'verification/attack-effect-current.json').read_text())
        assert digest(readable) == accepted['source_sha256']
        function, bindings, readable_command = attack.bind(readable, readable_out)
        results = []
        for case in original_proof['cases']:
            baseline = Path(case['comparison']).parent
            protocol = json.loads((baseline / 'protocol.json').read_text())
            command = next(row['command'][:] for row in protocol['commands'] if row['phase'] == 'reference')
            folder = out / case['name']
            captures = folder / 'captures'
            captures.mkdir(parents=True)
            command[command.index('--native-CPU-candidate') + 1] = str(capture_candidate)
            command[command.index('--output') + 1] = str(folder / 'reference')
            env = {**os.environ, 'BIWN_ATTACK_CAPTURE_DIR': str(captures)}
            with (folder / 'runtime.log').open('w') as log:
                child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
                state.update(status='capturing_' + case['name'], child_pid=child.pid)
                state['commands'].append(dict(command=command, observer_directory=str(captures), pid=child.pid))
                checkpoint()
                print(case['name'], 'PID', child.pid, flush=True)
                code = child.wait()
            assert code == 0, (case['name'], folder / 'runtime.log')
            report = json.loads((folder / 'reference/report.json').read_text())
            previous = json.loads((baseline / 'reference/report.json').read_text())
            assert report['frames'] == previous['frames'] and not report['errors']
            unchanged = {name: digest(folder / 'reference' / name) == digest(baseline / 'reference' / name)
                         for name in ['CPU-before-instructions.bin', 'retired-instruction-costs.bin', 'warm-RAM.bin',
                                      'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']}
            assert all(unchanged.values()), unchanged
            trace = np.memmap(folder / 'reference/CPU-before-instructions.bin', mode='r', dtype=TRACE_TYPE)
            entries = np.flatnonzero(trace['pc'] == 0x18df2)
            assert len(list(captures.glob('*-entry.ram'))) == len(entries)
            calls = []
            for ordinal, entry_index in enumerate(entries, 1):
                prefix = captures / f'call-{ordinal:02d}'
                entry = Path(str(prefix) + '-entry.ram').read_bytes()
                returned = Path(str(prefix) + '-return.ram').read_bytes()
                first = int(Path(str(prefix) + '-entry.index').read_text())
                last = int(Path(str(prefix) + '-return.index').read_text())
                assert first == int(entry_index) and last > first
                assert Path(str(prefix) + '-entry.cpu').read_bytes() == trace[first].tobytes()
                assert Path(str(prefix) + '-return.cpu').read_bytes() == trace[last].tobytes()
                sp = int(trace[first]['sp'])
                assert int(trace[last]['sp']) == sp + 4
                assert int.from_bytes(entry[sp:sp + 4], 'big') == int(trace[last]['pc'])
                # Reject asynchronous execution outside the function/helper
                # ranges instead of hiding unrelated IRQ RAM effects.
                pcs = trace['pc'][first:last]
                inside = ((pcs >= 0x18df2) & (pcs < 0x18e92)) | ((pcs >= 0x1a77c) & (pcs < 0x1a7f4)) | ((pcs >= 0xe540) & (pcs < 0xe61c))
                assert bool(np.all(inside)), 'Unexpected asynchronous/dependency code in call span'
                stack_low = int(np.min(trace['sp'][first:last + 1]))
                fixture = dict(initial=[], linked_rng=True)
                memory = attack.Script(entry, fixture)
                status, d0 = attack.translated(function, bindings, memory, fixture)
                assert status == 0 and not memory.errors
                assert d0 == int(trace[last]['D0'])
                expected_public = returned[:stack_low] + returned[sp + 4:]
                # Attribute concurrent writes using the native trace's writer,
                # not the mismatch addresses. OPStorePhrase writes two longs;
                # require each bitmap update to satisfy the pinned OP formula.
                events = [list(map(int, line.split())) for line in Path(str(prefix) + '-events.txt').read_text().splitlines()]
                assert all(len(event) == 8 for event in events)
                merged = bytearray(memory.memory)
                op_writes, current_object, pending_long = [], None, None
                for event in events:
                    sequence, frame, halfline, kind, who, pc, address, value = event
                    if kind == 6:  # VJT_EV_OP_OBJECT
                        current_object = (address, value)
                    if kind != 12 or who != 8:  # WATCH_WR / OP
                        continue
                    assert current_object is not None and current_object[1] == 0
                    base_address = current_object[0]
                    assert base_address % 8 == 0 and base_address + 16 <= len(merged)
                    if address == base_address:
                        assert pending_long is None
                        pending_long = (address, value)
                        continue
                    assert address == base_address + 4 and pending_long is not None and pending_long[0] == base_address
                    p0 = int.from_bytes(merged[base_address:base_address + 8], 'big')
                    p1 = int.from_bytes(merged[base_address + 8:base_address + 16], 'big')
                    height = (p0 & 0xffc000) >> 14
                    assert p0 & 7 == 0 and height > 0
                    data = ((p0 & 0xfffff80000000000) >> 40) + ((p1 & 0xffc0000) >> 15)
                    predicted = ((p0 & ~0xfffff80000ffc000) | ((height - 1) << 14) | (data << 40)) & 0xffffffffffffffff
                    actual = (pending_long[1] << 32) | value
                    assert predicted == actual, (case['name'], ordinal, 'OP writeback formula differs')
                    # The readable body must not depend on or modify the
                    # supplied concurrent phrase locations.
                    assert not any(row[0] in ['r', 'w'] and row[1] < base_address + 8 and row[1] + row[2] > base_address for row in memory.trace)
                    merged[base_address:base_address + 8] = actual.to_bytes(8, 'big')
                    op_writes.append(dict(sequence=sequence, halfline=halfline, address=base_address,
                                          before=p0, after=actual, writer='OP', source_formula_verified=True))
                    pending_long = None
                assert pending_long is None
                actual_public = merged[:stack_low] + merged[sp + 4:]
                assert actual_public == expected_public, (case['name'], ordinal, 'public RAM mismatch')
                get = lambda data, address: int.from_bytes(data[address:address + 2], 'big')
                hits = int(np.count_nonzero(pcs == 0x18e5c))
                calls.append(dict(ordinal=ordinal, entry_instruction=first, return_instruction=last,
                                  original_instructions=last - first, D0=d0,
                                  private_stack_excluded=[stack_low, sp + 4], damage_instruction_hits=hits,
                                  health_before=get(entry, 0x49fd0), health_after=get(returned, 0x49fd0),
                                  real_RNG_calls=sum(row[0] == 'call' and row[1] == 0x1a77c for row in memory.trace),
                                  concurrent_OP_writebacks=op_writes, OP_effects_supplied_to_private_replay=bool(op_writes),
                                  readable_public_effects=[row for row in memory.trace if row[0] == 'w'],
                                  public_RAM_sha256=hashlib.sha256(expected_public).hexdigest()))
            assert sum(row['damage_instruction_hits'] for row in calls) == 1
            damage = next(row for row in calls if row['damage_instruction_hits'])
            assert damage['health_before'] == 2 and damage['health_after'] == 0xffc6
            results.append(dict(name=case['name'], frames=case['frames'], observer_inertness=unchanged,
                                natural_calls=len(calls), calls=calls, directory=str(folder)))
        proof = dict(status='readable_attack_and_real_C_RNG_match_natural_original_invocation_effects',
                     recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(out), cases=results,
                     natural_calls=sum(row['natural_calls'] for row in results), damage_calls=2,
                     source=str(readable), source_sha256=digest(readable), readable_compiler=readable_command,
                     original_gameplay_proof=state['original_gameplay_proof'], observer_inert=True,
                     target_fields_patched=False, game_program_patched=False,
                     concurrent_OP_effects_supplied=True, OP_source=state['OP_source'], OP_source_sha256=state['OP_source_sha256'],
                     high_level_component_in_frame_runtime=False, native_keyboard_verified=False,
                     new_training=False, whole_game_complete=False,
                     scope='Readable18DF2body and actual C indexedRNG/division/multiply replay privately from all observed native entry RAM states in the ordinary120/300frame unarmed/Beretta routes. FullD0 matches; every nonstack RAM byte matches after merging native-traced concurrent OP bitmap writebacks, each independently checked against the pinned OPStorePhrase formula and disjoint from readable bus accesses. Both natural60point damage calls match. Observer runs reproduce all earlier CPU/cycle/frame/final-machine/PCM bytes. No supplied RNG return, target/position/game-code injection or asynchronous CPU code in each call span. Concurrent OP effects are supplied, not generated by this component. Private CPU registers/CCR/stack/cycles and live replacement of the instruction-level frame body remain excluded; no standalone/audio/wholegame promotion.')
        save(out / 'report.json', proof)
        save(ROOT / 'verification/natural-attack-effect-current.json', proof)
        state.update(status='terminal_readable_natural_attack_effect_match', natural_calls=proof['natural_calls'])
        checkpoint()
        print(json.dumps(dict(status=proof['status'], natural_calls=proof['natural_calls'], damage_calls=2)), flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        checkpoint()
        raise


if __name__ == '__main__':
    main()
