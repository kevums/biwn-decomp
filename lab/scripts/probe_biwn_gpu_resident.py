"""Capture resident draws with reproducible original preparation/blitter state."""
import argparse,ctypes as c,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
from probe_biwn_gpu_draw import blitter_registers
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);ref=read(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json');base=Path(ref['directory']);refrows=read(base/'cases.json');mapping=read(session/'gpu-resident-C-candidate/C-generation.json');decoded={r['address']:r for r in mapping['instructions_decoded']}
    out=session/'gpu-resident-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-resident-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0;lib.lab_resident_watch.restype=c.c_int;assert lib.lab_resident_watch()==0
    lib.lab_resident_prepare.argtypes=[c.c_uint32];lib.lab_resident_prepare.restype=c.c_int;lib.lab_resident_original.restype=c.c_int;lib.lab_resident_steps.restype=c.c_uint32;lib.lab_resident_PC.argtypes=[c.c_uint32];lib.lab_resident_PC.restype=c.c_uint32;lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    vectors=[(i,n)for i,r in enumerate(refrows)for n in range(1,r['commands'].count('0x6380'))][:opt.limit or None];rows=[];covered=set()
    try:
        for number,(index,occurrence)in enumerate(vectors):
            stem=f'case-{number:02d}';save(out/'status.json',dict(status='running',case=number));memory=(base/f'case-{index:02d}-before-RAM.bin').read_bytes();raw=(base/f'case-{index:02d}-before-GPU-state.bin').read_bytes();device.seed(memory,1);buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw);assert lib.lab_resident_prepare(occurrence)==0,(index,occurrence)
            before=device.ram();before_raw,before_state=gpu_state(core);before_blitter=blitter_registers(core)
            for suffix,data in [('before-RAM',before),('before-GPU-state',before_raw),('before-blitter-registers',before_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            status=lib.lab_resident_original();after=device.ram();after_raw,after_state=gpu_state(core);after_blitter=blitter_registers(core);steps=[lib.lab_resident_PC(i)for i in range(lib.lab_resident_steps())]
            for suffix,data in [('after-RAM',after),('after-GPU-state',after_raw),('after-blitter-registers',after_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            events=[]
            for i in range(lib.lab_movement_event_count()):
                event=(c.c_uint32*5)();assert lib.lab_movement_event(i,event)==0
                if event[1]==3 and event[0]in [11,12]:events.append(list(event))
            for pc in steps:
                assert pc in decoded,hex(pc);covered.add(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:covered.add(pc+2)
            row=dict(case=number,original_projection_case=index,occurrence=occurrence,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,events=events,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw),before_blitter_registers_sha256=sha(before_blitter),after_blitter_registers_sha256=sha(after_blitter),preparation_scope='Replayed original setup/dispatcher/consumer/material/preceding-resident from frozen real projection with initially reset blitter. Ccomparison must rerun the same preparation, not restore only aliased blitter readbacks.')
            rows.append(row);save(out/'cases.json',rows);assert status==0 and after_state['pc']==0xf031be,(number,status,hex(after_state['pc']));print(json.dumps(dict(case=number,entry=hex(before_state['pc']),steps=len(steps),events=len(events))),flush=True)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_resident_entries_captured_C_unverified',directory=str(out),cases=len(rows),source_instruction_coverage=[len(covered),len(decoded)],uncovered_instructions=[decoded[pc]for pc in sorted(set(decoded)-covered)],source_projection_directory=str(base),probe_source_sha256=sha(Path(__file__).read_bytes()),bridge_source_sha256=sha((ROOT/'scripts/biwn_resident_probe_bridge.c').read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-resident-probe.dylib').read_bytes()),scope='Original GPU resident only after repeatable original preparation and synchronous pinned fast blitter. Reset blitter at initial replay, preserve context thereafter. Stop at F031BE; dispatcher recipient not compared. Original CPU submission wrappers host-adapted. Watch readvalues placeholders; original GPU sole oracle. Full natural scene/hardware/async timing not proved.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_preflight'if opt.limit else'terminal_pass'))
        if not opt.limit:save(ROOT/'verification/biwn-gpu-resident-original-probes.json',report)
        print(json.dumps(dict(cases=len(rows),coverage=report['source_instruction_coverage'],directory=str(out))))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
