"""Original52E0 with declared camera variants over retained real scene records.

The scene prefix is not rerun for variants: restored GPUStateLoad and identical
record buffers isolate projection. Neither game progression nor hardware proof.
"""
import argparse,ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;save=frame.save;sha=lambda x:hashlib.sha256(x).hexdigest()
read=lambda p:json.loads(p.read_text())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=64);opt=ap.parse_args()
    base=read(ROOT/'verification/biwn-gpu-projection-original-probes.json');capture=Path(base['directory']);base_rows=read(capture/'cases.json');session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-render-52e0-overlay/C-generation.json');decoded={r['address']:r for r in mapping['instructions_decoded']}
    out=session/'gpu-render-52e0-overlay/camera-variant-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-projection-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    for name in ['lab_projection_prepare','lab_projection_original']:getattr(lib,name).restype=c.c_int
    lib.lab_projection_steps.restype=c.c_uint32;lib.lab_projection_PC.argtypes=[c.c_uint32];lib.lab_projection_PC.restype=c.c_uint32
    lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    rotations=[[16384,0,0,0,16384,0,0,0,16384],[0,0,16384,0,16384,0,-16384,0,0],[0,0,-16384,0,16384,0,16384,0,0],[-16384,0,0,0,16384,0,0,0,-16384],[16384,0,0,0,0,-16384,0,16384,0],[0,-16384,0,16384,0,0,0,0,16384],[0,16384,0,-16384,0,0,0,0,16384],[16384,0,0,0,-16384,0,0,0,-16384]]
    rng=random.Random(0x52e0450);rows=[];covered=set()
    try:
        for number in range(opt.limit):
            save(out/'status.json',dict(status='running',case=number));original=base_rows[(number//16)*4%16];stem=f'case-{number:02d}';base_stem=f'case-{original["case"]:02d}'
            prefix=bytearray((capture/f'{base_stem}-prefix-RAM.bin').read_bytes());prefix_raw=(capture/f'{base_stem}-prefix-GPU-state.bin').read_bytes();assert sha(prefix)==original['prefix_RAM_sha256']and sha(prefix_raw)==original['prefix_GPU_state_sha256']
            rotation=rotations[number%len(rotations)];translation=[rng.choice([-4096,-512,-64,-1,0,1,64,512,4096])for _ in range(3)]
            for i,value in enumerate(rotation+translation):prefix[0x47b88+2*i:0x47b8a+2*i]=(value&65535).to_bytes(2,'big')
            device.seed(bytes(prefix),0);raw_buffer=c.create_string_buffer(prefix_raw);assert core.GPUStateLoad(raw_buffer)==len(prefix_raw)
            raw,state=gpu_state(core);assert raw==prefix_raw
            (out/f'{stem}-prefix-GPU-state.bin').write_bytes(raw)
            assert lib.lab_projection_prepare()==0
            before=device.ram();before_raw,before_state=gpu_state(core);(out/f'{stem}-before-RAM.bin').write_bytes(before);(out/f'{stem}-before-GPU-state.bin').write_bytes(before_raw)
            status=lib.lab_projection_original();steps=[lib.lab_projection_PC(i)for i in range(lib.lab_projection_steps())];after=device.ram();after_raw,after_state=gpu_state(core)
            (out/f'{stem}-after-RAM.bin').write_bytes(after);(out/f'{stem}-after-GPU-state.bin').write_bytes(after_raw)
            events=[]
            for i in range(lib.lab_movement_event_count()):
                event=(c.c_uint32*5)();assert lib.lab_movement_event(i,event)==0
                if event[1]==3 and event[0]in [11,12]:events.append(list(event))
            covered.update(steps)
            for pc in steps:
                assert pc in decoded,hex(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:covered.add(pc+2)
            row=dict(case=number,base_original_case=original['case'],base_directory=str(capture),camera_rotation=rotation,camera_translation=translation,prefix_GPU=state,before_GPU=before_state,after_GPU=after_state,record_count=int.from_bytes(prefix[0x49b88:0x49b8c],'big'),status=status,steps=steps,events=events,completion_before=int.from_bytes(before[0x10a684:0x10a688],'big'),completion_after=int.from_bytes(after[0x10a684:0x10a688],'big'),before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw))
            rows.append(row);save(out/'cases.json',rows);assert status==0 and after_state['pc']==0xf031be,dict(case=number,status=status,pc=hex(after_state['pc']))
            print(json.dumps(dict(case=number,steps=len(steps),covered=len(covered),wrap_previous=0xf03558 in covered,wrap_next=0xf03560 in covered)),flush=True)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='declared_camera_variants_original_GPU52E0_returned_C_comparison_pending',directory=str(out),cases=len(rows),source_instruction_coverage=[len(covered),450],unobserved_candidate_addresses=[hex(pc)for pc in sorted(set(decoded)-covered)],base_original_probe=str(capture),camera_matrices=rotations,payload_sha256=mapping['payload_sha256'],probe_source_sha256=sha(Path(__file__).read_bytes()),scope='Declared valid axis rotation and signedtranslation camera fixtures on real captured records. GPUstate is restored from retained live prefix, no syntheticGPUinstruction entry inside program. PrefixCPU is not rerun; mainRAMcamera words are controlled inputs. OriginalGPUonly; fullviewport/game unproved.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-projection-variant-original-probes.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
