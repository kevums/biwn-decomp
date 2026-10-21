"""Fixed candidate file/receipt driver for two GPU-mailbox roots and callers."""
import json,subprocess,sys
from pathlib import Path
import native_gpu_mailbox_engine as e
def main():
 descriptor=e.read(sys.argv[1]);candidate=Path(descriptor['candidate']);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False);state=dict(status='checking_gpu_mailbox_candidate',completed=0,source_accepted=False,new_training=False,source=str(candidate),source_sha256=e.sha(candidate))
 def mark():e.save(out/'protocol.json',state)
 mark();run=subprocess.run(['make','-f','Makefile.gpu-mailbox-v2','gpu-mailbox','BUILD='+str(out/'build'),'MAILBOX_SOURCE='+str(candidate)],cwd=e.ND,capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);state['compiler_exit_code']=run.returncode;mark()
 if run.returncode:state.update(status='terminal_gpu_mailbox_candidate_rejected_by_strict_compiler');mark();return
 binary=out/'build/gpu-mailbox.bin';elf=out/'build/gpu-mailbox.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();depths=[]
 try:
  for index,case in enumerate(e.cases()):
   try:
    ranges=[(e.SP-296,e.SP-216)]if case['entry']==0xe220 else[(e.SP-428,e.SP-352),(e.SP-166,e.SP-94)];memory=bytearray(snapshot);canaries=[]
    for low,high in ranges:
     canary=bytes((i*37+case['sr']+19)&255 for i in range(high-low));memory[low:high]=canary;canaries.append((low,high,canary))
    memory=bytes(memory)
    a=e.execute(memory,case,payload,symbols,False);b=e.execute(memory,case,payload,symbols,True);diff=[k for k in ['ram','registers','trace','mmio']if a[k]!=b[k]];left=e.replay(native,memory,case,payload,symbols,False,a);right=e.replay(native,memory,case,payload,symbols,True,b)
    if left!=right:diff.append('native_CPU_SR_banks_helper_entries')
    if any(native.device.ram()[lo:hi]!=value for lo,hi,value in canaries) or b['private_depth']>=(216 if case['entry']==0xe220 else 352):diff.append('caller_context_or_stack_limit')
    if diff:e.save(out/'counterexample.json',dict(index=index,case=case,differences=diff,original=left,candidate=right,original_trace=a['trace'],candidate_trace=b['trace']));raise AssertionError('Original comparison failed')
   except BaseException as error:
    if not(out/'counterexample.json').exists():
     diagnostic={};tb=error.__traceback__
     while tb:
      frame=tb.tb_frame
      if frame.f_code.co_name=='execute'and 'script'in frame.f_locals:
       bus=frame.f_locals['script'];u=frame.f_locals['u'];diagnostic=dict(PC=u.reg_read(e.UC_M68K_REG_PC),SP=u.reg_read(e.UC_M68K_REG_A7),phase=bus.phase,read_counts=bus.indices,required_reads={k:len(case[k])for k in ['pre','ack','post']},last_public_accesses=bus.trace[-16:],last_instructions=frame.f_locals['machine'][-16:])
      tb=tb.tb_next
     original=dict(instructions=len(a['machine']),trace=a['trace'])if 'a'in locals()else None
     e.save(out/'counterexample.json',dict(index=index,case=case,error=repr(error),original_execution=original,candidate_execution=diagnostic,scope='Observed machine execution and actual injected replies, no target C supplied. Repeated acknowledgement reads after an unequal reply mean the candidate did not follow the original branch.'))
    state.update(status='terminal_gpu_mailbox_candidate_rejected_by_original_execution',counterexample=str(out/'counterexample.json'),first_failed_case=index,error=repr(error));mark();return
   state['completed']=index+1;depths.append(b['private_depth'])
   if index%128==0:mark();print('Candidate',index+1,'/2492',flush=True)
  state.update(status='terminal_gpu_mailbox_component_and_caller_context_pass_pending_layout_gameplay_v2',component_cases_pass=True,caller_context_cases_pass=True,binary=str(binary),ELF=str(elf),binary_sha256=e.sha(binary),binary_bytes=len(payload),symbols=symbols,code_address=e.BASE,max_private_depth=max(depths),cases=2492,scope=__doc__);mark();print(json.dumps(state))
 finally:native.close()
if __name__=='__main__':main()
