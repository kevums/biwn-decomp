"""Finite material/viewport variants over real resident entry data; no force PC."""
import ctypes as c,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
from probe_biwn_gpu_draw import blitter_registers
import resident_fixture_inputs
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);proof=read(ROOT/'verification/biwn-gpu-resident-original-probes.json');base=Path(proof['directory']);assert not proof.get('declared_variant_cases');projection=Path(proof['source_projection_directory']);natural=read(base/'cases.json');mapping=read(session/'gpu-resident-C-candidate/C-generation.json');decoded={r['address']:r for r in mapping['instructions_decoded']};out=session/'gpu-resident-variant-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=list(natural)
    for row in natural:
        stem=f'case-{row["case"]:02d}'
        for suffix in ['before-RAM','before-GPU-state','before-blitter-registers','after-RAM','after-GPU-state','after-blitter-registers']:os.link(base/f'{stem}-{suffix}.bin',out/f'{stem}-{suffix}.bin')
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-resident-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32;lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0;lib.lab_resident_watch.restype=c.c_int;assert lib.lab_resident_watch()==0
    lib.lab_resident_prepare.argtypes=[c.c_uint32];lib.lab_resident_prepare.restype=c.c_int;lib.lab_resident_original.restype=c.c_int;lib.lab_resident_steps.restype=c.c_uint32;lib.lab_resident_PC.argtypes=[c.c_uint32];lib.lab_resident_PC.restype=c.c_uint32;lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    try:
        bases=[row for row in natural if row['original_projection_case']==0 and row['before_GPU']['pc']==0xf03440]
        for original in bases:
            for variant in range(8):
                number=len(rows);stem=f'case-{number:02d}';save(out/'status.json',dict(status='running',case=number));original_stem=f'case-{original["case"]:02d}';memory=(base/f'{original_stem}-before-RAM.bin').read_bytes();raw=(base/f'{original_stem}-before-GPU-state.bin').read_bytes();params=int.from_bytes(raw[0x20c:0x210],'big');count=int.from_bytes(memory[params+2:params+4],'big');assert 0<count<512
                patches=[];cursor=params+16;palette=[0x0000,0xffff,0x0080,0x7f80]
                for polygon in range(count):
                    n=int.from_bytes(memory[cursor+4:cursor+6],'big');assert 2<n<=16,(original['case'],polygon,n)
                    if variant<4:
                        patches.extend([dict(address=cursor,width=2,value=0xffff),dict(address=cursor+6,width=2,value=palette[variant])])
                    cursor+=8+2*n
                registers=[]
                if variant in [4,5,6,7]:
                    width,height=[(32,32),(112,90),(320,240),(1,1)][variant-4];registers=[dict(bank=1,register=2,value=width),dict(bank=1,register=3,value=height)]
                inputs=dict(base_natural_case=original['case'],variant=variant,polygon_count=count,parameter_pointer=hex(params),RAM_patches=patches,register_patches=registers,scope='Declared flat material/color or finite viewport-bound constants over captured polygon/vertex buffers. No force-PC instruction entry; preceding CPU/GPU producers not rerun after patches.')
                projection_stem=f'case-{original["original_projection_case"]:02d}';device.seed((projection/f'{projection_stem}-before-RAM.bin').read_bytes(),1);initial=(projection/f'{projection_stem}-before-GPU-state.bin').read_bytes();buf=c.create_string_buffer(initial);assert core.GPUStateLoad(buf)==len(initial);assert lib.lab_resident_prepare(original['occurrence'])==0;resident_fixture_inputs.apply(device,core,inputs)
                before=device.ram();before_raw,before_state=gpu_state(core);before_blitter=blitter_registers(core)
                for suffix,data in [('before-RAM',before),('before-GPU-state',before_raw),('before-blitter-registers',before_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
                status=lib.lab_resident_original();after=device.ram();after_raw,after_state=gpu_state(core);after_blitter=blitter_registers(core);steps=[lib.lab_resident_PC(i)for i in range(lib.lab_resident_steps())];events=[]
                for suffix,data in [('after-RAM',after),('after-GPU-state',after_raw),('after-blitter-registers',after_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
                for i in range(lib.lab_movement_event_count()):
                    ev=(c.c_uint32*5)();assert lib.lab_movement_event(i,ev)==0
                    if ev[1]==3 and ev[0]in [11,12]:events.append(list(ev))
                assert status==0 and after_state['pc']==0xf031be,(original['case'],variant,status)
                rows.append(dict(case=number,original_projection_case=original['original_projection_case'],occurrence=original['occurrence'],declared_variant=True,declared_inputs=inputs,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,events=events,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw),before_blitter_registers_sha256=sha(before_blitter),after_blitter_registers_sha256=sha(after_blitter)));save(out/'cases.json',rows);print(json.dumps(dict(case=number,variant=variant,steps=len(steps))),flush=True)
        covered=set()
        for row in rows:
            for pc in row['steps']:
                assert pc in decoded,hex(pc);covered.add(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:covered.add(pc+2)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_resident_and_declared_variants_captured_C_unverified',directory=str(out),cases=len(rows),natural_entry_cases=len(natural),declared_variant_cases=len(rows)-len(natural),source_instruction_coverage=[len(covered),len(decoded)],uncovered_instructions=[decoded[pc]for pc in sorted(set(decoded)-covered)],source_projection_directory=str(projection),source_natural_probe_directory=str(base),probe_source_sha256=sha(Path(__file__).read_bytes()),fixture_adapter_sha256=sha(Path(resident_fixture_inputs.__file__).read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-resident-probe.dylib').read_bytes()),scope='28natural entries plus finite declared flat-material/color/viewport-constant variants. Identical original GPU preparation before each patched entry; no force-PC execution or producer rerun after patches. Synchronous shared pinned fast blitter; original GPU sole oracle, native watch readvalues placeholders. Recipient dispatcher not included.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-resident-original-probes.json',report);print(json.dumps(dict(cases=len(rows),coverage=report['source_instruction_coverage'],directory=str(out))))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
