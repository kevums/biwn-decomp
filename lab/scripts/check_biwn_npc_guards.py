"""Host error contracts of fixed NPC code; guards do not add normal coverage."""
import ctypes as c
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_doorway_cpu as prior

ROOT, queue = prior.ROOT, prior.queue
queue.ENTRIES = {0xdfa6, 0x101e0}
queue.SCRIPTS = set()
queue.RETURNS = set()


class Runtime(prior.Runtime):
    def __init__(self, library, rows):
        super().__init__(library, rows)
        self.fn = self.lib.biwn_npc_cpu_body
        self.call = self.lib.biwn_npc_cpu_call
        for fn in [self.fn, self.call]:
            fn.argtypes = [c.POINTER(queue.world.Bus), c.POINTER(queue.CPU), queue.cd.dispatch.W8,
                           queue.cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int


def main():
    report = queue.read(ROOT / 'verification/biwn-scheduled-npc-checks.json')
    directory = Path(report['directory'])
    session = Path(queue.read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = queue.read(session / 'npc-fullCPU-generation.json')
    runtime = Runtime(directory / 'libscheduled-npc.dylib', mapping['instructions_decoded'])
    ram = bytearray((directory / 'case-0-before-RAM.bin').read_bytes())
    put = lambda a, w, v: ram.__setitem__(slice(a, a + w), v.to_bytes(w, 'big'))
    put(queue.SP, 4, queue.STOP)
    put(0xc0920, 4, 0xc1528)
    put(0xc1528 + 30, 4, 4)
    registers = [0] * 15 + [queue.SP]
    registers[10] = 0x49d6c + 4 * 206
    case = {'id': 0, 'entry': 0xedc4, 'registers': registers, 'SR': 0,
            'usp': queue.SP, 'ssp': 0x1ff000, 'body': True, 'render': False,
            'outer_RTS': 0, 'read_queues': []}
    guards = []
    try:
        for options in [{'missing': i} for i in range(6)] + [{'null_bus': True}, {'null_cpu': True},
                      {'null_service': True}, {'budget': 0}, {'stop_flag': 2}, {'bad_pc': True}, {'budget': 1}]:
            _, _, result = runtime.translated(bytes(ram), case, **options)
            expected = 7 if options.get('bad_pc') else 4 if options.get('budget') == 1 else 1
            assert result['status'] == expected and result['CPU_unchanged'], (options, result)
            guards.append({'options': options, 'status': result['status']})
        for fail in [('read', 2), ('read', 4), ('write', 4)]:
            _, _, result = runtime.translated(bytes(ram), case, fail=fail)
            assert result['status'] in [2, 3] and result['CPU_unchanged'], (fail, result)
            guards.append({'bus_failure': fail, 'status': result['status']})
        for entry, fail in [(0x14076, ('read', 1)), (0xee0e, ('write', 2))]:
            _, _, result = runtime.translated(bytes(ram), {**case, 'entry': entry}, fail=fail)
            assert result['status'] == 2 and result['CPU_unchanged'], (entry, result)
            guards.append({'internal_guard_entry': hex(entry), 'failure': fail, 'status': result['status']})
        for target in [0xdfa6, 0x101e0]:
            _, _, result = runtime.translated(bytes(ram), case, fail=('helper', target))
            assert result['status'] == 3 and result['CPU_unchanged'], (target, result)
            guards.append({'helper_failure': hex(target), 'status': result['status']})
        corrupt = {**case, 'read_queues': [{'address': queue.SP - 24, 'width': 4, 'values': [0]}]}
        _, _, result = runtime.translated(bytes(ram), corrupt)
        assert result['status'] == 5 and result['CPU_unchanged'], result
        guards.append({'corrupt_getter_return': True, 'status': result['status']})
        record = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'NPC_host_guards_pass',
                  'guards': guards, 'host_guards': len(guards), 'source_sha256': mapping['source_sha256'],
                  'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'normal_source_instruction_coverage_changed': False,
                  'limits': 'Callback/budget/argument/internal guard entries are host contracts, not normal source coverage or exception emulation. Partial RAM effects retained, input CPU unchanged.'}
        (ROOT / 'verification/biwn-npc-guard-checks.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps({'host_guards': len(guards), 'normal_coverage_changed': False}))
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
