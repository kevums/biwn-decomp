"""Final layout for task initializer and separately owned per-task GPU C stacks.
No disc/game frames here. Code,arena data and reservation sizes are distinct.
"""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_task_pool_engine_v1 as pool
import native_gpu_mailbox_arena_engine_v1 as gpu
ROOT=pool.ROOT;ND=pool.ND;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def build(out,make,target,variable,source,address,extra=None):
 command=['make','-f',make,target,'BUILD='+str(out),'ADDRESS='+hex(address),variable+'='+str(source)]
 if extra:command+=extra
 p=subprocess.run(command,cwd=ND,capture_output=True,text=True);out.parent.mkdir(parents=True,exist_ok=True);out.with_suffix('.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 filename='task-pool'if target=='task-pool'else'gpu-mailbox';binary=out/(filename+'.bin');elf=out/(filename+'.elf');nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);out.with_suffix('.symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};return binary,elf,symbols
def main():
 parent=read(V/'native-gpu-mailbox-disc-build-current.json');pgate=read(V/'native-task-pool-current.json');ggate=read(V/'native-gpu-mailbox-arena-current.json');assert parent['linked_component_bytes']==31758 and pgate['cases']==512 and ggate['cases']==2512
 assert ROOT.is_relative_to(Path(ggate['source_sha256'] and ROOT));out=V/'task-pool-arena-final-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 for name,data in [('parent-build.json',parent),('pool-prototype.json',pgate),('arena-prototype.json',ggate)]:pool.save(out/name,data)
 prefix=bytearray(Path(parent['linked_component']).read_bytes());resident=parent['resident_address'];prefix.extend(bytes((-len(prefix))%4));pool_address=resident+len(prefix);pool_source=ND/'task-pool-hybrid-v1.c';pbin,pelf,psymbols=build(out/'pool','Makefile.task-pool','task-pool','POOL_SOURCE',pool_source,pool_address);pbytes=pbin.read_bytes();prefix.extend(pbytes);prefix.extend(bytes((-len(prefix))%4));gpu_address=resident+len(prefix);gpu_source=ROOT/'runs/easy-gpu-recovery-20261019T135157.998050Z/repair/candidate.c'
 # Link once to establish code length,then link exactly at its final arena base.
 tbin,_,_=build(out/'gpu-size','Makefile.gpu-mailbox-arena','gpu-mailbox','MAILBOX_SOURCE',gpu_source,gpu_address);size=len(tbin.read_bytes());arena=(gpu_address+size+63)&~63;arena_end=arena+102*256;heap=arena_end+64;reserve=heap-resident;growth=reserve-parent['component_bytes'];staging=parent['staging_address']-growth;clear=0xfe200-staging;assert growth>0 and clear-40-reserve==88
 gbin,gelf,gsymbols=build(out/'gpu','Makefile.gpu-mailbox-arena','gpu-mailbox','MAILBOX_SOURCE',gpu_source,gpu_address,['ARENA_ADDRESS='+hex(arena)]);gbytes=gbin.read_bytes();assert len(gbytes)==size and gsymbols['GPU_ARENA_BASE']==arena
 relocations=[]
 def relocate(address,old,new,reason):
  at=address-resident;assert prefix[at:at+len(old)]==old;prefix[at:at+len(old)]=new;relocations.append(dict(resident_address=hex(address),old=old.hex(),new=new.hex(),reason=reason))
 for row in parent['layout_relocations'][:7]:
  old=bytes.fromhex(row['new']);relocate(int(row['resident_address'],16),old,(int.from_bytes(old,'big')+growth).to_bytes(4,'big'),'Raise heap floor for separately owned per-task GPU arenas and initializer code.')
 relocate(resident+0x16,parent['staging_address'].to_bytes(4,'big'),staging.to_bytes(4,'big'),'Relocate temporary loader staging; trailerFE200 unchanged.')
 relocate(resident+0x1c,(parent['staging_bytes_cleared']//2-1).to_bytes(2,'big'),(clear//2-1).to_bytes(2,'big'),'Clear relocated staging through FE200.')
 full=bytes(prefix)+gbytes;component=bytearray(full+bytes(reserve-len(full)))
 for slot in range(102):
  at=arena-resident+slot*256;component[at:at+16]=bytes([0xa5])*16;component[at+240:at+256]=bytes([0xa5])*16
 linked=out/'resident-code.bin';padded=out/'resident-with-arenas.bin';linked.write_bytes(full);padded.write_bytes(component);assert len(component)==reserve and resident+len(full)<=arena
 snapshot=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());snapshot[resident:resident+reserve]=component;snapshot=bytes(snapshot);pool.BASE=pool_address;gpu.BASE=gpu_address;gpu.ARENA=arena;gpu.PARENT_OVERRIDE=dict(parent,component=str(padded));native=pool.Native();pool_rows=[];gpu_rows=[]
 inputs=[Path(__file__),Path(pool.__file__),Path(gpu.__file__),pool_source,gpu_source,ND/'task-pool-native.h',ND/'task-pool-shim-v1.S',ND/'Makefile.task-pool',ND/'task-pool.ld',ND/'gpu-mailbox-native.h',ND/'gpu-mailbox-arena-shim-v1.S',ND/'Makefile.gpu-mailbox-arena',ND/'gpu-mailbox.ld',pbin,pelf,gbin,gelf,linked,padded,out/'parent-build.json',out/'pool-prototype.json',out/'arena-prototype.json',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];hashes={str(p):pool.sha(p)for p in inputs}
 state=dict(status='checking_final_pool_and_GPU_arenas',pid=os.getpid(),directory=str(out),completed_pool=0,completed_GPU=0,source_sha256=hashes,resident_address=resident,resident_code_bytes=len(full),reservation_bytes=reserve,reserved_arena_bytes=102*256,arena_address=arena,arena_end=arena_end,arena_slots=102,arena_slot_stride=256,arena_guards_each_end=16,arena_usable_slot_bytes=224,free_code_gap_bytes=arena-(resident+len(full)),free_tail_bytes=64,heap_start=heap,staging_address=staging,staging_clear_bytes=clear,layout_relocations=relocations,pool_address=pool_address,pool_binary=str(pbin),pool_ELF=str(pelf),pool_symbols=psymbols,pool_bytes=len(pbytes),pool_source=str(pool_source),GPU_address=gpu_address,GPU_binary=str(gbin),GPU_ELF=str(gelf),GPU_symbols=gsymbols,GPU_bytes=len(gbytes),GPU_source=str(gpu_source),GPU_source_authorship='Unchanged fresh one-clickv2 informedrepair; earlier old-stack rejection retained. New coordinator arena ABI. No new prediction or weight gain.',pool_source_authorship='Local informed repair plus one coordinator uint16_t wrap cast; supplied coordinator ABI/flags/platform boundary.',disc_integrated=False,new_predictions=0,new_training=False)
 def mark():pool.save(out/'protocol.json',state);pool.save(V/'task-pool-arena-final-active.json',state)
 mark()
 try:
  for index,case in enumerate(pool.cases()):
   a=pool.execute(snapshot,case,pbytes,psymbols,False);b=pool.execute(snapshot,case,pbytes,psymbols,True);assert all(a[k]==b[k]for k in['ram','registers','USP','trace']);left=pool.replay(native,snapshot,case,pbytes,psymbols,False,a);right=pool.replay(native,snapshot,case,pbytes,psymbols,True,b);assert left['pre']==right['pre']and left['final']==right['final'];pool_rows.append(dict(index=index,depth=b['private_depth']));state['completed_pool']=len(pool_rows)
   if index%128==0:mark();print('Final pool',index+1,'/512',flush=True)
  for index,case in enumerate(gpu.arena_cases()):
   a=gpu.execute(snapshot,case,gbytes,gsymbols,False);b=gpu.execute(snapshot,case,gbytes,gsymbols,True);assert all(a[k]==b[k]for k in['ram','registers','trace','mmio']);left=gpu.replay(native,snapshot,case,gbytes,gsymbols,False,a);right=gpu.replay(native,snapshot,case,gbytes,gsymbols,True,b);assert left==right;ram=native.device.ram();assert ram[resident:resident+len(full)]==full;gpu_rows.append(dict(index=index,slot=case['slot'],original_stack_bytes=b['private_depth'],arena_stack_bytes=b['arena_depth']));state['completed_GPU']=len(gpu_rows)
   if index%128==0:mark();print('Final GPU arena',index+1,'/2512',flush=True)
  assert all(pool.sha(p)==h for p,h in hashes.items());pool.save(out/'pool-results.json',pool_rows);pool.save(out/'GPU-results.json',gpu_rows);state.update(status='terminal_final_task_pool_and_GPU_arena_CPU_ownership_pass',pool_cases=len(pool_rows),GPU_cases=len(gpu_rows),max_original_GPU_stack_bytes=max(x['original_stack_bytes']for x in gpu_rows),max_GPU_arena_stack_bytes=max(x['arena_stack_bytes']for x in gpu_rows),minimum_GPU_arena_stack_headroom=224-max(x['arena_stack_bytes']for x in gpu_rows),scope=__doc__+' Supervisor/noIRQpool domain;scriptedGPUreplies and all102owners/guards. ABIidentityread explicitlyseparate. Live task/arena resource,IRQ/timing/game paths/hardware remain separate.');mark();pool.save(V/'task-pool-arena-final-current.json',state);print({k:state[k]for k in['status','resident_code_bytes','reservation_bytes','arena_address','heap_start','max_GPU_arena_stack_bytes']})
 except BaseException as error:state.update(status='terminal_final_pool_and_GPU_arena_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
