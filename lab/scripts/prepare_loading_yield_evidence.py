"""Publish real loader scheduler suspensions and the explicit device/stack scope."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';linked=read(ROOT/'verification/biwn-disc-world-loading-yields-checks.json');old=read(ROOT/'verification/biwn-disc-world-cd-wrappers-checks.json')
    assert linked['cases']==16 and linked['world_updates']==720 and linked['actor_iterations']==2048 and linked['task_handoffs']==5136
    assert linked['loader_inner_yields']==linked['loading_completion_event_count']==32 and linked['dispatcher_inner_yields']==272
    assert linked['loading_task_context_switches_verified']and linked['loading_completion_adapter_removed']and linked['resource_IO_adapter_call_counts']=={'0x303c':32,'0x3042':32}
    assert linked['loaded_payload_bytes']==3080416 and linked['disc_transfer_requests']==linked['disc_transfer_completions']==32
    for k,v in old.items():linked.setdefault(k,v)
    rows=read(Path(linked['directory'])/'fixtures.json');unique={(p['tag'],p['bytes'],p['sha256'])for p in linked['loaded_payloads']};assert len(unique)==3
    linked['loaded_payload_unique']=[{'tag':tag,'bytes':size,'sha256':h}for tag,size,h in sorted(unique)]
    linked['stack_correction_detail']={'first_detected_payload_mismatch_source_address':'0x1cfffa','TRAP_exception_frame_begins_at':'0x1cfffa','total_changed_byte_count':'not measured; a first mismatching address does not establish that only one byte was corrupted','corrected_supplied_SSP':'0x1ff000','scope':'Test-fixture stack placement, not a repaired game bug or verified original boot stack.'}
    def world_calls(target):return sum(sum(c['target']==target for c in r['rebuilt']['world_calls'])for r in rows)
    linked.update(dispatcher_calls=world_calls(0x191f4),camera_calls=world_calls(0xf0fa),targeting_calls=world_calls(0x20820),animation_request_calls=sum(len(r['rebuilt']['animation_requests'])for r in rows),dispatcher_nested_helper_call_count=sum(len(r['rebuilt']['dispatcher_helper_calls'])for r in rows),original_GPU_submit_entries=sum(r['original']['steps'].count(0xe220)for r in rows),cases_with_position_change=sum(r['positions_changed']for r in rows))
    assert linked['dispatcher_calls']==linked['camera_calls']==linked['targeting_calls']==720 and linked['animation_request_calls']==160
    assert all(p['matches_preserved_normalized_disc_payload']for p in linked['loaded_payloads'])
    for r in rows:
        assert r['supplied_initial_SSP']=='0x1ff000'
        assert len(r['rebuilt']['loading_yield_calls'])==len(r['rebuilt']['loading_completion_events'])==len(r['rebuilt']['disc_requests'])==2
        assert all(e['context']!=0xc2128 for e in r['rebuilt']['loading_completion_events'])
        assert all(request['destination_end']<=0x1fe000 for request in r['rebuilt']['disc_requests'])
        assert r['original']['steps'].count(0xdf8c)==r['original']['steps'].count(0xdf9c)==0
    save(ROOT/'verification/biwn-disc-world-loading-yields-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    proof_names=['biwn-disc-world-loading-yields-checks.json','biwn-input-dispatch-cpu-checks.json','biwn-input-dispatch-yield-checks.json']
    for name in proof_names:
        proof=read(ROOT/'verification'/name);folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snapshot=folder/'publication-snapshot';snapshot.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_input_dispatch_cpu.py','check_biwn_input_dispatch_cpu.py','check_biwn_input_dispatch_yield.py','check_biwn_disc_world_yields.py','check_biwn_disc_scene_actors.py','biwn_disc_backend.py']]
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
        for p in files:shutil.copy2(p,snapshot/p.name)
        save(snapshot/'manifest.json',{'recorded_at':now,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    cpu=read(ROOT/'verification/biwn-input-dispatch-cpu-checks.json');yielded=read(ROOT/'verification/biwn-input-dispatch-yield-checks.json');assert cpu['CPU_cases']==1890 and cpu['CPU_instruction_coverage']==[816,816]and cpu['host_guards']==38 and yielded['cases']==25 and yielded['task_handoffs']==225
    correction={'recorded_at':now,'status':'fixture_overlap_identified_and_corrected','first_bad_payload_offset':51354,'selected_tag_offset':14112,'tag_header_bytes':64,'CD_destination':hex(0x1c0000),'first_corrupted_source_address':hex(0x1c0000+14112+64+51354),'historical_supplied_SSP':'0x1d0000','TRAP_exception_frame_address':hex(0x1d0000-6),'corrected_supplied_SSP':'0x1ff000','reserved_stack_low':'0x1fe000','all32transfers_below_reserve':True,'source_behavior_repaired':False,'scope':'Historical assisted-startup fixture supplied the stack; this does not recover or prove original uninterrupted boot stack placement.'}
    assert correction['first_corrupted_source_address']==correction['TRAP_exception_frame_address'];correction['total_changed_byte_count']='not measured';save(ROOT/'verification/loading-stack-overlap-correction.json',correction)
    scope=('The disc-scene test now uses actual scheduler suspension and resume during resource loading. All16cases match original CPU/GPU execution across720worldupdates,2048actoriterations,272equipment suspensions,32loader suspensions and5136handoffs. Loader1B0D4 calls DF60 and resumes1B0DA while nested loader/acquisition/input/world frames remain in RAM. All32loads, totaling3080416bytes, independently match preserved disc payloads. The former DF60 completion/RTS adapter is removed. Two BIOS transfer/stop adapters remain,303C/3042,32calls each. Completion file bytes/progress arrive as an explicit external device event after a real switch away from the loading task; BIOS firmware and physical drive timing are unproved. The supplied supervisor stack is1FF000 with a4KB reserve, outside all tested transfers. The historical supplied1D0000stack overlapped the stream; the first detected payload mismatch was at1CFFFA, exactly the TRAP frame start; total changed byte count was not measured. This is a fixture correction, not a game-code fix or proof of original boot stack placement. Updated input fullCPU regression passes1890cases/all816instructions/38guards;25scheduler cases also pass. Real resource/cache/heap/copy/CD game wrappers and animation remain linked; synchronizationDF8C/DF9C and11otherdispatcher services remain unsupported/unreached. Three top-world scripts are configured/unreached. Sixteencontexts includingrender stay blocked. Queueconsumer/rendering/scenes/remainingtasks/audio/fullgame/hardware remain unfinished; the game is not playable. Count108unchanged.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_resource_answer=scope,checked_dispatcher_answer='Both equipment waits and loader waits now switch through the actual scheduler, preserving source frames.272equipment/32loader suspensions and5136handoffs. Completion bytes/progress are controlled external events; BIOS303C/3042, synchronization/render/fullgame remain unfinished.',checked_timestep_answer='World movement timing is computed by actual code.720completed updates in the newer loading-suspension run; the previous completion-adapter run had752. Extra loader suspensions let other tasks run before loading resumes; this is not a performance regression claim.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);v=read(session/'boot-slice-validation.json');assert v['portable_C_component_count']==108;v.update(disc_world_actor_pipeline=linked,disc_world_loading_pipeline=linked,world_dispatch_full_CPU=cpu,dispatcher_scheduled_yields=yielded,latest_aggregate_update=now);save(session/'boot-slice-validation.json',v)
    p=session/'input-dispatch-fullCPU-generation.json';g=read(p);g.update(status='accepted_fullCPU_direct_and_nested_loader_suspensions',whole_game_complete=False,evidence=['verification/'+n for n in proof_names]);save(p,g)
    checkpoint={'recorded_at':now,'status':'code_passed_local_review_pending','published_components':108,'new_components':0,'disc_cases':16,'world_updates':720,'actor_iterations':2048,'equipment_inner_yields':272,'loader_inner_yields':32,'task_handoffs':5136,'disc_payloads':32,'disc_payload_bytes':3080416,'BIOS_adapters':['0x303c','0x3042'],'loading_completion_adapter_removed':True,'loading_task_switches_verified':True,'completion_data_is_controlled_external_input':True,'supplied_supervisor_stack':'0x1ff000','stack_fixture_correction':str(ROOT/'verification/loading-stack-overlap-correction.json'),'resource_sync_verified':False,'queue_consumer_run':False,'full_goal_status':'active incomplete','evidence':['verification/'+n for n in proof_names]+['verification/loading-stack-overlap-correction.json'],'next_work':'Reconstruct resource synchronization DF8C/DF9C and handlers, exercise readiness waits/wakeups with multiple tasks; then connect live queue consumer/rendering and remaining tasks/scenes/audio/uninterrupted boot. Keep BIOS/device timing and native Chat verification separate.'};save(ROOT/'verification/disc-loading-yield-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        p=ROOT/name;value=read(p);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=checkpoint['evidence'],disc_loading_yield_checkpoint=checkpoint)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:16real-loading-switch cases,1890inputCPU and25scheduler regressions passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actual loader scheduler switches replace DF60 completion shortcut; supplied-stack overlap identified/corrected. BIOS/completion device data/synchronization/render/fullgame remain incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(p,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    note='\nACTUAL LOADER SUSPENSIONS — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored nested status6 propagation and frame-resume integration. OriginalCPU/GPU validates actualloading/scheduler execution; nativeCPU/Unicorn validates1890inputCPU regressions. The stack correction is explicit and retained, with failed trials. No new localmodel code/training/default promotion.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write(note)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);p.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
