"""Host error semantics of the new fixed factory, separate from normal proof."""
import ctypes as c
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_doorway_cpu as prior

ROOT, queue = prior.ROOT, prior.queue
queue.ENTRIES = set()
queue.SCRIPTS = {0x134dc}
queue.RETURNS = set()


class Runtime(prior.Runtime):
    def __init__(self, library, rows):
        super().__init__(library, rows)
        self.fn = self.lib.biwn_actor_factory_cpu_body
        self.call = self.lib.biwn_actor_factory_cpu_call
        for fn in [self.fn, self.call]:
            fn.argtypes = [c.POINTER(queue.world.Bus), c.POINTER(queue.CPU), queue.cd.dispatch.W8,
                           queue.cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int


def main():
    report = queue.read(ROOT / 'verification/biwn-scheduled-entrance-checks.json')
    directory = Path(report['directory'])
    session = Path(queue.read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = queue.read(session / 'actor-factory-fullCPU-generation.json')
    runtime = Runtime(directory / 'libscheduled-entrance.dylib', mapping['instructions_decoded'])
    ram = bytearray((directory / 'case-0-before-RAM.bin').read_bytes())
    put = lambda a, w, v: ram.__setitem__(slice(a, a + w), v.to_bytes(w, 'big'))
    put(queue.SP, 4, queue.STOP)
    for offset, width, value in [(4, 2, 9), (6, 4, 0), (10, 2, 0), (12, 4, 0), (16, 2, 0)]:
        put(queue.SP + offset, width, value)
    case = {'id': 0, 'entry': 0x13ae0, 'registers': [0] * 15 + [queue.SP], 'SR': 0,
            'usp': queue.SP, 'ssp': 0x1ff000, 'body': False, 'render': False,
            'outer_RTS': 0x13b58, 'read_queues': []}
    guards = []
    try:
        for options in [{'missing': i} for i in range(6)] + [{'null_bus': True}, {'null_cpu': True},
                      {'null_service': True}, {'budget': 0}, {'stop_flag': 2}, {'bad_pc': True}, {'budget': 1}]:
            _, _, result = runtime.translated(bytes(ram), case, **options)
            expected = 7 if options.get('bad_pc') else 4 if options.get('budget') == 1 else 1
            assert result['status'] == expected and result['CPU_unchanged'], (options, result)
            guards.append({'options': options, 'status': result['status']})
        for fail in [('read', 1), ('read', 2), ('read', 4), ('write', 4)]:
            _, _, result = runtime.translated(bytes(ram), case, fail=fail)
            assert result['status'] == 2 and result['CPU_unchanged'], (fail, result)
            guards.append({'bus_failure': fail, 'status': result['status']})
        internal = {**case, 'entry': 0x134dc}
        _, _, result = runtime.translated(bytes(ram), internal, fail=('write', 2))
        assert result['status'] == 2 and result['CPU_unchanged']
        guards.append({'internal_entry_write16_failure': True, 'status': result['status']})
        _, _, result = runtime.translated(bytes(ram), case, fail=('helper', 0x134dc))
        assert result['status'] == 3 and result['CPU_unchanged']
        guards.append({'helper_failure': '0x134dc', 'status': result['status']})
        corrupt = {**case, 'read_queues': [{'address': queue.SP - 36, 'width': 4, 'values': [0]}]}
        _, _, result = runtime.translated(bytes(ram), corrupt)
        assert result['status'] == 5 and result['CPU_unchanged']
        guards.append({'corrupt_private_return': True, 'status': result['status']})
        empty = {**case, 'entry': 0xde5c}
        put(0xc0924, 4, 0)
        after, _, result = runtime.translated(bytes(ram), empty)
        assert result['status'] == 7 and result['CPU_unchanged'] and after == bytes(ram)
        guards.append({'empty_free_pool_unsupported_source_ILLEGAL': True, 'status': result['status']})
        record = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'actor_factory_host_guards_pass',
                  'guards': guards, 'host_guards': len(guards), 'source_sha256': mapping['source_sha256'],
                  'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'normal_source_instruction_coverage_changed': False,
                  'limits': 'Host error/budget/callback/unsupported source exception contracts only; guard internal entries excluded from normal coverage. Helper in bad-return probe is an explicit ABI script. Earlier RAM effects retained; input CPU unchanged. Empty-pool original ILLEGAL is not emulated.'}
        (ROOT / 'verification/biwn-actor-factory-guard-checks.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps({'host_guards': len(guards), 'source_ILLEGAL_emulated': False}))
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
