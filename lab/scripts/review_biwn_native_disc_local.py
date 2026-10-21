"""Advisory local code/scope review of native-derived disc build."""
import fcntl,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
b=json.loads((ROOT/'verification/native-disc-build-current.json').read_text());e=json.loads((ROOT/'verification/native-disc-entry-current.json').read_text());out=ROOT/'runs'/('local-native-disc-review-'+lab.stamp());out.mkdir()
system=lab.COMMON+'\n'+lab.ROLES['game']['reviewer']+'\nWrite only Reviewer, under160words. Distinguish observed defects from untested scope. You have no tools and are not an independent execution oracle.'
assembly=(Path(b['directory'])/'native-stage-entry.S').read_text();patches=json.loads(Path(b['patch_manifest']).read_text())
prompt='Audit this concrete partial native-CD build and entry design. Give any specific correctness concern and the next missing acceptance step. Do not invent a failure or a test.\nNATIVE STARTUP ASSEMBLY\n'+assembly+'\nDECLARED LAYOUT/PATCHES\n'+json.dumps(patches)+'\nEXECUTED ENTRY CHECK EVIDENCE\n'+json.dumps({k:e[k]for k in ['status','entry_cases','component_cases','heap_reserved_bytes','payload_unchanged_after_heap_init_allocation_compaction','scope']})+'\nCURRENT LIMITS\nFresh24000frame original/derived disc runs are in progress, not yet accepted. No checkpoint or host RAMpatch in those runs. HLE/CD bootstrap, drive and full original CPU/GPU/DSP/device emulator remain providers. No physical/authenticated boot proof. Mainstage first10bytes also lie within the original60000byte initial boot payload overlap; the derived image deliberately changes that overlap. Loader staging atFF000is consumed immediately before original initialization, not assumed forever-free. Native130byte payload has no internal absolute code references and is copied below a heap base raised by136bytes. New frame-level equivalence, audio/content and broader routes remain unaccepted. Coordinator wrote loader/build/checks, reused recovered C plus coordinator-adapted earlier guided-model ABI shim. No new training.'
state=dict(status='prepared',pid=os.getpid(),directory=str(out),system=system,prompt=prompt,role='Reviewer',native_Chat=False,new_training=False,advisory=True)
def save():
 (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/local-native-disc-review-current.json').write_text(json.dumps(state,indent=2)+'\n')
save();print(out,flush=True)
try:
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);state['status']='generating';save();result=lab.generate('game',system,prompt,900,model='advertising-scholar')
 state.update(status='terminal_pending_coordinator_review',result=result);save();(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nRAW REVIEWER\n'+result['text']+'\n');print(json.dumps(dict(status=state['status'],seconds=result['seconds'],flags=result['quality_flags'],words=len(result['text'].split()),text=result['text'])),flush=True)
except BaseException as e:state.update(status='terminal_failed',error=repr(e));save();raise
