"""Publish three recovered algorithms and actual rejected local source trial."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    out=V/'deeper-Deck-helper-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    component=V/'deck-geometry-helpers-v1/20261020T153545.559683Z/protocol.json'
    connected=V/'deck-geometry-connected-helpers-v1/20261020T153801.891267Z/protocol.json'
    c,n=read(component),read(connected)
    assert c['status']=='terminal_three_deeper_helpers_full_CPU_RAM_match'and c['completed']==772 and c['instruction_locations']==[80,80]and c['guard_cases']==173
    assert n['status']=='terminal_geometry_with_three_recovered_helpers_CPU_RAM_match'and n['completed']==256
    checked={}
    for s in [c,n]:
        for p,h in s['source_sha256'].items():assert sha(p)==h,p;checked[p]=h
    native=Path(c['directory'])/'native-build/build.json';build=read(native)
    assert sha(build['source'])==build['source_sha256']and sha(build['object'])==build['object_sha256']and not build['undefined_symbols']
    faults_path=V/'deck-deeper-helper-fault-controls-v1-current.json';faults=read(faults_path);assert len(faults['negative_controls'])==4
    for x in faults['negative_controls']:
        assert x['rejected']and x['proof']['status']=='terminal_original_CPU_or_RAM_comparison_rejected'
        assert Path(x['proof']['counterexample']).exists()
    session_dir=Path.home()/'.lmstudio/local-ai-lab/runs/native-chat-teams/2026-10-20T15-33-34.232Z-237677cb-5107-466a-bdac-f601e325a99e'
    session=read(session_dir/'session.json');assert session['status']=='terminal_research_team_generation_complete_semantic_review_required'and len(session['roles'])==3
    assert session['evidence']['topic']=='deck_deeper_helpers_source'
    baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)==session['evidence']['evidence']['baseline_sha256']
    # Existing oracle qualification pins these same original bytes and binaries.
    prior=read(V/'Deck-scene-source-current.json')
    for p,h in prior['native_dependencies_sha256'].items():assert sha(p)==h,p;checked[p]=h
    raw_dir=V/'deck-geometry-helpers-v1/20261020T153809.717012Z';raw=read(raw_dir/'protocol.json')
    assert raw['status']=='terminal_original_CPU_or_RAM_comparison_rejected'and raw['completed']==0
    assert sha(session_dir/'raw-Restorer.c')==hashlib.sha256(session['roles'][1]['response'].encode()).hexdigest()
    diagnostics=read(raw_dir/'root-diagnostics/cases.json');assert len(diagnostics)==6 and all(x['register_differences']or x['RAM_difference_count']or not x['helper_entries_equal']for x in diagnostics)
    for p in session_dir.iterdir():
        if p.is_file():shutil.copyfile(p,out/p.name)
    text=['ACTUAL NATIVE CHAT SOURCE RECOVERY','3sequentialsame-weight passes; no optimizer update or independent verification.','The actual Analyst also simulated later roles. Those embedded sections are not actual agent passes.','']
    for i,role in enumerate(session['roles'],1):text+=['ACTUAL ROLE '+role['role'],'EXACT PROMPT',(session_dir/f'{i}-{role["role"]}-prompt.txt').read_text(),'RAW RESPONSE',role['response'],'']
    (out/'prompts-and-responses.txt').write_text('\n'.join(text))
    review=dict(status='terminal_deeper_helper_local_raw_source_rejected',directory=str(out),actual_predictions=3,optimizer_updates=0,native_Chat_initiated_and_partial_output_observed=True,
        final_Reviewer_UI_observed=False,final_UI_observation='Mac locked; completed saved session reviewed headlessly per user instruction.',same_weight_independent=False,raw_source_adopted=False,
        local_source_compiles=True,raw_source_matches_first_case=False,first_case_passed_count=0,diagnostic_cases=diagnostics,
        coordinator_review='Raw Restorer leaves D0,D1,A1 and oftenA0 updates in C locals without committing CPU registers;10BA4timer branch and frame compare reversed;11384pushes a word as long,uses stale record base after110D4 mutation,and loses instruction CCR effects. Rejected unchanged. Analyst violates role contract by simulating Restorer/Reviewer. Actual Reviewer correctly rejects overall and identifies word-push/CCR issues, but its10988unsigned-comparison finding is wrong: original CMP/BHI is unsigned after MOVEA sign extension. Its ADDQ.L always clearsV/C wording is also wrong; ADDQ computes both. Agreement and rejection labels are not correctness evidence.',
        source_sha256={str(p):sha(p)for p in [session_dir/'session.json',session_dir/'raw-Restorer.c',raw_dir/'protocol.json',raw_dir/'counterexample.json',raw_dir/'root-diagnostics/cases.json',out/'prompts-and-responses.txt']})
    save(out/'local-review.json',review);save(V/'deeper-Deck-helper-local-reviewed-v1-current.json',review)
    for p,name in [(component,'component.json'),(connected,'connected.json'),(native,'native-object-build.json'),(faults_path,'fault-controls.json')]:shutil.copyfile(p,out/name)
    save(out/'verified-original-dependencies.json',checked)
    report=ROOT/'reports/Three Deeper Deck Helpers Recovery Review.txt'
    report.write_text('BIWN — THREE DEEPER GEOMETRY HELPERS\n\n'
        'Three additional algorithm bodies are recovered as structured coordinator C:10968 clears record bytes,10BA4 advances animated texture selection,and11384 initializes the geometry matrix record. The current six-caller preview/disc is unchanged. These helpers are not yet installed as native game code.\n\n'
        'The complete functions includingRTS match original68000 execution in772finite cases:260clear-record,256texture and256matrix cases. All80instruction locations are reached. Comparisons cover fullCPU,2MBRAM,stack banks,partial registers,all32CCR values across each routine,word/frame wraps,large CLR counts and mutable110D4effects.173host bus/service/work-limit cases check error handling. This is aggregate finite coverage,not every parameter/CCR cross-product,arbitrary aliases,MMIO,IRQ or timing.\n\n'
        'A separate256case connected comparison executes geometry11AD4 plus all three recovered helpers as C against all four original68000 bodies. Ordered callee CPU/RAM entries match. Original110D4 remains a declared fixture;1142E and10734 are still fixture dependencies. No source-processor ownership or native game installation is claimed. Four deliberate algorithm mutations are rejected:clear-base offset,reversed timer branch,word-as-long push,and stale post-helper counter.\n\n'
        'The coordinator C compiles forM68000 to a5,194-byte text object with no undefined symbols. That object has not yet been executed or linked into a disc; host-C equivalence and successful cross-compilation are separate results.\n\n'
        'Three actual local predictions ran in LM Studio Chat. Analyst simulated later roles inside its output; those are not actual extra passes. Actual Restorer C compiles but fails its firstCPU case and all six targeted root diagnostics. It loses register updates,reverses timer/frame branches,and pushes a word as32bits. No raw source adopted. Actual Reviewer rejects overall but gives an incorrect unsigned-loop diagnosis and incorrect ADDQflag explanation. Exact outputs retained;coordinator review is separate. No optimizer update occurred. Final UI inspection encountered lock; saved session confirms completion and no unlock was requested.\n\n'
        'Next:execute relocated M68000 helper code,integrate three algorithms into the native geometry path while preserving real110D4calls,qualify C-stack/fallback/nesting,then compare fresh candidate/control routes. Keep the installed preview until those gates pass. Deeper1142E/10734/110D4 recovery,whole-game source rebuilding,fidelity,broad accepted game/Advertising training and portable migration remain open.\n\n'
        'Recovered source: '+c['source']+'\nComponent proof: '+str(component)+'\nConnected proof: '+str(connected)+'\nExact prompts/responses: '+str(out/'prompts-and-responses.txt')+'\n')
    facts=dict(status='terminal_three_deeper_Deck_helpers_recovered_and_component_reviewed',directory=str(out),report=str(report),recovered_entries=['10968','10ba4','11384'],authorship='Coordinator structured C; raw local Restorer rejected unchanged.',
        component_cases=772,original_instruction_locations=80,host_error_cases=173,connected_cases=256,native_object_text_bytes=5194,native_object_executed=False,native_disc_changed=False,
        installed_native_Deck_callers=6,new_native_caller_integrations=0,original_dependency_110D4_is_fixture=True,remaining_geometry_helpers=['110d4','1142e','10734'],actual_local_predictions=3,optimizer_updates=0,
        local_review=str(V/'deeper-Deck-helper-local-reviewed-v1-current.json'),whole_game_complete=False,
        source_sha256={str(p):sha(p)for p in [Path(__file__),report,out/'component.json',out/'connected.json',out/'native-object-build.json',out/'fault-controls.json',out/'verified-original-dependencies.json',out/'local-review.json',Path(c['source']),Path(build['object'])]})
    save(out/'review.json',facts);save(V/'deeper-Deck-helpers-reviewed-v1-current.json',facts)
    # Preserve exact earlier frontend sources instead of implying they were run
    # with this new source-recovery route installed.
    old_chat_path=V/'visible-six-caller-Chat-reviewed-current.json';old=read(old_chat_path);script=ROOT/'scripts/native_chat_team_context.py'
    archived=Path(old['directory'])/'native_chat_team_context-as-run-six-preview.py'
    assert sha(archived)==old['source_sha256'][str(script)]
    shutil.copyfile(old_chat_path,out/'previous-six-preview-Chat-review.json');old['source_sha256'][str(archived)]=old['source_sha256'].pop(str(script));save(old_chat_path,old)
    sp=V/'native-Deck-current-status-v1-current.json';state=read(sp);shutil.copyfile(sp,out/'previous-current-status-publication.json')
    pp=Path(state['packet']);packet=read(pp);shutil.copyfile(pp,out/'previous-current-status-packet.json')
    packet['deeper_helper_recovery']=facts;save(pp,packet)
    state['dependencies_sha256'][str(old_chat_path)]=sha(old_chat_path);state['dependencies_sha256'][str(pp)]=sha(pp);state['dependencies_sha256'][str(V/'deeper-Deck-helpers-reviewed-v1-current.json')]=sha(V/'deeper-Deck-helpers-reviewed-v1-current.json');save(sp,state)
    ip=ROOT/'config/current-model-work-sources.json';shutil.copyfile(ip,out/'previous-model-work-sources.json');items=read(ip)
    item=['deeper-Deck-helper-local-reviewed-v1-current.json','Actual native Chat:three deeper geometry helpers;raw C rejected by CPU oracle;Reviewer errors retained']
    assert not any(x[0]==item[0]for x in items);items.insert(0,item);save(ip,items)
    gp=V/'goal-continuation-current.json';shutil.copyfile(gp,out/'previous-goal.json');g=read(gp)
    g.update(status='active_three_deeper_helpers_component_pass_native_integration_pending',recorded_at=datetime.now(timezone.utc).isoformat(),
        previous_goal_turn_classification='Progress:six-caller GUI run mapping,source-bound nativeChat/actual one-click output tests completed.',
        current_turn_classification='Progress:three complete deeper algorithms recovered;772CPU/RAM cases and173error checks pass;256connected geometry cases pass;4faults rejected;M68000object compiles.Three actual local Chat passes rawC/Reviewer reviewed and rejected.',
        current_turn_predictions=3,current_turn_actual_local_predictions=3,current_turn_optimizer_updates=0,current_turn_new_game_routines=3,current_turn_new_native_caller_integrations=0,
        deeper_helper_delivery=str(V/'deeper-Deck-helpers-reviewed-v1-current.json'),latest_source_recovery_report=str(report),full_objective_complete=False,blocked=False,ongoing_finite_workers=[])
    g['remaining_requirements']['game']='Three deeper geometry algorithms pass772component and256connected cases but are not native-disc integrated. Current preview remains reviewed six-caller build. Original110D4/1142E/10734,deeper game recovery,arbitrary suspension/IRQ,fidelity and full source rebuilding remain incomplete.'
    g['next_actions']=['Execute relocated native helper code and integrate three recovered helpers into geometry without new global/task state; measure stack and preserve real110D4calls.','Run final-address/fallback/nesting and fresh candidate/control comparisons before changing the preview.','Improve game/Advertising model source fidelity and accepted training quality;complete current portable migration.']
    save(gp,g)
    print(out,'3recovered algorithms;772component+256connected;native integration pending',flush=True)
if __name__=='__main__':main()
