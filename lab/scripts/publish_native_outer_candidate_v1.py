"""Publish qualified candidate gates without promoting a disc or preview."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    final_path=V/'native-Deck-six-final-v1-current.json';final=read(final_path)
    assert final['status']=='terminal_six_caller_final_addresses_startup_and_heap_gates_pass'
    bp=V/'native-Deck-six-disc-build-v1-current.json';b=read(bp)
    assert sha(bp)==final['build_sha256'] and sha(b['derived_disc'])==b['derived_disc_sha256']
    checked={}
    def verify(proof):
        for p,h in proof['source_sha256'].items():assert sha(p)==h,p;checked[p]=h
    verify(final);verify(b)
    names=['native-Deck-outer-v1-current.json','native-Deck-outer-connected-v1-current.json','native-Deck-outer-fallback-v1-current.json','native-Deck-outer-waits-v1-current.json',
           'native-Deck-outer-final-v1-current.json','native-deck-shared-six-final-v1-current.json','native-Deck-outer-fallback-final-v1-current.json','native-Deck-outer-waits-final-v1-current.json',
           'native-Deck-outer-connected-final-v1-current.json','native-Deck-six-startup-heap-v1-current.json','native-Deck-six-capacity-v1-current.json']
    proofs={name:read(V/name)for name in names}
    for p in proofs.values():verify(p)
    component=proofs['native-Deck-outer-final-v1-current.json'];connected=proofs['native-Deck-outer-connected-final-v1-current.json'];startup=proofs['native-Deck-six-startup-heap-v1-current.json']
    assert component['completed']==1280 and component['maximum_C_stack_bytes']==356
    assert proofs['native-deck-shared-six-final-v1-current.json']['completed']==5248
    assert connected['completed']==128 and connected['task_slots']==101 and connected['protected_suspended_frame_checks']==2245
    assert startup['startup_cases']==6 and startup['heap_initialize_cases']==192 and startup['initial_heap_bytes']==137728
    assert proofs['native-Deck-six-capacity-v1-current.json']['cases']==36
    previous=read(V/'native-Deck-shared-reviewed-v4-current.json');assert sha(previous['disc'])==previous['disc_sha256']
    out=V/'native-Deck-outer-candidate-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for name in [*names,'native-Deck-six-final-v1-current.json','native-Deck-six-disc-build-v1-current.json']:
        shutil.copyfile(V/name,out/name)
    save(out/'all-verified-dependencies.json',checked)
    facts=dict(status='terminal_six_caller_candidate_final_gates_reviewed_fresh_gameplay_pending',
               candidate_native_Deck_callers=6,latest_fresh_reviewed_disc_native_Deck_callers=5,desktop_preview_native_Deck_callers=5,
               new_native_entry='0x11E6C outer task',candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],
               native_code_bytes=b['linked_component_bytes'],total_reservation_bytes=b['component_bytes'],initial_heap_bytes=b['initial_heap_bytes'],
               outer_component_cases_each_address=1280,retained_five_component_cases_final_address=5248,
               full_CPU_full_RAM_fallback_cases_each_address=384,wait_resume_pairs_each_address=192,
               connected_cases_each_address=128,connected_task_slots=101,connected_native_returns=connected['native_returns'],suspended_parent_checks_each_address=2245,
               startup_cases=6,heap_initialize_cases=192,capacity_cases=36,outer_slot_bytes=576,outer_arena_bytes=58176,
               maximum_observed_outer_C_stack_bytes=356,declared_C_stack_region=[144,560],observed_lowest_C_stack_offset=204,observed_margin_bytes=60,
               final_module_byte_identity=True,whole_game_complete=False,fresh_candidate_gameplay_verified=False,real_scheduler_suspension_verified=False,
               new_model_authored_game_code=False,new_training=False,default_promoted=False,authorship='Coordinator native wrapper, capture assembly and layout. Recovered outer algorithm included unchanged. Existing five caller bodies retained.',
               scope='Seeded native CPU fixtures, declared helper/GPU effects and final startup/heap checks. All six caller bodies execute in the connected matrix; deeper helpers are fixtures and E540 executes. This is not a fresh game or whole-game source build.',
               next_action='Run fresh candidate and same-layout original-outer control, qualify real helper suspension/returns and new arena observers, then review video/state/heap fidelity before promotion.')
    save(out/'candidate-facts.json',facts)
    # Review the local outputs against code and deterministic evidence. Keep
    # raw responses intact; do not relabel a coordinator correction as model output.
    model_reviews=[]
    for version in [1,2]:
        path=V/f'outer-local-review-v{version}-current.json';state=read(path);verify(state);folder=Path(state['directory'])
        responses={role:read(folder/role/'result.json')for role in ['Analyst','Reviewer']}
        parse={}
        for role,result in responses.items():
            try:json.loads(result['text']);parse[role]=True
            except ValueError:parse[role]=False
        review=dict(state,status='terminal_outer_local_raw_review_rejected',JSON_parse_by_role=parse,
                    coordinator_review=('Both roles repeat an unsupported576-byte slot insufficiency claim. Coordinator prompt ambiguously said below the lower bound. Actual lowest offset 204 is60bytes ABOVE lower bound144. No observed overflow in the576-byte layout; the earlier512-byte layout did fail.'if version==1 else
                    'Clarified Analyst arithmetic is supported by the gates. Reviewer outputs a self-retracted error item, then an unsupported C-stack return claim and stops mid-sentence with invalid JSON (699completion tokens,700-token request). The saved C stack contains the capture caller return address: restoring it, popping44bytes and RTS is intentional. Existing helper-entry/CPU/RAM checks contradict the alleged defect in their finite scope. Raw Reviewer rejected; no model code or suggested change adopted.'),
                    unchanged_model_code_adopted=False,independent_verification=False,native_Chat_display_verified=False)
        save(V/f'outer-local-review-v{version}-reviewed-current.json',review);save(out/f'local-v{version}-review.json',review);model_reviews.append(review)
    report=ROOT/'reports/Native Outer Deck Task Candidate Review.txt'
    report.write_text('BIWN — NATIVE OUTER TASK CANDIDATE\n\n'
        'Coordinator work now provides a native bridge for outer task 0x11E6C, with per-task C-stack storage, saved live CPU pointers, original helper calls and explicit iteration/wait continuations. The recovered outer algorithm is included unchanged. The five existing native callers are retained.\n\n'
        'The outer component matches the original CPU in 1,280 cases at prototype addresses and again at final addresses. The connected six-caller matrix passes 128 cases across all 101 task slots at each address. Final connected returns are coordinate 832, input 800, face 485, scan 112 and geometry 16, with 2,245 checks that suspended parent frames stay unchanged. Remaining helpers and GPU submissions are fixtures; E540 executes. These are seeded component tests, not fresh gameplay.\n\n'
        'At both addresses, 384 invalid/busy fallback cases match full CPU and full RAM without arena normalization. Another 192 wait/resume pairs compare 64 actual native volatile reads against 64 original polls and then release the flag to resume native work. All 5,248 retained five-caller cases pass at final addresses. Six startup cases verify exact CPU and RAM, including both initialized arenas and per-task pointers. There are 192 heap-initialization and 36 capacity checks.\n\n'
        'The candidate contains 72,204 native code bytes, reserves 260,160 bytes and leaves 137,728 bytes of initial heap. Its outer arena uses 101 slots of 576 bytes (58,176 bytes). The declared C-stack range is slot offsets 144–560, or 416 bytes. Observed use is 356 bytes, reaching offset 204 and leaving 60 bytes above the lower guard. This is finite observed headroom, not arbitrary interrupt safety. Fresh-game resource loading and heap peaks remain untested for this candidate.\n\n'
        'Failures were retained and fixed: the initial 512-byte slot overflowed its lower fence by 4 bytes; a fixture serializer used host padding and little-endian layout; and the first relocated module was loaded 2 bytes before its ELF origin. Explicit 4-byte module/finalizer alignment and origin assertions now pass. The rejected and partial builds remain separate.\n\n'
        'Four actual local predictions ran as two sequential Analyst/Reviewer trials on the same base weights. The first prompt had ambiguous margin wording and both roles made an unsupported stack finding. The clarified Analyst handled the arithmetic; its Reviewer introduced an unsupported claim and returned incomplete JSON. Raw reviews were not adopted. No optimizer update or model-authored game algorithm was added. The native Chat inspection timed out, so these trials used saved local API streams with no native-display claim.\n\n'
        'The installed desktop preview and latest fresh-reviewed disc remain five-caller builds. This separate six-caller candidate is not promoted. Next: fresh candidate versus an original-outer control at the same layout, qualified real helper/scheduler observations, heap/resource loading and video/state review. Whole-game source rebuilding, arbitrary suspension/IRQ, visual/timing/audio/physical fidelity, broad accepted game/Advertising training and future-machine migration remain incomplete.\n\n'
        'Candidate: '+b['derived_disc']+'\nSHA-256: '+b['derived_disc_sha256']+'\n'
        'Final gates: '+str(final_path)+'\nLocal exact prompts/responses:\n'+'\n'.join(str(Path(x['directory'])/'prompts-and-responses.txt')for x in model_reviews)+'\n')
    facts_path=out/'candidate-facts.json';publication=dict(status=facts['status'],directory=str(out),facts=str(facts_path),report=str(report),
        facts_sha256=sha(facts_path),build_snapshot=str(out/'native-Deck-six-disc-build-v1-current.json'),
        dependencies_sha256={str(p):sha(p)for p in [facts_path,out/'native-Deck-six-disc-build-v1-current.json',out/'native-Deck-six-final-v1-current.json',out/'all-verified-dependencies.json']},
        verified_source_records=len(checked),new_predictions=4,new_optimizer_updates=0,desktop_preview_changed=False,whole_goal_complete=False)
    save(out/'publication.json',publication);save(V/'native-Deck-outer-candidate-reviewed-v1-current.json',publication)
    sources=ROOT/'config/current-model-work-sources.json';shutil.copyfile(sources,out/'model-work-sources-before-outer.json');items=read(sources)
    for n in [1,2]:
        item=[f'outer-local-review-v{n}-reviewed-current.json',f'Outer-task local review v{n}: raw assessments and source adjudication; no source adopted']
        assert not any(x[0]==item[0]for x in items);items.insert(0,item)
    save(sources,items)
    goal_path=V/'goal-continuation-current.json';shutil.copyfile(goal_path,out/'previous-goal.json');goal=read(goal_path)
    goal.update(status='active_six_caller_native_candidate_final_gates_pass_fresh_gameplay_pending',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),
        previous_goal_turn_classification='Progress: installed/observed five-caller GUI, published correct current MCP status, and reviewed actual visible local team answers.',
        current_turn_classification='Progress: added native outer-task bridge;1280component/384fallback/192wait-resume/128connectedcases pass at prototype and final addresses; retained5248finalcases andstartup6/heap192/capacity36pass; built separate aligned six-caller candidate. Four actual local reviews adjudicated without adoption.',
        publication=str(V/'native-Deck-outer-candidate-reviewed-v1-current.json'),review=str(report),current_turn_predictions=4,current_turn_optimizer_updates=0,ongoing_finite_workers=[],
        full_objective_complete=False,blocked=False,foreground_UI_preview_changed=False,
        candidate_native_Deck_callers=6,current_GUI_native_callers=5,latest_fresh_reviewed_disc_native_Deck_callers=5,candidate_native_code_bytes=72204,candidate_initial_heap_bytes=137728,
        candidate_total_reservation_bytes=260160,candidate_fresh_gameplay_verified=False)
    goal['remaining_requirements']['game']='Six-caller native candidate passes final-address component/nested/fallback/wait/startup/heap gates. Fresh candidate/control gameplay, real helper suspension and candidate heap/resource peaks remain untested. Installed/latest fresh-reviewed disc remains five callers. Whole-game source rebuilding and fidelity remain incomplete.'
    goal['next_actions']=[facts['next_action'],'Keep the five-caller preview until candidate freshness/fidelity checks pass; preserve all failed local reviews and existing AdvertisingV12rejection.','Complete whole-game recovery, broad accepted research/education training, current portable migration and future-machine acceptance.']
    save(goal_path,goal);print(json.dumps(dict(directory=str(out),candidate_native_callers=6,reviewed_default_callers=5,verified_source_records=len(checked),fresh_gameplay=False),indent=2))


if __name__=='__main__':main()
