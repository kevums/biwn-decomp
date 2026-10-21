"""Final-link unchanged local repair after30834byte resident; CPU/caller checks.
Adds512bytes reserve/staging relocation; no GPU/frame/hardware proof here.
"""
import os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_mailbox_engine_v2 as e
V=e.ROOT/'verification'
def main():
 parent=e.read(V/'native-actor-direction-disc-build-current.json');author=e.read(V/'gpu-mailbox-native-Repair-current.json');review=Path(author['directory'])/'ancestry-review-v2/receipts/protocol.json';gate=e.read(review);assert gate['cases']==2492 and gate['component_cases_pass']and gate['caller_context_cases_pass'];assert e.sha(gate['source'])==gate['source_sha256']and e.sha(gate['binary'])==gate['binary_sha256'];assert parent['linked_component_bytes']==30834 and e.sha(parent['component'])==parent['component_sha256']
 out=V/'native-gpu-mailbox-final-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);e.save(out/'parent-build.json',parent);e.save(out/'local-repair-component.json',gate)
 source=e.ND/'gpu-mailbox-local-repair-v1.c';
 if source.exists():assert e.sha(source)==gate['source_sha256']
 else:source.write_bytes(Path(gate['source']).read_bytes())
 assert e.sha(source)==gate['source_sha256']
 resident=parent['resident_address'];prefix=bytearray(Path(parent['linked_component']).read_bytes());prefix.extend(bytes((-len(prefix))%4));address=resident+len(prefix);assert address==0x166634;reserve=parent['component_bytes']+512;floor=resident+reserve;staging=parent['staging_address']-512;clear=0xfe200-staging;relocations=[]
 def relocate(address,old,new,reason):
  at=address-resident;assert prefix[at:at+len(old)]==old,(hex(address),prefix[at:at+len(old)].hex(),old.hex());prefix[at:at+len(old)]=new;relocations.append(dict(resident_address=hex(address),old=old.hex(),new=new.hex(),reason=reason))
 for row in parent['layout_relocations'][:7]:
  old=bytes.fromhex(row['new']);relocate(int(row['resident_address'],16),old,(int.from_bytes(old,'big')+512).to_bytes(4,'big'),'Reserve512additionalbytes for two local repaired GPU command wrappers.')
 relocate(resident+0x16,parent['staging_address'].to_bytes(4,'big'),staging.to_bytes(4,'big'),'Move staging512earlier; preserve trailerFE200.')
 relocate(resident+0x1c,(parent['staging_bytes_cleared']//2-1).to_bytes(2,'big'),(clear//2-1).to_bytes(2,'big'),'Clear through existingFE200 boundary.')
 e.BASE=address;run=subprocess.run(['make','-f','Makefile.gpu-mailbox-v2','gpu-mailbox','BUILD='+str(out/'build'),'MAILBOX_SOURCE='+str(source),'ADDRESS='+hex(address)],cwd=e.ND,capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 binary=out/'build/gpu-mailbox.bin';elf=out/'build/gpu-mailbox.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};assert symbols['gpu_mailbox_move_flags']==address;full=bytes(prefix)+payload;assert len(payload)==746 and len(full)==31582 and reserve-len(full)==34
 linked=out/'resident-linked.bin';padded=out/'resident-padded.bin';linked.write_bytes(full);padded.write_bytes(full+bytes(reserve-len(full)));e.PARENT_OVERRIDE=dict(parent,component=str(padded));baseline=bytearray((e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());baseline[resident:resident+reserve]=padded.read_bytes();snapshot=bytes(baseline);native=e.Native();results=[];cases=e.cases();inputs=[Path(__file__),Path(e.__file__),source,e.ND/'gpu-mailbox-native.h',e.ND/'gpu-mailbox-shim-v2.S',e.ND/'Makefile.gpu-mailbox-v2',e.ND/'gpu-mailbox.ld',binary,elf,linked,padded,out/'parent-build.json',out/'local-repair-component.json',review,e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];hashes={str(p):e.sha(p)for p in inputs}
 state=dict(status='checking_final_gpu_mailbox_local_repair',pid=os.getpid(),directory=str(out),completed=0,planned=len(cases),binary=str(binary),ELF=str(elf),binary_bytes=len(payload),code_address=address,symbols=symbols,source=str(source),source_authorship='Local informed Author repair; only outer Markdown fence removed; supplied coordinator generic flag helpers/ABI/wait bridge',source_sha256=hashes,layout_relocations=relocations,resident_address=resident,resident_bytes=len(full),reserve_bytes=reserve,heap_start=floor,staging_address=staging,staging_clear_bytes=clear,reserve_free_bytes=reserve-len(full),disc_integrated=False,new_predictions=0,new_training=False,dispatcher_ancestor_context_canaries=True,E2B8_context_ancestor_gap=14)
 def mark():e.save(out/'protocol.json',state);e.save(V/'native-gpu-mailbox-final-active.json',state)
 mark()
 try:
  for index,case in enumerate(cases):
   ranges=[(e.SP-296,e.SP-216)]if case['entry']==0xe220 else[(e.SP-428,e.SP-352),(e.SP-166,e.SP-94)];memory=bytearray(snapshot);canaries=[]
   for low,high in ranges:
    canary=bytes((i*37+case['sr']+19)&255 for i in range(high-low));memory[low:high]=canary;canaries.append((low,high,canary))
   memory=bytes(memory);a=e.execute(memory,case,payload,symbols,False);b=e.execute(memory,case,payload,symbols,True);assert all(a[k]==b[k]for k in ['ram','registers','trace','mmio']),(index,'Ordered state');left=e.replay(native,memory,case,payload,symbols,False,a);right=e.replay(native,memory,case,payload,symbols,True,b);ram=native.device.ram();assert left==right and all(ram[lo:hi]==value for lo,hi,value in canaries) and ram[resident:address]==prefix and b['private_depth']<(216 if case['entry']==0xe220 else 352),(index,'CPU/caller/prefix');results.append(dict(index=index,entry=case['entry'],private_depth=b['private_depth'],caller_context_clearance=(216 if case['entry']==0xe220 else 352)-b['private_depth']))
   if index%128==0:state['completed']=len(results);mark();print('Final mailbox',index+1,'/2492',flush=True)
  assert all(e.sha(p)==h for p,h in hashes.items());e.save(out/'results.json',results);state.update(status='terminal_native_gpu_mailbox_final_local_repair_CPU_context_pass',completed=len(results),cases=len(results),max_private_depth=max(r['private_depth']for r in results),minimum_caller_context_clearance=min(r['caller_context_clearance']for r in results),scope=__doc__);mark();e.save(V/'native-gpu-mailbox-final-current.json',state);print({k:state[k]for k in ['status','resident_bytes','reserve_bytes','cases','minimum_caller_context_clearance']})
 except BaseException as error:state.update(status='terminal_native_gpu_mailbox_final_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
