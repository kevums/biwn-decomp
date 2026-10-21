"""Actual movement/sprite caller context ranges; four semantic negative controls.

Movement context rootSP-360..-280, E220 entry rootSP-64: -296..-216.
Sprite context rootSP-500..-424, E2B8 entry rootSP-72: -428..-352.
Ranges follow current compiled caller assembly, not an interrupt stack bound.
"""
import capstone,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_mailbox_engine as e
V=e.ROOT/'verification'
def main():
 gate=e.read(V/'native-gpu-mailbox-current.json');assert gate['cases']==2492
 for p,h in gate['source_sha256'].items():assert e.sha(p)==h,p
 out=V/'native-gpu-mailbox-contexts-negatives-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);e.save(out/'component-gate.json',gate);print(out,flush=True)
 payload=Path(gate['binary']).read_bytes();symbols=gate['symbols'];snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();rows=[];controls=[];cases=e.cases();state=dict(status='checking_mailbox_callers_and_negatives',pid=os.getpid(),directory=str(out),completed=0,planned=len(cases))
 def mark():e.save(out/'protocol.json',state);e.save(V/'native-gpu-mailbox-contexts-negatives-active.json',state)
 mark()
 try:
  for index,case in enumerate(cases):
   low,high=(e.SP-296,e.SP-216)if case['entry']==0xe220 else(e.SP-428,e.SP-352);canary=bytes((i*37+case['sr']+19)&255 for i in range(high-low));memory=bytearray(snapshot);memory[low:high]=canary;memory=bytes(memory)
   a=e.execute(memory,case,payload,symbols,False);b=e.execute(memory,case,payload,symbols,True);assert all(a[k]==b[k]for k in ['ram','registers','trace','mmio']);left=e.replay(native,memory,case,payload,symbols,False,a);right=e.replay(native,memory,case,payload,symbols,True,b);assert left==right and native.device.ram()[low:high]==canary and b['private_depth']<e.SP-high
   rows.append(dict(index=index,entry=case['entry'],depth=b['private_depth'],clearance=e.SP-high-b['private_depth']))
   if index%128==0:state['completed']=len(rows);mark();print('Caller',index+1,'/',len(cases),flush=True)
  source=(e.ND/'gpu-mailbox-reference-v1.c').read_text();xcase=next(i for i,case in enumerate(cases)if case['sr']&16);ackcase=next(i for i,case in enumerate(cases)if len(case['ack'])>1)
  defects=[('wrong_argument_offset','r[15]+4u+4u*i','r[15]+8u+4u*i',0),('wrong_five_parameter_count','?5u:3u','?4u:3u',0),('lost_X_before_second_wait','gpu_mailbox_compare_flags(r,value,command);','gpu_mailbox_compare_flags(r,value,command);r[16]&=~16u;',xcase),('skip_command_acknowledgement','if(value!=command)break;','break;',ackcase)]
  for name,old,new,index in defects:
   assert source.count(old)==1;folder=out/name;folder.mkdir();candidate=folder/'candidate.c';candidate.write_text(source.replace(old,new));run=subprocess.run(['make','-f','Makefile.gpu-mailbox','gpu-mailbox','BUILD='+str(folder/'build'),'MAILBOX_SOURCE='+str(candidate)],cwd=e.ND,capture_output=True,text=True);(folder/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
   binary=folder/'build/gpu-mailbox.bin';elf=folder/'build/gpu-mailbox.elf';badpayload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);badsymbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};case=cases[index];diff=[]
   try:
    a=e.execute(snapshot,case,badpayload,badsymbols,False);b=e.execute(snapshot,case,badpayload,badsymbols,True);diff=[k for k in ['ram','registers','trace','mmio']if a[k]!=b[k]];left=e.replay(native,snapshot,case,badpayload,badsymbols,False,a);right=e.replay(native,snapshot,case,badpayload,badsymbols,True,b)
    if left!=right:diff+=['native_CPU_SR_banks_helper_entries']
   except AssertionError as error:diff+=['execution_invariant:'+repr(error)]
   assert diff,(name,'Semantic defect escaped');row=dict(defect=name,index=index,rejected=True,differences=diff,source_sha256=e.sha(candidate),binary_sha256=e.sha(binary));e.save(folder/'result.json',row);controls.append(row);print(name,diff,flush=True)
  witness=max(rows,key=lambda row:row['depth']);case=cases[witness['index']];memory=bytearray(snapshot);low,high=e.SP-190,e.SP-114;canary=bytes([0xa5])*76;memory[low:high]=canary;result=e.execute(bytes(memory),case,payload,symbols,True);e.replay(native,bytes(memory),case,payload,symbols,True,result);assert native.device.ram()[low:high]!=canary;controls.append(dict(defect='deliberately_overlapping_caller_context',rejected=True,range=[low,high]))
  decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);sites={i.address for entry,(end,*_)in e.ROOTS.items()for i in decoder.disasm(snapshot[entry:end],entry)};assert sites<=set(gate['original_sites'])
  e.save(out/'results.json',rows);e.save(out/'negative-controls.json',controls);inputs=[Path(__file__),out/'component-gate.json',out/'results.json',out/'negative-controls.json',e.ND/'actor-chain-compact-shim.S',e.ND/'sprite-create-shim.S',Path(gate['binary'])]
  state.update(status='terminal_gpu_mailbox_caller_contexts_and_semantic_negatives_pass',completed=len(rows),cases=len(rows),max_private_depth=max(r['depth']for r in rows),minimum_caller_context_clearance=min(r['clearance']for r in rows),semantic_negatives_rejected=4,overlap_negative_rejected=True,original_reachable_sites=[len(sites),len(sites&set(gate['original_sites']))],source_sha256={str(p):e.sha(p)for p in inputs},scope=__doc__);mark();e.save(V/'native-gpu-mailbox-contexts-negatives-current.json',state);print(json.dumps(state))
 except BaseException as error:state.update(status='terminal_gpu_mailbox_contexts_negatives_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
