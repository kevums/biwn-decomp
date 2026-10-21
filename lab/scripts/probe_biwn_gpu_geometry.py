"""Observe originalGPU4D80 over checked captured scene RAM, no C claim."""
import ctypes as c,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
ROOT=frame.ROOT
read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,indent=2)+'\n')
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    folder=session/'gpu-geometry-overlay';mapping=read(folder/'initial-linear-decode.json');decoded={r['address']:r for r in mapping['rows']}
    out=folder/'original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    capture=ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z'
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-geometry-probe.dylib');lib=device.lib
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    lib.lab_geometry_original.argtypes=[c.c_uint32];lib.lab_geometry_original.restype=c.c_int
    lib.lab_geometry_steps.restype=c.c_uint32;lib.lab_geometry_PC.argtypes=[c.c_uint32];lib.lab_geometry_PC.restype=c.c_uint32;lib.lab_geometry_final_PC.restype=c.c_uint32
    lib.lab_geometry_gpu_RAM.restype=c.c_void_p;lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    lib.lab_movement_register.argtypes=[c.c_uint,c.c_uint];lib.lab_movement_register.restype=c.c_uint32
    rows=[];direct=set();derived=set()
    try:
        for i,path in enumerate(sorted(capture.glob('startup-C-*.bin'))):
            save(out/'status.json',dict(status='running',case=i));ram=path.read_bytes();metadata=read(capture/f'startup-capture-{path.stem.split("-")[-1]}.json');assert hashlib.sha256(ram).hexdigest()==metadata['C_RAM_sha256']
            assert hashlib.sha256(ram[0x4d88:0x4d88+1360]).hexdigest()==mapping['payload_sha256']
            device.seed(ram,0);status=lib.lab_geometry_original(0x4d800000+i);steps=[lib.lab_geometry_PC(j)for j in range(lib.lab_geometry_steps())]
            events=[]
            for j in range(lib.lab_movement_event_count()):
                event=(c.c_uint32*5)();assert lib.lab_movement_event(j,event)==0
                if event[1]==3 and event[0]in [11,12]:events.append(list(event))
            after=device.ram();(out/f'case-{i:02d}-RAM.bin').write_bytes(after);(out/f'case-{i:02d}-GPU-RAM.bin').write_bytes(c.string_at(lib.lab_geometry_gpu_RAM(),4096))
            direct.update(steps)
            for pc in steps:
                assert pc in decoded,hex(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:derived.add(pc+2)
            row=dict(case=i,capture=str(path),capture_sha256=metadata['C_RAM_sha256'],status=status,final_GPU_PC=hex(lib.lab_geometry_final_PC()),steps=steps,register_banks=[[lib.lab_movement_register(bank,j)for j in range(32)]for bank in range(2)],events=events,RAM_sha256=hashlib.sha256(after).hexdigest(),changed_RAM_bytes=sum(a!=b for a,b in zip(ram,after)),first_changed_addresses=[hex(j)for j,(a,b)in enumerate(zip(ram,after))if a!=b][:40],device=device.stats())
            rows.append(row);save(out/'cases.json',rows)
            assert status==0 and row['final_GPU_PC']=='0xf031be',row
        covered=direct|derived;candidate={pc for pc in decoded if pc<0xf03634};assert covered<=candidate,[hex(pc)for pc in covered-candidate]
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='four_originalGPU4D80_captured_scene_probes_returned_C_unimplemented',directory=str(out),cases=len(rows),payload_bytes=1360,payload_sha256=mapping['payload_sha256'],candidate_code_instructions=len(candidate),direct_PC_addresses=len(direct),derived_mandatory_delay_addresses=len(derived-direct),observed_instruction_addresses=len(covered),unobserved_candidate_addresses=[hex(pc)for pc in sorted(candidate-covered)],C_geometry_reconstructed=False,full_viewport_proved=False,scope='Original GPU overlay directly primed atF03240 with sourceE0A6mailbox arguments and supplied GPU register seeds, captured assisted-startup RAM. Not original dispatcher/CPU scene execution or reconstructed C transform. Native trace read-value fields may be placeholders; retained raw events and actual writes/RAM. Direct PC samples omit delay slots; mandatory JR/JUMP slots derived separately. No gameframes/physicaltiming.',probe_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),bridge_source_sha256=hashlib.sha256((ROOT/'scripts/biwn_geometry_probe_bridge.c').read_bytes()).hexdigest(),probe_library_sha256=hashlib.sha256((ROOT/'tools/libbiwn-geometry-probe.dylib').read_bytes()).hexdigest())
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(folder/'original-probe-current.json',report);save(ROOT/'verification/biwn-gpu-geometry-original-probes.json',report);print(json.dumps({k:v for k,v in report.items()if k!='unobserved_candidate_addresses'}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
