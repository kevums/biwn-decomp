"""Publish all-state fixture coverage and the separately preserved failed gate."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    badp=V/'native-input-all-states-v2-current.json';rp=V/'native-input-all-states-v3-current.json'
    cp=V/'native-input-copied-build-v3-current.json';lp=V/'input-helper-seeds-exposed-v1-current.json'
    bad,r,copied,lesson=[read(x)for x in [badp,rp,cp,lp]]
    assert bad['completed']==1890 and bad['original_helper_seed_mismatch_cases']==26
    assert r['completed']==2315 and r['original_helper_seed_mismatch_cases']==0
    assert r['all_thirteen_state_fixture_paths_verified']and r['original_helper_D0_seed_match']
    assert r['payload_bytes']==copied['bytes']==10280 and r['native_C_ABI_stack_bytes']==332 and copied['byte_identical']
    assert len(r['physical_helper_targets'])==18 and lesson['optimizer_updates']==0 and lesson['examples']==2
    for receipt in [bad,r,copied,lesson]:
        for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    for path,digest in copied['copied_source_sha256'].items():assert sha(path)==digest,path
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,digest in w['dependencies_sha256'].items():assert sha(path)==digest,path
    out=V/'native-input-seed-correction-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p)
    assert p['latest_native_candidate']['native_record_returns']==4777 and not p['pending_native_candidate']['default_promoted']
    report=ROOT/'reports/BIWN Native Input All States and Register Seed Correction.txt'
    report.write_text('BIWN — all-state input component and register correction\n\n'
        'The reviewed game image remains v34. The separate v37image remains unpromoted after its fresh matrix-video comparison failed22858pixels. Desktop outdoor checkpoint preview unchanged. This work changes a versioned source/component prototype,not a game image.\n\n'
        'FAILED GATE PRESERVED\n'
        'The unmodified10240byte input component passed1890all-state fixtures for final output,ordered global accesses and nonprivate memory. But a newly added dependency-entry check found26equipment cases with incorrect incomingD0at1B002,1AF04and152A2. Nativebridge stack arguments and its propagation of the logical Cseed were correct;the recovered logical C lacked the original intermediate D0bookkeeping. Scripted helper return values had hidden this gap. The26counterexamples and failed gate remain saved.\n\n'
        'SOURCE CORRECTION\n'
        'A new input-dispatch-native-v2variant preserves the originalD0seeds without adding or reordering memory accesses:1B002gets sign-extended slot*2;1AF04gets sign-extended actor*10on removal or new slot*2on addition;152A2gets bytecount*2while its separate stack argument is that value+16. These are grounded in original instruction boundaries1951E/1953A/19568and195D4/1960E/1963C. The guarded original and earlier component are unchanged. Coordinator authored the correction;no local model generated it.\n\n'
        'PASSING COMPONENT CHECKS\n'
        'Corrected component10280bytes.2315original/hostC/native comparisons pass:the1890all-state cases plus425walking/backward/run regressions,including194captured walking inputs. Every finalD0,ordered global read/write/helper argument,nonprivate RAM and compared dependency-entryD0seed agrees. All13states and out-of-range state guards are exercised. The physical bridge reaches18retained helper targets,withD1/A0/A1deliberately clobbered on their fixture returns;stack arguments and callee-save registers remain correct. OriginalE588division instructions execute in the reference;the native component uses recovered signeddivision C. Other helper bodies are scripted dependencies,not real-body or scheduler proof.\n\n'
        'Broad fixture stack peak332bytes was observed both before and after the correction. The earlier276bytes came from walking-only coverage;it was not a whole-dispatcher bound. The corrected component is40bytes larger. The copied sources/SDK rebuild is byte-identical10280bytes using the relative-path portable recipe.\n\n'
        'LIMITS / NEXT\n'
        'Public entry remains a C-ABI test entry. Original191F4caller entry/return ABI,real retained helper behavior,actual task-stack admission,yielding and arbitraryIRQ are unqualified. The fixture allows a large private stack region;332observed bytes is not proof of safe engine-task allocation. No native-image integration,fresh-game rerun,same-console whole-game rebuild or fidelity completion is claimed. Continue caller/admission and scheduler/yield tests before considering an image;preserve the separate failed v37fresh matrix gate.\n\n'
        'LOCAL MODELS / TRAINING\n'
        'Shared inference lease remained unavailable on actual nonblocking probes;no live owner is inferred. No model was loaded,unloaded or interrupted and no inference/optimizer updates ran. Two development SFT lessons grounded in the26failed and2315passing cases are prepared and copied,explicitly exposed and excluded from untouched quality evaluation. This is prepared training data,not trained weights or useful measured gain. Earlier base/adapter pilot each0/4still stands. Native LMStudioChat usability and future256GBhardware measurements remain unverified. Reader43remains the default with historical supplied-snapshot approval;newsource facts have not received a fresh local reply.\n\n'
        'Failed gate:'+str(badp)+'\nCorrected proof:'+str(rp)+'\nCopied build:'+str(cp)+'\nPrepared lessons:'+str(lp)+'\n')
    previous=dict(p['current_native_input_prototype_progress']);previous.update(known_all_state_dependency_seed_gate_failed=True,
        all_state_failed_gate=str(badp),all_state_failed_seed_cases=26)
    p['previous_native_input_component_before_seed_fix']=previous
    component=dict(status=r['status'],profile='native-191f4-input-dispatch-prototype-v2',artifact_type='source_component_prototype',
        directory=r['directory'],report=str(report),review=str(rp),copied_build=str(cp),module_bytes=10280,native_component_cases=2315,
        captured_walking_cases=194,boundary_cases=231,C_stack_bytes=332,prior_walking_only_stack_bytes=276,
        all_thirteen_state_fixture_paths_verified=True,retained_helper_fixture_targets=18,original_dependency_D0_seeds_verified=True,
        original_dependency_D0_seed_mismatches=0,all_thirteen_states_qualified=False,caller_191F4_ABI_qualified=False,
        real_retained_helper_bodies_qualified=False,private_task_stack_admission_qualified=False,yielding_or_IRQ_qualified=False,
        copied_SDK_byte_identical=True,copied_recipe_handles_spaces=True,new_disc_built=False,fresh_gameplay_verified=False,
        model_source_installed=False,game_image_changed=False,new_predictions=0,new_training=False,source_unique_functions_recovered=0,
        authorship='Coordinator equipment D0register-bookkeeping correction to existing recovered source/native adapter. No local model generated this variant.',
        scope=r['scope']+' CopiedSDKbinary is byte-identical10280bytes. Broadfixturestack332before/after,not the earlier walking-only276bound. Actualcaller/taskstack/yield/IRQ and real retainedhelper bodies remain unqualified.')
    p['current_native_input_prototype_progress']=component;p['latest_source_development']=component
    p['current_input_all_states_progress']={k:v for k,v in r.items()if k not in ['source_sha256','pid']}
    p['input_dependency_seed_failure_preserved']=dict(status=bad['status'],review=str(badp),cases=1890,failed_seed_cases=26,waived=False)
    p['input_helper_seed_development_lessons']=dict(status=lesson['status'],manifest=str(lp),examples=2,exposed_case_families=1,heldout_families=0,optimizer_updates=0,new_weights=False)
    p['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,
        current_source_factual_claims_reviewed=False,new_native_input_seed_facts_in_prior_prediction=False)
    p['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v26.py')
    p['checked_current_summary']+=' Nativeinputv2corrects26equipmentD0seedcounterexamples.2315all-state/capturedregressioncases pass with0seedmismatches;component10280bytes,332broadfixturestack,copiedSDKbyteidentical. Originalcaller/taskstack/yield/IRQ and realhelper bodies remainunqualified. TwoexposedSFTlessons prepared;zero optimizerupdates.'
    p['checked_answer']=p['checked_current_summary'];p['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',p)
    deps={str(Path(__file__)):sha(__file__),str(report):sha(report)}
    for pointer,receipt in [(badp,bad),(rp,r),(cp,copied),(lp,lesson)]:deps[str(pointer)]=sha(pointer);deps.update(receipt['source_sha256'])
    for source in [ROOT/'scripts/show_native_status_v13.py',ROOT/'scripts/portable_biwn_entry_v26.py']:
        deps[str(source)]=sha(source);clone(source,P/'workbench/scripts'/source.name)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py');clone(ROOT/'scripts/portable_biwn_entry_v26.py',P/'workbench/portable_biwn.py')
    deps.update({str(x):sha(x)for x in out.iterdir()if x.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    save(V/'native-input-seed-correction-delivered-v1-current.json',dict(status='terminal_corrected_all_state_input_component_published_no_game_image_change',
        directory=str(out),report=str(report),new_predictions=0,new_training=False,new_disc_built=False))
    print('Nativeinputv2published:2315cases/zero seedmismatches/10280bytes/332fixturestack/copiedSDKidentity.',flush=True)


if __name__=='__main__':main()
