"""Actual loaded gates -> cleanup -> actor removal -> scheduled C CD loading.

Host enters 19F2C on the captured world task with a controlled player position.
Five contexts run; renderer and sixteen other contexts are explicitly blocked.
Disc completion is an external event after actual scheduler handoff. Full
CPU/private RAM and helper/yield/removal/disc events compare against original.
"""
import ctypes as c
import hashlib
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_interior_loading_cpu as loading
import check_biwn_actor_full_movement_runtime as actor
import generate_biwn_interior_loading_cpu as loader_gen
import generate_biwn_transition_cpu as transition_gen
import generate_biwn_actor_factory_cpu as factory_gen
import generate_biwn_resource_cpu as resource_gen
import check_biwn_render_actors_runtime as startup

ROOT, CPU = loading.ROOT, loading.CPU
save, read, sha = loading.save, loading.read, loading.sha
WORLD, STOP, SSP = 0xc2128, 0x1ffe00, 0x1ff000
RUNNABLE = {WORLD, 0xc1928, 0xc1528, 0xc5928, 0xc5528}


class Runtime(loading.Runtime):
    def __init__(self, library, rows, generated):
        super().__init__(library, rows)
        self.device.close()
        self.device = actor.Device(ROOT / 'tools/libbiwn-interior-render-device.dylib')
        self.native_oracle.device = self.device
        self.generated = {row['address']: row for row in generated}
        self.owner = {}
        self.functions = {}
        self.return_functions = {}
        groups = {'interior_loading': loader_gen.RANGES, 'transition': transition_gen.RANGES,
                  'actor_factory': factory_gen.RANGES, 'resource': resource_gen.RANGES,
                  'doorway': {0x10430: 0x10520}}
        session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
        cd_rows = read(session / 'cd-wrapper-fullCPU-generation.json')['instructions_decoded']
        groups['cd'] = {row['address']: row['address'] + row['size'] for row in cd_rows}
        for name, ranges in groups.items():
            fn = getattr(self.lib, 'biwn_' + name + '_cpu_body')
            fn.argtypes = self.bodies[0x1aa40].argtypes
            fn.restype = c.c_int
            self.functions[name] = fn
            call = getattr(self.lib, 'biwn_' + name + '_cpu_call')
            call.argtypes = fn.argtypes
            call.restype = c.c_int
            self.return_functions[name] = call
            for lo, hi in ranges.items():
                for row in generated:
                    if lo <= row['address'] < hi:
                        self.owner[row['address']] = name
        self.actor_fn = actor.actor.bind(self.lib)
        self.rng = actor.rng_cpu.bind(self.lib)
        self.navigation = actor.navigation.bind(self.lib)
        self.yield_fn = self.lib.biwn_scheduler_yield
        self.remove_fn = self.lib.biwn_scheduler_remove
        for fn in [self.yield_fn, self.remove_fn]:
            fn.argtypes = [c.POINTER(loading.cd.world.Bus), c.POINTER(CPU), c.c_uint32]
            fn.restype = c.c_int
        self.idle_fn = self.lib.biwn_task_loop_step
        self.idle_fn.argtypes = [c.POINTER(loading.cd.world.Bus), c.POINTER(CPU), actor.prior.BODY, c.c_void_p, c.c_uint32]
        self.idle_fn.restype = c.c_int
        self.provider_targets = set(loader_gen.RANGES) | set(transition_gen.RANGES) | set(factory_gen.RANGES)
        self.provider_targets |= set(resource_gen.RANGES) | {0x20e8c, 0x20f0c, 0xe3ee, 0xd1e0, 0xd206, 0xd2f0, 0xd306, 0x10430,
                                                          0x1a77c, 0xe540, 0xe588, 0xe60a,
                                                          0xf368, 0x13f12, 0x13f7c, 0x13fea}

    def current(self):
        return self.device.read(0xc0920, 4)

    def reset_run(self, ram, translated):
        self.device.seed(ram, int(translated))
        self.disc.reset()
        self.calls, self.events, self.errors = [], [], []
        self.frames = defaultdict(list)
        self.idle_pending = None
        self.host_phase = 0

    def event(self, kind, state):
        row = {'kind': kind, 'context': self.current(), 'CPU': loading.cd.scheduler.cpu_dict(state),
               'RAM_sha256': sha(self.device.ram())}
        self.events.append(row)
        return row

    def handoff(self, state):
        row = self.event('handoff', state)
        if self.disc.pending:
            assert self.current() != WORLD, 'Completion requires a real loading-task switch'
            row['complete_disc_request'] = len(self.disc.requests)
            self.disc.tick(lambda a, data: c.memmove(self.device.pointer + a, data, len(data)),
                           lambda a, value: self.device.direct(a, 4, value))
            row['RAM_after_external_completion_sha256'] = sha(self.device.ram())

    def bios(self, state, target):
        row = {'target': target, 'context': self.current(), 'actual_body': False,
               'incoming': loading.cd.scheduler.cpu_dict(state)}
        if target == 0x303c:
            assert state.registers[9] <= SSP - 4096
            self.disc.start(state.registers[8], state.registers[9], state.registers[0])
        else:
            assert target == 0x3042
            self.disc.stop()
        row['return'] = loading.cd.scheduler.cpu_dict(state)
        self.calls.append(row)

    def observe_return(self, state):
        frames = self.frames[self.current()]
        if frames and state.registers[15] == frames[-1]['incoming']['registers'][15]:
            frame = frames.pop()
            frame['return'] = loading.cd.scheduler.cpu_dict(state)
            if frame['target'] == 0xdf6c:
                frame['created_context'] = hex(state.registers[0])

    def next_host_stage(self, state):
        """Controlled pose/button entries; source positioning selects the room.

        No scene/gate/actor records or task pool are changed by the host.
        These entries are explicit fixtures, not natural walking/input polling.
        """
        if self.gate['target'] != 312 or self.host_phase == 4:
            return False
        self.event('host_stage_return', state)
        if self.host_phase % 2 == 0:
            scene = self.device.read(0x49c18, 4)
            count, records = self.device.read(scene, 2), self.device.read(scene + 4, 4)
            stairs = next(records + index * 24 for index in range(count)
                          if self.device.read(records + index * 24, 2) & 0x8000)
            for source_offset, origin, coordinate in [(2, 0x49c6a, 0x49c50), (4, 0x49c72, 0x49c56)]:
                offset = self.device.read(stairs + source_offset, 2)
                if offset & 0x8000:
                    offset -= 65536
                self.device.direct(coordinate, 4, self.device.read(origin, 4) + offset * 64 + 32)
            state.registers[15] -= 4
            self.device.direct(state.registers[15], 4, STOP)
            self.device.direct(state.registers[15] + 4, 4, 0x49c4c)
            state.pc = 0x10520
        else:
            assert state.registers[0] & 65535 == 1, 'Source positioning must find the real stair room'
            room = self.device.read(0x49c78, 4)
            assert self.device.read(room, 2) & 0x8000
            scene = self.device.read(0x49c18, 4)
            assert self.device.read(scene + 12, 2) & 0x8000
            self.device.direct(0x49ba5, 1, 0x10)
            state.registers[15] -= 4
            self.device.direct(state.registers[15], 4, STOP)
            state.pc = 0x1a0f8
        state.usp = state.registers[15]
        self.host_phase += 1
        self.event('host_controlled_entry', state)
        return True

    def native(self, ram, initial, coverage):
        self.reset_run(ram, False)
        loading.cd.lifecycle.seed_cpu(self, initial)
        pending = {}
        steps = []
        for _ in range(2000000):
            pc = self.core.m68k_get_reg(None, 16)
            if pc == STOP:
                state = self.cpu()
                if self.next_host_stage(state):
                    loading.cd.lifecycle.seed_cpu(self, state)
                    continue
                break
            context = self.current()
            assert pc in self.rows, hex(pc)
            if pending.get(context) == pc:
                frame = {'target': pc, 'context': context, 'actual_body': True,
                         'incoming': loading.cd.scheduler.cpu_dict(self.cpu())}
                self.calls.append(frame)
                self.frames[context].append(frame)
                pending.pop(context)
            if pc in [0x303c, 0x3042]:
                state = self.cpu()
                self.bios(state, pc)
                if pc == 0x3042:
                    self.observe_return(state)
                opcode = self.device.read(pc, 2)
                self.device.direct(pc, 2, 0x4e75)
                self.core.m68k_execute(1)
                self.device.direct(pc, 2, opcode)
                continue
            row = self.rows[pc]
            if row['assembly'] == 'rts':
                self.observe_return(self.cpu())
            if (pc in self.generated or 0xf4d8 <= pc < 0xf712) and row['assembly'].startswith(('jsr ', 'bsr.')):
                operand = row['assembly'].split(' ', 1)[1]
                if operand.startswith('('):
                    target = self.core.m68k_get_reg(None, loader_gen.base.register(operand[1:-1]))
                else:
                    target = int(operand.split('$')[1].split('.')[0], 16)
                if target in self.provider_targets:
                    pending[context] = target
                elif target not in [0xdf60, 0xdf7a, 0xdfa6, 0x303c, 0x3042]:
                    raise AssertionError(('Unimplemented native source provider', hex(pc), hex(target)))
            if pc in [0xdf60, 0xdf7a]:
                self.event('yield' if pc == 0xdf60 else 'remove', self.cpu())
            steps.append(pc)
            coverage.add(pc)
            self.core.m68k_execute(1)
            if pc == 0xdf6a or (pc == 0xde5a and self.core.m68k_get_reg(None, 16) != 0xdf66):
                self.handoff(self.cpu())
        else:
            raise AssertionError(('Native entrance work bound', hex(pc)))
        if self.current() != WORLD or any(self.frames.values()) or self.disc.pending:
            save(self.output / 'native-open-frames.json', {'CPU': loading.cd.scheduler.cpu_dict(self.cpu()),
                 'context': hex(self.current()), 'frames': dict(self.frames), 'disc_pending': bool(self.disc.pending),
                 'calls': self.calls, 'events': self.events})
            raise AssertionError(str(self.output / 'native-open-frames.json'))
        return self.device.ram(), self.cpu(), {'steps': steps, 'calls': self.calls, 'events': self.events,
               'disc_requests': self.disc.requests, 'disc_completions': self.disc.completions,
               'disc_stops': self.disc.stops, 'device': self.device.stats()}

    def translated(self, ram, initial):
        self.reset_run(ram, True)
        state = CPU.from_buffer_copy(bytes(initial))

        def writer(_, address, value):
            try:
                self.device.write(address, value)
                if self.idle_pending and address == self.idle_pending.registers[15] - 4:
                    prospective = CPU.from_buffer_copy(bytes(self.idle_pending))
                    assert value == prospective.pc + 6
                    prospective.registers[15] -= 4
                    prospective.usp = prospective.registers[15]
                    prospective.pc = 0xdf60
                    self.event('yield', prospective)
                    self.idle_pending = None
                return 0
            except Exception as error:
                self.errors.append(repr(error))
                return 1

        w32 = loading.cd.world.W32(writer)
        bus = loading.cd.world.Bus(self.device.r8, self.device.r16, self.device.r32,
                                  self.device.w16, w32, loading.cd.world.CALL(), None, 0)

        def body(passed, cpu):
            pc = cpu.contents.pc
            if pc in self.owner:
                return self.functions[self.owner[pc]](passed, cpu, self.device.write8, callback, None, 1000000, 1)
            if pc in [0x1a77c, 0xe540, 0xe588, 0xe60a]:
                return self.rng(passed, cpu)
            if pc in [0xf368, 0x13f12, 0x13f7c, 0x13fea]:
                return self.navigation(passed, cpu)
            raise AssertionError(('Unimplemented C source provider', hex(pc)))

        def service(_, passed, cpu, target):
            try:
                if target in [0x303c, 0x3042]:
                    self.bios(cpu.contents, target)
                    return 0
                assert target in self.provider_targets, hex(target)
                context = self.current()
                frame = {'target': target, 'context': context, 'actual_body': True,
                         'incoming': loading.cd.scheduler.cpu_dict(cpu.contents)}
                self.calls.append(frame)
                self.frames[context].append(frame)
                status = body(passed, cpu)
                if not status:
                    assert self.frames[context][-1] is frame
                    self.observe_return(cpu.contents)
                return status
            except Exception as error:
                self.errors.append(repr(error))
                return 1

        callback = loading.cd.world_cpu.SERVICE(service)
        actor_callback = c.cast(callback, actor.actor.SERVICE)
        for _ in range(10000):
            pc = state.pc
            if pc == STOP:
                if self.next_host_stage(state):
                    continue
                break
            if pc in [0xdf60, 0xdf7a]:
                self.event('yield' if pc == 0xdf60 else 'remove', state)
                fn = self.yield_fn if pc == 0xdf60 else self.remove_fn
                status = fn(c.byref(bus), c.byref(state), 128)
                assert not status, ('Scheduler', status, self.errors)
                self.handoff(state)
                continue
            if pc in [0xf360, 0xf880, 0xf366, 0xf886]:
                yielding = pc in [0xf360, 0xf880]
                if yielding:
                    self.idle_pending = CPU.from_buffer_copy(bytes(state))
                status = self.idle_fn(c.byref(bus), c.byref(state), actor.prior.BODY(), None, 128)
                assert not status, ('Idle', status, self.errors)
                if yielding:
                    assert self.idle_pending is None
                    self.handoff(state)
                continue
            if pc in [0xf4d8, 0xf56e, 0xf70c]:
                status = self.actor_fn(c.byref(bus), c.byref(state), self.device.write8, actor_callback, None, 100000)
                assert status in [0, 6], ('Actor', status, self.errors)
                assert state.pc in [0xdf60, 0xdf7a]
                continue
            status = body(c.byref(bus), c.pointer(state))
            if status == 6:
                assert state.pc == 0xdf60
                continue
            assert not status, ('Source body', hex(pc), status, self.errors)
            self.observe_return(state)
            assert self.rows[state.pc]['assembly'] == 'rts', hex(state.pc)
            status = self.return_functions[self.owner[state.pc]](c.byref(bus), c.byref(state),
                     self.device.write8, callback, None, 1, 1)
            assert not status, ('Source RTS', status)
        else:
            raise AssertionError(('C entrance work bound', hex(state.pc), self.errors))
        assert self.current() == WORLD and not any(self.frames.values()) and not self.disc.pending
        return self.device.ram(), state, {'calls': self.calls, 'events': self.events,
               'disc_requests': self.disc.requests, 'disc_completions': self.disc.completions,
               'disc_stops': self.disc.stops, 'errors': self.errors, 'device': self.device.stats()}


