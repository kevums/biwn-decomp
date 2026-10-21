"""Publish finished final/nesting gates and clarified model outcomes, without promotion."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    prior=read(V/'geometry-faces-recovery-reviewed-v1-current.json')
    for p,h in prior['dependencies_sha256'].items():assert sha(p)==h,p
    build=read(V/'native-Deck-faces-disc-build-v1-current.json')
    master=read(V/'native-Deck-faces-final-v1-current.json')
    assert master['status']=='terminal_deeper_candidate_final_component_startup_heap_gates_pass'
    assert len(master['results'])==8 and all(x['exit_code']==0 for x in master['results'].values())
    names=['native-Deck-faces-final-v1-current.json','native-faces-geometry-alias-v1-current.json','native-deck-alias-nesting-faces-final-v1-current.json']
    proofs={n:read(V/n)for n in names}
    for n in names[1:]:assert proofs[n]['completed']==128
    for proof in [build,*proofs.values()]:
        for p,h in proof['source_sha256'].items():assert sha(p)==h,p
    assert sha(build['derived_disc'])==build['derived_disc_sha256']
    diag=read(V/'game-header-diagnostic-v1-current.json')
    assert diag['status']=='terminal_paired_diagnostic_pending_review'and diag['original_results_unchanged']
    for p,h in diag['original_results_sha256'].items():assert sha(p)==h,p
    out=V/'faces-final-and-model-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'prior-source-publication.json',prior);save(out/'candidate-build.json',build)
    for name,proof in proofs.items():save(out/name,proof)
    results={};model_files=[]
    for phase in ['base','adapter']:
        p=V/f'game-header-diagnostic-v1-{phase}-evaluation-current.json';e=read(p)
        assert e['status']=='terminal_code_evaluation'and e['total']==4 and e['daily_model_restored']
        cases=[];save(out/(phase+'-diagnostic.json'),e);model_files.append(out/(phase+'-diagnostic.json'))
        for row in e['results']:
            folder=Path(e['directory'])/row['function'];result=read(folder/'result.json');log=(folder/'check.log').read_text()
            candidate=folder/Path(next(x for x in read(Path(diag['directory'])/'cases.json')if x['function_id']==row['function'])['source']).name
            assert sha(candidate)==row['candidate_sha256']and result['verified']==row['verified']
            assert 'file not found'not in log and 'No such file or directory'not in log
            classification='truncated_output'if row['finish_reason']=='length'else'compiler_failure'if 'error:'in log else'CPU_RAM_or_execution_mismatch'
            cases.append(dict(function=row['function'],verified=row['verified'],classification=classification,check_log=str(folder/'check.log')))
            model_files.extend([folder/'prompt.json',folder/'response.txt',folder/'result.json',folder/'check.log',candidate])
        results[phase]=dict(passed=e['passed'],total=e['total'],cases=cases)
    assert results['base']['passed']==results['adapter']['passed']==0
    model_report=ROOT/'reports/Game Geometry Filename Clarification Review.txt'
    model_report.write_text('GAME MODEL — FILENAME-CLARIFIED COMPARISON\n\n'
        'The separate paired diagnostic completed eight local generations. Base:0/4accepted. Selected step40adapter:0/4accepted. Explicit filenames removed the missing-header failures;no output was hand-edited and no acceptance gate was relaxed. Both phases restored the daily LMStudio model.\n\n'
        'Base release,acquire and plane-layout outputs reached functional CPU/RAM failures. Base load failed the existing compiler warning checks. Adapter release reached a functional mismatch;acquire and load failed compiler warning checks. Adapter plane-layout reached the5,000token limit and failed compilation. The base plane output finished in4,209tokens but failed the full gate. These outputs do not justify promoting the trained adapter.\n\n'
        'The diagnostic was frozen after inspecting the original pilot failures. It changes only a filename clarification in each prompt. The checkpoint was already selected from validation and was not reselected. This is an adaptive development comparison,not an untouched holdout or a general model ranking. The original4+4benchmark results and selection hashes remain unchanged.\n\n'
        'Next:use bounded local repair with actual compiler/emulator counterexamples and compare the installed coder model on identical tasks. Record each Author/Repair prompt and unchanged response;only the complete machine checks may accept generated game code. No further blind training is justified by loss alone.\n\n'
        'Exact requests/results:Model Prompts and Responses.command. Summary:Game Model Training Progress.command.\n')
    model_review=dict(status='terminal_filename_clarified_paired_model_results_reviewed_unpromoted',directory=str(out),report=str(model_report),results=results,
        selected_step=40,new_predictions=8,new_training=False,default_promoted=False,original_results_unchanged=True,
        source_sha256={str(p):sha(p)for p in [Path(__file__),V/'game-header-diagnostic-v1-current.json',model_report,*model_files]})
    save(out/'model-review.json',model_review);save(V/'game-header-diagnostic-reviewed-v1-current.json',model_review)
    facts=read(prior['facts']);save(out/'prior-prototype-facts.json',facts)
    facts.update(status='terminal_five_helper_disc_final_and_alias_gates_pass_fresh_pending',directory=str(out),
        final_address_gates_verified=True,new_nesting_verified=True,native_disc_qualified=False,new_fresh_gameplay_verified=False,
        final_geometry_cases=256,final_retained_cases=4992,final_fallback_cases=1280,startup_cases=6,heap_initialize_cases=192,
        capacity_cases=36,outer_component_cases=1280,outer_fallback_cases=384,outer_wait_resume_pairs=192,alias_cases=256,
        candidate_disc=build['derived_disc'],candidate_disc_sha256=build['derived_disc_sha256'],native_code_bytes=build['linked_component_bytes'],
        total_reservation_bytes=build['component_bytes'],candidate_initial_heap_bytes=build['initial_heap_bytes'],
        installed_preview_changed=False,scope=facts['scope']+' Separate candidate now passes all eight final-address/startup/heap/outer gates and256explicit alias cases. Geometry/coordinate alias fixture uses zero descriptor face count;nonzero face counts remain covered by separate native256matrix. Natural combined six-caller integration,observer-qualified fresh gameplay,real helper/device suspension and fidelity remain unverified.',
        next_action='Complete the five-helper six-caller connected matrix and qualify updated read-only runtime observers,then run a fresh same-layout original-geometry control. Preserve all six public callers and the installed preview. Recover10734with actual MMIO/device effects and existing formatter/text work;resolve fidelity differences.')
    report=ROOT/'reports/Five Geometry Helpers Final Address Review.txt';facts['report']=str(report)
    report.write_text('BIWN — FIVE INTERNAL GEOMETRY HELPERS: FINAL ADDRESS AND NESTING\n\n'
        'The separate candidate retains all six public Deck callers and compiles five internal geometry helpers:10968,10BA4,11384,110D4and1142E. Their global original helper entries remain unpatched. The installed BIWN Test Preview remains unchanged. This is not a full-game source rebuild.\n\n'
        'All eight final-address gate processes passed:256geometry,4,992retained-caller,1,280fallback,six startup,192heap initialization,36capacity,1,280outer component,384outer fallback and192outerwait/resume pairs. Both final native modules match deployed disc component bytes exactly. The new candidate has81,514native code bytes,reserves269,504bytes,copies107,904bytes and starts with128,384heap bytes.\n\n'
        'Coordinate/geometry and input/face alias checks each pass128cases. Bothstackbanks/allCCR,four task slots and three guest stack depths are covered. An injected helper JSR forces an inner caller into original-code busy fallback while exact suspended parent frame/stack bytes remain unchanged. Coordinate/geometry uses zero descriptor face count;nonzero counts were checked in the separate256native geometry matrix. These are explicit nesting fixtures,not arbitrary interrupts or natural gameplay.\n\n'
        'The geometry C stack peaks at164of176bytes in its component matrix;no arena was added. The original seven monitor fences remain enforced. Fresh-gameplay resource minima and timing are not established by these component checks. The complete face builder also retains its640host cases,188instruction locations,330host-error cases,2,073GPU fixture calls and four rejected semantic defects.\n\n'
        'New combined six-caller/five-helper integration and read-only observer qualification remain pending before a fresh candidate/control route. E26CGPUand10734debug effects remain fixtures in the component matrices. Real device composition,arbitrary suspension/IRQ,audio,physical console and whole-game fidelity remain incomplete. The earlier four-helper fresh run had94differing video frames despite equal final video.\n\n'
        'The builder initially published the new receipt under the old four-helper name. The old receipt was restored byte-exact against its saved SHA;the new receipt has its own name. Builder-as-run and repair notes are preserved. All eight new final gates completed without receipt-name repair.\n\n'
        'Next:'+facts['next_action']+'\n')
    save(out/'facts.json',facts)
    paths=[Path(__file__),out/'facts.json',report,out/'candidate-build.json',out/'prior-source-publication.json',out/'prior-prototype-facts.json',*[out/n for n in names]]
    publication=dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),
        dependencies_sha256={str(p):sha(p)for p in paths},whole_objective_complete=False,new_predictions=0,new_training=False)
    save(out/'publication.json',publication);save(V/'geometry-faces-final-reviewed-v1-current.json',publication)
    print(out,flush=True)
if __name__=='__main__':main()
