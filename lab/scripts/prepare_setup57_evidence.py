"""Publish checked local-model setup57 case bodies and hybrid scope."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    checked=read(ROOT/'verification/biwn-gpu-setup57-candidate-checks.json');hybrid=read(ROOT/'verification/biwn-gpu-setup57-hybrid-checks.json');candidate=Path(checked['candidate_directory']);package=read(candidate/'package.json')
    assert checked['GPU_cases']==64 and checked['source_instruction_coverage']==[73,73]and checked['host_guards']==14 and not checked['original_GPU_calls_on_C_side']
    assert hybrid['cases']==4 and hybrid['C_setup_calls']==4 and not hybrid['original_GPU57A0_executed']and hybrid['other_original_GPU_programs_executed']and not hybrid['full_renderer_C']
    for name,digest in package['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest==hashlib.sha256((candidate/name).read_bytes()).hexdigest()
    body=(candidate/'candidate-cases.txt').read_text();assert body in(source/'biwn_gpu_setup57.c').read_text()
    assert hashlib.sha256(body.encode()).hexdigest()==package['case_bodies_sha256']
    roles=[]
    for role,key,result_name in [('Author','GPU57-local-author-current.json','author.json'),('Reviewer','GPU57-local-reviewer-current.json','reviewer.json'),('Remediator','GPU57-local-remediator-current.json','remediator.json')]:
        folder=Path(read(ROOT/'verification'/key)['directory']);protocol=read(folder/'protocol.json');result=read(folder/result_name)
        roles.append(dict(role=role,model_key=protocol['model']['model_key'],directory=str(folder),seconds=result['seconds'],usage=result['usage'],accepted=role=='Remediator',compiled=role=='Remediator',executed=role=='Remediator',fresh_context=True,case_body_edits_by_coordinator=False,static_review=read(folder/'static-review.json')))
    checked.update(publication_status='accepted_local_model_case_bodies_with_coordinator_framework_standalone_and_hybrid_checks',source_sha256=package['source_sha256'],case_body_edits_by_coordinator=False,new_components=1,hybrid_evidence=str(ROOT/'verification/biwn-gpu-setup57-hybrid-checks.json'))
    save(ROOT/'verification/biwn-gpu-setup57-checks.json',checked)
    validation=read(session/'boot-slice-validation.json')
    if 'GPU_setup57_program'not in validation:
        assert validation['portable_C_component_count']==116 and validation['processor_component_counts']=={'CPU':112,'GPU':4};validation['portable_C_component_count']=117;validation['processor_component_counts']['GPU']=5
    assert validation['portable_C_component_count']==117 and validation['processor_component_counts']=={'CPU':112,'GPU':5}
    validation.update(GPU_setup57_program=checked,hybrid_GPU_setup57_draw_chain=hybrid,latest_aggregate_update=now,component_count_scope='One new GPU57A0 setup program. Local27B authored73casebodies unchanged; coordinator supplied framework/primitives/facts/tests.117selected112CPU/5GPU is not completion percentage. Four hybrid tests retain original dispatcher and other draw programs; fullCdraw and liveCPU integration unfinished.')
    save(session/'boot-slice-validation.json',validation)
    setup=dict(report=str(ROOT/'verification/biwn-gpu-setup57-checks.json'),GPU_cases=64,source_instruction_coverage=[73,73],host_guards=14,local_model_authored_case_bodies=True,local_model='local/advertising-qwen38,27B6bit everyday base',coordinator_case_body_edits=False,coordinator_authored='interface, fixed execution engine, integer primitives, decoder facts, native observer, checks and integration',accepted_candidate_directory=str(candidate),roles=roles,original_GPU_calls_inside_standalone_C=0,blitter_backend='Shared pinned emulator blitter; reset for both standalone paths',copied_resident_program=dict(CPU_header='0x58a0',GPU_destination='0xf03440',bytes=2776,source_SHA256='9f14522e92bc2a5b3d9bb2db0adb7a2dfb897709bf3f500ef7c6f58203ef25ff'),queued_command='0x6380',hybrid=dict(report=str(ROOT/'verification/biwn-gpu-setup57-hybrid-checks.json'),cases=4,C_setup_calls=4,natural_preceding_blitter_context_preserved=True,original_GPU57A0_executed=False,other_original_GPU_programs_executed=True,remaining_original_components=['resident dispatcher F031BE','58A0 resident drawing','6380 list consumer','6460 material program'],source_CPU_E19E_E202_executed=False,full_renderer_C=False,full_viewport_proved=False),limitations=checked['limits'],evaluation_scope='Task-specific success after two rejected drafts, with both model and input facts changed. Not a controlled model ranking, general code reliability or independent model verification.')
    checkpoint=dict(recorded_at=now,status='local27B_GPU57A0_case_bodies_accepted_after_two_rejected30B_drafts_standalone64_hybrid4_passed_full_game_incomplete',published_components=117,processor_components={'CPU':112,'GPU':5},new_components=1,setup57=setup,full_goal_status='active incomplete',full_renderer_C=False,full_viewport_proved=False,next_work='Reconstruct resident dispatcher and58A0/6380/6460 with typed decoder facts and checked C; verify memory/control/framebuffer effects, then connect fullCPU E19E/E202 and coherent GPUcontext. Continue overlay/display-list, other tasks/scenes/audio/boot/fullgame and easy native inference/advertising evaluation.')
    save(ROOT/'verification/setup57-checkpoint.json',checkpoint)
    previous=read(ROOT/'verification/projection-full-coverage-checkpoint.json');previous['pending_integration_evidence'].update(GPU57A0_setup=setup,selected_component_count=117,later_draw_programs=['resident dispatcher F031BE','0x58a0','0x6380','0x6460'],later_draw_programs_reconstructed=False)
    previous['pending_integration_evidence']['original_draw_chain']['C_setup57_now_verified_in_separate_hybrid_proof']=True
    previous['pending_integration_evidence']['original_draw_chain']['scope']='Historical original-only draw proof; newer C57A0 hybrid proof is separate. Neither proves fullyC draw/viewport.'
    save(ROOT/'verification/projection-full-coverage-checkpoint.json',previous)
    manifest=read(session/'gpu-render-57a0-overlay/C-generation.json');manifest.update(status='accepted_local_model_case_bodies_standalone64_and_hybrid4',hybrid_evidence=str(ROOT/'verification/biwn-gpu-setup57-hybrid-checks.json'),roles=roles,whole_game_complete=False);save(session/'gpu-render-57a0-overlay/C-generation.json',manifest)
    workmap=read(session/'remaining-draw-GPU-workmap.json');workmap['status']=checkpoint['status']
    for program in workmap['programs']:
        if program['CPU_header']=='0x57a0':program.update(status=checked['publication_status'],C_reconstructed=True,source_instruction_coverage=[73,73],standalone_cases=64,hybrid_cases=4,report=str(ROOT/'verification/biwn-gpu-setup57-checks.json'))
    workmap['draw_chain'].update(C_setup57_verified=True,C_full_draw_chain_verified=False,hybrid_C_setup_calls=4,hybrid_report=str(ROOT/'verification/biwn-gpu-setup57-hybrid-checks.json'))
    workmap['scope']='C57A0setup accepted:64 standalone cases/all73instructions/14guards and4hybrid originaldrawchain cases. Otherdrawprograms/dispatcher remainoriginal andunreconstructed; fullCviewport/game incomplete.117selected112CPU/5GPU,notcompletionpercentage.';save(session/'remaining-draw-GPU-workmap.json',workmap)
    scope='Local27B authored all73GPU57A0instructioncasebodies unchanged. Coordinator framework/primitives/decodedfacts/tests;64standalonecases/14guards and4hybrid originalGPUdrawchaincases pass. Two30BAuthor/Reviewerdrafts rejectedbeforecompilation. OtherGPUdrawprogramsanddispatcherremainoriginal; sourceCPU E19E/E202notruninhybrid.117selected112CPU/5GPU,notcompletionpercentage. FullCviewport/game/audio/boot/remainingtasksunfinished.'
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json']:
        path=ROOT/name;value=read(path);value.update(setup57_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':
            value['chat_frontend']['game']['status']=scope
            value['models']['game']['latest_GPU57_drafting_probe']='Two30B-A3B Author/Reviewer drafts rejected before compilation for memory/bank/flags/address errors. Everyday27B Remediator with typed decoder operands produced73casebodies accepted unchanged by64nativeGPUcases/14guards and4hybrid checks. Multiple factors changed; no general model ranking. See verification/setup57-checkpoint.json.'
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:64standaloneGPU57cases/14guards and4hybridcases. Model output reviewed; ordinary assistant check pending.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':value.update(recorded_at_utc=now,this_goal_turn_classification='Progress:localmodelcasebodiesacceptedunchangedaftertoolassistedrepair;64standaloneand4hybriddrawchecks.',next_safe_work=checkpoint['next_work'])
        save(path,value)
    script=ROOT/'scripts/summarize_biwn_checks.py';text=script.read_text();needle="('original_GPU_draw_chain','biwn-gpu-draw-original-probes.json')]:"
    if needle in text:text=text.replace(needle,"('original_GPU_draw_chain','biwn-gpu-draw-original-probes.json'),('GPU_setup57_program','biwn-gpu-setup57-checks.json'),('hybrid_GPU_setup57_draw_chain','biwn-gpu-setup57-hybrid-checks.json')]:");script.write_text(text)
    tool=ROOT/'chat_tools.py';text=tool.read_text();needle='GPU52E0 or10A684 questions belong to rendering:'
    if needle in text:text=text.replace(needle,'GPU52E0, GPU57A0 setup, local code authorship or10A684 questions belong to rendering:');tool.write_text(text)
    for script_name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script_name)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(dict(published_components=117,GPU_cases=64,instruction_coverage=[73,73],guards=14,hybrid_cases=4,local_case_body_edits=False)))
if __name__=='__main__':main()
