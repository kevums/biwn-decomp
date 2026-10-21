"""Register controlled CPU synchronization proof without claiming resource contention."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);v=read(session/'boot-slice-validation.json');source=ROOT/'projects/black-ice-white-noise/restoration';sync=read(ROOT/'verification/biwn-resource-sync-checks.json');linked=read(ROOT/'verification/biwn-disc-world-loading-yields-checks.json')
    assert sync['CPU_cases']==1216 and sync['signal_dual_oracle_cases']==1024 and sync['source_instruction_coverage']==[21,21]and sync['host_guards']==31
    assert linked['cases']==16 and linked['world_updates']==720 and linked['loader_inner_yields']==32 and linked['task_handoffs']==5136 and linked['loaded_payload_bytes']==3080416
    for k,value in v['disc_world_actor_pipeline'].items():linked.setdefault(k,value)
    names=['biwn-resource-sync-checks.json','biwn-scheduler-checks.json','biwn-input-dispatch-yield-checks.json','biwn-disc-world-loading-yields-checks.json']
    for name in names:
        proof=linked if name==names[-1]else read(ROOT/'verification'/name);folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snap=folder/'publication-snapshot';snap.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['check_biwn_resource_sync.py','check_biwn_scheduler.py','check_biwn_input_dispatch_yield.py','check_biwn_disc_world_yields.py','check_biwn_disc_scene_actors.py']]
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
        for p in files:shutil.copy2(p,snap/p.name)
        save(snap/'manifest.json',{'recorded_at':now,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    save(ROOT/'verification/biwn-disc-world-loading-yields-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    assert v['portable_C_component_count']in [108,112]
    v.update(portable_C_component_count=112,processor_component_counts={'CPU':110,'GPU':2},component_count_scope='Four new CPU entries:DF04signal,DF9Csignalwrapper,DF8Cwaitwrapper,DEF6TRAP4handler. DF96 restore is part of the wait wrapper; existing scheduler reused. Selected proofs, not a full-game completion percentage.',resource_synchronization_full_CPU=sync,disc_world_actor_pipeline=linked,disc_world_loading_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',v)
    p=session/'resource-synchronization-fullCPU-workmap.json';mapping=read(p);mapping.update(status='reconstructed_and_verified_controlled_CPU_not_resource_readiness',evidence='verification/biwn-resource-sync-checks.json',whole_game_complete=False);save(p,mapping)
    next_plan={'recorded_at':now,'status':'planned_not_executed','fixture':'Two real resource acquisition callers share a cold cache entry. First starts actual loader and yields; second increments references and TRAP4-waits on not-ready state. First resumes loading, marks ready, then sourceDF9C/DF04 clears second wait mask. Verify second resumes at1AF56 viaDF96 and both receive the same valid handle/payload.',
        'required_changes':['Resource CPU stop_on_yield must also stop/commit atDF8C; nested status6 propagation must accept that PC. Current code stops onlyDF60.','Controlled fixture uses separate per-context resource frame stacks; real scheduler wait/signal and existing task removal provide continuations. No captured-handle or readiness-flag scripts.','Keep existing BIOS303C/3042 and explicit completion event boundaries; deliver file bytes after first actual handoff, but resource ready flag changes only in source loader/acquisition code.','Use checked startupRAM/heap/resource table and cold IDs24/29. Supply supervisor stack outside transfer window. Preserve fullCPU/RAM/heap/cache/privateframes and independent payload hashes.','If removing the first finished synthetic client, use sourceTRAP2/DEB6, not a fabricated task switch; clearly declare any synthetic call/return glue.'],
        'scope':'Separate controlled two-client resource-readiness integration before full game task integration. Neither is proved by current synchronization CPU tests.'};save(session/'resource-readiness-two-client-plan.json',next_plan)
    scope=('Added resource wait/wake reconstruction for four entries:DF04,DF8C,DF9C andDEF6. Controlled task-ring tests pass1216cases/all21instructions/31hostguards. Signal paths have1024independentUnicorn ordered-bus cases;128wait and64handler cases use original nativeCPU. CompleteCPU/SR/USP/SSP,2MBRAM and sourceprivateframes match. The scheduler now restores warmDF96 wait continuations as well asDF66 yields. Its512native/256Unicorn-preRTE regression,25equipment-yield cases and16disc-loading cases pass. Existing real loading proof remains720worldupdates/2048actoriterations/32loader+272equipment suspensions/5136handoffs, with32payloads/3080416bytes matching preserveddisc. Synchronization is not yet called or exercised by those disc-scene resource cases; two-client readiness coordination remains unproved. BIOS transfer/stop and controlled completion events, rendering/queueconsumer/remainingtasks/scenes/audio/uninterruptedboot/fullgame/hardware remain unfinished. The game is not playable. Count112:110CPU/twoGPU.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_synchronization_answer='Wait/wake CPU code now passes controlled-ring tests. This is separate from the disc-scene proof, where synchronization calls remain unreached/unlinked. Actual shared-resource readiness and wake coordination require the planned two-client integration. Fullgame remains unfinished.');save(ROOT/'verification/world-actor-checked-examples.json',examples)
    checkpoint={'recorded_at':now,'status':'code_passed_local_scope_review_pending','published_components':112,'new_components':4,'CPU_cases':1216,'source_instruction_coverage':[21,21],'signal_Unicorn_cases':1024,'wait_native_cases':128,'handler_native_cases':64,'host_guards':31,'scheduler_regression_native_cases':512,'scheduler_regression_Unicorn_preRTE_cases':256,'equipment_regression_cases':25,'disc_loading_regression_cases':16,'disc_resource_synchronization_executed':False,'resource_readiness_verified':False,'full_goal_status':'active incomplete','next_work':'Implement and verify the two-client resource-readiness fixture, then link synchronization into running game task bodies; continue live queue/render/scenes/audio/uninterruptedboot. NativeChat/BIOS/physical timing remain separate requirements.','next_plan':str(session/'resource-readiness-two-client-plan.json'),'evidence':['verification/'+n for n in names]};save(ROOT/'verification/resource-sync-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        p=ROOT/name;value=read(p);value.update(resource_sync_checkpoint=checkpoint,latest_resource_sync_progress=scope)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal: synchronization CPU cases and scheduler/equipment/disc-loading regressions passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: synchronization CPU bodies and warm wait resume accepted. Actual resource contention integration remains incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(p,value)
    text='RESOURCE SYNCHRONIZATION — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored wait/wake C and checks. OriginalCPU/Unicorn decide scoped acceptance. First full test passed CPU cases but an injected write-failure guard chose a one-context signal ring with no writes; selected a case with an actual write, then all31guards passed. No game C behavior repair. No actual readiness integration claim.\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(text)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+text)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);p.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
