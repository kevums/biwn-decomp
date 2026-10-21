"""Deliver actual retained camera/animation/GPU integration; preserve open gates."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    ap=V/'native-input-real-animation-caller-v4-current.json'
    cp=V/'native-input-real-camera-caller-v3-current.json'
    animation,camera=read(ap),read(cp)
    assert animation['completed']==318 and animation['inherited_passing_cases']==312 and animation['new_paired_trials']==6
    assert animation['actual_input_animation_CPU_calls']==6 and animation['actual_animation_CPU_calls']==324 and animation['actual_animation_queue_CPU_calls']==312
    assert animation['admitted_native_cases']==106 and animation['original_fallback_cases']==212
    assert animation['native_max_caller_stack']==432 and animation['raw_volatile_differing_cases']==8
    assert camera['completed']==78 and camera['actual_camera_CPU_calls']==78 and camera['actual_animation_CPU_calls']==78
    assert camera['actual_animation_queue_CPU_calls']==72 and camera['original_GPUExec1_calls']==40758
    assert camera['admitted_native_cases']==26 and camera['original_fallback_cases']==52 and camera['raw_volatile_differing_cases']==0
    assert camera['actual_GPU_arithmetic_executed'] and camera['original_GPU_execution_both_lanes']
    for receipt in [animation,camera]:
        for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    raw=read(Path(animation['directory'])/'raw-volatile-differences.json')
    assert Counter(i for row in raw for i in row['registers'])=={1:8}
    assert all((row['original'][1]&65535)==(row['candidate'][1]&65535)for row in raw)
    reviewer=[]
    for version in [1,2]:
        path=V/f'local-input-helpers-reviewer-v{version}-current.json';receipt=read(path)
        assert receipt['new_predictions']==1
        for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
        decision=read(V/f'local-input-helpers-reviewer-v{version}-reviewed.json')
        assert not decision['default_promoted']
        reviewer.append(dict(version=version,seconds=receipt['seconds'],words=receipt['words'],
            transcript=str(Path(receipt['directory'])/'prompts-and-responses.txt'),
            provided_snapshot_accepted=False,decision=decision['status']))
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp)
    for path,digest in wrapper['dependencies_sha256'].items():assert sha(path)==digest,path
    packet=read(wrapper['packet']);previous=packet['current_native_input_prototype_progress']
    assert previous['module_bytes']==10580 and previous['profile']=='native-191f4-input-admission-prototype-v4'
    assert packet['current_input_admission_progress']['raw_D1_upper_differences']==837
    assert not packet['pending_native_candidate']['default_promoted']
    out=V/'input-real-helpers-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-packet.json',packet)
    report=ROOT/'reports/BIWN Guarded Input Real Animation Camera and GPU Tests.txt'
    report.write_text(
        'BIWN — guarded input with real retained animation/camera helpers\n\n'
        'New diagnostic integration connects original animation/camera and original GPU movement code to the unchanged10580byte guarded input prototype. The binary has not changed;the copied SDK10580byte build proof is inherited,not replayed. These are retained original helper bodies in an emulator,not newly recovered functions or a source-only GPU build. No game image or installed preview changed.\n\n'
        'ACTUAL ANIMATION / QUEUE\n'
        '318paired full-caller fixtures pass:312base layout cases across13input states,plus6equipment add/remove comparisons. The supplement reuses the312passing cases and executes only6new pairs. The initial three cases had been reexecuted for a new explicit D1lowword check/raw capture after a logging failure,not for receipt creation. Candidate-side routes:106native input calls/212original fallbacks;no skips.324actual originalEB04animation calls and312nestedEAC4queue calls execute. Six animation calls occur inside the input equipment routine,two of them through the compiled native physical-call bridge. YieldDF60remains a scripted RTS in this particular fixture. Earlier realTRAP/RTEevidence is separate.\n\n'
        'PublicRAM,ordered CPU accesses,helper arguments/inputD0seeds,finalSRandcallee-save match. Eightcases retain upperD1differences;thelowword agrees. This is a different controlled layout set from the earlier6945cases/837upperD1differences.8versus837is not an improvement measurement. Synthetic finite animation records and explicit counters/timesteps are declared inputs;the caller input gate is opened to ensure helper coverage. This is not a live input replay or a test that normalizes poses/timers to match a game image.\n\n'
        'Maximum full-caller stack now432bytes in the equipment/animation cases,versus120original fallback bytes. The prior392real-yield measurement has a different scope and does not bound this new connected path. These bounded stacks respect the task fence. The guard entry reserve512remains provisional for full real resource/helper nesting and arbitraryIRQ.\n\n'
        'ACTUAL CAMERA / MATH / ORIGINAL GPU\n'
        '78new paired full-caller fixtures across13input states pass:26nativeinput/52originalfallback. Both sides execute originalF0FAcamera,nested originalmultiply/division/direction,originalEB04/EAC4,and originalGPU4320movement under synchronous device completion. Candidate side:78camera/78animation/72queuecalls;40758GPUExec1callbackinvocations,not40758submissions. Original GPU instructions are retained on both sides;there is no claim that the rebuilt side replaces them with new source here.\n\n'
        'Whole publicRAM,ordered CPU bus accesses,helper arguments,finalSRand all finalregisters match in this bounded set. Zero raw finalcontext differences here do not waive the broader837differences. Maximum stack352native/122originalfallback in this path set;it is not the new global432maximum. GPU writes are propagated to the CPU memory mapping at the actual synchronous submission. Final CPU-cache-versus-deviceRAM checks pass without result-region masking. Changed GPU memory blocks are recorded. The 68000 comparison runs in Unicorn;the GPU is the pinned emulator. Earlier standalone fullCPU camera/animation proofs are existing separate evidence,not rerun. Arbitrary scheduling/interrupts and physicalconsole remain unproven.\n\n'
        'RETAINED DIAGNOSTIC FAILURES\n'
        'Animation v1passed3cases then hit a receipt-path variable-shadowing bug. v2rejected its own false prefix-reuse assumption before any new trial. v3fixed logging and added the lowword gate;v4added only the equipment supplement. Camera v1caught incoherent cached GPU result memory;v2implemented synchronous coherence but misclassified a legitimate original direction-helper division as an input escape. v3includes that nested math context and passes78cases. All failures/scripts remain saved;no game source was changed to force these diagnostics to pass.\n\n'
        'LOCAL MODEL WORK / WHO DID WHAT\n'
        'Coordinator authored these integrations and checks. The prior local Coder120byte admission predicate remains unedited inside the unchanged prototype. Two real local Reviewer responses ran through LMStudioSSE using the owned copied27B6bit model under the shared lease. First15.88seconds/213words:factual supplied-snapshot review passed,but the160wordlimit failed. One explicit correction produced5.05seconds/'+str(reviewer[1]['words'])+'words,but one paragraph instead of three and imprecise measured432-versus-provisional512stack wording left it unapproved. Both raw replies/prompts are preserved;neither replaces the default Reader. Role labels are sequential uses of one model,not independent reviewers. No optimizer updates or new weights;no useful untouched-task training gain claimed. Native Chat visibility remains unverified;headless work is authorized.\n\n'
        'REMAINING WORK\n'
        'Execute and qualify real resource/collision/targeting helpers and their register/stack contracts,cover actualcooperative/IRQreentry and logical error handling,then allocated image placement/startupcopy/heap/alias/observer and fresh gameplay. Prototype1C0000is a fixture address. The original191F4globalentry stays intact. v34remains reviewed baseline;v37remains unpromoted after its freshmatrix finalvideoFAIL22858pixels and fractionalpose differences. Desktop preview remains the earlier six-caller outdoor checkpoint. Fullsource-onlysame-console game,CPU/GPU/DSP/audiovisualfidelity,usefultraininggain,nativeChat ease and future256GBcapacity remain incomplete.\n\n'
        'Animation proof:'+str(ap)+'\nCamera/GPUproof:'+str(cp)+'\n'
        'First Reviewer exact prompt/response:'+reviewer[0]['transcript']+'\nCorrection exact prompt/response:'+reviewer[1]['transcript']+'\n')
    progress=dict(status='terminal_real_animation_camera_original_GPU_connected_remaining_helpers_open',report=str(report),directory=str(out),
        module_bytes=10580,component_bytes_changed=False,new_original_functions_recovered=0,
        animation_fixture_cases=318,animation_base_cases=312,new_equipment_paired_cases=6,
        animation_native_calls=106,animation_original_fallbacks=212,animation_CPU_calls=324,queue_CPU_calls=312,
        input_animation_calls=6,input_native_bridge_animation_calls=2,animation_upper_D1_differences=8,
        camera_fixture_cases=78,camera_native_calls=26,camera_original_fallbacks=52,camera_CPU_calls=78,
        camera_animation_CPU_calls=78,camera_queue_CPU_calls=72,camera_raw_final_context_differences=0,
        original_GPU_both_lanes=True,original_GPUExec1_callback_invocations_candidate=40758,
        synchronous_GPU_completion=True,CPU_GPU_RAM_coherence_checked=True,GPU_result_masking=False,
        maximum_connected_caller_stack=432,animation_fallback_caller_stack=120,camera_native_stack=352,camera_fallback_stack=122,
        admission_reserve_bytes=512,full_real_helper_or_IRQ_bound_proven=False,
        broader_scripted_837_D1_differences_waived=False,actual_animation_queue_CPU_connected=True,
        actual_camera_math_CPU_connected=True,resource_collision_targeting_bodies_still_open=True,
        real_helper_yield_IRQ_qualified=False,new_disc_built=False,installed_preview_changed=False,
        new_local_predictions=2,optimizer_updates=0,local_Reviewer=reviewer[-1],local_Reviewer_trials=reviewer,
        native_Chat_verified=False,default_Reader_changed=False,animation_review=str(ap),camera_review=str(cp))
    component=dict(previous)
    component.update(status=progress['status'],report=str(report),directory=str(out),
        connected_original_animation_queue_verified=True,connected_original_camera_math_GPU_verified=True,
        connected_animation_cases=318,connected_camera_GPU_cases=78,connected_equipment_animation_stack=432,
        real_retained_helper_bodies_qualified=False,private_task_stack_admission_qualified=False,
        arbitrary_IRQ_qualified=False,full_real_helper_bound_proven=False,
        real_helpers_progress=progress,scope='Unchanged10580byteguardedinput. New318animation/equipmentfixturesand78camera/animation/originalGPUfixturespass. Realresources/collision/targeting,broader837rawD1contexts,fullstack/IRQ/error/image/freshgatesremainopen.')
    packet['previous_native_input_component_before_real_helpers']=previous
    packet['current_native_input_prototype_progress']=component;packet['latest_source_development']=component
    packet['current_input_real_helpers_progress']=progress
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v29.py')
    packet['checked_current_summary']+=' Newrealanimation/queue318fixturesincluding6equipmentsupplementand78camera/math/originalGPUfixturespass.432fullcallerstackobserved;512reserveprovisional. Broader837D1differencesremain. TwoReviewerresponses15.88/5.05secondsunapproved;no weights/disc/previewchange.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    save(out/'current-status-packet.json',packet);save(out/'facts.json',progress)
    deps={str(Path(__file__)):sha(__file__),str(report):sha(report)}
    for path,receipt in [(ap,animation),(cp,camera)]:deps[str(path)]=sha(path);deps.update(receipt['source_sha256'])
    for name in ['native-input-real-animation-caller-v1','native-input-real-animation-caller-v2','native-input-real-camera-caller-v1','native-input-real-camera-caller-v2']:
        path=V/(name+'-current.json');assert read(path)['status'].startswith('terminal_');deps[str(path)]=sha(path)
    for version in [1,2]:
        path=V/f'local-input-helpers-reviewer-v{version}-current.json';receipt=read(path);deps[str(path)]=sha(path);deps.update(receipt['source_sha256'])
        review_path=V/f'local-input-helpers-reviewer-v{version}-reviewed.json';deps[str(review_path)]=sha(review_path)
    for name in ['show_native_status_v16.py','portable_biwn_entry_v29.py','check_native_input_real_animation_caller_v1.py',
        'check_native_input_real_animation_caller_v2.py','check_native_input_real_camera_caller_v1.py','check_native_input_real_camera_caller_v2.py']:
        path=ROOT/'scripts'/name;deps[str(path)]=sha(path)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py')
    clone(ROOT/'scripts/portable_biwn_entry_v29.py',P/'workbench/portable_biwn.py')
    deps.update({str(path):sha(path)for path in out.iterdir()if path.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps})
    atomic(wp,wrapper);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V/'input-real-helpers-delivered-v1-current.json',dict(status=progress['status'],directory=str(out),report=str(report),new_predictions=2,new_training=False,new_disc_built=False,dependencies_sha256=deps))
    print(progress['status'],flush=True)


if __name__=='__main__':main()
