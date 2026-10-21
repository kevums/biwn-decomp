"""Publish accepted scene-caller integration without implying geometry recovery."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    source = ROOT/'projects/black-ice-white-noise/restoration'
    validation = read(session/'boot-slice-validation.json')
    cpu = read(ROOT/'verification/biwn-scene-draw-cpu-checks.json')
    linked = read(ROOT/'verification/biwn-disc-world-scene-draw-checks.json')
    assert cpu['CPU_cases'] == 1024 and cpu['source_instruction_coverage'] == [102,102] and cpu['host_guards'] == 17
    assert linked['cases'] == 16 and linked['task_handoffs'] == 6144 and linked['actual_C_sprite_decodes'] == 160
    assert linked['scene_draw_body_call_counts'] == {'0x17e0e':1008,'0xe03a':1008,'0x17f14':1008}
    assert linked['render_scene_overlay_script_call_counts'] == {'0x181f8':1008,'0xe0a6':1008,'0xe0f2':0,'0xe148':0,'0xe19e':0,'0xe202':0,'0x170a0':1008,'0x185b2':1008}
    for key, value in validation['disc_world_actor_pipeline'].items(): linked.setdefault(key, value)
    rows = read(Path(linked['directory'])/'fixtures.json')
    assert all(row['final_queue_count']==0 and all('CPU' in h for h in row['rebuilt']['handoffs']) for row in rows)
    linked.update(full_scene_draw_executed=False, overlay_executed=False, full_game_viewport_proved=False)
    previews=[]
    for i,row in enumerate(rows):
        folder=Path(linked['sprite_preview_directory'])/f'case-{i:02d}'
        meta=read(folder/'sprite.json')
        assert hashlib.sha256((folder/'sprite.raw16be').read_bytes()).hexdigest()==meta['raw_sha256']
        assert [c['output'] for c in row['rebuilt']['render_queue_calls'] if 'output' in c][-1]==meta
        previews.append(dict(case=i,png=str(folder/'sprite.png'),png_sha256=hashlib.sha256((folder/'sprite.png').read_bytes()).hexdigest(),raw=str(folder/'sprite.raw16be'),**meta))
    linked['decoded_sprite_previews']=previews
    save(ROOT/'verification/biwn-disc-world-scene-draw-checks.json',linked)
    save(Path(linked['directory'])/'report.json',linked)
    for proof in [cpu,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass'
        snap=folder/'publication-snapshot';snap.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_scene_draw_cpu.py','check_biwn_scene_draw_cpu.py','check_biwn_render_queue_cpu.py','check_biwn_disc_scene_actors.py','check_biwn_disc_world_yields.py']]
        for name,expected in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
        for p in files:shutil.copy2(p,snap/p.name)
        save(snap/'manifest.json',dict(recorded_at=now,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
    validation.update(scene_draw_full_CPU=cpu,disc_world_actor_pipeline=linked,disc_world_scene_draw_pipeline=linked,latest_aggregate_update=now)
    assert validation['portable_C_component_count']==112
    save(session/'boot-slice-validation.json',validation)
    generated=read(session/'scene-draw-fullCPU-generation.json');generated.update(status='accepted_standalone_fullCPU_and_live_disc_scene_caller',whole_game_complete=False,evidence=['verification/biwn-scene-draw-cpu-checks.json','verification/biwn-disc-world-scene-draw-checks.json']);save(session/'scene-draw-fullCPU-generation.json',generated)
    scope=('The live renderer now executes the actual17E0E scene caller, E03A framebuffer clear with pinned emulated-blitter rasterization, and17F14 triple-buffer rotation, each1008calls. FullCPU scene proof passes1024cases/all102instructions/17guards with nativeCPU and independent Unicorn. The16disc-scene cases retain720worldupdates/2048actoriterations/6144fullCPUhandoffs/1008queueconsumers/160C sprite decodes and32preserved-disc payloads/3080416bytes. Final queues empty;6contexts runnable/15blocked. Eight lower rendering helpers are configured scripts:181F8overlay,E0A6,E0F2,E148,E19E,E202,170A0geometry and185B2display-list. Four are reached1008times each:181F8,E0A6,170A0,185B2. The other four are unreached. Thus actual scene caller/clear/rotation does not prove complete geometry, viewport or scanout. Three configured world scripts remain unreached. BIOS/completion adapters, phased startup, supplied clock/button/inventory inputs and synchronous GPU completion remain. Resource synchronization is verified separately in two clients, unexercised in this21-context game scene. Audio/uninterruptedboot/remainingtasks/scenes/fullgame/physicalhardware are unfinished. Game not playable. Aggregate112 unchanged.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json')
    examples.update(checked_world_actor_scope=scope,checked_render_queue_answer='17E0E is no longer a stub: actual scene caller, E03A clear and17F14rotation each ran1008times. Eight lower rendering scripts configured/four reached:181F8,E0A6,170A0,185B2 each1008;E0F2,E148,E19E,E202 unreached. Live queue160decodes retained. Complete geometry/viewport/scanout/audio/game remain unfinished.',checked_dispatcher_answer='Actual world/input/equipment/loading/render queue and scene caller run together with272equipment/32loader suspensions/6144fullCPUhandoffs. Main-scene synchronization unexercised; lowergeometry/display-list/overlay bodies and fullgame unfinished.',checked_resource_answer='Actual resource/cache/heap/loader/CD wrappers load32preserved-disc payloads/3080416bytes in the newest live scene-caller proof. Separate two-client readiness is verified. BIOS/completion adapters, main-scene synchronization and remaining rendering/fullgame remain incomplete.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    checkpoint=dict(recorded_at=now,status='code_passed_local_native_scope_review_pending',published_components=112,new_components=0,CPU_cases=1024,source_instruction_coverage=[102,102],host_guards=17,
                    disc_cases=16,world_updates=720,actor_iterations=2048,task_handoffs=6144,full_handoff_CPU_states_compared=True,live_C_sprite_decodes=160,
                    scene_draw_body_call_counts=linked['scene_draw_body_call_counts'],configured_render_scripts=linked['render_scene_overlay_script_targets'],reached_render_script_call_counts=linked['render_scene_overlay_script_call_counts'],
                    full_scene_geometry_executed=False,full_viewport_proved=False,full_goal_status='active incomplete',native_current_checkpoint_response_verified=False,
                    next_work='Reconstruct reached E0A6,170A0geometry,185B2display-list and181F8overlay bodies/dependencies with full CPU/native-device checks. Link game resource waits; continue remaining tasks/scenes/audio/uninterrupted boot/fullgame. Keep easy native Chat and advertising workflow tests current.',
                    evidence=['verification/biwn-scene-draw-cpu-checks.json','verification/biwn-disc-world-scene-draw-checks.json'])
    save(ROOT/'verification/scene-draw-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(scene_draw_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:1024sceneCPU cases and16live scene-caller cases passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: fullCPU scene caller/clear/rotation linked into live disc-scene renderer; full geometry and game incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(path,value)
    note='SCENE CALLER / CLEAR / ROTATION — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored fixed C and integration. OriginalCPU/GPU and independent standalone Unicorn validate scoped effects. No local-model-authored code, subagents, new training or weight/default promotion. Eight lower helper scripts declared with actual counts. No full viewport/game claim. One Python preflight Device.write signature error fixed before comparison; no C behavior repair.\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(note)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with (ROOT/name).open('a') as f:f.write('\n'+note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:
        subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(checkpoint))

if __name__=='__main__':main()
