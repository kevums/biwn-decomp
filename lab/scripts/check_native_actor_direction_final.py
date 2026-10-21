"""Link direction after the current resident payload and verify planned layout.
Full original/native CPU/SR/banks/publicRAM/ordered access plus actual caller
context canary. The new heap/staging plan still needs constructor/gameplay gates.
"""
import copy,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_actor_direction_engine_v1 as e
ROOT=e.ROOT;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 parent=read(V/'native-navigation-hybrid-disc-build-current.json');proto=read(V/'native-actor-direction-current.json');contexts=read(V/'native-actor-direction-contexts-current.json');assert proto['cases']==contexts['cases']==2560
 assert e.g.sha(parent['linked_component'])==e.g.sha(Path(parent['directory'])/'resident-linked.bin')and parent['linked_component_bytes']==30036
 out=V/'native-actor-direction-final'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);e.g.save(out/'parent-build.json',parent);e.g.save(out/'prototype-gate.json',proto)
 resident=parent['resident_address'];prefix=bytearray(Path(parent['linked_component']).read_bytes());address=resident+len(prefix);assert address==0x166314
 reserve=parent['component_bytes']+1024;floor=resident+reserve;staging=parent['staging_address']-1024;clear=0xfe200-staging;assert reserve==31104 and floor==0x166740 and staging==0xf6800 and clear-40-reserve==88
 relocations=[]
 def relocate(at,old,new,reason):
  assert prefix[at:at+len(old)]==old,(at,prefix[at:at+len(old)].hex(),old.hex());prefix[at:at+len(old)]=new;relocations.append(dict(resident_address=hex(resident+at),old=old.hex(),new=new.hex(),reason=reason))
 for row in parent['inherited_layout_relocations'][:7]:
  old=bytes.fromhex(row['new']);relocate(int(row['resident_address'],16)-resident,old,(int.from_bytes(old,'big')+1024).to_bytes(4,'big'),'Additional1024bytes reserve for complete direction native body.')
 relocate(0x16,parent['staging_address'].to_bytes(4,'big'),staging.to_bytes(4,'big'),'Move staging earlier by1024; preserve trailer endFE200.')
 relocate(0x1c,(parent['staging_bytes_cleared']//2-1).to_bytes(2,'big'),(clear//2-1).to_bytes(2,'big'),'Clear through existingFE200 trailer boundary.')
 planned=out/'relocated-parent-prefix.bin';planned.write_bytes(prefix);e.BASE=address
 source=e.ND/'actor-direction-reference-v2.c';run=subprocess.run(['make','-f',str(e.ND/'Makefile.actor-direction-v2'),'actor-direction','BUILD='+str(out/'build'),'DIRECTION_SOURCE='+str(source),'ADDRESS='+hex(address)],capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 binary=out/'build/actor-direction.bin';elf=out/'build/actor-direction.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
 full=bytes(prefix)+payload;assert len(payload)==798 and len(full)==30834 and reserve-len(full)==270
 (out/'resident-linked.bin').write_bytes(full);(out/'resident-padded.bin').write_bytes(full+bytes(reserve-len(full)))
 baseline=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());baseline[resident:resident+reserve]=bytes(prefix)+bytes(reserve-len(prefix));snapshot=bytes(baseline);native=e.Native();rows=[];coverage=set();cases=e.vectors();inputs=[Path(__file__),Path(e.__file__),Path(e.g.__file__),source,e.ND/'actor-direction-native.h',e.ND/'actor-direction-shim-v2.S',e.ND/'Makefile.actor-direction-v2',e.ND/'actor-direction.ld',binary,elf,planned,out/'parent-build.json',out/'prototype-gate.json',out/'resident-linked.bin',out/'resident-padded.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];hashes={str(p):e.g.sha(p)for p in inputs}
 state=dict(status='checking_final_direction_with_planned_parent',pid=os.getpid(),directory=str(out),completed=0,planned=len(cases),binary=str(binary),ELF=str(elf),binary_bytes=len(payload),code_address=address,symbols=symbols,source_sha256=hashes,source=str(source),source_authorship='Coordinator native adaptation of earlier checked portablebody;localproposalsnotadopted',layout_relocations=relocations,resident_address=resident,resident_bytes=len(full),reserve_bytes=reserve,heap_start=floor,staging_address=staging,staging_clear_bytes=clear,reserve_free_bytes=reserve-len(full),disc_integrated=False,new_predictions=0,new_training=False)
 def mark():e.g.save(out/'protocol.json',state);e.g.save(V/'native-actor-direction-final-active.json',state)
 mark()
 try:
  for index,original in enumerate(cases):
   case=copy.deepcopy(original);low,high=e.SP-312,e.SP-232;canary=bytes(((i*43+case['sr']+17)&255)for i in range(high-low));case['initial']+=[[low+i,1,value]for i,value in enumerate(canary)]
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);assert all(a[k]==b[k]for k in ['ram','registers','trace']),(index,'orderedorRAM')
   left=e.replay(native,snapshot,case,payload,symbols,False,a);right=e.replay(native,snapshot,case,payload,symbols,True,b);assert left==right,(index,'nativeCPU');assert native.device.ram()[low:high]==canary,(index,'callercontext');assert b['private_depth']<232
   coverage.update(a['coverage']);rows.append(dict(index=index,private_depth=b['private_depth'],caller_context_clearance=232-b['private_depth'],task_headroom=870-b['private_depth']))
   if index%128==0:state['completed']=len(rows);mark();print('Final direction',index+1,'/2560',flush=True)
  assert all(e.g.sha(p)==h for p,h in hashes.items());e.g.save(out/'results.json',rows);state.update(status='terminal_native_direction_final_original_ABI_and_caller_context_pass',completed=len(rows),cases=len(rows),original_sites=sorted(coverage),max_private_depth=max(r['private_depth']for r in rows),minimum_caller_context_clearance=min(r['caller_context_clearance']for r in rows),minimum_task_headroom=min(r['task_headroom']for r in rows),scope=__doc__);mark();e.g.save(V/'native-actor-direction-final-current.json',state);print(json.dumps({k:state[k]for k in ['status','cases','binary_bytes','resident_bytes','heap_start','minimum_caller_context_clearance']}))
 except BaseException as error:state.update(status='terminal_native_direction_final_failed',error=repr(error),completed=len(rows));mark();raise
 finally:native.close()
if __name__=='__main__':main()
