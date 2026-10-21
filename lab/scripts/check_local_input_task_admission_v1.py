"""Independent integer-domain oracle and real M68000 C-ABI execution.

This verifies a pure predicate on a trusted fixture stack, not a preflight
entry adapter on untrusted task stacks. No image or preview is patched.
"""
import ctypes as c
import hashlib
import itertools
import os
from pathlib import Path
import random
import struct
import subprocess
import time
from datetime import datetime, timezone
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha

POOL = 0xc0928
SLOTS = frozenset(POOL + i * 1024 for i in range(101))
MASK = 0xffffffff


def oracle(task, sp, sr, reserve):
    # Python integers and explicit set/range membership cannot wrap.
    return int(task in SLOTS and sp in range(task + 64, task + 1021, 2)
               and sr & 0x2000 == 0 and reserve in range(2, 961, 2)
               and task + 64 + reserve <= sp)


def main():
    author_path = V / 'local-input-task-admission-author-v1-current.json'
    author = read(author_path)
    assert author['status'] == 'terminal_local_Coder_complete_unedited_candidate_review_pending'
    assert author['new_predictions'] == 1 and author['candidate_statement_edits'] == 0
    for path, digest in author['source_sha256'].items():
        assert sha(path) == digest, path
    candidate = Path(author['directory']) / 'candidate.c'
    out = V / 'local-input-task-admission-reviewed-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V / 'local-input-task-admission-reviewed-v1-current.json'
    state = dict(status='building_unedited_local_task_admission', directory=str(out), pid=os.getpid(),
                 host_cases=0, native_cases=0, new_predictions=0, optimizer_updates=0,
                 game_image_changed=False, installed_preview_changed=False,
                 runtime_entry_guard_qualified=False, native_Chat_verified=False)

    def mark():
        save(out / 'protocol.json', state)
        save(pointer, state)

    mark()
    commands = []

    def run(command):
        commands.append(command)
        result = subprocess.run(command, capture_output=True, text=True)
        with (out / 'build.log').open('a') as log:
            log.write(repr(command) + '\n' + result.stdout + result.stderr + '\n')
        assert result.returncode == 0, result.stderr[-2500:]
        return result.stdout

    start = time.monotonic()
    rows = []
    try:
        libpath = out / 'admission.dylib'
        run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-O2', '-shared', str(candidate), '-o', str(libpath)])
        lib = c.CDLL(str(libpath))
        fn = lib.biwn_input_task_admit
        fn.argtypes = [c.c_uint32] * 4
        fn.restype = c.c_int
        digest = hashlib.sha256()
        counts = {}

        def host_group(name, vectors):
            positive = negative = 0
            for v in vectors:
                wanted = oracle(*v)
                got = fn(*v)
                assert got == wanted, dict(group=name, inputs=v, expected=wanted, actual=got)
                digest.update(struct.pack('>4IB', *v, wanted))
                positive += wanted
                negative += 1 - wanted
            counts[name] = dict(cases=positive + negative, admitted=positive, rejected=negative)
            state['host_cases'] += positive + negative
            mark()

        host_group('exhaustive_one_slot_stack_and_reserve_boundaries', (
            (POOL, POOL + offset, 0, reserve)
            for offset in range(-4, 1029) for reserve in itertools.chain(range(965), [MASK, MASK - 1])))
        offsets = [-1, 0, 1, 62, 63, 64, 65, 66, 574, 575, 576, 577, 1018, 1019, 1020, 1021, 1022, 1024]
        reserves = [0, 1, 2, 4, 510, 512, 958, 960, 962, MASK]
        modes = [0, 0x2000, MASK ^ 0x2000, MASK]
        host_group('every_slot_stack_reserve_mode_cross_product', (
            (task, task + offset, sr, reserve)
            for task in sorted(SLOTS) for offset in offsets for reserve in reserves for sr in modes))
        host_group('all_interior_pool_task_addresses', (
            (task, task + 1020, 0, 512) for task in range(POOL - 2, POOL + 101 * 1024 + 3)))
        host_group('every_SR_low_word', ((POOL, POOL + 1020, sr, 512) for sr in range(65536)))
        rng = random.Random(0x191f4a)

        def random_vectors():
            for _ in range(100000):
                yield tuple(rng.getrandbits(32) for _ in range(4))
            for _ in range(100000):
                task = rng.choice(sorted(SLOTS)) + rng.choice([-2, -1, 0, 0, 0, 1, 2])
                yield (task, task + rng.randrange(0, 1027), rng.getrandbits(32) & ~0x2000,
                       rng.randrange(0, 965))

        host_group('seeded_full_uint32_and_near_valid_random', random_vectors())
        save(out / 'host-groups.json', counts)
        state.update(status='compiling_68000_unedited_task_admission', host_case_digest=digest.hexdigest())
        mark()
        cross = str(ROOT / 'tools/m68k-elf/bin/m68k-elf-')
        obj = out / 'admission.o'
        elf = out / 'admission.elf'
        binary = out / 'admission.bin'
        link = out / 'link.ld'
        link.write_text('OUTPUT_ARCH(m68k)\nENTRY(biwn_input_task_admit)\nSECTIONS {\n . = 0x1c0000;\n .text : { *(.text*) *(.rodata*) }\n /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }\n}\n')
        run([cross + 'gcc', '-std=c99', '-m68000', '-msoft-float', '-Os', '-ffreestanding',
             '-fno-builtin', '-fno-pic', '-fno-stack-protector', '-Wall', '-Wextra', '-Werror',
             '-c', str(candidate), '-o', str(obj)])
        run([cross + 'gcc', '-m68000', '-msoft-float', '-nostdlib', '-Wl,-T,' + str(link), str(obj), '-o', str(elf)])
        assert run([cross + 'nm', '-u', str(elf)]).strip() == '', 'Unexpected external dependency'
        run([cross + 'objcopy', '-O', 'binary', str(elf), str(binary)])
        disassembly = run([cross + 'objdump', '-d', str(elf)])
        (out / 'admission.disassembly.txt').write_text(disassembly)
        payload = binary.read_bytes()
        base = 0x1c0000
        stop = 0x3000
        trusted_sp = 0x1ff000
        cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        cpu.mem_map(0, 0x200000)
        cpu.mem_write(base, payload)
        regs = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
                UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
                UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
                UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6]
        saved = [i for i in range(15) if i not in [0, 1, 8, 9]]
        minimum = trusted_sp
        instructions = 0
        writes = 0

        def code(engine, pc, width, user):
            nonlocal minimum, instructions
            assert base <= pc < base + len(payload), hex(pc)
            minimum = min(minimum, engine.reg_read(UC_M68K_REG_A7))
            instructions += 1

        def access(engine, kind, address, width, value, user):
            assert (trusted_sp - 512 <= address and address + width <= trusted_sp + 20
                    or base <= address and address + width <= base + len(payload)), (hex(address), width)

        def write(engine, kind, address, width, value, user):
            nonlocal writes
            assert trusted_sp - 512 <= address and address + width <= trusted_sp, (hex(address), width)
            writes += 1

        cpu.hook_add(UC_HOOK_CODE, code)
        cpu.hook_add(UC_HOOK_MEM_READ, access)
        cpu.hook_add(UC_HOOK_MEM_WRITE, write)
        native_vectors = list((task, task + offset, sr, reserve)
            for task in sorted(SLOTS) for offset in [63, 64, 65, 66, 575, 576, 577, 1018, 1020, 1021]
            for reserve in [0, 2, 512, 960, 962] for sr in [0, 0x2000])
        native_vectors += [(task + delta, task + 1020, 0, 512)
                           for task in sorted(SLOTS) for delta in [-2, -1, 1, 2]]
        native_vectors += [(task, sp, sr, reserve)
            for task in [0, 2, POOL - 1024, POOL - 1, POOL + 101 * 1024, 0xfffffc28, MASK]
            for sp in [0, 2, 64, 0xfffffc68, MASK - 3, MASK]
            for sr in modes for reserve in reserves]
        for _ in range(4096):
            task = rng.choice(sorted(SLOTS))
            native_vectors.append((task, task + rng.randrange(0, 1027), rng.getrandbits(32), rng.randrange(0, 965)))
        state.update(status='running_real_68000_task_admission', planned_native_cases=len(native_vectors))
        mark()
        for index, vector in enumerate(native_vectors):
            minimum = trusted_sp
            instructions = writes = 0
            incoming = [rng.getrandbits(32) for _ in regs]
            for reg, value in zip(regs, incoming):
                cpu.reg_write(reg, value)
            cpu.reg_write(UC_M68K_REG_SR, 0)
            cpu.reg_write(UC_M68K_REG_A7, trusted_sp)
            frame = struct.pack('>5I', stop, *vector)
            cpu.mem_write(trusted_sp, frame)
            cpu.emu_start(base, stop, count=1000, timeout=1000000)
            assert cpu.reg_read(UC_M68K_REG_PC) == stop, (index, vector)
            assert cpu.reg_read(UC_M68K_REG_A7) == trusted_sp + 4
            result = cpu.reg_read(UC_M68K_REG_D0)
            expected = oracle(*vector)
            assert result == expected == fn(*vector), dict(case=index, inputs=vector, expected=expected, native=result)
            for i in saved:
                assert cpu.reg_read(regs[i]) == incoming[i], (index, i)
            assert bytes(cpu.mem_read(trusted_sp, 20)) == frame
            rows.append(dict(inputs=vector, admitted=result, stack_bytes=trusted_sp - minimum,
                             instructions=instructions, private_stack_writes=writes))
            if index % 512 == 0:
                state['native_cases'] = len(rows)
                mark()
        assert bytes(cpu.mem_read(base, len(payload))) == payload
        save(out / 'native-cases.json', rows)
        save(out / 'build-commands.json', commands)
        state.update(status='terminal_unedited_local_predicate_host_and_M68000_oracle_pass_not_runtime_guard',
                     native_cases=len(rows), native_module_bytes=len(payload),
                     native_stack_bytes=max(r['stack_bytes'] for r in rows),
                     native_max_instructions=max(r['instructions'] for r in rows),
                     host_groups=counts, candidate_source=str(candidate),
                     candidate_statement_edits=0, local_model_authored=True,
                     admitted_native_cases=sum(r['admitted'] for r in rows),
                     elapsed_seconds=round(time.monotonic() - start, 3),
                     all_101_slots_exercised=True, C_ABI_callee_save_and_return_SP_verified=True,
                     external_memory_accesses=False, linked_external_calls=False,
                     source_sha256={str(p): sha(p) for p in [Path(__file__), author_path, candidate,
                         out / 'host-groups.json', out / 'native-cases.json', out / 'build-commands.json',
                         out / 'build.log', link, libpath, obj, elf, binary, out / 'admission.disassembly.txt']},
                     scope='Unedited local C99 predicate on trusted fixture C-ABI stack. Independent Python big-integer set/range oracle. Every original slot, boundaries, uint32 extremes, exhaustive one-slot SP/reserve and all65536lowSRwords tested. Real68000instructions, callee-save/returnSP and private-only accesses pass. Does not establish safe preflight on invalid stacks, real helper or arbitraryIRQ bound, caller equivalence, image placement, fresh game or training gain.')
        mark()
        print(state['status'], state['host_cases'], state['native_cases'], flush=True)
    except BaseException as error:
        save(out / 'completed-native-before-failure.json', rows)
        state.update(status='terminal_local_task_admission_review_failed', error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
