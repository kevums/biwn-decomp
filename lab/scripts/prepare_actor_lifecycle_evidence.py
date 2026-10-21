"""Publish actual TRAP2/removal/reuse without promoting the full game."""
import collections
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    names = ['biwn-task-removal-checks.json', 'biwn-actor-lifecycle-runtime-checks.json',
             'biwn-scheduler-checks.json', 'biwn-actor-full-movement-runtime-checks.json']
    proofs = {n: read(ROOT / 'verification' / n) for n in names}
    removal, lifecycle, scheduler, actor = proofs.values()
    assert removal['native_CPU_cases'] == 1024 and removal['CPU_instruction_coverage'] == [29,29]
    assert lifecycle['cases'] == 256 and lifecycle['task_handoffs'] == 3840 and lifecycle['reused_idle_body_executions'] == 256
    assert scheduler['native_CPU_cases'] == 512 and actor['cases'] == 128
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for proof in proofs.values():
        assert read(Path(proof['directory']) / 'status.json')['status'] == 'terminal_pass'
        for name, digest in proof['source_sha256'].items():
            assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
        snapshot = Path(proof['directory']) / 'harness-snapshot'
        snapshot.mkdir(exist_ok=True)
        scripts = ['check_biwn_task_removal.py', 'check_biwn_actor_lifecycle_runtime.py', 'check_biwn_actor_full_movement_runtime.py',
                   'check_biwn_scheduler.py', 'check_biwn_actor_task.py', 'check_biwn_actor_navigation.py', 'check_biwn_rng_cpu.py',
                   'check_biwn_actor_movement_collision.py', 'check_biwn_actor_movement_gpu.py', 'check_biwn_movement_submit_cpu.py',
                   'check_biwn_actor_collision.py', 'check_biwn_geometry_cpu.py', 'check_biwn_geometry.py',
                   'check_biwn_actor_direction.py', 'check_biwn_actor_movement.py', 'check_biwn_world_movement_pipeline.py',
                   'check_biwn_inventory_frame.py', 'check_biwn_render_display_runtime.py', 'check_biwn_transition_cleanup.py']
        files = [ROOT / 'scripts' / n for n in scripts] + [source / n for n in proof['source_sha256']]
        for path in files:
            shutil.copy2(path, snapshot / path.name)
        save(snapshot / 'manifest.json', {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    # The shared scheduler changed, so refresh derived metadata after its
    # regular actor regression. This does not copy stale source hashes.
    rows = read(Path(actor['directory']) / 'fixtures.json')
    counts = dict(collections.Counter(hex(e['target']) for r in rows for e in r['rebuilt']['navigation_returns']))
    assert sum(counts.values()) == 2671 and counts['0x13c9a'] == 1024
    moved = sum(any([p['X'],p['Y'],p['Z']] != [r['rebuilt']['movements'][0]['X'],r['rebuilt']['movements'][0]['Y'],r['rebuilt']['movements'][0]['Z']] for p in r['rebuilt']['movements'][1:]) for r in rows)
    assert moved == 101
    actor.update(helper_return_CPU_comparisons=counts, helper_return_CPU_comparisons_total=2671,
                 navigation_helper_return_comparisons_total=1289, indexed_RNG_return_CPU_comparisons=358,
                 movement_return_CPU_comparisons=1024, position_change_cases_observed=101,
                 original_GPU_submit_entries=sum(r['original']['steps'].count(0xe220) for r in rows))
    actor['limits'][-1] = 'This regular-path regression does not execute removal. Current removal/reuse is checked in the separate256-case actor lifecycle proof; original21-context startup/world/render/assets and full game/hardware remain unfinished.'
    save(ROOT / 'verification/biwn-actor-full-movement-runtime-checks.json', actor)
    save(Path(actor['directory']) / 'report.json', actor)
    startup = read(ROOT / 'verification/biwn-render-actors-runtime-checks.json')
    contexts = read(Path(startup['directory']) / 'fixtures.json')[0]['startup_contexts']
    implemented = {0x17c40, 0x1a544, 0xf360, 0xf880, 0xf4d8}
    unique = {r['entry'] for r in contexts}
    covered = [r for r in contexts if r['entry'] in implemented]
    assert len(contexts) == 21 and len(unique) == 20 and len(covered) == 6
    coverage = {'captured_contexts': 21, 'captured_distinct_entries': 20,
                'implemented_distinct_entry_bodies': 5, 'contexts_with_implemented_entry': 6,
                'unimplemented_distinct_entries': 15, 'contexts_with_unimplemented_entry': 15,
                'implemented_entries': [hex(a) for a in sorted(implemented)],
                'scope': 'Across separate proofs. Two captured actor contexts share F4D8. This is not six bodies executing in startup: startup still executes three bodies and blocks18contexts.'}
    scope = ('106 checked components:104 CPU and two GPU. New entries are removal handler DEB6, TRAP2 DF7A and the previously pending F4D8 actor caller; shared scheduler/geometry/math are not recounted. '
             'Removal passes1,024 original-CPU cases, all29 reached handler/shared-tail instructions and23host guards. Existing512scheduler and128regular-actor comparisons pass after refactoring. '
             'The separate256-case actor lifecycle proof has128cold exits and128exits aftereightiterations:1,024actor iterations,256actual removals,256context reuses and3,840real handoffs, including execution/yield of256reused idle bodies. '
             'AllCPU/SR/USP/SSP andcomplete2MBRAM/privateframes match; noactorhelper scripts. Removal does not save the dead task state or return toF57C; actualDE5C reinitializes and reuses itscontext. '
             'Synthetic geometry, seededclock/contexts, synchronousGPU completion, external killwords andhost-stagedcreation calls are explicit fixtures. The reused entry isidleF360, notanactorrespawnfactory. '
             'Across separate proofs,five distinct captured taskentrybodies areimplemented,coveringsixof21contexts becauseF4D8appears twice;15distinctentries/15contextsremain unimplemented. '
             'Actors remain blocked in the separate21-contextstartup. Fullstartup/world/render/assets, remainingtasks, real loading switches,3Ddrawing/scanout/mainloop/scenes/audio/game/hardware remainunfinished. Counts are notcompletion percentages.')
    examples = {'checked_lifecycle_scope': scope, 'task_entry_coverage': coverage,
                'checked_removal_answer': 'Yes, actual TRAP2 removal and freed-context reuse now execute in a separate256-case lifecycle test. DEB6 pushes the dead context onto C0924, unlinks its next/prev links, discards its six-byte exception frame and schedules another task without saving the dead task SP/PC/SR. F57C is not reached after TRAP2. DE5C then reuses the context for idleF360; that body executes a real yield. This is not actor respawn or full startup/game completion.',
                'checked_remaining_answer': 'The full game remains unfinished. The separate21-context startup still blocks actors; synthetic geometry/synchronousGPU/host kill-and-creation stimuli, startup/world/render/asset integration, remaining task entries, loading switches,3Ddrawing/scanout/mainloop/scenes/audio/hardware remain.'}
    save(ROOT / 'verification/actor-lifecycle-checked-examples.json', examples)
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    backup = ROOT / 'verification/actor-lifecycle-backup' / Path(lifecycle['directory']).name
    backup.mkdir(parents=True)
    for name in ['chat_tools.py', 'scripts/summarize_biwn_checks.py', 'config.json', 'corpus/game/project-intake.json', 'presets/Game Assistant.system.txt', 'presets/Game Assistant.preset.json', 'CURRENT DECOMPILATION.txt', 'START HERE.txt']:
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    validation = read(session / 'boot-slice-validation.json')
    assert validation['portable_C_component_count'] == 103
    save(backup / 'boot-slice-validation.json', validation)
    validation.update(portable_C_component_count=106, processor_component_counts={'CPU':104,'GPU':2},
                      task_removal_reconstruction=removal, actor_lifecycle_runtime=lifecycle,
                      scheduler_reconstruction=scheduler, actor_full_movement_runtime=actor,
                      task_entry_coverage=coverage, latest_aggregate_update=now,
                      component_count_scope='Three new entries:DEB6removalhandler,DF7ATRAP2wrapper,F4D8actorcaller. Previously counted scheduler/geometry/math reused. Selected proofs, not full-game completion.')
    save(session / 'boot-slice-validation.json', validation)
    for proof, lib, dest in [(removal,'libtask-removal.dylib','libbiwn-task-removal.dylib'),(lifecycle,'libactor-lifecycle.dylib','libbiwn-actor-lifecycle.dylib')]:
        shutil.copy2(Path(proof['directory']) / lib, ROOT / 'tools' / dest)
    path = ROOT / 'scripts/summarize_biwn_checks.py'
    text = path.read_text()
    needle = "    save(folder / 'emulator-runtime/summary.json', runtime)"
    block = """    lifecycle_path=root/'verification/biwn-actor-lifecycle-runtime-checks.json'
    if lifecycle_path.exists():
        lifecycle=json.loads(lifecycle_path.read_text());removal_path=root/'verification/biwn-task-removal-checks.json';removal=json.loads(removal_path.read_text())
        if lifecycle['cases']!=256 or lifecycle['task_handoffs']!=3840 or removal['native_CPU_cases']!=1024:
            raise ValueError('Actor lifecycle/removal proof incomplete')
        runtime['CPU_task_removal_reconstruction']={**removal,'report':str(removal_path)}
        runtime['actor_lifecycle_runtime']={**lifecycle,'report':str(lifecycle_path)}
        runtime['actor_lifecycle_checked_examples']=json.loads((root/'verification/actor-lifecycle-checked-examples.json').read_text())
"""
    assert 'actor_lifecycle_runtime' not in text
    path.write_text(text.replace(needle, block + needle))
    path = ROOT / 'chat_tools.py'
    text = path.read_text().replace("'task_creation', 'render_startup'", "'task_creation', 'task_removal', 'render_startup'").replace("'task_creation','render_startup'", "'task_creation','task_removal','render_startup'")
    # Tool descriptions must not freeze historical progress as current truth.
    a = text.index('    """Get checked Black Ice White Noise evidence.')
    b = text.index('    folder = session()', a)
    old_description = text[a:b]
    new_description = old_description.replace('two scripted collision helpers and unlinked actor-task scope', 'current collision/geometry/task linkage')
    new_description = new_description.replace('Use actor_task for the F4D8 caller: 512 boundary cases plus a separate 128-case actor/two-idle integration with 3072 real scheduler handoffs.', 'Use actor_task or task_removal for current F4D8 lifecycle, TRAP2/DEB6 unlink/free, context reuse, checked task counts and remaining startup/game scope.')
    new_description = new_description.replace('only movement remains scripted. Actor bodies are still blocked in the 21-context startup; removal remains pending.', 'use current returned lifecycle evidence to distinguish separate actor execution from blocked actors in21-context startup.')
    text = text[:a] + new_description + text[b:]
    marker = '    def latest_pipeline(compact,observed):'
    helper = """    def latest_actor_lifecycle(compact,observed):
        if not isinstance(observed,dict) or 'actor_lifecycle_runtime' not in observed:return compact
        proof=observed['actor_lifecycle_runtime'];examples=observed['actor_lifecycle_checked_examples']
        compact['current_actor_lifecycle']={k:proof[k]for k in ['report','cases','cold_exit_cases','exit_after_eight_iterations_cases','actor_iterations','task_handoffs','actor_removals','context_reuses','fresh_reused_context_selections','reused_idle_body_executions','scripted_actor_helpers','removal_TRAP2_executed','removed_state_not_saved','allCPU_SR_USP_SSP_complete2MBRAM_privateframes_compared','synthetic_scene_geometry','synchronous_GPU_completion','startup21context_fixture_linked','creation_call_fixture','matched','limits']}
        compact.update(examples)
        compact['current_vs_historical']='Current_actor_lifecycle and checked_lifecycle_scope supersede older pending-removal labels. Historical regular/boundary/startup reports retain their exact old scope; startup actors remain blocked.'
        if 'checked_current_summary' in compact:compact['checked_current_summary']=examples['checked_lifecycle_scope']
        if 'checked_actor_task_scope' in compact:compact['checked_actor_task_scope']=examples['checked_lifecycle_scope']
        if 'render_task_startup_progress' in compact:
            compact['render_task_startup_progress'].update(implemented_captured_task_callers_total=6,other_captured_task_callers_unported=15,task_entry_coverage=examples['task_entry_coverage'])
        return compact
"""
    assert marker in text
    text = text.replace(marker, helper + marker)
    text = text.replace("        return compact\n    if topic == 'actor_collision':", "        return latest_actor_lifecycle(compact,observed)\n    if topic == 'actor_collision':", 1)
    marker = "    if topic == 'actor_collision':"
    block = """    if topic in ['task_removal','actor_task'] and 'actor_lifecycle_runtime' in common.get('emulator_runtime',{}):
        observed=common['emulator_runtime']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        removal=observed['CPU_task_removal_reconstruction']
        compact['CPU_task_removal']={k:removal[k]for k in ['report','native_CPU_cases','handler_cases','TRAP2_cases','CPU_instruction_coverage','new_removal_entry_instructions','new_removal_entry_bytes','host_guards','task_context_range','removed_contexts_not_resumed','removed_state_not_saved','matched','limits']}
        compact['actor_caller_boundary_coverage']={k:observed['CPU_actor_task_boundary_reconstruction'][k]for k in ['report','CPU_cases','reachable_instruction_coverage','host_guard_checks']}
        compact['startup_scope']='Separate21-context startup still blocks18contexts including actors and executes only render/twoidle bodies. Current isolated actor lifecycle does not change that startup result.'
        return record('project_evidence',{'topic':topic},latest_actor_lifecycle(compact,observed))
"""
    text = text.replace(marker, block + marker, 1)
    text = text.replace("return record('project_evidence',{'topic':topic},compact)", "return record('project_evidence',{'topic':topic},latest_actor_lifecycle(compact,common.get('emulator_runtime',{})))")
    text = text.replace("return record('project_evidence',{'topic':topic},current)", "return record('project_evidence',{'topic':topic},latest_actor_lifecycle(current,observed))")
    text = text.replace("f\"{progress['implemented_captured_task_callers_total']} unique captured task callers out of21 are implemented; {progress['other_captured_task_callers_unported']} callers remain unported. \"", "f\"{progress['implemented_captured_task_callers_total']} of21capturedcontexts have implemented entrybodies across separate proofs; {progress['other_captured_task_callers_unported']} contexts have unimplemented entrybodies. \"")
    text = text.replace('Removal/TRAP2 remains pending; this does not run actors in the 21-context startup.', 'See current_actor_lifecycle for newer removal/reuse; this does not run actors in the21-contextstartup.')
    text = text.replace('Removal and21-context startup linkage remain pending.', 'Newer removal/reuse is in current_actor_lifecycle;21-contextstartup linkage remains pending.')
    path.write_text(text)
    for name in ['actor-collision-checked-examples.json','actor-movement-checked-examples.json','actor-navigation-checked-examples.json']:
        path = ROOT / 'verification' / name
        value = read(path)
        for key in ['checked_collision_scope','checked_movement_scope','checked_navigation_scope']:
            if key in value:value[key] = scope
        if 'checked_actor_runtime_answer' in value:value['checked_actor_runtime_answer'] = examples['checked_removal_answer']
        if 'checked_pending_answer' in value:value['checked_pending_answer'] = examples['checked_remaining_answer']
        save(path, value)
    path = ROOT / 'presets/Game Assistant.system.txt'
    text = path.read_text().replace('- actor_task:', '- task_removal: actualTRAP2/DEB6 removal, dead-task state, context reuse and current lifecycle/startup limits.\n- actor_task:', 1)
    path.write_text(text)
    path = ROOT / 'presets/Game Assistant.preset.json'
    preset = read(path)
    for field in preset['operation']['fields']:
        if field['key'] == 'llm.prediction.systemPrompt':field['value'] = text.strip()
    save(path, preset)
    for name in ['config.json','corpus/game/project-intake.json'] + ['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path = ROOT / name
        value = read(path)
        value.update(actor_lifecycle_progress=scope,actor_lifecycle_evidence=['verification/'+n for n in names],task_entry_coverage=coverage)
        if name == 'config.json':value['chat_frontend']['game']['status'] = scope
        if name == 'corpus/game/project-intake.json':value['latest_checked_status'] = scope
        if name == 'verification/current-runtime-state.json':value['decomp_progress'] = scope
        if name == 'verification/setup-status.json':value['game_work'] = scope
        if name == 'verification/requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:item['state'] = scope
        save(path, value)
    (ROOT / 'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\nConnect the actor bodies with original startup/world/render scene assets, remaining task bodies and actual loading switches. Full goal active and incomplete.\n')
    path = ROOT / 'START HERE.txt'
    text = path.read_text();a = text.index('LATEST GAME RESULT\n');b = text.index('LOCAL INFERENCE RESULT\n', a)
    path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:
        subprocess.run([str(ROOT / '.venv/bin/python'), str(ROOT / 'scripts' / name)], check=True)
    print(json.dumps({'components':106,'lifecycle_cases':256,'handoffs':3840,'task_entry_coverage':coverage}))

if __name__ == '__main__':
    main()