def fixture(capture, info, gate):
    ram = bytearray(capture)
    put = lambda a, w, v: ram.__setitem__(slice(a, a + w), (v & ((1 << (8 * w)) - 1)).to_bytes(w, 'big'))
    for context in startup.CONTEXTS:
        put(context + 26, 4, 0 if context in RUNNABLE else 1)
    put(0xc0920, 4, WORLD)
    put(0x80, 4, 0xde08)
    put(0x88, 4, 0xdeb6)
    put(0x49c8c, 2, gate['tile'])
    direction = gate['directions'][0]
    record = bytes.fromhex(gate['record_hex'])
    key = record[[11, 13, 15, 17][direction]]
    left, right = [(6, 0x4e), (0x4a, 6), (0x52, 12), (12, 0x56)][direction]
    value = int.from_bytes(ram[0x49c4c + right:0x49c4c + right + 2], 'big')
    put(0x49c4c + left, 2, value + key * 64)
    state = CPU()
    state.registers[:] = info['CPU']['registers']
    state.registers[15] = WORLD + 0x3d0
    state.usp, state.ssp, state.sr, state.pc = state.registers[15], SSP, 0x71f, 0x19f2c
    for offset, width, value in [(0, 4, STOP), (4, 2, 0x1000 | gate['gate']), (6, 2, direction), (8, 2, 0)]:
        put(state.registers[15] + offset, width, value)
    return bytes(ram), state


