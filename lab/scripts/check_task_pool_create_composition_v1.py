"""Actual initializer ->100 real creates -> real empty-pool ILLEGAL, two lanes.
Fixture harness seeds call args/return slots between calls; not game execution.
Current native creator is the checked published component, original lane uses
original DE5C. Only main-task private stack/code/boot private frame normalize;
actual exception frame is compared separately, not discarded by normalization.
"""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_task_pool_engine_v1 as e
V=e.ROOT/'verification';MAIN=0xc0928;TOP=MAIN+0x400;STOP=0x192000;FAULT=STOP+0x20
def read(p):return json.loads(Path(p).read_text())
def main():
 gate=read(V/'native-task-pool-current.json');build=read(V/'native-gpu-mailbox-disc-build-current.json');assert gate['cases']==512;out=V/'task-pool-create-composition-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);payload=Path(gate['binary']).read_bytes();symbols=gate['symbols'];snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();resident=Path(build['component']).read_bytes();stage=Path(build['derived_stage']).read_bytes();native=e.Native();rows=[];cases=[e.cases()[i]for i in[0,31,224,255,256,287,480,511]]
 def norm(ram,case):
  m=bytearray(e.normalize(ram,snapshot,case,len(payload)))
  for lo,hi in [(MAIN+38,TOP),(0xde5c,0xde62),(0xdf6c,0xdf72)]:m[lo:hi]=snapshot[lo:hi]
  return bytes(m)
 def cpu():
  l=native.lib;regs=[l.m68k_get_reg(None,i)for i in range(16)];sr=l.m68k_get_reg(None,17);return dict(registers=regs,PC=l.m68k_get_reg(None,16),SR=sr,USP=native.prefix[16]if sr&0x2000 else regs[15],SSP=regs[15]if sr&0x2000 else native.prefix[17])
 def lane(case,compiled):
  memory=bytearray(snapshot);memory[build['resident_address']:build['resident_address']+len(resident)]=resident;memory[0x10:0x14]=FAULT.to_bytes(4,'big')
  if compiled:
   for a in [0xde5c,0xdf6c]:memory[a:a+6]=stage[a-0x4000:a-0x4000+6];assert memory[a:a+2]==b'\x4e\xf9'
  expected=e.execute(bytes(memory),case,payload,symbols,compiled);e.replay(native,bytes(memory),case,payload,symbols,compiled,expected);results=[];l=native.lib
  for index in range(101):
   callback=0x190000+8*index;parameter=(0x8d000001+index*0x10203)&0xffffffff;l.m68k_set_reg(0,callback);l.m68k_set_reg(1,parameter);l.m68k_set_reg(15,TOP-4);native.device.direct(TOP-4,4,STOP);l.m68k_set_reg(16,0xde5c)
   for step in range(2000):
    pc=l.m68k_get_reg(None,16)
    if pc in [STOP,FAULT]:break
    assert(0xde5c<=pc<=0xdeb4)or(compiled and build['resident_address']<=pc<build['resident_address']+len(resident)),hex(pc);l.m68k_execute(1)
   else:raise AssertionError('Create did not return/fault')
   actual=cpu();ram=native.device.ram();word=lambda a:int.from_bytes(ram[a:a+4],'big')
   if index<100:
    task=0xc0d28+index*0x400;assert actual['PC']==STOP and actual['registers'][0]==task and actual['registers'][15]==TOP and word(task+8)==word(task+16)==callback and word(task+30)==parameter and word(task+12)==task+0x400
    assert not any(ram[task+20:task+30])and word(task+34)==0
    cursor=MAIN;ring=[]
    while not ring or cursor!=MAIN:
     assert cursor not in ring;ring.append(cursor);nxt=word(cursor);assert word(nxt+4)==cursor;cursor=nxt
    assert len(ring)==index+2 and word(0xc0920)==MAIN and word(0xc0924)==(task+0x400 if index<99 else 0)
    results.append(dict(index=index,CPU=actual,RAM_sha256=__import__('hashlib').sha256(norm(ram,case)).hexdigest(),ring_nodes=len(ring)))
   else:
    assert actual['PC']==FAULT and actual['SR']&0x2000;depth=case['ssp']-actual['registers'][15];assert depth==6;frame=ram[actual['registers'][15]:case['ssp']];results.append(dict(index=index,CPU=actual,RAM_sha256=__import__('hashlib').sha256(norm(ram,case)).hexdigest(),actual_exception_frame=frame.hex(),exception_PC=int.from_bytes(frame[2:],'big'),free_head=word(0xc0924)));assert word(0xc0924)==0
  return results
 try:
  for index,case in enumerate(cases):
   left=lane(case,False);right=lane(case,True)
   if left!=right:e.save(out/'mismatch.json',dict(case=case,first=next(i for i,(a,b)in enumerate(zip(left,right))if a!=b),original=left,compiled=right));raise AssertionError('Initializer/create composition mismatch')
   rows.append(dict(case_index=index,case=case,original_and_compiled_results=right));print('Composition',index+1,'/',len(cases),flush=True)
  e.save(out/'results.json',rows);paths=[Path(__file__),Path(e.__file__),Path(gate['binary']),Path(gate['ELF']),Path(build['component']),Path(build['derived_stage']),e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',out/'results.json'];state=dict(status='terminal_task_pool_100creates_and_empty_ILLEGAL_composition_pass',directory=str(out),cases=len(cases),native_lanes=2*len(cases),successful_create_calls=200*len(cases),actual_ILLEGAL_calls=2*len(cases),free_slots=100,total_slots=101,task_stride=1024,source_sha256={str(p):e.sha(p)for p in paths},scope=__doc__,new_predictions=0,new_training=False,game_frames=0);e.save(out/'protocol.json',state);e.save(V/'task-pool-create-composition-current.json',state);print({k:state[k]for k in ['status','successful_create_calls','actual_ILLEGAL_calls']})
 finally:native.close()
if __name__=='__main__':main()
