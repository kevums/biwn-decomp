"""Publish actual two-client readiness while retaining its controlled-ring scope."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);v=read(session/'boot-slice-validation.json');source=ROOT/'projects/black-ice-white-noise/restoration';ready=read(ROOT/'verification/biwn-resource-readiness-checks.json');linked=read(ROOT/'verification/biwn-disc-world-loading-yields-checks.json');cpu=read(ROOT/'verification/biwn-resource-cpu-checks.json')
    assert ready['cases']==16 and ready['acquisition_returns']==32 and ready['actual_readiness_waits']==ready['actual_source_signals']==ready['actual_first_client_removals']==16 and ready['task_handoffs']==48
    assert ready['verified_payloads']==16 and ready['verified_payload_bytes']==1538816 and ready['resource_body_scripts']==ready['readiness_flag_scripts']==0
    assert cpu['CPU_cases']==4064 and cpu['CPU_instruction_coverage']==[506,506]and cpu['host_guards']==18
    assert linked['cases']==16 and linked['world_updates']==720 and linked['loader_inner_yields']==32 and linked['task_handoffs']==5136 and linked['loaded_payload_bytes']==3080416
    for k,value in v['disc_world_actor_pipeline'].items():linked.setdefault(k,value)
    names=['biwn-resource-readiness-checks.json','biwn-resource-cpu-checks.json','biwn-disc-world-loading-yields-checks.json']
    for name in names:
        proof=linked if name==names[-1]else read(ROOT/'verification'/name);folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snap=folder/'publication-snapshot';snap.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_resource_cpu.py','check_biwn_resource_readiness.py','check_biwn_resource_cpu.py','check_biwn_disc_world_yields.py','check_biwn_disc_scene_actors.py','biwn_disc_backend.py']]
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
        for p in files:shutil.copy2(p,snap/p.name)
        save(snap/'manifest.json',{'recorded_at':now,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    save(ROOT/'verification/biwn-disc-world-loading-yields-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    rows=read(Path(ready['directory'])/'fixtures.json');assert all(row['all_CPU_full_RAM_nestedframes_handoffs_readiness_match']for row in rows)
    assert all(p['matches_preserved_normalized_disc_payload']for p in ready['payloads'])
    unique={(p['tag'],p['bytes'],p['sha256'])for p in ready['payloads']};assert len(unique)==2
    ready['unique_payloads']=[{'tag':tag,'bytes':size,'sha256':h}for tag,size,h in sorted(unique)];save(ROOT/'verification/biwn-resource-readiness-checks.json',ready);save(Path(ready['directory'])/'report.json',ready)
    assert v['portable_C_component_count']==112;v.update(two_client_resource_readiness=ready,resource_full_CPU=cpu,disc_world_actor_pipeline=linked,disc_world_loading_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',v)
    p=session/'resource-fullCPU-generation.json';g=read(p);g.update(status='accepted_fullCPU_with_yield_and_wait_suspension',whole_game_complete=False,evidence=['verification/'+n for n in names]);save(p,g)
    p=session/'resource-readiness-two-client-plan.json';plan=read(p);plan.update(status='implemented_and_verified_controlled_two_client_fixture',evidence='verification/biwn-resource-readiness-checks.json',whole_game_complete=False);save(p,plan)
    scope=('Actual two-client resource readiness now passes 16 controlled cases. The first caller starts the real loader and yields; the second joins the same cache entry, raises its reference count to two and waits through TRAP4. Reconstructed loader/acquisition code marks the entry ready, and DF9C/DF04 clears the waiter mask. Actual task removal then lets the second resume its saved wait continuation. Both return the same valid handle. There are 32 acquisition returns, 16 loading yields, 16 readiness waits, 16 wake signals and 48 handoffs. All 16 payloads, totaling 1,538,816 bytes, independently match preserved disc data. Full CPU state, 2 MB RAM, nested frames and every handoff CPU state match original execution. No resource-body or ready-flag scripts. This uses a supplied two-client ring in captured scene RAM, with declared call/return/task-removal scaffolding; it is not original full-game task behavior. BIOS transfer/stop and controlled file-completion events remain. The separate 21-context world/actor scene still does not exercise synchronization; its 16 loading cases continue to pass, with 32 payloads/3,080,416 bytes and 5,136 handoffs. Updated resource CPU regression passes 4,064 cases/all 506 instructions/18 guards. Rendering, live queue consumption, remaining tasks, scenes, audio, uninterrupted boot and full-game/hardware validation remain unfinished. The game is not playable. Aggregate112 unchanged.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_synchronization_answer='Actual two-client readiness/wake coordination now passes16controlled cases with no ready-flag scripts. It is separate from the21-context world/actor scene, where synchronization is still unexercised. BIOS/file-completion boundaries and fullgame/render/audio remain unfinished.',checked_resource_answer=scope);save(ROOT/'verification/world-actor-checked-examples.json',examples)
    checkpoint={'recorded_at':now,'status':'code_passed_local_scope_review_pending','published_components':112,'new_components':0,'controlled_two_client_cases':16,'acquisition_returns':32,'readiness_waits':16,'source_wake_signals':16,'task_handoffs':48,'verified_payloads':16,'verified_payload_bytes':1538816,'resource_body_scripts':0,'ready_flag_scripts':0,'resource_readiness_verified_in_controlled_fixture':True,'disc_scene_synchronization_executed':False,'BIOS_adapters':['0x303c','0x3042'],'completion_bytes_are_controlled_external_input':True,'resource_CPU_regression_cases':4064,'disc_loading_regression_cases':16,'full_goal_status':'active incomplete','next_work':'Connect verified wait/signal services and their suspension propagation into game task callers, then connect the live animation queue consumer/render task and remaining services/tasks/scenes/audio/uninterrupted boot. Keep controlled two-client proof distinct from full-game behavior and native Chat verification.','evidence':['verification/'+n for n in names]};save(ROOT/'verification/resource-readiness-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        p=ROOT/name;value=read(p);value.update(resource_readiness_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:16actual two-client readiness cases,4064resourceCPU and16world-loading regressions passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actual two-client shared-resource wait/load/wake/return verified. Original full-game task linkage/render/audio/boot remain incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(p,value)
    text='TWO-CLIENT RESOURCE READINESS — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored wait-suspension support and controlled two-client driver. OriginalCPU and independent preserved-disc hashes decide integration acceptance. Separate resourceCPU regressions also use Unicorn. No resource/ready-flag mocks or localmodel code. Preflight and all16cases passed without Cbehavior repair.\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n';(ROOT/'CURRENT DECOMPILATION.txt').write_text(text)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+text)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);p.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