def main():
    out = ROOT / 'verification/biwn-scheduled-entrance' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_interior_loading_cpu.c', 'biwn_transition_cpu.c', 'biwn_doorway_cpu.c',
             'biwn_actor_factory_cpu.c', 'biwn_resource_cpu.c', 'biwn_cd_cpu.c', 'biwn_actor_task.c',
             'biwn_actor_navigation.c', 'biwn_rng_cpu.c', 'biwn_signed_division.c', 'biwn_camera.c',
             'biwn_scheduler.c', 'biwn_task_loops.c']
    library = out / 'libscheduled-entrance.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror'] + [str(source / name) for name in names] + ['-o', str(library)]
    compiler = subprocess.run(command, capture_output=True, text=True,
                             env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(compiler.stdout + compiler.stderr)
    assert compiler.returncode == 0, compiler.stderr
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    generated = []
    for name in ['interior-loading-fullCPU-generation.json', 'transition-fullCPU-generation.json',
                 'doorway-fullCPU-generation.json', 'actor-factory-fullCPU-generation.json',
                 'resource-fullCPU-generation.json', 'cd-wrapper-fullCPU-generation.json']:
        generated += read(session / name)['instructions_decoded']
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    rows = {row['address']: row for row in generated}
    for lo, hi in actor.navigation.RANGES + actor.rng_cpu.RANGES + [(0xf4d8, 0xf712), (0xdfa6, 0xdfb2),
                   (0xdf60, 0xdf6c), (0xdf7a, 0xdf7c), (0xde08, 0xde5c), (0xdeb6, 0xdee2),
                   (0xf360, 0xf368), (0xf880, 0xf888)]:
        rows.update({row['address']: row for row in loader_gen.base.binary_tools.m68k_instructions(snapshot[lo:hi], lo)[0]})
    for address in [0x303c, 0x3042]:
        rows[address] = {'address': address, 'assembly': 'declared BIOS preserve-register RTS adapter'}
    runtime = Runtime(library, list(rows.values()), generated)
    runtime.output = out
    capture_dir = ROOT / 'verification/biwn-render-actors-runtime/20261013T190116.161377Z'
    capture = (capture_dir / 'startup-C-0.bin').read_bytes()
    info = read(capture_dir / 'startup-capture-0.json')
    assert sha(capture) == info['C_RAM_sha256']
    gates = read(ROOT / 'verification/biwn-startup-loaded-doorway-candidates.json')['candidates']
    results, coverage = [], set()
    try:
        for index, gate in enumerate(gates):
            save(out / 'status.json', {'status': 'running', 'case': index, 'gate': gate})
            ram, initial = fixture(capture, info, gate)
            runtime.gate = gate
            (out / f'case-{index}-before-RAM.bin').write_bytes(ram)
            left, expected, native = runtime.native(ram, initial, coverage)
            right, actual, rebuilt = runtime.translated(ram, initial)
            keys = ['calls', 'events', 'disc_requests', 'disc_completions', 'disc_stops']
            if left != right or bytes(expected) != bytes(actual) or any(native[key] != rebuilt[key] for key in keys):
                (out / 'original-final-RAM.bin').write_bytes(left)
                (out / 'C-final-RAM.bin').write_bytes(right)
                save(out / 'mismatch.json', {'case': index, 'gate': gate, 'CPU_original': loading.cd.scheduler.cpu_dict(expected),
                     'CPU_C': loading.cd.scheduler.cpu_dict(actual), 'native': native, 'C': rebuilt,
                     'RAM_diff': [hex(i) for i, (a, b) in enumerate(zip(left, right)) if a != b][:80]})
                raise AssertionError(str(out / 'mismatch.json'))
            assert runtime.device.read(0x49c60, 2) == 2
            assert runtime.device.read(0x49c64, 2) == (314 if gate['target'] == 312 else 17)
            if gate['target'] == 17:
                assert actual.registers[0] == 2
            creations = [call for call in rebuilt['calls'] if call['target'] == 0xdf6c]
            if len(creations) != (1 if gate['target'] == 312 else 0):
                (out / 'unexpected-creation-C-final-RAM.bin').write_bytes(right)
                save(out / 'unexpected-creation.json', {'case': index, 'gate': gate,
                     'creations': creations, 'native': native, 'C': rebuilt})
                raise AssertionError(str(out / 'unexpected-creation.json'))
            if creations:
                assert {int(call['created_context'], 16) for call in creations} == {0xc1528}
                context = int(creations[0]['created_context'], 16)
                assert runtime.device.read(context + 8, 4) == 0xedc4
            assert len([event for event in rebuilt['events'] if event['kind'] == 'remove']) == 2
            assert not rebuilt['device']['original_GPUExec1_calls'] and not rebuilt['device']['game_frames_executed']
            (out / f'case-{index}-C-final-RAM.bin').write_bytes(right)
            results.append({'case': index, 'gate': gate, 'CPU': loading.cd.scheduler.cpu_dict(actual),
                            'before_RAM_sha256': sha(ram), 'after_RAM_sha256': sha(right), 'native': native, 'C': rebuilt})
            save(out / 'fixtures.json', results)
        generated_addresses = {row['address'] for row in generated}
        groups = {}
        for name in ['interior-loading', 'transition', 'doorway', 'actor-factory', 'resource', 'cd-wrapper']:
            mapping = read(session / (name + '-fullCPU-generation.json'))
            addresses = {row['address'] for row in mapping['instructions_decoded']}
            groups[name] = [len(addresses & coverage), len(addresses)]
        save(out / 'coverage.json', {'generated_instruction_count': len(generated_addresses),
                   'exercised_generated_instructions': len(generated_addresses & coverage),
                   'source_group_instruction_coverage': groups, 'native_PC_coverage': sorted(coverage)})
        report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'scheduled_actual_gate_cleanup_actor_removal_loading_and_creation_native_C_match',
                  'directory': str(out), 'cases': len(results), 'source_interiors': [17, 312, 313, 314],
                  'disc_transfers': sum(len(row['C']['disc_requests']) for row in results),
                  'transferred_bytes': sum(sum(req['bytes'] for req in row['C']['disc_requests']) for row in results),
                  'task_removals': sum(sum(event['kind'] == 'remove' for event in row['C']['events']) for row in results),
                  'task_creations': sum(sum(call['target'] == 0xdf6c for call in row['C']['calls']) for row in results),
                  'source_stair_transitions_312_to_313_to_314': sum(row['gate']['target'] == 312 for row in results) * 2,
                  'native_CPU_steps': sum(len(row['native']['steps']) for row in results),
                  'source_sha256': {name: sha((source / name).read_bytes()) for name in names}, 'compiler': command,
                  'test_script_sha256': sha(Path(__file__).read_bytes()), 'source_group_instruction_coverage': groups,
                  'full_CPU_RAM_privateframes_helper_yield_removal_disc_events_match': True,
                  'source_boundary_transition_and_scheduled_loading_verified_for_declared_fixtures': True,
                  'original_CPU_or_GPU_execution_on_C_side': False, 'new_published_components': 0,
                  'whole_game_complete': False, 'playable': False,
                  'limits': ['Host directly enters19F2C on captured world context with actual loaded gate/tile records and controlled player position/tile; not natural input/walking reachability.',
                             'Five runnable contexts/world,two old actor tasks,two idle; sixteen others including renderer blocked. No manual spare contexts. Actual cleanup kills actors,TRAP2 removes them,source DF6C creates new actors using freed contexts.',
                             'BIOS303C/3042 preserve-register RTS adapters; actual normalized disc bytes complete externally after real scheduler handoff. Supplied SSP1FF000 reserve/assisted startup,source code/free lists remain fixtures.',
                             'Four17cases stop at boundary return. Two312cases retain device/RAM, host positions player inside actual stair rectangles, source10520 selects them, supplied buttonbit4 drives actual1A0F8 transitions312->313->314. No gate/scene/actor records or freepool are patched. Source table gives IDs4/5/6/7 no tasks. Interior314 ID9 requests EDC4 and reuses one of the two contexts actually removed by the first transition; one free context remains.',
                             'Stops before new indoor actor behavior/rendering/world/input polling. Host entries/pose/button are controlled fixtures, not natural walking or uninterrupted world-loop control. Factory generated branches/static137E0/empty-poolILLEGAL outside exercised paths remain unverified; fullgame/audio/boot/globalGPU/scanout/hardware accuracy remain incomplete.',
                             'Coordinator authored fixed blocks, no new local-model authorship/weights/training/default changes.']}
        save(out / 'report.json', report)
        save(out / 'status.json', {'status': 'terminal_pass'})
        save(ROOT / 'verification/biwn-scheduled-entrance-checks.json', report)
        print(json.dumps(report))
    except Exception as error:
        save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error), 'errors': runtime.errors})
        raise
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
