"""Bind the real post-publication local Reader; do not change game evidence."""
import datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
pp=ROOT/'verification/native-unsigned-publication-current.json';pub=read(pp);out=Path(pub['directory']);report=Path(pub['report']);reader_pointer=ROOT/'verification/current-biwn-status-reader-current.json';reader=read(reader_pointer);folder=Path(reader['directory'])
assert reader['status']=='terminal_local_current_status_pending_review' and not reader['answer_review_flags'] and reader['model_inference_invoked']
assert len(reader['calls'])==1 and reader['calls'][0]['name']=='project_evidence'
response=reader['calls'][0]['result'];assert response['proof_sha256']==sha(pp)
expected=dict(pub['current_status'],proof_sha256=sha(pp));assert response==expected,'Tool scope changed'
assert len(reader['answer'].split())<180
before=(out/'publication-before-operator-followup.json');before.write_bytes(pp.read_bytes());(out/'report-before-operator-followup.txt').write_bytes(report.read_bytes())
for p,h in pub['status_dependencies_sha256'].items():assert sha(p)==h,p
review=dict(status='accepted_local_unsigned_status_Reader_within_published_scope',recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),directory=str(folder),protocol=str(folder/'protocol.json'),protocol_sha256=sha(folder/'protocol.json'),input_publication_snapshot=str(before),input_publication_sha256=sha(before),actual_configured_MCP_calls=1,seconds=reader['seconds'],words=len(reader['answer'].split()),answer_accepted_unchanged=True,reviewer='Codex coordinator; not independent human validation',source_read_correct=True,physical_console_or_whole_game_claim=False,new_training=False,native_Chat_verified=False,model_authored_C=False,scope='One local SDK operator-status generation over verified published evidence. Not a coding-success benchmark or new game test.')
save(folder/'coordinator-review.json',review);save(ROOT/'verification/native-unsigned-status-reader-reviewed-current.json',review)
text=report.read_text().replace('The current status shortcut is being connected to this publication; its local Reader validation is recorded separately after publication.', 'The existing status shortcut now reads this publication through the installed MCP integration. Its post-publication local Reader validation is recorded below.')
text+=f'''\nPost-publication local status workflow\nDesktop -> Local AI Lab -> Ask BIWN Candidate Status.command successfully reads the8956byte build through actual configured MCP. A real local Reader took{reader['seconds']:.2f}seconds,two prediction rounds,one MCP call and returned{review['words']}words. Codex accepted the raw summary unchanged against the exact publication it saw; no whole-game,frame-equivalence,speedup,physical-console or weight-training claim was added. This was SDK inference,not a new native Chat generation.\nReader prompts/tool response/raw answer: {folder/'prompts-and-responses.txt'}\nReader review: {folder/'coordinator-review.json'}\nThe exact publication bytes supplied to that run are archived at{before}. Only this report/operator metadata changed afterward; current_status fields and all game-core evidence remain identical,except the automatically computed publication hash.\n'''
report.write_text(text)
pub['operator_followup']=review;pub['dependencies_sha256'][str(report)]=sha(report)
for p in folder.rglob('*'):
 if p.is_file():pub['dependencies_sha256'][str(p.resolve())]=sha(p)
