"""Coupled native heap lifecycle. Host supplies calls/payload fixtures, never heap bodies."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,random
import check_biwn_native_free_bundle_heap as heap
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x15edc0;SP=0x1e0000;STOP=0x1f0000
REDIRECTS={0x1b002:('biwn_native_resource_release',8),0x15200:('biwn_native_heap_compact',10),0x152a2:('biwn_native_heap_allocate',6),0x1545c:('biwn_native_free',8),0x1557a:('biwn_native_heap_initialize',10),0xe3e0:('biwn_native_copy_source_first',6),0xe3ee:('biwn_native_copy_destination_first',6)}
def normalize(ram,ref,length):
 b=bytearray(ram);b[BASE:BASE+length]=ref[BASE:BASE+length];b[SP-8192:SP]=ref[SP-8192:SP]
 for a,(_,size)in REDIRECTS.items():b[a:a+size]=ref[a:a+size]
 return b

def execute(n,image,entry,args,incoming,sr,payload,symbols,original):
 n.device.seed(image,1)
 for a in range(0xf02200,0xf022a0,4):
  if a!=0xf02238:n.device.write(a,0)
 l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
 l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if sr&0x2000 else 0x1fc000)
 l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000 if sr&0x2000 else SP);l.m68k_set_reg(17,sr)
 for i,v in enumerate(incoming+[SP]):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,entry);n.device.direct(SP,4,STOP)
 width=2 if entry==0x1b002 else 4
 for i,v in enumerate(args):n.device.direct(SP+4+width*i,width,v)
 pcs=[]
 for step in range(200000):
  pc=l.m68k_get_reg(None,16)
  if pc==STOP:break
  allowed=(0x15200<=pc<0x155c2 or 0xe3e0<=pc<0xe4aa or 0x1b002<=pc<0x1b044)if original else(BASE<=pc<BASE+len(payload) or pc in REDIRECTS)
  assert allowed,('original'if original else'compiled',hex(pc))
  pcs.append(pc);l.m68k_execute(1)
 else:raise AssertionError('Lifecycle native call failed to return')
 cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17));cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
 assert cpu['registers'][15]==SP+4
 return n.device.ram(),cpu,pcs,[n.device.read(a,4)for a in [0xf02200,0xf02204,0xf0220c,0xf02224,0xf02228,0xf02230,0xf0223c]]

def main():
 gp=ROOT/'verification/native-load-bundle-free-current.json';g=json.loads(gp.read_text());assert g['source_accepted']and g['native_cases']==1411
 ip=ROOT/'verification/native-load-bundle-initialize-current.json';init=json.loads(ip.read_text());assert init['source_accepted']and init['native_cases']==192 and init['compiled_binary_sha256']==g['compiled_binary_sha256']
 for proof in [g,init]:
  for p,d in proof['source_sha256'].items():assert sha(p)==d,p
 payload=Path(g['compiled_binary']).read_bytes();assert sha(g['compiled_binary'])==g['compiled_binary_sha256'];symbols=g['symbols'];floor=symbols['biwn_native_heap_start']
 out=ROOT/'verification/native-load-bundle-lifecycle'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='running',pid=os.getpid(),directory=str(out),game_frames=0,source_accepted=False,host_heap_bodies=False,host_payload_fixtures=True)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-load-bundle-lifecycle-active.json',state)
 mark();n=heap.sched.Native();rng=random.Random(0x1545c1557a);rows=[];u=lambda b,a:int.from_bytes(b[a:a+4],'big');verified_bytes=0
 try:
  for variant in range(8):
   original=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
   for a,v in [(0x1521c,floor),(0x1526c,floor),(0x1557c,floor),(0x1558c,floor),(0x15592,floor),(0x15598,floor+4),(0x1559e,floor+8)]:original[a:a+4]=v.to_bytes(4,'big')
   compiled=bytearray(original);compiled[BASE:BASE+len(payload)]=payload
   for a,(symbol,size)in REDIRECTS.items():compiled[a:a+size]=b'\x4e\xf9'+symbols[symbol].to_bytes(4,'big')+b'\x4e\x71'*((size-6)//2)
   live={};handles={};next_id=0
   def call(entry,args,label):
    nonlocal original,compiled,verified_bytes
    incoming=[rng.getrandbits(32)for _ in range(15)];sr=(0x2000 if variant&1 else 0)|rng.randrange(32)|((variant%8)<<8)
    left=execute(n,original,entry,args,incoming,sr,payload,symbols,True);right=execute(n,compiled,entry,args,incoming,sr,payload,symbols,False)
    if left[1]!=right[1]or left[3]!=right[3]or normalize(right[0],left[0],len(payload))!=left[0]:
     save(out/'mismatch.json',dict(variant=variant,label=label,entry=hex(entry),args=args,original_CPU=left[1],compiled_CPU=right[1],RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left[0],normalize(right[0],left[0],len(payload))))if a!=b][:32]));raise AssertionError(str(out/'mismatch.json'))
    assert right[0][BASE:BASE+len(payload)]==payload
    original,compiled=bytearray(left[0]),bytearray(right[0])
    for h,pattern in live.items():
     pointer=u(compiled,h);assert pointer>=floor+8 and compiled[pointer:pointer+len(pattern)]==pattern,(variant,label,hex(h),'payload');verified_bytes+=len(pattern)
    rows.append(dict(variant=variant,operation=label,entry=hex(entry),arguments=args,CPU=right[1],live_payload_count=len(live),free_bytes=u(compiled,0x112d64),compiled_resource_release_C_calls=right[2].count(symbols['biwn_native_resource_release_body']),compiled_free_body_calls=right[2].count(symbols['biwn_native_free_body']),compiled_init_calls=right[2].count(symbols['biwn_native_heap_initialize']),compiled_copy_body_calls=right[2].count(symbols['biwn_native_copy_body']),full_CPU_public_RAM_hardware_match=True))
    return right[1]['registers'][0]
   def allocate(size):
    nonlocal next_id
    h=call(0x152a2,[size],'allocate_'+str(size));assert h and h not in live;pointer=u(compiled,h);assert floor+8<=pointer and pointer+size<=0x1c0000
    pattern=bytes((variant*37+next_id*61+j*13)&255 for j in range(size));next_id+=1
    original[pointer:pointer+size]=compiled[pointer:pointer+size]=pattern;live[h]=pattern;return h
   def release(h):
    pattern=live.pop(h);call(0x1545c,[h],'free');assert u(compiled,h)==0
   call(0x1557a,[],'initialize');call(0x1545c,[0],'free_null');call(0x1545c,[0x112960],'free_empty')
   hs=[allocate(size)for size in [9,128,257,64,513,32]]
   linked=allocate(96)
   # Host fixtures bind a real allocated handle to a cache slot; both
   # caller bodies and both nested frees then execute native instructions.
   for image in [original,compiled]:
    for slot in range(50):
     address=0x15b534+slot*12;image[address:address+12]=b'\xff\xff'+bytes(10)
    address=0x15b534+(49 if variant&1 else 0)*12
    image[address:address+2]=(0x1234).to_bytes(2,'big');image[address+2:address+6]=linked.to_bytes(4,'big');image[address+6:address+8]=(2).to_bytes(2,'big')
   call(0x1b002,[0x1234],'resource_release_retain')
   assert int.from_bytes(compiled[address+6:address+8],'big')==1 and u(compiled,linked)!=0
   live.pop(linked);call(0x1b002,[0x1234],'resource_release_unload')
   assert int.from_bytes(compiled[address:address+2],'big')==0xffff and int.from_bytes(compiled[address+6:address+8],'big')==0 and u(compiled,linked)==0
   order=[1,3,0]if variant<4 else[4,2,5]
   for i in order:release(hs[i])
   call(0x15200,[],'compact_fragmented');extra=[allocate(80),allocate(385)]
   remaining=list(live);rng.shuffle(remaining)
   for h in remaining:release(h)
   call(0x15200,[],'compact_empty');assert u(compiled,0x112d60)==floor and u(compiled,floor)==0x1c0000-floor and u(compiled,0x112d64)==0x1c0000-floor
   for i in range(3):
    h=allocate([2048,17,511][i]);release(h)
   assert u(compiled,0x112d64)==0x1c0000-floor
   state['completed_variants']=variant+1;mark();print('Lifecycle',variant+1,'/8',len(rows),'calls',flush=True)
  save(out/'results.json',rows)
  state.update(status='terminal_coupled_native_heap_lifecycle_pass',source_accepted=True,variants=8,native_call_pairs=len(rows),payload_byte_comparisons=verified_bytes,compiled_resource_release_C_calls=sum(x['compiled_resource_release_C_calls']for x in rows),compiled_free_body_calls=sum(x['compiled_free_body_calls']for x in rows),compiled_initializer_calls=sum(x['compiled_init_calls']for x in rows),compiled_copy_body_calls=sum(x['compiled_copy_body_calls']for x in rows),component_proofs={str(p):sha(p)for p in [gp,ip]},compiled_binary_sha256=sha(g['compiled_binary']),source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_biwn_native_free_bundle_heap.py',ROOT/'scripts/check_biwn_scheduler.py']},execution_dependencies_sha256=g['execution_dependencies_sha256'],scope='Eight coupled call sequences, two stack modes, varied incoming CPU/CCR and allocation/free orders. Original and target source initializer/allocator/free/compactor/copy/resource-release execute native emulated instructions and blitter; full returnCPU/publicRAM/hardware match, known host-seeded payloads survive compaction, all free space recovered. Private8KBstack and redirects/payload excluded; isolated gates separately check original public save slots and bus order. No gameframes/IRQ/device concurrency/arbitrary malformed lists/physical console or whole-game proof.')
  mark();save(ROOT/'verification/native-load-bundle-lifecycle-current.json',state);print(state['status'],len(rows),verified_bytes,flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:n.close()
if __name__=='__main__':main()
