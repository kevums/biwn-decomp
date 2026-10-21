"""Human entry points and actual local-role provenance; no new inference/tests."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/formatter-operator-followup'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 pp=ROOT/'verification/native-formatter-experiment-publication-current.json';pub=read(pp);rp=ROOT/'verification/native-formatter-status-reader-reviewed-current.json';review=read(rp);protocol=Path(review['directory'])/'protocol.json';reader=read(protocol)
 ap=ROOT/'verification/advertising-seminar-evaluation-publication-current.json';ad=read(ap)
 assert review['status']=='accepted_raw_formatter_experiment_status_with_failure_limits'and review['source_publication_sha256']==sha(pp)
 assert not reader['answer_review_flags']and reader['calls'][0]['result']['proof_sha256']==sha(pp)and len(reader['calls'])==1
 assert pub['runtime_regression_unresolved']and not pub['default_promoted']and not ad['new_training']and ad['corrected_example_words']==292
 runtime=Path('/Users/kevin/.lmstudio/local-ai-lab/native_format_evidence.py');assert sha(runtime)==sha(ROOT/'native_format_evidence.py')
 for table in [pub['status_dependencies_sha256'],ad['dependencies_sha256']]:
  for p,h in table.items():assert sha(p)==h,p
 summary=ROOT/'reports/local-lab-formatter-and-teaching-progress.txt'
 summary.write_text(f'''Local AI Lab progress — {now.isoformat()}

BIWN restoration
All seven scoped formatter/arithmetic entries now have native C implementations. Combined tests cover323original instruction addresses in that subsystem. The14,664byte optimized image passed1,950full formatter CPU/public-memory/access cases,the separate helper matrices,and all19installation/component/resource gates. This is not a full game decompilation.
The candidate completed the merchant/floor0/outdoor route in24,975frames; its parent took24,974. The candidate's short Deck run completed672wrapper calls with no observed task-stack violation. However,the same-layout Deck control corrupted state,first oddCPU PC recorded atframe1,430. The slower formatter prototype also failed atframe8,546. The runtime/control cause is still unresolved,so this remains experimental and no default preview was changed.
Inlining reduces emulatedcycles64percent in one offline captured call,still9.7times original assembly cost. This does not measure whole-gameFPS or physical-console speed. The full source console rebuild,IRQ/content reliability and physicalboot remain unfinished.
Detailed game report: {pub['report']}

Easy local inference
Desktop > Local AI Lab > Ask BIWN Candidate Status.command
The actual local Reader used one configuredMCPlookup and returned171words in24.81seconds. Its answer explicitly retained the failed control and scope limits. It was accepted unchanged for this current-status example. This was anSDKrun,not a new generation in nativeLMStudioChat.
Exact Reader prompts/tool data/response: {Path(review['directory'])/'prompts-and-responses.txt'}
Advertising Research Desk.command remains the ordinary research/education entry point. The daily base model islocal27B6bit with32Kcontext; loaders can reload it after its idleTTL. Earlier adapters with failed quality gates remain unpromoted.

Advertising teaching output test
The local Educator,Source Reviewer and two revision strategies processed a complete21page validation paper with22,840to25,057input tokens and no source/task truncation. They used the same weights in sequential contexts,not independent models. All four generations took249.67seconds total; the separate initial model load was observed at5.92seconds.
The first463word draft failed a320word cap. The Reviewer caught the cap but missed source-precision issues. Character-limited revision passed a word count while ending mid-clause and was rejected. A complete-prose guided revision produced281words and fixed the larger issues. A separate292word coordinator-corrected example supplies the final schedule and precision edits; it is explicitly not raw local-model output.
Corrected teaching example: {ad['corrected_example']}
Full prompts,failure analysis and source boundaries: {ad['report']}
This is guided validation development,not new weight training or broad teaching reliability. The validation paper remains outside both retrieval indexes and SFTtraining; frozen test papers were not generated.

Who is doing what
Codex coordinator: C reconstruction,compiler/CPU/device checks,disc building,runtime diagnosis and source grading.
Local Scope Reviewer: one receipt callback,seven guided claim decisions; advisory only.
Local Reader: current game status via actualMCP. Optional same-weight Editor is configured for overlong summaries,but was not needed in the171word run.
Local Educator -> Source Reviewer -> Reviser: supplied-full-paper lesson experiment. All prompts/raw responses are saved in the linked reports.
Compilers,retainedCPU/Unicorn oracles,renderers and game runners are deterministic programs,not agents. No new model weights or preview build were promoted. No new nativeChat UI verification occurred.

Next work remains the runtime/control corruption,the rest of the game/platform source,representative advertising/game training gains,and verification on the future256GB system and physicalJaguarCD.
''')
 # Human status files are mutable entry points, kept outside immutable game core.
 note=f'''LATEST FORMATTER / LOCAL-INFERENCE / TEACHING RESULTS — {now.isoformat()}
Game: seven scoped formatter entries compiled;14,664byte image,323subsystem addresses,1,950formatter cases and19component gates. Candidate merchant/outdoor route completes, but a same-layout Deckcontrol corrupts state atfirst recorded oddPCframe1,430. Runtimecause unresolved; experimental only,defaultpreview unchanged. Full game/physicalconsole rebuild remains unfinished.
Local Reader:171words in24.81seconds,one actualMCPcall,explicit failure limits retained. Local advertising lesson test:463word failure -> rejected clipped211word revision -> guided281word complete prose; separate292word coordinator-corrected example. Four generation calls total249.67seconds; no new training or weight promotion.
Readable progress: {summary}
Game report: {pub['report']}
Advertising report: {ad['report']}
Corrected teaching example: {ad['corrected_example']}

Earlier records follow.

'''
 docs=[ROOT/'CURRENT DECOMPILATION.txt',ROOT/'CURRENT LOCAL INFERENCE.txt',ROOT/'WATCH LOCAL AGENTS.txt',ROOT/'projects/black-ice-white-noise/restoration/native-m68k/README.txt']
 for p in docs:(out/p.name).write_bytes(p.read_bytes());p.write_text(note+p.read_text())
 files=[Path(__file__),pp,rp,protocol,ap,summary,ROOT/'native_format_evidence.py',ROOT/'biwn_status_editor.py',ROOT/'scripts/ask_biwn_current_status.py',ROOT/'Ask BIWN Candidate Status.command',ROOT/'Advertising Research Desk.command',*docs]
 files.extend(p for p in Path(review['directory']).rglob('*')if p.is_file())
 state=dict(status='terminal_formatter_and_teaching_operator_followup_verified',directory=str(out),game_publication=str(pp),game_publication_sha256=sha(pp),advertising_publication=str(ap),advertising_publication_sha256=sha(ap),reader_protocol=str(protocol),reader_seconds=reader['seconds'],reader_words=len(reader['answer'].split()),reader_actual_MCP_calls=1,reader_failure_scope_accepted=True,editor_used=bool(reader.get('Editor')),readable_report=str(summary),runtime_regression_unresolved=True,coordinator_corrected_teaching_example=True,native_Chat_verified=False,dependencies_sha256={str(p):sha(p)for p in files},runtime_frontend=str(runtime),runtime_frontend_sha256=sha(runtime),new_training=False,default_promoted=False,goal_complete=False)
 save(out/'followup.json',state);save(ROOT/'verification/formatter-operator-followup-current.json',state)
 lp=ROOT/'verification/goal-continuation-current.json';ledger=read(lp);ledger.update(latest_formatter_operator_followup=str(ROOT/'verification/formatter-operator-followup-current.json'),latest_advertising_source_seminar=str(ap),latest_current_status_launcher_verified=True,current_goal_turn_progress='Inline-specialized seven-entry formatter passes1950core/1196number/3592math andpad/string matrices,all323source addresses/19gates. Candidate24975frame route completes;controlcorrupts1430,rootcauseopen. Reader171words24.81seconds1MCP. Full21page teaching baseline463word failure,clipped211revision rejected,guided281revision qualified;292wordcoordinator-correctedexample and allsource/role logs saved. No newtraining/defaultpromotion.',latest_finite_jobs_running=False,latest_finite_job_status='All game and local inference/evaluation jobs terminal; existing user preview is separate.',next_actions=['Capture the first world-state write/invalid control transition; distinguish CPU ABI,dead-stack/device and IRQ timing effects without hiding the regression.','Continue remaining source/platform reconstruction and original-console boot validation.','Build representative source-grounded training tasks from reserved train papers using the observed review/conciseness failures; keep validation/test artifacts out of training.','Verify new workflows in nativeLMStudioChat when UI is available; current SDK/one-click status is verified.','Verify future256GB deployment and physicalJaguarCD/audio; neither is achieved.'],goal_complete=False,new_training=False);save(lp,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),action='formatter and full-source teaching publication/operator handoff',game_publication=str(pp),advertising_publication=str(ap),Reader_seconds=reader['seconds'],Reader_words=len(reader['answer'].split()),actual_MCP_calls=1,roles_same_weights=True,independent_review=False,new_training=False,native_Chat_verified=False,goal_complete=False))+'\n')
 print(json.dumps(dict(status=state['status'],reader_seconds=state['reader_seconds'],reader_words=state['reader_words'],runtime_regression_unresolved=True,report=str(summary),goal_complete=False)))
if __name__=='__main__':main()
