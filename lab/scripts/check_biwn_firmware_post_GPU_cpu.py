"""Compare the live CPU copy/wait and every first instruction checkpoint."""
import ctypes as c,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_firmware_relocation_cpu as relocation
import check_biwn_media_setup_cpu as media
import observe_biwn_relocated_firmware as observation
ROOT=media.ROOT;save=media.save;sha=media.sha

def main():
    native=json.loads((ROOT/'verification/BIWN-relocated-firmware-observation/20261015T032537.188491Z/report.json').read_text())
    translated=json.loads((ROOT/'verification/BIWN-relocated-firmware-observation/20261015T032742.614404Z/report.json').read_text())
    left=Path(native['directory']);right=Path(translated['directory'])
    assert native['emulator_shutdown_completed'] and translated['emulator_shutdown_completed']
    a=native['CPU_continuation_after_GPU'];b=translated['CPU_continuation_after_GPU']
    assert not a['source_C_verified'] and b['source_C_verified'] and b['original_CPU_instructions_on_C_path']==0
    assert not b['CPU_reseeded'] and not b['initial_CPU_boundary_hostloaded'] and not b['source_C_mirror_used_core_pulse_reset']
    for key in ['steps','initial_CPU','final_CPU','PC_trace_sha256','RAM_sha256','hardware']:assert a[key]==b[key],key
    assert {(r['address'],r['bytes'],r['count'])for r in a['visited_instructions']}=={(r['address'],r['bytes'],r['count'])for r in b['visited_instructions']}
    for name in ['CPU-before-post-GPU.bin','RAM-before-post-GPU.bin','RAM-after-GPU-CPU.bin']:assert (left/name).read_bytes()==(right/name).read_bytes(),name
    assert a['steps']==433 and len(a['visited_instructions'])==15
    for x,y in zip(native['further_explicit_video_events'],translated['further_explicit_video_events']):
        for key in ['steps','CPU_before','CPU_exception_entry','CPU_after','video_counter_before','video_counter_after','RAM_sha256','hardware','PC_trace_sha256','visited_instructions']:assert x[key]==y[key],(x['number'],key)
    out=ROOT/'verification/BIWN-firmware-post-GPU-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    preceding=json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text());runtime=relocation.Runtime(Path(preceding['directory'])/'libfirmware-relocation.dylib',[]);closed=False
    machine=(left/'machine-before-post-GPU.bin').read_bytes();RAM=(left/'RAM-before-post-GPU.bin').read_bytes();initial=(left/'CPU-before-post-GPU.bin').read_bytes()
    runtime.core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];runtime.core.retro_unserialize.restype=c.c_bool
    if hasattr(runtime.core,'BlitterStateSave'):
        runtime.core.BlitterStateSave.argtypes=[c.c_void_p];runtime.core.BlitterStateSave.restype=c.c_size_t;runtime.savers['Blitter']=runtime.core.BlitterStateSave
    def reset():
        runtime.reset(RAM,0);assert runtime.core.retro_unserialize(c.create_string_buffer(machine),len(machine));assert bytes(runtime.cpu())==initial and runtime.device.ram()==RAM
    try:
        reset();frames=[];coverage=set();trace=hashlib.sha256();counts={}
        for step in range(433):
            pc=runtime.cpu().pc;new=pc not in coverage;coverage.add(pc);trace.update(pc.to_bytes(4,'big'));counts[pc]=counts.get(pc,0)+1;runtime.core.m68k_execute(1)
            if new or (step+1)%100==0 or step==432:frames.append(dict(steps=step+1,CPU=bytes(runtime.cpu()).hex(),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],PC_trace_sha256=trace.hexdigest()))
        assert trace.hexdigest()==a['PC_trace_sha256']
        save(out/'native-checkpoints.json',frames);reset();state=media.CPU.from_buffer_copy(initial);Ctrace=hashlib.sha256();Ccounts={};done=0
        def observed(_,bus,pointer,pc):Ctrace.update(pc.to_bytes(4,'big'));Ccounts[pc]=Ccounts.get(pc,0)+1;return 0
        # Compile once, then keep the fixed library loaded for all chunks.
        status,state=observation.run_firmware_post_GPU_CPU_C(runtime,out,state,frames[0]['steps'],observed);assert status==4
        fn=c.CDLL(str(out/'libfirmware-post-GPU-CPU.dylib')).biwn_firmware_post_GPU_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8]
        def reader(width):return lambda _,address,value:(value.__setitem__(0,runtime.read(address,width)),0)[1]
        def writer(width):return lambda _,address,value:(runtime.write(address,width,value),0)[1]
        callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        bus=media.Bus(*callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0);service=media.world_cpu.SERVICE(observed)
        comparisons=[]
        for index,frame in enumerate(frames):
            if index:status=fn(c.byref(bus),c.byref(state),callbacks[5],service,None,frame['steps']-done,0);assert status==4
            assert bytes(runtime.cpu())==initial
            assert bytes(state).hex()==frame['CPU'] and sha(runtime.device.ram())==frame['RAM_sha256'] and runtime.snapshot()['hardware']==frame['hardware'] and Ctrace.hexdigest()==frame['PC_trace_sha256'],frame['steps']
            comparisons.append(dict(steps=frame['steps'],match=True));done=frame['steps']
        assert Ccounts==counts and len(coverage)==15
        # Negative source guard: reject an unsupported first instruction without fallback.
        reset();runtime.write(0x50292,2,runtime.read(0x50292,2)^1);bad_RAM=runtime.device.ram();bad=media.CPU.from_buffer_copy(initial);before=bytes(bad)
        guard=fn(c.byref(bus),c.byref(bad),callbacks[5],service,None,433,0)
        assert guard==7 and bytes(bad)==before and runtime.device.ram()==bad_RAM and bytes(runtime.cpu())==initial
        save(out/'comparisons.json',comparisons);runtime.oracle.close();closed=True
        source=ROOT/'projects/black-ice-white-noise/restoration'
        report=dict(status='live_and_standalone_post_GPU_CPU_copy_wait_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),native_directory=str(left),C_directory=str(right),source_instruction_coverage=[15,15],executed_instructions=433,checkpoints=len(frames),full_CPU_both_stack_banks_private2MBRAM_GPU_DSP_TOM_JERRY_DAC_CDROM_extension_PC_trace_counts_match=True,compared_peripheral_fields=list(a['hardware']),private_Blitter_state_compared='Blitter'in a['hardware'],source_copy_bytes=228,source_copy_from='0x502aa',source_copy_to='0x1000',natural_source_JMP_to_1000=True,wait_counter_delta=5,final_PC='0x100c',initial_CPU_boundary_hostloaded_in_live_run=False,source_C_register_export_used_core_pulse_reset=False,original_CPU_instructions_on_C_path=0,guard_return_code=7,guard_CPU_RAM_unchanged=True,guard_no_original_fallback=True,further_original_CPU_video_event_comparisons=min(len(native['further_explicit_video_events']),len(translated['further_explicit_video_events'])),further_video_events_C_verified=False,emulator_shutdown_completed=True,source_sha256={name:sha((source/name).read_bytes())for name in ['biwn_firmware_post_GPU_cpu.c','biwn_firmware_post_GPU_cpu.h']},test_sha256=sha(Path(__file__).read_bytes()),implementation_authorship='coordinator',local_model_authored_bodies_added=0,main_firmware_CPU_complete=False,physical_global_schedule_verified=False,disc_attached=False,whole_game_complete=False,limits=['Fifteen observed instructions and first 433 steps, plus first-use/periodic checkpoints. Delta-five fallthrough and further video handlers are original CPU discovery, not part of this C proof.', 'Standalone restores a captured live incoming machine for independent comparison; the separate live C run uses the natural preceding CPU/C DSP/C videoIRQ/C GPU sequence with no loaded CPU boundary or pulse reset at the C export.', 'Shared pinned peripheral bus, logical CPU state export and explicit video events remain providers. No global-clock/prefetch-bus-cycle/real disc loading/full boot/playability claim.'])
        save(out/'report.json',report);save(ROOT/'verification/firmware-post-GPU-CPU-checks.json',report);print(json.dumps({k:report[k]for k in ['status','source_instruction_coverage','executed_instructions','checkpoints','guard_return_code','whole_game_complete']}))
    finally:
        if not closed:runtime.oracle.close()

if __name__=='__main__':main()
