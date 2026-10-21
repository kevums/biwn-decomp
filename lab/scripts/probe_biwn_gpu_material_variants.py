"""Declared finite descriptor variants over retained original material entries."""
import ctypes as c,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);proof=read(ROOT/'verification/biwn-gpu-material-original-probes.json');base=Path(proof['directory']);assert proof.get('declared_variant_cases',0)==0
    out=session/'gpu-material-variant-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=read(base/'cases.json')
    for row in rows:
        stem=f'case-{row["case"]:02d}'
        for suffix in ['before-RAM','before-GPU-state','after-RAM','after-GPU-state']:os.link(base/f'{stem}-{suffix}.bin',out/f'{stem}-{suffix}.bin')
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-material-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0;lib.lab_material_original.restype=c.c_int;lib.lab_material_steps.restype=c.c_uint32;lib.lab_material_PC.argtypes=[c.c_uint32];lib.lab_material_PC.restype=c.c_uint32;lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    decoded={}
    for h,end in [('0x6460',0xf033a4),('0x6720',0xf0335a),('0x69a0',0xf0335a)]:decoded[h]={r['address']:r for r in read(session/f'gpu-render-{h[2:]}-overlay/initial-linear-decode.json')['rows']if r['address']<end}
    natural=list(rows)
    try:
        for header in decoded:
            original=next(row for row in natural if row['CPU_header']==header);original_stem=f'case-{original["case"]:02d}'
            for variant in range(8):
                number=len(rows);stem=f'case-{number:02d}';save(out/'status.json',dict(status='running',case=number,header=header))
                memory=bytearray((base/f'{original_stem}-before-RAM.bin').read_bytes());raw=(base/f'{original_stem}-before-GPU-state.bin').read_bytes();record=original['before_GPU']['registers'][0][24]
                def get(a,w):return int.from_bytes(memory[a:a+w],'big')
                def put(a,w,v):assert 0<=a<=0x200000-w;memory[a:a+w]=v.to_bytes(w,'big')
                model=get(record+60,4);index=get(record+34,2);descriptor=get(model+8,4)+index*20;assert 0<=index<256 and 0<=descriptor<0x1fffec,(index,hex(descriptor))
                declared=dict(base_natural_case=original['case'],record=hex(record),model=hex(model),descriptor_index=index,descriptor_address=hex(descriptor))
                if header=='0x6460':
                    texture=82+(variant%4);put(descriptor,2,texture);put(descriptor+16,2,2+variant%2);put(descriptor+18,2,3)
                    declared.update(texture_ID=texture,grid_width=2+variant%2,grid_height=3)
                else:
                    offset=6 if header=='0x6720'else 8;texture_index=get(descriptor+offset,2)&0xfff;texture=get(model+12,4)+texture_index*28;flag_offset=14 if header=='0x6720'else 16
                    width=2+variant%2;height=[1,5,6,7][variant%4];put(descriptor+18,2,width);put(texture+8,2,height);put(texture+flag_offset,1,index if variant<4 else(index+1)&255);put(texture+flag_offset+1,1,variant%2)
                    declared.update(texture_info_address=hex(texture),grid_width=width,texture_height=height,matching_material_byte=variant<4,special_column=variant%2)
                device.seed(bytes(memory),1);buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw);before=device.ram();before_raw,before_state=gpu_state(core)
                for suffix,data in [('before-RAM',before),('before-GPU-state',before_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
                status=lib.lab_material_original();after=device.ram();after_raw,after_state=gpu_state(core);steps=[lib.lab_material_PC(i)for i in range(lib.lab_material_steps())]
                for suffix,data in [('after-RAM',after),('after-GPU-state',after_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
                events=[]
                for i in range(lib.lab_movement_event_count()):
                    ev=(c.c_uint32*5)();assert lib.lab_movement_event(i,ev)==0
                    if ev[1]==3 and ev[0]in [11,12]:events.append(list(ev))
                assert status==0 and after_state['pc']==0xf03440,(header,variant,status)
                rows.append(dict(case=number,CPU_header=header,declared_variant=True,declared_inputs=declared,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,events=events,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw)));save(out/'cases.json',rows)
        coverage={h:set()for h in decoded}
        for row in rows:
            h=row['CPU_header']
            for pc in row['steps']:
                assert pc in decoded[h],(h,hex(pc));coverage[h].add(pc)
                if int(decoded[h][pc]['bytes'][:4],16)>>10 in [52,53]:coverage[h].add(pc+2)
        programs={h:dict(cases=sum(row['CPU_header']==h for row in rows),source_instruction_coverage=[len(coverage[h]),len(decoded[h])],uncovered_instructions=[decoded[h][pc]for pc in sorted(set(decoded[h])-coverage[h])])for h in decoded}
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_material_entries_and_declared_descriptor_variants_captured_C_unverified',directory=str(out),cases=len(rows),natural_entry_cases=len(natural),declared_variant_cases=len(rows)-len(natural),programs=programs,source_natural_probe_directory=str(base),probe_source_sha256=sha(Path(__file__).read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-material-probe.dylib').read_bytes()),full_renderer_C=False,scope='21natural entry inputs plus24declared finite descriptor/texture variants. CPU and preceding GPU chain are not rerun for variant inputs. Header-sized source unchanged; no force-PC coverage or recipient resident execution. Pinned GPU is sole oracle; native watch read values placeholders.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-material-original-probes.json',report);print(json.dumps(dict(cases=len(rows),programs={h:{k:v for k,v in p.items()if k!='uncovered_instructions'}for h,p in programs.items()})))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
