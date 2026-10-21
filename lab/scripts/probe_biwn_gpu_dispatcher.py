"""Original dispatcher source bodies: copies, cache hits and declared polling."""
import ctypes as c,hashlib,json,random,struct
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-dispatcher-loop/source-decode.json');decoded={r['address']:r for r in mapping['rows']};projection=Path(read(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json')['directory']);out=session/'gpu-dispatcher-loop/original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-dispatcher-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    lib.lab_dispatcher_prepare.argtypes=[c.c_uint32,c.c_int];lib.lab_dispatcher_prepare.restype=c.c_int;lib.lab_dispatcher_original.argtypes=[c.c_uint,c.c_uint32,c.c_uint];lib.lab_dispatcher_original.restype=c.c_int;lib.lab_dispatcher_steps.restype=c.c_uint32;lib.lab_dispatcher_PC.argtypes=[c.c_uint32];lib.lab_dispatcher_PC.restype=c.c_uint32;lib.lab_dispatcher_polls.restype=c.c_uint32;lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    lib.lab_dispatcher_flags.argtypes=[c.c_uint32];lib.lab_dispatcher_flags.restype=c.c_uint32
    headers=[0x57a0,0x6380,0x6460,0x6720,0x69a0,0x4d80,0x52e0,0x58a0];vectors=[dict(header=h,cache_hit=hit,seed=seed,yield_idle=1,inject_header=0xffffffff,wait_reads=0)for h in headers for hit in [False,True]for seed in range(4)]
    vectors += [dict(header=0xffffffff,cache_hit=False,seed=seed,yield_idle=1,inject_header=0xffffffff,wait_reads=0)for seed in range(4)]
    vectors += [dict(header=0xffffffff,cache_hit=False,seed=i,yield_idle=0,inject_header=0x57a0,wait_reads=wait)for i,wait in enumerate([0,1,3,7])]
    rows=[];covered=set()
    try:
        for number,fixture in enumerate(vectors):
            stem=f'case-{number:02d}';save(out/'status.json',dict(status='running',case=number));index=fixture['seed']%4;device.seed((projection/f'case-{index:02d}-before-RAM.bin').read_bytes(),1);raw=bytearray((projection/f'case-{index:02d}-before-GPU-state.bin').read_bytes());rng=random.Random(0x31be+number);struct.pack_into('=64I',raw,4139,*[rng.getrandbits(32)for _ in range(64)]);raw[4136:4139]=bytes([(number>>n)&1 for n in range(3)]);buf=c.create_string_buffer(bytes(raw));assert core.GPUStateLoad(buf)==len(raw);assert lib.lab_dispatcher_prepare(fixture['header'],fixture['cache_hit'])==0
            before=device.ram();before_raw,before_state=gpu_state(core)
            for suffix,data in [('before-RAM',before),('before-GPU-state',before_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            status=lib.lab_dispatcher_original(fixture['yield_idle'],fixture['inject_header'],fixture['wait_reads']);after=device.ram();after_raw,after_state=gpu_state(core);steps=[lib.lab_dispatcher_PC(i)for i in range(lib.lab_dispatcher_steps())];events=[]
            for suffix,data in [('after-RAM',after),('after-GPU-state',after_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            for i in range(lib.lab_movement_event_count()):
                ev=(c.c_uint32*5)();assert lib.lab_movement_event(i,ev)==0
                if ev[1]==3 and ev[0]in [11,12]:events.append(list(ev))
            for pc in steps:
                assert pc in decoded,hex(pc);covered.add(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:covered.add(pc+2)
            assert status==0 and (after_state['pc']==0xf031ce or not 0xf031be<=after_state['pc']<0xf03200)
            rows.append(dict(case=number,fixture=fixture,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,flags_before_each_direct_PC=[lib.lab_dispatcher_flags(i)for i in range(len(steps))],events=events,host_poll_count=lib.lab_dispatcher_polls(),before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw)));save(out/'cases.json',rows)
        assert covered==set(decoded),[hex(pc)for pc in set(decoded)-covered]
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_dispatcher31_instructions_captured_C_unverified',directory=str(out),cases=len(rows),source_instruction_coverage=[31,31],program_headers=[hex(h)for h in headers],copy_cases=32,cache_hit_cases=32,idle_yield_cases=4,scripted_poll_cases=4,source_payload_sha256=mapping['payload_sha256'],probe_source_sha256=sha(Path(__file__).read_bytes()),bridge_source_sha256=sha((ROOT/'scripts/biwn_dispatcher_probe_bridge.c').read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-dispatcher-probe.dylib').read_bytes()),scope='Eight preserved positive finite source headers,copy/cache variants and seeded register/flag state. Host idle-yield boundary matches original draw observer; four additional source polling cases use declared command injection before chosen LOAD poll. Not asynchronous/hardware validation or full636byte mainGPUboot program. Nativewatchreadvalues placeholders; originalGPU sole oracle.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-dispatcher-original-probes.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['scope','program_headers']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
