"""Publish accepted local6380 source and combined57/6380 hybrid evidence."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    checked=read(ROOT/'verification/biwn-gpu-consumer6380-candidate-checks.json');hybrid=read(ROOT/'verification/biwn-gpu-consumer6380-hybrid-checks.json');package=checked['package'];candidate=Path(checked['candidate_directory']);author=Path(package['author_directory']);result=read(author/'author.json')
    assert checked['GPU_cases']==36 and checked['source_instruction_coverage']==[67,67]and checked['host_guards']==16 and checked['original_GPU_calls_on_C_side']==0
    assert hybrid['cases']==4 and hybrid['C_setup_calls']==4 and hybrid['C_consumer_calls']==32 and not hybrid['original_GPU57A0_executed']and not hybrid['original_GPU6380_executed']and hybrid['other_original_GPU_programs_executed']
    for name,digest in package['source_sha256'].items():assert sha(source/name)==sha(candidate/name)==digest
    body=(author/'candidate-cases.txt').read_text();assert body in(source/'biwn_gpu_consumer6380.c').read_text()and hashlib.sha256(body.encode()).hexdigest()==package['case_bodies_sha256']
    checked.update(publication_status='accepted_local27B_case_bodies_unchanged_standalone36_and_combined_hybrid4',source_sha256=package['source_sha256'],case_body_edits_by_coordinator=False,hybrid_evidence=str(ROOT/'verification/biwn-gpu-consumer6380-hybrid-checks.json'),new_components=1)
    save(ROOT/'verification/biwn-gpu-consumer6380-checks.json',checked)
    remaining=['resident dispatcher F031BE','0x58a0','0x6460','0x6720','0x69a0']
    scope=('Local27B authored all67GPU6380 list-consumer instruction bodies in its first draft with typed source operands; accepted without edits. '
        'Coordinator supplied interface, fixed engine, integer primitives, decoded facts, original observer, guards and integration. '
        '36originalGPU comparisons cover all67instructions, allthree handoff destinations and16hostguards. '
        'Four combined draw chains replace both57A0 and6380 with unchanged local C:4setup calls and32consumer calls; complete RAM/GPUarchitecture/PCorder and blitter readbacks match the original integer-mode reference. '
        'Other GPU material/resident programs and dispatcher remain original, so this is not a full C renderer or playable game. '
        'There are118selected components112CPU/6GPU, not a completion percentage. Local model instruction bodies now total140across two accepted GPU programs. '
        'Current live C scene remains1008geometry calls with counters0/58 plus4builder records, absolute4/62. '
        'Full CPU E19E/E202 linkage, coherent GPU context, full drawing/display/overlay, remaining tasks/scenes/audio/boot and easy native Chat/advertising evaluation remain unfinished. Backend raster discrepancy remains unresolved.')
    checkpoint=dict(recorded_at=now,status='local27B_consumer6380_accepted_unchanged_standalone36_combined_hybrid4',published_components=118,processor_components={'CPU':112,'GPU':6},new_components=1,local_model='local/advertising-qwen38,27B6bit everyday base',role='Author',fresh_context=True,author_seconds=result['seconds'],author_usage=result['usage'],author_directory=str(author),exact_prompts_and_response=str(author/'prompts-and-responses.txt'),accepted_case_bodies=67,total_local_model_case_bodies=140,local_model_programs=['GPU57A0 setup','GPU6380 list consumer'],coordinator_case_body_edits=False,coordinator_authored=package['coordinator_authored'],reviewer='Codex source/contract review and pinned original-GPU comparisons; no independent model or second GPU oracle',GPU_cases=36,source_instruction_coverage=[67,67],host_guards=16,source_sha256=package['source_sha256'],case_bodies_sha256=package['case_bodies_sha256'],GPU_division_control=0,hybrid=dict(report=str(ROOT/'verification/biwn-gpu-consumer6380-hybrid-checks.json'),cases=4,C_setup_calls=4,C_consumer_calls=32,original_GPU57A0_executed=False,original_GPU6380_executed=False,other_original_GPU_programs_executed=True,remaining_original_components=remaining,source_CPU_E19E_E202_executed=False,full_renderer_C=False,full_viewport_proved=False),full_game_complete=False,full_renderer_C=False,full_viewport_proved=False,scope=scope,next_work='Reconstruct resident dispatcher and58A0/6460/6720/69A0, then integrate fullCPU E19E/E202 and coherent GPU context. Continue full renderer/display/overlay, raster discrepancy, remaining tasks/scenes/audio/boot and everyday native Chat/advertising evaluation.',native_Chat=False,training_this_turn=False,base_model_changed=False)
    save(ROOT/'verification/consumer6380-checkpoint.json',checkpoint)
    validation=read(session/'boot-slice-validation.json')
    if 'GPU_consumer6380_program'not in validation:
        assert validation['portable_C_component_count']==117 and validation['processor_component_counts']=={'CPU':112,'GPU':5};validation['portable_C_component_count']=118;validation['processor_component_counts']['GPU']=6
    assert validation['portable_C_component_count']==118 and validation['processor_component_counts']=={'CPU':112,'GPU':6}
    validation.update(GPU_consumer6380_program=checked,combined_GPU_setup57_consumer6380_draw_chain=hybrid,consumer6380_checkpoint=checkpoint,latest_aggregate_update=now,component_count_scope=scope)
    save(session/'boot-slice-validation.json',validation)
    previous=read(ROOT/'verification/projection-full-coverage-checkpoint.json');pending=previous['pending_integration_evidence']
    pending.update(selected_component_count=118,later_draw_programs=remaining,GPU6380_consumer=checkpoint,combined_hybrid_draw_chain=checkpoint['hybrid'],scope=scope)
    pending['original_draw_chain'].update(C_setup57_and_consumer6380_now_verified_in_separate_hybrid_proof=True,scope='Original-only draw reference retained. New combined C57A0+6380 hybrid proof is separate; other programs remain original. Not fully C viewport/game.')
    save(ROOT/'verification/projection-full-coverage-checkpoint.json',previous)
    workmap=read(session/'remaining-draw-GPU-workmap.json')
    for program in workmap['programs']:
        if program['CPU_header']=='0x6380':program.update(status=checked['publication_status'],C_reconstructed=True,source_instruction_coverage=[67,67],standalone_cases=36,host_guards=16,combined_hybrid_cases=4,combined_hybrid_calls=32,local_model_case_bodies=True,coordinator_case_body_edits=False,report=str(ROOT/'verification/biwn-gpu-consumer6380-checks.json'))
    workmap.update(status=checkpoint['status'],scope=scope)
    workmap['draw_chain'].update(C_consumer6380_verified=True,C_full_draw_chain_verified=False,hybrid_C_consumer_calls=32,hybrid_report=str(ROOT/'verification/biwn-gpu-consumer6380-hybrid-checks.json'),remaining_C_programs=remaining)
    save(session/'remaining-draw-GPU-workmap.json',workmap)
    save(session/'gpu-render-6380-overlay/C-generation.json',dict(**package,publication_status=checked['publication_status'],standalone_report=str(ROOT/'verification/biwn-gpu-consumer6380-checks.json'),hybrid_report=str(ROOT/'verification/biwn-gpu-consumer6380-hybrid-checks.json')))
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json']:
        path=ROOT/name;value=read(path);value.update(consumer6380_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:36consumer6380comparisons/16guards and4combinedhybridchains passed.',model_jobs='Terminal:local27B author completed in169.75seconds; model idle at publication.')
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: local27B first consumer6380 draft accepted unchanged in36originalGPUcases and4combineddrawchains.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope)
        save(path,value)
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_render_queue_answer=scope,checked_projection_scope=scope,consumer6380_checkpoint=checkpoint);save(ROOT/'verification/world-actor-checked-examples.json',examples)
    path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="('hybrid_GPU_setup57_draw_chain','biwn-gpu-setup57-integer-hybrid-checks.json')]:"
    if needle in text:text=text.replace(needle,"('hybrid_GPU_setup57_draw_chain','biwn-gpu-setup57-integer-hybrid-checks.json'),('GPU_consumer6380_program','biwn-gpu-consumer6380-checks.json'),('combined_GPU_setup57_consumer6380_draw_chain','biwn-gpu-consumer6380-hybrid-checks.json')]:")
    needle="    projection_checkpoint=root/'verification/projection-full-coverage-checkpoint.json'"
    insert="    consumer_checkpoint=root/'verification/consumer6380-checkpoint.json'\n    if consumer_checkpoint.exists():runtime['GPU_consumer6380_checkpoint']=json.loads(consumer_checkpoint.read_text())\n"
    if insert not in text:text=text.replace(needle,insert+needle)
    path.write_text(text)
    audit=ROOT/'verification/consumer6380-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');audit.mkdir(parents=True);snapshot=audit/'snapshot';snapshot.mkdir()
    files=[ROOT/'scripts'/name for name in ['draft_gpu6380_local.py','package_gpu6380_candidate.py','probe_biwn_gpu_consumer6380.py','check_biwn_gpu_consumer6380.py','probe_biwn_gpu_consumer6380_hybrid.py','biwn_consumer6380_probe_bridge.c','biwn_consumer6380_hybrid_bridge.c','prepare_consumer6380_evidence.py']]
    files+=[ROOT/'verification'/name for name in ['consumer6380-checkpoint.json','biwn-gpu-consumer6380-original-probes.json','biwn-gpu-consumer6380-checks.json','biwn-gpu-consumer6380-hybrid-checks.json','consumer6380-probe-device-build.json','consumer6380-hybrid-device-build.json']]
    files+=[source/name for name in package['source_sha256']]
    files+=[ROOT/'tools'/name for name in ['libbiwn-consumer6380-probe.dylib','libbiwn-consumer6380-hybrid.dylib']]
    files+=[session/'remaining-draw-GPU-workmap.json']
    for p in files:shutil.copy2(p,snapshot/p.name)
    shutil.copytree(author,audit/'local-author',dirs_exist_ok=True)
    save(audit/'manifest.json',dict(recorded_at=now,files=[dict(source=str(p),sha256=sha(p))for p in files]))
    note='BLACK ICE WHITE NOISE — LOCAL GPU6380 C ACCEPTED\n'+now+'\n\n'+scope+'\n\nWHO DID WHAT\nOne local27B Author, fresh context, typed decoded operands and coordinator interface contract;169.75seconds. All67case bodies accepted unchanged on first draft. Codex supplied framework/primitives/native observer/checks/hybrid integration and reviewed acceptance. Original pinned GPU is an oracle, not a model agent. No Codex subagents or new training/default model changes. Native Chat remains unavailable after the prior UI timeout; this author used local API.\n\nHARNESS ISSUE\nFirst native probe failed before testing the model because Codex omitted lab_movement_setup. Resolved by initializing existing trace symbols; original source/core and model body unchanged. Failed run remains terminal evidence.\n\nEXACT PROMPTS AND RESPONSE\n'+str(author/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\n'
    (audit/'readable-results.txt').write_text(note);(ROOT/'CURRENT DECOMPILATION.txt').write_text(note+'\nAUDIT\n'+str(audit)+'\n')
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    save(ROOT/'verification/consumer6380-review.json',dict(directory=str(audit),recorded_at=now))
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(dict(published_components=118,source_instruction_coverage=[67,67],cases=36,guards=16,combined_hybrid_cases=4,combined_hybrid_C_consumer_calls=32,coordinator_case_body_edits=False,audit=str(audit))))
if __name__=='__main__':main()
