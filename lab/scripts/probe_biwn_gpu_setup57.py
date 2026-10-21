"""Original57A0 standalone fixtures: frozen real projection plus declared seeds.

Both comparison paths reset the pinned blitter before restoring identical GPU
inputs. The natural original draw-chain proof is retained separately.
"""
import ctypes as c,hashlib,json,random,struct
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
from probe_biwn_gpu_draw import blitter_registers
ROOT=frame.ROOT;save=frame.save;read=lambda p:json.loads(p.read_text());sha=lambda x:hashlib.sha256(x).hexdigest()
def main():
    original=read(ROOT/'verification/biwn-gpu-draw-original-probes.json');base=Path(original['directory']);base_rows=read(base/'cases.json');session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-render-57a0-overlay/initial-linear-decode.json');decoded={r['address']:r for r in mapping['rows']if r['address']<0xf03322};assert len(decoded)==73
    out=session/'gpu-render-57a0-overlay/standalone-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-setup57-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    for name in ['lab_setup57_watch','lab_setup57_prepare','lab_setup57_original']:getattr(lib,name).restype=c.c_int
    assert lib.lab_setup57_watch()==0
    lib.lab_setup57_steps.restype=c.c_uint32;lib.lab_setup57_PC.argtypes=[c.c_uint32];lib.lab_setup57_PC.restype=c.c_uint32
    lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    rows=[];covered=set();rng=random.Random(0x57a073)
    try:
        for number in range(64):
            save(out/'status.json',dict(status='running',case=number));base_case=number//16;stem=f'case-{number:02d}';prefix=(base/f'case-{base_case:02d}-before-RAM.bin').read_bytes();raw=bytearray((base/f'case-{base_case:02d}-before-GPU-state.bin').read_bytes());assert sha(prefix)==base_rows[base_case]['before_RAM_sha256']and sha(raw)==base_rows[base_case]['before_GPU_state_sha256']
            seed=None
            if number%16:
                seed=rng.getrandbits(32);values=[rng.getrandbits(32)for _ in range(64)];struct.pack_into('=64I',raw,4139,*values);raw[4136:4139]=bytes([number&1,(number>>1)&1,(number>>2)&1])
                struct.pack_into('=I',raw,4100,rng.getrandbits(32));struct.pack_into('=I',raw,4104,rng.getrandbits(32));struct.pack_into('=I',raw,4116,rng.getrandbits(32));struct.pack_into('=I',raw,4120,rng.getrandbits(32)&~3)
            device.seed(prefix,0);buf=c.create_string_buffer(bytes(raw));assert core.GPUStateLoad(buf)==len(raw)
            assert lib.lab_setup57_prepare()==0
            before=device.ram();before_gpu,before_state=gpu_state(core);before_blitter=blitter_registers(core)
            for suffix,data in [('before-RAM',before),('before-GPU-state',before_gpu),('before-blitter-registers',before_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            status=lib.lab_setup57_original();steps=[lib.lab_setup57_PC(i)for i in range(lib.lab_setup57_steps())];after=device.ram();after_gpu,after_state=gpu_state(core);after_blitter=blitter_registers(core)
            for suffix,data in [('after-RAM',after),('after-GPU-state',after_gpu),('after-blitter-registers',after_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            events=[]
            for i in range(lib.lab_movement_event_count()):
                event=(c.c_uint32*5)();assert lib.lab_movement_event(i,event)==0
                if event[1]==3 and event[0]in [11,12]:events.append(list(event))
            covered.update(steps)
            for pc in steps:
                assert pc in decoded,hex(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:covered.add(pc+2)
            row=dict(case=number,base_original_case=base_case,declared_register_seed=seed,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,events=events,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_gpu),after_GPU_state_sha256=sha(after_gpu),before_blitter_registers_sha256=sha(before_blitter),after_blitter_registers_sha256=sha(after_blitter),queued_command=hex(int.from_bytes(after_gpu[0x204:0x208],'big')),resident_payload_sha256=sha(after_gpu[0x440:0xf18]))
            rows.append(row);save(out/'cases.json',rows);assert status==0 and after_state['pc']==0xf031be and row['queued_command']=='0x6380'and row['resident_payload_sha256']=='9f14522e92bc2a5b3d9bb2db0adb7a2dfb897709bf3f500ef7c6f58203ef25ff',row
        assert covered==set(decoded),[hex(pc)for pc in set(decoded)-covered]
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_GPU57A0_all73_standalone_observed_C_unverified',directory=str(out),cases=len(rows),source_instruction_coverage=[len(covered),73],payload_sha256=mapping['payload_SHA256'],bridge_source_sha256=sha((ROOT/'scripts/biwn_setup57_probe_bridge.c').read_bytes()),probe_source_sha256=sha(Path(__file__).read_bytes()),probe_library_sha256=sha((ROOT/'tools/libbiwn-setup57-probe.dylib').read_bytes()),scope='Four real projection-output captures and60declared register/flag/accumulator/remainder/matrix-state variants. Blitter is reset before bothpaths; originalresidentdispatcher prepares57A0entry but is not part of Ccomparison. No GPUreset after restoringinputstate. Nativeexternalbuswatch readvalues are placeholders; readshape/stores retained. Matrixcontrol/localmailbox effects compared throughsnapshot; directGPUinternal accesses are not watched. Fullnatural drawchain is a separate original-only proof; noCsetup acceptance/viewport/game claim.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-setup57-original-probes.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
