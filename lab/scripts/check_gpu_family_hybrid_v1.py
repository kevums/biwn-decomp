"""Two explicit coordinator fixes to rejected local repair; no unchanged-model success claim."""
import json,hashlib,subprocess,os,signal,sys,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 local=read(V/'GPU-command-family-local-native-current.json');assert local['status']=='terminal_eight_GPU_command_local_C_rejected_after_one_repair' and local['new_predictions']==2
 trial=Path(local['directory']);counter=read(trial/'repair/receipts/counterexample.json');assert counter['index']==3738 and counter['case']['entry']==0xe19e
 out=V/'GPU-command-family-coordinator-fix'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'local-trial-as-run.json',local);save(out/'original-counterexample.json',counter)
 before=(trial/'repair/candidate.c').read_text();source=before;edits=[dict(before='        d0 += 0x40u;\n',after='        d0 += 0x40u;\n        r[0] = d0;\n',reason='OriginalE19E changes guestD0 to47BC8;locald0alone does not change captured guestD0.'),dict(before='r[16] = (r[16] & 0xfff0u)',after='r[16] = (r[16] & 0xffe0u)',reason='Known32bit ADD47B88+40 setsX=0;allsubsequentMOVE/CMP/wait operations preserveX. ClearX along withNZVC before calculating the known ADD flags.')]
 for e in edits:assert source.count(e['before'])==1;source=source.replace(e['before'],e['after'])
 target=ND/'gpu-family-hybrid-v1.c';assert not target.exists();target.write_text(source);(out/'before.c').write_text(before);(out/'after.c').write_text(source);save(out/'edits.json',edits);save(out/'descriptor.json',dict(candidate=str(target)))
 state=dict(status='checking_eight_GPU_hybrid',pid=os.getpid(),directory=str(out),source=str(target),source_sha256=sha(target),local_trial=local['directory'],local_trial_passed=False,coordinator_edit_operations=2,new_predictions=0,new_training=False,source_accepted=False,live_integrated=False,scope=__doc__)
 def mark():save(out/'protocol.json',state);save(V/'GPU-command-family-hybrid-current.json',state)
 mark();print(out,flush=True)
 with(out/'check.log').open('w')as log:
  child=subprocess.Popen([sys.executable,str(ROOT/'scripts/check_gpu_family_arena_candidate_v1.py'),str(out/'descriptor.json'),str(out/'receipts')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);state['current_child_pid']=child.pid;mark()
  try:code=child.wait(timeout=900)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
 receipt=read(out/'receipts/protocol.json');state.update(current_child_pid=None,verifier_exit_code=code,component_receipt=str(out/'receipts/protocol.json'),component_cases=receipt['completed'],component_pass=code==0 and receipt.get('component_cases_pass',False),max_original_stack_depth=receipt.get('max_private_depth'),max_arena_stack_depth=receipt.get('max_arena_depth'))
 state['status']='terminal_eight_GPU_roots_hybrid_component_pass_pending_final_layout'if state['component_pass']else'terminal_eight_GPU_roots_hybrid_rejected';state['source_bindings_sha256']={str(p):sha(p)for p in [Path(__file__),target,trial/'repair/candidate.c',out/'edits.json',out/'original-counterexample.json',out/'receipts/protocol.json',ROOT/'scripts/check_gpu_family_arena_candidate_v1.py',ROOT/'scripts/native_gpu_family_arena_engine_v1.py',ND/'gpu-family-arena-shim-v1.S',ND/'Makefile.gpu-family-arena-v1']};mark();print(json.dumps(state))
if __name__=='__main__':main()
