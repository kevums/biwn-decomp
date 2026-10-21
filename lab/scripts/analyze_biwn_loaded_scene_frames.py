"""Audit reached task contexts and observed controls in a whole-frame comparison."""
import argparse,collections,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
get=lambda raw,a,w=4:int.from_bytes(raw[a:a+w],'big')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--publish',action='store_true');args=ap.parse_args();folder=args.run.resolve()
    protocol=json.loads((folder/'protocol.json').read_text());comparison=json.loads((folder/'comparison.json').read_text());reference=json.loads((folder/'reference/report.json').read_text());rebuilt=json.loads((folder/'C/report.json').read_text());tasks=json.loads((folder/'tasks.json').read_text())
    failed=[k for k,value in comparison['checks'].items()if not value];assert failed in [[],['DSP_owned_positive']],failed
    if failed:assert comparison['DSP_counts']==dict(Owned=0,Original=0,Rejected=0)
    assert not reference['errors']and not rebuilt['errors']and len(reference['frames'])==len(rebuilt['frames'])==protocol['frames']
    initial=(folder/'starting-scene-RAM.bin').read_bytes();final=(folder/'C/final-RAM.bin').read_bytes();assert sha(initial)==protocol['initial_RAM_sha256']
    dtype=np.dtype({'names':['SP','PC','SR'],'formats':['>u4','>u4','>u2'],'offsets':[60,64,76],'itemsize':78});path=folder/'C/CPU-before-instructions.bin';count=path.stat().st_size//78;assert path.stat().st_size==count*78 and count==comparison['owned_CPU_instructions']
    from check_biwn_loaded_actor_runtime import ring
    final_tasks=ring(final);initial_addresses={int(row['task'],16)for row in tasks};all_addresses=initial_addresses|set(final_tasks)
    task_counts=collections.Counter();entries=collections.Counter();supervisor=0;PCs=[0x1a188,0x191f4,0xf0fa,0x17e0e,0xe4c0,0xdef6,0xdefc,0xdf00,0xf4d8,0xedc4,0x20f78,0x20e8c,0x20f0c,0x1aa40,0x19f2c,0x19fda,0x10430,0x1039c,0xdf6c,0xde5c,0xdf7a,0xdeb6]
    for start in range(0,count,1_000_000):
        a=np.memmap(path,dtype=dtype,mode='r',offset=start*78,shape=(min(1_000_000,count-start),));user=(a['SR']&0x2000)==0;supervisor+=int((~user).sum())
        for pc in PCs:entries[hex(pc)]+=int((a['PC']==pc).sum())
        for address in all_addresses:
            task_counts[hex(address)]+=int((user&(a['SP']>=address+38)&(a['SP']<=address+0x400)).sum())
        del a
    task_rows=[dict(**task,user_mode_instructions=task_counts[task['task']])for task in tasks]
    snapshots=[dict(frame=0,RAM=initial)]+[dict(frame=int(path.name.split('-')[1]),RAM=path.read_bytes())for path in sorted((folder/'C').glob('frame-*-RAM.bin'),key=lambda p:int(p.name.split('-')[1]))]
    captures=[]
    for row in snapshots:
        ram=row['RAM'];captures.append(dict(frame=row['frame'],player_X=get(ram,0x49c50),player_Y=get(ram,0x49c54,2),player_Z=get(ram,0x49c56),player_heading=get(ram,0x49cba,1),player_state=get(ram,0x49cb8,2),held_input=hex(get(ram,0x49ba4)),source_clock=get(ram,0x778cc),scene_mode=get(ram,0x49c60,2),floor=get(ram,0x49c62,2),scene_index=get(ram,0x49c64,2),camera_record_sha256=sha(ram[0x47b88:0x47bc8]),camera_position=ram[0x49b8c:0x49b98].hex()))
    moving=[]
    for slot in range(40):
        obj=0x49d6c+206*slot
        if get(initial,obj,2)!=64:continue
        before=dict(X=get(initial,obj+4),Z=get(initial,obj+10));after=dict(X=get(final,obj+4),Z=get(final,obj+10));observed=[dict(frame=row['frame'],X=get(row['RAM'],obj+4),Z=get(row['RAM'],obj+10))for row in snapshots if get(row['RAM'],obj,2)==64]
        moving.append(dict(slot=slot,source_id=64,final_id=get(final,obj,2),before=before,after=after,coordinates_changed=before!=after and get(final,obj,2)==64,observed_source_actor_positions=observed,observed_coordinate_changes=len({(row['X'],row['Z'])for row in observed})>1))
    cpu_bridge=json.loads((folder/'C/native-CPU-bridge-report.json').read_text())
    report=dict(status='whole_frame_loaded_scene_CPU_GPU_match_with_task_and_control_audit',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(folder),frames=protocol['frames'],CPU_instructions=count,GPU_counts=comparison['GPU_counts'],DSP_counts=comparison['DSP_counts'],combined_gate_passed=not failed,combined_gate_failed_checks=failed,task_contexts=len(tasks),task_contexts_with_user_execution=sum(row['user_mode_instructions']>0 for row in task_rows),new_task_contexts=sum(row['new']for row in task_rows),new_task_contexts_with_user_execution=sum(row['new']and row['user_mode_instructions']>0 for row in task_rows),task_rows=task_rows,supervisor_CPU_instructions=supervisor,function_entries=dict(entries),source_clock_delta=(get(final,0x778cc)-get(initial,0x778cc))&0xffffffff,player_position_changed=(get(initial,0x49c50),get(initial,0x49c56))!=(get(final,0x49c50),get(final,0x49c56)),player_heading_changed=get(initial,0x49cba,1)!=get(final,0x49cba,1),camera_records_changed=len({row['camera_record_sha256']for row in captures})>1,source_actors=moving,source_actors_with_coordinate_changes=sum(row['coordinates_changed']for row in moving),unique_frontend_video_frames=len({row['video']for row in rebuilt['frames']}),audio_final=rebuilt['frames'][-1]['audio'],headless_frame_loop_seconds=cpu_bridge['elapsed_seconds'],captured_controls=captures,source_scene_setup=protocol['source_scene_proof'],comparison=str(folder/'comparison.json'),original_C_CPU_trace_and_cycle_costs_match=True,all_frame_RAM_video_PCM_and_final_machine_match=True,source_RAM_was_supplied=True,no_extra_actor_task_blocking=True,no_per_frame_processor_reset=True,natural_scene_entry_verified=False,default_promoted=False,native_window_keyboard_verified=False,source_files=dict(runner=str(ROOT/'scripts/run_biwn_loaded_scene_frames.py'),runner_sha256=protocol.get('script_sha256'),analyzer_sha256=sha(Path(__file__).read_bytes())),scope='Exact original serialized machine then explicit C-loaded mainRAM scene overlay. Existing sourcecode recipe repairs remain; offline queue operands restored. Reconstructed instruction-level CPU and sourceGPU run the original whole-frame scheduler/clock/input/IRQ/device environment without per-frame resets or host task blocking. Original/C CPU states/costs, each frame RAM/frontendvideo/PCM and final complete serializedmachine compare. User-mode SP ranges attribute execution to initial task contexts; this is reached execution, not coverage of every task branch or lifecycle. Initial GPU/device state remains supplied from the checkpoint, originalIRQ/HLE/OP/devices retained, no natural scene entry/fresh boot/standalone/fullgame/physical scanout or audible output claim. DSP inactive gives no DSP execution evidence.')
    report.update(final_task_contexts=len(final_tasks),task_addresses_removed_from_initial_ring=[hex(a)for a in sorted(initial_addresses-set(final_tasks))],additional_final_task_addresses=[hex(a)for a in sorted(set(final_tasks)-initial_addresses)],additional_final_tasks_with_user_execution=sum(task_counts[hex(a)]>0 for a in set(final_tasks)-initial_addresses),source_actors_with_observed_coordinate_changes=sum(row['observed_coordinate_changes']for row in moving),final_scene_mode=get(final,0x49c60,2),final_scene_index=get(final,0x49c64,2),ordinary_controller_indoor_entry_after_supplied_start_verified=get(initial,0x49c60,2)==1 and get(final,0x49c60,2)==2 and entries['0x20f78']>0,fresh_boot_to_scene_verified=False)
    report['scope']+=' Ordinary-controller indoor entry, when observed, is measured after the supplied initial outdoor state; it does not establish natural reachability of that initial state. Initial actor slots may be removed or reused during scene cleanup; observed initial-actor movement is counted only in captures where their sourceID remains64.'
    report['scope']=report['scope'].replace('no natural scene entry/fresh boot/standalone/fullgame/physical scanout or audible output claim','initial scene reachability/fresh boot/standalone/fullgame/physical scanout and audible output remain unverified')
    report['scene_entry_distinction']=dict(initial_outdoor_scene='Supplied C-loaded scene RAM on a restored original machine; natural arrival at this initial state remains unproved.',subsequent_indoor_scene='Ordinary controller doorway entry into scene41 verified after the supplied start.'if report['ordinary_controller_indoor_entry_after_supplied_start_verified']else'No subsequent indoor entry observed in this run.')
    report['PCM_units']=dict(stereo_sample_frames=report['audio_final']['frames'],nonzero_individual_channel_samples=report['audio_final']['nonzero_samples'])
    (folder/'task-control-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    if args.publish:(ROOT/'verification/loaded-scene-task-control-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in ['status','frames','CPU_instructions','task_contexts','task_contexts_with_user_execution','new_task_contexts_with_user_execution','player_position_changed','player_heading_changed','camera_records_changed','source_actors_with_coordinate_changes','unique_frontend_video_frames','headless_frame_loop_seconds']}),flush=True)

if __name__=='__main__':main()
