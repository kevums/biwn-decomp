"""Full logical GPU4320 state versus original instructions, all prior vectors."""
import argparse
import ctypes as c
import hashlib
import json
import os
import random
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_movie_GPU as gpu
import check_biwn_retained_merchant_movement as joined

ROOT = gpu.ROOT
save = gpu.save
sha = gpu.sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    options = parser.parse_args()
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    setup = json.loads((session/'media-setup-fullCPU-generation.json').read_text())
    proof = json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text())
    runtime = gpu.media.Runtime(Path(proof['directory'])/'libmedia-setup.dylib', setup['instructions_decoded'])
    out = ROOT/'verification/GPU4720-full-state'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    generated=json.loads((ROOT/'verification/GPU4720-generation-current.json').read_text());src=Path(generated['directory'])
    library = out/'libGPU4720-full-state.dylib'
    command = ['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_gpu_command4720.c'),'-o',str(library)]
    built = subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.txt').write_text(built.stdout+built.stderr)
    assert built.returncode==0,built.stderr
    lib = c.CDLL(str(library)); run = lib.biwn_gpu_command4720_run
    run.argtypes=[c.POINTER(joined.MovementBus),c.POINTER(gpu.State),c.c_uint32];run.restype=c.c_int
    core=runtime.core
    core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32
    core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
    core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count')
    cases=[];fixture_rng=random.Random(0x4720)
    for axis in range(3):
        for angle in range(256):
            params=[0x47bc8,0,0,0,0];params[axis+1]=angle;cases.append(dict(kind='single_axis',axis=axis,params=params))
    for i in range(128):
        cases.append(dict(kind='mixed_raw_angles_and_flag',params=[0x47bc8,*[fixture_rng.getrandbits(32)for _ in range(3)],[0,1,0x7fff,0x8000,0xffff,0x12340000,0xffff0001,0xffffffff][i%8]]))
    if options.limit:cases=cases[:options.limit]
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    payload=snapshot[generated['payload_start']:generated['payload_start']+generated['payload_bytes']];assert hashlib.sha256(payload).hexdigest()==generated['payload_sha256']
    decoded={x['address']:x for x in generated['instructions_decoded']}
    rng=random.Random(0x47204720);results=[];coverage=set();all_outer=0;all_steps=0;errors=[]
    def reader(width):
        def read(_,a,v):
            try:v[0]=core.GPUReadWord(a,3) if width==2 else core.GPUReadLong(a,3);return 0
            except Exception as e:errors.append(repr(e));return 1
        return read
    def writer(width):
        def write(_,a,v):
            try:(core.GPUWriteWord if width==2 else core.GPUWriteLong)(a,v,3);return 0
            except Exception as e:errors.append(repr(e));return 1
        return write
    PCs=[]
    callbacks=[gpu.R16(reader(2)),gpu.R32(reader(4)),joined.W16(writer(2)),gpu.W32(writer(4)),gpu.OBS(lambda _,pc:PCs.append(pc))]
    bus=joined.MovementBus(*callbacks,None)
    try:
        for index,case in enumerate(cases):
            save(out/'status.json',dict(status='running',case=index,total=len(cases)))
            ram=bytearray(snapshot);base=case['params'][0];ram[base:base+32]=rng.randbytes(32)
            runtime.reset(bytes(ram),index%3)
            raw,_=joined.video.gpu_state(core)
            s=gpu.state_from_raw(raw)
            s.local_RAM[0x240:0x240+len(payload)]=payload
            for offset,value in enumerate(case['params']):s.local_RAM[0x20c+4*offset:0x210+4*offset]=value.to_bytes(4,'big')
            for bank in range(2):
                for register in range(32):s.registers[bank][register]=rng.getrandbits(32)
            s.active_bank=0;s.pc=0xf03240;s.control=0x2801;s.flags=0xd0
            s.z=index&1;s.c=(index>>1)&1;s.n=(index>>2)&1
            s.matrix_control=rng.getrandbits(32);s.matrix_pointer=rng.getrandbits(32)
            s.accumulator=rng.getrandbits(32);s.remainder=rng.getrandbits(32);s.hidata=rng.getrandbits(32)
            s.division_control=rng.getrandbits(32)
            inherited=bytes(s)
            native_initial=gpu.logical(s)+raw[4396:]
            buf=c.create_string_buffer(native_initial);assert core.GPUStateLoad(buf)==len(raw)
            steps=[];delays=[]
            for _ in range(10000):
                pc=core.GPUGetPC()
                if pc==0xf031be:break
                assert pc in decoded,hex(pc)
                steps.append(pc);core.GPUExec(1)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53] and core.GPUGetPC()!=pc+2:delays.append(pc+2)
            else:raise AssertionError('Native GPU4720 bound')
            expected=joined.video.gpu_state(core)[0][:4396];expected_ram=runtime.device.ram()
            runtime.reset(bytes(ram),index%3);PCs.clear();s=gpu.State.from_buffer_copy(inherited);count=counter.value
            status=run(c.byref(bus),c.byref(s),10000)
            assert counter.value==count and not errors
            if status or gpu.logical(s)!=expected or runtime.device.ram()!=expected_ram or PCs!=steps or s.instructions!=len(steps)+len(delays):
                save(out/'mismatch.json',dict(case=index,parameters=case,status=status,C_PC=hex(s.pc),
                    GPU_differences=[hex(i) for i,(a,b) in enumerate(zip(gpu.logical(s),expected)) if a!=b][:40],
                    RAM_differences=[hex(i) for i,(a,b) in enumerate(zip(runtime.device.ram(),expected_ram)) if a!=b][:40],
                    PC_trace_match=PCs==steps,C_steps=s.instructions,native_steps=len(steps)+len(delays)))
                raise AssertionError(str(out/'mismatch.json'))
            coverage.update(steps);coverage.update(delays);all_outer+=len(steps);all_steps+=s.instructions
            results.append(dict(case=index,parameters=case,logical_GPU_sha256=sha(expected),RAM_sha256=sha(expected_ram),
                                outer_blocks=len(steps),instructions=s.instructions,original_GPU_instructions_on_C_path=0))
        save(out/'fixtures.json',results)
        assert options.limit or coverage==set(decoded)
        # Added ABI/work/error contracts are not source behavior claims.
        guards=[];initial=gpu.State.from_buffer_copy(inherited)
        checks=[('null_bus',None,c.byref(initial),10000,1),('null_state',c.byref(bus),None,10000,1),
                ('zero_budget',c.byref(bus),c.byref(initial),0,1)]
        for name,busarg,statearg,budget,expected_status in checks:
            before=bytes(initial);assert run(busarg,statearg,budget)==expected_status and bytes(initial)==before
            guards.append(dict(case=name,status=expected_status))
        for name,value,status in [('pc',0,3),('active_bank',1,1),('z',2,1),('c',2,1),('n',2,1)]:
            state=gpu.State.from_buffer_copy(inherited);setattr(state,name,value);before=bytes(state)
            assert run(c.byref(bus),c.byref(state),10000)==status and bytes(state)==before
            guards.append(dict(case=name,value=value,status=status))
        save(out/'guards.json',guards)
        report=dict(status='GPU4720_full_inherited_state_original_C_match' if not options.limit else 'terminal_preflight',
                    recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),
                    source_instruction_coverage=[len(coverage),len(decoded)],outer_blocks=all_outer,instructions=all_steps,
                    guards=len(guards),logical_GPU_bytes=4396,complete_RAM_bytes=2097152,source_sha256=generated['source_sha256'],payload_sha256=generated['payload_sha256'],core_path=str(runtime.core._name),core_sha256=sha(Path(runtime.core._name).read_bytes()),coordinator_authored=True,new_training=False,source_service_integrated=False,
                    script_sha256=sha(Path(__file__).read_bytes()),whole_game_complete=False,
                    limits=['Controlled standalone source-loaded GPU4720 and argument fixtures; CPU E26C/dispatcher and seven-scene chain not yet connected.',
                            'Logical architectural GPU state excludes pipeline microstate; pinned emulator, no physical timing.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass' if not options.limit else 'terminal_preflight'))
        if not options.limit:save(ROOT/'verification/GPU4720-full-state-current.json',report)
        print({k:report[k]for k in ['status','cases','source_instruction_coverage','instructions','guards','logical_GPU_bytes','complete_RAM_bytes']},flush=True)
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()


if __name__=='__main__':main()
