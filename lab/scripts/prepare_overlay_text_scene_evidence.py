"""Publish source formatter/fullCPU overlay-text and zero reached render scripts."""
import hashlib,json,shutil,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    scene=read(ROOT/'verification/biwn-disc-world-overlay-text-checks.json');fmt=read(ROOT/'verification/biwn-formatter-cpu-checks.json');text=read(ROOT/'verification/biwn-overlay-text-cpu-checks.json');previous=read(ROOT/'verification/scene-display-list-checkpoint.json')
    assert scene['cases']==16 and scene['render_frames']==scene['display_list_calls']==scene['overlay_text_calls']['0x181f8']==1008
    assert scene['remaining_render_scripts']=={'0xe0f2':0,'0xe148':0}and scene['GPU_scene_stats']['submissions']==3024 and not scene['GPU_scene_stats']['native_GPU_steps']and not scene['GPU_scene_stats']['forbidden_GPU_attempts']
    assert fmt['CPU_cases']==3038 and fmt['source_instruction_coverage']==[321,323]and fmt['host_guards']==17
    assert text['CPU_cases']==2077 and text['source_instruction_coverage']==[641,642]and text['reachable_instruction_coverage']==[641,641]and text['host_guards']==15
    for name,digest in {**scene['source_sha256'],**fmt['source_sha256'],**text['source_sha256']}.items():assert sha(source/name)==digest
    assert sha(ROOT/'tools/libbiwn-scene-render-device.dylib')==scene['device_library_sha256']
    assert sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib')=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    raw=read(Path(scene['directory'])/'fixtures.json');covered={pc for r in raw for pc in r['original']['steps']};generation=read(session/'overlay-text-fullCPU-generation.json');fmtgen=read(session/'formatter-fullCPU-generation.json')
    world_scripts={hex(target):sum(sum(c['target']==target for c in r['rebuilt']['world_calls'])for r in raw)for target in [0x1b786,0x19f2c,0x19fda]};assert not any(world_scripts.values())
    observation=Path('/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/biwn-disc-world-overlay-text/20261014T031335.623918Z/framebuffer-observation');sample=read(observation/'observation.json');assert (observation/'C-final-RAM.bin').read_bytes()==(observation/'original-final-RAM.bin').read_bytes()
    image=ROOT/'verification/current-C-scene-geometry.png';shutil.copy2(observation/'C-geometry.png',image);assert sha(image)==sample['png_sha256']
    sample.update(image_path=str(image),observation_directory=str(observation),rendered_by='C path of separately compared native/C live scene',visual_review='Recognizable street and character geometry observed; no composited HUD/OP scanout claim.');save(ROOT/'verification/current-C-scene-geometry.json',sample)
    scope=('The bounded16case C scene now removes every reached rendering-helper script: actual181F8overlay/fullsourceformatter/text/multiply/display-list, scene clear/rotation/geometryrecords/CPU submissions and C GPU geometry/projection/dispatcher/setup/consumer/material/experimentalresident execute. '
        '1008overlay/display/rendercycles,3024GPUsubmissions,720worldupdates,2048actoriterations,6144handoffs and32disc payloads3080416bytes match original. FullCPU/private/global scratch/main2MBRAM including device-produced framebuffer bytes compare; each GPU submission architecture/4KBRAM/PCcount/hash also matches. Cpath executes zerooriginalGPU instructions. '
        '3038native+independentUnicorn+C formatter/unsignedmath cases cover321normal instructions of323source,17guards; source divisorzero exception path2instructions excluded. '
        '2077native+Unicorn+C overlay/text/multiply cases coverall641reachable of642sourceinstructions,15guards. BRA14AC6 is unreachable because sourceD0mask38hex allowsmultiples8, and priorCMP8/BEQ/BLT/TST/BEQ consume everypossiblevalue. '
        'Sourceformatting includes d/u/o/x/c/s/percent,long/word arguments,padding and254characterlimit,actual globaldigitscratch; hostsnprintf adapter removed from this scene. '
        'OnlyrenderE0F2/E148 remainconfigured, bothunreached. Threeworldhelpers1B786/19F2C/19FDA remainconfigured butunreached. Live font3/alignment/stringformatter branches are unreached; broader standalone proofs coverthem.15othercontexts blocked. '
        'Geometry retains declaredperframeGPUreset/seed/fixedRAMfixture; latercontext inheritedwithinframe. Shared synchronous pinned emulatorblitter/BIOStransfer/completion adapters/assistedstartup/clock+inputfixtures remain. GlobalGPUcontext,othermodes/scenes/tasks/audio/boot/objectprocessor/scanout/rasterbackend accuracy and playablefullgame incomplete. '
        'Resident remains experimental83unexercised instructions inits standaloneproof. Exportedgeometryplane matches originalRAM andshowsrecognizablestreet/character; it is not compositedHUD/scanout or playablegame. '
        '130selectedcomponents120CPU/10GPU: sevennewnormalreturn sourceformatter/unsignedhelpers; fivealreadycountedoverlay/text/multiply gainfullCPUlinkage. Counts are not completionpercentage. Localmodel171instructionbodies unchanged; this source-specific code/integration is coordinator generated. NativeLMStudioChat unverified and latestSDKshort-answer formatting bug remainsopen; no newtraining/defaultmodel/presetchange.')
    checkpoint={**previous,'recorded_at':now,'status':scene['status'],'published_components':130,'processor_components':{'CPU':120,'GPU':10},'new_components':7,'new_source_function_entries':fmt['source_function_entries'],'scope':scope,'report':str(ROOT/'verification/biwn-disc-world-overlay-text-checks.json'),
        'overlay_text_fullCPU':True,'overlay_text_live_calls':scene['overlay_text_calls'],'remaining_render_scripts':scene['remaining_render_scripts'],'reached_render_helper_scripts':0,'remaining_world_scripts':world_scripts,'reached_world_helper_scripts':0,
        'formatter_standalone':{k:fmt[k]for k in ['CPU_cases','source_instruction_coverage','normal_return_instruction_coverage','excluded_zero_divisor_exception_path','host_guards','source_function_entries']},
        'overlay_text_standalone':{k:text[k]for k in ['CPU_cases','source_instruction_coverage','reachable_instruction_coverage','unreachable_instructions','unreachable_basis','host_guards','source_function_entries']},
        'live_overlay_text_instruction_coverage':[sum(r['address']in covered for r in generation['instructions_decoded']),642],
        'live_formatter_instruction_coverage':[sum(r['address']in covered for r in fmtgen['instructions_decoded']),323],
        'wholeCPU_mainRAM_private_global_and_framebuffer_match':True,'source_formatter_adapter_removed_in_current_scene':True,
        'geometry_sample':sample,'latest_SDK_plain_answer_formatting_verified':False,
        'next_work':'Replace/unexercise remaining mode2 helpersE0F2/E148 and threeworldhelpers1B786/19F2C/19FDA; extend actual movement/camera input and scene/task stimuli. Remove perframeGPUreset/globalcontext gap, strengthen resident paths, unblockedtasks/audio/boot/objectprocessor/scanout/backend accuracy. Fix SDK/MLX short-answer reasoning markers and verify native easyChat/advertising workflows.'}
    save(ROOT/'verification/overlay-text-scene-checkpoint.json',checkpoint)
    validation=read(session/'boot-slice-validation.json')
    if 'source_formatter_unsigned_math_fullCPU'not in validation:
        assert validation['portable_C_component_count']==123 and validation['processor_component_counts']=={'CPU':113,'GPU':10};validation['portable_C_component_count']=130;validation['processor_component_counts']['CPU']=120
    assert validation['portable_C_component_count']==130 and validation['processor_component_counts']=={'CPU':120,'GPU':10}
    validation.update(source_formatter_unsigned_math_fullCPU=fmt,overlay_text_multiply_fullCPU=text,overlay_text_scene_checkpoint=checkpoint,latest_aggregate_update=now,component_count_scope=scope);save(session/'boot-slice-validation.json',validation)
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json','verification/world-actor-checked-examples.json']:
        p=ROOT/name;v=read(p);v.update(overlay_text_scene_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':v['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':v['latest_checked_status']=scope
        if name=='verification/setup-status.json':v['game_work']=scope
        if name=='verification/current-runtime-state.json':v.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:3038formatter/2077overlaytext native+Unicorn+C comparisons and16integrated scene cases passed; one new read-only geometry-plane capture passed/visually reviewed.',model_jobs='No new local model code generation/training this turn; latest SDKformatting failure retained, no passing current answer claimed.')
        if name=='verification/requirements-audit.json':
            v.update(recorded_at_utc=now,this_goal_turn_classification='Progress: fullsource formatter/unsignedmath and fullCPUoverlay/text/multiply accepted; allreached rendering scripts removed in bounded16case scene.',next_safe_work=checkpoint['next_work'])
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=scope
        if name=='verification/world-actor-checked-examples.json':v.update(checked_world_actor_scope=scope,checked_render_queue_answer=scope,checked_projection_scope=scope)
        save(p,v)
    audit=ROOT/'verification/overlay-text-scene-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');audit.mkdir(parents=True);snap=audit/'snapshot';snap.mkdir()
    files=[ROOT/'scripts'/n for n in ['generate_biwn_formatter_cpu.py','check_biwn_formatter_cpu.py','generate_biwn_overlay_text_cpu.py','check_biwn_overlay_text_cpu.py','check_biwn_disc_scene_actors.py','check_biwn_disc_scene_overlay_cpu.py','prepare_overlay_text_scene_evidence.py']]+[ROOT/'verification'/n for n in ['biwn-formatter-cpu-checks.json','biwn-overlay-text-cpu-checks.json','biwn-disc-world-overlay-text-checks.json','overlay-text-scene-checkpoint.json','current-C-scene-geometry.json','current-C-scene-geometry.png']]+[source/n for n in {**fmt['source_sha256'],**text['source_sha256']}]
    for p in files:shutil.copy2(p,snap/p.name)
    save(audit/'manifest.json',dict(recorded_at=now,files=[dict(source=str(p),sha256=sha(p))for p in files],formatter_directory=fmt['directory'],overlay_text_directory=text['directory'],scene_directory=scene['directory'],geometry_observation_directory=str(observation)))
    note='BLACK ICE WHITE NOISE — FULL SOURCE FORMATTER / OVERLAY / TEXT SCENE\n'+now+'\n\n'+scope+'\n\nWHO DID WHAT / PROMPTS\nCodex coordinator generated fixed C blocks from pinned source bytes, added predecrement/frame/register arithmetic forms, supplied fullCPU providers and original/independentCPU harnesses, integrated source render callbacks and captured the matching geometryplane. No localLLMprompt/code-author role or training in this upgrade. Prior171localmodel instruction bodies and exactroleprompts remain unchanged/in priorrun audits.\n\nREJECTED / REPAIRED CHECKS\nInitial generator count322 assertion corrected to actual323 decoded instructions. First formatter harness inherited10kCPUinstruction allowance and stopped on a valid longer fixture; increasednative/Unicorn/Cworkallowance. Expanded formatter suite lacked unsupported-specifier>u branch; added actual%z input, allnormal paths passed. Overlay/text suite leftBRA14AC6unobserved; source mask/branch analysis proves unreachable, so no forcedPCcoverage. Stable controlledfont/validmarkerfixtures retain realblitterRAMeffects; no private/global/pixel masks.\n\nCURRENT DEPENDENCIES\nOnlytwo configuredrender scripts remainunreached; threeconfiguredworldscripts also0calls. Sixof21contexts runnable; fullgame unfinished. Sharedblitter/BIOS/completion/startup/clock/input/perframeGPUresetfixtures retained. Livefont3/alignment/stringformathelpercalls0; standalone2077/3038cases supply their separate coverage, not a live-source claim.\n\nNEXT\n'+checkpoint['next_work']+'\n\nAUDIT\n'+str(audit)+'\nGeometrysample: '+str(image)+'\nFull goal active/incomplete.\n'
    (audit/'readable-results.txt').write_text(note);(ROOT/'CURRENT DECOMPILATION.txt').write_text(note)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+note)
    p=ROOT/'START HERE.txt';s=p.read_text();a=s.index('LATEST GAME RESULT\n');b=s.index('LOCAL INFERENCE RESULT\n',a);p.write_text(s[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+s[b:])
    save(ROOT/'verification/overlay-text-scene-review.json',dict(recorded_at=now,directory=str(audit)))
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(dict(components=130,formatter_cases=3038,overlay_text_cases=2077,live_cases=16,reached_render_scripts=0,reached_world_scripts=0,geometry_image=str(image),audit=str(audit))))
if __name__=='__main__':main()
