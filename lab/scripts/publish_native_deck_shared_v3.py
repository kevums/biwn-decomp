"""Seal the fourth native Deck caller and bounded local C-glue contribution."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=V/'native-Deck-shared-delivery-v3'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 gp=V/'native-Deck-shared-reviewed-v3-current.json';rp=V/'Deck-status-live-v15-reviewed-current.json';cp=V/'native-Deck-context-v8-current.json';ap=V/'local-native-face-bridge-accepted-v1-current.json'
 game,reader,context,accepted=[read(p)for p in [gp,rp,cp,ap]]
 assert game['status']=='terminal_fresh_four_native_Deck_callers_reviewed'and reader['source_reviewed']and accepted['accepted_bridge_fragments']==1 and context['new_predictions']==0
 paths=[Path(__file__),gp,rp,cp,ap,ROOT/'scripts/author_native_face_bridge_local_v1.py',ROOT/'native_deck_source_context_v8.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'scripts/run_deck_status_live_v15.py',ROOT/'Live Local BIWN Briefing.command']
 for proof in [game,reader,context]:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p;paths.append(Path(p))
 model=json.loads(subprocess.run([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd='/',capture_output=True,text=True,check=True,timeout=10).stdout);assert len(model)==1 and model[0]['status']=='idle'and model[0]['queued']==0
 author=read(V/'local-native-face-bridge-author-v1-current.json');folders=[Path(author['directory']),ROOT/'runs/Deck-status-live-20261020T074108.828990Z',ROOT/'runs/Deck-status-live-20261020T074156.301674Z',ROOT/'runs/Deck-status-live-20261020T074317.912277Z',Path(reader['directory'])];assert len(set(folders))==5
 transcript=[];predictions=0
 for i,folder in enumerate(folders):
  g=read(folder/'protocol.json');predictions+=g.get('actual_predictions',g.get('new_predictions',0));shutil.copytree(folder,out/'model-runs'/folder.name);transcript.extend(['='*72,str(folder),(folder/'prompts-and-responses.txt').read_text()]);paths.extend(p for p in folder.rglob('*')if p.is_file())
 assert predictions==6
 (out/'prompts-and-responses.txt').write_text('\n\n'.join(transcript)+'\n')
 report=ROOT/'reports/Four Native Deck Callers Review.txt'
 report.write_text(f'''FOUR NATIVE DECK CALLERS — {now.isoformat()}

Face contact (1186A) now runs as compiled 68000 C alongside scan (11828), input (11B4C) and coordinate updates (11D1A) on a separate experimental disc. Two of the six recovered Deck callers remain hosted-only: geometry collection (11AD4) and the outer task (11E6C). These six routines form a subsystem, not the entire game.

The existing face algorithm was recovered by the coordinator earlier and remains unchanged. The local Author supplied only the appended six-line C service/body bridge; that fragment was accepted unchanged after external gates. Codex wrote the assembly, fallback and shared-slot integration. Input and face share the same frame and C stack. If either is active, a nested attempt uses original code without modifying the suspended frame. The Deck arena remains 101 × 1,024 bytes.

Fresh comparison: the candidate completed 19 calls and returns for EACH of the four native callers. The control restored only the six-byte face entry and completed 19 original face calls, while scan/input/coordinate remained native. Both preserved 19 suspended scan parents. Candidate/control ran 25,010/25,011 frames, with 400/401 input frames; extra released input allowed watched calls to return. The recorded CPU/GPU/DSP/video/navigation fields match for 24,610 pre-input frames, excluding declared RAM/stage hashes. Final images match. All observed errors, pending calls and stack violations are zero. All 101 Deck slots retain seven fences, all 102 GPU slots retain their fences, and immutable code matches.

The same 4,992 component-case family passed at prototype and final addresses. The 128 connected scenarios exercised 800 input, 485 face and 800 coordinate calls, with 2,085 suspended-parent checks per matrix. Another 128-case family tested actual helper JSRs in both alias directions across both CPU banks and all condition codes; it was repeated at final addresses. All 1,024 fallback cases compare full CPU and all RAM without normalization. Six startup, 192 heap-initialization and 36 allocation-boundary cases pass. The live region checker rejects 57 fault records at 56 distinct addresses; the aliased input/face frame accounts for the repeated address.

Native code is 62,036 bytes; total reservation is 191,744 bytes and initial heap is 206,144 bytes. The explicit 13-frame asset restoration still changes original 16-frame behavior. Equal counts and images do not establish cycle identity. Original helpers, original fallback bodies and emulator/HLE dependencies remain; this is not a complete source rebuild or physical-console validation.

LOCAL MODEL WORK
Six actual predictions used the loaded {model[0]['identifier']} weights: Author, Reviewer and four status drafts. The Author bridge passed unchanged. The Reviewer was truncated and self-contradictory, so its review was rejected. Status drafts needed correction for hosted-only wording, length and an instruction echo. All raw prompts/responses and source corrections are retained. The final {reader['words']}-word one-click briefing passed source and format review in {reader['seconds']} seconds. Same weights are not independent verification. No optimizer updates or new model-authored game algorithm occurred.

The native Chat evidence helper now routes four installed/two hosted-only facts and still passes its Advertising grammar-workflow check. This check performs no inference and does not demonstrate current native Chat rendering. The Desktop BIWN Test Preview app still uses the earlier three-caller image; its new GUI/live-key testing remains unverified. Both earlier preview apps remain available.

Advertising research/teaching quality and accepted training remain unfinished. Broader game recovery, arbitrary suspension/reentry/IRQ, timing/audio/physical fidelity, migration and future-hardware acceptance remain unfinished. The full goal remains active.

EXPERIMENTAL DISC
{game['disc']}

EXACT LOCAL PROMPTS AND RAW RESPONSES
{out/'prompts-and-responses.txt'}

DETAILED GAME PROOF
{gp}
''')
 receipt=dict(status='terminal_four_caller_native_integration_delivered',recorded_at=now.isoformat(),directory=str(out),report=str(report),game_review=str(gp),game_review_sha256=sha(gp),installed_Deck_callers=game['installed_recovered_Deck_entries'],hosted_only_Deck_callers=game['remaining_hosted_only_Deck_entries'],ordinary_returns_each=19,control_original_face_calls=19,accepted_local_bridge_C_fragments=1,accepted_new_local_algorithm_bodies=0,new_native_caller_integrations=1,newly_recovered_algorithms=0,actual_local_predictions=6,Author_predictions=1,Reviewer_predictions=1,Reader_predictions=4,Reviewer_accepted=False,optimizer_updates=0,native_Chat_predictions=0,Reader_seconds=reader['seconds'],Reader_words=reader['words'],Desktop_preview_updated=False,model_idle_receipt=model,prompts=str(out/'prompts-and-responses.txt'),source_bindings=str(out/'source-bindings.json'),whole_game_complete=False,physical_console_verified=False,limits='Two recovered Deck callers remain hosted-only. Full-game source rebuilding, arbitrary suspension/reentry/IRQ, timing/audio/physical fidelity, current-image GUI/live-key testing, broad game/Advertising training quality and migration/future hardware remain unfinished.')
 save(out/'delivery.json',receipt);save(V/'native-Deck-shared-delivery-v3-current.json',receipt)
 config=ROOT/'config/current-model-work-sources.json';sources=read(config);entry=['native-Deck-shared-delivery-v3-current.json','Four native Deck callers: actual local C bridge Author, rejected Reviewer and all current-status drafts']
 if not any(x[0]==entry[0]for x in sources):sources.append(entry)
 config.write_text(json.dumps(sources,indent=2)+'\n');p=subprocess.run([str(Path.home()/'.lmstudio/local-ai-lab/.venv/bin/python3.12'),str(ROOT/'scripts/show_current_model_work_v4.py'),'--no-open'],cwd='/',capture_output=True,text=True,check=True);(out/'model-index-refresh.txt').write_text(p.stdout+p.stderr)
 paths.extend([config,V/'current-model-work-index-v4-current.json',report,out/'prompts-and-responses.txt']);bindings={};frozen=[]
 for i,p in enumerate(sorted(set(paths),key=str)):
  h=sha(p);bindings[str(p)]=h
  if p.stat().st_size<=8*1024*1024 and p.suffix not in ['.bin','.cdi','.dylib','.elf']:
   dest=out/'frozen'/(str(i).zfill(3)+'-'+p.name);dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest);frozen.append(dict(original=str(p),snapshot=str(dest),sha256=h))
 save(out/'source-bindings.json',bindings);save(out/'frozen-small-artifacts.json',frozen)
 gp0=V/'goal-continuation-current.json';shutil.copy2(gp0,out/'previous-goal-continuation.json');goal=read(gp0)
 goal.update(status='active_four_native_Deck_callers_reviewed_two_hosted_remaining',recorded_at=now.isoformat(),directory=str(out),previous_goal_turn_classification='progress: natural original-face route and separate headless-tested app/current briefing delivered',current_turn_classification='progress',full_objective_complete=False,blocked=False,ongoing_finite_workers=[],publication=str(V/'native-Deck-shared-delivery-v3-current.json'),review=str(report),latest_usability_report=str(report),resident_code_bytes=62036,total_reservation_bytes=191744,initial_heap_bytes=206144,candidate_control_frames=[25010,25011],current_turn_predictions=6,current_turn_optimizer_updates=0,current_turn_new_game_routines=0,current_turn_new_native_caller_integrations=1,current_turn_accepted_local_bridge_fragments=1,current_native_Deck_installed=game['installed_recovered_Deck_entries'],current_Deck_hosted_only=game['remaining_hosted_only_Deck_entries'],live_GPU_returns=game['native_GPU_returns'],natural_face_contact_body_native=True,natural_face_contacts_each_lane=19,native_face_parent_checks=19,saved_prompt_or_transcript_records=read(V/'current-model-work-index-v4-current.json')['saved_prompt_or_transcript_records'],training_scope_this_turn='6 actual same-weight predictions;0 optimizer updates. One unchanged six-line bridge C fragment accepted after external gates; no new model-authored game algorithm. Reviewer rejected; status drafts retained.',one_click_launcher=str(ROOT/'Live Local BIWN Briefing.command'),limits=receipt['limits'])
 goal['remaining_requirements']['game']='Four native Deck callers now pass final-address and fresh original-face-control gates; two remain hosted-only. Original helpers/fallbacks, arbitrary suspension/reentry/IRQ, timing/audio/physical fidelity and complete same-console source rebuilding remain incomplete.'
 goal['remaining_requirements']['local_frontend']='V8 current four/two evidence routing and reviewed V15 oneclick briefing pass. Native Chat display and latest-image GUI/live keys remain unverified; separate Test Preview still uses the prior three-caller image.'
 goal['next_actions']=['Advance Advertising research/teaching training with disjoint source-backed evaluation families; preserve previously rejected adapters until quality evidence improves.','Compile geometry11AD4 and outer task11E6C while preserving all four current native callers and suspended contexts.','Freeze historical UI evidence independently before updating the separate Test Preview to the four-caller image; verify its GUI/live keys when observation is available.','Continue complete game recovery, natural interruption/timing/audio/physical fidelity and migration/future-hardware acceptance.'];save(gp0,goal);print(out,flush=True)
if __name__=='__main__':main()
