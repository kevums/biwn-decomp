"""Full CPU scene/clear/rotation versus native CPU and independent Unicorn.

The existing pinned blitter rasterizes actual MMIO submissions on each side.
Eight lower-level helpers remain declared ABI adversaries in this standalone
proof. Busy-read inputs are explicit device fixtures, never a timing claim.
"""
import argparse
import ctypes as c
import hashlib
import importlib.util
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_render_scene as logical
import check_biwn_cd_cpu as cd
import check_biwn_actor_lifecycle_runtime as lifecycle

ROOT = cd.ROOT
# A private harness instance preserves the accepted queue test's globals.
spec = importlib.util.spec_from_file_location('scene_draw_queue_harness', ROOT / 'scripts/check_biwn_render_queue_cpu.py')
queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue)
queue.ENTRIES = {0xe03a, 0x17f14}
queue.RETURNS = {0xe096, 0x17f66}
queue.SCRIPTS = set(logical.HELPERS)
CPU = cd.CPU
SP = queue.SP
STOP = queue.STOP
save = cd.save
read = lambda p: json.loads(p.read_text())

class Runtime(queue.Runtime):
    def __init__(self, library, rows):
        self.native_oracle = cd.scheduler.Native()
        self.device = self.native_oracle.device
        self.core = self.native_oracle.lib
        self.prefix = self.native_oracle.prefix
        self.lib = c.CDLL(str(library))
        self.rows = {r['address']: r for r in rows}
        self.fn = self.lib.biwn_scene_draw_cpu_body
        self.call = self.lib.biwn_scene_draw_cpu_call
        for fn in [self.fn, self.call]:
            fn.argtypes = [c.POINTER(cd.world.Bus), c.POINTER(CPU), cd.dispatch.W8, cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int
    def reset(self, ram, case, mode):
        super().reset(ram, case, mode)
        self.draws = 0
        for address in range(0xf02200, 0xf022a0, 4):
            if address != 0xf02238:
                self.device.write(address, 0)
    def read(self, address, width):
        if address == 0xf02238:
            values = self.queues.get((address, width))
            value = values.pop(0) if values else self.device.read(address, width)
            self.trace.append(['r', address, width, value])
            return value
        return super().read(address, width)
    def scripted(self, state, target):
        super().scripted(state, target)
        if target == 0x170a0:
            counts = self.case['draw_counts']
            self.device.direct(0x49b88, 4, counts[min(self.draws, len(counts)-1)])
            self.draws += 1
    def native(self, ram, case, coverage):
        self.reset(ram, case, 0)
        lifecycle.seed_cpu(self, queue.make_cpu(case))
        steps, stack, pending = [], [], None
        for target in queue.SCRIPTS:
            self.device.direct(target, 2, 0x4e75)
        try:
            for _ in range(10000):
                pc = self.core.m68k_get_reg(None, 16)
                if pc == STOP or (case['body'] and pc == case['outer_RTS']):
                    break
                if pc in queue.SCRIPTS:
                    state = self.cpu()
                    self.scripted(state, pc)
                    for reg in [0, 1, 8, 9]:
                        self.core.m68k_set_reg(reg, state.registers[reg])
                    self.core.m68k_set_reg(17, state.sr)
                    pending = None
                else:
                    assert pc in self.rows, hex(pc)
                    if pending == pc:
                        row = {'target': pc, 'actual_body': True, 'incoming': cd.scheduler.cpu_dict(self.cpu())}
                        self.calls.append(row)
                        stack.append(row)
                        pending = None
                    if pc in queue.RETURNS and stack:
                        stack.pop()['return'] = cd.scheduler.cpu_dict(self.cpu())
                    source = self.rows[pc]
                    if source['assembly'].startswith('jsr '):
                        target = int(source['assembly'].split('$')[1].split('.')[0], 16)
                        pending = target if target in queue.ENTRIES else None
                    if pc in [0x17e18, 0x17e34, 0x17e6e, 0x17ef8]:
                        self.inject(0x49c60, 2)
                    if pc in [0x17e5c, 0x17ed6]:
                        self.inject(0x10a684, 4)
                    steps.append(pc)
                    coverage.add(pc)
                self.core.m68k_execute(1)
                if pc == 0xe03e:
                    # The controlled MMIO return is supplied before the next
                    # instruction, exactly as the other two CPU bus readers.
                    values = self.queues.get((0xf02238, 4))
                    if values:
                        self.core.m68k_set_reg(0, values.pop(0))
            else:
                raise AssertionError('native scene draw did not return')
        finally:
            for target in queue.SCRIPTS:
                self.device.direct(target, 2, int.from_bytes(ram[target:target+2], 'big'))
        assert not stack
        return self.device.ram(), self.cpu(), {'steps': steps, 'calls': self.calls, 'device': self.stats()}

def cases():
    rng = random.Random(0x17e0e102)
    vectors = []
    for old in logical.cases():
        index = len(vectors)
        registers = old['incoming'] + [SP]
        supervisor = index % 2
        case = dict(id=index, entry=old['entry'], registers=registers,
                    SR=(0x2000 if supervisor else 0) | ((index % 8) << 8) | rng.randrange(32),
                    usp=0x170000 if supervisor else SP, ssp=SP if supervisor else 0x1d0000,
                    body=index % 3 == 1, render=False, outer_RTS={0xe03a:0xe096, 0x17e0e:0x17f12, 0x17f14:0x17f66}[old['entry']],
                    initial=old['initial'], params=old['params'], draw_counts=old['draw_counts'],
                    read_queues=old['read_queues'] + [{'address': 0xf02238, 'width': 4, 'values': old['blitter_status']}])
        # Real clear commands must target bounded framebuffers. Logical-only
        # predecessor fixtures allowed arbitrary pointer words.
        for row in case['initial']:
            if row[0] in [0xbd83c, 0xbd840, 0xbd844]:
                row[2] = {0xbd83c:0x130000, 0xbd840:0x145000, 0xbd844:0x160000}[row[0]]
        if case['entry'] == 0xe03a:
            case['params'] = [0x130000 + (index % 3) * 0x15000, old['params'][1]]
        vectors.append(case)
    return vectors

def fixture(snapshot, case):
    ram = bytearray(snapshot)
    for address, width, value in case['initial']:
        ram[address:address+width] = value.to_bytes(width, 'big')
    for i, value in enumerate([STOP] + case['params']):
        ram[SP+i*4:SP+i*4+4] = value.to_bytes(4, 'big')
    return bytes(ram)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    opts = parser.parse_args()
    out = ROOT / 'verification/biwn-scene-draw-cpu' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    library = out / 'libscene-draw-cpu.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(source/'biwn_scene_draw_cpu.c'), '-o', str(library)]
    compiled = subprocess.run(command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(compiled.stdout + compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = read(session/'scene-draw-fullCPU-generation.json')
    snapshot = (ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    vectors = cases()
    if opts.limit:
        indices = [0,1,127,128,129,255,256,257,258,259,260,261,262,267,269,270,300]
        vectors = [vectors[i] for i in indices[:opts.limit]]
    runtime, rows, coverage = Runtime(library, mapping['instructions_decoded']), [], set()
    try:
        for i, case in enumerate(vectors):
            save(out/'status.json', {'status':'running','case':i})
            ram = fixture(snapshot, case)
            left, expected, original = runtime.native(ram, case, coverage)
            observed, observer, independent = runtime.unicorn(ram, case, coverage)
            right, actual, rebuilt = runtime.translated(ram, case)
            if rebuilt['status'] or bytes(expected) != bytes(actual) or bytes(observer) != bytes(actual) or left != right or observed != right or independent['trace'] != rebuilt['trace'] or original['calls'] != rebuilt['calls']:
                save(out/'mismatch.json', dict(case=case, CPU_original=cd.scheduler.cpu_dict(expected), CPU_Unicorn=cd.scheduler.cpu_dict(observer), CPU_C=cd.scheduler.cpu_dict(actual),
                     RAM_differences=[hex(j) for j,(a,b) in enumerate(zip(left,right)) if a != b][:30], Unicorn_RAM_differences=[hex(j) for j,(a,b) in enumerate(zip(observed,right)) if a != b][:30], original=original, Unicorn=independent, rebuilt=rebuilt))
                raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls'] and not rebuilt['device']['game_frames_executed'] and not rebuilt['device']['device_error']
            rows.append(dict(case=case, CPU=cd.scheduler.cpu_dict(actual), original=original, rebuilt=rebuilt, full_CPU_RAM_privateframes_orderedbus_match=True))
        save(out/'fixtures.json', rows)
        if opts.limit:
            save(out/'status.json', {'status':'terminal_preflight','cases':len(rows),'coverage':[len(coverage),102]})
            print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(coverage),102]}))
            return
        missing = [r for r in mapping['instructions_decoded'] if r['address'] not in coverage]
        save(out/'coverage.json', {'instructions':mapping['instructions_decoded'],'uncovered':missing})
        assert not missing, [hex(r['address']) for r in missing]
        guards = []
        case = vectors[0]
        ram = fixture(snapshot, case)
        for kw in [{'missing':i} for i in range(6)] + [{'null_bus':True},{'null_cpu':True},{'null_service':True},{'budget':0},{'stop_flag':2}]:
            _,_,result = runtime.translated(ram, case, **kw)
            assert result['status'] == 1 and result['CPU_unchanged'] and not result['trace']
            guards.append(kw)
        for kw, status in [({'bad_pc':True},7),({'budget':1},4)]:
            _,_,result = runtime.translated(ram, case, **kw)
            assert result['status'] == status and result['CPU_unchanged']
            guards.append(kw)
        for failure in [('read',2),('read',4),('write',4)]:
            probe = next(r['case'] for r in rows if any(t[0] == ('r' if failure[0]=='read' else 'w') and t[2] == failure[1] for t in r['rebuilt']['trace']))
            _,_,result = runtime.translated(fixture(snapshot,probe), probe, fail=failure)
            assert result['status'] in [2,3] and result['CPU_unchanged']
            guards.append({'failure':failure})
        probe = vectors[257]
        _,_,result = runtime.translated(fixture(snapshot,probe), probe, fail=('helper',0xe03a))
        assert result['status'] == 3 and result['CPU_unchanged']
        guards.append({'helper_failure':0xe03a})
        report = dict(recorded_at=datetime.now(timezone.utc).isoformat(), status='scene_draw_clear_rotation_fullCPU_dual_CPU_native_blitter_match', directory=str(out),
                      CPU_cases=len(rows), source_instruction_coverage=[102,102], host_guards=len(guards), source_sha256=mapping['source_sha256'],
                      stage_sha256=mapping['stage_sha256'], generator_sha256=mapping['generator_sha256'], scripted_helpers=[hex(a) for a in sorted(queue.SCRIPTS)],
                      matched=['All CPU registers/PC/SR/USP/SSP, complete 2MB RAM/private frames, ordered Unicorn/C CPU bus, nested real clear/rotation helper states and ABI-adversary helper states.',
                               'Actual pinned blitter rasterizes E03A MMIO commands on native and reconstructed sides; modes0/1/2/3/other, mode rereads, signed region words, paired-list sentinels and both display-buffer triple rotations.'],
                      limits=['Eight lower helper bodies are explicit ABI adversaries. Display-list builder and geometry/scene/GPU helpers not reconstructed by this proof; no complete viewport, OP scanout, audio or full game.',
                              'Standalone synthetic bounded scene inputs, controlled busy MMIO and completion RAM rereads, shared synchronous emulated blitter. No independent blitter implementation, physical frame rate, scheduler or live game scene linkage claim.'], compiler=command)
        save(out/'guards.json', guards)
        save(out/'report.json', report)
        save(out/'status.json', {'status':'terminal_pass'})
        save(ROOT/'verification/biwn-scene-draw-cpu-checks.json', report)
        print(json.dumps(report))
    except Exception as error:
        save(out/'status.json', {'status':'terminal_failed','error':repr(error)})
        raise
    finally:
        runtime.close()

if __name__ == '__main__':
    main()
