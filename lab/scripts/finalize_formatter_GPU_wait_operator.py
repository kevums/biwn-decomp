"""Verify current game, advertising handoff and actual local inference records."""
import hashlib,json,shlex,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import native_format_evidence
from biwn_status_editor import completion_flags
from ask_biwn_current_status import verified_scope_note
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def main():
 pp=ROOT/'verification/native-formatter-GPU-wait-publication-current.json';publication=read(pp)
 current=native_format_evidence.load(ROOT);assert current.pop('proof_sha256')==sha(pp)and current==publication['current_status']
 rp=ROOT/'verification/current-biwn-status-reader-current.json';reader=read(rp);ro=Path(reader['directory']);reviewp=ROOT/'verification/native-formatter-wait-status-reader-reviewed-current.json';review=read(reviewp)
 observed=dict(reader['calls'][0]['result']);assert observed.pop('proof_sha256')==sha(pp)and observed==current
 assert not reader['answer_review_flags']and not completion_flags(reader['Editor']['structured_fields'])and len(reader['calls'])==1
 assert len(reader['answer'].split())==85 and review['protocol_sha256']==sha(ro/'protocol.json')
 old=read(ROOT/'runs/current-biwn-status-20261018T225116.988062Z/protocol.json');assert len(completion_flags(old['Editor']['structured_fields']))==4
 footer=verified_scope_note(observed);assert footer==review['source_backed_scope_footer']
 ap=ROOT/'verification/advertising-seminar-evaluation-publication-current.json';advertising=read(ap)
 for p,h in advertising['dependencies_sha256'].items():assert sha(p)==h,p
 assert advertising['new_training']is False and advertising['corrected_example_words']==292
 runtime=Path('/Users/kevin/.lmstudio/local-ai-lab/native_format_evidence.py');assert runtime.read_bytes()==(ROOT/'native_format_evidence.py').read_bytes()
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-formatter-GPU-wait-operator'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 ps=subprocess.check_output(['ps','-axo','pid,etime,command'],text=True);live=[]
 for line in ps.splitlines()[1:]:
  parts=line.strip().split(None,2)
  if len(parts)!=3:continue
  try:args=shlex.split(parts[2])
  except ValueError:continue
  scripts=[Path(a).name for a in args if a.endswith('.py')]
  if any(n in scripts for n in ['run_biwn_interactive.py','run_biwn_native_fast_core_wait_entry_deck_pair.py','run_format_fast_core_wait_long_route.py','ask_biwn_current_status.py']):live.append(dict(pid=int(parts[0]),elapsed=parts[1],command=parts[2],scripts=scripts))
 assert all(row['scripts']==['run_biwn_interactive.py']for row in live),live
 model=subprocess.check_output(['/Users/kevin/.lmstudio/bin/lms','ps'],text=True);assert 'advertising-scholar'in model and 'IDLE'in model
 (out/'processes.txt').write_text(ps);(out/'model-state.txt').write_text(model)
 for name in ['CURRENT LOCAL INFERENCE.txt','WATCH LOCAL AGENTS.txt']:
  path=ROOT/name;text=path.read_text();text=text.replace('A fresh Reader generation is being checked separately; this is SDK inference,not nativeChat.','Latest Reader+Editor retest:85words,24.66seconds,1actual configuredMCPcall. Complete sentences; a separate verifiedscopefooter supplies fullsource/physicalconsole/training limits. SDK inference,not nativeChat.')
  text=text.replace('runs/current-biwn-status-20261018T225116.988062Z.','runs/current-biwn-status-20261018T225301.243905Z; the earlier225116Editoroutput was rejected as clipped.')
  path.write_text(text)
 report=ROOT/'reports/local-inference-GPU-wait-handoff.txt'
 report.write_text(f"""LOCAL AI LAB: GAME REPAIR AND LOCAL INFERENCE HANDOFF
{now.isoformat()}

The experimental BIWN build now includes a 26-byte GPU completion-wait repair in a 14,690-byte resident payload. The original 14,664 resident bytes remain unchanged. The first corrupt blit reproduces the captured full 2 MB RAM result exactly in both retained blitter engines.

The repair passes 256 native mailbox fixtures, 96 startup cases and 5,151 installed keypad ABI cases. Both fresh 2,600-frame Deck lanes finish without the earlier invalid CPU address or formatter stack violations. The repaired raw-disc route completes the merchant visit and outdoor return in 24,975 frames. Positions and video still differ between lanes; these results do not establish frame equivalence. Earlier failed artifacts are preserved. The playable preview remains unchanged.

Detailed game report:
{publication['report']}

The local Reader and Editor produced an 85-word summary in 24.66 seconds using one actual configured MCP call. Their exact prompts, tool results, overlong draft, edited response and coordinator review are saved here:
{ro}

Unedited local model answer:
{reader['answer']}

{footer}
The scope note above is deterministic evidence, separate from the model's answer. The reported 24,975 frames cover the complete merchant and outdoor route, rather than the first arrival at the merchant.

The earlier Editor response was rejected because hard character limits cut all four fields mid-sentence. Those limits have been removed, and the new completion check rejects the four recorded failures. The two Diagnostic Analyst answers were also rejected as complete advice: one confused opcode values with elapsed cycles, and the other proposed changing a command register as if it held pixel data. The coordinator wrote the repair from the traces. Compiler and emulator processes are tools, not additional AI agents. This remains a guided workflow check, not proof of general local coding quality.

For advertising, the existing 27B, 6-bit model is loaded and idle with a 32K context. Research Desk and Teaching Demo remain available. The latest 292-word teaching example is explicitly coordinator-corrected:
{ROOT/'reports/advertising-source-seminar-example.txt'}

Advertising source and evaluation publication:
{ap}

No new weight training or adapter promotion occurred in this round. This round used LM Studio SDK/MCP inference; native Chat generation was not verified. The existing interactive preview process was left in place. Remaining work includes full game and platform reconstruction, broader synchronization and scene testing, physical-console boot, audio listening, demonstrated training gains and the future 256 GB hardware test.
""")
 paths=[Path(__file__),pp,ap,rp,reviewp,ro/'protocol.json',ro/'answer.txt',ro/'prompts-and-responses.txt',ro/'Editor/request.json',ro/'Editor/response.json',ro/'Editor/raw-response.json',ro/'coordinator-review.json',ROOT/'native_format_evidence.py',ROOT/'biwn_status_editor.py',ROOT/'scripts/ask_biwn_current_status.py',ROOT/'Ask BIWN Candidate Status.command',ROOT/'Advertising Research Desk.command',ROOT/'Advertising Teaching Demo.command',ROOT/'CURRENT DECOMPILATION.txt',ROOT/'CURRENT LOCAL INFERENCE.txt',ROOT/'WATCH LOCAL AGENTS.txt',report,out/'processes.txt',out/'model-state.txt']
 deps={str(p):sha(p)for p in paths};allpaths=set(publication['status_dependencies_sha256'])|set(advertising['dependencies_sha256'])|set(deps)
 state=dict(status='terminal_formatter_GPU_wait_game_and_operator_handoff_verified',recorded_at=now.isoformat(),directory=str(out),game_publication=str(pp),game_publication_sha256=sha(pp),advertising_publication=str(ap),advertising_publication_sha256=sha(ap),game_evidence_files=len(publication['status_dependencies_sha256']),all_checked_files=len(allpaths),integrity_mismatches=0,current_MCP_result_matches_publication=True,local_Reader_Editor_seconds=reader['seconds'],local_summary_words=85,actual_MCP_calls=1,coordinator_review='Qualifiedconcisecomplete-sentence summary; separatelylabelledverifiedscopefooterprovidesomittedreadinesslimits.',known_clipped_fields_now_rejected=4,old_clipped_output_preserved=True,footer_is_model_output=False,native_Chat_verified=False,new_training=False,default_promoted=False,goal_complete=False,runtime_frontend=str(runtime),runtime_frontend_sha256=sha(runtime),dependencies_sha256=deps,live_processes=live,model_idle=True,report=str(report))
 save(out/'verification.json',state);save(ROOT/'verification/native-formatter-GPU-wait-operator-current.json',state)
 ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);ledger.update(recorded_at=now.isoformat(),latest_GPU_wait_operator=str(ROOT/'verification/native-formatter-GPU-wait-operator-current.json'),latest_local_inference=str(ro/'protocol.json'),latest_finite_jobs_running=False,live_processes=live,live_processes_scope='Actualpsshows onlyexistinginteractivepreviewamong selectedgame/localinferencejobs; alladdedjobscompleted.',model_backend_observation=model.strip(),goal_complete=False)
 ledger['next_actions']=['Integrate source-backed pending-command wait behavior into broader recoveredC/runtime workflows and verify other scenes/IRQinterleavings.','Keep experimentalconsoleCDI andsourceCpreview scopesdistinct; verify nativeChatwhenUIavailable.','Develop representative training-source evaluations; keep validationpaperandfrozen testsoutofSFT/index.','Complete remaininggame/platformrestoration,physicalconsole/audioverification andfuture256GBhardwaretest.'];save(ledgerp,ledger)
 print(json.dumps({k:state[k]for k in ['status','all_checked_files','integrity_mismatches','local_Reader_Editor_seconds','local_summary_words','actual_MCP_calls','known_clipped_fields_now_rejected','new_training','goal_complete','report']},indent=2))
if __name__=='__main__':main()
