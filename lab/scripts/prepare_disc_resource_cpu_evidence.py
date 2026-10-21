"""Publish full resource/cache/heap CPU and verified disc payload linkage."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn-resource-cpu-checks.json','biwn-disc-world-resources-checks.json'];cpu,linked=[read(ROOT/'verification'/n)for n in names];old=read(ROOT/'verification/biwn-disc-world-yields-checks.json')
    assert cpu['CPU_cases']==4064 and cpu['CPU_instruction_coverage']==[506,506]and cpu['host_guards']==18
    assert linked['cases']==16 and linked['world_updates']==752 and linked['dispatcher_inner_yields']==272 and linked['task_handoffs']==5136
    assert linked['resource_fixture_call_count']==0 and not linked['resource_script_targets']and linked['disc_transfer_requests']==linked['disc_transfer_completions']==32 and linked['loaded_payload_bytes']==3080416
    for k,v in old.items():linked.setdefault(k,v)
    rows=read(Path(linked['directory'])/'fixtures.json');unique={(p['tag'],p['bytes'],p['sha256'])for p in linked['loaded_payloads']};assert len(unique)==3
    linked['loaded_payload_unique']=[{'tag':tag,'bytes':size,'sha256':h}for tag,size,h in sorted(unique)]
    linked.update(dispatcher_calls=sum(sum(c['target']==0x191f4 for c in r['rebuilt']['world_calls'])for r in rows),dispatcher_nested_helper_call_count=sum(len(r['rebuilt']['dispatcher_helper_calls'])for r in rows),original_GPU_submit_entries=sum(r['original']['steps'].count(0xe220)for r in rows),source_sha256=linked['source_sha256'])
    assert all(p['matches_preserved_normalized_disc_payload']for p in linked['loaded_payloads'])and all(r['original']['steps'].count(0xdf8c)==r['original']['steps'].count(0xdf9c)==0 for r in rows)
    save(ROOT/'verification/biwn-disc-world-resources-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    for proof in [cpu,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snapshot=folder/'publication-snapshot';snapshot.mkdir(exist_ok=True)
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_resource_cpu.py','generate_biwn_input_dispatch_cpu.py','check_biwn_resource_cpu.py','check_biwn_disc_world_yields.py','check_biwn_disc_scene_actors.py','biwn_disc_backend.py']]
        for path in files:shutil.copy2(path,snapshot/path.name)
        save(snapshot/'manifest.json',{'recorded_at':now,'scope':'Accepted C hashes; harness at publication disables invalid partial-memory CLI mode.','sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    scope=('Actual release1B002,acquire1AF04,free1545C,allocate152A2 and loader1B044/copy now execute in the disc-scene world/input/actor ring. The four resource-body scripts are removed. All16cases match original CPU/GPU across752worldupdates,2048actoriterations,272equipment inner-yields and5136handoffs, completeCPU/SR/USP/SSP/2MBRAM/privateframes. '
           'There are32release,32acquire,32loader,64free,64allocation and32copy calls. Compaction is linked but not reached. The32loads total3,080,416bytes; every payload independently matches preserved normalized disc bytes. Three unique payloads are MESP96350bytes,MHSP89068bytes andMASP103284bytes. Resource handles/cache/reference/free-list changes run actual CPU/C code; no captured-handle acquisition stub remains. '
           'Four CDoffset/transfer/stop/completion adapter targets remain (D206,D2F0,D306,DF60),32calls each. LoaderDF60 completes a transfer with an RTS adapter rather than switching tasks; equipmentDF60 still uses the actual scheduler. Resource synchronization DF8C/DF9C is unsupported/unreached, as are11otherdispatcher services. Three top-world scripts remain configured/unreached:1B786/19F2C/19FDA. '
           'The separate resource/heap/copy fullCPU proof passes4064cases/all506instructions/18guards, including user/supervisor banks and ordered bus/privateframes. Acquire/release standalone fixtures still script some callees; the actualscene linkage proves them together. First CPUrun lacked two copyalignment instructions; unequal alignments added. No generatedCbehavior repair was needed. '
           'Actual original-stage animation flags drive equipment waits and160queue requests. Existinginventoryselection1/2 is an explicit initialscenario input; B+C comes through the actual emulatedpad. The phased21context ring blocks16includingrender; startup private-stack/formatter exclusions remain. Queueconsumer, actual loading task switches/physicaldrive, targetacquisition/crosshair,3Ddraw/scanout/mainloop/scenes/audio/fullgame/hardware remain unfinished. The game is not playable. Count remains106:104CPU/twoGPU.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_timestep_answer='Actual world computes movement time and resumes both internal equipment waits. Newest16case proof runs actual resource/cache/heap/loader/copy and checks32payloads againstdisc. Four CD/completion adapters remain; loading switches/synchronization/render/queueconsumer/fullgame unverified.',checked_dispatcher_answer='Realworld equipment yields remain verified:272innersuspensions/5136handoffs andactualanimation. The fourresourcebody stubs are now removed, but CDoffset/transfer/stop/completion remain adapters and loaderDF60 does not switchtasks. Eleven otherdispatcher services and tworesource synchronization routines remain unsupported.',checked_resource_answer='Release/acquire/free/allocate/loader/copy now run actual reconstructed CPU bodies in16discscene cases. Thirty-two payloads/3080416bytes matchpreserveddisc, includingMESP/MHSP/MASP. CD/completion adapters and unverifiedloadingcontextswitches remain; no rendering/fullgame/physicaldrive claim.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);v=read(session/'boot-slice-validation.json');assert v['portable_C_component_count']==106;v.update(resource_full_CPU=cpu,disc_world_actor_pipeline=linked,disc_world_resource_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',v)
    path=session/'resource-fullCPU-generation.json';g=read(path);g.update(status='accepted_fullCPU_and_live_disc_resource_linkage',evidence=names,whole_game_complete=False);save(path,g)
    checkpoint={'recorded_at':now,'status':'code_passed_local_review_pending','published_components':106,'new_components':0,'CPU_cases':4064,'CPU_instruction_coverage':[506,506],'host_guards':18,'disc_cases':16,'inner_yields':272,'task_handoffs':5136,'resource_body_scripts':0,'disc_payloads':32,'disc_payload_bytes':3080416,'unique_payloads':3,'CD_adapter_targets':4,'loading_task_switches_verified':False,'unsupported_resource_sync':2,'unsupported_other_dispatcher_services':11,'queue_consumer_run':False,'full_goal_status':'active incomplete','evidence':['verification/'+n for n in names],
                'next_work':'Replace CD/offset/completion adapters with full CPU BIOS-wrapper and loading scheduler linkage; port synchronization, connect live queueconsumer/render and remainingtasks/audio/fullgame. Keep native Chat and local inference verification separate.'};save(ROOT/'verification/disc-resource-cpu-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=checkpoint['evidence'],disc_resource_cpu_checkpoint=checkpoint)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:4064fullresourceCPU cases/all506instructions and16actualresourceworldcases/32disc payloads passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actualresource/cache/heap/loader/copy and verifieddisc payloads replace4resource scripts. CD/completion/loading-switch/render/fullgame remain incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(path,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    note='\nACTUAL RESOURCE CPU / DISC PAYLOADS — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored staticresourceCPU and integration; nativeCPU/Unicorn/originalGPU and preserveddisc hashes decide acceptance. Partialmemory trial failed because actualfree invalidated the captured-handle acquisition stub. Replaced acquisition/loader too, rather than preserving that invalid fixture. Firstfullintegration CPU/RAM matched; a localvariable overwrote actorreturnlogs, corrected before acceptance. No localmodel code/training/defaultpromotion.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
