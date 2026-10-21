"""Real captured CPU/task frames through the request-to-scheduler bridge.

The earlier logical effects use a declared interface fixture. Other tasks'
execution is supplied by inertness-checked natural snapshots, not executed
by this host test. The first scheduler dispatch itself runs readable C.
"""
import ctypes as c
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

import check_biwn_coordinate_flow as flow
import check_biwn_scheduler as scheduler
from check_biwn_natural_coordinate_scheduler import DTYPE, cpu_record, sha, save
import numpy as np

ROOT = flow.ROOT
RESTORE = flow.RESTORE


class Ticket(c.Structure):
    _fields_ = [('context', c.c_uint64), ('sequence', c.c_uint64),
                ('phase', c.c_uint32), ('owner', c.c_uint32), ('return_sp', c.c_uint32),
                ('saved', c.c_uint32 * 11)]


class Memory:
    def __init__(self, data, fail_at=None):
        self.memory, self.trace, self.errors = bytearray(data), [], []
        self.fail_at = fail_at
        self.events = 0
        self.context = 0x123456
        def read(width):
            def callback(context, address, value):
                assert context == self.context
                self.events += 1
                if self.events == self.fail_at:
                    return 1
                if address + width > len(self.memory):
                    self.errors.append('outside RAM');return 1
                value[0] = int.from_bytes(self.memory[address:address + width], 'big')
                self.trace.append(['r', address, width, value[0]])
                return 0
            return callback
        def write(width):
            def callback(context, address, value):
                assert context == self.context
                self.events += 1
                if self.events == self.fail_at:
                    return 1
                if address + width > len(self.memory):
                    self.errors.append('outside RAM');return 1
                self.memory[address:address + width] = value.to_bytes(width, 'big')
                self.trace.append(['w', address, width, value])
                return 0
            return callback
        world = scheduler.cleanup.world
        self.callbacks = [world.R8(read(1)), world.R16(read(2)), world.R32(read(4)),
                          world.W16(write(2)), world.W32(write(4)), world.CALL()]
        self.bus = world.Bus(*self.callbacks, self.context, 0)


