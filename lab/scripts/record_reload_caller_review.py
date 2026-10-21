"""Record separate caller proof, unreached-path diagnostic and local error."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');proof=read(ROOT/'verification/GPU-reload-real-BIOS-checks.json');raw=Path(proof['directory'])
    assert proof['cases']==12 and proof['source_instruction_coverage']==[32,32] and not proof['reached_game_reload_caller']
    assert read(raw/'status.json')['status']=='terminal_pass' and not cp['actual_BIOS3000_reload_game_caller_reached']
    diag=ROOT/'verification/BIWN-BIOS-reload-movie-transport-music-cold-entry-timer-startup-loading-movie-world/20261014T232136.770098Z'
    d=read(diag/'status.json');assert d['status']=='terminal_interrupted_scope_probe' and d['case0_complete_snapshot_match']
    a=read(diag/'case-0-native.json');b=read(diag/'case-0-C.json');assert a==b and not a['summary']['actual_reload_bios_calls']
    local=Path(read(ROOT/'verification/easy-reload-caller-scope-pointer.json')['directory']);run=read(local/'protocol.json');item=run['results'][0]
    assert run['status']=='completed_pending_coordinator_review' and not item['quality_flags'] and item['words']<130
    assert all(x['stats']['stopReason']=='eosFound'for x in item['prediction_stats'])
    now=datetime.now(timezone.utc);out=ROOT/'verification/reload-caller-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    findings=[
        'Separate sourceE00A caller executes actual resident BIOS3000. Twelve original/C user/supervisor inputs cover all32selectedCPUinstructions and match CPU/privateRAM/peripherals/GPU/controller baseline+9byte timing extension. GPU instructions do not execute. Saved postmovie RAM/logicalGPU plus CPU/device/controller/pipeline-tail inputs are explicit initial fixtures.',
        'Experimental connected reload integration recorded zero reload calls. Case0 original/C complete snapshots match; coordinator interrupted case1 rather than promoting an unreached path. No natural game reload adoption is established.',
        'Local119word/32.69second SDK answer correctly distinguishes separate caller proof from the connected movie/world path. It then recommends making the postmovie path callE00A. That recommendation is unsupported: checked source mappings identify initial entry4064->E00A, and do not establish that movie exit should reload throughE00A. Do not modify game behavior to satisfy an invented expected call.',
        'The local claim that reload code itself is correct is accepted only within12tested inputs/all32selectedCPUinstructions, not all hardware states, firmware behavior or complete boot. Local answer did not establish easy native Chat interaction or a playable rebuilt game.',
        'Two evidence publication checks failed before final success: reload metadata initially added after checkpoint save; then installed evidence copy stale after corrected root publication. Coordinator moved updates before saves and reinstalled before fresh MCP check. Exact model response follows only the final passing MCP state.',
        'Coordinator authored the integration experiment, source caller test and evidence corrections. Local GameAssistant supplied an explanation with one unsupported recommendation. No new local-model code authorship, accepted body counts, weight training/default changes or independent model verification.'
    ]
    gold='The connected test now moves asset and movie bytes through the BIOS, controller and GPU, then resumes the checked world cycles. It does not reach a later E00A GPU reload. Separately, we invoked E00A from a supplied saved fixture and matched the original in 12 CPU input profiles, including its actual BIOS3000 call. This proves that bounded caller test; it does not establish when another game path should invoke it. We should trace legitimate source callers and continue firmware/timing/input/task work. The local model can explain saved evidence and produce previews through configured tools; current native Chat interaction and a playable rebuilt game remain unverified.'
    (out/'coordinator-corrected-answer.txt').write_text(gold+'\n')
    files=[Path(__file__),ROOT/'scripts/check_biwn_GPU_reload_real_BIOS.py',ROOT/'scripts/biwn_bios_reload_runtime.py',ROOT/'scripts/check_biwn_bios_reload_scheduled_startup.py',ROOT/'scripts/check_biwn_continuous_loading_movie_world.py',ROOT/'scripts/prepare_movie_transport_evidence.py',ROOT/'scripts/check_movie_transport_mcp.py',ROOT/'scripts/test_reload_caller_scope.py',ROOT/'chat_tools.py',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/movie-transport-MCP-check.json',ROOT/'verification/GPU-reload-real-BIOS-checks.json',ROOT/'verification/BIOS-reload-run-console.txt',raw/'report.json',raw/'cases.json',raw/'compiler.txt',raw/'status.json',raw/'libGPU-reload.dylib',diag/'status.json',local/'protocol.json',local/'prompts-and-responses.txt']
    manifest=[]
    for n,p in enumerate(files):
        dest=out/f'{n:02d}-{p.name}';shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    report=dict(status='separate_reload_caller_verified_local_explanation_partly_correct_unsupported_next_step_rejected',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],source_report=str(raw),unreached_path_diagnostic=str(diag),local_output=str(local),interface=run['interface'],model=run['model'],words=item['words'],seconds=item['seconds'],semantic_review=findings,native_Chat_verified=False,whole_goal_complete=False,new_training=False,model_defaults_changed=False,local_source_authorship=False,manifest=manifest)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+'\n'.join(findings)+'\n\nLOCAL GAME ASSISTANT — EXACT SYSTEM / USER / TOOL RESULTS / RESPONSE\n'+(local/'prompts-and-responses.txt').read_text()+'\n\nCOORDINATOR CORRECTED ANSWER — NOT LOCAL OUTPUT\n'+gold+'\n')
    feedback=ROOT/'training/feedback/game-reload-caller-20261014.jsonl'
    feedback.write_text(json.dumps(dict(role='diagnostic_feedback_candidate',source_group='BIWN_same_connected_checkpoint_not_independent_heldout',question=run['questions'][0]['user'],original_answer=item['answer'],coordinator_corrected_answer=gold,failure='Unsupported recommendation to introduceE00A into postmovie source flow',used_in_weight_training=False),ensure_ascii=False)+'\n')
    history=out/'prior-daily-pages';history.mkdir()
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,history/name)
    p=ROOT/'START HERE.txt';s=p.read_text();s=s.replace(s.splitlines()[1],'Updated '+now.isoformat());s=s.replace('Latest local Game Assistant answer: 97 words/15.24 seconds; core scope accepted.',f'Latest local reload explanation: {item["words"]} words/{item["seconds"]:.2f} seconds; scope facts correct, unsupported next-step recommendation rejected. Prior transport answer: 97 words/15.24 seconds, core scope accepted.')
    s=s.replace('Nominal pacing/clocks, remaining firmware adapters, full boot and playability are unfinished.', 'Nominal pacing/clocks, full boot and playability are unfinished. Separate E00A/BIOS3000 caller passes 12 cases; the tested game path does not reach a later reload.')
    previous=Path(read(ROOT/'verification/movie-transport-local-review.json')['directory']);s=s.replace(str(previous/'who-prompts-and-responses.txt'),str(out/'who-prompts-and-responses.txt')).replace(str(previous/'review.json'),str(out/'review.json')).replace(str(previous/'prior-daily-pages'),str(history));p.write_text(s)
    p=ROOT/'CURRENT LOCAL INFERENCE.txt';s=p.read_text();s=s.replace(s.splitlines()[1],'Updated '+now.isoformat());start=s.index('Latest ');end=s.index('\n\nEXACT WHO',start)
    s=s[:start]+f'Latest reload explanation: {item["words"]} words/{item["seconds"]:.2f}s, one evidence lookup. Correct separate-versus-connected scope; unsupported recommendation to force a postmovie reload rejected. Coordinator correction saved separately. Earlier transport answer: 97 words/15.24s, core scope accepted. These are SDK tests, not broad reliability or native Chat verification.'+s[end:];s=s.replace(str(previous/'who-prompts-and-responses.txt'),str(out/'who-prompts-and-responses.txt')).replace(str(previous/'review.json'),str(out/'review.json')).replace(str(previous/'prior-daily-pages'),str(history));p.write_text(s)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(source_audit=cp['audit'],local_audit=str(out),last_turn_classification='progress',local_roles_this_turn='Coordinator verified separate actual E00A/BIOS3000 caller and found connected reload path unreached. Local GameAssistant explained scope but recommended unsupported game behavior; correction saved. No new weights/defaults.')
    n['next_source_work'][0]='Actual asset/movie BIOS-controller-GPU transport passes two connected profiles. Complete firmware relocation/stage loading/boot and global scheduling; trace legitimate firmware/reload callers from original source. Separate host-invoked E00A/3000 passes12cases/all32instructions but no later game reload call is reached. Do not force a postmovie call. Other calls/movies and buffer/end semantics remain unverified.';save(p,n)
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        dest=out/('current-'+name);shutil.copy2(ROOT/name,dest);manifest.append(dict(source=str(ROOT/name),snapshot=str(dest),sha256=sha(dest)))
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in manifest)
    assert (ROOT/'chat_tools.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/chat_tools.py').read_bytes()
    save(out/'review.json',report);save(ROOT/'verification/reload-caller-local-review.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),words=item['words'],seconds=item['seconds'])))
if __name__=='__main__':main()
