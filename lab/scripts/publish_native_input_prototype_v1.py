"""Publish native input source work separately from the pending game image."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    rp=V/'native-input-prototype-v1-current.json';r=read(rp)
    cp=V/'native-input-copied-build-v2-current.json';copied=read(cp)
    assert r['cases']==425 and r['captured_walking_cases']==194 and r['C_stack_bytes']==276
    assert r['payload_bytes']==copied['bytes']==10240 and copied['byte_identical']
    for receipt in [r,copied]:
        for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    for path,digest in copied['copied_source_sha256'].items():assert sha(path)==digest,path
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,digest in w['dependencies_sha256'].items():assert sha(path)==digest,path
    out=V/'native-input-prototype-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p)
    assert p['latest_native_candidate']['native_record_returns']==4777
    pending=p['pending_native_candidate'];assert not pending['default_promoted'] and not pending['final_matrix_video_comparison_pass']
    report=ROOT/'reports/BIWN Native Input Prototype and Clock Diagnosis.txt'
    report.write_text('BIWN — native input component and clock diagnosis\n\n'
        'Latest reviewed gameplay remains v34. The newer v37image remains unpromoted after its additional freshmatrix final-video failure22858pixels. Desktop outdoor checkpoint preview unchanged.\n\n'
        'NEW SOURCE COMPONENT\n'
        'The complete existing recovered191F4input dispatcher now has a separate native68000 C-ABI component prototype. It links the recovered signeddivision C,uses direct volatile global memory access,and has an explicit physical bridge for other retained original helper dependencies. Payload10240bytes;no writable globals. The sole change to the recovered dispatcher source is braces/newline around an existing conditional to satisfy strict GCC warning rules;the guarded original is unchanged. Coordinator authored the adapter/bridge/fixture and portability repair. No new unique original routine is claimed.\n\n'
        'All425walking/backward/run fixtures execute the compiled68000component,including194captured walking inputs. Output,ordered global memory accesses,nonprivate RAM,callee-save registers,argument bytes and immutable native code agree with the checked source/original evidence. Native execution stays entirely inside the component in these cases;the linked Cdivision replaces the original helper call for them. This is not qualification of every input state or the generic helper bridge.\n\n'
        'Measured stack276bytes is for the standalone C-ABI fixture only. Original191F4entry/caller ABI,remaining input states,physical helper arguments across all states,actual task-stack admission,yielding and arbitraryIRQ remain unqualified. This is a component prototype,not an installed game replacement or a new CDI.\n\n'
        'COPIED PACKAGE\n'
        'The copied sources and copied68000SDK produced a byte-identical10240bytebinary. The first copiedbuild exposed GNUmake splitting an absolute path containing spaces. A new Makefile.portable uses relativeSDK/build paths and succeeds inside the existing moved package with spaces in its name. Strict warnings remain enabled;no original sources are overwritten. Rebuild inside the component folder with:make -f Makefile.portable.\n\n'
        'CLOCK DIAGNOSIS\n'
        'A new read-only observer preserves every earlier CPU/RAM/GPU/DSP/video row across four180-frame motion lanes. From one exact starting state,identical60frame Up input admits287native-scene movement clockticks versus290underoriginal scene code,producing22/23whole steps. The other origin admits293/293ticks and23/23steps. Release atframe61 resets fractional remainder tozero.425connected original-dispatch/division checks,including194captured walking calls,match recovered C. This explains the controlled one-step difference;the earlier fresh-route mismatch cause remains unresolved and its failed gate is not waived.\n\n'
        'LOCAL MODELS / TRAINING\n'
        'Prepared local Trace Analyst generated zero responses because the shared inference lease was unavailable;no model was loaded,unloaded or interrupted. Reader43remains the default CLI role;its previous99word/8.27second generation(18.94secondsfirsttext/25.18totalwarmCLI) is historical supplied-snapshot approval. New source-component facts have not received a new local Reader reply,so current-source reply approval is marked unverified. Exact prior prompts/rawresponses remain in the saved199Root/200copied-record indices. No new predictions or optimizer updates this turn;useful untouched-task training gain remains unproven.\n\n'
        'NEXT\n'
        'Qualify all13input states and physical helper bridge with explicit dependency fixtures;then original caller ABI and safe task-stack/yield handling before considering any image integration. Do not rerun the terminal425native/425connected cases merely for receipts. Continue full-game source-only same-console rebuilding,CPU/GPU/DSPintegration,audio/IRQ/wider fidelity,useful training and nativeChat usability. Future256GBhardware capacity remains unmeasured.\n\n'
        'Native proof:'+str(rp)+'\nCopied build:'+str(cp)+'\nClock proof:'+str(V/'input-timing-connected-v1-current.json')+'\n')
    component=dict(status=r['status'],profile='native-191f4-input-dispatch-prototype-v1',artifact_type='source_component_prototype',
        directory=r['directory'],report=str(report),review=str(rp),copied_build=str(cp),module_bytes=10240,
        native_component_cases=425,captured_walking_cases=194,boundary_cases=231,C_stack_bytes=276,
        all_thirteen_states_qualified=False,caller_191F4_ABI_qualified=False,private_task_stack_admission_qualified=False,
        yielding_or_IRQ_qualified=False,copied_SDK_byte_identical=True,copied_recipe_handles_spaces=True,
        new_disc_built=False,fresh_gameplay_verified=False,model_source_installed=False,game_image_changed=False,
        authorship='Coordinator native adapter/physical helper bridge and braces-only portability change around the existing recovered source. No local model generated this component.',
        new_predictions=0,new_training=False,source_unique_functions_recovered=0,
        scope=r['scope']+' CopiedSDKrebuild byte-identical;newrelativeMakefile.portable handles enclosingpackagepathspaces.')
    p['current_native_input_prototype_progress']=component
    p['previous_latest_source_before_native_input_component']=p['latest_source_development']
    p['latest_source_development']=component
    reader=p['current_copied_Reader_progress'];reader.update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,
        current_source_factual_claims_reviewed=False,prior_snapshot_reply_approval_retained=True,new_native_input_component_facts_in_prior_prediction=False)
    p['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v25.py')
    p['checked_current_summary']+=' Newest source work is a separate10240byte native191F4input component,425native cases/194captured inputs/276fixturestackbytes,and copiedSDKbyteidentical. Not a disc or originalcaller/yield/IRQqualification;pendingv37image staysunpromoted. PriorReader43reply approval is historical after this newsource component.'
    p['checked_answer']=p['checked_current_summary'];p['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',p)
    deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(cp):sha(cp),**r['source_sha256'],**copied['source_sha256'],str(report):sha(report)}
    for source in [ROOT/'scripts/show_native_status_v12.py',ROOT/'scripts/portable_biwn_entry_v25.py']:
        deps[str(source)]=sha(source);clone(source,P/'workbench/scripts'/source.name)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py')
    clone(ROOT/'scripts/portable_biwn_entry_v25.py',P/'workbench/portable_biwn.py')
    deps.update({str(x):sha(x)for x in out.iterdir()if x.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    save(V/'native-input-prototype-delivered-v1-current.json',dict(status='terminal_native_input_component_published_v34baseline_v37pending_image_unchanged',
         directory=str(out),report=str(report),new_predictions=0,new_training=False,new_disc_built=False))
    print('Native input prototype delivered;425cases/10240bytes/276stack;copied SDK matches. No disc changed.',flush=True)


if __name__=='__main__':main()
