"""Strict-build and original-facing check of one unchanged local proposal.
Only one complete outer Markdown code fence is removed and explicitly recorded.
"""
import json,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import native_actor_direction_engine_v2 as e
ROOT=e.ROOT;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 pointer=Path(sys.argv[1]);author=read(pointer);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False);raw=Path(author['candidate']).read_text();match=re.fullmatch(r'\s*```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',raw);source=match[1]if match else raw;candidate=out/'candidate-unfenced.c';candidate.write_text(source+'\n')
 state=dict(status='checking_unchanged_local_direction_proposal',directory=str(out),author_pointer=str(pointer),candidate=str(candidate),raw_candidate=author['candidate'],normalization='One complete outercodefence removed;no sourcechanges'if match else'No normalization',requested_raw_C_format_violated=bool(match),source_accepted=False,new_training=False)
 def mark():e.g.save(out/'protocol.json',state)
 mark();run=subprocess.run(['make','-f',str(e.ND/'Makefile.actor-direction-v2'),'actor-direction','BUILD='+str(out/'build'),'DIRECTION_SOURCE='+str(candidate)],capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);state['compiler_exit_code']=run.returncode;mark()
 if run.returncode:state.update(status='terminal_local_direction_proposal_rejected_by_strict_compiler');mark();return
 binary=out/'build/actor-direction.bin';elf=out/'build/actor-direction.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();completed=0
 try:
  for index,case in enumerate(e.vectors()):
   import copy
   case=copy.deepcopy(case);low,high=e.SP-312,e.SP-232;canary=bytes(((i*43+case['sr']+17)&255)for i in range(80));case['initial']+=[[low+i,1,value]for i,value in enumerate(canary)]
   try:
    a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);differences=[k for k in ['ram','registers','trace']if a[k]!=b[k]];left=e.replay(native,snapshot,case,payload,symbols,False,a);right=e.replay(native,snapshot,case,payload,symbols,True,b)
    if left!=right:differences.append('nativeCPU_SR_banks_or_helper_entry')
    if native.device.ram()[low:high]!=canary or b['private_depth']>=232:differences.append('caller_context_or_private_stack_limit')
    if differences:
     e.g.save(out/'counterexample.json',dict(index=index,case=case,differences=differences,original=left,local=right,original_trace=a['trace'],local_trace=b['trace']));raise AssertionError('Original-facing comparison failed')
   except BaseException as error:
    if not(out/'counterexample.json').exists():e.g.save(out/'counterexample.json',dict(index=index,case=case,error=repr(error),execution=e.LAST_EXECUTION_DIAGNOSTIC))
    state.update(status='terminal_local_direction_proposal_rejected_by_original_execution',completed=completed,first_failed_case=index,error=repr(error),counterexample=str(out/'counterexample.json'));mark();print(json.dumps(state));return
   completed+=1
   if index%128==0:state['completed']=completed;mark();print('Local proposal',completed,'/2560',flush=True)
  state.update(status='terminal_direction_component_and_caller_context_pass_pending_layout_gameplay',completed=completed,source_accepted=False,component_cases_pass=True,caller_context_cases_pass=True,binary=str(binary),binary_sha256=e.g.sha(binary),binary_bytes=len(payload));mark();print(json.dumps(state))
 finally:native.close()
if __name__=='__main__':main()
