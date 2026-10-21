"""Publish standalone52E0/E19E, retain distinction from original draw oracle."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    gpu=read(ROOT/'verification/biwn-gpu-projection-checks.json');cpu=read(ROOT/'verification/biwn-gpu-projection-submit-cpu-checks.json');draw=read(ROOT/'verification/biwn-gpu-draw-original-probes.json')
    assert gpu['GPU_cases']==48 and gpu['source_instruction_coverage']==[450,450]and gpu['actual_live_prefix_cases']==16 and gpu['declared_camera_variant_cases']==32 and gpu['host_guards']==16
    assert cpu['CPU_cases']==128 and cpu['source_instruction_coverage']==[14,14]and cpu['wait_instruction_coverage']==[3,3]and cpu['host_guards']==18
    assert draw['cases']==4 and draw['commands']==['0x57a0','0x6380','0x6460']and draw['original_dispatcher_executed']and not draw['C_draw_reconstructed']
    for proof in [gpu,cpu]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']in ['terminal_pass','terminal_bounded_pass']
        for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
    observed_draw=read(Path(draw['directory'])/'cases.json');assert all(r['drawing_list_head_after']==0 and r['GPU_busy_after']==0 and r['GPU_command_after']=='0xffffffff'for r in observed_draw)
    assert [r['framebuffer_changed_bytes']for r in observed_draw]==[20153,20153,20152,0]
    validation=read(session/'boot-slice-validation.json')
    if 'GPU_projection_program'not in validation:
        assert validation['portable_C_component_count']==114 and validation['processor_component_counts']=={'CPU':111,'GPU':3}
        validation['portable_C_component_count']=116;validation['processor_component_counts']={'CPU':112,'GPU':4}
    assert validation['portable_C_component_count']==116 and validation['processor_component_counts']=={'CPU':112,'GPU':4}
    for proof,name in [(gpu,'biwn-gpu-projection-checks.json'),(cpu,'biwn-gpu-projection-submit-cpu-checks.json')]:
        proof.update(publication_status='accepted_standalone_C_full_instruction_comparison_not_live_renderer_integration',new_published_components=1)
        save(ROOT/'verification'/name,proof);save(Path(proof['directory'])/'report.json',proof)
    validation.update(GPU_projection_program=gpu,CPU_projection_submit=cpu,original_GPU_draw_chain=draw,latest_aggregate_update=now,component_count_scope='Two new standalone components:GPU52E0projection andfullCPU E19Esubmission.116selected112CPU/4GPU is not completion percentage. E19E remains scripted in existing live scene until drawchain is reconstructed and coherent GPUcontext integrated.')
    save(session/'boot-slice-validation.json',validation)
    pending={k:gpu[k]for k in ['status','GPU_cases','actual_live_prefix_cases','declared_camera_variant_cases','source_instruction_coverage','uncovered_instruction_addresses','host_guards','original_GPU_core_calls_on_C_side','live_CPU_E19E_linked','full_renderer_verified','matched','limits']}
    pending.update(report=str(ROOT/'verification/biwn-gpu-projection-checks.json'),source_E19E_wrapper_reconstructed=True,E19E_standalone=dict(report=str(ROOT/'verification/biwn-gpu-projection-submit-cpu-checks.json'),CPU_cases=128,source_instruction_coverage=[14,14],actual_E098_wait=True,wait_instruction_coverage=[3,3],host_guards=18,CPU_oracles=['pinned_native68000','independentUnicorn'],live_renderer_linked=False,mailbox_busy_ack_transitions='declared_device_inputs_GPU_not_executed_in_this_CPU_test'),projection_list_head_values=[0,47],later_draw_programs=['0x57a0','0x58a0','0x6380','0x6460'],later_draw_programs_reconstructed=False,published_component_count_includes_GPU52E0=True,published_component_count_includes_CPU_E19E=True,selected_component_count=116,scope='StandaloneCaccepted; integrationpending. OriginalGPUdrawchain below is separate and does not validate reconstructedCdraw.',original_draw_chain=dict(report=str(ROOT/'verification/biwn-gpu-draw-original-probes.json'),cases=4,original_resident_dispatcher_executed=True,queued_commands=['0x57a0','0x6380','0x6460'],resident_program='0x58a0',all_lists_consumed=True,framebuffer_changed_bytes=[20153,20153,20152,0],C_draw_reconstructed=False,full_viewport_proved=False,source_CPU_wrappers_executed=False,observer='GPUstate and mainRAM snapshots;blitter read-register-window snapshots are not fulldecodedhardwarestate. In-processblittercontext preserved.',diagnostic_preview='CRYinterpretedframebuffer currently contains noisy/banded output; no verified viewport/scanout claim.'))
    checkpoint=dict(recorded_at=now,status='standalone_GPU52E0_all450_and_CPU_E19E_all14_accepted_original_draw_chain_mapped_integration_pending',published_components=116,processor_components={'CPU':112,'GPU':4},new_components=2,live_GPU4D80_calls=1008,live_E19E_calls=0,configured_live_renderer_scripts=6,reached_live_renderer_scripts=4,pending_integration_evidence=pending,full_viewport_proved=False,full_game_complete=False,full_goal_status='active incomplete',next_work='Reconstruct GPUresidentdispatcher and57A0/58A0/6380/6460drawchain; verifyframebufferandcoherentGPUstate then integrateCPU E19E/E202. ContinuefullCPUdisplay-list/overlay,remainingtasks/scenes,audio,uninterruptedboot,fullgame/physicalchecks and easy native inference/advertising evaluation.')
    save(ROOT/'verification/projection-full-coverage-checkpoint.json',checkpoint)
    workmap=read(session/'remaining-draw-GPU-workmap.json');workmap['status']=checkpoint['status'];workmap['programs'][0].update(status=gpu['publication_status'],source_instruction_coverage=[450,450],GPU_cases=48,live_CPU_wrapper_linked=False)
    if not any(p['CPU_header']=='0x6460'for p in workmap['programs']):
        program=read(session/'gpu-render-6460-overlay/initial-linear-decode.json');workmap['programs'].append({k:v for k,v in program.items()if k not in ['rows','decoder']})
    workmap['CPU_wrappers']['0xe19e']={'program':'GPU52E0','C_standalone_verified':True,'source_instructions':14,'cases':128,'live_linked':False}
    workmap['draw_chain'].update(original_dispatcher_executed=True,draw_chain_verified='OriginalGPUoracleonly_fourcases',queued_commands=['0x57a0','0x6380','0x6460'],C_reconstructed=False,report=str(ROOT/'verification/biwn-gpu-draw-original-probes.json'))
    workmap['scope']='48GPUcases/all450 and128CPUcases/all14 pass standalone. OriginalGPUdispatcherdrawchain consumeslist in4cases, but Cdraw/integration/fullviewport/game remainunfinished.116selected112CPU/4GPU, notcompletionpercentage.';save(session/'remaining-draw-GPU-workmap.json',workmap)
    for path in [session/'gpu-render-52e0-overlay/C-generation.json',session/'gpu-projection-submit-fullCPU-generation.json']:
        manifest=read(path);manifest.update(status='accepted_standalone_full_instruction_comparison_live_integration_pending',whole_game_complete=False,evidence=['verification/biwn-gpu-projection-checks.json','verification/biwn-gpu-projection-submit-cpu-checks.json']);save(path,manifest)
    scope='GPU52E0projection nowmatches48cases/all450instructions/16guards; fullCPU E19EsubmissionwithactualE098waitmatches128native+Unicorncases/all14+3instructions/18guards. BotharestandaloneandunlinkedtoexistingliveCscene. OriginalGPUresidentdispatcher57A0/58A0/6380/6460drawchainconsumeslistin4cases; framebufferbytechanges20153/20153/20152/0arenotCdraworverifiedviewport.116selectedcomponents112CPU/4GPU,notcompletionpercentage. ExistingliveGPU4D80 remains1008calls; sixrenderer scripts remainconfigured/fourreached,includingE19E/E202. Fullgame,viewport,audio,boot,remainingtasks/scenesandnativeeasyinference/ad evaluationincomplete.'
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json']:
        path=ROOT/name;value=read(path);value.update(projection_full_coverage_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:48GPUprojection,128CPUsubmission and4originaldrawchain cases.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':value.update(recorded_at_utc=now,this_goal_turn_classification='Progress:all450projectioninstructions andfullCPU14submissionstandaloneproved;originaldrawchain exposes6460 andresidentdispatcher.',next_safe_work=checkpoint['next_work'])
        save(path,value)
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples['checked_projection_scope']=scope;save(ROOT/'verification/world-actor-checked-examples.json',examples)
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps({k:checkpoint[k]for k in ['status','published_components','processor_components','new_components','live_E19E_calls','full_viewport_proved']}))
if __name__=='__main__':main()
