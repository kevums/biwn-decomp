"""Guarded full caller with actual EB04/EAC4 animation CPU bodies.

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
import check_biwn_world_movement_pipeline as gpu
import check_biwn_game_controls as controls
import check_biwn_boundary_handlers as boundary
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
    all_inputs = [row['parameters'] for row in saved[::2]]
    assert len(all_inputs) == 2315
    inputs = [case for state in range(13) for case in [x for x in all_inputs if x['state']==state][:2]]
    assert len(inputs)==26
    target_proof_path=V/'biwn-targeting-cpu-checks.json'
    target_proof=read(target_proof_path)
    assert target_proof['CPU_cases']==1026 and target_proof['CPU_instruction_coverage']==[183,183]
    for name,digest in target_proof['source_sha256'].items():assert sha(ROOT/'projects/black-ice-white-noise/restoration'/name)==digest,name
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
    linked_fixtures=controls.cases(snapshot)
    seed=next(x for x in linked_fixtures if x['kind']=='equipment_slot'and next(v for a,w,v in reversed(x['initial'])if a==0x49d5a)==1)
    inputs=[dict(seed,resource_scenario='resident_remove'),dict(seed,resource_scenario='resident_add')]
    for kind in ['resource_evict','resource_cache_miss','resource_pending','resource_load_shared','heap_merge_previous','heap_merge_next','heap_merge_both']:
        inputs.append(dict(next(x for x in linked_fixtures if x['kind']==kind),resource_scenario=kind))
    assert len(inputs)==9

    patch = b'\x4e\xb9' + entry.to_bytes(4, 'big')
    assert snapshot[0x1a266:0x1a26c] == b'\x4e\xb9\x00\x01\x91\xf4'
    world_helpers = [0xe4c0, 0x1b786, 0x19f2c, 0x19fda, 0xf0fa, 0xeb04, 0x20820]
    stubs = sorted(set([a for a in dispatch.HELPERS if a not in [0xe588,0xeb04,0x1af04,0x1b002,0x152a2,0x1545c]] + [a for a in world_helpers if a not in [0xeb04,0xf0fa,0x20820,0x19f2c,0x19fda]]))
    backend_widths={0x1b044:[4]*5,0xdf8c:[4],0xdf9c:[4]}
    stubs=sorted(set(stubs+list(backend_widths)))
    stubs=sorted(set(stubs+boundary.HELPERS))
    boundary_widths={0x1039c:[4,2],0x10430:[4,2,2],0x102c4:[4],0x1028e:[4],0x10652:[4,2],0x1aa40:[2],0x20f78:[2]}
    out = V / 'native-input-real-combined-caller-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V / 'native-input-real-combined-caller-v1-current.json'
    state = dict(status='running_full_original_world_caller_guarded_input', directory=str(out), pid=os.getpid(),
                 completed=0, planned_cases=len(inputs)*3, new_predictions=0, optimizer_updates=0,
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
    device=gpu.Device()

    def execute(case, task, initial_sp, sr, changed, index):
        script = Script(case)
        script.put(0xc0920, 4, task)
        script.memory[task:task+64] = b'\xa5'*64
        device.seed(bytes(script.memory),0)
        assert device.ram()==bytes(script.memory), 'Device seed changed fixture RAM'
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
        actual_animation = []
        actual_camera=[]
        actual_targeting=[]
        actual_resources=[]
        actual_boundaries=[]
        nested_boundary_calls=[]
        resource_backend_calls=[]
        resource_waits=0
        GPU_coherent_blocks=[]

        def private(address, width):
            return task + 64 <= address and address + width <= task + 1024

        def code(engine, pc, width, user):
            nonlocal minimum, route, instructions, resource_waits
            minimum = min(minimum, engine.reg_read(UC_M68K_REG_A7))
            instructions += 1
            assert minimum >= task+64, (hex(minimum), hex(task))
            if start <= pc < 0x1a544:
                covered.add(pc)
            if pc in [native_body, original_body]:
                assert route is None
                route = 'native' if pc == native_body else 'original'
            if pc in [0xeb04,0xeac4]:
                a7=engine.reg_read(UC_M68K_REG_A7)
                args=[int.from_bytes(engine.mem_read(a7+4+j*4,4),'big')for j in range(1 if pc==0xeb04 else 4)]
                actual_animation.append([pc,args])
                script.trace.append(['actual_animation',pc,args])
                if pc==0xeb04:
                    caller=int.from_bytes(engine.mem_read(a7,4),'big')
                    helper_contracts.append([pc,args,None if start<=caller<0x1a544 else engine.reg_read(UC_M68K_REG_D0)])
            if pc == 0xe220:
                a7 = engine.reg_read(UC_M68K_REG_A7)
                args = [int.from_bytes(engine.mem_read(a7+4+i*4, 4), 'big') for i in range(5)]
                matrix_args.append(args)
                script.trace.append(['actual_GPU_submit',pc,args])
            if pc==0xf0fa:
                args=[engine.reg_read(UC_M68K_REG_D2)&65535,engine.reg_read(UC_M68K_REG_D3)&65535]
                actual_camera.append(args)
                helper_contracts.append([pc,args,None])
                script.trace.append(['actual_camera',pc,args])
            if pc==0x20820:
                incoming=[engine.reg_read(reg)for reg in dispatch.world.REGS]
                incoming.append(engine.reg_read(UC_M68K_REG_A7))
                actual_targeting.append(incoming)
                script.trace.append(['actual_targeting',pc])
            if pc in [0x1af04,0x1b002,0x152a2,0x1545c,0x15200]:
                a7=engine.reg_read(UC_M68K_REG_A7)
                width=2 if pc in [0x1af04,0x1b002]else 4
                args=[]if pc==0x15200 else[int.from_bytes(engine.mem_read(a7+4,width),'big')]
                actual_resources.append([pc,args])
                script.trace.append(['actual_resource',pc,args])
                helper_contracts.append([pc,args,engine.reg_read(UC_M68K_REG_D0)])
            if pc in backend_widths:
                a7=engine.reg_read(UC_M68K_REG_A7);args=[];offset=4
                for w in backend_widths[pc]:
                    args.append(int.from_bytes(engine.mem_read(a7+offset,w),'big'));offset+=w
                resource_backend_calls.append([pc,args])
                script.trace.append(['resource_backend_script',pc,args])
                effects=[]
                if pc==0x1b044:
                    _,_,handle,_,completion=args
                    data=int.from_bytes(device.ram()[handle:handle+4],'big')
                    effects.append((data+8,4,0x80))
                    if completion:effects.append((completion,2,1))
                    if case.get('resource_shared_during_load'):effects.append((completion-2,2,2))
                elif pc==0xdf8c:
                    resource_waits+=1
                    if resource_waits>=case.get('resource_ready_after',2):effects.append((0x15b53c,2,1))
                for a,w,v in effects:
                    script.put(a,w,v);device.direct(a,w,v);engine.mem_write(a,v.to_bytes(w,'big'))
                engine.reg_write(UC_M68K_REG_D0,0)
                return
            if pc in [0x19f2c,0x19fda]:
                a7=engine.reg_read(UC_M68K_REG_A7)
                widths=[2,2,2]if pc==0x19f2c else[4,2]
                args=[];offset=4
                for w in widths:
                    args.append(int.from_bytes(engine.mem_read(a7+offset,w),'big'));offset+=w
                incoming=[engine.reg_read(reg)for reg in dispatch.world.REGS]
                actual_boundaries.append(dict(target=pc,args=args,incoming=incoming))
                script.trace.append(['actual_boundary',pc,args])
                helper_contracts.append([pc,args,None])
            if pc in stubs or pc == 0xe588:
                a7 = engine.reg_read(UC_M68K_REG_A7)
                caller = int.from_bytes(engine.mem_read(a7, 4), 'big')
                from_world = start <= caller < 0x1a544
                if 0x19f2c<=caller<0x1a0f8 and pc in boundary.HELPERS:
                    args=[];offset=4
                    for w in boundary_widths.get(pc,[]):
                        args.append(int.from_bytes(engine.mem_read(a7+offset,w),'big'));offset+=w
                    nested_boundary_calls.append([pc,args])
                    script.trace.append(['boundary_script',pc,args])
                    engine.reg_write(UC_M68K_REG_D0,case['boundary_helper_return'])
                    return


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
                    if 0xf0fa<=caller<0xf35e or 0x13440<=caller<0x134dc or 0xe540<=caller<0xe588 or 0x20820<=caller<0x20a9c:
                        script.trace.append(['camera_math',pc,args])
                        return
                    assert route == 'original'
                    script.trace.append(['call', pc, args])
                    return
                helper_contracts.append([pc, args, None if from_world else engine.reg_read(UC_M68K_REG_D0)])
                script.changed = []
                result = script.world_call(pc, args) if from_world else script.call(pc, args)
                for a, w, v in script.changed:
                    device.direct(a,w,v)
                    engine.mem_write(a, v.to_bytes(w, 'big'))
                engine.reg_write(UC_M68K_REG_D0, result)
                if not from_world and route == 'native':
                    for reg in [UC_M68K_REG_D1, UC_M68K_REG_A0, UC_M68K_REG_A1]:
                        engine.reg_write(reg, 0x13579bdf)
                return
            assert (start <= pc < 0x1a544 or 0x1b718 <= pc < 0x1b780
                or 0xe220 <= pc < 0xe26c or 0xe098 <= pc < 0xe0a6
                or 0x19f2c<=pc<0x1a0f8 or 0x1af04<=pc<0x1b044 or 0x15200<=pc<0x1557a or 0xe3e0<=pc<0xe4aa or 0x20820<=pc<0x20a9c or 0xe540 <= pc < 0xe60a or 0x13440<=pc<0x134dc or 0xf0fa<=pc<0xf35e or 0xeac4 <= pc < 0xec04 or 0x191f4 <= pc < 0x19f2c
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
                value=device.read(a,w)
                script.trace.append(['r',a,w,value])
            else:
                # Synchronize device-owned GPU writes before the CPU sees RAM;
                # declared changing-read inputs remain explicit in Script.read.
                script.memory[a:a+w]=device.read(a,w).to_bytes(w,'big')
                value=script.read(a,w)
                device.direct(a,w,value)
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
                before_GPU=device.ram() if a==0xf03204 and value==0x4320 else None
                device.write(a,value)
                if before_GPU is not None:
                    after_GPU=device.ram()
                    for block in range(0,0x200000,256):
                        previous=before_GPU[block:block+256]
                        following=after_GPU[block:block+256]
                        if previous!=following:
                            assert not(block<task+1024 and block+256>task+64), 'GPU modified CPU task stack'
                            assert not changed or not(block<base+len(payload)and block+256>base), 'GPU modified native code'
                            GPU_coherent_blocks.append(block)
                            engine.mem_write(block,following)

            else:
                script.write(a, w, value)
                device.direct(a,w,value)

        cpu.hook_add(UC_HOOK_CODE, code)
        cpu.hook_add(UC_HOOK_MEM_READ, memory_read)
        cpu.hook_add(UC_HOOK_MEM_WRITE, memory_write)
        cpu.emu_start(start, stop, count=500000, timeout=5000000)
        assert cpu.reg_read(UC_M68K_REG_PC) == stop and cpu.reg_read(UC_M68K_REG_A7) == initial_sp+4
        route = route or 'skipped'
        final_sr = cpu.reg_read(UC_M68K_REG_SR)
        registers = [cpu.reg_read(reg) for reg in dispatch.world.REGS]
        for i in range(len(registers)):
            if i not in [0, 1, 8, 9]:
                assert registers[i] == case['incoming'][i]
        cpu.reg_write(UC_M68K_REG_SR, final_sr ^ 0x2000)
        assert cpu.reg_read(UC_M68K_REG_A7) == alternate
        cpu.reg_write(UC_M68K_REG_SR, final_sr)
        stats=device.stats()
        assert stats['GPUExec1_calls']>0 and not stats['device_error'] and not stats['game_frames_executed']
        script.memory[:]=device.ram()
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
            if actual[at:lo]!=script.memory[at:lo]:
                save(out/'CPU-device-cache-mismatch.json',dict(interval=[at,lo],first_differences=[[j,actual[j],script.memory[j]]for j in range(at,lo)if actual[j]!=script.memory[j]][:50],GPU_coherent_blocks=GPU_coherent_blocks,actual_targeting=actual_targeting,actual_resources=actual_resources,actual_boundaries=actual_boundaries,nested_boundary_calls=nested_boundary_calls,resource_backend_calls=resource_backend_calls,target_slot=int.from_bytes(script.memory[0x49d60:0x49d62],'big'),cursor=[int.from_bytes(script.memory[a:a+2],'big')for a in [0x49d68,0x49d6a]]))
                raise AssertionError('CPU-device-cache-mismatch.json')
            at = hi
        assert actual[at:] == script.memory[at:]
        return dict(script=script, route=route, registers=registers, SR=final_sr,
                    stack=initial_sp-minimum, args=matrix_args, mailbox=mailbox,
                    helpers=helper_contracts, guard_reads=len(guard_reads), instructions=instructions, actual_animation=actual_animation,actual_camera=actual_camera,GPU_stats=stats,GPU_coherent_blocks=GPU_coherent_blocks,actual_targeting=actual_targeting,actual_resources=actual_resources,actual_boundaries=actual_boundaries,nested_boundary_calls=nested_boundary_calls,resource_backend_calls=resource_backend_calls,target_slot=int.from_bytes(script.memory[0x49d60:0x49d62],'big'),cursor=[int.from_bytes(script.memory[a:a+2],'big')for a in [0x49d68,0x49d6a]])

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
            # New bounded helper-layout fixtures, not a live input replay.
            # Open the caller's input gate to ensure actual helper coverage.
            case['initial'] += [[0x49ba4,4,input_case['held']&~0x80],
                [0x49c4c,2,0],[0x49c4e,2,0],[0x49d5a,2,0],
                [0x49cb0,4,0x90000],[0x49cb4,4,0],
                [0x49cae,2,[1,30,127,0x7fff,0x8000,0xffff][i%6]],
                [0x49d16,2,1],[0x49d18,2,i%2],[0x4c24c,4,[0,1,8,30][i%4]],
                [0x112940,2,[0,39,40][i%3]]]
            for record_address in [0x90000,0x96000]:
                case['initial'] += [[record_address,1,0],[record_address+1,1,127],[record_address+2,1,1],[record_address+3,1,0]]
            tables=[0x45db8,0x45df4,0x4613c,0x46088,0x46010,0x45f20,0x45f5c,0x45f98,0x460c4,0x45e6c,0x45ea8,0x45ee4,0x46100,0x45fd4,0x45e30,0x4604c]
            case['initial'] += [[table+actor*20+slot*4,4,0x96000]for table in tables for actor in [0,1,2]for slot in [0,1,2,3,4]]

            # Explicit candidate/transform inputs for the newly connected
            # targeting producer. No host mutation occurs during execution.
            px=next(v for a,w,v in reversed(case['initial'])if a==0x49c50 and w==4)
            pz=next(v for a,w,v in reversed(case['initial'])if a==0x49c56 and w==4)
            case['initial'] += [[0x49d6c+j*206,2,0]for j in range(40)]
            case['initial'] += [[0x49dd8+j*206,2,0]for j in range(40)]
            case['initial'] += [[0x49d5c,2,i%2],[0x49d60,2,0xffff],[0x49d68,2,112],[0x49d6a,2,90],
                [0x49d5a,2,0],[0x4c280,4,0x7fffffff],[0x49cba,1,0]]
            if i%4:
                for j in ([0,39]if i%4==2 else[0]):
                    record=0x49d6c+j*206
                    matrix=0x47b88+(j+4)*64
                    case['initial'] += [[record,2,1],[record+0x6c,2,1],[record+4,4,px],
                        [record+10,4,(pz+10)&0xffffffff],[record+0xc0,2,j+4],
                        [matrix+0x16,2,100],[matrix+0x12,2,0],[matrix+0x14,2,20]]
            if i in [1,2]:
                # Stationary valid-target examples supplement the varied
                # movement states, not a normalization of a live game replay.
                case['poll_inputs']=[0];case.pop('mode_reads',None)
                case['initial'] += [[0x46252,4,case['clock']],[0x49cc4,4,0],[0x49cc8,4,0]]
            # Restore the existing coherent cache/heap fixtures after the
            # generic camera/targeting setup. Actual CPU code computes all
            # get/release/allocate/free outcomes; only loading/wait/signal are
            # explicit providers. No original staging load runs at1C0000.
            case['initial'] += input_case['initial']
            case.pop('mode_reads',None);case['poll_inputs']=[0]
            case['initial'] += [[0x49cb8,2,1],[0x49ba4,4,0x02002000],[0x49c60,2,1],
                [0x49c4c,2,0],[0x49c4e,2,0],[0x49d62,2,0],[0x49d54,2,0],[0x49d56,2,0],
                [0x49d5a,2,0 if input_case['resource_scenario']=='resident_add'else 1],
                [0x49d2c,2,0x70],[0x4622e,1,2],[0x49d16,2,1]]
            case['initial'] += [[0x45d9a+j*2,2,j]for j in range(5)]
            # Additional bounded boundary records. Both lanes receive these
            # exact initial inputs; no host position/counter changes at runtime.
            case.pop('mode_reads',None)
            bx=[200,-200,0,0][i%4];bz=[0,0,200,-200][i%4]
            case['boundary_helper_return']=[0,1,0x12340001][i%3]
            edge=[0x0001,0x1001,0xffff,0x2000][(i//2)%4]
            tile=0x81234;node=0x98000;table=0x99000
            case['initial'] += [[0x49c60,2,1 if i%2==0 else 2],[0x49c50,4,bx&0xffffffff],
                [0x49c56,4,bz&0xffffffff],[0x49cc4,4,0],[0x49cc8,4,0],
                [0x49c78,4,tile],[0x49c18,4,node],[node+8,4,table],
                [tile+6,2,0],[tile+8,2,0],[tile+0x16,2,0],
                [table,2,1],[table+2,2,0x7000],[table+4,2,0xffff if i%4==3 else 0x1234],
                [table+6,2,0xffff],[table+8,2,0x8000],[table+10,2,0],
                [0x49c62,2,0],[0x49c8c,2,1]]
            case['initial'] += [[0x80000+off,2,edge]for off in [2,4,6,8]]
            for path, sr, offset in [('native', 0x700 | (i%32), 1020), ('supervisor_fallback', 0x2700 | (i%32), 1020), ('headroom_fallback', 0x700 | (i%32), 500)]:
                index = len(rows)
                task = 0xc0928 + (i%101)*1024
                sp = task+offset
                state['current_case'] = dict(input=i, path=path, task=task, initial_SP=sp)
                left = execute(case, task, sp, sr, False, index)
                right = execute(case, task, sp, sr, True, index)
                expected_route = 'skipped' if left['route'] == 'skipped' else ('native' if path == 'native' else 'original')
                assert right['route'] == expected_route, (index, right['route'])
                expected = [x for x in left['script'].trace if x[:2] != ['call', 0xe588]] if path == 'native' else left['script'].trace
                assert expected == right['script'].trace, ('trace', index)
                assert left['script'].memory == right['script'].memory, ('RAM', index)
                assert left['helpers'] == right['helpers'], ('helper arguments or D0 seed', index)
                assert left['actual_animation']==right['actual_animation']
                assert left['actual_camera']==right['actual_camera'] and len(right['actual_camera'])==1
                assert len(left['actual_targeting'])==len(right['actual_targeting'])==1
                assert [(x['target'],x['args'])for x in left['actual_boundaries']]==[(x['target'],x['args'])for x in right['actual_boundaries']]
                assert left['nested_boundary_calls']==right['nested_boundary_calls']
                assert left['actual_resources']==right['actual_resources']
                assert left['resource_backend_calls']==right['resource_backend_calls']
                assert left['actual_targeting']==right['actual_targeting'], ('Targeting incoming fullregisters',index)
                assert left['target_slot']==right['target_slot'] and left['cursor']==right['cursor']
                assert left['GPU_stats']['GPUExec1_calls']==right['GPU_stats']['GPUExec1_calls']
                assert left['args'] == right['args'] and left['mailbox'] == right['mailbox']
                assert left['SR'] == right['SR'], ('SR', index)
                raw = [j for j, (a, b) in enumerate(zip(left['registers'], right['registers'])) if a != b]
                assert set(raw).issubset({1, 8, 9}), (index, raw)
                assert left['registers'][1]&65535==right['registers'][1]&65535, ('D1low',index)
                if raw:
                    differences.append(dict(case=index, registers=raw, original=left['registers'], candidate=right['registers']))
                rows.append(dict(input_case=i, input_state=input_case['state'], path=path, actual_route=right['route'], task=task,
                                 original_stack=left['stack'], candidate_stack=right['stack'],
                                 final_SR_equal=True, public_RAM_bus_helper_contracts_equal=True,
                                 raw_volatile_register_differences=raw, guard_identity_reads=right['guard_reads'], actual_animation=right['actual_animation'],actual_camera=right['actual_camera'],GPU_stats=right['GPU_stats'],GPU_coherent_blocks=right['GPU_coherent_blocks'],actual_targeting_incoming=right['actual_targeting'],target_slot=right['target_slot'],cursor=right['cursor'],actual_resources=right['actual_resources'],resource_backend_calls=right['resource_backend_calls'],resource_scenario=input_case['resource_scenario'],actual_boundaries=right['actual_boundaries'],nested_boundary_calls=right['nested_boundary_calls'],boundary_incoming_register_differences=[[j for j,(a,b)in enumerate(zip(x['incoming'],y['incoming']))if a!=b]for x,y in zip(left['actual_boundaries'],right['actual_boundaries'])]))
            if i%16 == 0:
                state['completed'] = len(rows)
                mark()
                gc.collect()
        assert any(x['target']==0x19f2c for row in rows for x in row['actual_boundaries'])
        assert any(x['target']==0x19fda for row in rows for x in row['actual_boundaries'])
        assert all(any(x[0]==0x1af04 for x in row['actual_resources'])for row in rows), 'Resource get not covered'
        assert all(any(x[0]==0x1545c for x in row['actual_resources'])for row in rows), 'Heap free not covered'
        assert any(row['target_slot']==0xffff for row in rows), 'No target-rejection coverage'
        save(out/'cases.json', rows)
        save(out/'raw-volatile-differences.json', differences)
        save(out/'covered-caller-instructions.json', sorted(covered))
        state.update(status='terminal_combined_original_resource_heap_boundary_targeting_camera_animation_GPU_match_provider_limits',
                     completed=len(rows), admitted_native_cases=sum(r['actual_route']=='native' for r in rows),
                     input_skipped_cases=sum(r['actual_route']=='skipped' for r in rows),
                     original_fallback_cases=sum(r['actual_route']=='original' for r in rows),
                     actual_caller_start=start, actual_caller_end=0x1a544,
                     raw_volatile_differing_cases=len(differences),
                     D1_low_word_equal_all_cases=True,
                     earlier_three_prefix_reexecution_reason='New explicitD1lowwordgate and raw-registercapture,not receipt replay.',
                     native_max_caller_stack=max(r['candidate_stack'] for r in rows if r['path']=='native'),
                     fallback_max_caller_stack=max(r['candidate_stack'] for r in rows if r['path']!='native'),
                     guarded_entry_component_prefix_preserved=True,
                     whole_public_RAM_bus_helper_arguments_and_D0_seeds_equal=True,
                     full_caller_final_SR_equal=True, actual_GPU_arithmetic_executed=True,
                     actual_outdoor_boundary_calls=sum(sum(x['target']==0x19f2c for x in row['actual_boundaries'])for row in rows),
                     actual_indoor_boundary_calls=sum(sum(x['target']==0x19fda for x in row['actual_boundaries'])for row in rows),
                     nested_boundary_script_calls=sum(len(row['nested_boundary_calls'])for row in rows),
                     actual_resource_get_calls=sum(sum(x[0]==0x1af04 for x in row['actual_resources'])for row in rows),
                     actual_resource_release_calls=sum(sum(x[0]==0x1b002 for x in row['actual_resources'])for row in rows),
                     actual_heap_allocate_calls=sum(sum(x[0]==0x152a2 for x in row['actual_resources'])for row in rows),
                     actual_heap_free_calls=sum(sum(x[0]==0x1545c for x in row['actual_resources'])for row in rows),
                     scripted_resource_loader_calls=sum(sum(x[0]==0x1b044 for x in row['resource_backend_calls'])for row in rows),
                     scripted_resource_wait_calls=sum(sum(x[0]==0xdf8c for x in row['resource_backend_calls'])for row in rows),
                     scripted_resource_signal_calls=sum(sum(x[0]==0xdf9c for x in row['resource_backend_calls'])for row in rows),
                     resource_scenarios=sorted(set(row['resource_scenario']for row in rows)),
                     actual_targeting_CPU_calls=sum(len(row['actual_targeting_incoming'])for row in rows),
                     all_targeting_incoming_registers_equal=True,
                     selected_target_cases=sum(row['target_slot']!=0xffff for row in rows),
                     actual_targeting_20820_scripted=False,
                     original_GPU_execution_both_lanes=True,
                     actual_camera_CPU_calls=sum(len(row['actual_camera'])for row in rows),
                     original_GPUExec1_calls=sum(row['GPU_stats']['GPUExec1_calls']for row in rows),
                     actual_animation_CPU_calls=sum(sum(x[0]==0xeb04 for x in row['actual_animation'])for row in rows),
                     actual_animation_queue_CPU_calls=sum(sum(x[0]==0xeac4 for x in row['actual_animation'])for row in rows),
                     actual_animation_EB04_EAC4_scripted=False, actual_camera_F0FA_scripted=False,
                     input_states_covered=sorted(set(row['input_state']for row in rows)),
                     source_sha256={str(p):sha(p) for p in [Path(__file__),guard_path,proof_path,payload_path,snapshot_path,target_proof_path,
                         Path(proof['directory'])/'cases.json',Path(dispatch.__file__),Path(world.__file__),Path(gpu.__file__),Path(controls.__file__),Path(boundary.__file__),ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',
                         out/'cases.json',out/'raw-volatile-differences.json',out/'covered-caller-instructions.json']},
                     scope='ActualoriginalfullcallerwithoriginalEB04/EAC4andE588CPUinstructions;guardednativeinputat1A266only.26boundedlayoutfixturesacross13states,threemodes. Explicitfiniteanimationrecords/counters/timestepandcallerinputgateopenedforcoverage;notlivecontrollerorimageequalitytest. SynchronousGPUwritesarepropagatedcoherentlytotheCPUcacheattheactualsubmit;noresultmasking. CameraF0FA/originalnestedmultiply/division/directionandoriginalGPU4320executeinbothlaneswithsynchronousdevicecompletion. Original20820targetingandnestedmathnowexecute;candidate/transformrecordsareexplicitfixtureinputs. Actualresource1AF04/1B002andheap152A2/1545Cexecute;loader1B044/waitDF8C/signalDF9Cremainexplicitproviders. Originalstreamloaderwouldusestaging1C0000whichisfixturecode,soisnotexecutedhere. Original19F2C/19FDAalsoconnectedinthesamecaller;nestedgeometry/cleanup/scene setup/yieldremainexplicitproviders. Notfullcollisionordisc-loading/IRQproof. ComparepublicRAM,orderedbus/helperargs/inputD0seeds,finalSR,callee-saveandrecordrawvolatilelimits. RealanimationCPUisnewlyconnected,notnewlyrecoveredfunction;noarbitraryIRQ/freshgame/imageclaim.')
        mark()
        device.close()
        print(state['status'], len(rows), 'cases', len(differences), 'raw contexts differ', flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json', rows)
        if 'left' in locals() and 'right' in locals():
            save(out/'failure-comparison.json',dict(original_trace=left['script'].trace,candidate_trace=right['script'].trace,
                original_helpers=left['helpers'],candidate_helpers=right['helpers']))
        state.update(status='terminal_full_caller_comparison_failed',completed=len(rows),error=repr(error))
        mark()
        device.close()
        raise


if __name__ == '__main__':
    main()
