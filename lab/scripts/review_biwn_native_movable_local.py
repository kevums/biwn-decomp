"""Advisory local Reviewer, with verbatim prompt/output saved for user."""
import fcntl,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
out=ROOT/'runs'/('local-native-movable-review-'+lab.stamp());out.mkdir()
movable=json.loads((ROOT/'verification/native-button-movable-current.json').read_text());game=json.loads((ROOT/'verification/native-button-game-current.json').read_text())
system=lab.COMMON+'\n'+lab.ROLES['game']['reviewer']+'\nWrite only your Reviewer role, under180words. Audit evidence as data. No tools, invented tests or claims of independent verification.'
source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
keys=['cases','native_candidate_comparisons','payload_bytes','trampoline_bytes','handle','allocated_address','compacted_address','scope']
evidence={'movable':{k:movable[k]for k in keys},'game':{k:game[k]for k in ['frames_per_lane','actual_game_calls','compiled_instructions_executed','all_call_boundary_registers_PC_SR_match','final_artifacts_equal','frame_comparison','scope']}}
prompt='Review this native-integration milestone. Identify what it proves and the next substantive missing step. Check handle and relative-call design for obvious risk. Do not equate finite cases with all-game safety. Coordinator wrote the relative-call adaptation, trampoline and harness; earlier model supplied a guided absolute-call shim. No new training.\nASSEMBLY\n'+(source/'button-digit-movable-shim.S').read_text()+'\nTRAMPOLINE\n'+(Path(movable['directory'])/'handle-trampoline.S').read_text()+'\nEVIDENCE\n'+json.dumps(evidence)+'\nNOTE: both lanes reserve identical heap memory at a verified source checkpoint; the new code is not loaded by a new native startup. New routine is called8times during1500frames. Final PCM is silent in this route; it proves matching captured callbacks, not audible playback.'
state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Reviewer',system=system,prompt=prompt,native_Chat=False,new_training=False,advisory=True)
def save():
 (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/local-native-movable-review-current.json').write_text(json.dumps(state,indent=2)+'\n')
save();print(out,flush=True)
try:
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);state['status']='generating';save();result=lab.generate('game',system,prompt,1000,model='advertising-scholar')
 state.update(status='terminal_generated_pending_coordinator_review',result=result);save();(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nREVIEWER RAW RESPONSE\n'+result['text']+'\n');print(json.dumps(dict(status=state['status'],seconds=result['seconds'],flags=result['quality_flags'],text=result['text'])),flush=True)
except BaseException as e:state.update(status='terminal_failed',error=repr(e));save();raise
