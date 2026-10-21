"""Publish actual live rendering records and explicit unexecuted GPU path."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    validation=read(session/'boot-slice-validation.json');cpu=read(ROOT/'verification/biwn-geometry-records-cpu-checks.json');linked=read(ROOT/'verification/biwn-disc-world-geometry-records-checks.json')
    assert cpu['CPU_cases']==512 and cpu['source_instruction_coverage']==[166,166]and cpu['host_guards']==19 and cpu['actual_copy_calls']==5782 and cpu['actual_movement_matrix_submissions']==2569
    assert linked['cases']==16 and linked['task_handoffs']==6144 and linked['actual_C_sprite_decodes']==160
    assert linked['geometry_record_body_call_counts']=={'0x170a0':1008,'0xe3e0':3024,'0xe220':0}and linked['geometry_record_count_values']==[4]
    assert len(linked['render_scene_overlay_script_targets'])==7 and sum(v>0 for v in linked['render_scene_overlay_script_call_counts'].values())==5
    for k,v in validation['disc_world_actor_pipeline'].items():linked.setdefault(k,v)
    rows=read(Path(linked['directory'])/'fixtures.json');assert all(r['final_queue_count']==0 and all('CPU'in h for h in r['rebuilt']['handoffs'])for r in rows)
    total_matrix=sum(r['original']['steps'].count(0xe220)for r in rows);world_matrix=sum(sum(c['target']==0xe220 for c in r['rebuilt']['world_calls'])for r in rows)
    assert total_matrix==3488 and world_matrix==1440
    linked['movement_matrix_scope']={'whole_scene_E220_submissions':total_matrix,'world_recorded_E220_calls':world_matrix,'geometry_record_builder_E220_calls':linked['geometry_record_body_call_counts']['0xe220'],'actor_E220_calls_by_difference':total_matrix-world_matrix-linked['geometry_record_body_call_counts']['0xe220'],'geometry_record_builder_E220_provider_linked':True,'geometry_record_builder_E220_branch_executed':False,'scope':'Zero applies only to the nested170A0record-builder branch. Its actual E220/E098/GPU4320 provider is compiled and linked into the render callback; this fixture does not reach it. World and actor movement already execute actual E220/GPU4320 math in this same21-context scene. Total is measured from originalCPU entry traces; world and builder counts from their matched fullCPU helper logs; actor count is their difference.'}
    previews=[]
    for i,row in enumerate(rows):
        folder=Path(linked['sprite_preview_directory'])/f'case-{i:02d}';meta=read(folder/'sprite.json');assert hashlib.sha256((folder/'sprite.raw16be').read_bytes()).hexdigest()==meta['raw_sha256']
        assert [c['output']for c in row['rebuilt']['render_queue_calls']if 'output'in c][-1]==meta
        previews.append(dict(case=i,png=str(folder/'sprite.png'),png_sha256=hashlib.sha256((folder/'sprite.png').read_bytes()).hexdigest(),raw=str(folder/'sprite.raw16be'),**meta))
    linked.update(decoded_sprite_previews=previews,full_scene_draw_executed=False,overlay_executed=False,full_scene_geometry_executed=False,full_game_viewport_proved=False)
    save(ROOT/'verification/biwn-disc-world-geometry-records-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    for proof in [cpu,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snap=folder/'publication-snapshot';snap.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_geometry_records_cpu.py','check_biwn_geometry_records_cpu.py','check_biwn_render_queue_cpu.py','check_biwn_disc_scene_actors.py','check_biwn_disc_world_yields.py']]
        for name,expected in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
        for p in files:shutil.copy2(p,snap/p.name)
        save(snap/'manifest.json',dict(recorded_at=now,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}))
    if 'geometry_records_full_CPU'not in validation:
        assert validation['portable_C_component_count']==112 and validation['processor_component_counts']=={'CPU':110,'GPU':2}
        validation['portable_C_component_count']=113;validation['processor_component_counts']['CPU']=111
    assert validation['portable_C_component_count']==113 and validation['processor_component_counts']=={'CPU':111,'GPU':2}
    validation.update(geometry_records_full_CPU=cpu,disc_world_actor_pipeline=linked,disc_world_geometry_record_pipeline=linked,latest_aggregate_update=now,component_count_scope='One new CPU entry170A0 rendering-record builder. ExistingE220/E098submission and E3E0copy upgraded/linked, not counted again. Selected proofs, not a game-completion percentage.')
    save(session/'boot-slice-validation.json',validation)
    generation=read(session/'geometry-records-fullCPU-generation.json');generation.update(status='accepted_standalone_and_live_disc_scene_record_builder',whole_game_complete=False,evidence=['verification/biwn-geometry-records-cpu-checks.json','verification/biwn-disc-world-geometry-records-checks.json']);save(session/'geometry-records-fullCPU-generation.json',generation)
    scope=('Actual170A0 now builds rendering records in the live disc-scene renderer:1008calls,3024realE3E0copies and4records percall. The captured scene never reaches nestedE220matrixsubmission (0calls), while the separate512case fullCPU proof executes5782copies/2569matrixsubmissions and covers all166instructions/19guards with nativeCPU+independent Unicorn and originalGPU4320versusCmath. Sixteen integrated cases retain720worldupdates/2048actoriterations/6144fullCPUhandoffs/1008queueconsumers/160sprite decodes/32disc payloads totaling3080416bytes; finalqueues empty. Scene caller/clear/rotation each1008actualcalls. Seven configured lower rendering scripts remain:181F8overlay,E0A6,E0F2,E148,E19E,E202,185B2display-list. Five reached1008times each:181F8,E0A6,E19E,E202,185B2;E0F2/E148 unreached. GPU4D80transform is not reconstructed by170A0record building. No full3Dgeometry/viewport/scanout/audio/uninterruptedboot/fullgame/physicaltiming proof. Six contexts runnable/15blocked. BIOS/completion adapters, supplied clock/pad/inventory, assistedstartup and synchronousGPU remain fixtures. Main-scene resource synchronization still unexercised despite separate two-client proof. Game not playable. Aggregate113selectedcomponents:111CPU/2GPU, one new170A0entry; not a completion percentage.')
    scope+=' The entire live scene DOES execute3488E220/GPU4320movement submissions:1440matchedworld calls,2048actor calls by difference, and0inside170A0record builder. The zero is only that nested rendering branch, not all live movement/GPUmath. The record-builder E220/E098/GPU4320 provider IS compiled and linked in the render callback, but this fixture never reaches it; linked code and exercised branches are different facts.'
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_render_queue_answer='170A0 is actual rendering-record construction:1008livecalls/3024actualcopies/4records each. Its nestedE220branch has0calls; the entire live scene has3488actualE220/GPU4320calls from world/actor movement. Standalone512cases separately execute2569matrixsubmissions. Seven rendering scripts configured/five reached:181F8,E0A6,E19E,E202,185B2 each1008;E0F2/E148 unreached. GPU4D80transform/fullviewport/game unfinished.',checked_dispatcher_answer='Actual world/input/loading/render queue/scene caller/record builder run together;272equipment/32loader suspensions/6144fullCPUhandoffs. Main-scene sync unexercised; GPU4D80transform/display-list/overlay/lowerdraw/fullgame unfinished.',checked_resource_answer='Actual resource/heap/loader/CD and32disc payloads/3080416bytes verified in latest live geometry-record test. Record builder performs3024actual64bytecopies. BIOS/completion adapters,main-scene sync and fullgame remain incomplete.');save(ROOT/'verification/world-actor-checked-examples.json',examples)
    checkpoint=dict(recorded_at=now,status='code_passed_local_scope_review_pending',published_components=113,new_components=1,CPU_cases=512,source_instruction_coverage=[166,166],host_guards=19,standalone_copy_calls=5782,standalone_matrix_submissions=2569,disc_cases=16,task_handoffs=6144,live_geometry_calls=1008,live_copy_calls=3024,live_matrix_submissions=0,live_record_count_values=[4],live_C_sprite_decodes=160,configured_render_scripts=7,reached_render_scripts=5,full_scene_geometry_executed=False,full_viewport_proved=False,full_goal_status='active incomplete',next_work='Reconstruct actual GPU4D80transform and E0A6submission, E19E/E202draw helpers, fullCPU185B2display-list and181F8overlay; continue resource game waits, remaining tasks/scenes/audio/uninterruptedboot/fullgame and native/everyday local/advertising workflows.',evidence=['verification/biwn-geometry-records-cpu-checks.json','verification/biwn-disc-world-geometry-records-checks.json'])
    save(ROOT/'verification/geometry-records-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        p=ROOT/name;v=read(p);v.update(geometry_records_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':v['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':v['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':v.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:512standalone/16live geometry-record cases passed; noCbehavior repair.')
        if name=='verification/setup-status.json':v['game_work']=scope
        if name=='verification/requirements-audit.json':
            v.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actual geometry-record builder and copies replace reached170A0stub. GPUtransform andfullgame still incomplete.',next_safe_work=checkpoint['next_work'])
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(p,v)
    note='GEOMETRY RECORDS — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored C/harness/integration. NativeCPU/GPU and independent Unicorn validate scoped behavior. First dense observer stopped at its10000instructionlimit while native/Cmatched; raised private observer ceiling100000and asserted endpoints. Preflight/fullbatch passed, noCbehaviorrepair. No subagents/newtraining/defaultpromotion.\n\nNEXT\n'+checkpoint['next_work']+'\nFullgoalactive andincomplete.\n';(ROOT/'CURRENT DECOMPILATION.txt').write_text(note)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+note)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);p.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
