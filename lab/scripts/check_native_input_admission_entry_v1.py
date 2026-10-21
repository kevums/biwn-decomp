"""Execute preflight on adversarial SP/task values; stop before either route.

No invalid-stack memory is mapped merely to make rejection pass. The small
trusted preflight frame is checked against each task's real metadata fence.
"""
import os
from pathlib import Path
import random
import subprocess
from datetime import datetime, timezone
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha
from check_local_input_task_admission_v1 import oracle, SLOTS, POOL, MASK


def main():
    local_path = V / 'local-input-task-admission-reviewed-v1-current.json'
    prior = read(local_path)
    assert prior['native_cases'] == 16280 and prior['host_cases'] == 1440596
    for path, digest in prior['source_sha256'].items():
        assert sha(path) == digest, path
    nd = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k'
    source = nd / 'input-dispatch-native-v4-admission'
    old_path = nd / 'input-dispatch-native-v3-entry/build-portable/native-input.bin'
    payload_path = source / 'build-portable/native-input.bin'
    payload = payload_path.read_bytes()
    old = old_path.read_bytes()
    assert payload[:len(old)] == old
    symbols = {}
    text = subprocess.check_output([str(ROOT / 'tools/m68k-elf/bin/m68k-elf-nm'), '-n',
                                    str(source / 'build-portable/native-input.elf')], text=True)
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 3:
            symbols[parts[2]] = int(parts[0], 16)
    base = 0x1c0000
    entry = symbols['biwn_native_input_admission_entry']
    c_entry = symbols['biwn_input_task_admit']
    native = symbols['biwn_native_input_entry']
    original = 0x191f4
    c_blob = Path(prior['directory']) / 'admission.bin'
    assert payload[c_entry-base:entry-base] == c_blob.read_bytes(), 'Local C code changed at integration'
    out = V / 'native-input-admission-entry-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V / 'native-input-admission-entry-v1-current.json'
    state = dict(status='running_68000_stack_first_admission', directory=str(out), pid=os.getpid(),
                 completed=0, new_predictions=0, optimizer_updates=0, installed_in_game=False,
                 full_caller_qualified=False, real_helper_bound_qualified=False, arbitrary_IRQ_qualified=False)

    def mark():
        save(out / 'protocol.json', state)
        save(pointer, state)

    mark()
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(base, payload)
    regs = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
            UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
            UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
            UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6]
    rng = random.Random(0x191f4b)
    task = sp = initial_sr = 0
    trace = []
    writes = []
    min_stack = None
    c_calls = 0

    def preflight_stack_is_safe():
        return task in SLOTS and initial_sr & 0x2000 == 0 and sp % 2 == 0 and task + 104 <= sp <= task + 1020

    def code(engine, pc, width, user):
        nonlocal min_stack, c_calls
        if pc in [native, original]:
            engine.emu_stop()
            return
        assert c_entry <= pc < base + len(payload), hex(pc)
        trace.append(pc)
        if pc == c_entry:
            c_calls += 1
            assert preflight_stack_is_safe()
        actual_sp = engine.reg_read(UC_M68K_REG_A7)
        if actual_sp != sp:
            assert preflight_stack_is_safe(), 'Stack changed before preflight'
            min_stack = actual_sp if min_stack is None else min(min_stack, actual_sp)

    def read_mem(engine, access, address, width, value, user):
        if address == 0xc0920 and width == 4:
            return
        assert preflight_stack_is_safe() and task + 64 <= address and address + width <= sp, (hex(address), width)

    def write_mem(engine, access, address, width, value, user):
        assert preflight_stack_is_safe() and task + 64 <= address and address + width <= sp, (hex(address), width)
        writes.append([address, width, value & ((1 << (width * 8)) - 1)])

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_READ, read_mem)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write_mem)
    modes = [0, 0x15, 0x700, 0x71f, 0x2000, 0x271f]
    vectors = [(t, t + offset, sr) for t in sorted(SLOTS)
               for offset in [0, 62, 63, 64, 65, 66, 102, 103, 104, 105, 106, 574, 575, 576, 577, 578, 1018, 1019, 1020, 1021, 1022, 1024]
               for sr in modes]
    vectors += [(t + delta, t + 1020, sr) for t in sorted(SLOTS)
                for delta in [-2, -1, 1, 2] for sr in modes]
    vectors += [(t, s, sr)
        for t in [0, 2, POOL - 1024, POOL - 1, POOL + 101 * 1024, 0xfffffc28, MASK, POOL]
        for s in [0, 1, 2, 64, 0xfffffc68, MASK - 3, MASK] for sr in modes]
    for _ in range(4096):
        t = rng.choice(sorted(SLOTS)) + rng.choice([0, 0, 0, -2, 1, 2])
        vectors.append((t, (t + rng.randrange(0, 1027)) & MASK, rng.choice(modes)))
    rows = []
    try:
        for index, (task, sp, requested_sr) in enumerate(vectors):
            trace = []
            writes = []
            min_stack = None
            c_calls = 0
            incoming = [rng.getrandbits(32) for _ in regs]
            for reg, value in zip(regs, incoming):
                cpu.reg_write(reg, value)
            alternate = 0x1ef800
            cpu.reg_write(UC_M68K_REG_SR, 0x2000)
            cpu.reg_write(UC_M68K_REG_A7, sp if requested_sr & 0x2000 else alternate)
            cpu.reg_write(UC_M68K_REG_SR, 0)
            cpu.reg_write(UC_M68K_REG_A7, alternate if requested_sr & 0x2000 else sp)
            cpu.reg_write(UC_M68K_REG_SR, requested_sr)
            initial_sr = cpu.reg_read(UC_M68K_REG_SR)
            cpu.mem_write(0xc0920, task.to_bytes(4, 'big'))
            if task in SLOTS:
                cpu.mem_write(task, b'\xa5' * 1024)
            cpu.emu_start(entry, 0x1ffffe, count=500, timeout=1000000)
            wanted = oracle(task, sp, initial_sr, 512)
            final_pc = cpu.reg_read(UC_M68K_REG_PC)
            assert final_pc == (native if wanted else original), dict(index=index, task=task, sp=sp, sr=initial_sr, PC=final_pc)
            assert cpu.reg_read(UC_M68K_REG_A7) == sp
            assert cpu.reg_read(UC_M68K_REG_SR) == initial_sr, dict(index=index, original=initial_sr, final=cpu.reg_read(UC_M68K_REG_SR))
            for i in [0, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14]:
                assert cpu.reg_read(regs[i]) == incoming[i], (index, i)
            cpu.reg_write(UC_M68K_REG_SR, initial_sr ^ 0x2000)
            assert cpu.reg_read(UC_M68K_REG_A7) == alternate
            cpu.reg_write(UC_M68K_REG_SR, initial_sr)
            assert c_calls == int(preflight_stack_is_safe())
            if not preflight_stack_is_safe():
                assert writes == [] and min_stack is None
            if task in SLOTS:
                assert bytes(cpu.mem_read(task, 64)) == b'\xa5' * 64, 'Task metadata/fence changed'
            rows.append(dict(task=task, sp=sp, SR=initial_sr, route='native' if wanted else 'original',
                             C_called=bool(c_calls), stack_bytes=sp-min_stack if min_stack is not None else 0,
                             private_stack_write_count=len(writes), instructions=len(trace)))
            if index % 512 == 0:
                state['completed'] = len(rows)
                mark()
        assert bytes(cpu.mem_read(base, len(payload))) == payload
        save(out / 'cases.json', rows)
        state.update(status='terminal_stack_first_admission_routes_and_fences_pass_caller_and_IRQ_open',
                     completed=len(rows), module_bytes=len(payload), prior_prefix_bytes=len(old),
                     prior_prefix_byte_identical=True, unedited_local_C_code_identical=True,
                     native_routes=sum(r['route'] == 'native' for r in rows),
                     checked_original_routes=sum(r['route'] == 'original' and r['C_called'] for r in rows),
                     early_original_routes=sum(not r['C_called'] for r in rows),
                     preflight_stack_bytes=max(r['stack_bytes'] for r in rows),
                     native_entry=entry, prototype_native_body=native, original_body=original,
                     all_101_task_slots_exercised=True, entry_D0_callee_save_SR_SP_and_banks_match=True,
                     no_public_writes_before_route=True, no_stack_access_before_preflight=True,
                     task_metadata_and_fence_unchanged=True, native_reserve_bytes=512,
                     native_reserve_full_real_helper_bound_proven=False,
                     original_invalid_stack_execution_safe_claim=False,
                     source_sha256={str(p): sha(p) for p in [Path(__file__), local_path, old_path, payload_path, c_blob,
                         out / 'cases.json', *[p for p in source.iterdir() if p.is_file()],
                         source / 'build-portable/native-input.elf']},
                     scope='68000admission routes stopped before original/native input execution. No stack access before user-mode slot/evenSP and40byte headroom check;actualCframe36bytes. Localpredicate unedited. D0/callee-save/fullSR/SP/banks preserved;D1/A0/A1 scratch. Original fallback is before native publiceffects but does not repair an invalid originalstack. Fullcaller,realhelpers,arbitraryIRQ,gameimage/freshroute remain open.')
        mark()
        print(state['status'], len(rows), 'cases', state['preflight_stack_bytes'], 'bytes', flush=True)
    except BaseException as error:
        save(out / 'completed-before-failure.json', rows)
        state.update(status='terminal_stack_first_admission_failed', completed=len(rows),
                     current_case=dict(task=task, sp=sp, SR=initial_sr, trace=trace, writes=writes), error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
