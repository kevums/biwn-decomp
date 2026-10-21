"""Publish accepted full CPU CD game wrappers and actual disc integration."""
import hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration'
    cpu=read(ROOT/'verification/biwn-cd-cpu-checks.json');linked=read(ROOT/'verification/biwn-disc-world-cd-wrappers-checks.json');old=read(ROOT/'verification/biwn-disc-world-resources-checks.json')
    assert cpu['CPU_cases']==1280 and cpu['CPU_instruction_coverage']==[83,83]and cpu['host_guards']==18
    assert linked['cases']==16 and linked['world_updates']==752 and linked['task_handoffs']==5136 and linked['dispatcher_inner_yields']==272
    assert linked['resource_fixture_call_count']==0 and linked['loaded_payload_bytes']==3080416 and linked['disc_transfer_requests']==linked['disc_transfer_completions']==32
    assert set(linked['resource_IO_adapter_call_counts'].values())=={32}and set(linked['resource_IO_adapter_call_counts'])=={'0x303c','0x3042','0xdf60'}
    assert set(linked['cd_body_call_counts'].values())=={32}
    for k,v in old.items():linked.setdefault(k,v)
    linked['new_components']=2
    rows=read(Path(linked['directory'])/'fixtures.json');unique={(p['tag'],p['bytes'],p['sha256'])for p in linked['loaded_payloads']};assert len(unique)==3
    linked['loaded_payload_unique']=[{'tag':tag,'bytes':size,'sha256':h}for tag,size,h in sorted(unique)]
    linked.update(dispatcher_calls=sum(sum(c['target']==0x191f4 for c in r['rebuilt']['world_calls'])for r in rows),dispatcher_nested_helper_call_count=sum(len(r['rebuilt']['dispatcher_helper_calls'])for r in rows),original_GPU_submit_entries=sum(r['original']['steps'].count(0xe220)for r in rows))
    assert all(p['matches_preserved_normalized_disc_payload']for p in linked['loaded_payloads'])
    save(ROOT/'verification/biwn-disc-world-cd-wrappers-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    for proof in [cpu,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snapshot=folder/'publication-snapshot';snapshot.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_cd_cpu.py','check_biwn_cd_cpu.py','check_biwn_disc_world_yields.py','check_biwn_disc_scene_actors.py','biwn_disc_backend.py']]
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
        for p in files:shutil.copy2(p,snapshot/p.name)
        save(snapshot/'manifest.json',{'recorded_at':now,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    scope=('The game-level D206 offset/MSF calculation with actual D1E0 division, D2F0 transfer-start wrapper and D306 stop wrapper now execute reconstructed CPU code in the disc-scene test. Each runs 32 times. All 16 cases match original execution across 752 world updates, 2,048 actor iterations, 272 equipment suspensions and 5,136 handoffs, including complete CPU state, 2 MB RAM, private frames and helper states. The 32 loaded payloads total 3,080,416 bytes and independently match preserved disc data. No resource-body or game-level CD-wrapper scripts remain. The separate CD wrapper proof passes 1,280 cases, all 83 instructions and 18 host guards, including both stack banks. BIOS303C transfer and BIOS3042 stop remain adapters, plus DF60 loading completion; 32 calls each. The start adapter clobbers A2 to verify real save/restore; the stop adapter preserves the loader cursor in A2 as an explicit boundary assumption. Actual loading task switches and resource synchronization DF8C/DF9C remain unverified. Eleven other dispatcher services are unsupported; three top-world scripts are configured but unreached. Sixteen contexts including rendering remain blocked; the live queue consumer, rendering, scene transitions, remaining tasks, audio and full-game/hardware validation remain unfinished. The game is not playable.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_resource_answer=scope,checked_dispatcher_answer='Equipment waits yield through the actual scheduler. Resources and game-level CD wrappers execute actual C. BIOS transfer/stop and loader completion remain adapters; loading task switching, synchronization, render and the full game remain unfinished.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);v=read(session/'boot-slice-validation.json')
    assert v['portable_C_component_count']in [106,108]
    v.update(portable_C_component_count=108,processor_component_counts={'CPU':106,'GPU':2},component_count_scope='Two new CPU entries D2F0 transfer-start and D306 stop wrappers. D1E0 division and D206 offset calculation were previously counted; now upgraded to full CPU/private-frame coverage. This is not a completion percentage.',cd_wrapper_full_CPU=cpu,disc_world_actor_pipeline=linked,disc_world_CD_wrapper_pipeline=linked,latest_aggregate_update=now)
    save(session/'boot-slice-validation.json',v)
    p=session/'cd-wrapper-fullCPU-generation.json';g=read(p);g.update(status='accepted_fullCPU_and_disc_world_wrapper_linkage',whole_game_complete=False,evidence=['verification/biwn-cd-cpu-checks.json','verification/biwn-disc-world-cd-wrappers-checks.json']);save(p,g)
    checkpoint={'recorded_at':now,'status':'code_passed_local_review_pending','published_components':108,'processor_components':{'CPU':106,'GPU':2},'new_components':2,'CPU_cases':1280,'CPU_instruction_coverage':[83,83],'host_guards':18,'disc_cases':16,'inner_yields':272,'task_handoffs':5136,'disc_payloads':32,'disc_payload_bytes':3080416,'resource_body_scripts':0,'CD_game_wrapper_scripts':0,'BIOS_adapters':['0x303c','0x3042'],'loading_completion_adapter':'0xdf60','loading_task_switches_verified':False,'resource_sync_verified':False,'queue_consumer_run':False,'full_goal_status':'active incomplete','evidence':['verification/biwn-cd-cpu-checks.json','verification/biwn-disc-world-cd-wrappers-checks.json'],'next_work':'Propagate loader suspensions through resource/input/world frames and run the actual scheduler during disc completion; reconstruct synchronization. Then connect live queue consumption/rendering and remaining tasks, scene transitions, audio and full-game startup. Keep native Chat verification separate.'}
    save(ROOT/'verification/disc-cd-cpu-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        p=ROOT/name;value=read(p);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=checkpoint['evidence'],disc_cd_cpu_checkpoint=checkpoint)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal: 1280 CD wrapper CPU cases and 16 integrated disc cases passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actual CD game wrappers replace three game-level adapters. BIOS/completion/synchronization/loading switches/render/full game remain incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(p,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    note='\nCD GAME WRAPPERS — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored static CD-wrapper CPU code and checks. Native CPU and independent Unicorn decide acceptance; preserved disc hashes check integrated payloads. First integration stalled because the stop adapter clobbered the A2 stream cursor. Corrected that boundary to preserve A2; source C was unchanged. BIOS behavior is still an explicit assumption, not verified firmware.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write(note)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);p.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
