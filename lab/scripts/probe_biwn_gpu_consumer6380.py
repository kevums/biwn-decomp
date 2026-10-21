"""Original6380 entry after real projection and original setup/dispatcher.

Four natural captures, plus declared finite list/material/seed variants.
Stop at a source dispatcher/resident handoff, without executing the recipient.
"""
import ctypes as c, hashlib, json, random, struct
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;save=frame.save;read=lambda p:json.loads(p.read_text());sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    original=read(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json');base=Path(original['directory'])
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping=read(session/'gpu-render-6380-overlay/initial-linear-decode.json');decoded={r['address']:r for r in mapping['rows'] if r['address']<0xf03312};assert len(decoded)==67
    out=session/'gpu-render-6380-overlay/original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-consumer6380-probe.dylib');lib=device.lib;core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    for name in ['lab_consumer6380_prepare','lab_consumer6380_original']:getattr(lib,name).restype=c.c_int
    lib.lab_consumer6380_steps.restype=c.c_uint32;lib.lab_consumer6380_PC.argtypes=[c.c_uint32];lib.lab_consumer6380_PC.restype=c.c_uint32
    lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    prepared=[];rows=[];covered=set()
    def capture(number,memory,raw,fixture):
        stem=f'case-{number:02d}';device.seed(memory,1);buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw)
        before=device.ram();before_raw,before_state=gpu_state(core)
        assert before_state['pc']==0xf03240 and before_state['active_bank']==0
        for suffix,data in [('before-RAM',before),('before-GPU-state',before_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
        status=lib.lab_consumer6380_original();steps=[lib.lab_consumer6380_PC(i)for i in range(lib.lab_consumer6380_steps())]
        after=device.ram();after_raw,after_state=gpu_state(core)
        for suffix,data in [('after-RAM',after),('after-GPU-state',after_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
        events=[]
        for i in range(lib.lab_movement_event_count()):
            ev=(c.c_uint32*5)();assert lib.lab_movement_event(i,ev)==0
            if ev[1]==3 and ev[0]in [11,12]:events.append(list(ev))
        for pc in steps:
            assert pc in decoded,hex(pc);covered.add(pc)
            if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:covered.add(pc+2)
        row=dict(case=number,fixture=fixture,status=status,before_GPU=before_state,after_GPU=after_state,steps=steps,events=events,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw),handoff_PC=hex(after_state['pc']),list_head_before=int.from_bytes(before[0x10a684:0x10a688],'big'),list_head_after=int.from_bytes(after[0x10a684:0x10a688],'big'),queued_command=hex(int.from_bytes(after_raw[0x204:0x208],'big')))
        assert status==0 and after_state['pc']in [0xf031be,0xf03440,0xf03ca0],row
        rows.append(row);save(out/'cases.json',rows)
    try:
        for index in range(4):
            save(out/'status.json',dict(status='running_prepare',case=index));stem=f'case-{index:02d}'
            device.seed((base/f'{stem}-before-RAM.bin').read_bytes(),1);raw=(base/f'{stem}-before-GPU-state.bin').read_bytes();buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw)
            assert lib.lab_consumer6380_prepare()==0
            memory=device.ram();raw,_=gpu_state(core);prepared.append((memory,raw))
            capture(index,memory,raw,dict(natural_entry=True,original_projection_case=index,scope='Original57setup and resident dispatcher prepare actual first6380 entry; blitter reset on replay, consumer performs no blitter access.'))
        modes=['empty','disabled','resident7','resident8','mapped0','mapped1','mapped2','unmapped']
        for i in range(32):
            number=i+4;save(out/'status.json',dict(status='running_declared_variant',case=number))
            memory,raw=prepared[i%4];memory=bytearray(memory);raw=bytearray(raw);mode=modes[i%len(modes)];head=1+(i//8)%3;record=0x47b88+head*64
            memory[0x10a684:0x10a688]=(0 if mode=='empty'else head).to_bytes(4,'big')
            material={'empty':0,'disabled':65535,'resident7':7,'resident8':8,'mapped0':0,'mapped1':1,'mapped2':2,'unmapped':3}[mode]
            memory[record+24:record+26]=b'\0\0';memory[record+32:record+34]=material.to_bytes(2,'big')
            if mode=='unmapped':memory[0x3bc80+material*4:0x3bc84+material*4]=b'\0'*4
            randomizer=random.Random(6380+i);struct.pack_into('=64I',raw,4139,*[randomizer.getrandbits(32)for _ in range(64)]);raw[4136:4139]=bytes([(i>>j)&1 for j in range(3)])
            capture(number,bytes(memory),bytes(raw),dict(natural_entry=False,base_original_projection_case=i%4,declared_mode=mode,declared_head=head,declared_material=material,declared_next_index=0,declared_register_seed=6380+i,table_entry_forced_zero=mode=='unmapped',scope='Controlled finite material/list/flags/register variant, not a rerun of CPU scene generation.'))
        missing=sorted(set(decoded)-covered);assert not missing,[hex(pc)for pc in missing]
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_GPU6380_all67_observed_C_unverified',directory=str(out),cases=len(rows),natural_entry_cases=4,declared_variant_cases=32,source_instruction_coverage=[len(covered),67],handoff_PCs=sorted({r['handoff_PC']for r in rows}),source_payload_sha256=mapping['payload_SHA256'],original_projection_directory=str(base),probe_source_sha256=sha(Path(__file__).read_bytes()),bridge_source_sha256=sha((ROOT/'scripts/biwn_consumer6380_probe_bridge.c').read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-consumer6380-probe.dylib').read_bytes()),full_draw_C=False,scope='Source consumer only, ending at dispatcher or resident program entry after mandatory delays. Original preparation precedes captured entry. Recipient renderer/dispatcher not included in comparison. Native watch read values are placeholders; exact read shape and actual stores retained.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-consumer6380-original-probes.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
