"""Fixed candidate file/receipt driver for eight complete GPU-mailbox roots; finite CPU/bus/arena checks."""
import json,subprocess,sys
from pathlib import Path
import native_gpu_family_arena_engine_v1 as e
def main():
 descriptor=e.read(sys.argv[1]);candidate=Path(descriptor['candidate']);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False);state=dict(status='checking_gpu_mailbox_candidate',completed=0,source_accepted=False,new_training=False,source=str(candidate),source_sha256=e.sha(candidate))
 def mark():e.save(out/'protocol.json',state)
 mark();run=subprocess.run(['make','-f','Makefile.gpu-family-arena-v1','gpu-mailbox','BUILD='+str(out/'build'),'MAILBOX_SOURCE='+str(candidate)],cwd=e.ND,capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);state['compiler_exit_code']=run.returncode;mark()
 if run.returncode:state.update(status='terminal_gpu_mailbox_candidate_rejected_by_strict_compiler');mark();return
 binary=out/'build/gpu-mailbox.bin';elf=out/'build/gpu-mailbox.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(e.read(e.ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert all(snapshot[a:b]==image[a-0x4000:b-0x4000]for a,(b,*_)in e.ROOTS.items());native=e.Native();depths=[];arena_depths=[];coverage=set()
 try:
  for index,case in enumerate(e.arena_cases()):
   try:
    sp=case['sp'];ranges=[(sp-296,sp-216)]if case['entry']==0xe220 else([(sp-428,sp-352),(sp-230,sp-158)]if case['entry']==0xe2b8 else[(sp-90,sp-10)]);memory=bytearray(snapshot);canaries=[]
    for low,high in ranges:
     canary=bytes((i*37+case['sr']+19)&255 for i in range(high-low));memory[low:high]=canary;canaries.append((low,high,canary))
    memory=bytes(memory)
    a=e.execute(memory,case,payload,symbols,False);b=e.execute(memory,case,payload,symbols,True);diff=[k for k in ['ram','registers','trace','mmio']if a[k]!=b[k]];left=e.replay(native,memory,case,payload,symbols,False,a);right=e.replay(native,memory,case,payload,symbols,True,b)
    if left!=right:diff.append('native_CPU_SR_banks_helper_entries')
    if any(native.device.ram()[lo:hi]!=value for lo,hi,value in canaries) or b['private_depth']>10 or b['arena_depth']>224:diff.append('caller_context_or_stack_limit')
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
   coverage.update(a['coverage']);state['completed']=index+1;depths.append(b['private_depth']);arena_depths.append(b['arena_depth'])
   if index%128==0:mark();print('Candidate',index+1,'/10048',flush=True)
  from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
  decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);expected={i.address for a,(b,*_)in e.ROOTS.items()for i in decoder.disasm(snapshot[a:b],a)};assert coverage==expected;(out/'original-coverage.json').write_text(json.dumps(dict(expected=sorted(expected),observed=sorted(coverage)),indent=2)+'\n')
  state.update(status='terminal_eight_GPU_command_roots_component_pass_pending_integration',original_instruction_addresses=len(expected),component_cases_pass=True,caller_context_cases_pass=True,binary=str(binary),ELF=str(elf),binary_sha256=e.sha(binary),binary_bytes=len(payload),symbols=symbols,code_address=e.BASE,max_private_depth=max(depths),max_arena_depth=max(arena_depths),arena_address=e.ARENA,arena_slots=102,arena_usable_slot_bytes=224,cases=len(e.arena_cases()),scope=__doc__);mark();print(json.dumps(state))
 finally:native.close()
if __name__=='__main__':main()
