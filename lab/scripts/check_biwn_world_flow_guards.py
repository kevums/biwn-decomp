"""Error contracts of the source world-flow candidate, outside normal coverage."""
import ctypes as c
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_doorway_cpu as prior

ROOT, queue = prior.ROOT, prior.queue
queue.ENTRIES = set()
queue.SCRIPTS = {0xe4c0}
queue.RETURNS = set()


class Runtime(prior.Runtime):
    def __init__(self, library, rows):
        super().__init__(library, rows)
        self.fn = self.lib.biwn_world_flow_cpu_body
        self.call = self.lib.biwn_world_flow_cpu_call
        for fn in [self.fn, self.call]:
            fn.argtypes = [c.POINTER(queue.world.Bus), c.POINTER(queue.CPU), queue.cd.dispatch.W8,
                queue.cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int


def main():
    report = queue.read(ROOT/'verification/biwn-scheduled-world-NPC-render-checks.json')
    directory = Path(report['directory'])
    session = Path(queue.read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = queue.read(session/'world-flow-fullCPU-generation.json')
    runtime = Runtime(directory/'libscheduled-world-NPC-render.dylib', mapping['instructions_decoded'])
    ram = bytearray((directory/'case-0-before-RAM.bin').read_bytes())
    ram[queue.SP:queue.SP+4] = queue.STOP.to_bytes(4,'big')
    case = dict(id=0, entry=0x1a188, registers=[0]*15+[queue.SP], SR=0,
        usp=queue.SP, ssp=0x1ff000, body=True, render=False, outer_RTS=0x1a542, read_queues=[])
    guards=[]
    try:
        for options in [{'missing':i} for i in range(6)] + [dict(null_bus=True),dict(null_cpu=True),
                dict(null_service=True),dict(budget=0),dict(stop_flag=2),dict(bad_pc=True),dict(budget=1)]:
            _,_,result=runtime.translated(bytes(ram),case,**options)
            expected=7 if options.get('bad_pc') else 4 if options.get('budget')==1 else 1
            assert result['status']==expected and result['CPU_unchanged'],(options,result)
            guards.append(dict(options=options,status=result['status']))
        for entry,fail in [(0x1a196,('read',1)),(0x1a20a,('read',2)),(0x1a188,('read',4)),
                (0x1a21c,('write',2)),(0x1a188,('write',4))]:
            _,_,result=runtime.translated(bytes(ram),{**case,'entry':entry},fail=fail)
            assert result['status']==2 and result['CPU_unchanged'],(entry,fail,result)
            guards.append(dict(guard_entry=hex(entry),failure=fail,status=result['status']))
        for entry,target in [(0x1a188,0xe4c0),(0x1a544,0x1a188)]:
            _,_,result=runtime.translated(bytes(ram),{**case,'entry':entry},fail=('helper',target))
            assert result['status']==3 and result['CPU_unchanged'],(entry,target,result)
            guards.append(dict(helper_failure=hex(target),status=result['status']))
        corrupt={**case,'read_queues':[dict(address=queue.SP-60,width=4,values=[0])]}
        _,_,result=runtime.translated(bytes(ram),corrupt)
        assert result['status']==5 and result['CPU_unchanged'],result
        guards.append(dict(corrupt_poll_return=True,status=result['status']))
        record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='world_flow_host_guards_pass',
            guards=guards,host_guards=len(guards),source_sha256=mapping['source_sha256'],
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            normal_source_instruction_coverage_changed=False,
            limits='Internal error entries are host-contract tests, not normal coverage or original exception handling. Input CPU unchanged; prior partial RAM effects retained.')
        (ROOT/'verification/biwn-world-flow-guard-checks.json').write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(dict(host_guards=len(guards),normal_coverage_changed=False)))
    finally:
        runtime.close()


if __name__=='__main__':
    main()
