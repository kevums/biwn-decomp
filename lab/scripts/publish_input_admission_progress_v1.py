"""Publish reviewed local C, guarded entry and complete scripted caller results."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    names = ['local-input-task-admission-author-v1', 'local-input-task-admission-reviewed-v1',
             'native-input-admission-entry-v1', 'native-input-full-caller-v3', 'native-input-copied-build-v5']
    pointers = [V / (name+'-current.json') for name in names]
    receipts = [read(path) for path in pointers]
    author, predicate, entry, caller, copied = receipts
    assert author['new_predictions'] == 1 and author['candidate_statement_edits'] == 0
    assert predicate['host_cases'] == 1440596 and predicate['native_cases'] == 16280
    assert entry['completed'] == 20188 and entry['module_bytes'] == 10580 and entry['preflight_stack_bytes'] == 36
    assert caller['completed'] == 6945 and caller['admitted_native_cases'] == 1264
    assert caller['original_fallback_cases'] == 2528 and caller['input_skipped_cases'] == 3153
    assert caller['raw_volatile_differing_cases'] == 837
    assert copied['byte_identical'] and copied['bytes'] == 10580
    for receipt in receipts:
        for path, digest in receipt['source_sha256'].items():
            assert sha(path) == digest, path
    for path, digest in copied['copied_source_sha256'].items():
        assert sha(path) == digest, path
    raw = read(Path(caller['directory'])/'raw-volatile-differences.json')
    assert Counter(i for row in raw for i in row['registers']) == {1:837}
    assert all((row['original'][1]&65535) == (row['candidate'][1]&65535) for row in raw)
    wp = V / 'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    for path, digest in wrapper['dependencies_sha256'].items():
        assert sha(path) == digest, path
    packet = read(wrapper['packet'])
    out = V / 'input-admission-delivered-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out/'before-packet.json', packet)
    assert packet['latest_native_candidate']['native_record_returns'] == 4777
    assert not packet['pending_native_candidate']['default_promoted']
    transcript = Path(author['directory'])/'prompts-and-responses.txt'
    report = ROOT/'reports/BIWN Local Coder Task Admission and Full Caller Tests.txt'
    report.write_text(
        'BIWN — local Coder, safe preflight and complete caller fixture\n\n'
        'The new source component is a separate10580byte prototype. Its earlier10304byte body/entry prefix is identical. No disc or installed preview was changed. The reviewed gameplay baseline remainsv34;pendingv37still fails its fresh matrix final-video gate by22858pixels. The Desktop outdoor checkpoint remains the earlier six-caller preview.\n\n'
        'WHO DID WHAT\n'
        'Local LMStudio Coder:the package-owned27B6bit model produced the task/stack predicate in one19.7second response. Its398streamed fragments,exact system/user prompts and raw output are saved. No candidate statements were edited. It generated a120byte freestanding68000function using8bytes in the isolated C-ABI fixture. Coordinator:specified the task,authored an independent Python big-integer set/range oracle,the assembly preflight and the caller/portability diagnostics. These were real local inference and code tests,not model weight training or an untouched-task quality benchmark. No optimizer updates or new weights. Native LMStudioChat display was not exercised by this SSE run.\n\n'
        'PREDICATE\n'
        'Accepts only101original1024byte task bases starting0xC0928,user mode,even SP in[task+64,task+1020],even reserve2..960,and sufficient space below SP. Rejects uint32overflow/underflow cases. Host oracle1440596cases:exhaustive one-slot SP/reserve neighborhood,all-slot boundary cross-product,all103429pool/interior/neighbor task addresses,all65536lowSRwords and200000random/near-valid cases. ActualM68000instructions pass16280cases with C-ABI callee-save/returnSP and private-only accesses;no external calls.\n\n'
        'STACK-FIRST ENTRY\n'
        'The coordinator preflight uses no stack access until it has checked user mode,one captured current-task identity,slot range/alignment,evenSP,upperSP bound and40bytes of private headroom. It then calls the unedited local C predicate with a provisional512byte native reserve. The actual preflight frame uses36bytes. All20188route/fence trials pass,including odd/unmapped/extreme SP and invalid task addresses. D0,callee-save,fullSR,SP and inactive bank are preserved up to the selected original/native route. D1/A0/A1are scratch. Task metadata/fences and code stay intact;no public writes before routing. Rejection tails to original191F4before native public effects;this does not make an invalid original stack safe.512is not a proven bound for all real helper nesting or arbitraryIRQ.\n\n'
        'COMPLETE ORIGINAL WORLD CALLER\n'
        'The actual1A188..1A544caller executes through its RTS,with original digit helper,E220/E098CPU mailbox code and originalE588division in the reference. Only the JSRoperand at1A266is redirected;the global191F4entry remains unchanged.2315input fixtures are crossed cyclically with1024world fixtures under three modes:ordinary admitted user-stack,supervisor fallback,and low-headroom user fallback. All6945comparisons pass:1264actual native calls,2528original-input fallbacks and3153original caller input skips. Skips are not counted as native calls. Whole publicRAM,ordered accesses,helper arguments/inputD0seeds,matrix arguments/mailbox transactions,callee-save and finalSRagree. UpperD1differs in837cases;its low word agrees. Raw differences are retained. Helpers for resources,animation,collision,camera/entity and GPU results are scripted;actual GPU arithmetic is not executed. These fixtures therefore do not prove real helper contracts or universal raw ABI.\n\n'
        'The maximum full-caller stack in this fixture is356native/102fallback bytes. It covers a different path set from the earlier348entry/352prefix and392real-yield measurements;it does not replace the larger392bound. Earlier bounded16paired originalTRAP/RTEtrials and104switches belong to the preserved prior body. The new admission tests stop at each route;no new arbitraryIRQ/scheduler proof is claimed.\n\n'
        'HARNESS FAILURES RETAINED\n'
        'Full-caller v1made a false assertion that every caller invokes input;it completed3cases before a legitimate skip. v2had a logging reference to a result before assignment and completed0cases. Both failure records and scripts are retained. v3separates skips from admitted calls/fallbacks and completed6945cases. No game source was changed to work around these harness failures.\n\n'
        'PORTABILITY / NEXT\n'
        'Copied sources and copied SDK rebuild10580bytes identically,using only the moved package compiler and relative make paths that handle spaces. This fixture still uses1C0000as a diagnostic address,not allocated game-image placement. Real retained helper bodies,upperD1contract,IRQ/reentry,reserve sizing,placement/startup/heap/alias/observer qualification and fresh gameplay remain ahead of an image patch. Full source-only same-console rebuilding,CPU/GPU/DSP/audiovisual fidelity,useful untouched-task training gain,native Chat ease and future256GBcapacity remain unfinished.\n\n'
        'Exact local prompts and response:'+str(transcript)+'\n'
        'Local predicate:'+str(pointers[1])+'\nGuard:'+str(pointers[2])+'\nFull caller:'+str(pointers[3])+'\nCopied build:'+str(pointers[4])+'\n')
    progress = dict(status='terminal_local_C_and_stack_first_full_caller_fixture_delivered_not_image',
        profile='native-191f4-input-admission-prototype-v4', report=str(report), directory=str(out),
        module_bytes=10580, prior_prefix_bytes=10304, prior_prefix_byte_identical=True,
        local_Coder_seconds=author['seconds'], local_predictions=1, candidate_statement_edits=0,
        host_cases=predicate['host_cases'], native_predicate_cases=predicate['native_cases'],
        predicate_native_bytes=120, predicate_C_ABI_stack=8, transcript=str(transcript),
        admission_route_cases=entry['completed'], preflight_stack_bytes=36, native_reserve_bytes=512,
        no_stack_access_before_preflight=True, runtime_admission_route_fixture_verified=True,
        full_caller_cases=6945, admitted_native_calls=1264, original_fallback_calls=2528, input_skips=3153,
        full_caller_public_RAM_bus_helpers_final_SR_match=True, raw_D1_upper_differences=837,
        full_caller_D1_low_words_equal=True, full_caller_native_stack=356, fallback_caller_stack=102,
        full_real_helper_bound_proven=False, real_helper_bodies_qualified=False, universal_raw_ABI_qualified=False,
        arbitrary_IRQ_qualified=False, installed_in_game=False, new_disc_built=False,
        copied_build_identical=True, optimizer_updates=0, useful_training_gain_proven=False,
        native_Chat_verified=False, author_review=str(pointers[0]), predicate_review=str(pointers[1]),
        admission_review=str(pointers[2]), full_caller_review=str(pointers[3]), copied_build_review=str(pointers[4]))
    old = packet['current_native_input_prototype_progress']
    packet['previous_native_input_component_before_admission'] = old
    component = dict(old, **{k:v for k,v in progress.items() if k not in old or k in ['status','profile','report','directory','module_bytes','authorship']})
    component.update(profile=progress['profile'], status=progress['status'], report=str(report), directory=str(out), module_bytes=10580,
        full_caller_scripted_dependencies_verified=True, private_task_stack_route_fixture_verified=True,
        private_task_stack_admission_qualified=False, remaining_full_caller_qualified=False,
        authorship='Unedited120byte local C predicate;coordinator156byte assembly preflight appended to unchanged10304bytepriorbody. Caller-specific prototype only.',
        scope='Preserved prior body tests plus new20188admissionroutes/6945fullcallerfixtures.1264native/2528originalfallback/3153skips;837upperD1differencesretained. Realhelpers,fullreserve,arbitraryIRQ,placement/gameimage/freshqualificationremainopen.')
    packet['current_native_input_prototype_progress'] = component
    packet['latest_source_development'] = component
    packet['current_input_admission_progress'] = progress
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source'] = str(ROOT/'scripts/portable_biwn_entry_v28.py')
    packet['checked_current_summary'] += ' NewlocalCoderuneditedpredicatepasses1440596host/16280nativecases;stack-firstguard20188routesandfullcaller6945fixturespasswith837upperD1differencesretained.10580bytecopiedbuildidentical. Realhelper/IRQ/reserve/imagegatesopen;no disc/preview/trainingupdate.'
    packet['checked_answer'] = packet['checked_current_summary']
    packet['recorded_at'] = datetime.now(timezone.utc).isoformat()
    save(out/'current-status-packet.json', packet)
    save(out/'facts.json', progress)
    deps = {str(Path(__file__)):sha(__file__), str(report):sha(report)}
    for path, receipt in zip(pointers, receipts):
        deps[str(path)] = sha(path)
        deps.update(receipt['source_sha256'])
    for name in ['native-input-full-caller-v1','native-input-full-caller-v2']:
        path = V/(name+'-current.json')
        assert read(path)['status'] == 'terminal_full_caller_comparison_failed'
        deps[str(path)] = sha(path)
    for name in ['check_native_input_full_caller_v1.py','check_native_input_full_caller_v2.py',
                 'show_native_status_v15.py','portable_biwn_entry_v28.py']:
        path = ROOT/'scripts'/name
        deps[str(path)] = sha(path)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py')
    clone(ROOT/'scripts/portable_biwn_entry_v28.py',P/'workbench/portable_biwn.py')
    deps.update({str(path):sha(path) for path in out.iterdir() if path.is_file()})
    for path, digest in deps.items():
        source = Path(path)
        assert source.is_relative_to(ROOT) and sha(source) == digest, path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    wrapper.update(packet=str(out/'current-status-packet.json'), dependencies_sha256={**wrapper['dependencies_sha256'], **deps})
    atomic(wp,wrapper)
    clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V/'input-admission-delivered-v1-current.json',dict(status=progress['status'],directory=str(out),report=str(report),
        new_predictions=1,new_training=False,new_disc_built=False,dependencies_sha256=deps))
    print(progress['status'],flush=True)


if __name__=='__main__':
    main()