for p in [before,out/'report-before-operator-followup.txt',ROOT/'native_format_evidence.py',ROOT/'scripts/ask_biwn_current_status.py',Path(__file__)]:pub['dependencies_sha256'][str(p.resolve())]=sha(p)
pub['workflow_dependencies_sha256']={str(p):sha(p) for p in [ROOT/'native_format_evidence.py',RT/'native_format_evidence.py',ROOT/'scripts/ask_biwn_current_status.py',ROOT/'reference_mcp_bridge.py',RT/'chat_tools.py']}
save(out/'publication.json',pub);save(pp,pub)
# Updating operator notes must not mutate source/game evidence.
notes={
 'CURRENT DECOMPILATION.txt':f'''LATEST EXPERIMENTAL NATIVE UNSIGNED ARITHMETIC - {review['recorded_at']}\nTwo new coordinator C entry contracts E61C/E67C pass3592native/ordered+512zero cases,43/43instruction addresses. New8956byte payload in9216reservation; prior8482bytes exact.1654formatter calls/24421outer helper returns and19component/install/resource gates pass. Fresh repaired Deck:1228completed calls each,zero stack violations. Both long merchant/floor0/outdoor routes finish,29791versus24958frames,but movie/audio/player/video differ: no speedup or frame-equivalence claim. Original engine/emulator/firmware/device providers remain; full source and physicalconsole incomplete. Defaultpreview unchanged.\nReport: {report}\nCDI: {pub['derived_disc']}\n\nEarlier records follow.\n\n''',
 'CURRENT LOCAL INFERENCE.txt':f'''LATEST UNSIGNED RECOVERY AND LOCAL STATUS - {review['recorded_at']}\nLocal Author:152.77seconds,3500token output limit,incompleteC rejected before compilation. Accepted new arithmetic is coordinator source,not that model output. Local status Reader:{reader['seconds']:.2f}seconds,one actual MCP lookup,{review['words']}words accepted unchanged against scoped8956byte evidence. SDK runs,not new nativeChat generations;no new training/weight promotion.\nUse Ask BIWN Candidate Status.command.\nAuthor: {Path(pub['current_status']['local_inference_example']['prompts_and_responses'])}\nReader: {folder/'prompts-and-responses.txt'}\n\nEarlier records follow.\n\n''',
 'WATCH LOCAL AGENTS.txt':f'''LATEST SAVED ROLES - {review['recorded_at']}\nAuthor used the daily local27B/6bit model and failed complete C generation; its raw output was not installed.\n{pub['current_status']['local_inference_example']['prompts_and_responses']}\nReader used the same weights and one real configured MCP lookup to explain current evidence in{reader['seconds']:.2f}seconds.\n{folder/'prompts-and-responses.txt'}\nCompiler,CPU/Unicorn comparisons,disc builder and gameplay runners are deterministic programs,not LLM agents or independent reviewers.\n{report}\n\nEarlier records follow.\n\n''',
 'projects/black-ice-white-noise/restoration/native-m68k/README.txt':f'''PARTIAL NATIVE M68000 RESTORATION - latest8956byte unsigned-arithmetic experiment\n\nNew E61C/E67C coordinator C: unsigned-division-native.c,header and exception/ABI shim.\nStandalone build: make -f Makefile.unsigned-division unsigned-division BUILD=/tmp/biwn-unsigned-standalone\nComplete tested mixed payload: make -f {Path(pub['current_status']['experimental_build']['compiled_binary']).parents[1]/'Makefile'} format-bundle BUILD=/tmp/biwn-unsigned-rebuild\n8956linked bytes,9216reservation,heap0x1611C0.27stageJMPredirects are not recovered-function totals. Full scoped helper/caller/component checks pass; finite gameplay/audio differ. Original engine/emulator/firmware/device providers remain. No complete source-built console game or physical-console result;defaultpreview unchanged.\n{report}\n\nHistorical diagnostic instructions follow.\n\n'''}
for name,header in notes.items():
 path=ROOT/name;assert str(path)not in pub['status_dependencies_sha256'];old=path.read_bytes();(out/(path.name.replace(' ','-')+'-before')).write_bytes(old);path.write_text(header+old.decode())
ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);ledger.update(latest_native_status_reader_review=str(ROOT/'verification/native-unsigned-status-reader-reviewed-current.json'),latest_current_status_launcher_verified=True,latest_finite_jobs_running=False,latest_finite_job_status='All source,component,gameplay and local Reader jobs terminal; no pending job from this continuation.');save(ledgerp,ledger)
import sys
sys.path.insert(0,str(ROOT))
import native_format_evidence
actual=native_format_evidence.load(ROOT);actual.pop('proof_sha256');assert actual==pub['current_status']
assert all(sha(p)==h for p,h in pub['status_dependencies_sha256'].items())
assert all(sha(p)==h for p,h in pub['dependencies_sha256'].items())
model=json.loads(subprocess.check_output(['/Users/kevin/.lmstudio/bin/lms','ps','--json'],text=True));assert any(m.get('identifier')=='advertising-scholar' and m.get('status')=='idle' for m in model)
print(json.dumps(dict(status=pub['status'],local_Reader_seconds=reader['seconds'],local_Reader_words=review['words'],MCP_calls=1,game_core_files=len(pub['status_dependencies_sha256']),integrity_mismatches=0,goal_complete=False),indent=2))
