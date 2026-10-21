"""Capture actual material entries from original integer-mode draw chains."""
import ctypes as c,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);reference=read(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json');base=Path(reference['directory']);reference_rows=read(base/'cases.json')
    out=session/'gpu-material-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-material-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    lib.lab_material_prepare.argtypes=[c.c_uint32,c.c_uint32];lib.lab_material_prepare.restype=c.c_int;lib.lab_material_original.restype=c.c_int;lib.lab_material_steps.restype=c.c_uint32;lib.lab_material_PC.argtypes=[c.c_uint32];lib.lab_material_PC.restype=c.c_uint32
    lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    rows=[];coverage={h:set()for h in [0x6460,0x6720,0x69a0]};decoded={}
    for h,end in [(0x6460,0xf033a4),(0x6720,0xf0335a),(0x69a0,0xf0335a)]:decoded[h]={r['address']:r for r in read(session/f'gpu-render-{h:x}-overlay/initial-linear-decode.json')['rows']if r['address']<end}
    try:
        for h in coverage:
            for index,ref in enumerate(reference_rows):
                for occurrence in range(1,ref['commands'].count(hex(h))+1):
                    number=len(rows);stem=f'case-{number:02d}';save(out/'status.json',dict(status='running',header=hex(h),case=number))
                    device.seed((base/f'case-{index:02d}-before-RAM.bin').read_bytes(),1);raw=(base/f'case-{index:02d}-before-GPU-state.bin').read_bytes();buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw)
                    assert lib.lab_material_prepare(h,occurrence)==0
                    before=device.ram();before_raw,before_state=gpu_state(core)
                    for suffix,data in [('before-RAM',before),('before-GPU-state',before_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
                    status=lib.lab_material_original();after=device.ram();after_raw,after_state=gpu_state(core);steps=[lib.lab_material_PC(i)for i in range(lib.lab_material_steps())]
                    for suffix,data in [('after-RAM',after),('after-GPU-state',after_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
                    events=[]
                    for i in range(lib.lab_movement_event_count()):
                        event=(c.c_uint32*5)();assert lib.lab_movement_event(i,event)==0
                        if event[1]==3 and event[0]in [11,12]:events.append(list(event))
                    for pc in steps:
                        assert pc in decoded[h],(hex(h),hex(pc));coverage[h].add(pc)
                        if int(decoded[h][pc]['bytes'][:4],16)>>10 in [52,53]:coverage[h].add(pc+2)
                    assert status==0 and after_state['pc']==0xf03440
                    rows.append(dict(case=number,CPU_header=hex(h),original_scene_case=index,occurrence=occurrence,declared_variant=False,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,events=events,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw)))
                    save(out/'cases.json',rows)
        programs={hex(h):dict(cases=sum(row['CPU_header']==hex(h)for row in rows),source_instruction_coverage=[len(coverage[h]),len(decoded[h])],uncovered_instructions=[decoded[h][pc]for pc in sorted(set(decoded[h])-coverage[h])])for h in coverage}
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_material_entries_captured_C_unverified',directory=str(out),cases=len(rows),programs=programs,source_original_draw_directory=str(base),probe_source_sha256=sha(Path(__file__).read_bytes()),bridge_source_sha256=sha((ROOT/'scripts/biwn_material_probe_bridge.c').read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-material-probe.dylib').read_bytes()),full_renderer_C=False,scope='Actual original projection/setup/consumer/material/resident execution precedes each captured entry. Stop at resident F03440 after mandatory delay; recipient execution not in material comparison. CPU submission wrappers remain host-adapted. Original pinned GPU only; watch read values are placeholders.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-material-original-probes.json',report);print(json.dumps(dict(cases=len(rows),programs={h:{k:v for k,v in p.items()if k!='uncovered_instructions'}for h,p in programs.items()})))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
