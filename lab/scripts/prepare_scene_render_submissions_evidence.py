"""Publish verified bounded scene linkage; preserve historical phase proofs."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    scene=read(ROOT/'verification/biwn-disc-world-render-submissions-checks.json');cpu=read(ROOT/'verification/biwn-gpu-draw-submit-cpu-checks.json');old=read(ROOT/'verification/dispatcher-C-draw-checkpoint.json')
    assert scene['cases']==16 and scene['render_frames']==1008 and scene['CPU_submission_calls']=={'0xe19e':1008,'0xe202':1008}
    assert scene['GPU_scene_stats']['submissions']==3024 and not scene['GPU_scene_stats']['native_GPU_steps']and not scene['GPU_scene_stats']['forbidden_GPU_attempts']
    assert cpu['CPU_cases']==128 and cpu['source_instruction_coverage']==[5,5]and cpu['host_guards']==18
    for name,digest in {**scene['source_sha256'],**cpu['source_sha256']}.items():assert sha(source/name)==digest
    assert sha(ROOT/'tools/libbiwn-scene-render-device.dylib')==scene['device_library_sha256']
    assert sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib')=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    scope=('Sixteen bounded disc-scene cases now link actual CPU E19E/E202 submissions and E098 waits to C geometry/projection/dispatcher/setup/consumer/material/experimental resident routines. '
        '1008render cycles/3024GPU submissions,720world updates,2048actor iterations,6144task handoffs and32disc payloads (3080416bytes) match the original. '
        'Every completed GPU submission compares full architecture/4KB RAM, whole2MB mainRAM and source-PC count/hash; complete CPU/privateframes and scheduler/loading events also compare. '
        'Csubmissions execute zerooriginalGPU instructions under an actual GPUExecguard. The shared pinned synchronous emulator blitter remains. '
        'Geometry starts from a declared GPUreset/seed/fixed4KBfixture eachframe; state after that entry is inherited through projection/draw. This is not fullboot/globalcontext across movement/sprite providers. '
        'Fourrender scripts remain configured:181F8overlay and185B2display eachreached1008; E0F2/E148unreached.15othercontexts blocked. BIOS/completion adapters, assistedstartup, clock/input fixtures remain. '
        'Resident remains experimental with83unexercised instructions in its standalone84case proof; othermodes/scenes/audio/boot/scanout/rasterbackend disagreement/full playable game remain unfinished. '
        '123selected Ccomponents113CPU/10GPU, not a completion percentage. Localmodel instruction bodies remain171 acrosssetup73/consumer67/dispatcher31; this integration and CPU E202code are coordinator authored. '
        'No new training/defaultmodel change. Native LMStudioChat access timed out again; latest installed-tool/SDK checks do not verify native cached provider adoption or visible Chat.')
    checkpoint=dict(recorded_at=now,status=scene['status'],published_components=123,processor_components={'CPU':113,'GPU':10},new_components=1,
        scope=scope,report=str(ROOT/'verification/biwn-disc-world-render-submissions-checks.json'),cases=16,render_cycles=1008,GPU_submissions=3024,
        CPU_E19E_E202_calls=scene['CPU_submission_calls'],C_GPU_statistics={k:v for k,v in scene['GPU_scene_stats'].items()if k!='last_direct_PC_count'},
        complete_CPU_RAM_private_frames_and_handoffs_match=True,per_submission_GPU_architecture_RAM_and_PC_hash_match=True,
        original_GPU_instructions_during_C_submissions=0,geometry_reset_seed_RAM_fixture_retained=True,GPU_context_inherited_within_frame=True,global_GPU_context_proved=False,
        remaining_render_scripts=scene['remaining_render_scripts'],blocked_contexts=15,shared_pinned_blitter=True,
        resident_standalone_instruction_coverage=[1192,1275],resident_experimental=True,local_model_instruction_bodies=171,
        full_game_complete=False,playable=False,native_Chat_verified=False,training_this_turn=False,
        next_work='Replace overlay181F8 and display-list185B2 ABI scripts with fullCPU/privateframe C bodies. Continue other render modes, resident coverage, global GPU context, remaining tasks/scenes/audio/boot/scanout/backend comparison and native easy Chat/advertising evaluation.')
    save(ROOT/'verification/scene-render-submissions-checkpoint.json',checkpoint)
    validation=read(session/'boot-slice-validation.json')
    if 'CPU_E202_draw_submission'not in validation:
        assert validation['portable_C_component_count']==122 and validation['processor_component_counts']=={'CPU':112,'GPU':10}
        validation['portable_C_component_count']=123;validation['processor_component_counts']['CPU']=113
    assert validation['portable_C_component_count']==123 and validation['processor_component_counts']=={'CPU':113,'GPU':10}
    validation.update(CPU_E202_draw_submission=cpu,scene_render_submissions_checkpoint=checkpoint,latest_aggregate_update=now,component_count_scope=scope);save(session/'boot-slice-validation.json',validation)
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json','verification/world-actor-checked-examples.json']:
        p=ROOT/name;v=read(p);v.update(scene_render_submissions_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':v['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':v['latest_checked_status']=scope
        if name=='verification/setup-status.json':v['game_work']=scope
        if name=='verification/current-runtime-state.json':v.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:128CPU E202 standalone comparisons and16integrated scene cases passed.',model_jobs='No model generation in this integration; subsequent local scope question recorded separately.')
        if name=='verification/requirements-audit.json':
            v.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actual CPU submissions connect C GPU draw programs to16bounded disc-scene cases.',next_safe_work=checkpoint['next_work'])
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=scope
        if name=='verification/world-actor-checked-examples.json':v.update(checked_world_actor_scope=scope,checked_render_queue_answer=scope,checked_projection_scope=scope)
        save(p,v)
    audit=ROOT/'verification/scene-render-submissions-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');audit.mkdir(parents=True);snap=audit/'snapshot';snap.mkdir()
    files=[ROOT/'scripts'/n for n in ['generate_biwn_gpu_draw_submit_cpu.py','check_biwn_gpu_draw_submit_cpu.py','check_biwn_disc_scene_actors.py','check_biwn_disc_scene_render_submissions.py','biwn_scene_render_device_bridge.c','prepare_scene_render_submissions_evidence.py']]
    files += [ROOT/'verification'/n for n in ['scene-render-submissions-checkpoint.json','biwn-disc-world-render-submissions-checks.json','biwn-gpu-draw-submit-cpu-checks.json','scene-render-device-build.json']]+[source/n for n in cpu['source_sha256']]+[ROOT/'tools/libbiwn-scene-render-device.dylib']
    for p in files:shutil.copy2(p,snap/p.name)
    save(audit/'manifest.json',dict(recorded_at=now,files=[dict(source=str(p),sha256=sha(p))for p in files],scene_raw_fixtures=str(Path(scene['directory'])/'fixtures.json'),standalone_CPU_directory=cpu['directory']))
    note='BLACK ICE WHITE NOISE — LIVE BOUNDED C SCENE LINKAGE\n'+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex coordinator generated CPU E202, bound existing CPU E19E, supplied deterministic GPU entry fixture, inherited GPU architecture/RAM state, source dispatcher/overlay selection, native/C command guard and per-submission comparison. No new local-model code authorship or model training in this integration. Earlier local roles/complete prompts and responses remain in dispatcher-C-draw-review and referenced model run directories.\n\nPROMPTS / ACTIONS\nThis integration used source instruction facts and executable comparisons, no new LLM prompt. A separate ordinary local assistant question tests how easily the saved evidence is retrieved. Native UI getApp timed out120.62seconds; no visible Chat verified.\n\nVERIFICATION\n128native+independentUnicorn+C E202cases/all5instructions/actualE098all3/18guards. One scene preflight passed, then full16cases passed. Raw full fixture details: '+str(Path(scene['directory'])/'fixtures.json')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active/incomplete.\n'
    (audit/'readable-results.txt').write_text(note);(ROOT/'CURRENT DECOMPILATION.txt').write_text(note+'\nAUDIT\n'+str(audit)+'\n')
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+note)
    p=ROOT/'START HERE.txt';s=p.read_text();a=s.index('LATEST GAME RESULT\n');b=s.index('LOCAL INFERENCE RESULT\n',a);p.write_text(s[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+s[b:])
    save(ROOT/'verification/scene-render-submissions-review.json',dict(directory=str(audit),recorded_at=now))
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:
        subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(dict(selected_components=123,scene_cases=16,render_cycles=1008,GPU_submissions=3024,original_GPU_instructions_during_C=0,audit=str(audit))))
if __name__=='__main__':main()
