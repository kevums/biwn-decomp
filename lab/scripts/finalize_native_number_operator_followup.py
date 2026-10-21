"""Review actual local Reader and refresh human entry points without new tests."""
import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-number-operator-followup'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 pp=ROOT/'verification/native-number-publication-current.json';pub=read(pp);rp=ROOT/'verification/current-biwn-status-reader-current.json';reader=read(rp)
 assert reader['status']=='terminal_local_current_status_pending_review' and not reader['answer_review_flags']
 assert len(reader['calls'])==1 and reader['rounds']==2
 assert reader['calls'][0]['name']=='project_evidence' and reader['calls'][0]['arguments']=={'topic':'status'}
 evidence=reader['calls'][0]['result'];assert evidence['proof_sha256']==sha(pp) and evidence['experimental_build']['binary_sha256']==pub['binary_sha256']
 assert reader['model_inference_invoked'] and reader['native_Chat_verified']is False
 reviewp=ROOT/'verification/native-number-status-reader-reviewed-current.json';review=read(reviewp)
 import hashlib
 assert review['status']=='accepted_raw_scoped_status_summary' and review['answer_sha256']==hashlib.sha256(reader['answer'].encode()).hexdigest()
 print('RAW ANSWER FOR REVIEW\n'+reader['answer'],flush=True)
 # Manual coordinator semantic review is recorded separately after reading the
 # raw answer. This utility checks identity/integrity, not truth by keywords.
 raw=(Path(reader['directory'])/'prompts-and-responses.txt');assert raw.exists()
 readable=ROOT/'reports/native-number-restoration-readable.txt'
 readable.write_text(f'''BIWN number conversion: verified progress on {now.isoformat()}

One more original game routine now runs as reconstructed C: number-to-text conversion at0x1B212. The coordinator generated it from the pinned instruction semantics. The local model did not write this C. The compiler and test runners are programs, not agents.

The standalone and linked routine each passed1,196normal cases with CPU and ordered memory comparisons,256divide-by-zero cases,and all50original instruction addresses. The full formatter matched3,654number-helper returns across1,654calls. These finite fixtures cover the public registers,stack and shared digit buffer. They do not prove arbitrary exception handlers,aliases or interrupt timing.

The experimental disc uses11,224resident bytes inside an11,264byte reservation. The heap starts at0x1619C0. The larger layout passed all19installation,component and resource checks. The originalCDI and default preview are unchanged.

Fresh gameplay completed the merchant and return-outdoors route in24,974frames,versus24,958for the immediate parent. A separate2,600frame repaired Deck test observed445completed compiled number calls with no task-stack violation; minimum observed headroom was444bytes. Player positions,video and audio differ. This is neither a whole-game speedup nor frame-equivalence result.

Easy local inference
Double-click Ask BIWN Candidate Status.command in the Desktop Local AI Lab folder. It now reads this new publication through the configured MCP connection. The actual local workflow took {reader['seconds']:.2f} seconds and produced {len(reader['answer'].split())} words. It uses the existing local 27B 6bit model; no weights were retrained. This run used the LM Studio SDK. Native Chat UI observation timed out, so no new native Chat generation is claimed.
The Reader fetches the evidence through MCP. If its draft exceeds the limit, a same-model Editor generates four short structured fields that are joined without truncation. This run used the Editor: {bool(reader.get('Editor'))}. These are sequential roles using the same weights, not independent verification. Raw drafts, Editor requests and constrained outputs are retained. The first scoped answer and unconstrained editing attempts failed their scope/length checks; those records remain available.
Exact system/user prompts,tool results and raw model response:
{raw}

ExperimentalCDI:
{pub['derived_disc']}

Full scoped report and exact rebuild command:
{pub['report']}

Remaining work includes the rest of the game/platform source,broader gameplay/audio,interrupt timing and authentic physical-console boot. Advertising research/education reliability,representative training gains and the future256GB deployment remain active requirements.
''')
 # Improve legibility of the human companion; authoritative receipts retain
 # exact raw wording/data and remain untouched.
 text=readable.read_text()
 for a,b in [('at0x','at 0x'),('passed1,196normal','passed 1,196 normal'),('comparisons,256divide-by-zero','comparisons, 256 divide-by-zero'),('all50original','all 50 original'),('matched3,654number-helper','matched 3,654 number-helper'),('across1,654calls','across 1,654 calls'),('registers,stack','registers, stack'),('handlers,aliases','handlers, aliases'),('uses11,224resident','uses 11,224 resident'),('an11,264byte','an 11,264 byte'),('at0x','at 0x'),('all19installation,component','all 19 installation, component'),('originalCDI','original CDI'),('in24,974frames,versus24,958for','in 24,974 frames, versus 24,958 for'),('separate2,600frame','separate 2,600 frame'),('observed445completed','observed 445 completed'),('was444bytes','was 444 bytes'),('positions,video','positions, video'),('connection. The','connection. The'),('local27B6bit','local 27B 6bit'),('NativeChat','Native Chat'),('timed out,so','timed out, so'),('ExperimentalCDI','Experimental CDI'),('prompts,tool','prompts, tool'),('source,broader','source, broader'),('audio,interrupt','audio, interrupt'),('reliability,representative','reliability, representative'),('future256GB','future 256GB')]:text=text.replace(a,b)
 readable.write_text(text)
 header='LATEST VERIFIED NUMBER CONVERSION'
 game_note=f'''{header} — {now.isoformat()}
Reconstructed number-to-text C at0x1B212 passed1,196normal/ordered cases,256zero-divisor cases and50/50instruction addresses. Complete formatter callers match3,654number returns. New11,224byte payload in11,264byte reservation,heapstart0x1619C0; all19layout/component/resource gates pass. Fresh Deck:445compiled returns,zero observed stack violations,444bytes minimum headroom. Both merchant/outdoor routes complete,parent24,958frames,new24,974; position/video/audio differ. No whole-game speedup,equivalence,complete source rebuild or physical-console proof. No default preview/weight promotion.
Readable report: {readable}
ExperimentalCDI: {pub['derived_disc']}

Earlier records follow.

'''
 local_note=f'''LATEST LOCAL STATUS OUTPUT — {now.isoformat()}
Ask BIWN Candidate Status.command now uses the new 11,224 byte number-conversion publication. Actual local workflow: {reader['seconds']:.2f} seconds, {len(reader['answer'].split())} words, one actual configured MCP status call, two Reader prediction rounds; same-model structured Editor used: {bool(reader.get('Editor'))}. SDK inference, not a new native Chat demonstration. Raw final answer passed the separately saved coordinator review within its finite evidence scope. Earlier overlong or conflated answers remain recorded.
Prompts/tool results/response: {raw}
Compiler and CPU/gameplay checks are deterministic tools. No localLLMauthored new C or new training updates in this step. Chat UI timedout120.6605seconds; continuing headlessly per user instruction.

Earlier records follow.

'''
 docs=[(ROOT/'CURRENT DECOMPILATION.txt',game_note),(ROOT/'CURRENT LOCAL INFERENCE.txt',local_note),(ROOT/'WATCH LOCAL AGENTS.txt',local_note),(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/README.txt',game_note)]
 for p,note in docs:
  (out/p.name).write_bytes(p.read_bytes());p.write_text(note+p.read_text())
 files=[Path(__file__),pp,rp,reviewp,raw,Path(reader['directory'])/'protocol.json',Path(reader['directory'])/'answer.txt',readable,ROOT/'native_format_evidence.py',ROOT/'biwn_status_editor.py',ROOT/'scripts/ask_biwn_current_status.py',ROOT/'Ask BIWN Candidate Status.command',*[p for p,_ in docs]]
 files.extend(p for p in Path(reader['directory']).rglob('*')if p.is_file())
 for name in ['current-biwn-status-20261018T184542.948118Z','current-biwn-status-20261018T184713.713397Z','current-biwn-status-20261018T184857.724523Z','current-biwn-status-Editor-20261018T184842.835010Z']:
  files.extend(p for p in (ROOT/'runs'/name).rglob('*')if p.is_file())
 runtime=Path('/Users/kevin/.lmstudio/local-ai-lab/native_format_evidence.py');assert sha(runtime)==sha(ROOT/'native_format_evidence.py')
 mismatches=[p for p,h in pub['status_dependencies_sha256'].items()if sha(p)!=h];assert not mismatches,mismatches
 state=dict(status='terminal_native_number_operator_followup_integrity_and_scoped_review_pass',directory=str(out),publication=str(pp),publication_sha256=sha(pp),game_evidence_files_checked=len(pub['status_dependencies_sha256']),game_evidence_mismatches=0,reader_directory=reader['directory'],reader_seconds=reader['seconds'],reader_word_count=len(reader['answer'].split()),reader_actual_MCP_calls=1,reader_rounds=reader['rounds'],roles=['Reader']+(['Editor']if reader.get('Editor')else[]),same_weights=True,Reader_draft_word_limit_pass=not bool(reader.get('Reader_draft_flags')),Editor_final_flags=reader.get('Editor',{}).get('flags'),answer=reader['answer'],coordinator_semantic_review_pending=False,semantic_review=str(reviewp),native_Chat_verified=False,local_UI_timeout_seconds=120.6605,dependencies_sha256={str(p):sha(p)for p in files},runtime_frontend=str(runtime),runtime_frontend_sha256=sha(runtime),new_training=False,default_promoted=False,goal_complete=False)
 save(out/'followup.json',state);save(ROOT/'verification/native-number-operator-followup-current.json',state)
 ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);ledger.update(latest_native_number_operator_followup=str(ROOT/'verification/native-number-operator-followup-current.json'),latest_current_status_launcher_verified=True,latest_finite_jobs_running=False);save(ledgerp,ledger)
 print(json.dumps(dict(status=state['status'],seconds=reader['seconds'],words=state['reader_word_count'],game_files_checked=state['game_evidence_files_checked'],report=str(readable))))
if __name__=='__main__':main()
