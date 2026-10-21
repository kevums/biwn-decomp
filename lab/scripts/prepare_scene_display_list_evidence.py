"""Publish the fullCPU display-list upgrade and live scene linkage."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    scene=read(ROOT/'verification/biwn-disc-world-display-list-checks.json');cpu=read(ROOT/'verification/biwn-display-list-cpu-checks.json');previous=read(ROOT/'verification/scene-render-submissions-checkpoint.json')
    assert scene['cases']==16 and scene['display_list_calls']==scene['render_frames']==1008
    assert scene['remaining_render_scripts']=={'0x181f8':1008,'0xe0f2':0,'0xe148':0}
    assert cpu['CPU_cases']==1025 and cpu['source_instruction_coverage']==[252,254]and cpu['reachable_instruction_coverage']==[252,252]and cpu['host_guards']==17
    for name,digest in {**scene['source_sha256'],**cpu['source_sha256']}.items():assert sha(source/name)==digest
    assert scene['GPU_scene_stats']['submissions']==3024 and not scene['GPU_scene_stats']['native_GPU_steps']and not scene['GPU_scene_stats']['forbidden_GPU_attempts']
    assert sha(ROOT/'tools/libbiwn-scene-render-device.dylib')==scene['device_library_sha256']
    raw=read(Path(scene['directory'])/'fixtures.json');covered={pc for r in raw for pc in r['original']['steps']};generation=read(session/'display-list-fullCPU-generation.json');live_covered=sum(r['address']in covered for r in generation['instructions_decoded'])
    scope=('Display-list185B2 now executes fullCPU C in the bounded16case live scene,1008calls, replacing its ABI script. '
        'Standalone1025native+independentUnicorn+C comparisons cover252of254source instructions (all252reachable; two fixed-positive-literal negativealternates unreachable) and17hostguards. '
        'FullD/A,SR,USP/SSP,whole2MBRAM,sourceLINK/MOVEM/localframe/dynamically allocated private linktable/args/returnframes and orderedbus compare with no private exclusions. '
        'Live16case scene still matches original for1008rendercycles/3024GPUsubmissions,720world updates/2048actoriterations/6144handoffs/32disc payloads3080416bytes. '
        'Cgeometry/projection/dispatcher/setup/consumer/material/experimentalresident execute zerooriginalGPU instructions under an actual guard; GPUarchitecture/RAM and PCcount/hash compare after every CPU submission. '
        'Remaining render scripts:181F8overlay reached1008; E0F2/E148unreached. Overlay still includes its formatter/text dependencies. Display-list packing does not prove objectprocessor/scanout. '
        'Geometry retains a declared perframe GPUreset/seed/fixedRAMfixture; later projection/draw inherit that frame context. Movement/sprite globalGPUcontext, boot,15blockedtasks,othermodes/scenes/audio/scanout/rasterbackend accuracy/fullplayable reconstruction remain unfinished. '
        'Shared pinned synchronous emulator blitter, BIOS/completion adapters, assistedstartup, clock/input fixtures remain. Resident experimental83unexercised instructions in its standaloneproof. '
        '123selectedcomponents113CPU/10GPU unchanged: this upgrades an alreadycounted display function. Localmodel instructionbodies171unchanged; displayfullCPU andintegration coordinator authored. NativeLMStudioChat unverified; no newtraining/defaultmodelchange.')
    checkpoint={**previous,'recorded_at':now,'status':scene['status'],'new_components':0,'scope':scope,'report':str(ROOT/'verification/biwn-disc-world-display-list-checks.json'),
        'display_list_fullCPU':True,'display_list_calls':1008,'display_list_standalone_cases':1025,'display_list_source_instruction_coverage':[252,254],'display_list_reachable_instruction_coverage':[252,252],
        'display_list_live_instruction_coverage':[live_covered,252],'display_list_host_guards':17,'display_list_private_stack_exclusions':[],
        'remaining_render_scripts':scene['remaining_render_scripts'],'next_work':'Replace overlay181F8 and its formatter1B45A/text149AE dependencies with fullCPU C, including private/global scratch effects. Continue other render modes, resident coverage, globalGPUcontext, remaining tasks/scenes/audio/boot/objectprocessor/scanout/backend and native easy Chat/advertising evaluation.'}
    save(ROOT/'verification/scene-display-list-checkpoint.json',checkpoint)
    v=read(session/'boot-slice-validation.json');assert v['portable_C_component_count']==123 and v['processor_component_counts']=={'CPU':113,'GPU':10};v.update(display_list_fullCPU=cpu,scene_display_list_checkpoint=checkpoint,latest_aggregate_update=now,component_count_scope=scope);save(session/'boot-slice-validation.json',v)
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json','verification/world-actor-checked-examples.json']:
        p=ROOT/name;v=read(p);v.update(scene_display_list_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':v['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':v['latest_checked_status']=scope
        if name=='verification/setup-status.json':v['game_work']=scope
        if name=='verification/current-runtime-state.json':v.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:1025fullCPU displaylist comparisons/17guards and16live scene cases passed.',model_jobs='No local model code generation for this upgrade; ordinary inference review recorded separately.')
        if name=='verification/requirements-audit.json':
            v.update(recorded_at_utc=now,this_goal_turn_classification='Progress: fullCPU display-list reconstructed,1025dual-oracle comparisons and16live scene cases passed; script185B2 removed.',next_safe_work=checkpoint['next_work'])
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=scope
        if name=='verification/world-actor-checked-examples.json':v.update(checked_world_actor_scope=scope,checked_render_queue_answer=scope,checked_projection_scope=scope)
        save(p,v)
    audit=ROOT/'verification/scene-display-list-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');audit.mkdir(parents=True);snap=audit/'snapshot';snap.mkdir()
    files=[ROOT/'scripts'/n for n in ['generate_biwn_display_list_cpu.py','check_biwn_display_list_cpu.py','check_biwn_disc_scene_actors.py','check_biwn_disc_scene_display_cpu.py','prepare_scene_display_list_evidence.py']]+[ROOT/'verification'/n for n in ['scene-display-list-checkpoint.json','biwn-display-list-cpu-checks.json','biwn-disc-world-display-list-checks.json']]+[source/n for n in cpu['source_sha256']]+[ROOT/'chat_tools.py']
    for p in files:shutil.copy2(p,snap/p.name)
    save(audit/'manifest.json',dict(recorded_at=now,files=[dict(source=str(p),sha256=sha(p))for p in files],standalone_raw_fixtures=str(Path(cpu['directory'])/'fixtures.json'),live_raw_fixtures=str(Path(scene['directory'])/'fixtures.json')))
    note='BLACK ICE WHITE NOISE — FULLCPU DISPLAY-LIST LINKAGE\n'+now+'\n\n'+scope+'\n\nWHO DID WHAT / PROMPTS\nCodex coordinator extended the build-time source-specific generator for negative frame addressing, LINK/UNLK, frame-relative MOVEM restore and LSR.W. Existing254sourceinstructions generate fixed Cblocks; no runtimeCPUdecode or originalCPUcalls. No local-model author/reviewer role or weighttraining for this upgrade. The first generation attempt rejected negative load addressing; corrected generator then passed8case preflight/all252reachableinstructions, full1025cases/17guards and scene1case preflight/full16cases. Accepted historical logicaldisplay C unchanged.\n\nDEPENDENCIES / NEXT\nOverlay source184instructions has two calls: formatter1B45A andtext149AE. Their older adapters omit fullCPU/private/global effects. Linear formatter decode stops at embedded data1B20E; use source control-flow/table-aware ranges rather than interpreting the table as code. Do not claim overlay/formatter complete from earlier logical proofs.\n'+checkpoint['next_work']+'\n\nRAW AUDIT\n'+str(audit)+'\nStandalone: '+cpu['directory']+'\nLive scene: '+scene['directory']+'\nFull goal active/incomplete.\n'
    (audit/'readable-results.txt').write_text(note);(ROOT/'CURRENT DECOMPILATION.txt').write_text(note)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+note)
    p=ROOT/'START HERE.txt';s=p.read_text();a=s.index('LATEST GAME RESULT\n');b=s.index('LOCAL INFERENCE RESULT\n',a);p.write_text(s[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+s[b:])
    save(ROOT/'verification/scene-display-list-review.json',dict(recorded_at=now,directory=str(audit)))
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(dict(components=123,displayCPU_cases=1025,reachable_instructions=252,host_guards=17,live_cases=16,display_calls=1008,live_source_instructions=live_covered,audit=str(audit))))
if __name__=='__main__':main()
