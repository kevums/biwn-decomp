"""Deliver entry/caller/yield evidence with every unresolved context preserved."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    ep=V/'native-input-entry-ABI-v2-current.json';cp=V/'native-input-caller-prefix-v1-current.json'
    yp=V/'native-input-real-task-yield-v2-current.json';bp=V/'native-input-copied-build-v4-current.json'
    entry,caller,yielded,copied=[read(x)for x in [ep,cp,yp,bp]]
    assert entry['completed']==caller['completed']==4630 and entry['component_prefix_byte_identical']
    assert entry['raw_return_CCR_differing_cases']==2706 and entry['raw_return_volatile_differing_cases']==4630
    assert caller['final_SR_equal_all_cases']and caller['raw_D1_upper_differing_cases']==1480
    assert yielded['completed']==16 and yielded['actual_switches']==104 and yielded['maximum_native_task_stack']==392
    assert copied['byte_identical']and copied['bytes']==entry['payload_bytes']==10304
    for receipt in [entry,caller,yielded,copied]:
        for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    for path,digest in copied['copied_source_sha256'].items():assert sha(path)==digest,path
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,digest in w['dependencies_sha256'].items():assert sha(path)==digest,path
    out=V/'native-input-entry-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p)
    assert p['latest_native_candidate']['native_record_returns']==4777 and not p['pending_native_candidate']['default_promoted']
    report=ROOT/'reports/BIWN Input Entry Caller and Real Task Yield Tests.txt'
    report.write_text('BIWN — input entry,caller continuation and real task yields\n\n'
        'The game image remains unchanged:v34 reviewed baseline,v37 unpromoted after its fresh matrix-video failure22858pixels. Desktop checkpoint preview unchanged. This turn adds a separate entry/component prototype and bounded original scheduler tests,not a new disc.\n\n'
        'ENTRY ADAPTER\n'
        'A24byte original-style no-stack-argument entry was appended to the corrected input component. All10280earlier component bytes remain identical,so its2315body comparisons are inherited explicitly. New module10304bytes;the copied sources/SDK rebuild is byte-identical.\n\n'
        '4630entry cases(two stack modes across2315cases) match D0,callee-save registers,return/SP,and inactive stack banks. This is a basic entry contract,not raw context equivalence:2706cases differ inCCR and all4630differ in at least one caller-saved register. These are preserved as an unresolved universal-ABI gate. The adapter reports a logical Cerror with ILLEGAL in the fixture;production admission/error handling is not qualified.\n\n'
        'ACTUAL CALLER PREFIX\n'
        'Only the JSRoperand at1A266is redirected in this diagnostic;the original191F4global entry stays intact. Both lanes execute original caller instructions through1A340,including originalE220/E098CPU code. The declared device provider acknowledges4320with0..2busy reads and does not execute GPU arithmetic.4630cases match all publicRAM,ordered accesses,caller-local frame,matrix stack arguments and mailbox transactions. After player integration,full SR and all registers except upperD1agree;1480upper-D1differences remain recorded,with its low word equal. This proves the tested prefix consumes the differing state compatibly;it does not prove the rest of the caller,real GPU output or a universal entry ABI.\n\n'
        'REAL TWO-TASK YIELD\n'
        'Sixteenpaired trials execute originalDF60,TRAP,DE08,RTE andDF66,not a yield RTS stub. TaskBcompletes an animation after1/2/3/7turns and deliberately overwritesD2-D7/A2-A6. The input routine resumes its suspended native Cframe correctly through104actual switches. Helper stack arguments/D0and public effects match;the second task’s entire1024bytes match. Original task records are1024bytes with a fenced960byte stack region.\n\n'
        'Maximum native task-stack use392bytes;second task52;supervisor exception stack6. Canaries and native code remain unchanged. First-task private continuation/frame bytes and supervisor exception scratch are layout-dependent and excluded from cross-lane RAM equality while their bounds/fences are separately checked. First-task savedSRmatches in12of16pairs;raw context equality is not claimed. Animation/resource helpers remain scripted. This is bounded cooperative yield/stack evidence,not real-helper-body,arbitraryIRQ,all-task-admission,live-game or physical-console qualification.\n\n'
        'STACK SCOPES\n'
        'Existing component C-ABI maximum332bytes;entry fixture348;caller-prefix fixture352;actual two-task use392. These are different scopes,not evidence that a prior332byte bound covered every yield path.\n\n'
        'MODEL / FULL GOAL\n'
        'The coordinator authored the24byte adapter and diagnostics. No new local model prediction or optimizer update ran;shared inference lease was unavailable on the turn’s nonblocking probe. No live owner is inferred and no unrelated job/model was interrupted. Reader43remains the default with historical supplied-snapshot approval;new source facts have not received a fresh local reply. Useful untouched-task training gain and native LMStudioChat ease remain unproven.\n\n'
        'Next:qualify the remaining actual caller and retained helper bodies,implement/check runtime admission for the original task stacks,and cover IRQ/reentry before any callsite-specific image integration. Preserve the universal raw-return differences and the independent v37fresh matrix failure. Full source-only same-console game rebuilding,CPU/GPU/DSP/audiovisual fidelity,training quality and future256GBcapacity remain unfinished.\n\n'
        'Entry proof:'+str(ep)+'\nCaller proof:'+str(cp)+'\nYield proof:'+str(yp)+'\nCopied build:'+str(bp)+'\n')
    previous=p['current_native_input_prototype_progress'];p['previous_native_input_component_before_entry']=previous
    component=dict(previous,status='terminal_input_entry_basic_contract_caller_prefix_and_bounded_task_yield_checked',
        profile='native-191f4-input-entry-prototype-v3',report=str(report),directory=str(out),module_bytes=10304,
        entry_review=str(ep),caller_prefix_review=str(cp),task_yield_review=str(yp),copied_build=str(bp),
        inherited_component_bytes=10280,component_prefix_byte_identical=True,appended_entry_bytes=24,
        entry_ABI_cases=4630,basic_D0_callee_save_stack_bank_contract_verified=True,
        raw_entry_CCR_differing_cases=2706,raw_entry_caller_saved_differing_cases=4630,
        caller_prefix_cases=4630,caller_prefix_final_SR_equal=True,caller_prefix_upper_D1_differing_cases=1480,
        entry_fixture_stack_bytes=348,caller_prefix_fixture_stack_bytes=352,bounded_two_task_pairs=16,
        bounded_two_task_switches=104,bounded_two_task_yield_verified=True,actual_original_TRAP_RTE_executed=True,
        bounded_task_stack_bytes=392,bounded_task_stack_capacity=960,second_task_stack_bytes=52,supervisor_stack_bytes=6,
        universal_raw_context_ABI_verified=False,caller_191F4_ABI_qualified=False,remaining_full_caller_qualified=False,
        real_retained_helper_bodies_qualified=False,private_task_stack_admission_qualified=False,yielding_or_IRQ_qualified=False,
        new_disc_built=False,fresh_gameplay_verified=False,game_image_changed=False,
        authorship='Coordinator24byteentryadapter around the byte-identical corrected component;not local-model output.',
        scope='EntryD0/callee-save/SP/stackbanks pass4630cases,but2706rawCCR/allcaller-save differences remain. Actualcallerprefix/publicstate/flags/matrixmailbox match4630;upperD1differs1480. Sixteenoriginaltwo-taskTRAP/RTEfixtures/104switches resume Cframes andfit392/960fencedbytes. Scripted animation/resource and ack-only GPU providers. Not universalABI,realhelperbody,alltaskadmission/arbitraryIRQ/freshgame/image/console proof.')
    p['current_native_input_prototype_progress']=component;p['latest_source_development']=component
    p['current_input_entry_progress']={k:component[k]for k in ['entry_ABI_cases','raw_entry_CCR_differing_cases','raw_entry_caller_saved_differing_cases','caller_prefix_cases','caller_prefix_final_SR_equal','caller_prefix_upper_D1_differing_cases','bounded_two_task_pairs','bounded_two_task_switches','bounded_task_stack_bytes','bounded_task_stack_capacity','entry_review','caller_prefix_review','task_yield_review']}
    p['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False,new_entry_caller_yield_facts_in_prior_prediction=False)
    p['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v27.py')
    p['checked_current_summary']+=' Newinputentryprototype10304bytes preserves10280bytebody.4630basicentrycasespasswithrawcontextdifferencesretained;actualcallerprefixpublicstate/flagsmatch4630,upperD1remainsdifferent1480. Sixteenpairedactualtwo-taskTRAP/RTEtrials104switchesfit392/960fencedstackbytes. No gameimage or universalABI/IRQpromotion.'
    p['checked_answer']=p['checked_current_summary'];p['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',p)
    deps={str(Path(__file__)):sha(__file__),str(report):sha(report)}
    for pointer,receipt in [(ep,entry),(cp,caller),(yp,yielded),(bp,copied)]:deps[str(pointer)]=sha(pointer);deps.update(receipt['source_sha256'])
    for source in [V/'native-input-real-task-yield-v1-current.json',ROOT/'scripts/check_native_input_real_task_yield_v1.py']:
        deps[str(source)]=sha(source)
    for source in [ROOT/'scripts/show_native_status_v14.py',ROOT/'scripts/portable_biwn_entry_v27.py']:
        deps[str(source)]=sha(source);clone(source,P/'workbench/scripts'/source.name)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py');clone(ROOT/'scripts/portable_biwn_entry_v27.py',P/'workbench/portable_biwn.py')
    deps.update({str(x):sha(x)for x in out.iterdir()if x.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    save(V/'native-input-entry-delivered-v1-current.json',dict(status='terminal_entry_caller_bounded_real_yield_progress_published_no_game_image_change',directory=str(out),report=str(report),new_predictions=0,new_training=False,new_disc_built=False))
    print('Entry/caller/real task-yield evidence delivered;raw context and game gates remain explicit.',flush=True)


if __name__=='__main__':main()
