"""Full original1A188caller with one guarded JSRoperand intervention.

Input and world resources remain declared scripted dependencies. Real E220,
E098 and E588 CPU code executes; the device acknowledges only, no GPU math.
Tests original fallback and admitted native route on task-owned stacks.
"""
import gc
import os
from pathlib import Path
import random
from datetime import datetime, timezone
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_input_dispatch as dispatch
import check_biwn_world_update as world
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    guard_path = V / 'native-input-admission-entry-v1-current.json'
    guard = read(guard_path)
    assert guard['completed'] == 20188 and guard['prior_prefix_byte_identical']
    for path, digest in guard['source_sha256'].items():
        assert sha(path) == digest, path
    proof_path = V / 'native-input-entry-ABI-v2-current.json'
    proof = read(proof_path)
    assert proof['completed'] == 4630
    saved = read(Path(proof['directory']) / 'cases.json')
    inputs = [row['parameters'] for row in saved[::2]]
    assert len(inputs) == 2315
    worlds = world.cases()
    nd = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k/input-dispatch-native-v4-admission'
    payload_path = nd / 'build-portable/native-input.bin'
    payload = payload_path.read_bytes()
    base = 0x1c0000
    entry = guard['native_entry']
    native_body = guard['prototype_native_body']
    original_body = 0x191f4
    start = 0x1a188
    stop = 0x3000
    snapshot_path = ROOT / 'render-assets/biwn-inventory-baseline.bin'
    snapshot = snapshot_path.read_bytes()
    patch = b'\x4e\xb9' + entry.to_bytes(4, 'big')
    assert snapshot[0x1a266:0x1a26c] == b'\x4e\xb9\x00\x01\x91\xf4'
    world_helpers = [0xe4c0, 0x1b786, 0x19f2c, 0x19fda, 0xf0fa, 0xeb04, 0x20820]
    stubs = sorted(set([a for a in dispatch.HELPERS if a != 0xe588] + world_helpers))
    out = V / 'native-input-full-caller-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V / 'native-input-full-caller-v1-current.json'
    state = dict(status='running_full_original_world_caller_guarded_input', directory=str(out), pid=os.getpid(),
                 completed=0, planned_cases=2315*3, new_predictions=0, optimizer_updates=0,
                 game_image_changed=False, real_helper_bodies_qualified=False, arbitrary_IRQ_qualified=False)

    def mark():
        save(out / 'protocol.json', state)
        save(pointer, state)

    mark()

    class Script(dispatch.Script):
        def __init__(self, case):
            super().__init__(snapshot, case)
            self.polls = 0
            self.mode_reads = 0

        def read(self, address, width):
            if address == 0x49c60 and 'mode_reads' in self.case:
                values = self.case['mode_reads']
                self.put(address, width, values[min(self.mode_reads, len(values)-1)])
                self.mode_reads += 1
            return super().read(address, width)

        def world_call(self, address, args):
            return world.Script.call(self, address, args)

    covered = set()

    def execute(case, task, initial_sp, sr, changed, index):
        script = Script(case)
        script.put(0xc0920, 4, task)
        script.memory[task:task+64] = b'\xa5'*64
        cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        cpu.mem_map(0, 0x200000)
        cpu.mem_map(0xf02000, 0x2000)
        cpu.mem_write(0, bytes(script.memory))
        for a in stubs:
            cpu.mem_write(a, b'\x4e\x75')
        if changed:
            cpu.mem_write(base, payload)
            cpu.mem_write(0x1a266, patch)
        cpu.mem_write(initial_sp, stop.to_bytes(4, 'big'))
        for reg, value in zip(dispatch.world.REGS, case['incoming']):
            cpu.reg_write(reg, value)
        alternate = 0x1ef400
        cpu.reg_write(UC_M68K_REG_SR, 0x2000)
        cpu.reg_write(UC_M68K_REG_A7, initial_sp if sr & 0x2000 else alternate)
        cpu.reg_write(UC_M68K_REG_SR, 0)
        cpu.reg_write(UC_M68K_REG_A7, alternate if sr & 0x2000 else initial_sp)
        cpu.reg_write(UC_M68K_REG_SR, sr)
        minimum = initial_sp
        route = None
        instructions = 0
        matrix_args = []
        helper_contracts = []
        mailbox = {}
        busy_reads = ack_reads = 0
        latency = index % 3
        guard_reads = []

        def private(address, width):
            return task + 64 <= address and address + width <= task + 1024

        def code(engine, pc, width, user):
            nonlocal minimum, route, instructions
            minimum = min(minimum, engine.reg_read(UC_M68K_REG_A7))
            instructions += 1
            assert minimum >= task+64, (hex(minimum), hex(task))
            if start <= pc < 0x1a544:
                covered.add(pc)
            if pc in [native_body, original_body]:
                assert route is None
                route = 'native' if pc == native_body else 'original'
            if pc == 0xe220:
                a7 = engine.reg_read(UC_M68K_REG_A7)
                args = [int.from_bytes(engine.mem_read(a7+4+i*4, 4), 'big') for i in range(5)]
                matrix_args.append(args)
                # An explicit scripted GPU result, followed by actual CPU
                # mailbox submit/poll instructions; no GPU arithmetic proof.
                script.changed = []
                script.world_call(pc, args)
                for a, w, v in script.changed:
                    engine.mem_write(a, v.to_bytes(w, 'big'))
            if pc in stubs or pc == 0xe588:
                a7 = engine.reg_read(UC_M68K_REG_A7)
                caller = int.from_bytes(engine.mem_read(a7, 4), 'big')
                from_world = start <= caller < 0x1a544
                if from_world:
                    assert pc in world_helpers
                    if pc == 0xf0fa:
                        args = [engine.reg_read(UC_M68K_REG_D2)&0xffff, engine.reg_read(UC_M68K_REG_D3)&0xffff]
                    elif pc == 0x19f2c:
                        args = [int.from_bytes(engine.mem_read(a7+4+i*2, 2), 'big') for i in range(3)]
                    elif pc == 0x19fda:
                        args = [int.from_bytes(engine.mem_read(a7+4, 4), 'big'), int.from_bytes(engine.mem_read(a7+8, 2), 'big')]
                    elif pc == 0xeb04:
                        args = [int.from_bytes(engine.mem_read(a7+4, 4), 'big')]
                    else:
                        args = []
                else:
                    offset = 4
                    args = []
                    for w in dispatch.WIDTHS.get(pc, []):
                        args.append(int.from_bytes(engine.mem_read(a7+offset, w), 'big'))
                        offset += w
                if pc == 0xe588:
                    assert route == 'original'
                    script.trace.append(['call', pc, args])
                    return
                helper_contracts.append([pc, args, None if from_world else engine.reg_read(UC_M68K_REG_D0)])
                script.changed = []
                result = script.world_call(pc, args) if from_world else script.call(pc, args)
                for a, w, v in script.changed:
                    engine.mem_write(a, v.to_bytes(w, 'big'))
                engine.reg_write(UC_M68K_REG_D0, result)
                if not from_world and route == 'native':
                    for reg in [UC_M68K_REG_D1, UC_M68K_REG_A0, UC_M68K_REG_A1]:
                        engine.reg_write(reg, 0x13579bdf)
                return
            assert (start <= pc < 0x1a544 or 0x1b718 <= pc < 0x1b780
                or 0xe220 <= pc < 0xe26c or 0xe098 <= pc < 0xe0a6
                or 0xe588 <= pc < 0xe60a or 0x191f4 <= pc < 0x19f2c
                or changed and base <= pc < base+len(payload)), hex(pc)
            assert pc != base+0x283e, 'Native component rejected after side effects'

        def memory_read(engine, access, a, w, value, user):
            nonlocal busy_reads, ack_reads
            if private(a, w) or changed and base <= a < base+len(payload):
                return
            if changed and a == 0xc0920 and engine.reg_read(UC_M68K_REG_PC) >= entry:
                assert w == 4
                guard_reads.append(a)
                return
            if a >= 0xf02000:
                assert w == 4 and a in [0xf03200, 0xf03204]
                if a == 0xf03200:
                    value = int(busy_reads < latency)
                    busy_reads += 1
                else:
                    value = 0x4320 if ack_reads < latency else 0xffffffff
                    ack_reads += 1
                script.trace.append(['r', a, w, value])
            else:
                value = script.read(a, w)
            engine.mem_write(a, value.to_bytes(w, 'big'))

        def memory_write(engine, access, a, w, value, user):
            value &= (1 << (w*8))-1
            assert not changed or not (base <= a < base+len(payload) or 0x1a266 <= a < 0x1a26c)
            if private(a, w):
                return
            if a >= 0xf02000:
                assert w == 4 and 0xf03204 <= a <= 0xf0321c
                mailbox[a] = value
                script.trace.append(['w', a, w, value])
            else:
                script.write(a, w, value)

        cpu.hook_add(UC_HOOK_CODE, code)
        cpu.hook_add(UC_HOOK_MEM_READ, memory_read)
        cpu.hook_add(UC_HOOK_MEM_WRITE, memory_write)
        cpu.emu_start(start, stop, count=500000, timeout=5000000)
        assert cpu.reg_read(UC_M68K_REG_PC) == stop and cpu.reg_read(UC_M68K_REG_A7) == initial_sp+4
        assert route is not None
        final_sr = cpu.reg_read(UC_M68K_REG_SR)
        registers = [cpu.reg_read(reg) for reg in dispatch.world.REGS]
        for i in range(len(registers)):
            if i not in [0, 1, 8, 9]:
                assert registers[i] == case['incoming'][i]
        cpu.reg_write(UC_M68K_REG_SR, final_sr ^ 0x2000)
        assert cpu.reg_read(UC_M68K_REG_A7) == alternate
        cpu.reg_write(UC_M68K_REG_SR, final_sr)
        actual = bytearray(cpu.mem_read(0, 0x200000))
        assert actual[task:task+64] == b'\xa5'*64
        for a in stubs:
            actual[a:a+2] = script.memory[a:a+2]
        intervals = [(task+64, task+1024)]
        if changed:
            assert actual[base:base+len(payload)] == payload
            assert actual[0x1a266:0x1a26c] == patch
            assert actual[original_body:original_body+10] == snapshot[original_body:original_body+10]
            actual[0x1a266:0x1a26c] = script.memory[0x1a266:0x1a26c]
            intervals.append((base, base+len(payload)))
        at = 0
        for lo, hi in sorted(intervals):
            assert actual[at:lo] == script.memory[at:lo], (hex(at), hex(lo))
            at = hi
        assert actual[at:] == script.memory[at:]
        return dict(script=script, route=route, registers=registers, SR=final_sr,
                    stack=initial_sp-minimum, args=matrix_args, mailbox=mailbox,
                    helpers=helper_contracts, guard_reads=len(guard_reads), instructions=instructions)

    rows = []
    differences = []
    try:
        for i, input_case in enumerate(inputs):
            w = worlds[i % len(worlds)]
            case = dict(input_case, **{k: v for k, v in w.items() if k != 'initial'})
            case['initial'] = input_case['initial'] + w['initial']
            # Each input initial state remains explicit; world fixtures supply
            # positions, collision and camera outcomes, not a scripted input.
            case.pop('input_effects', None)
            for path, sr, offset in [('native', 0x700 | (i%32), 1020), ('supervisor_fallback', 0x2700 | (i%32), 1020), ('headroom_fallback', 0x700 | (i%32), 500)]:
                index = len(rows)
                task = 0xc0928 + (i%101)*1024
                sp = task+offset
                state['current_case'] = dict(input=i, path=path, task=task, initial_SP=sp)
                left = execute(case, task, sp, sr, False, index)
                right = execute(case, task, sp, sr, True, index)
                expected_route = 'native' if path == 'native' else 'original'
                assert right['route'] == expected_route, (index, right['route'])
                expected = [x for x in left['script'].trace if x[:2] != ['call', 0xe588]] if path == 'native' else left['script'].trace
                assert expected == right['script'].trace, ('trace', index)
                assert left['script'].memory == right['script'].memory, ('RAM', index)
                assert left['helpers'] == right['helpers'], ('helper arguments or D0 seed', index)
                assert left['args'] == right['args'] and left['mailbox'] == right['mailbox']
                assert left['SR'] == right['SR'], ('SR', index)
                raw = [j for j, (a, b) in enumerate(zip(left['registers'], right['registers'])) if a != b]
                assert set(raw).issubset({1, 8, 9}), (index, raw)
                if raw:
                    differences.append(dict(case=index, registers=raw, original=left['registers'], candidate=right['registers']))
                rows.append(dict(input_case=i, input_state=input_case['state'], path=path, task=task,
                                 original_stack=left['stack'], candidate_stack=right['stack'],
                                 final_SR_equal=True, public_RAM_bus_helper_contracts_equal=True,
                                 raw_volatile_register_differences=raw, guard_identity_reads=right['guard_reads']))
            if i%16 == 0:
                state['completed'] = len(rows)
                mark()
                gc.collect()
        save(out/'cases.json', rows)
        save(out/'raw-volatile-differences.json', differences)
        save(out/'covered-caller-instructions.json', sorted(covered))
        state.update(status='terminal_full_caller_public_state_flags_and_helpers_match_raw_volatile_limits_retained',
                     completed=len(rows), admitted_native_cases=sum(r['path']=='native' for r in rows),
                     original_fallback_cases=sum(r['path']!='native' for r in rows),
                     actual_caller_start=start, actual_caller_end=0x1a544,
                     raw_volatile_differing_cases=len(differences),
                     native_max_caller_stack=max(r['candidate_stack'] for r in rows if r['path']=='native'),
                     fallback_max_caller_stack=max(r['candidate_stack'] for r in rows if r['path']!='native'),
                     guarded_entry_component_prefix_preserved=True,
                     whole_public_RAM_bus_helper_arguments_and_D0_seeds_equal=True,
                     full_caller_final_SR_equal=True, actual_GPU_arithmetic_executed=False,
                     source_sha256={str(p):sha(p) for p in [Path(__file__),guard_path,proof_path,payload_path,snapshot_path,
                         Path(proof['directory'])/'cases.json',Path(dispatch.__file__),Path(world.__file__),
                         out/'cases.json',out/'raw-volatile-differences.json',out/'covered-caller-instructions.json']},
                     scope='Actualoriginal1A188..1A544caller/digithelper/E220/E098/E588CPUinstructions. OnlyJSR1A266operandredirected;global191F4unchanged.2315inputfixtures crossed cyclically with1024worldfixtures,each native/user,supervisorfallback,headroomfallback. Bothfallbacks executeoriginalinput. Resource/animation/collision/camera/entityhelpers scripted;GPUresultsscripted andmailboxackonly. PublicRAM,orderedbus/helperargs/inputD0seeds,finalSRandcallee-save agree. Rawvolatile differences retained;notrealhelperbody/universalABI/arbitraryIRQ/image/freshgameproof.')
        mark()
        print(state['status'], len(rows), 'cases', len(differences), 'raw contexts differ', flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json', rows)
        if 'left' in locals() and 'right' in locals():
            save(out/'failure-comparison.json',dict(original_trace=left['script'].trace,candidate_trace=right['script'].trace,
                original_helpers=left['helpers'],candidate_helpers=right['helpers']))
        state.update(status='terminal_full_caller_comparison_failed',completed=len(rows),error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
