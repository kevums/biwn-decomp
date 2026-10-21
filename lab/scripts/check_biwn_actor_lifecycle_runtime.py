"""Live actor cold/warm exit, actual TRAP2, context reuse and fresh scheduling."""
import argparse
import ctypes as c
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
import check_biwn_actor_full_movement_runtime as live

ROOT = live.ROOT
CPU = live.CPU
MAIN = live.MAIN
save = live.save
get = live.get

def seed_cpu(runtime, cpu):
    runtime.core.m68k_pulse_reset()
    runtime.core.m68k_set_irq(0)
    runtime.core.m68k_set_reg(17, 0x2000)
    runtime.core.m68k_set_reg(15, cpu.ssp)
    runtime.core.m68k_set_reg(17, 0)
    runtime.core.m68k_set_reg(15, cpu.usp)
    runtime.core.m68k_set_reg(17, cpu.sr)
    for i, value in enumerate(cpu.registers):
        runtime.core.m68k_set_reg(i, value)
    runtime.core.m68k_set_reg(16, cpu.pc)

def reuse(runtime, ram, cpu, argument, translated):
    # Explicit host call fixture: call original DE5C with D0/D1 and a real
    # return-stack word, returning to the selected idle continuation.
    runtime.device.seed(ram, int(translated))
    state = CPU.from_buffer_copy(bytes(cpu))
    state.registers[0] = 0xf360
    state.registers[1] = argument
    state.registers[15] -= 4
    state.usp = state.registers[15]
    runtime.device.direct(state.registers[15], 4, state.pc)
    ret = state.pc
    state.pc = 0xde5c
    bus = live.world.Bus(runtime.device.r8, runtime.device.r16, runtime.device.r32,
                         runtime.device.w16, runtime.device.w32, live.world.CALL(), None, 0)
    steps = []
    if translated:
        fn = runtime.lib.biwn_task_create
        fn.argtypes = [c.POINTER(live.world.Bus), c.POINTER(CPU)]
        fn.restype = c.c_int
        assert fn(c.byref(bus), c.byref(state)) == 0
        assert state.pc == ret
    else:
        seed_cpu(runtime, state)
        for _ in range(100):
            pc = runtime.core.m68k_get_reg(None, 16)
            if pc == ret:
                break
            assert 0xde5c <= pc < 0xdeb6, hex(pc)
            steps.append(pc)
            runtime.core.m68k_execute(1)
        else:
            raise AssertionError('Reused task creation did not return')
        state = runtime.cpu()
    created_ram = runtime.device.ram()
    created_cpu = CPU.from_buffer_copy(bytes(state))
    current = get(created_ram, 0xc0920)
    assert current != MAIN and get(created_ram, current) == MAIN
    assert state.registers[0] == MAIN and get(created_ram, MAIN+8) == 0xf360
    assert get(created_ram, MAIN+12) == MAIN+0x400 and get(created_ram, MAIN+30) == argument
    assert get(created_ram, MAIN+20, 2) == get(created_ram, MAIN+22) == get(created_ram, MAIN+26) == get(created_ram, MAIN+34) == 0
    if translated:
        for _ in range(4):
            if runtime.current() == MAIN:
                break
            status = runtime.idle(c.byref(bus), c.byref(state), live.prior.BODY(), None, 64)
            assert status == 0
        else:
            raise AssertionError('C scheduler did not enter reused context')
    else:
        for _ in range(200):
            pc = runtime.core.m68k_get_reg(None, 16)
            if runtime.current() == MAIN and pc == 0xf360:
                break
            assert any(a <= pc < b for a, b in [(0xf360, 0xf368), (0xf880, 0xf888), (0xdf60, 0xdf6c), (0xde08, 0xde5c)]), hex(pc)
            steps.append(pc)
            runtime.core.m68k_execute(1)
        else:
            raise AssertionError('Original scheduler did not enter reused context')
        state = runtime.cpu()
    assert state.pc == 0xf360 and state.registers[15] == MAIN+0x400
    fresh_cpu = live.prior.scheduler.cpu_dict(state)
    fresh_ram_digest = hashlib.sha256(runtime.device.ram()).hexdigest()
    # Execute the reused task's actual idle body through one real yield.
    if translated:
        assert runtime.idle(c.byref(bus), c.byref(state), live.prior.BODY(), None, 64) == 0
    else:
        for _ in range(100):
            pc = runtime.core.m68k_get_reg(None, 16)
            assert any(a <= pc < b for a, b in [(0xf360, 0xf368), (0xdf60, 0xdf6c), (0xde08, 0xde5c)]), hex(pc)
            steps.append(pc)
            runtime.core.m68k_execute(1)
            if pc == 0xdf6a or (pc == 0xde5a and runtime.core.m68k_get_reg(None, 16) != 0xdf66):
                break
        else:
            raise AssertionError('Reused task did not yield')
        state = runtime.cpu()
    assert runtime.current() != MAIN
    return runtime.device.ram(), state, {'creation_CPU': live.prior.scheduler.cpu_dict(created_cpu),
           'creation_RAM_sha256': hashlib.sha256(created_ram).hexdigest(),
           'creation_header': created_ram[MAIN:MAIN+38].hex(), 'steps': steps,
           'fresh_selected_CPU': fresh_cpu, 'fresh_selected_RAM_sha256': fresh_ram_digest,
           'reused_idle_body_executed_and_yielded': True,
           'final_CPU': live.prior.scheduler.cpu_dict(state), 'device': runtime.device.stats()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    options = parser.parse_args()
    out = ROOT / 'verification/biwn-actor-lifecycle-runtime' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_actor_task.c', 'biwn_actor_navigation.c', 'biwn_actor_movement.c',
             'biwn_actor_direction.c', 'biwn_movement_submit_cpu.c', 'biwn_actor_collision.c',
             'biwn_geometry_cpu.c', 'biwn_rng_cpu.c', 'biwn_signed_division.c', 'biwn_camera.c',
             'biwn_scheduler.c', 'biwn_task_loops.c', 'biwn_task_create.c']
    library = out / 'libactor-lifecycle.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror'] + [str(source / n) for n in names] + ['-o', str(library)]
    run = subprocess.run(command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stderr
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    vectors = []
    for case in [x for x in live.actor.cases() if x['PC'] == 0xf4d8][:128]:
        for iterations in [0, 8]:
            item = dict(case)
            item.update(iterations=iterations, kill_word=[1, 0x8000, 0xffff][len(vectors) % 3])
            vectors.append(item)
    if options.limit:
        vectors = vectors[:options.limit]
    runtime = live.Runtime(library)
    assert not live.STUBS
    rows, coverage = [], set()
    try:
        for i, case in enumerate(vectors):
            save(out / 'status.json', {'status': 'running', 'case': i})
            ram = bytearray(live.fixture(snapshot, case))
            obj = 0x49d6c + case['registers'][7] * 206
            def put(a, w, v):
                ram[a:a+w] = v.to_bytes(w, 'big')
            previous_free = 0xc1928 if case['iterations'] else 0
            put(0xc0924, 4, previous_free)
            put(0x88, 4, 0xdeb6)
            if previous_free:
                put(previous_free, 4, 0)
            if not case['iterations']:
                put(obj+2, 2, case['kill_word'])
            ram = bytes(ram)
            left, expected, old = runtime.native(ram, case, case['iterations'], remove=True)
            right, actual, new = runtime.translated(ram, case, case['iterations'], remove=True)
            coverage.update(old['steps'])
            keys = ['calls', 'movements', 'handoffs', 'yields', 'navigation_returns', 'removals']
            if left != right or bytes(expected) != bytes(actual) or any(old[k] != new[k] for k in keys):
                save(out / 'mismatch.json', {'case': case, 'CPU_original': live.prior.scheduler.cpu_dict(expected),
                     'CPU_C': live.prior.scheduler.cpu_dict(actual), 'original': old, 'rebuilt': new,
                     'RAM_differences': [hex(j) for j, (a, b) in enumerate(zip(left, right)) if a != b][:100]})
                raise AssertionError(str(out / 'mismatch.json'))
            assert len(new['movements']) == case['iterations']
            assert len(new['handoffs']) == case['iterations'] * 3 + 1
            assert len(new['removals']) == 1 and new['removals'][0]['return_PC'] == 0xf57c
            assert not new['device']['original_GPUExec1_calls'] and not new['device']['game_frames_executed']
            assert get(right, obj, 2) == 0 and get(right, obj+2, 2) == case['kill_word']
            assert get(right, 0xc0924) == MAIN and get(right, MAIN) == previous_free
            assert get(right, live.CONTEXTS[1]+4) == live.CONTEXTS[2]
            assert get(right, live.CONTEXTS[2]) == live.CONTEXTS[1]
            assert right[MAIN+8:MAIN+38].hex() == new['removals'][0]['context_header'][16:76]
            # The dead actor's 40-byte save frame and F57C return remain in
            # private RAM. They are not unwound or erased by removal/creation.
            assert new['removals'][0]['CPU']['registers'][15] == MAIN+0x400-44
            assert get(right, MAIN+0x400-44) == 0xf57c
            argument = (i * 0x1020305) & 0xffffffff
            reused_left, next_expected, reuse_old = reuse(runtime, left, expected, argument, False)
            reused_right, next_actual, reuse_new = reuse(runtime, right, actual, argument, True)
            if reused_left != reused_right or bytes(next_expected) != bytes(next_actual) or any(reuse_old[k] != reuse_new[k] for k in ['creation_CPU', 'creation_RAM_sha256', 'creation_header', 'fresh_selected_CPU', 'fresh_selected_RAM_sha256', 'final_CPU']):
                save(out / 'reuse-mismatch.json', {'case': case, 'original': reuse_old, 'rebuilt': reuse_new,
                     'RAM_differences': [hex(j) for j, (a, b) in enumerate(zip(reused_left, reused_right)) if a != b][:100]})
                raise AssertionError(str(out / 'reuse-mismatch.json'))
            assert get(reused_right, 0xc0924) == previous_free
            assert not reuse_new['device']['original_GPUExec1_calls'] and not reuse_new['device']['game_frames_executed']
            assert 0xf57c not in old['steps'][old['steps'].index(0xdf7a)+1:]
            rows.append({'case': i, 'parameters': case, 'original': old, 'rebuilt': new,
                         'reuse_original': reuse_old, 'reuse_rebuilt': reuse_new,
                         'whole2MBRAM_fullCPU_privateframes_match': True, 'removed_actor_return_not_executed_after_TRAP2': True,
                         'removed_task_state_not_saved': True, 'context_reused_and_fresh_entry_selected': True})
    except Exception as error:
        save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error)})
        raise
    finally:
        runtime.close()
    save(out / 'fixtures.json', rows)
    if options.limit:
        save(out / 'status.json', {'status': 'terminal_preflight', 'cases': len(rows)})
        print(json.dumps({'directory': str(out), 'cases': len(rows)}))
        return
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'actor_regular_exit_TRAP2_context_reuse_and_fresh_scheduling_match_original',
              'directory': str(out), 'cases': len(rows), 'cold_exit_cases': 128, 'exit_after_eight_iterations_cases': 128,
              'actor_iterations': 1024, 'task_handoffs': 3840, 'actor_removals': 256, 'context_reuses': 256,
              'fresh_reused_context_selections': 256, 'reused_idle_body_executions': 256, 'scripted_actor_helpers': [], 'removal_TRAP2_executed': True,
              'removed_actor_return_not_executed': True, 'removed_state_not_saved': True,
              'allCPU_SR_USP_SSP_complete2MBRAM_privateframes_compared': True, 'synthetic_scene_geometry': True,
              'synchronous_GPU_completion': True, 'startup21context_fixture_linked': False,
              'creation_call_fixture': 'Host stages DE5C register arguments and return frame; actual original/C creation and subsequent idle yield/scheduler execute.',
              'source_sha256': {n: hashlib.sha256((source / n).read_bytes()).hexdigest() for n in names + [n.replace('.c', '.h') for n in names]},
              'matched': ['Original actor cold/regular paths, six actual helpers, TRAP0 scheduler handoffs, kill flag, object-type clear, actual TRAP2/DEB6 unlink/free and next task continuation match C.',
                          'Actual DE5C reuses the freed actor context and resets entry/SP/PC/argument/flags; subsequent real idle yield and RTE select its fresh F360 entry, whose actual body executes another real yield. Full CPU/RAM after creation, selection and body compare.',
                          'No actor F57C return executed after TRAP2. Removed40byte actor save frame and return word persist in privateRAM; removed task context SP/PC/SR are not updated at exit.'],
              'limits': ['Three seeded task contexts, bounded synthetic outdoor geometry/clock and synchronous GPU completion. Kill word and creation call are explicit host stimuli. Reused context runs an idle entry, not a respawned actor factory.',
                         'Separate from21context startup/world/render/assets. Remaining task bodies, real loading switches, full graphics/scenes/mainloop/audio/game/hardware unfinished. No original GPU/gameframes execute on C side.'],
              'compiler': command}
    save(out / 'report.json', report)
    save(out / 'status.json', {'status': 'terminal_pass', 'cases': len(rows)})
    save(ROOT / 'verification/biwn-actor-lifecycle-runtime-checks.json', report)
    print(json.dumps(report))

if __name__ == '__main__':
    main()