def main():
    out = ROOT / 'verification/coordinate-yield' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    proof_path = ROOT / 'verification/natural-coordinate-scheduler-current.json'
    proof = json.loads(proof_path.read_text())
    assert proof['status'] == 'terminal_captured_scheduler_matches'
    assert sha(proof['scheduler_source']) == proof['scheduler_source_sha256']
    capture_dir = Path(proof['directory']) / 'captures'
    rows = json.loads((Path(proof['directory']) / 'transitions.json').read_text())
    first, last = rows[0]['first'], rows[-1]['last']
    before = (capture_dir / f'{first}.ram').read_bytes()
    entry = np.frombuffer((capture_dir / f'{first}.cpu').read_bytes(), dtype=DTYPE)[0]
    cpu = scheduler.make_cpu(cpu_record(entry))
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
               '-I', str(RESTORE), *[str(RESTORE / name) for name in
               ['biwn_coordinate_yield.c', 'biwn_scheduler.c', 'biwn_coordinate_flow.c', 'biwn_inventory_select.c']],
               '-o', str(out / 'libcoordinate-yield.dylib')]
    result = subprocess.run(command, capture_output=True, text=True,
                            env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    lib = c.CDLL(str(out / 'libcoordinate-yield.dylib'))
    begin, poll = lib.biwn_coordinate_yield_begin, lib.biwn_coordinate_yield_poll
    begin.argtypes = [c.POINTER(scheduler.cleanup.world.Bus), c.POINTER(Ticket), c.POINTER(flow.Request), c.POINTER(scheduler.CPU), c.c_uint32]
    begin.restype = c.c_int
    poll.argtypes = [c.POINTER(scheduler.cleanup.world.Bus), c.POINTER(Ticket), c.POINTER(scheduler.CPU), c.POINTER(flow.Completion)]
    poll.restype = c.c_int
    engine = flow.Engine(out / 'libcoordinate-yield.dylib')
    prior = json.loads((ROOT / 'verification/readable-coordinate-entry-current.json').read_text())
    standalone = json.loads(Path(prior['standalone_proof']).read_text())
    cases = json.loads((Path(standalone['directory']) / 'fixtures.json').read_text())
    case = next(row for row in cases if row['name'] == 'confirm_123_456')
    case['actions'][:6] = [dict(held=1, digit=int(digit)) for digit in '203662']
    script = flow.original.Script((ROOT / 'verification/zero-warm-startup-instruction-atlas.bin').read_bytes(), case)
    state, request = flow.Flow(), flow.Request()
    assert engine.begin(c.byref(state), 0x18200001, case['incoming'][0]) == 0
    assert engine.advance(c.byref(state), None, c.byref(request)) == 0
    fixture_effects = 0
    while not (request.kind == 7 and request.address == 0xdf60):
        value = flow.effect(script, request)
        # Explicitly supplied interface value, not a new cleanup-body proof.
        if request.kind == 7 and request.address == 0x20e8c:
            value = cpu.registers[0]
        reply = flow.Completion(request.context, request.sequence, value, 0)
        assert engine.advance(c.byref(state), c.byref(reply), c.byref(request)) == 0
        fixture_effects += 1
        assert fixture_effects < 10000
    original_request = flow.Request.from_buffer_copy(bytes(request))
    memory, ticket = Memory(before), Ticket()
    assert begin(c.byref(memory.bus), c.byref(ticket), c.byref(request), c.byref(cpu), 1024) == 0
    assert scheduler.cpu_dict(cpu) == dict(registers=rows[0]['return_CPU']['registers'],
        pc=rows[0]['return_CPU']['entry'], usp=rows[0]['return_CPU']['usp'],
        ssp=rows[0]['return_CPU']['ssp'], sr=rows[0]['return_CPU']['sr'])
    # Repeated begin must not dispatch twice or touch the bus/CPU/ticket.
    saved = (bytes(ticket), bytes(cpu), list(memory.trace), bytes(memory.memory))
    assert begin(c.byref(memory.bus), c.byref(ticket), c.byref(request), c.byref(cpu), 1024) == 2
    assert saved == (bytes(ticket), bytes(cpu), memory.trace, bytes(memory.memory))
    pending = []
    for row in rows:
        index = row['last']
        memory = Memory((capture_dir / f'{index}.ram').read_bytes())
        actual = scheduler.make_cpu(cpu_record(np.frombuffer((capture_dir / f'{index}.cpu').read_bytes(), dtype=DTYPE)[0]))
        reply = flow.Completion(999, 998, 997, -996)
        output_before, ticket_before, flow_before = bytes(reply), bytes(ticket), bytes(state)
        ticket = Ticket.from_buffer_copy(bytes(ticket))
        status = poll(c.byref(memory.bus), c.byref(ticket), c.byref(actual), c.byref(reply))
        if index != last:
            assert status == 0 and bytes(reply) == output_before and bytes(ticket) == ticket_before
            assert engine.advance(c.byref(state), None, c.byref(request)) == 0
            assert bytes(state) == flow_before and bytes(request) == bytes(original_request)
            pending.append(dict(index=index, selected_task=row['owner_after'], selected_PC=hex(actual.pc)))
        else:
            assert status == 1 and reply.context == original_request.context and reply.sequence == original_request.sequence
            assert reply.value == actual.registers[0] and reply.status == 0
            assert engine.advance(c.byref(state), c.byref(reply), c.byref(request)) == 0
            assert request.kind == 7 and request.address == 0xdf22 and request.incoming_d0 == actual.registers[0]
            stale_state = bytes(state)
            assert engine.advance(c.byref(state), c.byref(reply), c.byref(request)) == 4 and bytes(state) == stale_state
            trace_before, reply_before = list(memory.trace), bytes(reply)
            assert poll(c.byref(memory.bus), c.byref(ticket), c.byref(actual), c.byref(reply)) == 6
            assert memory.trace == trace_before and bytes(reply) == reply_before
    guards = []
    def reject(name, request_change=None, cpu_change=None, ram_change=None, missing=None, fail_at=None, limit=1024, expected=2):
        test_memory, test_ticket = Memory(before, fail_at), Ticket()
        test_request = flow.Request.from_buffer_copy(bytes(original_request))
        test_cpu = scheduler.make_cpu(cpu_record(entry))
        if request_change:request_change(test_request)
        if cpu_change:cpu_change(test_cpu)
        if ram_change:ram_change(test_memory.memory)
        if missing is not None:setattr(test_memory.bus, missing, type(getattr(test_memory.bus, missing))())
        ticket_before, cpu_before = bytes(test_ticket), bytes(test_cpu)
        status = begin(c.byref(test_memory.bus), c.byref(test_ticket), c.byref(test_request), c.byref(test_cpu), limit)
        assert status == expected and bytes(test_ticket) == ticket_before and bytes(test_cpu) == cpu_before, name
        if expected == 2:assert not test_memory.trace, name
        guards.append(dict(case=name, status=status, CPU_and_ticket_unchanged=True, prior_bus_writes_retained=any(event[0] == 'w' for event in test_memory.trace)))
    for field, value in [('context', 0), ('sequence', 0), ('kind', 3), ('address', 0xdf22), ('argument_count', 1), ('incoming_d0', cpu_record(entry)['registers'][0] ^ 1)]:
        reject('invalid_' + field, request_change=lambda request, f=field, v=value: setattr(request, f, v))
    for field in ['read32', 'read16', 'write16', 'write32']:
        reject('missing_' + field, missing=field)
    reject('zero_limit', limit=0)
    reject('wrong_PC', cpu_change=lambda cpu: setattr(cpu, 'pc', 0xdf64), expected=3)
    reject('supervisor', cpu_change=lambda cpu: setattr(cpu, 'sr', cpu.sr | 0x2000), expected=3)
    reject('stack_overflow', cpu_change=lambda cpu: cpu.registers.__setitem__(15, 0xfffffffe), expected=3)
    sp = int(entry['registers'][15])
    reject('wrong_return', ram_change=lambda ram: ram.__setitem__(slice(sp, sp+4), (0x19760).to_bytes(4, 'big')), expected=3)
    reject('no_owner', ram_change=lambda ram: ram.__setitem__(slice(0xc0920, 0xc0924), bytes(4)), expected=3)
    for fail_at in [1, 2]:reject('read_failure_' + str(fail_at), fail_at=fail_at, expected=4)
    reject('bad_trap_vector', ram_change=lambda ram: ram.__setitem__(slice(0x80, 0x84), bytes(4)), expected=5)
    # Every callback in successful begin may fail; CPU/ticket are not committed,
    # but successful writes preceding failure remain. Never automatically retry.
    good_memory, good_ticket = Memory(before), Ticket()
    good_cpu = scheduler.make_cpu(cpu_record(entry))
    assert begin(c.byref(good_memory.bus), c.byref(good_ticket), c.byref(original_request), c.byref(good_cpu), 1024) == 0
    for index in range(3, good_memory.events + 1):reject('scheduler_bus_failure_' + str(index), fail_at=index, expected=5)
    final_cpu = scheduler.make_cpu(cpu_record(np.frombuffer((capture_dir / f'{last}.cpu').read_bytes(), dtype=DTYPE)[0]))
    final_ram = (capture_dir / f'{last}.ram').read_bytes()
    for register in [2,3,4,5,6,7,10,11,12,13,14,15,17]:
        test_cpu = scheduler.copy_cpu(final_cpu)
        if register == 17:test_cpu.sr |= 0x2000
        else:test_cpu.registers[register] ^= 1
        test_ticket = Ticket.from_buffer_copy(bytes(good_ticket))
        test_memory, reply = Memory(final_ram), flow.Completion(1,2,3,4)
        ticket_before, reply_before = bytes(test_ticket), bytes(reply)
        assert poll(c.byref(test_memory.bus), c.byref(test_ticket), c.byref(test_cpu), c.byref(reply)) == 3
        assert bytes(test_ticket) == ticket_before and bytes(reply) == reply_before
        guards.append(dict(case='wrong_resume_register_' + str(register), status=3, output_and_ticket_unchanged=True))
    test_ticket = Ticket.from_buffer_copy(bytes(good_ticket));test_memory = Memory(final_ram, fail_at=1)
    reply = flow.Completion(1,2,3,4);saved_reply=bytes(reply);saved_ticket=bytes(test_ticket)
    assert poll(c.byref(test_memory.bus), c.byref(test_ticket), c.byref(final_cpu), c.byref(reply)) == 4
    assert bytes(reply)==saved_reply and bytes(test_ticket)==saved_ticket
    guards.append(dict(case='poll_bus_error', status=4, output_and_ticket_unchanged=True))
    save(out / 'guards.json', guards)
    save(out / 'pending-contexts.json', pending)
    dependencies = [RESTORE / name for name in ['biwn_coordinate_yield.c', 'biwn_coordinate_yield.h', 'biwn_scheduler.c', 'biwn_scheduler.h', 'biwn_coordinate_flow.c', 'biwn_coordinate_flow.h', 'biwn_inventory_select.c', 'biwn_world_update.h']]
    report = dict(status='captured_task_owned_coordinate_yield_bridge_matches', recorded_at=datetime.now(timezone.utc).isoformat(),
                  directory=str(out), compile_command=command, guard_count=len(guards),
                  library=str(out / 'libcoordinate-yield.dylib'), library_sha256=sha(out / 'libcoordinate-yield.dylib'),
                  code_authorship='Codex coordinator wrote bridge, observer and checks; existing readable scheduler reused.',
                  source_sha256={str(path): sha(path) for path in dependencies},
                  captured_scheduler_proof=str(proof_path), captured_scheduler_proof_sha256=sha(proof_path),
                  scheduler_transitions_observed=len(rows), pending_observations=len(pending),
                  coordinate_owner=proof['coordinate_owner'], coordinate_return_PC='0x18faa',
                  request_context=original_request.context, request_sequence=original_request.sequence,
                  completed_once=True, duplicate_dispatch_rejected=True, duplicate_reply_rejected=True,
                  eleven_saved_registers_verified=True, source_bus_context_forwarded=True,
                  preceding_logical_fixture_effects=fixture_effects, preceding_cleanup_return_supplied=True,
                  other_game_task_bodies_executed_by_this_test=False, native_snapshots_supplied=True,
                  actual_live_frame_installation=False, new_training=False, whole_game_complete=False,
                  scope='Request from real logical engine, first task switch executed by C on captured original frame/RAM. Ticket remains pending across all captured intervening selected contexts and completes once only at owning18FAA/SP with11saved registers. Other tasks/device/IRQ execution supplied by independently inertness-checked natural snapshots. Preceding logical calls are an interface fixture, not a natural full-flow or standalone runtime proof.')
    save(out / 'report.json', report)
    save(ROOT / 'verification/coordinate-yield-current.json', report)
    print(json.dumps(dict(status=report['status'], directory=str(out), guards=len(guards), pending=len(pending))), flush=True)


if __name__ == '__main__':
    main()
